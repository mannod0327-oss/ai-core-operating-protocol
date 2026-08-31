"""Check generated repository snapshots. No automatic source rewrites or installs."""
from pathlib import Path
import argparse
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.project import ROOT, NAME
from scripts.build_adapters import build
from scripts.package_release import files_under


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Explicit maintainer-only mechanical refresh of generated source snapshots")
    args = parser.parse_args()
    generated = build() / "marketplace"
    expected = files_under(generated)
    differences = [n for n, b in expected.items() if not (ROOT / n).is_file() or (ROOT / n).read_bytes() != b]
    plugin_root = ROOT / "plugins" / NAME
    actual = {"plugins/" + NAME + "/" + n for n in files_under(plugin_root)} if plugin_root.exists() else set()
    extras = sorted(actual - set(expected))
    if extras:
        print("Unexpected generated files; review and move them outside the plugin before refresh:\n" + "\n".join(extras))
        return 1
    if args.refresh:
        from installers.install import checked
        for name in differences:
            target = checked(ROOT / name)
            if not target.is_relative_to(ROOT):
                raise ValueError("Generated target escaped source")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(expected[name])
        print(f"Refreshed {len(differences)} generated snapshot files; canonical source unchanged")
        return 0
    if differences:
        print("Snapshot drift (source ZIP uses freshly generated copies):\n" + "\n".join(differences))
        return 1
    print("PASS: generated snapshots match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
