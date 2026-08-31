from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def test_no_obvious_secrets_in_repository():
    bad = re.compile(r"(sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (RSA|OPENSSH|EC) PRIVATE KEY-----)")
    hits=[]
    for p in ROOT.rglob("*"):
        if p.is_file() and ".git" not in p.parts and p.suffix not in {".zip", ".pyc"}:
            try: text=p.read_text(errors="ignore")
            except Exception: continue
            if bad.search(text): hits.append(str(p))
    assert not hits, hits


def test_installer_has_no_blind_recursive_delete():
    p = ROOT / "installers/install.py"
    text = p.read_text()
    assert "rm -rf" not in text
    assert "shutil.rmtree(destination" not in text
