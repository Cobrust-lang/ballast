---
catalogue_id: F50
title: "Parallel-surface divergence — two surfaces that must agree are built from independent copies of the same table, so one ships correct and the other diverges under a 'parity' claim"
family: F37-SilentRot (declared-coverage ≠ actual-coverage) + F35-ClaimDrift
severity: P1 (one surface materially wrong while release claims parity)
status: ratified_2026-05-22
empirical_project: Cobrust v0.6.0 LSP/CLI diagnostics (2026-05-22)
cobrust_local_id: F50 (f50-lsp-cli-diagnostic-divergence.md)
cobrust_sha: 07159ce (finding) ; resolution = shared PRELUDE module + parity smoke + corpus sweep
resolution: single source-of-truth for the shared input + smoke fixture + full-corpus parity sweep
related: [F47, F44, F45a, F35-ClaimDrift, F37-SilentRot]
---

# F50 — Parallel-surface divergence from duplicated source-of-truth

## Pattern

Two user-facing surfaces are supposed to behave identically on the same input
(here: a CLI checker and an editor language-server, both reporting diagnostics).
Each surface is wired through its **own independent copy** of a shared
prerequisite (a name table, a preprocessing step, a config). One surface includes
the prerequisite and is correct; the other omits it and diverges — emitting false
errors on inputs the first surface accepts. The release nonetheless claims the two
surfaces are at parity, because the claim was made per-surface, not differentially.

## Root cause

- **No single source of truth.** The shared prerequisite is duplicated, not
  imported. One consumer applies it (prepends a synthetic prelude before parsing);
  the other calls the parser directly without it, so every name the prelude
  declares surfaces as "unknown."
- **A correct-but-unwired table existed.** The diverging surface even had its own
  *correct* name table — but scoped to a different feature (autocomplete) and
  never reaching the diagnostic path. Two surfaces, two tables, one wired, one not.
- **F35-ClaimDrift**: the release advertised "full parity" based on the surfaces
  existing, not on a test proving identical output on a shared corpus.

## Why this is critical for Ballast / agent-driven projects

When two surfaces are built by different dispatches (or different sprints), each
agent legitimately wires *its* surface and tests *its* surface. Neither owns the
*equivalence*. The shared prerequisite gets re-implemented on each side and drifts.
The only defense is structural — a single source of truth both surfaces import —
plus a *differential* gate that runs identical input through both and asserts
identical output. "Both surfaces work" is not "both surfaces agree."

## Empirical evidence (Cobrust v0.6.0, 2026-05-22)

The CLI checker prepended a synthetic PRELUDE (declaring `print`, `range`,
`parse_int`, list/str/math/IO/argv/input intrinsics) before parsing; it reported
`ok` (exit 0) on every example. The language-server's diagnostic path called the
parser **without** the prelude, so every PRELUDE intrinsic resolved as an unknown
name. A full-corpus sweep quantified it:

| Phase | `.cb` files | LS-diagnostic-emitting | Top misclassified |
|---|---|---|---|
| Pre-fix | 144 | 144 (100%) | `print`, `range`, `parse_int`, `input`, `list_get/set` |
| Post-fix | 144 | 0 (0%) | — |

Every `print(...)` in every file rendered as a red squiggle in the editor while
the CLI said `ok`. The completion-side name table was already correct but never
fed the diagnostic path. Resolution: move the PRELUDE (plus compile-time-computed
length constants so coordinates can never drift) into a **shared module** both
consumers import; wire the LS path to prepend it and shift diagnostic
coordinates back into user space; add a 5-fixture parity smoke test (runs every
build) + a full-corpus parity sweep (`#[ignore]`'d, on-demand).

## Detection rule (CI gate)

1. **Differential parity fixture.** For any two surfaces claimed to agree, a test
   feeds identical input to both and asserts identical output (here: a curated
   5-fixture set, run on every build; plus an `#[ignore]`'d full-corpus sweep).
2. **Single source of truth for shared inputs.** The shared prerequisite (prelude,
   name table, preprocessing) lives in one module both surfaces import — never two
   copies. Compile-time-derive any dependent constants so they cannot drift from
   the literal.
3. **Parity claims require a differential test.** A release claiming "surface A and
   B at parity" must point at the differential fixture that proves it; per-surface
   green is insufficient.

## Resolution path

1. **Unify the source of truth**: extract the duplicated table/step into one
   shared module; both surfaces import it.
2. **Add a differential parity gate**: identical input → both surfaces → assert
   equal output, on every build; full-corpus sweep on demand.
3. **Audit for sibling duplications**: wherever a value table is referenced by >1
   surface, check for a second copy that can drift.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F47 — Type-conditional codegen empty output | Same-family (codegen/frontend), same reporting window: a value/type table one surface trusts and another lacks |
| F45a — Stub catalogue systemic | Sibling: "the claim said parity; the reality diverged per item" — F45a per-callee, F50 per-surface |
| F44 — CI cache stale-green | Sibling: "green ≠ working" — here per-surface green ≠ surfaces-agree |
| F35 — Commit-msg vs diff drift | Parent: release claimed parity the landed code did not provide |
| F37 — Silent-rot-on-accepted-debt | Parent: the divergence persisted unflagged because no gate compared the two surfaces |
