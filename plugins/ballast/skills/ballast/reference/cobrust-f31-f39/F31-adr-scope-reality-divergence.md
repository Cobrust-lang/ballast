---
catalogue_id: F31
title: "ADR scope-reality divergence — batch frame over-scopes due to missing pre-dispatch source verification"
family: F1-Sediment (verification-gap sub-form)
severity: P1
status: ratified_2026-05-16
empirical_project: Cobrust v0.3.0 Phase F.3 sprint
cobrust_local_id: F27-candidate (adr-scope-reality-divergence.md)
date_ratified: 2026-05-16
second_corroborator: confirmed (P9-A + P9-B independent rediscovery before audit)
---

# F31 — ADR scope-reality divergence

## Symptoms

A Phase batch ADR (or any strategic-altitude planning document) cites "work
needed across crates X / Y / Z" without source-code verification. Sub-agents
dispatched against the ADR re-discover at spike time that the work is already
partly or fully shipped. They either:

- Pivot scope on the branch (organic recovery — correct, but wastes spike-time)
- Implement redundantly (regression — incorrect, and wasted dispatch cost)

Two or more sub-agents independently re-discover the same divergence,
confirming that the gap is structural (not an individual agent oversight).

## Root cause

Strategic-altitude authorship is required to write a coherent batch frame. But
the same altitude is inherently lossy on local source state. The author models
the codebase's state from memory/prior ADRs rather than live `grep` evidence,
and memory lags behind recent sprint merges.

This is F1-family: the rule "verify before scoping" exists as common sense but
has no enforcement gate at ADR-authorship time. Without an explicit
"pre-dispatch verification commit", the gap propagates to every sub-agent
dispatched against the stale scope.

## SOP fix — ADR pre-dispatch source-code verification gate

Add this gate to every batch-frame ADR authorship:

**Phase 1 — source verification (mandatory, in the same commit as the ADR)**:
1. Run at least 3 representative `grep -nE` calls against the cited crates
   (symbol search, not file-existence check).
2. For each claimed "work needed", record the grep result in ADR §"Verification"
   section: either "not found — gap confirmed" or "found at `file::symbol` —
   gap already shipped".
3. Only scope the sub-ADR (sub-sprint) for unconfirmed gaps.

**Phase 2 — sub-dispatch (once Phase 1 committed)**:
Dispatch sub-agents with a reference to the verification commit. The sub-agent's
§"Done means" criteria must start with "confirm gap still exists at HEAD SHA".

The two-phase pattern ensures the verification is co-located with the ADR,
visible to every future reader, and forms a diff-based audit trail.

## Evidence

Cobrust ADR-0050 Phase F.3 batch, 2026-05-16 (SHA `891d235`):

- ADR scoped 5 P0 features as "work needed".
- Pre-impl audit (read-only opus `afe53e8f`) + two independent P9 spike commits
  (`1998dbe`, `909811f`) found that 3/5 features were already substantially shipped
  at HEAD `30cf2b2`:
  - `break`/`continue` — fully shipped end-to-end (lexer → AST → MIR → Cranelift).
  - `for`-loop protocol — operational over `list[i64]` + `list[str]` since ADR-0044.
  - `f64` — 80% shipped; remaining gap was a D2-sonnet scope, not D4-opus-1-week.
- Only `Str`-ownership debt (ADR-0050c) and `dict` (Wave 3) survived as honestly
  large work.
- Batch estimate revised from 4-5 weeks to 2-3 weeks after correction.
- Two redundant re-discoveries (P9-A + P9-B) before the dedicated pre-impl audit
  confirmed the pattern is structural, not accidental.

## Counter-pattern

Instead of:
```
Write batch ADR → dispatch sub-agents → sub-agents re-discover scope
```

Use:
```
Write batch ADR frame → run 3+ verification greps → amend ADR with results
→ dispatch sub-agents against verified gaps only
```

The pre-dispatch source verification gate converts a passive documentation
convention into an active confirmation step.

## Cross-references

- F34 (numeric-anchor degradation) — sibling; F31 is a scope-gap at ADR
  authorship time; F34 is a symbol-anchor gap at doc maintenance time.
- F32 (wave-2 cascade discovery deficit) — downstream: when F31 produces
  over-scoped sub-ADRs, F32-style cascade bugs surface during the impl sprint
  because the over-scoped design didn't enumerate all consumers.
- Cobrust finding: `docs/agent/findings/adr-scope-reality-divergence.md`
- Cobrust ADR: `docs/agent/adr/0050-phase-f3-language-completeness-batch.md`
  §"Amendment 2026-05-16"

## Status

Ratified 2026-05-16. Two-phase gate adopted in Cobrust CTO runbook for all
batch-frame ADR authorship. Second-corroborator requirement satisfied by
independent P9-A + P9-B rediscoveries.
