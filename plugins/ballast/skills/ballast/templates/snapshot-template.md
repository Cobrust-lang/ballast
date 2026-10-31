<!-- Template for a project state snapshot.
     One file per project, lives in agent memory or docs/state/.
     Updated end-of-turn by the CTO or its delegate.
     Source of truth for future agents post-compaction. -->

---
name: <project> state snapshot (compaction-resilient)
description: Authoritative compressed state of <project> at <date>. Update at end-of-CTO-turn so context compaction never loses load-bearing facts.
type: project

doc_kind: snapshot
base_head: <40-char SHA that is an ancestor of HEAD>
last_verified_commit: <40-char SHA that is an ancestor of HEAD>
drift_axis: bilingual | audience
# audience mode also requires:
# audience_human_dir: docs/human-procedure
# audience_agent_dir: docs/agent/procedure

schema_invariant: |
  Every ADR file appears exactly once in §"ADR roster", and every roster id has a file.
  Every finding file appears exactly once in §"Findings ledger", and every ledger id has a file.
  §"Verification summary" appears exactly once. Each Grade is offline, review, deployed, live, or not-run.
  base_head is an ancestor of HEAD. Equality is allowed and is not required.
  last_verified_commit resolves to an ancestor SHA. No document id is exempt.
---

## Project root + constitution

**Project root**: <absolute path>
**Constitution**: `<path to founding doc, e.g. CLAUDE.md>`
**Mandate**: <1-2 sentence statement of what the project commits to>

## main branch state

- **Base HEAD**: `<SHA>` — ancestor of the commit that records this snapshot. Do not require this field to equal `HEAD` after that commit lands.
- **HEAD when written**: `<SHA>` — `<commit message tag>`. Informational. The gate checks ancestry, not equality.
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
| 0001 | <title> | <phase> | <SHA> |

(Every ADR file in `docs/adr/` or `docs/agent/adr/` has exactly one row here,
and every row has a file. `scripts/check_ballast_docs.py` enforces this.
Delete the example row if that ADR does not exist.)

## Findings ledger

| Finding ID | Description | Status |
|---|---|---|
| <slug-1> | <one-line description> | closed |
| <slug-2> | <one-line description> | open |

(Every file in `docs/agent/findings/` has exactly one row here, and every row has a file. Delete the example rows.)

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

## Verification summary

| Claim | Grade | Evidence |
|---|---|---|
| <what this wave actually showed> | offline \| review \| deployed \| live \| not-run | <where the evidence is> |

`not-run` is a grade. Do not leave the row out, and do not copy a previous wave's grade forward. A passing stand-in is `offline` or `review`, not `live`.

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

- [ ] `python3 scripts/check_ballast_docs.py` passes. A ticked box is not the gate.
- [ ] `base_head` is an ancestor of `HEAD` (recorded from git, not memory). Equality was not required.
- [ ] `last_verified_commit` on this file, every ADR, and every finding is a full SHA and an ancestor. No `TBD`. No id exemption.
- [ ] ADR roster and findings ledger are bijections with the files. Each id appears once.
- [ ] Verification summary is a single section, and every grade is `offline`, `review`, `deployed`, `live`, or `not-run`.
- [ ] No correction banner left above a paragraph it contradicts. Rewrite or delete the paragraph.
- [ ] `drift_axis` is declared. Audience mode pairs the two directories by filename.
- [ ] No "in-flight at this turn" residue from prior turns
- [ ] Deferred items each have trigger + done-means + effort
