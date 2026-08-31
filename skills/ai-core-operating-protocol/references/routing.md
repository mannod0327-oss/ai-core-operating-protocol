# Capability Routing

1. Classify only what changes routing: outcome, domain, source of truth, action, freshness, risk, verification.
2. Inspect metadata first: skill names/descriptions, plugin manifests, filtered tool/function discovery.
3. Select the minimum sufficient set. Typical order when relevant: process → domain → source/tool → verifier.
4. Resolve overlap in favor of the narrower trigger and the real source of truth. Do not load near-duplicates unless requirements are complementary.
5. Let the host select installed, available, enabled and permitted capabilities when intent is sufficient. Never bypass explicit-only flags, consent, workspace trust or user disablement. Manual invocation remains an option, not a universal requirement.
6. Reuse already-loaded bodies/schemas in the same session unless they may have changed or a missing detail requires re-reading.
7. Never fabricate a capability. If absent, use a real fallback or state the limitation.
8. Guard against router recursion: a routing skill must not repeatedly activate itself or another router.

**Token rule:** never load every skill body or full large tool catalog “just in case.”

One layer can require multiple complementary capabilities (PDF plus DOCX; email plus calendar). Deduplicate identities, not layers. If a private connector is missing, report that requirement rather than replacing private content with public web guesses. The Python reference router distributed with the source is an offline regression tool, not the host's activation engine.
