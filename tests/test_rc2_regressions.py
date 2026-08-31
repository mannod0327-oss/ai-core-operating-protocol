from pathlib import Path
import json
import pytest

from core.router.router import Capability, CapabilityRegistry, route_request
from installers.install import install, uninstall

ROOT = Path(__file__).resolve().parents[1]


def test_empty_registry_is_a_normal_missing_capability():
    result = route_request("Gmail inboximni ko'rsat", CapabilityRegistry([]))
    assert result.selected == []
    assert result.unmet


def test_pdf_to_word_requires_two_domain_capabilities():
    registry = CapabilityRegistry.from_json(ROOT / "core/schemas/capabilities.json")
    assert {"pdf-processing", "document-authoring"} <= set(route_request("PDFdan Word hujjat tayyorla", registry).selected)


def test_duplicate_identity_rejected():
    cap = Capability("one", "domain", "test", ("test",))
    with pytest.raises(ValueError):
        CapabilityRegistry([cap, cap])


def test_repeat_install_no_new_backup(tmp_path):
    args = ("claude", "user", tmp_path / "work", tmp_path / "home", tmp_path / "state")
    first = install(*args)
    second = install(*args)
    assert second["status"] == "unchanged"
    assert second["destination"] == first["destination"]


def test_post_install_edit_not_deleted(tmp_path):
    home, work, state = (tmp_path / n for n in ("home", "work", "state"))
    record = install("claude", "user", work, home, state)
    file = Path(record["destination"]) / "SKILL.md"
    file.write_text("user changes", encoding="utf-8")
    with pytest.raises((ValueError, RuntimeError)):
        uninstall(state, runtime="claude", scope="user", workspace=work, home=home)
    assert file.read_text() == "user changes"


def test_unknown_workspace_runtime_never_writes(tmp_path):
    with pytest.raises(ValueError):
        install("unknown", "workspace", tmp_path / "work", tmp_path / "home", tmp_path / "state")
    assert not (tmp_path / "work").exists()
