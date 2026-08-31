from pathlib import Path
from installers.install import install, uninstall


def test_install_is_additive_and_uninstall_restores_collision(tmp_path):
    home = tmp_path / "home"
    workspace = tmp_path / "work"
    state = tmp_path / "state"
    old = home / ".claude/skills/ai-core-operating-protocol"
    old.mkdir(parents=True)
    (old / "SKILL.md").write_text("old-version")

    record = install("claude", "user", workspace, home, state, replace=True)
    dest = Path(record["destination"])
    assert dest.exists()
    assert "ai-core-operating-protocol" in dest.as_posix()
    assert record["backup"] is not None
    assert Path(record["backup"]).joinpath("SKILL.md").read_text() == "old-version"

    result = uninstall(state, runtime="claude", scope="user", workspace=workspace, home=home)
    assert result["status"] == "restored-backup"
    assert dest.joinpath("SKILL.md").read_text() == "old-version"


def test_workspace_gemini_uses_interoperable_agents_path(tmp_path):
    home = tmp_path / "home"
    workspace = tmp_path / "work"
    state = tmp_path / "state"
    record = install("gemini", "workspace", workspace, home, state)
    assert Path(record["destination"]) == workspace / ".agents/skills/ai-core-operating-protocol"
