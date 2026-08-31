import pytest
from scripts.validate_skill import validate

@pytest.mark.parametrize("front", [
    "name: bad\nname: duplicate\ndescription: Fine",
    "name: Invalid Name\ndescription: Fine",
    "name: okay\ndescription: [array]",
    "name: okay\ndescription:",
    "name: okay\ndescription: Fine\nunknown: true",
])
def test_invalid_frontmatter_fails(tmp_path, front):
    (tmp_path / "SKILL.md").write_text("---\n" + front + "\n---\nBody", encoding="utf-8")
    assert validate(tmp_path)

def test_missing_reference_fails(tmp_path):
    (tmp_path / "SKILL.md").write_text("---\nname: okay\ndescription: Fine\n---\nRead references/missing.md", encoding="utf-8")
    assert validate(tmp_path)

def test_empty_body_fails(tmp_path):
    (tmp_path / "SKILL.md").write_text("---\nname: okay\ndescription: Fine\n---\n", encoding="utf-8")
    assert validate(tmp_path)
