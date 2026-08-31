# Architecture

## Core idea
The user's outcome is the command. Runtime-native discovery should resolve capabilities automatically from metadata, then load full instructions only for selected skills.

## Layers
1. **Canonical skill** — behavioral operating protocol, vendor-neutral.
2. **Native runtime router** — preferred whenever the host already discovers skills from metadata.
3. **Reference router** — offline deterministic test harness only; not a native runtime fallback or an LLM replacement.
4. **Runtime adapters** — package the canonical skill into each host's expected layout.
5. **Evaluation/verification** — task-specific quality gates and evidence before completion claims.

## Why not a mega prompt?
Always-loaded instructions consume context and compete with the user's task. Agent Skills on supported runtimes already provide progressive disclosure, so v2 keeps the bootstrap small and pushes specialized detail into references.
