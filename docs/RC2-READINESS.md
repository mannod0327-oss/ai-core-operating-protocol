# RC2 readiness — local candidate, not stable

Date: 2026-08-31. RC1-derived planning archive retained unchanged. No GitHub publish, real agent-home
installation, paid model request or account-level import performed.

## Completed locally

- Installer: destination ownership, independent state records, shared-destination conflicts,
  dry-run default, user-edit protection, source/staging hashes, idempotence, upgrade/rollback,
  retained snapshots, transaction journals, controlled damaged-record errors.
- Reference router: empty/partial catalog, unavailable/disabled/explicit-only entries, mixed
  domains/sources, identity dedup, deterministic ties, Unicode apostrophes and lexical fixes.
- Canonical skill: narrow trigger, host-native selection, no recursion, authorization boundary,
  untrusted content separation and outcome-based verification.
- Packaging: one version source, eight filesystem adapter mappings, standalone and dedicated
  Claude upload ZIPs, two plugin formats, marketplace and source distribution.
- Tests build their own fixtures; repeated packages have equal SHA-256 and source is unchanged.
- Before final publication audit, Windows Python 3.12.13 test run: **96 passed**, including 17 independently authored lifecycle
  tests and all 16 runtime/scope combinations in fake homes. Real Windows junction rejection
  passed. Independent final recheck: 17/17 passed; no regressions found in the three fixes.
- A later independent publication audit found additional defects and added new regressions.
  Its findings, fixes and current verification are in [INDEPENDENT-AUDIT.md](INDEPENDENT-AUDIT.md).
- Legacy golden: 120 cases; RC2 fully labeled holdout: 22 cases. These measure the offline
  reference router only. See generated validation report for final benchmark and ZIP checks.
- CI configuration covers Windows/Linux/macOS and Python 3.12/3.13 with pinned development
  dependencies and SHA-pinned actions. No CI publish/deploy step or privileged PR job.

## Audit mapping

B01/B02: contextual destination and per-target records, verified by tampering/multi-owner tests.
B03: hash conflicts preserve user edits; UUID snapshots and no-op repeat install tested.
B04/B05: missing registry and multiple required domain/source capability tests pass.
B06: benchmark returns non-zero for failures and reports full allowed-set precision separately.
B07: sentinel, lifecycle, interrupted-copy, commit-error and real junction behavior tests replace
reliance on string scans alone.
B08: dependency installation and isolated fixtures implemented; remote six-job CI remains NOT RUN.
B09: centralized metadata, pure build, deterministic ZIPs and generated-source drift check.
B10: host evidence is explicitly NOT RUN; it is not falsely marked resolved by package tests.

## Remaining release gates

- T1/T2/T3: local parser/reference/lifecycle evidence exists; not a universal security proof.
- T4: Windows local and fresh-source verification; Linux/macOS/Python 3.13 and remote CI NOT RUN.
- T5: discovery, automatic activation and end-to-end outcomes NOT RUN on all named surfaces.
  Web and actual mobile testing needs the user's account/import interface and device session.
  Paid CLI/API tests require explicit consent. No “100% auto” or “all hosts supported” claim.
- T6: bootstrap <=200 words and metadata-only reference tests; real host token/latency and
  selected-body loading traces are NOT RUN.
- Abrupt kill/power-loss recovery blocks on a journal/lock and requires manual review.
  Normal caught failures roll back; automatic journal replay is not implemented.
- There is no AGENTS/CLAUDE/GEMINI marked-block bootstrap writer; the optional feature is
  intentionally omitted to preserve user files. Generic hosts without native discovery are unsupported.
- The reference router has no executable capability dependency graph or real connector bindings;
  it does not auto-install missing capabilities.
- Minimum host versions and user account entitlements are unknown. Copilot per-client user scope
  needs live confirmation. Runtime doctor is a path/state plan, not an auth/discovery diagnostic.
- A real private security-reporting channel must be selected before public release.

## Handoff

This is a **partial cross-agent RC**, suitable for review and isolated testing, not a certification
of native automatic activation. A separately approved draft/prerelease GitHub publication may
state these limitations; stable/support badges must wait for live evidence and the CI matrix.
Publishing additionally needs explicit owner, repository, visibility, branch/tag and release choice.

## Action provenance

CI action pins were checked against official release commits:
[checkout v4.2.2](https://github.com/actions/checkout/commit/11bd71901bbe5b1630ceea73d27597364c9af683),
[setup-python v5.6.0](https://github.com/actions/setup-python/commit/a26af69be951a213d495a4c3e4e4022e16d87065).
Pins are reproducibility controls, not an assertion that these are the newest releases.
