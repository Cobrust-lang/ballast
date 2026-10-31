---
catalogue_id: F39
title: "DEV commit message scope drift — commit message preserves original-spec framing after mid-sprint scope reduction"
family: F1-Sediment (commit-message surface-drift sub-form; sibling of F38)
severity: P2 (audit/traceability integrity)
status: ratified_2026-05-18
empirical_project: Cobrust v0.3.0 Phase H Wave 3 (ADR-0055d commit 7100849)
cobrust_local_id: F35-sibling-commit-msg (feedback_dev_agent_commit_msg_vs_diff_drift.md)
date_ratified: 2026-05-18
second_corroborator: Tier-1 audit ADR-0055d §13 amendments (`49ec536`) caught and filed
---

# F39 — DEV commit message scope drift

## Symptoms

A DEV agent is dispatched with an original §2 scope (e.g. "implement new Rust
module X"). Mid-sprint, the agent correctly discovers the scope should be
reduced (e.g. "X was already partially shipped; actual work is doc-expansion +
test un-ignore"). The agent implements the reduced scope correctly.

However, the `git commit -m` message describes the **original** scope, not the
**final** scope. A reader of `git log` gets a false picture of what landed:

- `feat(X): implement module X with 19 arms (Wave-N LARGEST DEV)` — but the
  diff contains no Rust implementation, only pseudocode expansion + test
  un-ignore.

Future agents reading `git log` to reconstruct sprint history will believe a
Rust module was implemented when it was not.

## Root cause

The DEV agent's in-context "intent" at commit time is shaped by the original
dispatch prompt. When scope reduces mid-sprint, the original framing
(the names, the "feat" prefix, the specific code claims) remains strongly
activated in context. The commit message is generated from this activated
framing, not from a fresh diff-based description.

The failure has two sub-components:

1. **Scope framing anchoring**: the original spec names ("cb-mirror", "19-arm",
   "Ctx") were in the dispatch prompt, which is the longest and most
   context-forming document in the agent's window.
2. **Commit-message shortcut**: the agent treats the commit message as a
   summary of "what I was working on" rather than "what I actually changed."

## Rule — commit message must mirror final-form scope

**Before `git commit -m`**, the DEV agent MUST answer: "Does this message
describe what is actually in the diff, or what was in the original dispatch
spec?"

If scope changed mid-sprint:
1. Write the commit message to describe the **final diff** (what files changed
   and why).
2. If the original spec framing is historically useful, add it as a
   parenthetical or an ADR note — NOT in the `git commit -m` subject line.
3. Use the **correct conventional-commit prefix**: `feat` implies new Rust
   source code. `docs` + `tests` implies documentation expansion and test
   corpus changes. Mismatched prefix is the most common symptom of scope drift.

**Quick self-check before committing**:
- Run `git diff --stat HEAD` and read the file extensions.
- If all changed files are `.md` / `.cb` + test files with `#[ignore]` removal:
  the prefix should be `docs`/`tests`, not `feat`.
- If the message says "implement X" but no `.rs` impl files are in the diff:
  the message is wrong.

## Evidence

Cobrust ADR-0055d Wave 3 LARGEST DEV, 2026-05-18:

**Original dispatch scope**: "cb-side Rust impl mirror of `check.rs` — a
`check_cb.rs` module with `synth_expr` 19-arm + `Ctx` struct + method-table."

**Actual mid-sprint scope reduction**: Wave-3 already partially shipped scope
was recognized; actual work reduced to:
- 80-test `#[ignore]`-marker deletion (test un-ignore)
- ADR ratification
- `check.cb` doc-ref expansion (98 → 1390 lines of Cobrust pseudocode)

**Committed message** (SHA `7100849`):
```
feat(check-cb): synth_expr 19-arm + Ctx + method-table cb-mirror (Wave-3 LARGEST DEV)
```

**What the message claims**: a new Rust `check_cb.rs` module implementing
`synth_expr` with 19 match arms, a `Ctx` struct, and a method-table mirror.

**What the diff actually contains**: `.cb` pseudocode doc-ref expansion
(98 → 1390 lines), `#[ignore]` removal from 80 tests, ADR ratification.
No new `check_cb.rs` Rust module; no 19-arm implementation.

**Correct message** would have been:
```
docs(check-cb): expand check.cb doc-ref 98→1390 lines + un-ignore 80 tests (Wave-3 LARGEST DEV)
```

Tier-1 audit (ADR-0055d §13 amendments, commit `49ec536`) caught this and
filed it as the F35-sibling finding for Ballast upstream.

## Downstream consequences of F39

1. Future agents reading `git log` to reconstruct sprint history believe the
   Rust module was implemented.
2. Tier-1 audit teammates must check the diff against the message for every
   DEV merge — this is audit overhead that clean commit messages would eliminate.
3. Ballast sprint accounting (which ADRs are "impl-done" vs "doc-only") is
   corrupted, leading to duplicate dispatch risk on the next sprint.

## Cross-references

- F38 (TEST corpus exit-0 claim drift) — sibling failure mode in the same
  PAIR dispatch: F38 is at TEST merge time; F39 is at DEV commit time. Both
  produce claims about work that don't match the actual artifact.
- F36 (agent self-disciplinary rule skip) — F39 is often an F36 instance:
  the agent "knows" the commit message should match the diff but skips
  the self-check because it judges the sprint "obviously correct."
- Cobrust memory:
  `feedback_dev_agent_commit_msg_vs_diff_drift.md`
- Cobrust ADR: `docs/agent/adr/0055d-*.md` §13 amendments (commit `49ec536`)
- Cobrust incident: commit `7100849` (`c89d540` in Cobrust repo — the
  feat(check-cb) commit with scope-drifted message)

## Status

Ratified 2026-05-18. Diff-first commit message check added to Cobrust DEV
dispatch prompt template. Second corroborator: Tier-1 audit teammate independently
identified and escalated the scope-drift in the same session it was introduced.
