---
catalogue_id: F47
title: "Type-conditional codegen branch produces empty/wrong output — a default-typed temporary (None/0) silently routes a value down the wrong formatting/lowering arm"
family: F-Codegen (type-propagation correctness)
severity: P1 (silent wrong output — no crash, no diagnostic)
status: ratified_2026-05-25
empirical_project: Cobrust f-string runtime (v0.5.1, caught 2026-05-22, fixed 2026-05-25)
cobrust_local_id: F47 (f47-fstring-user-fn-str-interp-empty.md)
cobrust_sha: cf0864c (fix + corpus) ; dcb1714 (finding update)
resolution: propagate the callee's declared return type to the synthetic _callret local + fire the str-materialize branch for the return slot
related: [F50, F53, F45, F-Codegen]
---

# F47 — Type-conditional codegen branch silently emits empty/wrong output

## Pattern

A codegen step dispatches on the *declared type* of a value to pick a lowering /
formatting arm. When the value flows through a synthetic temporary that was
declared with a **default placeholder type** (`None`, `i64`, "unknown") instead
of the value's real type, the dispatch picks the wrong arm — and the wrong arm
fails *silently* (empty string, raw pointer printed as a decimal, zero) rather
than crashing. There is no error, no diagnostic; the output is just quietly
wrong.

The defect is type-specific and source-specific: it only fires when the value's
provenance defeats the place where the real type would otherwise have been known
(here: a value *returned by a function* vs the same value as a *literal*).

## Root cause

- **Synthetic temporaries default-typed.** The compiler manufactures a
  destination local for a call result (and for the function return slot) and
  declares it with a convention placeholder (`Ty::None`) rather than threading the
  callee's *actual* declared return type.
- **Downstream dispatch trusts that type.** The formatter inspects
  `local.ty` to choose `format_as_str` vs `format_as_int`. With the placeholder,
  `is_str` is false, so a heap-string pointer is fed to the integer path (printed
  as a number / dropped) instead of the string path.
- **The literal path has a symmetric hole.** A `return "literal"` writes a
  `Constant::Str` into a return slot also declared with the placeholder; the
  str-materialize special-case required the destination type to be `Str`, so it
  fell through to a stub returning `0`.

## Why this is critical for Ballast / agent-driven projects

This is a `compile-time-catch` value that *escaped to runtime* — the F47 finding
is itself a CLAUDE.md §2.5 datapoint. The model writes the most natural code
(`f"{my_fn()}"`), it type-checks, it compiles, and it produces wrong output with
no signal the model can act on. Type-conditional lowering is exactly the kind of
seam where a default-placeholder temporary turns a would-be type error into a
silent behavioral bug. The fix (propagate real types onto synthetic locals)
restores the invariant that the lowering dispatch can trust `local.ty`.

## Empirical evidence (Cobrust 2026-05-22 → 25)

Minimal repro (six lines):

```cobrust
fn line_count(n: i64) -> str:
    if n == 1: return "1 bottle"
    return f"{n} bottles"

fn main() -> i64:
    let c: str = line_count(99)
    print(f"{c} of beer on the wall")
    # actual:   " of beer on the wall"   (the {c} slot is EMPTY)
    # expected: "99 bottles of beer on the wall"
    return 0
```

String literals and integers interpolated correctly in the *same* f-string; only
a `str` whose source was a user-function return value came out empty. Root cause
confirmed in two layers: (1) the MIR `_callret` destination local was declared
`Ty::None` regardless of the callee's real return type, so the f-string formatter
chose the int arm for a heap-string pointer; (2) both backends' `Use(Constant::Str)`
materialize branch required the destination type to be `Str`, but the function
return slot was `Ty::None`, so `return "literal"` fell through to a `0` stub. Fix
shipped at `cf0864c` with a 6-fixture regression corpus covering simple / concat /
multi-slot / branch-returns / int-mixed / literal-baseline cases.

## Detection rule (CI gate)

1. **Corpus the value-provenance matrix.** For any type-conditional lowering,
   test the same type from *every* provenance: literal, variable, **function
   return value**, method return value, branch result. The literal case passing
   does not prove the return-value case passes.
2. **Synthetic-local type-propagation invariant.** Assert (in a unit test on the
   lowering pass) that a manufactured destination local for a call result carries
   the callee's declared return type, not a placeholder.
3. **Cross-backend parity.** Run the corpus on every backend — the same
   type-dispatch hole tends to exist in each independently-written backend.

## Resolution path

1. **Thread real types onto synthetic temporaries** at manufacture time (call
   results, return slots) so downstream type-dispatch is trustworthy.
2. **Fire the type-specific materialize branch** for the return slot too, not just
   for ordinary named locals.
3. **Add the provenance-matrix corpus** as the regression gate; run it on all
   backends.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F53 — Default-flip aggregate gap | Sibling root cause: a `Ty::None`-typed binop/aggregate temporary routes a value down the wrong (null/int) codegen arm — same default-placeholder-type mechanism |
| F50 — LSP/CLI diagnostic divergence | Same-family (codegen/frontend), same reporting window: a name/type table that one surface trusts and another lacks |
| F45 — Stub silently shipped | Adjacent: both are "compiles + runs but silently wrong/empty" defects with no diagnostic |
| F-Codegen | Parent family: type information must be propagated onto every synthetic value the compiler manufactures, or type-conditional lowering misfires |
