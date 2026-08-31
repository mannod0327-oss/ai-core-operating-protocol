# Changelog

## 2.0.0-rc2 — 2026-08-31 (local candidate, not published)

Final pre-publication audit corrections (original local archives retained):
- Reject inconsistent previous rollback records and cross-filesystem state before writes.
- Report ineligible required domains; retain calendar aliases and complementary public sources.
- Reject malformed benchmark labels/cases and malformed registry identity types.
- Detect obsolete generated files, normalize metadata newlines and ZIP origin metadata.
- Include the original MIT notice in every skill/plugin/runtime distribution.

- Fixed manifest target trust, shared ownership, user-edit preservation and no-op installation.
- Added staging integrity checks, transaction locks/journals, retained snapshots and rollback.
- Fixed partial registries, explicit-only/disabled capabilities, mixed domains/sources and Unicode routing.
- Added 22 fully labeled reference cases and benchmark failure exits; no native accuracy claim.
- Centralized version/adapter metadata and deterministic source-pure packaging (14 artifacts).
- Added separate standalone/Claude upload/plugin variants plus Cursor/Copilot/OpenCode layouts.
- Added isolated fixtures, independent lifecycle tests, strict parser and cross-OS CI configuration.
- Live discovery/activation, real mobile tests and remote CI remain NOT RUN; abrupt-kill recovery is manual.

## 2.0.0-rc1 — 2026-08-31
- Re-architected v1.1 into a vendor-neutral canonical Agent Skill.
- Added generated adapters for OpenAI/Codex, Claude Code, Gemini CLI, Antigravity, and generic runtimes.
- Added deterministic metadata-only reference router and 120-case golden benchmark.
- Added token, compatibility, installer, security, and packaging tests.
- Added reversible installer/uninstaller and release packaging with SHA-256 checksums.
- Added runtime compatibility, security, routing, testing, and token-efficiency documentation.
