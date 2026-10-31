---
catalogue_id: F38
title: "TEST corpus exit-0 claim drift — TEST author's cargo check clean-claim not verifiable by DEV on post-merge crate-graph"
family: F1-Sediment (corpus-verification sub-form)
severity: P1 (methodology integrity)
status: ratified_2026-05-18
empirical_project: Cobrust v0.3.0 Phase H Wave 2 (ADR-0055b TEST corpus)
cobrust_local_id: F35 (implicit in 0055b Tier-1 audit honesty addendum)
date_ratified: 2026-05-18
second_corroborator: confirmed (DEV agent 0055b found 28 hidden compile errors at TEST corpus merge SHA)
---

# F38 — TEST corpus exit-0 claim drift

## Symptoms

In an F32 P10-direct PAIR dispatch:

1. TEST agent authors a corpus of `#[ignore]`-annotated tests, runs
   `cargo check` (or `cargo build`) on its own branch, reports
   `[TEST-CORPUS-READY]` with "0 compile errors."
2. P10 reviews and dispatches DEV with TEST's commit SHA.
3. DEV receives the corpus, attempts to un-ignore tests, and hits
   **compile errors that were not present on TEST's branch** — typically
   28-50 errors from API changes in a crate the TEST author compiled against
   but is now at a different version on main after sibling merges.

The TEST agent's clean-claim was correct on TEST's branch at TEST's merge time.
It is incorrect on the post-merge crate-graph that DEV inherits. The gap is not
TEST's fault — it is a structural verification-window problem.

## Root cause

TEST merges its corpus at time T₁. DEV receives the corpus at time T₂.
Between T₁ and T₂:

- Other sprints may merge changes to shared crates (e.g. a Wave-2 sibling
  merges a `Span::new` API change from 2-arg to 3-arg).
- The `Cargo.lock` and workspace `Cargo.toml` on main at T₂ may diverge from
  the TEST branch's state at T₁.
- Tests that compiled against the old API at T₁ now have 28+ compile errors
  at T₂ against the new API.

The TEST corpus's `#[ignore]` annotation is supposed to signal "do not run me
yet" but NOT "I might not compile." DEV inherits a corpus that doesn't compile
and cannot immediately distinguish: "the test is wrong" from "the API changed
under me" from "the corpus never compiled even at T₁."

## SOP fix — DEV must re-verify corpus on post-merge state before un-ignore

Add to every DEV agent's dispatch prompt:

```
**Step 0 (mandatory, before any implementation)**:
Run `cargo check --workspace` on the current HEAD (post-merge state).
If compile errors appear in the TEST corpus, do NOT proceed to un-ignore.
Instead:
1. Record the compile errors in a §"Corpus state" section.
2. Determine if errors are from API changes (crate diff vs. TEST branch)
   or pre-existing test authoring bugs.
3. Fix API-change errors (mechanical — update signatures to match current API).
4. File a finding if errors indicate test logic bugs.
5. Only after `cargo check` clean: proceed to un-ignore and implement.
```

This converts the "TEST corpus is ready" assumption into a verified invariant
that DEV checks before starting work.

**For TEST agents**: optionally add a `cargo check --workspace` run as the final
step before `[TEST-CORPUS-READY]` signal, and record the SHA + toolchain version
the check passed against. This narrows the verification window but does not
eliminate it (merges between TEST's final check and DEV's receipt can still
produce errors).

## Evidence

Cobrust ADR-0055b Phase H Wave 2, 2026-05-18:

- TEST corpus merged at `2e7ccb2` (Wave 2 error.rs + lib.rs cb-mirror corpus,
  +35 tests, all `#[ignore]`).
- TEST merge message: "F28 strict + F34 anchors verified." Implicit in
  "Tier-1 audit GO."
- DEV dispatch at `84e1286` (rebase onto main after `0cfeb3f` honesty addendum).
- DEV agent (`0055b DEV`) discovered **28 hidden compile errors** at the TEST
  corpus merge SHA due to stale `Span::new` 2-arg API (changed to 3-arg in a
  sibling sprint between TEST's merge and DEV's dispatch).
- DEV corrected the 28 API-change errors mechanically, then un-ignored and
  implemented, reaching 41/41 PASS.
- Tier-1 audit `929cd4a` filed an honesty addendum (ADR-0055b §10.3) noting
  the hidden compile errors as a finding.

## Relationship to F32

F38 is a downstream consequence of F32 (P10-direct PAIR pattern). The PAIR
pattern correctly separates TEST and DEV to eliminate same-agent bias. F38
shows that even with correct separation, a **temporal gap** between TEST's
clean-compile and DEV's execution can introduce compile errors. The fix is at
the DEV agent's Step 0, not at the PAIR separation level.

## Cross-references

- F32 (PAIR pattern impl gap) — F38 is the temporal-gap failure mode that
  correct PAIR dispatch does not prevent.
- F39 (DEV commit message scope drift) — sibling: both are DEV-agent
  execution-time failures in the PAIR pattern.
- Cobrust ADR: `docs/agent/adr/0055b-error-cb-mirror.md` §10.3 honesty
  addendum (commit `0cfeb3f`)
- Cobrust merge: `84e1286` (Wave-2 DEV rebase + 41/41 PASS)

## Status

Ratified 2026-05-18. DEV Step 0 verification protocol added to Cobrust DEV
dispatch prompt template. Second corroborator: DEV agent independently
discovered and fixed the 28 compile errors, confirming the gap is
mechanically reproducible.
