# Token Efficiency

v2 relies on progressive disclosure rather than loading every workflow into an always-on prompt.

Release checks:
- bootstrap section <= 200 words;
- canonical SKILL.md < 500 lines;
- supporting references lazy-loaded;
- 100+ catalog routing benchmark does not load skill bodies into the reference registry;
- adapters copy the same canonical skill instead of embedding duplicated behavioral prompts.

These checks reduce avoidable prompt overhead; they do not claim a fixed percentage reduction in all hosts because host-side metadata injection budgets differ.
