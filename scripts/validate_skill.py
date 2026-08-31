"""Structural validation only, not proof of model activation."""
from pathlib import Path
import re
import sys
import yaml


class UniqueLoader(yaml.SafeLoader):
    pass


def mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise ValueError("Duplicate or non-string YAML key")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def validate(root):
    root = Path(root)
    errors = []
    try:
        text = (root / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
        if not match:
            return ["Missing frontmatter"]
        meta = yaml.load(match[1], Loader=UniqueLoader)
        if not isinstance(meta, dict):
            return ["Frontmatter is not a mapping"]
        if set(meta) - {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}:
            errors.append("Unsupported frontmatter key")
        if not text[match.end():].strip():
            errors.append("Empty skill body")
        if not isinstance(meta.get("name"), str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", meta["name"]) or len(meta["name"]) > 64:
            errors.append("Invalid name")
        if not isinstance(meta.get("description"), str) or not 1 <= len(meta["description"].strip()) <= 1024:
            errors.append("Invalid description")
        if "[TODO:" in text:
            errors.append("Unfinished scaffold")
        for ref in re.findall(r"references/[\w.-]+\.md", text):
            p = root / ref
            if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(root.resolve()):
                errors.append("Invalid reference: " + ref)
        if (root / "agents/openai.yaml").exists():
            config = yaml.load((root / "agents/openai.yaml").read_text(encoding="utf-8"), Loader=UniqueLoader)
            if not 25 <= len(config["interface"]["short_description"]) <= 64:
                errors.append("OpenAI short description length")
            if config.get("policy", {}).get("allow_implicit_invocation") is not True:
                errors.append("Implicit invocation not enabled")
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError) as exc:
        errors.append(str(exc))
    return errors


if __name__ == "__main__":
    issues = validate(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "skills/ai-core-operating-protocol")
    print("\n".join(issues) if issues else "PASS (structure only)")
    raise SystemExit(bool(issues))
