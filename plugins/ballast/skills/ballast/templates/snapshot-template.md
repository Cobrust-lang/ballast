<!-- Template for a project state snapshot.
     One file per project, lives in agent memory or docs/state/.
     Updated end-of-turn by the CTO or its delegate.
     Source of truth for future agents post-compaction. -->

---
name: <project> state snapshot (compaction-resilient)
description: Authoritative compressed state of <project> at <date>. Update at end-of-CTO-turn so context compaction never loses load-bearing facts.
type: project

schema_invariant: |
  Every ADR mentioned in any section must appear in §"ADR roster" table.
  Every finding mentioned in any section must appear in §"Findings ledger".
  Binary verification list appears EXACTLY ONCE under §"main branch state".
  HEAD field reconciles with `git log -1 --format=%H` at write-time.
  cumulative_tests must include verification SHA + arch.
---

## Project root + constitution

**Project root**: <absolute path>
**Constitution**: `<path to founding doc, e.g. CLAUDE.md>`
**Mandate**: <1-2 sentence statement of what the project commits to>

## main branch state

- **HEAD**: `<SHA>` — `<commit message tag>`
- **Cumulative commits**: ~N
- **Cumulative tests**: <X> passed / <Y> failed / <Z> ignored — CTO verified @ HEAD `<SHA>` on <arch>. <Other-arch> validation: <status>.
- **5-gate baseline**: fmt 0 / clippy 0 / build 0 / test 0 / doc-coverage 0  (verified at <SHA>)
- **Cold rebuild time**: ~Ns on <reference machine>

### Definition-of-done anchors (multi-tier if applicable)

- **Tier 1** @ `<SHA>` — what condition was first met
- **Tier 2** @ `<SHA>` — what stricter condition was met
- **Tier N (TBD)** — what remains

### Binary verification (post-most-recent-milestone)

- `<command>` → `<expected output>` ✓
- ...

## ADR roster

| ADR | Title | Phase | Last verified |
|---|---|---|---|
| 0001 | <title> | <phase> | <SHA or —> |
| 0002 | ... | ... | ... |

(Every ADR in `docs/agent/adr/` MUST have a row here. Schema invariant
enforces this.)

## Findings ledger

| Finding ID | Description | Status |
|---|---|---|
| <slug-1> | <one-line description> | closed |
| <slug-2> | <one-line description> | open |

(Every file in `docs/agent/findings/` MUST have a row here.)

## Crate inventory (or module inventory for non-Rust projects)

| Crate | Status |
|---|---|
| `<name>` | <milestone level> — <one-line role> |

## In-flight at this turn

If anything is currently running:

- **<sprint name>** at agent `<id>` (<model>, background)
  - Branch: `<branch>` (worktree at `<path>`)
  - ADR: `<NNNN>` (Phase 1 spike)
  - Goal: <verbatim from ADR done-means>
  - When agent reports back: <CTO 守闸 protocol>

If nothing in flight: write **ZERO sub-agent in flight**.

(Don't keep historical "currently in-flight" sections from prior turns.
Delete or archive.)

## Audit / external review follow-ups

| Audit ID | Topic | Status | Commit / ADR |
|---|---|---|---|
| #1 | <topic> | DONE / queued / partial | <SHA / TBD> |

## Phase F (or future) backlog

Out-of-scope items deferred to next phase. Each must have:
- **Trigger condition** (what unblocks it)
- **Done means** (falsifiable success criterion)
- **Effort estimate** (calibrated against AI velocity)

If you can't fill these 3 fields, the item is fantasy not plan.

## How to resume next session

1. Read `MEMORY.md` (or equivalent index)
2. Read this file for current state
3. Read `<runbook>` for SOP catalogue
4. Run `git log --oneline -10` to verify HEAD claim
5. Run `git worktree list` to see in-flight worktrees
6. If sprints completed since last update: 守闸 protocol → merge → re-snapshot

**Authoritative source for current state is git log + this file.**
When in doubt, run the verification commands above before acting on
a snapshot claim.

---

## Anti-sediment checklist (run when updating snapshot)

- [ ] HEAD field matches `git log -1 --format=%H` (not from memory)
- [ ] Cumulative tests reflect actual `cargo test --workspace` output, not P9-reported
- [ ] ADR roster table has rows for ALL files in `docs/agent/adr/*.md`
- [ ] Findings ledger has rows for ALL files in `docs/agent/findings/*.md`
- [ ] Binary verification list is **a single section** (no duplicate stale copies)
- [ ] No "in-flight at this turn" residue from prior turns
- [ ] Phase F backlog items each have trigger + done-means + effort
