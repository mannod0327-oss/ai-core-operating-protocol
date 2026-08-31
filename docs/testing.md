# Testing

Install requirements-dev.txt in a clean Python environment and run python -m pytest -q.
Tests create their own generated trees and releases; no prior build is needed.

- Original golden: 120 unique requests, legacy include/forbidden constraints.
- RC2 holdout: 22 hand-labeled requests with complete allowed sets, including no-match,
  mixed sources/domains and lexical false-positive cases. It was used during development;
  it is a regression holdout, not a statistically independent blind evaluation.
- Lifecycle: isolated fake homes/workspaces; independent corruption, interrupted copy,
  record commit failure, user-edit preservation, rollback, lock and subprocess tests.
- Parser: real YAML, duplicate keys, missing references, metadata types and empty bodies.
- Build: source unchanged, generated copies equivalent, deterministic SHA, safe archive names,
  CRCs, conservative size limits and overwrite refusal.
- Security: sentinels plus targeted path/reparse tests and a limited secret-pattern scan.

The legacy “one per layer” test was replaced because PDF-to-Word requires two domains;
identity dedup remains mandatory. The 120 legacy expected labels were not loosened.
Keyword bug/rasm matching was narrowed after “bugungi”/“rasmiy” false positives.

Benchmark failures return exit 1; malformed/empty data returns exit 2.
Complete-label precision/recall and selection counts belong only to the reference router,
not model activation. The old forbidden-only dataset cannot measure full precision.

CI declares Ubuntu, Windows and macOS with Python 3.12/3.13, installs pinned dependencies,
runs all tests, both benchmarks and source snapshot drift check. No credentials, deployment
or automatic release job. Remote matrix execution is NOT RUN until explicitly published.

## Live evaluation procedure (not yet executed)

For each exact host/surface/version/OS/scope: record discovery + enabled state.
In fresh chats without naming this skill, run five positive tasks three times each; target
14/15 observed activations. Five trivial negative prompts target zero unnecessary invocations.
Validate three synthetic read-only/artifact outcomes. Observe real host activity events,
not only the assistant saying “I used it”. Record consent separately from selection.

Use no private mailbox and no paid API without explicit authorization. Web and real mobile
sessions are separate evidence. Fill runtime-evidence.json with actual observations only.
Bootstrap word count is a structural budget, not a measured token or latency saving.
