# AI Core Operating Protocol v2 Design

## Goal
Build a vendor-neutral automatic capability-routing operating layer for Agent Skills compatible runtimes. The user states the outcome; the runtime resolves the minimum relevant skills/tools, loads full instructions only after metadata selection, evaluates task-specific failure modes, and verifies before completion.

## Architecture
- Canonical skill: `skills/ai-core-operating-protocol/` is the single source of truth.
- Deterministic reference router: `core/router/` exists for tests, explainability, benchmark scoring, and runtimes without native routing; it does not replace native model skill activation.
- Generated adapters: OpenAI, Claude, Gemini, Antigravity, and generic packages are produced from canonical sources.
- Safe installer: additive copy with backups/manifests; no blind overwrite of instruction files.
- Tests: routing, compatibility, token budget, security, packaging, and generated-adapter drift.

## Runtime policy
Prefer native metadata-first skill discovery where available. Keep always-loaded bootstrap instructions tiny. Never require manual skill invocation when native automatic discovery can resolve intent. Permissions and confirmations remain runtime-controlled.
