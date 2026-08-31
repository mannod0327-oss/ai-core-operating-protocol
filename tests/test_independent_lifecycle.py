"""Independent lifecycle checks; all installs use pytest disposable roots."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

import installers.install as lifecycle


@pytest.fixture
def context(tmp_path):
    work, home, state = (tmp_path / name for name in ("workspace ü", "home ü", "state"))
    sentinel = tmp_path / "outside.txt"
    sentinel.write_bytes(b"untouched\r\n")
    yield ("claude", "workspace", work, home, state)
    assert sentinel.read_bytes() == b"untouched\r\n"


def remove(context, *, rollback=False):
    runtime, scope, work, home, state = context
    return lifecycle.uninstall(state, runtime=runtime, scope=scope, workspace=work,
                               home=home, rollback=rollback)


def record_path(context, record):
    return context[-1] / "records" / (record["identity"] + ".json")


def test_fresh_repeat_upgrade_rollback_remove(context, monkeypatch):
    first = lifecycle.install(*context)
    dest = Path(first["destination"])
    original = lifecycle.tree_hash(dest)
    assert lifecycle.verify(*context)["status"] == "verified"
    before_state = lifecycle.tree_hash(context[-1])
    assert lifecycle.install(*context)["status"] == "unchanged"
    assert lifecycle.tree_hash(context[-1]) == before_state
    monkeypatch.setattr(lifecycle, "VERSION", "2.0.0-test-next")
    assert lifecycle.install(*context)["version"] == "2.0.0-test-next"
    assert remove(context, rollback=True)["status"] == "rolled-back"
    assert lifecycle.tree_hash(dest) == original
    assert lifecycle.verify(*context)["status"] == "verified"
    assert remove(context)["status"] == "removed"
    assert not dest.exists()
    assert remove(context)["status"] == "not-installed"


def test_collision_requires_replace_and_preserves_unmanaged_original(context):
    dest = lifecycle.runtime_destination(*context[:4])
    dest.mkdir(parents=True)
    (dest / "custom.txt").write_bytes(b"prior bytes\r\n")
    original = lifecycle.tree_hash(dest)
    with pytest.raises(RuntimeError, match="collision"):
        lifecycle.install(*context)
    lifecycle.install(*context, replace=True)
    assert remove(context)["status"] == "restored-backup"
    assert lifecycle.tree_hash(dest) == original


def test_different_state_cannot_claim_managed_install(context):
    first = lifecycle.install(*context)
    before = lifecycle.tree_hash(Path(first["destination"]))
    with pytest.raises(RuntimeError, match="different state"):
        lifecycle.install(*context[:-1], context[-1].with_name("other-state"), replace=True)
    assert lifecycle.tree_hash(Path(first["destination"])) == before


def test_shared_destination_conflict(context):
    codex = ("codex", *context[1:])
    first = lifecycle.install(*codex)
    with pytest.raises(ValueError, match="another runtime"):
        lifecycle.install("gemini", *context[1:])
    assert lifecycle.verify(*codex)["status"] == "verified"
    assert Path(first["destination"]).exists()


def test_separate_workspaces_do_not_overwrite_records(context):
    first = lifecycle.install(*context)
    second_context = (*context[:2], context[2].with_name("second-workspace"), *context[3:])
    second = lifecycle.install(*second_context)
    assert first["identity"] != second["identity"]
    remove(context)
    assert lifecycle.verify(*second_context)["status"] == "verified"


def test_added_user_file_blocks_upgrade_and_removal(context, monkeypatch):
    first = lifecycle.install(*context)
    dest = Path(first["destination"])
    (dest / "user.txt").write_text("personal", encoding="utf-8")
    before = lifecycle.tree_hash(dest)
    monkeypatch.setattr(lifecycle, "VERSION", "next")
    with pytest.raises(RuntimeError, match="modified"):
        lifecycle.install(*context)
    with pytest.raises(RuntimeError, match="User changes"):
        remove(context)
    assert lifecycle.tree_hash(dest) == before


def test_tampered_manifest_target_is_rejected(context, tmp_path):
    record = lifecycle.install(*context)
    record["destination"] = str(tmp_path)
    record_path(context, record).write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="identity/target mismatch"):
        remove(context)


def test_missing_rollback_snapshot_refuses_mutation(context, monkeypatch):
    lifecycle.install(*context)
    monkeypatch.setattr(lifecycle, "VERSION", "next")
    record = lifecycle.install(*context)
    dest = Path(record["destination"])
    before = lifecycle.tree_hash(dest)
    snapshot = lifecycle._snapshot_path(context[-1], record["identity"], record["previous"]["snapshot"]["key"])
    snapshot.rename(snapshot.with_name("retained-missing-snapshot"))
    with pytest.raises(ValueError, match="Missing or changed snapshot"):
        remove(context, rollback=True)
    assert lifecycle.tree_hash(dest) == before


def test_record_commit_failure_restores_original(context, monkeypatch):
    record = lifecycle.install(*context)
    dest = Path(record["destination"])
    before = lifecycle.tree_hash(dest)
    old_record = record_path(context, record).read_bytes()
    monkeypatch.setattr(lifecycle, "VERSION", "next")
    real_write = lifecycle._write
    failed = False

    def fail_once(path, data):
        nonlocal failed
        if path.parent.name == "records" and not failed:
            failed = True
            raise PermissionError("injected record failure")
        return real_write(path, data)

    monkeypatch.setattr(lifecycle, "_write", fail_once)
    with pytest.raises(PermissionError):
        lifecycle.install(*context)
    assert lifecycle.tree_hash(dest) == before
    assert record_path(context, record).read_bytes() == old_record
    assert lifecycle.verify(*context)["status"] == "verified"


def test_pending_journal_blocks_writes(context):
    record = lifecycle.install(*context)
    pending = context[-1] / "journals" / (record["identity"] + ".json")
    pending.write_text("{}", encoding="utf-8")
    before = lifecycle.tree_hash(Path(record["destination"]))
    assert lifecycle.verify(*context)["status"] == "pending-recovery"
    with pytest.raises(RuntimeError, match="Pending transaction"):
        remove(context)
    assert lifecycle.tree_hash(Path(record["destination"])) == before


def test_lock_blocks_second_writer(context):
    record = lifecycle.install(*context)
    lock = context[-1] / ".operation.lock"
    lock.write_bytes(b"test")
    with pytest.raises(RuntimeError, match="lock"):
        remove(context)
    assert lifecycle.verify(*context)["status"] == "verified"
    assert lock.read_bytes() == b"test"


def test_plan_detects_same_version_source_change(context, tmp_path, monkeypatch):
    lifecycle.install(*context)
    source = tmp_path / "different-source"
    shutil.copytree(lifecycle.SOURCE, source)
    (source / "additional.txt").write_text("new source", encoding="utf-8")
    monkeypatch.setattr(lifecycle, "SOURCE", source)
    assert lifecycle.plan(*context)["changes_required"] is True


def test_publish_rejects_copy_content_mismatch(context, monkeypatch):
    real_copy = shutil.copytree

    def corrupt_copy(source, destination, *args, **kwargs):
        result = real_copy(source, destination, *args, **kwargs)
        (Path(destination) / "SKILL.md").write_text("truncated copy", encoding="utf-8")
        return result

    monkeypatch.setattr(lifecycle.shutil, "copytree", corrupt_copy)
    with pytest.raises((ValueError, RuntimeError), match="(?i)(source|copy|hash|valid)"):
        lifecycle.install(*context)
    assert not lifecycle.runtime_destination(*context[:4]).exists()


def test_source_change_during_copy_never_publishes_unvalidated_source(context, tmp_path, monkeypatch):
    source = tmp_path / "isolated-source"
    shutil.copytree(lifecycle.SOURCE, source)
    monkeypatch.setattr(lifecycle, "SOURCE", source)
    real_copy = shutil.copytree

    def change_source_before_copy(src, dest, *args, **kwargs):
        if Path(src) == source:
            (source / "SKILL.md").write_text("changed while copy starts", encoding="utf-8")
        return real_copy(src, dest, *args, **kwargs)

    monkeypatch.setattr(lifecycle.shutil, "copytree", change_source_before_copy)
    with pytest.raises((ValueError, RuntimeError), match="(?i)(source|copy|hash|valid)"):
        lifecycle.install(*context)
    assert not lifecycle.runtime_destination(*context[:4]).exists()


def test_interrupted_copy_preserves_original_install(context, monkeypatch):
    record = lifecycle.install(*context)
    dest = Path(record["destination"])
    before = lifecycle.tree_hash(dest)
    monkeypatch.setattr(lifecycle, "VERSION", "next")

    def interrupted_copy(source, stage, *args, **kwargs):
        Path(stage).mkdir()
        (Path(stage) / "partial.txt").write_text("partial", encoding="utf-8")
        raise PermissionError("simulated interrupted copy")

    monkeypatch.setattr(lifecycle.shutil, "copytree", interrupted_copy)
    with pytest.raises(PermissionError):
        lifecycle.install(*context)
    assert lifecycle.tree_hash(dest) == before
    assert lifecycle.verify(*context)["status"] == "verified"


def test_cli_plan_install_repeat_verify_uninstall(context):
    runtime, scope, workspace, home, state = context
    common = [sys.executable, "-B", str(Path(lifecycle.__file__)), runtime,
              "--scope", scope, "--workspace", str(workspace), "--home", str(home),
              "--state-dir", str(state)]
    for action, expected in (("plan", "plan"), ("install", "installed"),
                             ("install", "unchanged"), ("verify", "verified"),
                             ("uninstall", "removed"), ("verify", "not-installed")):
        result = subprocess.run([*common, "--action", action], capture_output=True,
                                text=True, encoding="utf-8", timeout=20)
        assert result.returncode == 0, result.stderr + result.stdout
        assert json.loads(result.stdout)["status"] == expected


def test_partial_record_is_reported_as_controlled_cli_failure(context, monkeypatch, capsys):
    record = lifecycle.install(*context)
    del record["hashes"]
    record_path(context, record).write_text(json.dumps(record), encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["install.py", context[0], "--scope", context[1],
        "--workspace", str(context[2]), "--home", str(context[3]),
        "--state-dir", str(context[4]), "--action", "verify"])
    assert lifecycle.main() == 2
    assert json.loads(capsys.readouterr().out)["status"] == "blocked"
