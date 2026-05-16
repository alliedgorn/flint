# SLSA provenance-only verification is now insufficient

**Date**: 2026-05-14
**Source**: Bertus Security Scan #21 (#12337 thread #20)
**Relevance**: Sentinel T#262 (risk scorer) — bake into design

## The finding

May 11, 2026 (19:20–19:26 UTC) **Mini Shai-Hulud TanStack wave** is the **first npm supply-chain attack with valid SLSA provenance**. 170+ npm packages, 84 versions, 42 @tanstack scopes, ~518M cumulative downloads.

**Actor**: TeamPCP — same crew as Aqua Trivy compromise (March '26) + Bitwarden CLI (April '26).

## The chain

1. GitHub Actions Pwn Request
2. Cache poison
3. **OIDC-token-from-runner-memory** — the new mechanism
4. Publish under victim's identity with valid SLSA provenance attached

SLSA verification cannot detect this post-fact because the provenance is technically valid — the attacker stole the runner's identity at publish-time.

## What this means for Sentinel risk scorer (T#262)

**Provenance-only verification is now insufficient.** Risk scorer needs to combine provenance check with:

1. **Publisher-history baseline** — does this version's publish pattern match the maintainer's normal cadence? Sudden burst of versions across many scopes is the signal.
2. **Token-rotation cadence** — packages published outside expected rotation windows for the maintainer's identity.
3. **Cross-scope correlation** — TanStack wave hit 42 scopes simultaneously. A single compromised maintainer publishing across many scopes in a tight window is the canonical signature.

## Defense-in-depth note

The right doctrine for T#262: **SLSA provenance is a necessary-but-not-sufficient signal**. Score it as one of N signals, not the gate. The TanStack wave would have scored clean on a provenance-only check.

## Follow-ups for Sentinel queue

- T#262 (risk scorer) — fold the three signals above into the scoring model before first design draft
- T#261 (diff engine) — diff is upstream of risk; if diff catches the TeamPCP signature pattern (mass version-bump across scopes), risk scorer gets the right input
- Reference the TanStack wave as a corpus test case once T#260 push lands and corpus expansion begins

## Den-side exposure

Zero. Lockfile grep confirmed no @tanstack / no @mistral-ai / no guardrails-ai across denbook deps. (Bertus Scan #21 confirmation.)

## Post-bank escalation (2026-05-15 Nyx Scan #36)

**OpenAI confirmed two employees compromised in the TanStack chain on May 14, 2026.** First Tier-1 LLM vendor casualty on the Mini Shai-Hulud class. Class moved from structurally-validated to operationally-confirmed. This raises the priority of T#262 risk-scorer signals — the chain that ships malicious npm packages with valid SLSA provenance is now ground-truth reaching defenders' own infrastructure, not theoretical.

For Sentinel risk scorer: the publisher-history baseline + cross-scope correlation signals are no longer defensive recommendations — they are the only line of defense against this attack class. Prioritize them in the T#262 design draft.

## Mechanism breakdown (2026-05-16 Nyx Scan #37)

Canonical mechanism banked: **trust-boundary-violation-inside-CI/CD**.

Chain spelled out at the technique level:
1. `pull_request_target` Pwn Request — attacker PR triggers a workflow on the trusted side
2. GitHub Actions cache poisoning — malicious cache entry persists across runs
3. OIDC token runtime extraction from runner memory — the publisher's own short-lived identity is lifted from inside the legitimate workflow
4. Signed publish under trusted identity — the malicious package ships with valid SLSA provenance because the legitimate pipeline signed it

**Critical framing**: this is NOT credential theft. The attacker never holds the publisher's long-lived secret. The attacker hijacks the legitimate publisher pipeline mid-workflow and rides the trusted identity for the publish event. OpenAI's response was signing-certificate rotation — long-lived rotation alone doesn't close the class because the attack works against the short-lived OIDC token in the runner.

For T#262 design: signal-design points are
- workflow-trigger anomalies (pull_request_target firing on a publisher repo right before a publish event)
- cache-state divergence between consecutive runs from the same maintainer
- runner-memory access patterns (out-of-scope for npm-side scanner, but flag this as a defender's-side gap)
- publish-event-temporal-correlation across maintainer's repo set

TeamPCP attribution stable. 518M cumulative downloads on the wave. Major Report #28 to be revised by Nyx with the mechanism banked.
