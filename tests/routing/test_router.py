import json
from pathlib import Path

from core.router.router import CapabilityRegistry, route_request

ROOT = Path(__file__).resolve().parents[2]


def load_registry():
    return CapabilityRegistry.from_json(ROOT / "core/schemas/capabilities.json")


def test_metadata_only_registry_loads_without_skill_bodies():
    registry = load_registry()
    assert registry.capabilities
    assert all(c.body is None for c in registry.capabilities)


def test_bug_request_selects_debugging_repo_and_verification_without_unrelated_tools():
    result = route_request("GitHubdagi Python loyihamdagi failing testni topib tuzat", load_registry())
    assert "systematic-debugging" in result.selected
    assert "github-repository" in result.selected
    assert "code-verification" in result.selected
    assert "gmail" not in result.selected
    assert "pdf-processing" not in result.selected


def test_private_email_routes_to_gmail_not_web():
    result = route_request("Inboximdagi bugungi muhim xatlarni ko'rsat", load_registry())
    assert "gmail" in result.selected
    assert "web-research" not in result.selected


def test_current_public_research_uses_web():
    result = route_request("Bugungi OpenAI yangiliklarini tekshir", load_registry())
    assert "web-research" in result.selected
    assert result.intent.freshness is True


def test_irreversible_action_is_high_risk():
    result = route_request("Production bazadagi barcha userlarni o'chir", load_registry())
    assert result.intent.risk == "destructive"
    assert result.requires_human_control is True


def test_duplicate_identity_is_suppressed_without_losing_distinct_domains():
    result = route_request("PDF faylni tahlil qilib Word hujjat qil", load_registry())
    assert len(result.selected) == len(set(result.selected))
    assert {"pdf-processing", "document-authoring"} <= set(result.selected)


def test_golden_dataset():
    registry = load_registry()
    data = json.loads((ROOT / "tests/routing/golden.json").read_text())
    assert len(data) >= 100
    failures = []
    for case in data:
        result = route_request(case["request"], registry)
        selected = set(result.selected)
        missing = set(case["must_include"]) - selected
        forbidden = set(case.get("must_not_include", [])) & selected
        if missing or forbidden:
            failures.append((case["id"], sorted(missing), sorted(forbidden), result.selected))
    assert not failures, failures[:10]
