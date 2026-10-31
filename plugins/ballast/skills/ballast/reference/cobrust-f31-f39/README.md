---
doc_kind: batch-index
batch_id: cobrust-f31-f39
title: "F31-F40 — Cobrust v0.3.0 empirical corroboration batch"
date: 2026-05-19
cobrust_version: v0.3.0
sprint_range: "Phase F.3 Wave 1 (2026-05-16) → Phase I Wave 3 (2026-05-19)"
total_findings: 10
---

# F31–F40 Cobrust empirical corroboration batch

Ten failure-mode findings empirically corroborated by the **Cobrust v0.3.0**
sprint cadence (Phase F.3 → Phase I, 2026-05-16 to 2026-05-19).

Each finding satisfies the catalogue's second-corroborator requirement: the
entry records the specific Cobrust SHA(s) where the pattern was observed plus
the independent audit or dispatch that confirmed it.

## Index

| File | Catalogue ID | One-line summary |
|---|---|---|
| F31-adr-scope-reality-divergence.md | F31 | ADR batch frame over-scopes without source-code verification gate |
| F32-pair-pattern-impl-gap-single-layer-subagent.md | F32 | PAIR ceremony unimplementable on single-layer agent platforms |
| F33-predicate-flip-cascade-discovery-deficit.md | F33 | F29 enumeration misses latent consumers of flipped predicates |
| F34-wrapper-type-bidirectional-unify-ambiguous-type-cascade.md | F34 | Bidirectional `Ref(T) ↔ T` unify produces 142-failure cascade |
| F35-wave2-cascade-discovery-deficit-third-instance.md | F35 | Third corroboration: ADR forward-looking claim ≠ current source state |
| F36-agent-self-disciplinary-rule-skip.md | F36 | Agent skips rules it just wrote when judged "low-risk" |
| F37-numeric-anchor-degradation-high-churn.md | F37 | `file:NNN` anchors drift >100 lines in 14 days on high-churn files |
| F38-test-corpus-exit-0-claim-drift.md | F38 | TEST corpus clean-claim invalid on post-merge crate-graph at DEV time |
| F39-dev-commit-message-scope-drift.md | F39 | DEV commit message preserves original-spec framing after scope reduction |
| F40-stream-watchdog-false-stall-signal.md | F40 | 600s watchdog signal is false-positive; agent completes work post-hoc |

## Cobrust SHA index

Key SHA anchors cited across findings (all on `Cobrust-lang/Cobrust` repo, branch `main`):

| SHA | Role |
|---|---|
| `891d235` | ADR-0050 batch frame at F31's over-scope moment |
| `30cf2b2` | HEAD at F31 pre-impl audit (3/5 features already shipped) |
| `1998dbe` | P9-A spike (independent F31 rediscovery — break/continue) |
| `909811f` | P9-B spike (independent F31 rediscovery — for-loop) |
| `aca5d87` | Wave 2 cascade fix merge (F33 latent consumers) |
| `23cadf6` | ADR-0052a pre-revision (bidirectional unify design, F34) |
| `bcf9c7d` | ADR-0052a revised (one-way coercion design replacing F34 trigger) |
| `6843a33` | DEV v3 merge (F34 — 0 regressions after design fix) |
| `1643776` | 0052d-prereq-dev HEAD (F35 parser blocker verified) |
| `0f42be2` | TEST corpus merge (F38 — TEST clean-claim baseline) |
| `2e7ccb2` | Wave-2 TEST final merge on main (F38 crate-graph state) |
| `84e1286` | DEV 0055b rebase + 41/41 PASS (F38 DEV-verified clean) |
| `0cfeb3f` | Tier-1 honesty addendum (F38 28 hidden errors documented) |
| `7100849` / `c89d540` | F39 scope-drifted commit (feat ≠ diff) |
| `49ec536` | Tier-1 amendments catching F39 |
| `56c81bb` | ADR-0055d merge (F39 filed as F35-sibling finding) |
| `8e28b7f` | F40 — first post-stall commit from agent `a2b6ebf` |
| `663cd56` | ADR-0056c final merge (F40 — all work completed post-hoc) |
