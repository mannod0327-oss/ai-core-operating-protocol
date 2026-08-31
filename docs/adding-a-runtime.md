# Adding a runtime

1. Verify the exact host/surface documentation and record URL/date. Do not infer mobile
   support from desktop or CLI behavior.
2. Add a runtime entry to core/adapters.json with safe relative user/workspace paths,
   surface and metadata transform. Unknown runtime identifiers fail before writes.
3. Keep behavior only in skills/ai-core-operating-protocol; build copies it automatically.
4. Add layout, safe destination, lifecycle and negative contract tests.
5. Register a separate runtime-evidence.json record; leave version and live evidence unknown
   until actually observed. A generated artifact is not a support badge.
6. Run parser, tests, reproducible package and drift gates. Source ZIP generation injects
   current generated marketplace snapshots without changing the working source.
7. Confirm real discovery/activation/outcomes with authorization before claiming support.

No fallback writes into AGENTS.md are implemented. Host metadata schemas may differ;
extend the specific transform, not universal canonical frontmatter.
