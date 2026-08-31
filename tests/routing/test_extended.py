from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import pytest
from core.project import ROOT
from core.router.router import CapabilityRegistry, Capability, route_request
from scripts.benchmark import evaluate

def registry():
    return CapabilityRegistry.from_json(ROOT / "core/schemas/capabilities.json")

def test_holdout_complete_allowed_labels():
    cases = json.loads((ROOT / "tests/routing/holdout.json").read_text(encoding="utf-8"))
    assert len({c["request"] for c in cases}) == len(cases)
    result = evaluate(cases, registry())
    assert result["complete_allowed_labels"]
    assert result["failed"] == 0, result["failures"]

@pytest.mark.parametrize("flag", ["available", "enabled", "permitted"])
def test_unavailable_source_not_fabricated(flag):
    caps = [replace(c, **{flag: False}) if c.id == "gmail" else c for c in registry().capabilities]
    result = route_request("Gmail", CapabilityRegistry(caps))
    assert "gmail" not in result.selected
    assert "gmail" in result.unmet
    assert result.clarification_required

def test_explicit_only_requires_explicit_id_not_keyword():
    cap = Capability("gmail", "source", "Mail", ("gmail",), explicit_only=True)
    reg = CapabilityRegistry([cap])
    assert route_request("gmail", reg).selected == []
    assert route_request("gmail", reg, explicit_ids=["gmail"]).selected == ["gmail"]

def test_explicit_cannot_enable_forbidden_capability():
    cap = Capability("gmail", "source", "Mail", ("gmail",), enabled=False)
    assert route_request("gmail", CapabilityRegistry([cap]), explicit_ids=["gmail"]).selected == []

def test_ties_are_deterministic():
    a = Capability("a", "process", "A", ("test",))
    b = Capability("b", "process", "B", ("test",))
    assert route_request("test", CapabilityRegistry([a,b])).selected == ["a"]
    assert route_request("test", CapabilityRegistry([b,a])).selected == ["a"]

@pytest.mark.parametrize("mark", ["'", "‘", "’", "ʻ", "ʼ"])
def test_unicode_apostrophes(mark):
    assert route_request("Barcha fayllarni o" + mark + "chir", registry()).intent.risk == "destructive"

def test_advisory_negation():
    assert route_request("Faqat tushuntir, faylni o‘chirma", registry()).intent.risk == "read"

def test_benchmark_failed_case_returns_nonzero(tmp_path):
    data = tmp_path / "bad.json"
    data.write_text(json.dumps([{"id":"intentional-failure","request":"Salom","must_include":["gmail"],"allowed":["gmail"]}]))
    run = subprocess.run([sys.executable, str(ROOT / "scripts/benchmark.py"), "--dataset", str(data)], capture_output=True, text=True)
    assert run.returncode == 1
    assert json.loads(run.stdout)["failed"] == 1

def test_benchmark_empty_rejected():
    with pytest.raises(ValueError):
        evaluate([], registry())
