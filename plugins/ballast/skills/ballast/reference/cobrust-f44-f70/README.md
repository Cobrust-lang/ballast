---
batch_id: cobrust-f44-f70
title: "F44-F72: Cobrust empirical corroboration batch (CI-as-oracle hardening + stub/parity false-pass family + cross-target enablement + ecosystem-import chain + 11 methodology deltas)"
date: 2026-05-30
cobrust_baseline: v0.6.0 → v0.7.0 multi-agent run (main HEAD 936f13c at time of filing; 2026-05-22 → 2026-05-29) + the 2026-05-29/30 dynamic-Workflow session (F71 + Delta 8 close + Delta 9) + the 2026-05-30 ADR-0080/ADR-0081 FastAPI-real impl run (F72 + Deltas 10-11)
prior_batch: cobrust-f41-f43 (catalogue through F43; PR follow-up to F31-F40)
---

# Cobrust F44-F72 batch — README

Twenty-eight failure-mode findings (F44-F72, with F45a as a systemic-scope
sub-form; F52 and F57 deliberately skipped in Cobrust's local numbering), two
distilled cross-cutting **pattern** docs, and one **methodology-deltas** doc —
empirically forced by the Cobrust v0.6.0 → v0.7.0 multi-agent run
(2026-05-22 → 2026-05-29), the follow-on 2026-05-29/30 dynamic-Workflow
session (which added F71, closed Delta 8 experiment → default, and folded in
Delta 9), and the 2026-05-30 ADR-0080/ADR-0081 FastAPI-real impl run (which added
F72 and Deltas 10-11). This is a follow-up to the f41-f43 batch (catalogue through
F43) and the f31-f39 batch (F31-F40). (The dir name stays `cobrust-f44-f70` for
stable cross-references even though the batch now extends to F72.)

Each finding carries its Cobrust commit SHA(s) as a ground-truth anchor in the
frontmatter (`cobrust_sha`). The slot numbers here ARE the Cobrust local IDs
(unlike f31-f39, which re-mapped local IDs onto free upstream slots) — Cobrust's
own catalogue had already advanced past F43 by the time of this back-port, so the
numbering is shared 1:1.

## What's new in this batch (vs. f41-f43)

Three shapes, all first-class deliverables:

1. **28 findings (F44-F72)** — same Symptoms / Root-cause / Recovery / Evidence
   format as the catalogue, clustered into recurring families (below). F71 (wasm
   typed-call ABI fuzzer) was added by the follow-on 2026-05-29/30 session; F72
   (killed-runner CI flake) by the 2026-05-30 FastAPI-real impl run.
2. **2 pattern docs** — distilled, multi-finding playbooks that sit above the
   individual findings:
   - `cross-compile-target-enablement-pattern.md` (the F4-Cross-Target family
     playbook: where the seams + gotchas live in staged cross-compile enablement)
   - `ecosystem-import-chain-pattern.md` (the 5-layer ecosystem-import / FFI
     marshalling chain + ID-block allocation discipline)
3. **1 methodology-deltas doc** — `methodology-deltas.md` — 11 refinements to
   **Ballast's own** topology / dispatch / audit discipline (NOT failure modes; these
   say "change how we *run* the process", not "the system did X wrong"). Delta 8
   (dynamic-Workflow orchestration) closed experiment → default and Delta 9 (the
   Elegance Law) was added in the follow-on session; Delta 10 (mutation-prove a
   tripwire) and Delta 11 (slice an ADR-phase to the smallest independently-gated
   increment) came from the 2026-05-30 FastAPI-real impl run. The six reusable
   orchestration patterns are in `reference/workflow-orchestration-patterns.md`
   (sibling, one level up).

## Finding families (clustering)

The 28 findings group into five recurring families plus a methodology track:

| Family | Findings | One-line shape |
|--------|----------|----------------|
| **F37-SilentRot** (declared-coverage ≠ actual-coverage) | F44, F45, F45a, F50, F51, F53 | a gate/badge declares coverage the run didn't actually achieve |
| **F35-ClaimDrift** (claim ≠ artifact/diff) | F45, F45a, F46, F48, F50, F53 | the stated scope/version/parity outruns the real artifact |
| **F1-Sediment** (declared-rule ≠ enforced pre-flight) | F46, F49, F54, F55, F65, F69 | a discipline exists as prose; the pre-flight that would enforce it is absent |
| **F-Codegen / parallel-impl drift** | F47, F50, F56, F60 | type-conditional or twin-backend code silently emits wrong output |
| **F4-Cross-Target / non-deterministic-CI** | F58, F59, F61, F62, F63, F66, F70, F71, F72 | a host-target / external-service / cold-build / ABI / infra-flake assumption breaks the gate |
| **Methodology deltas** (process refinements) | Deltas 1-11 | how Ballast dispatches + audits, not what a system did wrong |

(Findings appear in more than one family where the root cause is compound — the
frontmatter `family:` field is authoritative per file.)

## Slot mapping (slot = Cobrust local ID, 1:1)

| Slot | Title (short) | Cobrust SHA anchor | Status |
|------|---------------|--------------------|--------|
| **F44** | CI cache stale-green / false-pass | `41fbef3` (lurk a3a636c→e38dfe4) | ratified 2026-05-27 |
| **F45** | Backend stub silently shipped | `c8ba2bd`→`1adf3af` | ratified 2026-05-22 |
| **F45a** | Stub-catalogue systemic scope | `cb8893c` (ADR-0058g) | ratified 2026-05-22 |
| **F46** | Package not installable on a fresh environment | `c55f859`→v0.6.0 (ADR-0069) | ratified 2026-05-22 |
| **F47** | Type-conditional codegen emits empty/wrong output | `cf0864c`, `dcb1714` | ratified 2026-05-25 |
| **F48** | Version-bump must be accompanied by a tag | `e23d66c` | ratified 2026-05-22 |
| **F49** | Fresh-workspace identity fallback leak | `6491614` (leak cbc1e0e→cd2fe04) | ratified 2026-05-22 |
| **F50** | Parallel-surface divergence from duplicated tables | `07159ce` | ratified 2026-05-22 |
| **F51** | Conditional-compilation scope unlinted | `910279d` | ratified 2026-05-25 |
| **F53** | Default-flip blocked by curated-sweep blind spot | `4aa38da`→same-day | resolved 2026-05-26 |
| **F54** | Derived sub-payload escapes companion prepass | `66057a4`, `9aec0fc` | ratified 2026-05-26 |
| **F55** | Feature-gated test depends on another crate's runtime shim | `9b3b265`, `81cfc1f` | ratified 2026-05-27 |
| **F56** | Correctness fix in one of two parallel backends only | `b5b7318` | ratified 2026-05-27 |
| **F58** | Magic string passed verbatim, platform-divergent | `d276076` | ratified 2026-05-27 |
| **F59** | External-service dependency gates CI | `8b810e7` | ratified 2026-05-27 |
| **F60** | Removing an impl breaks hardcoded refs + reveals survivor gap | `27562c5` | ratified 2026-05-27 |
| **F61** | Negative-test probe used platform-divergent input | `27562c5` | ratified 2026-05-27 |
| **F62** | Build-config change surfaces cold-build-only fragilities | `d355b8f` | ratified 2026-05-28 |
| **F63** | Unbounded test-artifact accumulation in host-specific tempdir | `4089cd8`, `1b05ae3` | ratified 2026-05-28 |
| **F64** | Lockfile staging is part of the atomic commit | `1b05ae3`→`73aa3bb` | ratified 2026-05-28 |
| **F65** | Committed example without a paired smoke test is unverified | `a6ee367`→`447c22e` | ratified 2026-05-29 |
| **F66** | Cross-target seam lives at the toolchain-API boundary | `57ebc7e` | ratified |
| **F67** | All fix candidates clean ⇒ suspect the fixture | `d29470f` | ratified |
| **F68** | Ship the load-bearing chain, defer the surface sugar | `971d4ce` | ratified |
| **F69** | Constitutional-principle debt erodes at every call site | `936f13c` | **open** |
| **F70** | Default feature trio incompatible with a new target | `446016c` | **candidate** |
| **F71** | wasm is a free ABI-correctness fuzzer (typed-call extern audit) | 2026-05-29/30 session | **candidate** |
| **F72** | killed-runner CI flake — blank step + empty log ≠ code bug | `a1c9d83` (2026-05-30 run) | **candidate** |

> **F52 and F57 are intentional gaps** in Cobrust's local numbering (no finding
> was filed under those IDs). They are not missing clusters — no entry in this
> batch references them, so there are no dangling cross-refs.

## Finding summaries

### CI-as-authoritative-oracle hardening (F44, F51, F59, F62 + Delta 6)

- **F44 — CI cache stale-green / false-pass.** A cache hit keys on coarse inputs
  (SHA + lockfile hash) and skips clippy/rebuild recomputation, so a green badge
  stops meaning "workspace clean". Lints lurked across the `a3a636c→e38dfe4`
  window. Resolution: clean-target sweep at every phase-close + cargo-udeps gate +
  consistent `--all-targets --no-deps`. **Parent of methodology Deltas 6 and 7.**
- **F51 — Conditional-compilation scope unlinted.** CI lints only the default
  feature set; code behind opt-in flags accrues rot invisibly. Add a blocking lint
  job under the opt-in feature(s).
- **F59 — External-service dependency gates CI.** A live-HTTP test makes a third
  party's health, not the code, decide green/red. `#[ignore]` + opt-in.
- **F62 — Build-config change surfaces cold-build-only fragilities.** A
  rename/config change is a cold-build event; warm-build audits can't vet it.
  Clean-build cross-platform CI is the only authoritative oracle.

### Stub / parity false-pass family (F45, F45a, F47, F50, F53, F56)

- **F45 — Backend stub silently shipped.** A "Wave-N stub" fallthrough compiles +
  links but no-ops at runtime; "feature-complete" cascades over it. Resolution:
  stdout-diff differential gate + "a stub must cross-reference tracked debt".
- **F45a — Stub-catalogue systemic scope.** When one stub surface is found, the
  same fallthrough usually spans the whole subsystem; enumerate every reachable
  callee and lead docs with the exact user-path scope. (Amended by F53 after an
  over-claim correction.)
- **F47 — Type-conditional codegen emits empty/wrong output.** A default-typed
  temporary (`None`/`0`) routes a value down the wrong formatting arm — silent
  wrong output, no crash. Propagate the callee's declared return type to the
  synthetic return local.
- **F50 — Parallel-surface divergence from duplicated tables.** Two surfaces that
  must agree (LSP + CLI diagnostics) are built from independent copies of one
  table; one ships correct, the other diverges under a parity claim. Single
  source-of-truth + parity smoke + full-corpus sweep.
- **F53 — Default-flip curated-sweep blind spot.** A "stability" sweep declared a
  backend production-ready by running a curated corpus that excluded the
  integration paths the default flip would traverse (30+ silent regressions
  averted). Never flip a default without GREEN on every reachable path.
- **F56 — Correctness fix in only one of two parallel backends.** The unfixed twin
  produces silent garbage until it becomes default. Port correctness fixes to every
  parallel implementation in the same commit.

### Packaging / release discipline (F46, F48, F64, F65)

- **F46 — Package not installable on a fresh environment.** Build-host paths +
  unbundled runtime assets bake into the artifact: works on the build machine, 100%
  broken on a clean one. `current_exe()`-rooted asset lookup + bundle runtime/stdlib
  + post-package extract-and-run smoke gate.
- **F48 — Version-bump must be accompanied by a tag.** Bumping the version string
  without tagging creates a binary whose announced version has no matching artifact.
- **F64 — Lockfile staging is part of the atomic commit.** A dependency edit
  regenerates the lockfile; staging only the manifest makes locked-CI reject the
  drift and fan-out-fail every build job. **Parent of methodology Delta 4.**
- **F65 — Committed example without a paired smoke test is unverified.** A flagship
  demo committed with no end-to-end smoke test didn't even compile, hiding a stack
  of layered gaps because nothing ran it.

### Identity / opsec (F49)

- **F49 — Fresh-workspace identity fallback leak.** A new clone with no local git
  identity falls back to OS account + device hostname, leaking a real name into
  permanent public commit metadata. Neutral global identity (defense-in-depth) +
  per-dispatch identity pre-flight + audit scope follows the actual mutation
  surface. (Sibling of f41-f43's F42.) **Forces methodology Delta 1's audit
  carve-out reasoning.**

### Cross-target enablement + non-deterministic-input (F54, F55, F58, F60, F61, F63, F66, F67, F70, F71, F72)

- **F54** — a transform pass emits a derived sub-payload a companion prepass never
  registered → table-lookup panic on the synthesized form.
- **F55** — a feature-gated integration test links a bare artifact depending on a
  runtime shim in another crate; latent until the feature becomes default.
- **F58** — a "magic" config string (`"native"`) passed verbatim to an API that
  never interprets it: benign on one platform, hard-aborts on another.
- **F60** — deleting one implementation breaks tooling hardcoded to its path AND
  reveals the survivor never carried a declaration the deleted one had.
- **F61** — a negative/error-path test used a real-but-environment-dependent input;
  the "guaranteed-to-fail" case actually succeeds on some platforms.
- **F63** — tests create temp dirs without RAII cleanup; artifacts accumulate
  unbounded in a host-specific temp root the cleanup SOP never named.
- **F66** — cross-target enablement seams live at the toolchain-API boundary, not
  where the source-level config suggests. (Reconstructed from commit `57ebc7e`.)
- **F67** — when every plausible fix candidate verifies clean, suspect the test
  fixture, not the system under test. (Reconstructed from commit `d29470f`.)
- **F70** — a library's DEFAULT feature set is an implicit host-target assumption
  that breaks on the first constrained cross-target. (**candidate**.)
- **F71** — wasm is a free ABI-correctness fuzzer: a codegen extern declared with a
  sloppy signature (length arg hard-coded `i64` where the runtime used `usize` =
  `i32`-on-wasm32) is invisible on permissive native ELF linkers but TRAPS on
  wasm32's strict typed-call check. Cross-compiling to a strict-typed target audits
  the whole `__cobrust_*` extern table for ABI correctness for free; add a wasm
  cross-smoke that exercises the extern surface. (**candidate**.)
- **F72** — a killed-runner CI flake (OOM / timeout / infra reap) looks like a code
  failure but isn't: its signature is a **blank step conclusion + an empty
  `--log-failed`** (a killed runner never flushes step logs). Distinct from F64,
  whose lockfile mismatch gives the step a `failure` conclusion + a logged error.
  Diagnosis: reproduce the exact command locally (`cargo build --workspace
  --all-targets --locked` — `--locked` also rules out a lockfile bug) + `gh run rerun
  <id> --failed`; both green ⇒ environmental, don't touch code. Evidence `a1c9d83`
  (blank ubuntu build step; transient OOM on the memory-heavy `--all-targets` step).
  (**candidate**.)

### Scope / increment-boundary + design-principle debt (F68, F69)

- **F68 — Ship the load-bearing chain, defer the surface sugar.** Land the
  end-to-end functional chain first; defer ergonomic surface sugar — and predict
  the deferred work's blast radius. (Pairs with `ecosystem-import-chain-pattern.md`.)
- **F69 — Constitutional-principle debt erodes at every new call site.** A "we'll
  honor it later" design north star (here CLAUDE.md §2.5 LLM-first: explicit-borrow
  shortcut + error-UX-prints-the-fix) silently erodes at every new call site that
  doesn't honor it. **Status: open** — a forward-looking catalogue entry not yet
  filed in the Cobrust repo. (Sibling of f41-f43's F41 source-surface leakage.)

## Pattern docs

- **`cross-compile-target-enablement-pattern.md`** — the F4-Cross-Target playbook.
  Cross-compile enablement is a *staged pipeline of seams* (build.rs `--target`
  plumbing → codegen target init → cross-cc/sysroot → CI cross-smoke → qemu/wasmtime
  LIVE); failures cluster at the boundary between your toolchain and the vendored
  one and surface only under a live cross-run. Distilled from F66, F67, F70, F71,
  F58, F60, F61. Evidence: `57ebc7e`, `d29470f`, `446016c`. (F71 — the wasm
  typed-call ABI dividend of stage 5's live cross-run — is the newest sibling.)
- **`ecosystem-import-chain-pattern.md`** — the 5-layer ecosystem-import / FFI
  marshalling chain + ID-block allocation discipline (chain-generality sub-form of
  F2-Scope). Distilled from F68 + F41. Evidence: `aeb3f5a`, `caa0510`, `971d4ce`,
  `8c11e16`.

## Methodology deltas (`methodology-deltas.md`)

Eleven refinements to Ballast's own dispatch/audit discipline — research-product
co-evolution, not failure modes (Deltas 1-7 + Delta 8's first run from the v0.7.0
run; Delta 8's session-wide close and Delta 9 from the 2026-05-29/30 session;
Deltas 10-11 from the 2026-05-30 ADR-0080/ADR-0081 FastAPI-real impl run):

1. **All-top-tier sub-agents** — author *and* audit use the top model; the tier
   matrix is retired (forced by a mid-tier correlated-regression cluster).
2. **Dispatcher-as-context-custodian** — offload raw work by an explicit threshold
   table; the lead keeps only the compression-fragile strategic tier.
3. **Mandatory independent post-author audit** — pre-merge, read-only, different
   agent; Tier-1 (this commit) + Tier-2 (periodic project-wide sweep).
4. **Dependency-manifest staging is part of the atomic commit** — the F64
   generalization, demanded explicitly in the dispatch prompt.
5. **Chain-generality claims verified against the diff** — the F35-sibling guard
   promoted from reactive finding to a routine integration step.
6. **Deterministic-CI / CI-infra-hardening playbook** — concrete hardening for the
   single authoritative gate (disk reclaim, concurrency cancel, FS-visibility
   retry, SHA-pinned actions/toolchains, ignore external/disk-heavy tests).
7. **Honest-signal discipline** — fix true-positive signals by *removal*, never
   mask (the F44 stale-green failure mode in reverse).
8. **Dynamic-Workflow orchestration (meta) — experiment → default.** The
   deterministic fan-out → synthesis → impl → audit script mode. The follow-on
   2026-05-29/30 session ran the dispatch loop almost entirely as dynamic Workflows
   (**~11 workflows**; the last several **fully autonomous** — `GO`, push + CI, zero
   lead finishing), promoting it from experiment arm to the **default dev mode**.
   The audit gate caught real issues (a socket-truncated impl → `BLOCK`; a dogfood
   overclaim → `GO_WITH_FINDINGS`; a latent false-green dotted-attr bug → TEST-stage
   catch), and a self-improvement chain folded each run's failure into the next run's
   guard (`robust()` retry-wrap → honest-framing guards → the Elegance Law). The six
   reusable patterns: `reference/workflow-orchestration-patterns.md`.
9. **The Elegance Law.** When wrapping a Rust crate or designing an ecosystem/backend
   surface, the `.cb` surface is a **clean re-design that drops the accumulated
   footguns** of Flask/FastAPI/Express/pydantic — NOT a mechanical clone. Extends
   "Drop from Python" (CLAUDE.md §2.2) from the language core to the ecosystem
   surface: compile-time-typed validation over runtime-asserted, explicit deps over
   decorator/DI magic, `Result` over exceptions-as-control-flow, typed routes/bodies
   over stringly-typed, typed composable config over option-bag sprawl. Each
   ecosystem ADR carries a **footgun-ledger**; each backend/ecosystem workflow's
   audit scores **`elegant + no-legacy-debt`**.
10. **Mutation-prove a tripwire before relying on it.** A negative / regression-
   tripwire test can be **green for the wrong reason** — passing whether or not the
   bug it guards against is present. The audit mutates the guarded code into its
   buggy form and confirms the test goes RED, then reverts; a tripwire's protective
   value is unproven until a mutation makes it fail. (Empirical: ADR-0081 Phase-1b's
   runtime "no-UB" test passed 3/3 even under a mutated type-only `body.field` gate —
   null-pointer + null-guard masked the crash; the `nm`-based no-accessor-symbol
   tripwire was mutation-proven instead.) Sharpens F36/F37 with the *technique*; a
   one-line Tier-1 audit-checklist item (Delta 3). Cross-ref F36, F37, F61.
11. **An ADR "phase" is a starting unit, not an atomic dispatch unit.** Slice a
   high-blast-radius type-system / object-model phase recursively until each
   increment is independently testable (compile-time `well_typed`/`ill_typed` corpus
   or runtime E2E), independently gated (full regression + CI), and ordered to unblock
   the next — each shipping as its own audited, CI-green commit. A TEST agent that
   discovers a hidden prerequisite spins it into its own increment rather than bloating
   a sibling. (Empirical: ADR-0080 Phase-1 → 1a/1b-i/1b-ii/1b-iii; ADR-0081 Phase-1 →
   1a/1b; the Alias-vs-`Adt` non-unification found by 1a's TEST agent became its own
   1b-i.) Composes with Delta 2 + Delta 3.

## Frontmatter-schema note (honest divergence)

Two frontmatter conventions coexist in this batch, by author cohort:

- **F44-F65** use `catalogue_id:` + `family:` + `cobrust_local_id:` + `cobrust_sha:`.
- **F66-F72** use `doc_kind: finding` + `finding_id:` + `family:` + `cobrust_sha:`.
- **Pattern docs** use `doc_kind: pattern` + `pattern_id:` + `evidence_shas:`.
- **methodology-deltas.md** uses `doc_kind: methodology-deltas` + `batch_id:`.

All four schemas carry a stable ID, a family/era tag, and SHA evidence, so
cross-referencing is unambiguous. A future normalization pass could unify the
`catalogue_id` / `finding_id` keys; it is recorded here rather than papered over.

## Files in this batch

```
cobrust-f44-f70/
  README.md                                              (this file)
  F44-ci-cache-stale-green-false-pass.md
  F45-backend-stub-silently-shipped.md
  F45a-stub-catalogue-systemic-scope.md
  F46-package-not-installable-fresh-environment-gap.md
  F47-type-conditional-codegen-empty-output.md
  F48-version-bump-must-tag-discipline.md
  F49-fresh-workspace-identity-fallback-leak.md
  F50-parallel-surface-divergence-from-duplicated-tables.md
  F51-conditional-compilation-scope-unlinted.md
  F53-default-flip-curated-sweep-omits-paths.md
  F54-stripped-subpayload-intern-prepass-gap.md
  F55-feature-gated-test-depends-on-other-crate-runtime-shim.md
  F56-parallel-backend-correctness-fix-drift.md
  F58-magic-string-passed-verbatim-platform-divergent.md
  F59-external-service-dependency-gates-ci.md
  F60-removing-impl-breaks-hardcoded-refs-and-reveals-survivor-gap.md
  F61-negative-test-probe-platform-divergent-input.md
  F62-config-change-surfaces-coldbuild-only-fragilities.md
  F63-test-artifact-accumulation-host-specific-tempdir.md
  F64-lockfile-staging-part-of-atomic-commit.md
  F65-committed-example-without-paired-smoke-test-is-unverified.md
  F66-cross-target-seam-at-toolchain-api-boundary.md
  F67-when-all-fix-candidates-come-back-clean-suspect-the-fixture.md
  F68-ship-the-load-bearing-chain-defer-the-surface-sugar.md
  F69-design-principle-debt-explicit-borrow-and-bypassed-error-ux.md
  F70-default-feature-trio-incompatible-with-new-target.md
  F71-wasm-typed-call-abi-fuzzer.md                      (2026-05-29/30 session)
  F72-killed-runner-ci-flake-blank-step-empty-log.md     (2026-05-30 FastAPI-real run)
  cross-compile-target-enablement-pattern.md
  ecosystem-import-chain-pattern.md
  methodology-deltas.md                                  (Deltas 1-11; Delta 8 closed, Deltas 9-11 added)

reference/  (one level up — sibling, referenced by Delta 8)
  workflow-orchestration-patterns.md                     (the six dynamic-Workflow patterns)
```

(F52 and F57 intentionally absent — gaps in Cobrust's local numbering.)

## Relationship to prior batches

- **cobrust-f31-f39** (F31-F40) and **cobrust-f41-f43** (F41-F43) are independent
  predecessors. This batch can merge before or after either.
- Several entries explicitly cite earlier-batch siblings: F49↔F42 (opsec/identity),
  F69↔F41 (source-surface / principle erosion), and the methodology deltas build
  directly on F43 (CI-as-oracle → Delta 6), F44 (stale-green → Deltas 6 + 7), and
  F64 (lockfile staging → Delta 4).
- This is a **separate methodology repo**; the human reviewer pushes. No push is
  performed by this integration.
