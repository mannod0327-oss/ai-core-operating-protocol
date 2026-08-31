# Independent pre-publication audit

Date: 2026-08-31. Candidate: 2.0.0-rc2 (audited local revision).

## Verdict

Reported code/package defects are resolved in the reviewed scope. Three separate agent
review passes independently examined installer safety, reference routing, and release/build
behavior, then rechecked fixes. This is an AI-assisted technical review, not a security
certification or a native host activation test.

The first pass found eight P2 defects and one P3 robustness defect. Rechecking the fixes
found two further P2 regressions; those were also fixed and independently rechecked.
No scoped blocker remained in the final three reviewer responses.

## Findings and disposition

1. **A01 / P2 — inconsistent rollback state.** A null previous snapshot could remove the active
   skill while reporting rollback success. Previous snapshot/record identity, hashes and
   original snapshot consistency are checked before mutation; restored records are validated.
   Direct corrupted-state reproduction now blocks and preserves both tree and record bytes.
2. **A02 / P2 — cross-filesystem lifecycle.** A fresh install could succeed even though subsequent
   snapshot renames would fail across volumes. Plan/install now require destination and state
   on the same filesystem before writes. Use a same-volume --state-dir. This boundary was
   fault-injected; no second physical volume was available.
3. **A03 / P2 — hidden unmet domain.** Word generation disappeared silently when disabled,
   unavailable, unpermitted or explicit-only. Matched domain requirements now survive
   eligibility filtering as unmet needs; flags are not bypassed.
4. **A04 / P2 — lost complementary source.** Gmail plus meetings/news could lose calendar/web.
   Source aliases and independent public clauses retain these complementary requirements.
5. **A05 / P2 — malformed benchmark false success.** String labels could produce 100% PASS;
   null cases raised an uncontrolled traceback. Case shape, unique IDs, label arrays and
   conflicting labels are validated; malformed CLI data returns exit 2.
6. **A06 / P3 — malformed registry type.** List IDs/layers raised TypeError before validation.
   Types are now checked before hashing/membership; the result is controlled ValueError.
7. **A07 / P2 — obsolete generated files invisible.** Snapshot checks compared only expected
   paths. The owned plugin inventory now detects extras. Check and refresh both refuse them
   without altering existing bytes; maintainers explicitly review/move obsolete files.
8. **A08 / P2 — platform newline drift.** Windows CRLF metadata disagreed with Unix LF.
   Generated JSON/YAML and checksum text use LF; .gitattributes controls checkout text.
   ZIP origin metadata is fixed. Unix-newline emulation and repeated archive SHA tests pass;
   this does not substitute for native Linux/macOS CI.
9. **A09 / P2 — license notice absent from install archives.** The original MIT license is
   included in the canonical skill so every distribution retains the notice and copyright.
   All 14 regenerated ZIPs were independently checked.
10. **A10 / P2 — nonexistent volume loop introduced by A02 fix.** Device lookup could ascend
    forever at a missing root. A root-parent guard now returns controlled failure.
    Missing Windows workspace and state drives were independently tested for plan/install.
11. **A11 / P2 — source false positives introduced by A04 fix.** Gmail newsletter/release mail
    gained web, and a GitHub event handler gained calendar. Private clauses and software event
    phrases now retain their source of truth. Positive complementary-source cases still pass.

## Test evidence

Before fixes, 12 of the first 13 new audit regressions failed. After core corrections,
the three release regressions also failed as expected before their corrections.

Final full local run: **118 passed in 159.08 seconds**, Windows / Python 3.12.13.
The baseline had 96 tests; this audit added 22 regression cases.
Golden and development holdout remain 120 and 22 reference-router scenarios respectively.

Independent final rechecks:

- Installer: 44 relevant tests passed; four upgrades/four rollbacks verified; missing-drive
  CLI checks returned controlled exit 2 without creating roots; corrupted state preserved.
- Router: 39 relevant tests passed, five unrelated tests deselected; original positive and
  new negative source cases verified. No arbitrary-language or model routing guarantee.
- Release: all 14 new ZIPs carry the MIT notice and pass CRC; two separate builds have
  equal SHA manifests; LF/origin checks and non-destructive stale-file rejection verified.
  This reviewer did not rerun full pytest or native Linux/macOS.

## Publication boundaries

Native discovery/automatic activation/outcomes in ChatGPT web/mobile, Claude or other hosts
remain NOT RUN. Remote six-job CI remains NOT RUN until an authorized repository is pushed.
Abrupt process-kill recovery is manual and fail-closed; cross-filesystem installation is
explicitly unsupported. No real agent home, account credentials or paid model was touched.

GitHub owner/visibility and authenticated write access must be confirmed before creation/push.
A prerelease may state these limitations; stable or universally supported claims are not justified.
The audit adds no permission to force-push, overwrite an existing repository or expose secrets.
