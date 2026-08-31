"""Reference-router benchmark; never a native LLM activation evaluation."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.project import ROOT
from core.router.router import CapabilityRegistry, route_request


def evaluate(cases, registry):
    if not isinstance(cases, list) or not cases:
        raise ValueError("Empty or invalid benchmark dataset")
    identities = set()
    for case in cases:
        if not isinstance(case, dict) or not {"id", "request", "must_include"} <= case.keys():
            raise ValueError("Each benchmark case needs id, request and must_include")
        if not isinstance(case["id"], str) or not case["id"].strip() or case["id"] in identities or not isinstance(case["request"], str):
            raise ValueError("Invalid/duplicate case id or request")
        identities.add(case["id"])
        for field in ("must_include", "must_not_include", "allowed"):
            if field in case:
                labels = case[field]
                if not isinstance(labels, list) or any(not isinstance(label, str) or not label.strip() for label in labels) or len(labels) != len(set(labels)):
                    raise ValueError("Benchmark labels must be arrays of unique nonempty strings")
        if set(case["must_include"]) & set(case.get("must_not_include", [])) or set(case.get("allowed", [])) & set(case.get("must_not_include", [])):
            raise ValueError("Conflicting benchmark labels")
    failures = []
    extra_count = missing_count = 0
    selected_count = required_count = allowed_selected = required_selected = 0
    complete_labels = all("allowed" in c for c in cases)
    for case in cases:
        selected = set(route_request(case["request"], registry).selected)
        expected = set(case["must_include"])
        if "allowed" in case and not expected <= set(case["allowed"]):
            raise ValueError("Required labels must be allowed")
        selected_count += len(selected)
        required_count += len(expected)
        required_selected += len(selected & expected)
        allowed_selected += len(selected & set(case.get("allowed", [])))
        missing = expected - selected
        extra = selected - set(case["allowed"]) if "allowed" in case else selected & set(case.get("must_not_include", []))
        extra_count += len(extra)
        missing_count += len(missing)
        if missing or extra:
            failures.append({"id": case["id"], "missing": sorted(missing), "unexpected": sorted(extra)})
    return {"cases": len(cases), "passed": len(cases)-len(failures), "failed": len(failures),
            "compliance": (len(cases)-len(failures))/len(cases), "unexpected_selections": extra_count,
            "missing_selections": missing_count, "complete_allowed_labels": complete_labels,
            "allowed_precision": (allowed_selected / selected_count if selected_count else 1.0) if complete_labels else None,
            "required_recall": required_selected / required_count if required_count else 1.0,
            "scope": "reference-router only", "failures": failures}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=ROOT / "tests/routing/golden.json")
    args = parser.parse_args()
    try:
        result = evaluate(json.loads(args.dataset.read_text(encoding="utf-8")), CapabilityRegistry.from_json(ROOT / "core/schemas/capabilities.json"))
        print(json.dumps(result, indent=2))
        return int(result["failed"] > 0)
    except (ValueError, KeyError, OSError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
