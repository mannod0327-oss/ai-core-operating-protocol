"""Project-owned metadata, not vendor API definitions."""
import json
import re
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PROJECT = json.loads((ROOT / "project.json").read_text(encoding="utf-8"))
NAME = PROJECT["name"]
VERSION = PROJECT["version"]
ADAPTERS = json.loads((ROOT / "core/adapters.json").read_text(encoding="utf-8"))


def runtime_spec(runtime):
    if runtime not in ADAPTERS["runtimes"]:
        raise ValueError("Unknown filesystem runtime; web/mobile require host import")
    item = ADAPTERS["runtimes"][runtime]
    for scope in ("workspace", "user"):
        path = item[scope]
        if not path or PurePosixPath(path).is_absolute() or ".." in PurePosixPath(path).parts or ":" in path or "\\" in path:
            raise ValueError("Unsafe adapter path")
    return item


def openai_yaml():
    return ('interface:\n  display_name: "AI Core Operating Protocol"\n'
            '  short_description: "Route relevant skills and verify task outcomes"\n'
            'policy:\n  allow_implicit_invocation: true\n')
