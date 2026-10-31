---
catalogue_id: F33
title: "Predicate-flip cascade discovery deficit — F29-style enumeration misses latent consumers"
family: cascade-discovery-gap
severity: P2 (methodology integrity)
status: ratified_2026-05-16
empirical_project: Cobrust v0.3.0 Phase F.3 Wave 2 (ADR-0050c Str-ownership)
cobrust_local_id: F30-candidate (predicate-flip-cascade-discovery-deficit.md)
date_ratified: 2026-05-16
second_corroborator: audit teammate a15e69b315007f341 (post-Wave-2)
---

# F33 — Predicate-flip cascade discovery deficit

## Symptoms

A sub-ADR proposes flipping a shared MIR / codegen / type-system predicate
(e.g. `is_copy_type(Ty) → bool`, `is_drop_eligible(Ty) → bool`,
`is_pointer_type(Ty) → bool`). An F29-style §"Consequences" enumeration
captures direct consumers (all call sites of the predicate found via
static `grep`).

During implementation, the DEV agent surfaces additional cascade bugs that
the enumeration missed. These are **latent consumers** — code paths that
existed in the codebase but were unreachable under the old predicate state.
Recovery wall-time scales with the latent-consumer set size, not the
direct-consumer set size.

Signature symptom: the DEV dispatch stalls or runs significantly over time
budget while triaging cascade bugs serially.

## Root cause

F29-style static `grep` enumeration finds call sites — places in the code
that call the predicate function. It cannot enumerate:

1. **Placeholder-returning stubs** that were safe under the old predicate
   (e.g. `lower_constant(Str)` returning `0` — zero overhead when Str was
   never a non-Copy type; wrong placeholder when Str becomes non-Copy).
2. **Dispatch sites with IR-level type witnesses** that no longer correlate
   with MIR type after the flip (e.g. f-string holes dispatching on `i64`
   Cranelift value-type because Str pointers happen to be `i64` in IR).
3. **Bookkeeping calls** that had zero-overhead under the old predicate
   (e.g. `set_param_count` with an off-by-one that produced correct output
   when the predicate gated off non-Copy local enumeration).

All three classes are invisible to static symbol-search enumeration. They are
only discoverable via runtime test-failure analysis after the predicate flips.

## SOP fix — shadow-flip dry-run workflow

Every predicate-flip ADR must mandate a "shadow-flip dry-run" during design:

1. **Land the flip behind a feature flag** in the design-only ADR commit
   (e.g. `#[cfg(predicate_flip_NN)]` or a runtime config toggle).
2. **Run `cargo test --workspace`** with the flag ON against the current
   HEAD corpus.
3. **Classify each new failure**:
   - Direct-consumer (enumerated in §"Consequences"): expected.
   - Latent-consumer (new, not enumerated): add to §"Consequences addendum".
   - Genuine semantic breakage from the flip: note in ADR, fix design or scope.
4. **Enumerate all latent consumers** in a §"Consequences addendum" before
   removing the flag.
5. The pre-flag baseline + post-flag baseline diff IS the complete F29
   enumeration; the pre-impl audit verifies completeness.

**Cost/benefit**: ~2× design-ADR effort (shadow-flip takes a few hours) pays
back ~10× in impl wall-time by surfacing latent consumers at design time
when enumeration-mismatch costs 1 line of doc, not 1 hour of impl debugging.

## Evidence

Cobrust ADR-0050c Wave 2, 2026-05-16:

- ADR-0050c §"Consequences" enumerated **27 direct consumers** via thorough
  pre-impl audit.
- Wave 2 DEV agent (`a2056acb07469204f`) surfaced **7 additional latent
  consumers** as cascade bugs:
  - `lower_constant(Str)` returning `0` pointer sentinel (M9-era stub)
  - f-string hole dispatch on `i64` Cranelift type
  - `set_param_count` off-by-one
  - 4 additional Wave-2 cascade fixes (per merge `aca5d87`)
- **Miss rate: 26%** (7 out of 27 enumerated consumers were missed).
- List[str] DEV recovery agent stalled at 600s mid-investigation; cascade
  bugs surfaced serially over ~5h recovery wall-time.
- A shadow-flip dry-run during ADR-0050c design could have surfaced all 7
  within 1-2h, allowing the impl PAIR DEV to start with a complete enumeration.

## Pattern signal

Watch for F33 when:
1. A sub-ADR proposes flipping a **shared predicate** (a function returning
   `bool` that gates MIR / codegen / type-check behavior on type or value shape).
2. The §"Consequences" enumeration uses **static `grep`** of call sites rather
   than **runtime-observed** consumer behavior.
3. The codebase has multiple eras of code (e.g. M9 stubs, earlier-phase paths,
   compiler extension surfaces) where different eras gated off the predicate
   differently.

## Cross-references

- F31 (ADR scope-reality divergence) — F33 extends F31's "verify-at-HEAD"
  discipline to "verify-under-shadow-flip".
- F34 (wave-2 cascade discovery deficit) — third instance corroboration of
  same pattern (narrower domain: method-dispatch infrastructure).
- Cobrust finding:
  `docs/agent/findings/predicate-flip-cascade-discovery-deficit.md`
- Cobrust ADR: `docs/agent/adr/0050c-str-ownership.md`
- Latent consumer findings:
  `docs/agent/findings/lower-constant-str-zero-pointer-m9-stub.md`,
  `docs/agent/findings/fstring-hole-mir-type-dispatch.md`

## Status

Ratified 2026-05-16. Shadow-flip dry-run workflow added to Cobrust CTO runbook
as mandatory for all predicate-flip sub-ADRs. Post-Wave-2 audit teammate
`a15e69b315007f341` confirmed the 26% miss rate as the second corroborator.
