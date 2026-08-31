import hashlib
import json
from pathlib import Path
import zipfile
import pytest
from core.project import ROOT, NAME, VERSION, ADAPTERS
from installers.install import tree_hash
from scripts.package_release import package, zip_files
from scripts.validate_skill import validate

def test_release_zips_integrity_and_counts(release):
    archives = sorted(release.glob("*.zip"))
    assert len(archives) == 14
    for path in archives:
        assert path.stat().st_size < 25_000_000
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            assert len(z.namelist()) == len(set(n.casefold() for n in z.namelist()))
            assert all(".." not in Path(n).parts and not n.startswith("/") for n in z.namelist())
    sums = {line.split()[1]: line.split()[0] for line in (release / "SHA256SUMS.txt").read_text().splitlines()}
    assert all(sums[p.name] == hashlib.sha256(p.read_bytes()).hexdigest() for p in archives)

def test_source_package_is_clean_and_contains_planning(release):
    with zipfile.ZipFile(release / f"{NAME}-source-v{VERSION}.zip") as z:
        names = z.namelist()
        assert "docs/planning/TZ-CROSS-AGENT.md" in names
        assert "requirements-dev.txt" in names
        assert all(not any(x in Path(n).parts for x in ("release", "dist", ".git", "__pycache__", ".pytest_cache")) for n in names)
        manifest = json.loads(z.read(f"plugins/{NAME}/.codex-plugin/plugin.json"))
        assert manifest["version"] == VERSION
        assert z.read(f"skills/{NAME}/SKILL.md") == z.read(f"plugins/{NAME}/skills/{NAME}/SKILL.md")

def test_repeated_builds_identical_and_source_unchanged(release, tmp_path):
    before = {d: tree_hash(ROOT / d) for d in ("skills", "plugins", ".agents", ".claude-plugin", "scripts")}
    second = package(tmp_path / "second")
    assert (release / "SHA256SUMS.txt").read_bytes() == (second / "SHA256SUMS.txt").read_bytes()
    assert before == {d: tree_hash(ROOT / d) for d in before}

def test_existing_release_not_overwritten(release):
    before = tree_hash(release)
    with pytest.raises(ValueError):
        package(release)
    assert tree_hash(release) == before

@pytest.mark.parametrize("name", ["../escape", "/absolute", "a\\b", "C:/escape"])
def test_unsafe_zip_names_rejected(tmp_path, name):
    with pytest.raises(ValueError):
        zip_files({name: b"no"}, tmp_path / "unsafe.zip")
    assert not (tmp_path / "unsafe.zip").exists()

def test_generated_skills_pass_parser(built):
    skills = list(built.rglob("SKILL.md"))
    assert len(skills) == 13
    for skill in skills:
        assert validate(skill.parent) == [], (skill, validate(skill.parent))
