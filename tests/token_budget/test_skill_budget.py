from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills/ai-core-operating-protocol/SKILL.md"


def test_skill_exists():
    assert SKILL.exists()


def test_frontmatter_has_name_and_description():
    text = SKILL.read_text()
    assert text.startswith("---\n")
    front = text.split("---", 2)[1]
    assert re.search(r"^name:\s*ai-core-operating-protocol$", front, re.M)
    assert re.search(r"^description:\s*.+$", front, re.M)


def test_bootstrap_section_is_under_200_words():
    text = SKILL.read_text()
    marker = "## Bootstrap"
    end = "## Routing"
    section = text.split(marker,1)[1].split(end,1)[0]
    words = re.findall(r"\b[\w'-]+\b", section)
    assert len(words) <= 200


def test_skill_is_under_500_lines():
    assert len(SKILL.read_text().splitlines()) < 500


def test_references_are_one_level_deep_and_exist():
    text = SKILL.read_text()
    refs = re.findall(r"references/[a-z0-9-]+\.md", text)
    assert refs
    for ref in refs:
        assert (ROOT / "skills/ai-core-operating-protocol" / ref).exists(), ref
