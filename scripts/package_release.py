"""Deterministic release artifacts; does not mutate source or publish anything."""
from pathlib import Path
import argparse
import hashlib
import json
import stat
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.project import ROOT, NAME, VERSION, ADAPTERS
from installers.install import checked, tree_hash
from scripts.build_adapters import build


def zip_files(files, dest):
    folded = [n.casefold() for n in files]
    if len(folded) != len(set(folded)):
        raise ValueError("Case-colliding package entries")
    for name in files:
        if name.startswith("/") or ".." in Path(name).parts or ":" in name or "\\" in name:
            raise ValueError("Unsafe package entry")
    checked(dest)
    with zipfile.ZipFile(dest, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 8, 31, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            z.writestr(info, content)
    with zipfile.ZipFile(dest) as z:
        if z.testzip() is not None or any(z.read(n) != b for n, b in files.items()):
            raise ValueError("ZIP integrity failure")
    if dest.stat().st_size >= 25_000_000:
        raise ValueError("Artifact exceeds conservative upload budget")


def files_under(root):
    tree_hash(root)
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def package(output=None):
    output = checked(output or ROOT / "release" / VERSION)
    if output.exists() and any(output.iterdir()):
        raise ValueError("Release output must be empty; existing artifacts are preserved")
    output.mkdir(parents=True, exist_ok=True)
    built = build()
    variants = {"skill": built / "standalone", "claude-upload": built / "claude-upload",
                "openai": built / "openai/plugin" / NAME, "claude-plugin": built / "claude/plugin" / NAME,
                "marketplace": built / "marketplace"}
    variants.update({runtime: built / runtime / "workspace" for runtime in ADAPTERS["runtimes"]})
    source = {}
    for directory in ("core", "scripts", "installers", "skills", "tests", "docs", ".github"):
        for name, content in files_under(ROOT / directory).items():
            if "__pycache__" not in Path(name).parts and not name.endswith(".pyc"):
                source[directory + "/" + name] = content
    for name in ("project.json", "requirements-dev.txt", "pytest.ini", ".gitignore", ".gitattributes", "README.md", "CHANGELOG.md", "LICENSE", "SECURITY.md", "CONTRIBUTING.md", "THIRD_PARTY_NOTICES.md", "CODE_OF_CONDUCT.md"):
        source[name] = (ROOT / name).read_bytes()
    source.update(files_under(built / "marketplace"))
    for kind, root in variants.items():
        zip_files(files_under(root), output / f"{NAME}-{kind}-v{VERSION}.zip")
    zip_files(source, output / f"{NAME}-source-v{VERSION}.zip")
    sums = []
    for p in sorted(output.glob("*.zip")):
        sums.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}")
    (output / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8", newline="\n")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    print(package(parser.parse_args().output))
