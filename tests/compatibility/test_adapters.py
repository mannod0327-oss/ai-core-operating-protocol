from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"


def test_openai_plugin_package(built):
    p = built / "openai/plugin/ai-core-operating-protocol/.codex-plugin/plugin.json"
    assert p.exists()
    data = json.loads(p.read_text())
    assert data["name"] == "ai-core-operating-protocol"
    assert (p.parent.parent / "skills/ai-core-operating-protocol/SKILL.md").exists()


def test_claude_plugin_package(built):
    p = built / "claude/plugin/ai-core-operating-protocol/.claude-plugin/plugin.json"
    assert p.exists()
    data = json.loads(p.read_text())
    assert data["name"] == "ai-core-operating-protocol"
    assert (p.parent.parent / "skills/ai-core-operating-protocol/SKILL.md").exists()


def test_gemini_and_antigravity_workspace_packages_use_agents_alias(built):
    for runtime in ("gemini", "antigravity", "generic"):
        assert (built / runtime / "workspace/.agents/skills/ai-core-operating-protocol/SKILL.md").exists()


def test_generated_marketplace_preserves_identity_and_canonical_bytes(built):
    canonical = ROOT / "skills/ai-core-operating-protocol/SKILL.md"
    market = built / "marketplace"
    combined = market / "plugins/ai-core-operating-protocol/skills/ai-core-operating-protocol/SKILL.md"
    assert combined.exists()
    assert combined.read_bytes() == canonical.read_bytes()
    openai_market = json.loads((market / ".agents/plugins/marketplace.json").read_text())
    claude_market = json.loads((market / ".claude-plugin/marketplace.json").read_text())
    assert openai_market["plugins"][0]["name"] == "ai-core-operating-protocol"
    assert claude_market["plugins"][0]["name"] == "ai-core-operating-protocol"
    assert (ROOT / "plugins/ai-core-operating-protocol/.codex-plugin/plugin.json").exists()
    assert (ROOT / "plugins/ai-core-operating-protocol/.claude-plugin/plugin.json").exists()
