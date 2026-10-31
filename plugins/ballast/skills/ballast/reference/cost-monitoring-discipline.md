---
name: Cost monitoring + budget gate discipline
description: Practical patterns for tracking LLM cost across Ballast sprints, setting budget gates per sprint and per release, and recognizing when cost is signaling a deeper problem (loop / drift / over-spawn).
type: reference
version: 1.0.0
date: 2026-05-12
status: active
relates_to: [skill:SKILL.md §"Wave + Tx pattern", reference:failure-modes-catalogue.md F12]
---

# Cost monitoring discipline

> "Token cost is not a constraint" (per Cobrust constitution) does NOT mean "ignore cost." It means cost is not the primary correctness gate. Cost is still a **signal**: a sprint costing 10× the expected budget is telling you something — either the work is harder than estimated, or an agent is looping, or someone spawned 10× more sub-agents than needed.

## When this applies

- Any multi-sprint project running parallel agents
- Any sprint exceeding ~$5 in LLM cost
- Any sprint where consensus mode or stress sweeps fire (10×+ multipliers)
- Any release where you want to defend "we shipped at $X cost"

If you're a one-shot agent with one tool call, this reference is overkill.

## Three budget tiers

```
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER-A: Per-sprint budget                                                 │
│  Set BEFORE dispatch. Stop and escalate if exceeded.                      │
│  Typical: $1-$5 for sonnet sprint, $5-$15 for opus sprint                 │
├─────────────────────────────────────────────────────────────────────────┤
│ TIER-B: Per-release budget                                                │
│  Sum across all sprints leading to a tag.                                 │
│  Typical: $10-$50 per v0.X release; $50-$200 per v1.X major               │
├─────────────────────────────────────────────────────────────────────────┤
│ TIER-C: Per-project lifetime budget                                       │
│  Track for sanity / ROI conversation with funding source.                 │
│  Typical: $100-$1000 for a research-grade project; $1K-$10K for products  │
└─────────────────────────────────────────────────────────────────────────┘
```

Each tier escalates differently:

- TIER-A breach → STOP, report, ask user before continuing
- TIER-B breach → publish a finding documenting why; reassess release scope
- TIER-C breach → strategic review (ROI / pivot question)

## Cost ledger (Ballast pattern)

Every project running parallel agents must maintain a per-dispatch ledger. Ballast's recommended schema (codified in `cobrust-llm-router` if using a custom router, or in `.ballast/ledger.jsonl` as append-only log):

```
{
  "timestamp_utc": "2026-05-12T03:45:00Z",
  "sprint_id": "lc100-stress-sweep",
  "agent_role": "P7-sonnet-test-B1",
  "session_id": "abc12345",
  "provider": "anthropic",
  "model": "claude-sonnet-4-6",
  "prompt_tokens": 12345,
  "completion_tokens": 6789,
  "total_tokens": 19134,
  "cost_micro_usd": 142500,
  "cache_hit": false,
  "task_tag": "test_corpus_generation",
  "outcome": "ok"
}
```

Append on every API call. Materialize SQLite index for fast queries.

### Useful ledger queries

```sql
-- Cost per sprint
SELECT sprint_id, sum(cost_micro_usd)/1e6 as usd
FROM ledger
GROUP BY sprint_id
ORDER BY usd DESC;

-- Cost per model
SELECT model, count(*) as calls, sum(total_tokens) as tokens, sum(cost_micro_usd)/1e6 as usd
FROM ledger
WHERE timestamp_utc > date('now', '-7 days')
GROUP BY model;

-- Cache hit rate (savings)
SELECT cache_hit, count(*) as calls, sum(total_tokens) as tokens
FROM ledger
WHERE timestamp_utc > date('now', '-7 days')
GROUP BY cache_hit;
```

## Pre-sprint budget estimation

Before dispatching a sprint, write the budget estimate in the dispatch prompt itself:

```
BUDGET ESTIMATE (must include in P9 dispatch):
- Phase 1 (P9 opus ADR drafting): ~30K prompt + 5K completion = ~$2
- Phase 2 (4 × P7 sonnet pairs, ~25 problems each):
  - Per pair: 5 reads × 10K + 10 writes × 5K = ~$1
  - 4 pairs × 2 agents = ~$8
- Phase 3 (P9 opus triage): ~10K + 5K = ~$1
- Phase 4 (decision report): ~5K = ~$0.5

TOTAL ESTIMATE: $11.50 ± 30% = $8-$15 range
TIER-A BUDGET: $20 (~30% headroom)

Escalate at $15 actual if Phase 2 still in progress.
```

Estimation accuracy improves with practice. Track estimate vs actual across 10+ sprints to calibrate.

## In-flight monitoring

For long-running sprints (> 4 hr wall-clock or > $5 budget), check the ledger every ~1 hr:

```bash
# Quick health check
sqlite3 .ballast/ledger.db "
  SELECT
    sprint_id,
    count(*) as calls,
    sum(total_tokens) as tokens,
    sum(cost_micro_usd)/1e6 as usd
  FROM ledger
  WHERE sprint_id = '<current-sprint>'
"
```

If actual ≥ 70% of TIER-A budget and the sprint is < 50% complete → escalate early. Don't wait for the breach.

## Cost as a signal

Cost is not just expense — it's a diagnostic indicator:

### High cost without progress = loop

If a sprint is at $10 with 0 new commits, the agent is likely in a loop. Symptoms:

- Same files re-read 5+ times in ledger
- Same tool sequence repeating
- No new test cases / no new ADR sections

Recovery: kill the sprint, audit the prompt for ambiguity, re-dispatch with sharper scope.

### High cache miss rate = context shuffling

If cache hit rate < 30% on Anthropic/OpenAI, the prompt structure is changing per-call. Likely cause: system prompt or memory file being mutated mid-sprint.

Recovery: lock memory updates to inter-sprint boundaries. Don't edit memory while a sprint is running.

### Cost spike at specific phase = under-estimated scope

If Phase 2 of a 4-phase sprint costs 3× the budget for that phase, the work was scoped wrong. The next dispatch should split Phase 2 into 2a + 2b.

This is a productive finding — write it up as a finding entry under `docs/agent/findings/sprint-<id>-cost-overrun.md`.

## Anthropic-pattern adoption

### Prompt caching reduces cost dramatically

Anthropic caches stable prefixes (system prompt, project preamble) at ~10% of full cost.

For Ballast: structure agent prompts so:

1. System role + project preamble (cached) — top
2. Required-reads + RFC fragments (cached) — middle
3. User-turn / sprint-specific context — bottom

Don't shuffle the order — that breaks the cache. Ballast memory files + dispatch-prompt templates already shape this.

### Model selection by D-rating

Anthropic explicitly recommends "use the cheapest model that passes your eval." Ballast's D0-D5 matrix is the practical implementation:

- D0/D1 sonnet: ~5-10× cheaper than opus, generally sufficient
- D2 sonnet (with eval pair): fine if test corpus catches edge cases
- D3+ opus: pay the premium when the task requires it

Don't default to opus for every task — that's overspending. Don't default to sonnet for D3+ tasks — that's underspending leading to F20.

## OpenAI-pattern adoption

### Structured outputs reduce iteration

OpenAI's structured-outputs (JSON schema) feature reduces "re-prompt for fix" cycles. Each correct-format reply saves 1× the call cost.

Ballast shape: P7/P9 completion reports include YAML block (per prompt-engineering-patterns PT4). Saves ~20-30% across a typical multi-call sprint vs free-text reports.

### Streaming saves wall-clock but not token cost

OpenAI streaming saves user-perceived latency but not token cost. Ballast should use streaming for UX where it helps (release-readiness audit feedback to user) but understand it doesn't reduce $.

## Ballast integration with existing patterns

### Dispatch prompt budget block

Add to `templates/dispatch-prompt-p9.md` § just below DIFFICULTY-RATING:

```
BUDGET ESTIMATE (must include):
- Phase-by-phase cost estimate
- TIER-A budget with ~30% headroom
- Early escalation threshold

If actual cost exceeds estimate by 50% mid-sprint, STOP and report.
```

### Release-readiness ledger snapshot

Include in `[P7-RELEASE-READY-VERDICT]`:

```
Cost snapshot at release tag:
- This sprint: $X.YY
- Prior sprints to this tag: $Z.WW
- Total release-bearing cost: $A.BB
```

Defensible "we shipped at $X" claim.

### Cost as F-pattern detector

The F-pattern catalogue should include cost-anomaly as a diagnostic. Add to dispatch:

> If actual cost > 2× estimate, flag as potential F-pattern occurrence (likely F13 plan-vs-execute, F17 self-report, or unidentified). Findings entry mandatory.

## Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| No estimate, no monitoring | Bill shock at month end | Pre-sprint estimate + ledger |
| Ignore cost as "not a constraint" | Drift to over-spawning sub-agents | Cost as signal, not constraint |
| Cache miss not measured | Cost stays high after prompt-engineering optimization | Track cache hit rate per sprint |
| Over-using opus | Sonnet would suffice; 5-10× overspend | D-matrix rigor (PT7 in prompt patterns) |
| Cost ledger stale | Decisions made on outdated data | Append on every API call, not batched |

## Cross-references

- `templates/dispatch-prompt-p9.md` — budget estimate block (add per this reference)
- `reference/prompt-engineering-patterns.md` PT7 — D-rating drives cost
- `reference/evals-first-development.md` — eval delta lets you compare cost across optimizations
- `reference/failure-modes-catalogue.md` — F12 (model output starvation), cost signal for diagnosis
- Anthropic prompt caching docs: https://platform.claude.com/docs/en/prompt-caching
- OpenAI structured outputs: https://platform.openai.com/docs/guides/structured-outputs
