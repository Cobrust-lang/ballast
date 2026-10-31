---
catalogue_id: F54
title: "Transform pass emits a derived sub-payload that a companion prepass never registered — table-lookup panic on the synthesized form"
family: F1-Sediment (companion-pass coverage gap sub-form)
severity: P2
status: ratified_2026-05-26
empirical_project: Cobrust ADR-0070 §X.3 LLVM-default flip (2026-05-26)
cobrust_local_id: F54 (f54-fmtspec-intern-prepass-gap.md)
date_ratified: 2026-05-26
cobrust_sha: 66057a4 (finding filed), 9aec0fc (parent F53 closed)
related: [F55, F56, F60]
---

# F54 — Derived sub-payload escapes the companion registration prepass

## Pattern

A lowering / transform pass emits a **derived** form of an input (a stripped,
split, or re-encoded variant), but the **companion prepass** that pre-registers
all referenceable forms into a lookup table only registered the **original**
form. At runtime the consumer asks the table for the derived form, misses, and
fails with an internal-invariant panic — not a clean error.

The shape is universal across compilers, serializers, and any "intern / register
everything up front, then look it up by value later" architecture:

1. A producer pass takes operand `P` and emits both `P` and a derived `f(P)`
   (e.g. `"FMTSPEC:.2f"` → also materializes the stripped `".2f"`).
2. A separate prepass walks the IR and pre-interns every *literal operand* it
   sees — it registers `P` but never `f(P)`, because `f(P)` does not appear as a
   literal anywhere; it is *synthesized* downstream.
3. The consumer looks up `f(P)` in the interned table → not present → panic
   ("payload not interned", "symbol not in table", "key not found").

## Root cause

The producer-pass author closed the **caller-side** gap (correct routing of the
derived value) but did not extend the **companion prepass** to cover the derived
form. The two passes have an implicit contract — "every value the producer can
emit must have been pre-registered" — that no test enforced, because the derived
path was not the default-exercised one when the producer landed.

This is F1-Sediment with a twist: the debt is not a missing feature, it is a
**coverage gap between two passes that must stay in lock-step**. When you add a
new emitted form to pass A, pass B's registration set must grow with it, in the
same change.

## Why this matters for Ballast

When an LLM agent (or any contributor) extends a producer pass, the natural unit
of work is "make the producer emit the new form correctly." The companion prepass
is a *second* edit site, often in a different function or file, with no compiler
error linking them. The failure surfaces only when the new path is exercised —
which, per the detection-gate cascade (F55/F56/F60), may be many commits later
when a config default flips.

## Empirical evidence (Cobrust 2026-05-26)

Parent finding F53 routed float f-string holes through a `FMTSPEC:.2f` sentinel
to a precision-formatting helper, materializing the **stripped** spec `".2f"`.
But the `intern_str_payloads` prepass only interned the **full** operand
(`"FMTSPEC:.2f"`); the stripped sub-payload was never registered. The
value-lookup for `".2f"` then panicked:

```
internal codegen error: str payload ".2f" not interned;
intern_str_payloads pre-pass bug
```

This was invisible until the ADR-0070 §X.3 default-backend flip routed every
build through the path. Four fixed-precision f-string tests went red. The fix
was a one-site extension of the prepass: when a payload `starts_with("FMTSPEC:")`,
also intern its stripped suffix. Post-fix the float-format suite was 33/33.

**SHAs:** finding filed at `66057a4` (the §X.3-ratified commit); parent F53
closed at `9aec0fc`.

## Detection rule

For any "register-everything-then-look-up-by-value" architecture:

> Every value form that a producer pass can *emit* and a consumer can *look up*
> must be covered by the registration prepass — including derived/synthesized
> forms that never appear as literals in the source IR. When you teach a producer
> to emit `f(P)`, grep the registration prepass for where `P` is registered and
> add `f(P)` in the same change.

CI candidate: a property test that, for a corpus of inputs, asserts every
lookup the consumer issues hits the table (no fallthrough panic).

## General Ballast mitigation

1. **Co-locate the contract.** If pass A emits and pass B registers, write the
   invariant ("B registers every form A emits") as a doc comment on both, with a
   cross-reference.
2. **Test the derived path explicitly** when you add it, not just the
   producer-side unit. A producer unit test that doesn't go through the
   table-lookup consumer will pass while the gap is live.
3. **Treat a default-flip as the audit trigger** (see F55/F56): the gap may be
   latent until the path becomes default-exercised.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F55 / F56 / F60 (this batch) | Same detection-gate cascade: latent gap exposed by a config-default flip / backend removal |
| F1 — Declared rules without enforcement | Parent family: the two-pass lock-step contract is implicit, with no enforcement gate |
