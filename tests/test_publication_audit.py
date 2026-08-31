"""Independent-audit regressions: written before fixes."""
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import pytest
from core.project import ROOT
from core.router.router import CapabilityRegistry, route_request
from scripts.benchmark import evaluate
from installers import install as lifecycle

def registry():
    return CapabilityRegistry.from_json(ROOT / "core/schemas/capabilities.json")

@pytest.mark.parametrize("flag,value", [("enabled",False),("available",False),("permitted",False),("explicit_only",True)])
def test_disabled_required_domain_is_unmet(flag, value):
    caps = [replace(c, **{flag:value}) if c.id == "document-authoring" else c for c in registry().capabilities]
    result = route_request("Convert PDF to Word", CapabilityRegistry(caps))
    assert "document-authoring" not in result.selected
    assert "document-authoring" in result.unmet
    assert result.clarification_required

@pytest.mark.parametrize("prompt,expected", [
    ("Show Gmail and my meetings", {"gmail","calendar"}),
    ("Compare Gmail messages with current OpenAI news", {"gmail","web-research"}),
])
def test_mixed_source_aliases(prompt, expected):
    assert expected <= set(route_request(prompt, registry()).selected)

@pytest.mark.parametrize("cases", [
    [None],
    [{"id":"bad","request":"hello","must_include":"","allowed":""}],
    [{"id":"bad","request":"hello","must_include":[]}]*2,
    [{"id":"bad","request":None,"must_include":[]}],
])
def test_malformed_benchmark_is_rejected(cases):
    with pytest.raises(ValueError):
        evaluate(cases, registry())

def test_malformed_benchmark_cli_exit_two(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text("[null]")
    run = subprocess.run([sys.executable, str(ROOT / "scripts/benchmark.py"), "--dataset", str(path)], capture_output=True, text=True)
    assert run.returncode == 2
    assert "Traceback" not in run.stderr
    assert "error" in json.loads(run.stdout)

def test_corrupt_previous_snapshot_blocks_rollback(tmp_path, monkeypatch):
    workspace, home, state = (tmp_path / p for p in ("workspace","home","state"))
    first = lifecycle.install("claude","workspace",workspace,home,state)
    monkeypatch.setattr(lifecycle, "VERSION", "2.0.0-rc2.audit")
    second = lifecycle.install("claude","workspace",workspace,home,state)
    path = state / "records" / (first["identity"] + ".json")
    record = json.loads(path.read_text())
    record["previous"]["snapshot"] = None
    path.write_text(json.dumps(record))
    dest = Path(second["destination"])
    before = lifecycle.tree_hash(dest)
    with pytest.raises((ValueError, RuntimeError)):
        lifecycle.uninstall(state, runtime="claude",scope="workspace",workspace=workspace,home=home,rollback=True)
    assert lifecycle.tree_hash(dest) == before

def test_cross_volume_first_install_refused_before_writes(tmp_path, monkeypatch):
    # Fault injection covers volume preflight; no second physical volume is available locally.
    workspace, home, state = (tmp_path / p for p in ("workspace","home","state"))
    workspace.mkdir()
    home.mkdir()
    real_stat = Path.stat
    def device(path):
        return 2 if Path(path) == state else 1
    monkeypatch.setattr(lifecycle, "_device", device, raising=False)
    with pytest.raises(ValueError, match="filesystem"):
        lifecycle.install("claude","workspace",workspace,home,state)
    assert not state.exists()
    assert list(workspace.iterdir()) == []

def test_generated_text_uses_lf_only(built):
    for path in list(built.rglob("*.json")) + list(built.rglob("openai.yaml")):
        assert b"\r" not in path.read_bytes(), path

def test_all_archives_include_notice(release):
    import zipfile
    notice = (ROOT / "LICENSE").read_bytes().replace(b"\r\n", b"\n")
    for path in release.glob("*.zip"):
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist() if Path(n).name == "LICENSE"]
            assert names, path.name
            assert any(z.read(n).replace(b"\r\n",b"\n") == notice for n in names)

def test_snapshot_check_detects_stale_extra(tmp_path, monkeypatch, capsys, built):
    import shutil
    from scripts import sync_marketplaces as sync
    repo = tmp_path / "repo"
    shutil.copytree(built / "marketplace", repo)
    extra = repo / "plugins/ai-core-operating-protocol/skills/ai-core-operating-protocol/obsolete.txt"
    extra.write_text("stale")
    monkeypatch.setattr(sync, "ROOT", repo)
    monkeypatch.setattr(sync, "build", lambda: built)
    monkeypatch.setattr(sys, "argv", ["sync_marketplaces.py"])
    assert sync.main() == 1
    assert extra.exists()

@pytest.mark.parametrize("field", ["id", "layer"])
def test_bad_registry_types_are_controlled(tmp_path, field):
    data = {"id":"x","layer":"domain","description":"Example","keywords":[]}
    data[field] = []
    path = tmp_path / "registry.json"
    path.write_text(json.dumps([data]))
    with pytest.raises(ValueError):
        CapabilityRegistry.from_json(path)

def test_missing_filesystem_root_is_controlled(tmp_path, monkeypatch):
    monkeypatch.setattr(lifecycle, "checked", lambda p: Path(p))
    monkeypatch.setattr(Path, "exists", lambda p: False)
    with pytest.raises(ValueError, match="filesystem root"):
        lifecycle._device(tmp_path / "absent")

@pytest.mark.parametrize("prompt,unexpected", [
    ("Read the newsletter in my Gmail inbox", "web-research"),
    ("Summarize the release announcement email in my Gmail inbox", "web-research"),
    ("Explain the event handler in my GitHub repository", "calendar"),
])
def test_aliases_do_not_introduce_unrelated_sources(prompt, unexpected):
    assert unexpected not in route_request(prompt, registry()).selected
