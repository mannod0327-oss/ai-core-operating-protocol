# AI Core Operating Protocol

Release candidate **2.0.0-rc2** — one skill, host-specific packages, explicit evidence limits.

One vendor-neutral operating skill helps an agent choose relevant available skills/tools,
load only needed instructions, and verify results. It is **one skill**, not a bundle of
thousands. The 15 capability entries in the reference catalog are test metadata, not
installed skills, connectors or credentials.

Implicit selection is enabled where the host supports it; the host still decides whether
to invoke a skill. Installation, authorization and actual activation are different states.
There is no always-on daemon and no guarantee of automatic activation in every chat.

## Start here

- [Download release packages](https://github.com/mannod0327-oss/ai-core-operating-protocol/releases)
- [Cross-platform CI](https://github.com/mannod0327-oss/ai-core-operating-protocol/actions/workflows/ci.yml)
- [Uzbek guide](docs/README.uz.md)
- [Installation, migration and recovery](docs/install.md)
- [Platform-specific scope and official sources](docs/runtime-compatibility.md)
- [Validation and remaining release gates](docs/RC2-READINESS.md)
- [Independent pre-publication audit](docs/INDEPENDENT-AUDIT.md)
- [Release notes](docs/releases/v2.0.0-rc2.md)
- [Original technical specification](docs/planning/TZ-CROSS-AGENT.md)

## Local validation

Python 3.12 or 3.13 is the declared target. Use a fresh virtual environment.
Only the development/validation toolchain needs the pinned dependencies; the installer
and reference router use the Python standard library.

```sh
python -m venv .venv
# Activate .venv using your operating system's normal activation command.
python -m pip install -r requirements-dev.txt
python scripts/validate_skill.py
python -m pytest -q
python scripts/benchmark.py
python scripts/benchmark.py --dataset tests/routing/holdout.json
python scripts/package_release.py --output release/rc2-local
```

Builds use new output directories and refuse to overwrite existing release artifacts.
Tests build their own fixtures; no pre-existing dist or release directory is required.
Release output contains 14 ZIPs plus SHA256SUMS.txt, each ZIP below 25,000,000 bytes.
Version and runtime mappings come from project.json and core/adapters.json.

## Local installer

Dry-run is the default. Replace the example workspace with the intended project:

```sh
python installers/install.py claude --workspace ./example-project --action plan
python installers/install.py claude --workspace ./example-project --action install
python installers/install.py claude --workspace ./example-project --action verify
```

Use the same runtime, scope, workspace/home and state directory for later operations.
Destination and state must be on the same filesystem; for a workspace on a different
volume from your home, pass an explicit same-volume --state-dir. Plan detects this before writes.
Supported filesystem runtime identifiers: codex, claude, gemini, antigravity, cursor,
copilot, opencode, generic. A runtime identifier is a packaging target, **not a claim
of tested host support**. Generic requires a host that discovers .agents/skills.

## ChatGPT and Claude uploads

Use the standalone skill ZIP if your account provides a compatible skill importer.
If the selected surface only accepts plugins, use its separately generated plugin
artifact; a plugin is not mislabeled as a standalone skill. Claude's custom skill upload
has its own ZIP. The source ZIP is for developers, not the skill importer.

Uploading a ZIP as a conversation attachment is not necessarily skill installation.
Web/mobile import, enablement, discovery and new-chat activation require account-level
validation. Local installation does not synchronize to a cloud/mobile account.

## Architecture and evidence

Canonical SKILL.md → native metadata selection → selected instructions → scoped action →
outcome checks. The Python keyword router is an **offline reference implementation**,
not connected to native model routing. Its benchmark scores must not be advertised as
ChatGPT/Claude activation accuracy.

Cross-platform CI runs on pushes and pull requests across Windows, Linux and macOS with
Python 3.12 and 3.13. See the linked Actions page for actual results; configuration alone
does not prove a passing run. No live model calls or real agent-home installations were
made for this candidate. The readiness and audit documents record pre-publication evidence.
See the repository's Actions and Releases pages for actual remote CI and publication status.
No automatic deployment or release publishing is configured in CI.
