---
catalogue_id: F34
title: "Wrapper-type bidirectional unify produces AmbiguousType cascade in legacy code"
family: inference-layer-transparency-gap
severity: P1 (design correctness)
status: ratified_2026-05-17
empirical_project: Cobrust v0.3.0 Phase G Wave 1 (ADR-0052a borrow/ref)
cobrust_local_id: F31-candidate (0052a-wave1-dev-bidirectional-unify-cascade.md)
date_ratified: 2026-05-17
second_corroborator: confirmed (two consecutive DEV dispatches v1 + v2 hit identical cascade)
---

# F34 — Wrapper-type bidirectional unify produces AmbiguousType cascade in legacy code

## Symptoms

A sub-ADR introduces a new type wrapper (e.g. `Ref(T)`, `Mut(T)`,
`Option(T)` if net-new, `Slice(T)`). The ADR's §"Type inference rule" specifies
a **bidirectional unify arm**: `Ref(T) ↔ T` — the wrapper and its inner type
unify in both directions. This is motivated as a "transparency rule" so existing
code that uses `T` also works with `Ref(T)` automatically.

The first DEV dispatch hits a **142-failure cascade** across all legacy programs
that have no `Ref(T)` expressions. The cascade is all `AmbiguousType` errors,
not type mismatches or scope errors. The DEV agent re-scopes, strips the
bidirectional rule, and hits the **same cascade on the second dispatch** —
confirming the cascade is from the ADR design itself, not the implementation.

## Root cause

Bidirectional unify says: `Ref(T)` unifies with `T` in both directions. The
inference table has both arms:

```rust
// Structural arm — correct, safe:
(Ref(a), Ref(b)) => unify(a, b)

// Bidirectional arm — the problem:
(Ref(a), b)     => unify(a, b)   // Ref(T) ↔ T
(a, Ref(b))     => unify(a, b)   // T ↔ Ref(T)
```

Effect: type variable `?V` can now be resolved to EITHER `T` OR `Ref(T)` via
separate valid unifications. When a legacy program has `let x: T = expr`, the
inference table can bind `?V := T` (correct) AND `?V := Ref(T)` (also valid
via the bidirectional arm). Resolution becomes non-unique → `AmbiguousType`.

Legacy programs without any `Ref(T)` expression are affected because the
unification problem is over the entire type variable graph, not per-expression.

## SOP fix — one-way call-site coercion only

When introducing a new wrapper type:

1. **Forbid** `(Wrapper(a), b)` and `(b, Wrapper(a))` unify arms in
   `infer::unify`. Both directions of cross-wrapper unification are forbidden.
2. **Allow** only the structural arm: `(Wrapper(a), Wrapper(b)) → unify(a, b)`.
3. For ergonomic "transparency" at consumption sites: implement a
   **one-way call-site coercion** at specific binding sites only:
   - `synth_call_args`: when formal param type is `T` and actual is `Ref(T)`,
     the type checker drops the `Ref` wrapper locally.
   - Coercion is (a) local to the call-arg binding, (b) unidirectional
     (`Ref(T) → T` only, not `T → Ref(T)`), (c) scoped to fn-call arg binding
     (not `let`, return, arithmetic).
4. **Pre-dispatch checklist** for wrapper-type sub-ADRs: grep the proposed
   `infer.rs` diff for non-structural cross-wrapper unify arms; reject in ADR
   audit if found.

## Evidence

Cobrust ADR-0052a Wave 1, 2026-05-17:

- ADR-0052a §3 + §6 (borrow/ref `&s` form) mandated bidirectional
  `Ty::Ref(T) ↔ T` unify in `crates/cobrust-types/src/infer.rs`.
- **DEV v1** (`feature/0052a-dev-rejected-prelude-cascade`): 142 failures
  including 100+ LC-100 regressions, f64 fstring regression, Phase F.3
  honest-debt re-fire.
- **DEV v2** (`feature/0052a-dev-v2`): strict scope, same cascade — confirming
  the cascade is from the ADR design, not implementation scope-creep.
- **DEV v3** (`feature/0052a-dev-v3`, merged `6843a33`): replaced bidirectional
  unify with one-way call-site coercion → **0 non-0052a regressions vs main**.
- ADR-0052a revised at SHA `bcf9c7d` to document the one-way coercion design
  and prohibit the bidirectional arm.

Failure distribution for DEV v2 (strict-scope baseline):

| Category | Count |
|---|---|
| LC-100 `AmbiguousType` in legacy code | 77 |
| LC-100 `UseAfterMove` shifted to wrong sites | 23 |
| 0052a well-typed programs all-fail | 30 |
| 0052a F30-witness all-fail | 4 |
| f64 fstring regression | 6 |
| Phase F.3 honest-debt re-fired | 3 |
| **Total** | **142** |

## Relationship to F33

F33 (predicate-flip cascade discovery deficit) covers a broader predicate-flip
class. F34 is the specific inference-layer sub-case:

- F33: shared `bool`-returning predicates that gate execution paths.
- F34: type-unification arms that, when bidirectional, pollute the inference
  variable graph across the entire program under type-check.

Both share the root: a design-time decision has non-local consequences that
only manifest at impl time. F33's shadow-flip dry-run applies equally to F34
(the dry-run would have surfaced the cascade immediately).

## Cross-references

- F33 (predicate-flip cascade) — sibling; F34 is the type-inference-layer
  instantiation.
- Cobrust finding:
  `docs/agent/findings/0052a-wave1-dev-bidirectional-unify-cascade.md`
- Cobrust ADR: `docs/agent/adr/0052a-borrow-ref.md` (pre-revision SHA
  `23cadf6`; revised at `bcf9c7d`)

## Status

Ratified 2026-05-17. One-way call-site coercion design adopted in ADR-0052a
§3 + §6 + §13 at `bcf9c7d`. Second corroborator: DEV v1 and v2 independently
hit identical 142-failure cascade from the same root ADR design.
