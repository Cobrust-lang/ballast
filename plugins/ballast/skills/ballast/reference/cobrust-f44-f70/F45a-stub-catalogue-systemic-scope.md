---
catalogue_id: F45a
title: "Stub-catalogue systemic scope — when one stub-shipped surface is found, the same fallthrough usually spans the whole subsystem; enumerate every reachable callee and lead docs with the exact user-path scope"
family: F37-SilentRot (declared-coverage ≠ actual-coverage) + F35-ClaimDrift (scope-accuracy sub-form)
severity: P1 (systemic — single stub fix understates blast radius)
status: ratified_2026-05-22 (catalogue) ; resolved_2026-05-25 (all surfaces) ; amended_2026-05-26 (over-claim correction → see F53)
empirical_project: Cobrust Phase K LLVM backend (independent audit 2026-05-22)
cobrust_local_id: F45a (f45a-llvm-backend-wave3-scope-systemic.md)
cobrust_sha: cb8893c (catalogue) ; resolution via ADR-0058g sub-waves 1-6
resolution: per-surface differential fixtures + per-callee parity table in release notes + explicit user-path scope line
related: [F44, F45, F46, F51, F53, F37-SilentRot, F35-ClaimDrift]
---

# F45a — Stub-catalogue systemic scope

## Pattern

When a stub-shipped surface is discovered (F45), it is almost never isolated. The
same fallthrough mechanism — one `lower_call` no-op branch, one missing dispatch
arm — silently disables **every** callee that routes through it. The correct
response is not to fix the one reported symptom (stdout) but to **enumerate the
full catalogue** of surfaces that share the fallthrough, and to **lead every doc
update with the precise scope of who is actually affected**.

Two disciplines compound here:

- **Catalogue, don't spot-fix.** One symptom implies a category. Tabulate every
  reachable callee, its observable impact, and its status.
- **Scope-accuracy first (F35-ClaimDrift).** State plainly which user path is
  affected. If the default path is fine and only an opt-in flag is broken, that
  scope line must *lead* the finding — otherwise readers over-estimate the blast
  radius and the project over-reacts.

## Root cause

- **Shared fallthrough = shared blast radius.** A single "unknown callee →
  no-op" branch is hit by dozens of distinct runtime helpers (list, dict, set,
  tuple, input, fmt, iter, math, parse, str-methods, …). They all fail
  identically and invisibly.
- **Default vs opt-in path conflation.** The broken surface was gated behind an
  experimental opt-in flag; the default (shipped-wheel) path used a different,
  fully-working implementation. Without an explicit scope line, "the backend is
  broken" reads as "the product is broken."

## Why this is critical for Ballast / agent-driven projects

When an agent reports a bug, the cheapest-looking fix is the reported symptom.
But a stub fallthrough is a *category* defect: fixing stdout while leaving list /
dict / input / fmt as silent no-ops produces a release that is *still* broken,
now with a misleading "fixed" claim (F35-ClaimDrift). The catalogue table is the
artifact that converts "fix the symptom" into "close the category." And the
scope line is what keeps a correct-but-narrow finding from triggering a
disproportionate response.

## Empirical evidence (Cobrust 2026-05-22 → 25)

- After the F45 stdout fix shipped (wave-2), an independent audit enumerated the
  **remaining** stub surface as a **12-category table**: input/read_line, argv,
  list, dict, set/tuple, panic, fmt, iter, math, parse_int/str-parsing,
  str-methods, and the LLM-router surface — every one compiling under the opt-in
  flag but emitting no observable side effect, while the default backend handled
  all of them correctly at the same commit.
- The finding led with the scope line: **default path = Cranelift = full parity;
  shipped wheels do not enable the opt-in flag; an end-user on the standard
  install path never hits a stub.** This kept the P1 honest without inflating it.
- All 12 categories were closed across six sub-waves (ADR-0058g), each adding
  `category_*` fixtures that **link-and-run** and assert an observable exit-code /
  stdout signal — not merely object-emit.
- **Over-claim correction (cross-ref F53):** the 2026-05-25 "12/12 RESOLVED"
  status was later found to have closed the *runtime-helper* path for two
  categories (list, fmt) while the *aggregate-literal* codegen callsite for those
  same types still returned null — i.e. direct-helper-call fixtures passed but
  source-level `[1,2,3]` / `f"x={x}"` still no-op'd. The closure was claimed
  before the aggregate path had a fixture. F53 landed the missing implementations
  and the F45a §8 amendment recorded the correction (history-honest, per F35).

## Detection rule (CI gate)

1. **Catalogue-completeness gate.** Before claiming a subsystem "at parity," every
   category that routes through the shared dispatch MUST have ≥1 behavior-layer
   fixture that (a) emits via the path under test, (b) links against the real
   runtime, (c) runs the binary, (d) asserts `stdout == expected` / a specific
   exit code — never "non-empty artifact."
2. **Direct-call ≠ source-level.** A fixture that invokes a runtime helper
   directly does *not* prove the source-level construct that *should* call it
   works. Cover both the helper-call path **and** the source-literal path (this
   is the exact gap F53 exposed for list/fmt).
3. **Stub cross-ref contract** (inherited from F45): every stub comment carries a
   tracked back-reference; grep `Wave-N stub` for any line without one.
4. **Release-notes per-callee parity table**: columns = surface / reference-impl
   status / under-test-impl status. Prevents adjacent landings aggregating into
   an overstated "complete."

## Resolution path

1. **Enumerate** the full catalogue the moment one stub surface is found — table
   of (category, callees, observable impact, status).
2. **Lead with scope**: which user path is affected; is the default safe?
3. **Close per-category** with link-and-run fixtures covering *both* the
   helper-call and the source-literal path for each type.
4. **Keep claims behind fixtures**: do not flip a category to RESOLVED until its
   fixture exists and passes (the list/fmt over-claim is the cautionary tale).

## Related findings

| Finding | Relationship |
|---------|--------------|
| F45 — Stub silently shipped | Parent: F45a confirms the pattern is systemic across the full callee catalogue |
| F44 — CI cache stale-green | Sibling: object-emit green masks runtime silent failure (same structural "green ≠ working") |
| F46 — Wheel not installable | Sibling packaging-discipline: "right thing in wrong shape," docs claim coverage that doesn't match user reality |
| F53 — Default-flip aggregate gap | Child: the over-claim correction — direct-helper fixtures passed while the aggregate-literal path still no-op'd |
| F51 — Clippy feature-flag silent-rot | Sibling: the opt-in-flag code path is exactly where both the stubs and the unlinted clippy warnings lurk |
| F35 / F37 | Parents: scope-accuracy claim drift + silent rot on untracked stubs |
