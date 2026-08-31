# Routing

Routing dimensions: outcome, domain, source of truth, action, freshness, risk, verification.

Selection policy: metadata first → shortlist → minimum sufficient capabilities → load body/schema only when selected.

Reference router output includes selected identities, unmet needs, clarification and advisory risk. It may select multiple complementary domains and sources (PDF plus DOCX, Gmail plus calendar); identities are deduplicated. Process/verifier ties are resolved deterministically. Disabled/unavailable/unpermitted entries are excluded. Explicit-only entries require an explicit identity, not a keyword match. This code is a lexical regression harness, not connected to a host's native LLM selection engine or authorization system.
