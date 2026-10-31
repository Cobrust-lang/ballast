---
doc_kind: finding
finding_id: F68
title: "Ship the load-bearing chain first, defer the ergonomic surface sugar — and predict the deferred work's blast radius"
family: F2-Scope (increment-boundary sub-form)
severity: P2
status: ratified
empirical_project: Cobrust dora-cb Phase 1 (ADR-0076 / ADR-0074, 2026-05-29)
cobrust_local_id: F68 (f68-dora-phase1-followups.md)
cobrust_sha: 971d4ce
resolution_adr: ADR-0074 (ecosystem decorator desugar), ADR-0076 (dora .cb stream)
related: [F35, F36, "ecosystem-import-chain-pattern.md"]
---

# F68 — Ship the load-bearing chain, defer the surface sugar

## Hypothesis

A new feature has two parts: (1) a **load-bearing chain** that proves every layer
works end-to-end, and (2) a thin **surface sugar** that makes it ergonomic. The
ADR-canonical user surface is the decorator form
`@dora.node(inputs=[...], outputs=[...])`. The falsifiable scoping claim: *shipping
the explicit form `let _ = dora.node(handler)` in Phase 1 — and deferring the
decorator sugar — exercises the SAME MIR/codegen/runtime chain, so the deferred
sugar will land as pure surface-layer work with ~zero blast radius into the lower
layers.*

## Method

1. Phase 1 ships the explicit form, files F68 to track the deferred decorator
   desugar, and predicts (§"Why not extend in Phase 1?" point 3): *"The chain is
   proven without it… Adding the decorator desugar is pure HIR-layer sugar that
   lands cleanly atop the proven chain."*
2. Phase 2 (this resolution) implements the deferred decorator desugar.
3. Measure the actual blast radius: `git diff --stat` over the lower layers
   (`cobrust-mir/`, `cobrust-codegen/`, `cobrust-dora/`) + the manifest
   (`cobrust-types/src/ecosystem.rs`).

## Result

The prediction held exactly. The decorator desugar landed **HIR-only**:

| Layer | Predicted | Actual diff |
|---|---|---|
| HIR (`cobrust-hir/src/lower.rs`) | ~50 lines new sugar | new free fns: `is_decoratable_module_method`, `validate_module_node_decorator_shape`, `build_eco_module_register_call`, `inject_pending_eco_decorators` fork |
| MIR / codegen / dora-runtime | 0 / 0 / 0 | **EMPTY** — `git diff --stat` over all three is 0/0/0 |
| HIR error enum (`error.rs`) | maybe a new variant | **0** — the existing `EcosystemDecoratorShape { detail, span, suggestion }` free-text fields absorbed every module-receiver diagnostic |
| Manifest (`ecosystem.rs`) | maybe widen the row | **0** — `inputs=`/`outputs=` kwargs validated as list-of-str literals then **dropped**; synthesised call is byte-identical to the proven explicit form |

The deferred sugar was a strictly-additive recognition+synthesis layer. A second,
finer chain-generality point also held: the new shape (module-alias receiver,
`@dora.node`) reused the *same* `try_synth_ecosystem_call` Case-1 path that the
explicit form already drove — the desugar's only job was to *produce the call the
chain already handled*, not to extend the chain.

## Conclusion

Two reusable lessons:

1. **Increment boundary: cut between "proves the chain" and "polishes the
   surface."** Ship the load-bearing chain (the part that touches every layer and
   carries integration risk) first, even in a less-ergonomic form. Defer the
   surface sugar to a follow-up — it is the part with the *smallest* blast radius,
   so deferring it costs the least and de-risks the most. The explicit form
   `dora.node(handler)` and the eventual decorator form
   `@dora.node(inputs=..., outputs=...)` lower to byte-identical calls; the sugar
   was never load-bearing.

2. **Make the deferred work's blast-radius prediction falsifiable, then check
   it.** F68 wrote down "pure HIR-layer, 0 lower-layer change" as a prediction at
   defer-time. The follow-up verified it with `git diff --stat` = 0/0/0. A scope
   defer that names *which layers it will and won't touch* turns a vague "we'll do
   it later" into a testable contract — and a violated prediction (sugar leaking
   into MIR/codegen) would itself be the signal that the chain wasn't as general
   as claimed.

This is the surface-side complement to the **chain-generality property** of a
well-factored ecosystem-import path: a new module/shape adds ~0 HIR-semantic / 0
MIR / N codegen-extern lines (see `ecosystem-import-chain-pattern.md`). F68 is the
empirical confirmation that the property held when exercised by a genuinely new
receiver shape (module alias vs let-bound handle).

## Detection rule

When deferring an increment, the defer note MUST state which layers the deferred
work will touch and which it will NOT (a blast-radius claim). When the deferred
work lands, run `git diff --stat` over the "will NOT touch" set; a non-empty diff
there is a finding (the original increment's chain-generality claim was wrong, or
the defer was mis-scoped).

## Cross-references

- Cobrust finding `f68-dora-phase1-followups.md`; resolution commit `971d4ce`
  (HIR-only desugar). Tests: `crates/cobrust-cli/tests/decorator_dora_e2e.rs`
  (2 positive + 4 negative), no regression in `dora_hello_e2e` (explicit form
  still supported).
- ADR-0074 (decorator desugar machinery), ADR-0076 §Q4 (decorator-form decision).
- §2.5 Direction B (LLM-first): every new shape-gate diagnostic in
  `validate_module_node_decorator_shape` carries a fix-suggesting message.
- F35 (commit-msg vs diff drift): Phase 1's commit scoped accurately to the
  explicit-form surface it actually shipped — no drift, the increment boundary
  was honestly described.
- `ecosystem-import-chain-pattern.md` — the chain whose generality this finding
  confirms.
