"""Fail-closed local lifecycle; no recursive deletion. Snapshots are retained.

Targets come from explicit caller context, never from an untrusted manifest.
Pending journals block later writes after an interrupted transaction.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager, ExitStack
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.project import NAME, ROOT, VERSION, runtime_spec, openai_yaml

SOURCE = ROOT / "skills" / NAME
MARKER = ".ai-core-owner.json"


def checked(path: Path) -> Path:
    path = Path(path)
    if ".." in path.parts or (path.drive and not path.is_absolute()):
        raise ValueError("Traversal or drive-relative path is not supported")
    path = Path(os.path.abspath(path))
    if str(path).startswith(("\\\\", "//")):
        raise ValueError("UNC targets are not supported")
    for item in (*reversed(path.parents), path):
        if item.is_symlink():
            raise ValueError("Symbolic link is not an installation boundary")
        if item.exists() and getattr(item.lstat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError("Reparse point is not an installation boundary")
    return path.resolve()


def tree_hash(path: Path) -> dict:
    path = checked(path)
    if not path.exists():
        return {}
    if not path.is_dir():
        raise ValueError("Expected a directory")
    result = {}
    for item in sorted(path.rglob("*")):
        checked(item)
        relative = item.relative_to(path).as_posix()
        key = relative if item.is_file() else relative + "/"
        if key.casefold() in {k.casefold() for k in result}:
            raise ValueError("Case-colliding files")
        result[key] = hashlib.sha256(item.read_bytes()).hexdigest() if item.is_file() else "directory"
    return result


def runtime_destination(runtime, scope, workspace, home):
    spec = runtime_spec(runtime)
    if scope not in {"user", "workspace"}:
        raise ValueError("Invalid scope")
    base = checked(home if scope == "user" else workspace)
    if base == Path(base.anchor):
        raise ValueError("Disk root is not an installation root")
    dest = checked(base / spec[scope] / NAME)
    if not dest.is_relative_to(base) or dest == base:
        raise ValueError("Destination escapes selected root")
    return dest


def _context(runtime, scope, workspace, home, state_dir):
    dest = runtime_destination(runtime, scope, Path(workspace), Path(home))
    state = checked(state_dir)
    if state == Path(state.anchor) or state in {checked(home), checked(workspace)} or state.is_relative_to(dest) or dest.is_relative_to(state):
        raise ValueError("State must be a separate dedicated directory")
    identity = hashlib.sha256(os.path.normcase(str(dest)).encode()).hexdigest()[:24]
    return dest, state, identity


def _read(path):
    checked(path)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _write(path, data):
    checked(path)
    tmp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    with tmp.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


@contextmanager
def _lock(path):
    checked(path)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError("Another operation or stale lock exists; inspect before recovery") from exc
    try:
        os.close(fd)
        yield
    finally:
        checked(path).unlink()


def _record(state, identity, dest, runtime, scope):
    data = _read(state / "records" / (identity + ".json"))
    if data is not None:
        _validate_record(data, identity, dest, runtime, scope)
    return data


def _validate_record(data, identity, dest, runtime, scope):
    if data is not None and (not isinstance(data, dict) or not data):
        raise ValueError("Invalid managed record")
    if data:
        if not {"version", "hashes", "source_hashes", "original", "previous"}.issubset(data):
            raise ValueError("Incomplete managed record")
        if not isinstance(data["hashes"], dict) or not isinstance(data["source_hashes"], dict):
            raise ValueError("Invalid managed record hashes")
        if data.get("schema_version") != 2 or data.get("identity") != identity or data.get("destination") != str(dest):
            raise ValueError("Manifest identity/target mismatch")
        if data.get("runtime") != runtime or data.get("scope") != scope:
            raise ValueError("Shared destination owned by another runtime/scope")
        if data["original"] is not None:
            _validate_snapshot(data["original"])
        previous = data["previous"]
        if previous is not None:
            if not isinstance(previous, dict) or not isinstance(previous.get("record"), dict):
                raise ValueError("Invalid previous managed record")
            _validate_snapshot(previous.get("snapshot"))
            prior = previous["record"]
            if previous["snapshot"]["hashes"] != prior.get("hashes") or data["original"] != prior.get("original"):
                raise ValueError("Previous snapshot/record mismatch")
            # Only the previous record is restored; older chains are checked on use.
            required = {"version", "hashes", "source_hashes", "original", "previous"}
            if not required <= prior.keys() or prior.get("schema_version") != 2 or prior.get("identity") != identity or prior.get("destination") != str(dest) or prior.get("runtime") != runtime or prior.get("scope") != scope:
                raise ValueError("Invalid previous record context")


def _validate_snapshot(data):
    if not isinstance(data, dict) or not isinstance(data.get("key"), str) or not re.fullmatch(r"[a-f0-9]{32}", data["key"]) or not isinstance(data.get("hashes"), dict):
        raise ValueError("Invalid snapshot record")


def _device(path):
    path = checked(path)
    while not path.exists():
        if path.parent == path:
            raise ValueError("Selected filesystem root does not exist")
        path = path.parent
    return path.stat().st_dev


def _same_filesystem(dest, state):
    if _device(dest.parent) != _device(state):
        raise ValueError("Destination and state must share a filesystem; choose --state-dir on the workspace volume")


def _snapshot_path(state, identity, key):
    if not isinstance(key, str) or not re.fullmatch(r"[a-f0-9]{32}", key):
        raise ValueError("Invalid snapshot identity")
    return checked(state / "snapshots" / identity / key)


def _snapshot(state, identity, data):
    if data is None:
        return None
    path = _snapshot_path(state, identity, data["key"])
    if not path.is_dir() or tree_hash(path) != data["hashes"]:
        raise ValueError("Missing or changed snapshot; refusing to change installation")
    return path


def plan(runtime, scope, workspace, home, state_dir):
    dest, state, identity = _context(runtime, scope, workspace, home, state_dir)
    _same_filesystem(dest, state)
    record = _record(state, identity, dest, runtime, scope)
    pending = state / "journals" / (identity + ".json")
    checked(pending)
    return {"status": "plan", "identity": identity, "destination": str(dest),
            "state": str(state), "exists": dest.exists(), "managed": bool(record),
            "pending_transaction": pending.exists(), "version": VERSION,
            "changes_required": not record or record["version"] != VERSION or record["source_hashes"] != tree_hash(SOURCE)}


def verify(runtime, scope, workspace, home, state_dir):
    dest, state, identity = _context(runtime, scope, workspace, home, state_dir)
    record = _record(state, identity, dest, runtime, scope)
    pending = state / "journals" / (identity + ".json")
    checked(pending)
    if pending.exists():
        return {"status": "pending-recovery", "identity": identity}
    return {"status": "not-installed" if not record else "verified" if tree_hash(dest) == record["hashes"] else "modified",
            "identity": identity}


@contextmanager
def _operation(dest, state, identity):
    _same_filesystem(dest, state)
    for directory in (state, state / "records", state / "snapshots", state / "journals", dest.parent):
        checked(directory).mkdir(parents=True, exist_ok=True)
    with ExitStack() as locks:
        locks.enter_context(_lock(state / ".operation.lock"))
        locks.enter_context(_lock(dest.parent / (".ai-core-" + identity + ".lock")))
        if (state / "journals" / (identity + ".json")).exists():
            raise RuntimeError("Pending transaction: retained snapshots must be inspected before recovery")
        yield


def _commit(dest, state, identity, stage, old_record, new_record, before, backup_key):
    record_path = state / "records" / (identity + ".json")
    journal = state / "journals" / (identity + ".json")
    backup = _snapshot_path(state, identity, backup_key)
    backup.parent.mkdir(parents=True, exist_ok=True)
    _write(journal, {"identity": identity, "destination": str(dest), "backup_key": backup_key,
                     "before": before, "after": tree_hash(stage) if stage else {},
                     "old_record": old_record, "new_record": new_record})
    moved = published = False
    try:
        if tree_hash(dest) != before:
            raise RuntimeError("Destination changed during operation")
        if dest.exists():
            checked(dest).rename(backup)
            moved = True
        if stage:
            checked(stage).rename(dest)
            published = True
        if new_record:
            _write(record_path, new_record)
        elif record_path.exists():
            checked(record_path).unlink()
    except Exception:
        if published and dest.exists():
            checked(dest).rename(_snapshot_path(state, identity, uuid.uuid4().hex))
        if moved:
            checked(backup).rename(dest)
        if old_record:
            _write(record_path, old_record)
        elif record_path.exists():
            checked(record_path).unlink()
        checked(journal).unlink()
        raise
    checked(journal).unlink()


def install(runtime, scope, workspace, home, state_dir, *, replace=False):
    dest, state, identity = _context(runtime, scope, workspace, home, state_dir)
    with _operation(dest, state, identity):
        record = _record(state, identity, dest, runtime, scope)
        before = tree_hash(dest)
        if record and before != record["hashes"]:
            raise RuntimeError("Installation modified by user; preserve and resolve conflict first")
        if not record and dest.exists() and (dest / MARKER).exists():
            raise RuntimeError("Installation belongs to a different state directory")
        if not record and dest.exists() and not replace:
            raise RuntimeError("Unmanaged collision; explicit replace with snapshot required")
        source_hashes = tree_hash(SOURCE)
        if record and record["version"] == VERSION and record["source_hashes"] == source_hashes:
            return {**record, "status": "unchanged"}
        stage = dest.parent / (".ai-core-stage-" + uuid.uuid4().hex)
        checked(stage)
        shutil.copytree(SOURCE, stage)
        if tree_hash(stage) != source_hashes or tree_hash(SOURCE) != source_hashes:
            raise RuntimeError("Source or staged copy changed; installation refused")
        if runtime_spec(runtime)["metadata"] == "openai":
            (stage / "agents").mkdir(exist_ok=True)
            (stage / "agents/openai.yaml").write_text(openai_yaml(), encoding="utf-8", newline="\n")
        _write(stage / MARKER, {"identity": identity, "state": str(state)})
        key = uuid.uuid4().hex
        snapshot = {"key": key, "hashes": before} if dest.exists() else None
        data = {"schema_version": 2, "identity": identity, "runtime": runtime, "scope": scope,
                "destination": str(dest), "version": VERSION, "source_hashes": source_hashes,
                "hashes": tree_hash(stage), "original": record["original"] if record else snapshot,
                "previous": {"snapshot": snapshot, "record": record} if record else None}
        _commit(dest, state, identity, stage, record, data, before, key)
        return {**data, "status": "installed", "backup": str(_snapshot_path(state, identity, key)) if snapshot else None}


def uninstall(state_dir, *, runtime, scope, workspace, home, rollback=False):
    dest, state, identity = _context(runtime, scope, workspace, home, state_dir)
    with _operation(dest, state, identity):
        record = _record(state, identity, dest, runtime, scope)
        if not record:
            return {"status": "not-installed"}
        before = tree_hash(dest)
        if before != record["hashes"]:
            raise RuntimeError("User changes detected; uninstall/rollback refused without data loss")
        previous = record.get("previous")
        if rollback and not previous:
            raise ValueError("No previous managed version")
        snapshot = previous["snapshot"] if rollback else record["original"]
        restored_record = previous["record"] if rollback else None
        if restored_record:
            _validate_record(restored_record, identity, dest, runtime, scope)
        restore = _snapshot(state, identity, snapshot)
        stage = None
        if restore:
            stage = dest.parent / (".ai-core-stage-" + uuid.uuid4().hex)
            shutil.copytree(restore, stage)
            if tree_hash(stage) != snapshot["hashes"]:
                raise RuntimeError("Snapshot copy changed; restoration refused")
        _commit(dest, state, identity, stage, record, restored_record, before, uuid.uuid4().hex)
        return {"status": "rolled-back" if rollback else "restored-backup" if restore else "removed",
                "destination": str(dest), "snapshots_retained": True}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("runtime")
    p.add_argument("--scope", choices=["user", "workspace"], default="workspace")
    p.add_argument("--workspace", default=".")
    p.add_argument("--home", default=str(Path.home()))
    p.add_argument("--state-dir")
    p.add_argument("--action", choices=["plan", "doctor", "install", "upgrade", "verify", "list-installs", "uninstall", "rollback"], default="plan")
    p.add_argument("--replace", action="store_true")
    args = p.parse_args()
    state = Path(args.state_dir) if args.state_dir else Path(args.home) / ".ai-core-operating-protocol-v2"
    common = (args.runtime, args.scope, Path(args.workspace), Path(args.home), state)
    try:
        if args.action == "list-installs":
            runtime_spec(args.runtime)
            records_dir = checked(checked(state) / "records")
            records = []
            for path in sorted(records_dir.glob("*.json")):
                data = _read(path)
                if not isinstance(data, dict) or data.get("schema_version") != 2:
                    raise ValueError("Invalid managed record")
                records.append({key: data[key] for key in ("identity", "runtime", "scope", "version")})
            result = {"status": "listed", "installs": records}
        elif args.action in {"plan", "doctor"}:
            result = plan(*common)
        elif args.action == "verify":
            result = verify(*common)
        elif args.action in {"install", "upgrade"}:
            result = install(*common, replace=args.replace)
        else:
            result = uninstall(state, runtime=args.runtime, scope=args.scope, workspace=Path(args.workspace), home=Path(args.home), rollback=args.action == "rollback")
        print(json.dumps(result, indent=2))
        return 1 if result["status"] in {"modified", "pending-recovery"} else 0
    except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
