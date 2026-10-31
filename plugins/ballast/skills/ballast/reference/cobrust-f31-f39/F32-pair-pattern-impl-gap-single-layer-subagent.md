---
catalogue_id: F32
title: "PAIR pattern impl gap under single-layer sub-agent architecture"
family: methodology-gap (PAIR-topology sub-form)
severity: P0 (methodology integrity)
status: ratified_2026-05-16
empirical_project: Cobrust v0.3.0 Phase F.3 sprint
cobrust_local_id: F28-candidate (adsd-pair-pattern-impl-gap.md)
date_ratified: 2026-05-16
second_corroborator: structural (platform inspection confirms no Agent tool in sub-agents)
---

# F32 — PAIR pattern impl gap under single-layer sub-agent architecture

## Symptoms

Ballast §"Dev/test pair pattern" prescribes "P9 spawns P7-TEST first, then P9
reviews the corpus, then P9 spawns P7-DEV". A project adopts this ceremony but
sub-agents (P9-level) do not have the `Agent` tool — the platform only exposes
it to the top-level orchestrator (P10/main session).

Result: the PAIR ceremony is **structurally unimplementable as written** on
single-layer platforms. Sub-agents either:

- Silently ignore the instruction and perform TEST + DEV as a single-Opus pass
  (ceremonial PAIR, same-agent bias retained)
- Write sequential "phases" within their own context (still single agent,
  bias not eliminated)
- Send a message back to the orchestrator requesting a new dispatch
  (workable, but high coordination overhead)

The same-agent bias Ballast designed PAIR to prevent is present even when the
PAIR ceremony is nominally followed.

## Root cause

Ballast's PAIR pattern was written assuming a multi-layer agent architecture where
P9 can recursively dispatch P7-tier agents. Under Claude Code (and any other
single-layer orchestration platform), sub-agents have a constrained tool set
that excludes the Agent/dispatch tool. The PAIR ceremony cannot be implemented
by the sub-agent itself.

Same-agent bias: when one agent writes both the failing tests and the
implementation, the tests tend to mirror the author's mental model rather than
independently probe the spec. Constitution §6 "test-first" is honored in form
but not in spirit.

## SOP fix — P10-direct PAIR dispatch

On single-layer platforms, the orchestrator (P10/main session) MUST directly
dispatch both TEST and DEV agents as parallel calls:

1. **P10 dispatches TEST agent**: "Write failing test corpus only; forbidden
   to write impl; report `[TEST-CORPUS-READY]` with file paths + assertion
   counts + `cargo test` fail count."
2. **P10 reviews TEST corpus** (~5-10 min): coverage / spec-faithfulness /
   edge cases. Sends amendment message if needed.
3. **P10 dispatches DEV agent** with TEST's commit SHA + corpus paths as
   **required input**. DEV implements until `cargo test` 0-fails.
4. **P10 verifies** all gates green + merges.

**When NOT to use P10-direct PAIR** (P9 single-Opus is fine):
- ADR-authoring sprints (doc-only, no impl)
- Strategic decomposition where there's no impl yet
- Doc-only edits, runbook updates, frontmatter stamps
- Pre-impl audits (read-only is correct)

**Coordination overhead trade-off**: P10-direct PAIR costs ~2× dispatch
ceremony per sprint. For load-bearing sprints (contract-bearing public API,
novel semantics, multi-crate refactor) the methodological guarantee is worth
the cost. For trivial sprints (D1 well-scoped doc fix), single-sonnet is fine.

## Evidence

Cobrust Phase F.3 Wave 1, 2026-05-16:

- `cto_operations_runbook.md` §"Dev/test pair pattern" prescribed
  "P9-spawns-P7-TEST-then-P7-DEV".
- 3 P9 Opus sprint dispatches with full PAIR ceremony in the prompt.
- Tool surface inspection confirmed: P9 sub-agents have no `Agent` tool.
- 2/3 sprints (P9-A break/continue `1998dbe`, P9-B for-loop `909811f`)
  executed as single-Opus contract-seal + corpus. The PAIR ceremony was
  ceremonial — no double-blind separation achieved.
- 1/3 sprint (P9-C dict design `8466433`) was ADR-only and didn't need PAIR.
- User surfaced this gap 2026-05-16 during Wave 1 dispatch review.
- Runbook updated 2026-05-16 to mark P9-PAIR as structurally invalid and
  replace with P10-direct PAIR for D1-D3 / D5 sprints.

## Platform dependency note

This failure mode is specific to platforms that do not expose the Agent/dispatch
tool to sub-agents. On platforms that support recursive agent dispatch (e.g.
AutoGen, CrewAI, future Claude Code multi-layer), P9 can dispatch P7 as
originally written. Ballast methodology should declare PAIR's
implementation-layer responsibility explicitly per platform tier:

- Multi-layer platform: P9 dispatches P7-TEST + P7-DEV as written.
- Single-layer platform: Orchestrator (P10) directly dispatches TEST + DEV;
  P9 layer reserved for ADR-authoring + strategic decomposition.

## Cross-references

- F33 (agent self-disciplinary rule skip) — F32 is the structural reason PAIR
  discipline breaks: the rule is there, but the agent physically cannot execute it.
- F36 (TEST corpus exit-0 claim drift) — downstream: even when P10-direct PAIR
  runs, F36 shows the TEST corpus clean-claim itself needs independent re-verification.
- Cobrust finding: `docs/agent/findings/adsd-pair-pattern-impl-gap.md`
- Cobrust memory: `feedback_adsd_pair_pattern_impl_gap.md`
- ADR reference: `docs/agent/adr/0050-phase-f3-language-completeness-batch.md`
  §"Amendment 2026-05-16" §A7

## Status

Ratified 2026-05-16. P10-direct PAIR pattern adopted in Cobrust CTO runbook
for all D1-D3 / D5 sprints. Cobrust Phase F.3 Wave 2 + Wave 3 used P10-direct
PAIR as the new standard pattern.
