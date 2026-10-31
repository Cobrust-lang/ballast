---
name: Adopting-project snapshot gate
description: Four gate corrections back-ported from a later adopting project, which is not named in this repo. The snapshot roster is a failing script, last_verified_commit must resolve, evidence grades do not promote, and the project chooses its drift axis.
type: reference
version: 1.0.0
date: 2026-10-31
status: active
relates_to: [skill:SKILL.md §"Documentation Discipline", templates:snapshot-template.md, scripts:check_ballast_docs.py, reference:failure-modes-catalogue.md F1]
---

# Adopting-project snapshot gate

A later project adopted the discipline outside the origin compiler and sent
back four corrections. The project is not named here. None of its systems,
locations, or evidence are part of this repo. What follows is the method.

These are not new failure-mode numbers. They close a hole F1 already names:
a declared invariant that nothing checks. The check is
[`scripts/check_ballast_docs.py`](../../../../../scripts/check_ballast_docs.py).
This methodology repo runs `python3 scripts/check_ballast_docs.py --self-test`
from `scripts/doc-coverage.sh`. An adopting project runs the same script
against its own root and wires that command into CI.

## Delta 12 — Ancestry, exactly once, and a script

**What changed.** The snapshot no longer claims that its HEAD field equals
`git log -1` at write time. That equality dies in the commit that records
the snapshot. The durable invariant is weaker and still true afterwards:
`base_head` is an ancestor of `HEAD`. Equality remains allowed. It is not
required.

Every ADR file appears exactly once in `## ADR roster`. Every finding file
appears exactly once in `## Findings ledger`. Every roster id has a file.
The gate fails closed. A checklist in the template does not satisfy it.

**Why.** Requiring equality makes the first honest snapshot commit look
wrong, so people stop running the check. A roster that is only re-read by
the author gets a second copy of a row, or loses one, within a few waves.

Ancestry does not prove the prose is fresh. A `base_head` from many
commits ago is still an ancestor, and the gate passes. What ancestry
proves is that the snapshot describes this history, and that the check
still passes after the snapshot commit. Freshness of a claim is its
evidence grade, or a re-stamped `last_verified_commit`, not equality
with HEAD.

**How to apply.** Put `base_head` in the snapshot frontmatter. Run
`scripts/check_ballast_docs.py` on the repository. Do not add a prose
section that restates this delta and call that enforcement.

## Delta 13 — `last_verified_commit` must resolve

**What changed.** The field is a 40-character SHA that
`git merge-base --is-ancestor` accepts against `HEAD`. `TBD`, an empty
value, and a shortened SHA fail. No document id is exempt.

**Why.** A gate that only checks that the key exists accepts `TBD` on a
closed finding. Exempting the founding ADR, because it predates the
frontmatter, lets the decision everything else stands on skip the schema.

**How to apply.** Stamp the real SHA in the same commit as the decision or
the re-verification. If the founding document cannot yet carry the schema,
migrating it is the work. An `if id != 0001` branch in the gate is itself
a finding, not a configuration option.

## Delta 14 — Evidence grades do not promote

**What changed.** `## Verification summary` appears once. Each claim has a
Grade: `offline`, `review`, `deployed`, `live`, or `not-run`. A grade from
an earlier wave is not a grade for this wave. `not-run` is a grade, not an
omission. Exit 0 against a stand-in is not a live result.

**Why.** The honest-signal rule was already prose. Projects still copied a
green result forward, or let a passing fake stand in for a measurement,
because the summary had no column that made the substitution visible.

**How to apply.** When a claim was not exercised in this wave, write
`not-run`. Do not reuse the previous grade. The script rejects any other
token. It cannot notice a claim you deleted to avoid writing `not-run`;
that omission is still a miss, and the summary is where a reviewer looks
for it.

## Delta 15 — Choose the drift axis

**What changed.** Bilingual text is one split. An audience split is
another: a human procedure and an agent state machine, same filename,
cross-linked. The snapshot declares `drift_axis: bilingual` or
`drift_axis: audience`. Audience mode names `audience_human_dir` and
`audience_agent_dir`, and the gate requires those directories to contain
the same markdown names.

A single-language project does not invent a translation. A bilingual
project still pairs its languages; this repo's own pair is
`docs/human/zh` and `docs/human/en`, enforced by `scripts/doc-coverage.sh`.
That script does not choose the axis for anyone else.

A banner that contradicts the paragraph under it is not a correction.
Rewrite or delete the paragraph in the same commit. The banner becomes a
second document, and the next reader follows the older one.

**Why.** The split that silts is the split between the readers who can
disagree. Pairing a language nobody on the project reads does not catch
that. Leaving both paragraphs, with a note that one of them is stale, is
how the stale one survives.

**How to apply.** Declare the axis on the snapshot. Gate that pair. When a
section is wrong, replace it. Do not stack a dated disclaimer above it.
