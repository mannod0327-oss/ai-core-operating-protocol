"""Pure-source build into a NEW output directory; never erases an existing tree."""
from pathlib import Path
import json
import shutil
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.project import ROOT, NAME, VERSION, PROJECT, ADAPTERS, runtime_spec, openai_yaml
from installers.install import checked, tree_hash


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def copy_skill(dest, metadata="native"):
    source = ROOT / "skills" / NAME
    expected = tree_hash(source)
    shutil.copytree(source, dest)
    if tree_hash(dest) != expected or tree_hash(source) != expected:
        raise ValueError("Canonical source changed during build")
    if metadata == "openai":
        (dest / "agents").mkdir(exist_ok=True)
        (dest / "agents/openai.yaml").write_text(openai_yaml(), encoding="utf-8", newline="\n")


def plugin_manifest(vendor):
    result = {"name": NAME, "version": VERSION,
              "description": "Select relevant available skills and verify task outcomes.",
              "author": {"name": PROJECT["author"]}, "license": PROJECT["license"]}
    if vendor == "openai":
        result.update({"skills": "./skills/", "interface": {
            "displayName": "AI Core Operating Protocol",
            "shortDescription": "Route relevant skills and verify outcomes",
            "longDescription": "Task-scoped capability routing with progressive disclosure and evidence-based completion.",
            "developerName": PROJECT["author"], "category": "Productivity",
            "capabilities": ["Interactive"], "defaultPrompt": ["Choose relevant capabilities and verify my task outcome."]}})
    return result


def build(output=None):
    output = checked(output or ROOT / "dist" / ("build-" + uuid.uuid4().hex))
    output.mkdir(parents=True, exist_ok=False)
    for runtime in ADAPTERS["runtimes"]:
        spec = runtime_spec(runtime)
        copy_skill(output / runtime / "workspace" / spec["workspace"] / NAME, spec["metadata"])
    copy_skill(output / "standalone" / NAME)
    copy_skill(output / "claude-upload" / NAME)
    for vendor, manifest_dir in (("openai", ".codex-plugin"), ("claude", ".claude-plugin")):
        plugin = output / vendor / "plugin" / NAME
        copy_skill(plugin / "skills" / NAME, "openai" if vendor == "openai" else "native")
        write_json(plugin / manifest_dir / "plugin.json", plugin_manifest(vendor))
    market = output / "marketplace"
    plugin = market / "plugins" / NAME
    copy_skill(plugin / "skills" / NAME, "openai")
    for vendor, directory in (("openai", ".codex-plugin"), ("claude", ".claude-plugin")):
        write_json(plugin / directory / "plugin.json", plugin_manifest(vendor))
    # Preserve the repository's marketplace identifiers, order and policy fields.
    for rel in (".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"):
        data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        for entry in data["plugins"]:
            if entry["name"] == NAME and "version" in entry:
                entry["version"] = VERSION
        write_json(market / rel, data)
    write_json(output / "build-manifest.json", {"name": NAME, "version": VERSION,
               "canonical_hashes": tree_hash(ROOT / "skills" / NAME),
               "evidence": "GENERATED; host activation not tested"})
    return output


if __name__ == "__main__":
    print(build(Path(sys.argv[1]) if len(sys.argv) > 1 else None))
