# Contributing

1. Keep the canonical behavior in `skills/ai-core-operating-protocol`; adapters must not fork it.
2. Add/modify a failing regression test before behavior changes.
3. Verify current official runtime docs before changing discovery paths.
4. Install requirements-dev.txt; run `python -m pytest -q`, `python scripts/validate_skill.py`, and both benchmark datasets.
5. Keep bootstrap/context overhead small and document compatibility limitations.
6. After changing canonical skill/metadata, explicitly run `python scripts/sync_marketplaces.py --refresh` to mechanically refresh generated repository snapshots. Review that diff. Normal build/package/check commands never rewrite source.
   Extra files in the owned generated plugin subtree cause both check and refresh to fail.
   Review and move obsolete files out of that subtree yourself; refresh never deletes them.
   Keep generated text LF-only; .gitattributes fixes checkout newlines across operating systems.
7. GitHub Actions are SHA-pinned to verified release commits; Dependabot proposes updates monthly. Review changes and rerun the matrix before merging. Dependency pins are not a security guarantee or a hash-locked supply chain.
