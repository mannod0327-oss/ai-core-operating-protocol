import os
from pathlib import Path
import subprocess
import sys
import json
import pytest
from core.project import ADAPTERS, ROOT
from installers.install import checked, install, plan, verify, uninstall, runtime_destination

@pytest.mark.parametrize("runtime", list(ADAPTERS["runtimes"]))
@pytest.mark.parametrize("scope", ["user", "workspace"])
def test_every_adapter_lifecycle_isolated(tmp_path, runtime, scope):
    workspace = tmp_path / "workspace"
    home = tmp_path / "home"
    state = tmp_path / "state"
    workspace.mkdir()
    home.mkdir()
    sentinel = tmp_path / "external.txt"
    sentinel.write_bytes(b"untouched")
    configs = [workspace / name for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md")]
    for p in configs:
        p.write_bytes(b"user config")
    result = install(runtime, scope, workspace, home, state)
    assert result["status"] == "installed"
    assert verify(runtime, scope, workspace, home, state)["status"] == "verified"
    uninstall(state, runtime=runtime, scope=scope, workspace=workspace, home=home)
    assert sentinel.read_bytes() == b"untouched"
    assert all(p.read_bytes() == b"user config" for p in configs)

def test_plan_does_not_create_roots(tmp_path):
    workspace, home, state = (tmp_path / p for p in ("new-workspace", "new-home", "new-state"))
    assert plan("claude", "workspace", workspace, home, state)["status"] == "plan"
    assert not workspace.exists() and not home.exists() and not state.exists()

def test_traversal_rejected(tmp_path):
    with pytest.raises(ValueError):
        checked(tmp_path / ".." / "outside")

@pytest.mark.skipif(os.name != "nt", reason="Windows-only drive and UNC semantics")
@pytest.mark.parametrize("bad", ["C:relative", "\\\\server\\share"])
def test_windows_ambiguous_root_rejected(bad):
    with pytest.raises(ValueError):
        checked(Path(bad))

def test_reparse_or_symlink_boundary_rejected(tmp_path):
    external = tmp_path / "external"
    external.mkdir()
    sentinel = external / "keep.txt"
    sentinel.write_bytes(b"keep")
    link = tmp_path / "linked"
    if os.name == "nt":
        # Only a new fixture junction is created. No delete/move shell is used.
        quoted_link = str(link).replace("'", "''")
        quoted_target = str(external).replace("'", "''")
        cmd = f"New-Item -ItemType Junction -Path '{quoted_link}' -Target '{quoted_target}' | Out-Null"
        completed = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True)
        assert completed.returncode == 0
    else:
        link.symlink_to(external, target_is_directory=True)
    with pytest.raises(ValueError):
        checked(link / "child")
    assert sentinel.read_bytes() == b"keep"

def test_cli_list_installs_does_not_change_tree(tmp_path):
    workspace, home, state = (tmp_path / p for p in ("workspace", "home", "state"))
    install("claude", "workspace", workspace, home, state)
    run = subprocess.run([sys.executable, str(ROOT / "installers/install.py"), "claude",
        "--state-dir", str(state), "--action", "list-installs"], capture_output=True, text=True)
    assert run.returncode == 0
    assert json.loads(run.stdout)["installs"][0]["runtime"] == "claude"
