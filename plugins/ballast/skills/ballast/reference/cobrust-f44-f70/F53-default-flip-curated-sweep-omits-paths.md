---
catalogue_id: F53
title: "Default-flip blocked by curated-sweep blind spot — a 'stability' sweep declared a backend production-ready by running a curated corpus that excluded the integration paths the default flip would actually traverse"
family: F37-SilentRot (sweep-methodology sub-form) + F35-ClaimDrift
severity: P1 (a flip to default would have shipped 30+ silent regressions)
status: resolved_2026-05-26
empirical_project: Cobrust LLVM-default flip attempt (2026-05-26)
cobrust_local_id: F53 (f53-llvm-default-flip-aggregate-gap.md)
cobrust_sha: 4aa38da (pre-fix) → resolution same-day (lower_aggregate List + FormatString land)
resolution: enumerate every path the would-be default is reachable from; never flip without GREEN on that full set
related: [F45a, F47, F44, F37-SilentRot, F35-ClaimDrift]
---

# F53 — Default-flip blocked by curated-sweep blind spot

## Pattern

A component is about to be promoted to the **default** path. A "stability sweep"
over a curated corpus returns GREEN and is read as "production-ready." But the
curated corpus **omits substantial real paths** the default would actually
traverse — here, the workspace integration tests that drive the toolchain
end-to-end. The moment the default is flipped, those omitted paths light up with
dozens of failures that the sweep never exercised.

The flip is correctly rolled back (no flip without GREEN evidence — F35
discipline), and the lesson is: **a stability sweep must enumerate every path the
would-be default is reachable from**, not a hand-picked corpus that may dodge the
weak surfaces.

This is also a concrete recurrence of the F45a over-claim: surfaces marked
RESOLVED had their *direct-helper-call* fixtures passing while the
*source-literal* codegen path that should call those helpers still no-op'd.

## Root cause

- **Sweep corpus ≠ reachability set.** The curated sweep tested "language-level"
  programs but never the integration tests that drive the actual build path. A
  corpus chosen for coverage-feel can systematically miss the surfaces that route
  through the unfinished code.
- **Direct-call closure mistaken for source-level closure.** Earlier waves declared
  runtime extern functions and tested them via direct calls; the *aggregate-literal*
  codegen callsite that should emit those calls (`lower_aggregate` for list /
  format-string) still returned a null pointer. `[1,2,3]` and `f"x={x}"` produced
  null at runtime even though `__list_*` / `__fmt_*` "RESOLVED."
- **F35-ClaimDrift**: "production-ready / RESOLVED" claimed before the path that
  the flip depends on had any fixture.

## Why this is critical for Ballast / agent-driven projects

"Run the sweep, it's green, flip the default" is exactly the kind of confident
step an autonomous agent takes — and a green sweep over the wrong corpus is a trap
that *invites* the flip. The default path is the highest-blast-radius surface in
the project; promoting to it on the strength of a corpus that excludes the
integration tests means shipping silent regressions to every user at once. The
guardrail is reachability-completeness: before any default flip, the test set must
cover *every* entry point the new default is reachable from, including
compiler-level + integration-level drivers, not just a language-level sample.

## Empirical evidence (Cobrust 2026-05-26)

The flip attempt set the backend default to the opt-in implementation, then a full
`cargo test --workspace` sweep revealed **30+ failures across integration test
files driven by the real build path** that the prior 144-program "language-level"
sweep had returned GREEN on:

| Surface | Pre-flip sweep | Under default-flip | Root cause |
|---|---|---|---|
| stdin/argv e2e | GREEN | 6/15 fail | extern-call int→ptr coercion (fixed inline) |
| float e2e (panics) | GREEN | 6/33 panic | binop/cast f64-as-i64 slot (fixed inline) |
| float e2e (fstring) | GREEN | 4/33 empty | aggregate FormatString null stub (blocker) |
| list e2e | GREEN | 20/33 fail | aggregate List null stub (blocker) |
| fstring corpus | GREEN | 6/6 fail | aggregate FormatString null stub (blocker) |
| **TOTAL** | — | **42** | 6 inline-fixable, 36 require the aggregate-lowering port |

The flip was rolled back same-session (F35 discipline: no flip without GREEN). The
36 aggregate-stub failures were closed by implementing the source-literal codegen
callers (mirroring the reference backend); post-fix all four integration corpora
passed (15/15, 33/33, 31/33, 6/6 — the residual ignores being pre-existing,
unrelated). The companion F45a §8 amendment recorded the over-claim correction.

## Detection rule (process + CI gate)

1. **Reachability-complete sweep before any default flip.** Enumerate *every*
   entry point the would-be default is reachable from (language-level programs
   **and** workspace integration tests that drive the real toolchain) and require
   GREEN on the full set — not a curated subset.
2. **No flip without GREEN evidence** (F35): the flip commit/ADR cites the full
   sweep result; a rollback on red is mandatory, not optional.
3. **Direct-call ≠ source-level** (inherited from F45a): for any "RESOLVED"
   runtime surface, require a fixture that exercises the *source-level construct*,
   not only a direct helper call.
4. **Cite the finding in the re-flip commit** so the blind-spot lesson travels with
   the eventual successful flip.

## Resolution path

1. **Expand the sweep** to the reachability set (integration + compiler-level
   drivers), pairing the curated corpus with the real-driver test files.
2. **Implement the omitted path** (here: the aggregate-literal codegen callers),
   mirroring the working reference implementation.
3. **Gate the flip on full-set GREEN**; roll back instantly on any red; keep the
   inline-fixed correctness wins even when the flip itself stays blocked.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F45a — Stub catalogue systemic | Parent: F53 is the over-claim correction — direct-helper fixtures passed while the source-literal aggregate path still no-op'd |
| F47 — Type-conditional codegen empty output | Sibling root cause: a `Ty::None`-typed temporary routes a value down the wrong (null/int) codegen arm — same default-placeholder-type mechanism |
| F44 — CI cache stale-green | Sibling: the curated sweep's "GREEN" had the same flavour of partial coverage as a stale-cache green |
| F37 — Silent-rot-on-accepted-debt | Parent: F53 extends F37 to *sweep methodology* — a corpus that omits real paths falsely declares production-readiness |
| F35 — Commit-msg vs diff drift | Parent: the flip rollback honored "no false 'flip landed' claim"; the prior "RESOLVED" was claimed ahead of the fixture |
