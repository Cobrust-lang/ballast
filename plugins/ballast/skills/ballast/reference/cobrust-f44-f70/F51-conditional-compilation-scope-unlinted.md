---
catalogue_id: F51
title: "Conditional-compilation scope unlinted — CI lints only the default feature set, so code behind opt-in feature flags accumulates lint/build rot invisibly"
family: F37-SilentRot (declared-coverage ≠ actual-coverage) + F44-sibling (gate-scope incomplete)
severity: P2 (feature-gated lint rot; surfaces only under a non-default invocation)
status: ratified_2026-05-25
empirical_project: Cobrust LLVM backend feature-gated tests (2026-05-25)
cobrust_local_id: F51 (f51-clippy-feature-flag-silent-rot.md)
cobrust_sha: 910279d (finding)
resolution: add a blocking lint job under the opt-in feature flag(s), not just default features
related: [F44, F45a, F50, F37-SilentRot]
---

# F51 — Conditional-compilation scope unlinted

## Pattern

CI runs its lint/build gate with the **default** feature set only. Code behind an
opt-in feature flag (`#[cfg(feature = "X")]`) — and the test files that exercise
that path — is **never compiled by the gate**, so lint warnings and build errors
inside it accumulate invisibly. They would fail CI under `-D warnings`, but CI
never sees them, because the flag is off by default.

This generalizes F44 from "CI cache stale-green" to "**CI scope incomplete ≠
all-clean**": both hide problems that surface only under a different invocation
condition (a busted cache for F44; an enabled feature flag for F51).

## Root cause

- **Gate scope ≠ code scope.** The lint job's feature selection does not cover the
  union of features any code path compiles under. Feature-gated regions are dark
  to the gate.
- **Opt-in flag perceived as "out of scope."** Because the feature is off by
  default and may be experimental, its code is implicitly treated as not subject
  to the same lint bar — but it still ships, and still rots.
- **F37-SilentRot**: warnings inside the dark region are accepted debt nobody can
  see, because the only invocation that reveals them is never run in CI.

## Why this is critical for Ballast / agent-driven projects

Agents trust the gate to define "clean." If the gate's feature scope is narrower
than the code's, every dispatch that touches feature-gated code gets a false
all-clean. The rot compounds: each sub-agent adds to the dark region, the next
trusts the green, and the warnings only surface when someone *manually* runs the
flagged invocation (often during the very sprint that's trying to enable the
feature — the worst time to discover a backlog). The fix is to make the gate's
feature matrix cover the code's feature matrix.

## Empirical evidence (Cobrust 2026-05-25)

A feature-gated test file (landed in an earlier sub-wave) accumulated 4 clippy
warnings — `items_after_statements` ×3, `similar_names` ×1 — visible only under
`cargo clippy -p <crate> --all-targets --features llvm`. CI ran default-feature
clippy only and reported clean throughout. The warnings were discovered by the
*next* sub-wave's author when they manually ran the flagged invocation. Immediate
mitigation was a module-level `#![allow(...)]` on the offending file (mirroring the
discovering author's same-day defensive pattern); the systemic fix — adding a
blocking `--features llvm` clippy job to CI — was deferred to its own sprint
(a CI-workflow change that must be validated across all flag-gated paths).

## Detection rule (CI gate)

Lint/build under the **opt-in feature flags**, not just defaults, as a blocking job:

```bash
cargo clippy --workspace --all-targets --features <opt-in-flag> -- -D warnings
# repeat per meaningful feature (and ideally --all-features) so no #[cfg]
# region is dark to the gate.
```

Audit question: "For every `#[cfg(feature = ...)]` region in the tree, is there a
CI invocation that compiles and lints it under `-D warnings`?" Any 'no' is a dark
region accruing silent rot.

## Resolution path

1. **Map gate scope to code scope**: enumerate every feature any code compiles
   under; ensure the lint matrix covers their union (or `--all-features`).
2. **Add a blocking lint job per opt-in flag** (its own CI-workflow sprint, since
   enabling it may surface a backlog that must first be cleared per F37/F44).
3. **Until the gate lands**, treat any feature-gated lint patch as honest debt
   with a tracked reference, not a silent `#![allow]`.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F44 — CI cache stale-green | Direct sibling: "green ≠ working" — F44 hides via cache invalidation, F51 hides via feature-flag scope; both reveal under a different invocation |
| F45a — Stub catalogue systemic | Parent context: the opt-in-flag code path is exactly where both the runtime stubs (F45a) and the unlinted warnings (F51) lurk |
| F50 — Parallel-surface divergence | Sibling: "different invocation reveals different gaps" |
| F37 — Silent-rot-on-accepted-debt | Parent: warnings in the dark region are accepted debt nobody can see |
