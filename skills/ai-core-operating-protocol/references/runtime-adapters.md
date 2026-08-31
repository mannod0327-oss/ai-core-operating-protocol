# Runtime Adapters

The canonical skill is vendor-neutral. Adapters package the same skill for each runtime without duplicating behavioral logic.

- OpenAI: standalone Agent Skill plus ChatGPT/Codex plugin package when supported. Local Codex skill installation should use the current documented user skill location; ChatGPT UI installation remains a product flow.
- Claude Code: `.claude/skills/<name>/SKILL.md` for project/user skill discovery; plugin packages keep `.claude-plugin/plugin.json` at plugin root and `skills/` alongside it.
- Gemini CLI: `.gemini/skills/` or interoperable `.agents/skills/`; prefer `.agents/skills/` for shared workspace portability.
- Antigravity: workspace `.agents/skills/`; global path follows current Antigravity documentation and may differ from Gemini CLI.
- Cursor: `.cursor/skills/`; OpenCode: `.opencode/skills/` workspace, `.config/opencode/skills/` user; Copilot uses its documented per-surface discovery paths. Check the source package adapter registry before installation.
- Generic: `.agents/skills/` only for hosts documented to discover that location. No automatic AGENTS.md bootstrap is implemented.

Always verify current runtime documentation before changing adapter paths.

Claude web upload is separate from a Claude Code plugin. ChatGPT web/mobile and Codex cloud require their own account-enabled import/distribution flow, not a local filesystem copy. Gemini web/Gems and Antigravity SDK are not implied by CLI/IDE packaging. Package validation does not prove discovery, implicit activation or successful outcomes on any surface.
