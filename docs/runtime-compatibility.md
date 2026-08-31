# Runtime compatibility and evidence

Documentation review date: 2026-08-31. Version-specific live tests: NOT RUN.
Generated artifacts and fake-home lifecycle tests are not native host discovery evidence.
Machine-readable scope/status: [runtime-evidence.json](runtime-evidence.json).
Path mappings live in core/adapters.json; minimum host versions remain unknown.

## OpenAI surfaces

Codex local packaging uses .agents/skills and an OpenAI metadata transform with
allow_implicit_invocation enabled. CLI, IDE and desktop each need live discovery tests;
Codex cloud is a distinct surface. A local copy does not install into cloud.

For ChatGPT, the documented standalone versus plugin distribution flow varies by surface;
use the importer actually offered by the account. The standalone and plugin variants are
separate artifacts. This candidate neither denies an account-specific standalone importer nor
claims it has been tested. Web and mobile require separate real-session verification.
[Official skills authoring guide](https://learn.chatgpt.com/docs/build-skills).

## Claude and Claude Code

Claude Code workspace/user: .claude/skills; plugin: .claude-plugin/plugin.json with sibling
skills directory. Description-based selection respects user disablement and explicit invocation
controls. [Official Claude Code skills](https://code.claude.com/docs/en/skills).

Claude web/desktop custom skill upload is separate from Code plugins; use the claude-upload
ZIP with one outer skill directory. Account/organization enablement remains required.
Claude mobile has no tested import/activation evidence here.
[Official Claude custom skills](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

## Gemini and Antigravity

Gemini CLI uses workspace .agents/skills and user .gemini/skills in this adapter.
Trust and activation consent are retained. Gemini web/mobile/Gems is not supported by this
filesystem adapter. [Official Gemini CLI skills](https://geminicli.com/docs/cli/using-agent-skills/).

Antigravity IDE uses workspace .agents/skills and user .gemini/config/skills.
This does not certify the Antigravity SDK or Gemini product family.
[Official Antigravity IDE skills](https://antigravity.google/docs/skills?app=antigravity-ide).

## Additional filesystem targets

- Cursor: workspace/user .cursor/skills. [Official Cursor skills](https://cursor.com/docs/skills).
- Copilot: workspace .github/skills; user .copilot/skills is an adapter assumption requiring
  per-client confirmation. CLI/IDE/cloud capabilities must not be conflated.
  [Official Copilot skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills).
- OpenCode: workspace .opencode/skills; user .config/opencode/skills.
  [Official OpenCode skills](https://opencode.ai/docs/skills).
- Generic: .agents/skills only for explicitly compatible hosts. No universal compatibility
  or automatic instructions bridge is claimed.

All generated targets remain live-UNVERIFIED until a host lists the skill and emits observable
activation evidence in a new, unprompted-by-name task. Prompt traces must exclude private
chain-of-thought and credentials.
