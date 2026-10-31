---
catalogue_id: F56
title: "Correctness fix landed in only one of two parallel implementations — the unfixed backend silently produces wrong results until it becomes default"
family: parallel-implementation drift + detection-gate cascade
severity: P1 (silent wrong-answer, not a crash)
status: ratified_2026-05-27
empirical_project: Cobrust ADR-0070 §X.3 LLVM-default flip (2026-05-27)
cobrust_local_id: F56 (f56-llvm-double-neg-infer-local-types-gap.md)
date_ratified: 2026-05-27
cobrust_sha: b5b7318 (infer_local_types ported to LLVM backend)
related: [F54, F55, F60, F37]
---

# F56 — Correctness fix in one backend, silent garbage in its twin

## Pattern

A system keeps **two parallel implementations** of the same contract (two
codegen backends, two serializers, an interpreter + a compiler, a fast-path + a
reference-path). A correctness fix — a non-obvious algorithm that the naive
implementation needs to get right — is landed in **one** of them. The other
keeps the simpler-but-wrong path, justified by an explicit "this backend takes
the simpler fallback for now" comment. As long as the fixed one is the default,
everything looks correct. Flip the default to the unfixed twin and it **silently
produces wrong answers** — no crash, just incorrect output that passes any test
not asserting exact values.

This is more dangerous than a missing feature: a missing feature errors loudly;
a missing *correctness pass* in a parallel impl returns plausible-looking garbage.

## Root cause

Two compounding dynamics:

- **Parallel-impl drift**: the team fixes the path currently in use and defers
  the same fix in the twin to "later," recording the deferral in a code comment
  rather than a tracked gate. The comment is honest but inert — nothing fails
  while the unfixed path is dormant.
- **Type/representation under-inference**: the specific Cobrust instance was a
  synthetic temp typed "unknown," which the fixed backend converged to its real
  type via a fixed-point dataflow pass, and the unfixed backend defaulted to a
  fallback type — so a float was stored into an integer slot and negated as an
  integer bit-pattern. The general lesson is that *any* correctness-load-bearing
  analysis present in one impl and absent in the other is latent wrong-answer debt.

## Why this matters for Ballast

When you maintain N parallel implementations of one contract, **every
correctness fix is an N-site obligation**, but the natural unit of agent work is
one site (the one currently exercised). The deferred sites are invisible until a
default-flip or a removal forces them live. Before you delete the "reference"
implementation (Cobrust's §X.4 Cranelift removal), you must port every
correctness-bearing pass it has that the survivor lacks — *the removal deletes
the only correct path otherwise.*

## Empirical evidence (Cobrust 2026-05-27)

A double-negation of a float constant, `let y: f64 = -(-3.25)`, printed garbage
under the LLVM backend after the §X.3 default-flip:

```
test fr14_value_correctness_double_neg_const ... FAILED
fr14 stdout mismatch: "0\n"   (expected "1\n")
```

The two synthetic MIR temps were typed `Ty::None`, which the LLVM backend's
`lower_ty` mapped to i64 (its documented "simpler fallback"); the float was
stored as raw bits into an i64 slot and the outer negation ran as a
two's-complement int-negation of the IEEE-754 bit pattern → wrong value. The
Cranelift backend converged those temps to f64 via a fixed-point
`infer_local_types` dataflow; the LLVM backend's own doc comment admitted it
"explicitly does not" — that deferred debt biting.

Notably, sibling fixtures `(a+b)*c` and `-a+b` *passed*, because their depth-2
chain terminated in a binop, which a narrower §X.3 bitcast workaround already
handled — so the failure was a sharp edge case (all-unary chain) that a coarse
test would have missed.

**Resolution:** the Cranelift fixed-point `infer_local_types` pass was **ported**
to the LLVM backend (not patched around), the previously-`#[ignore]`'d fixture
un-ignored, and the whole crate stayed green. **SHA:** `b5b7318`.

## Detection rule

> For any contract with N parallel implementations: maintain an explicit list of
> correctness-bearing analyses/passes per implementation, and require that a fix
> to one is mirrored (or explicitly + trackably deferred with a failing/ignored
> differential test) to the others. Before removing any implementation, diff its
> pass set against the survivor's and port every correctness-load-bearing one.

CI candidate: a **differential test** that runs the same value-asserting corpus
through every backend and fails if outputs diverge — this catches silent
wrong-answer drift that single-backend tests cannot.

## General Ballast mitigation

1. **Port, don't patch around.** The narrow §X.3 bitcast workaround handled the
   binop case but not the all-unary case; the durable fix was porting the whole
   inference pass. Workarounds in a parallel impl tend to cover only the cases
   the author happened to test.
2. **Value-assert in cross-backend tests.** "It ran without crashing" is not a
   correctness signal for a parallel impl; assert exact outputs and run them
   through every backend.
3. **Pre-removal pass-parity audit.** Deleting the reference implementation is a
   one-way door — audit its correctness passes against the survivor first.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F54 / F55 / F60 / F61 (this batch) | Same §X.3/§X.4 detection-gate cascade — latent backend gap exposed by default-flip/removal |
| F37 (Cobrust) — silent-rot-on-accepted-debt | The deferral lived as an inert code comment, not a tracked gate — silent rot of a correctness obligation |
| F1 — Declared rules without enforcement | Parent family: "mirror correctness fixes across impls" is implicit; no gate enforced it |
