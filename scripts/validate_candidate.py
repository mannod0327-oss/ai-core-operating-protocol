"""Run local evidence gates and write a sanitized report outside the source tree."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.project import ROOT, VERSION
from installers.install import checked
from scripts.package_release import files_under

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    report_path = checked(args.report)
    if report_path.is_relative_to(ROOT):
        raise ValueError("Keep validation output outside the source tree")
    if report_path.exists():
        raise ValueError("Preserve existing validation reports; choose a new path")
    commands = [
        ["scripts/validate_skill.py"],
        ["-m", "pytest", "-q", "-p", "no:cacheprovider"],
        ["scripts/benchmark.py"],
        ["scripts/benchmark.py", "--dataset", "tests/routing/holdout.json"],
        ["scripts/sync_marketplaces.py"],
    ]
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
    results = []
    for args_list in commands:
        run = subprocess.run([sys.executable, "-X", "utf8", *args_list], cwd=ROOT,
                             env=environment, text=True, encoding="utf-8", capture_output=True, timeout=180)
        output = (run.stdout + run.stderr).replace(str(ROOT), "<source>").replace(ROOT.as_posix(), "<source>")
        results.append({"command": "python " + " ".join(args_list), "exit_code": run.returncode, "output": output})
        print(json.dumps({"command": args_list, "exit_code": run.returncode}), flush=True)
    canonical = files_under(ROOT / "skills/ai-core-operating-protocol")
    data = {"candidate": VERSION, "os": platform.system(), "python": platform.python_version(),
            "evidence_scope": "local static/reference/fake-home tests only",
            "native_host_activation": "NOT_RUN",
            "checks": results, "passed": all(r["exit_code"] == 0 for r in results),
            "canonical_sha256": {k: hashlib.sha256(v).hexdigest() for k,v in canonical.items()}}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return 0 if data["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
