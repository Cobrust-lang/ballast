---
catalogue_id: F62
title: "A rename/build-config change is a cold-build event — warm-build audits cannot vet it; clean-build cross-platform CI is the only authoritative oracle"
family: warm-build-audit blind spot + non-deterministic CI (resource-pressure sub-form)
severity: P2
status: ratified_2026-05-28
empirical_project: Cobrust ADR-0071 cobra-rebrand CI run (2026-05-28)
cobrust_local_id: F62 (f62-cobra-rebrand-ci-fragilities.md)
date_ratified: 2026-05-28
cobrust_sha: d355b8f
related: [F58, F60, F61, F59]
---

# F62 — Build-config change surfaces cold-build-only fragilities

## Pattern

A change that touches **build configuration** — a crate rename, a `[lib] name`
change, a workspace restructure, a toolchain bump — triggers behaviour that only
manifests on a **cold/clean build**. Two classes recur:

1. **Build-ordering fragility**: a clean build hits a dependency-resolution
   ordering that a warm build (with artifacts already present) never exercises
   (e.g. a merged-doctest harness trying to link an rlib before it's built).
2. **Resource-pressure fragility**: a cold full rebuild of a now-larger workspace
   pressures the CI runner's disk/memory, producing a truncated artifact that a
   warm incremental build (recompiling little) never provokes — surfacing on a
   heavy temp-I/O test (a size benchmark, a fixture-heavy suite).

Both are invisible to a **warm-build** local audit: the artifacts already exist,
the disk isn't pressured. They appear only on the clean-build CI, and often on
*both* platforms or *only* the resource-constrained one.

## Root cause

A warm local build reuses cached artifacts and recompiles minimally, so it
exercises neither the cold dependency-ordering path nor the full-rebuild resource
footprint. The audit signal "green on my machine" is structurally unable to
predict the clean-build CI outcome for a build-config change. The size-benchmark
sub-failure additionally violated deterministic-CI discipline (F59): a heavy
temp-I/O *benchmark* must not gate CI.

## Why this matters for Ballast

The recurring Ballast lesson across this whole arc (F58/F60/F61/F62): **a green
warm-build single-platform local/paired audit is necessary, but never sufficient,
for build-config / codegen / cross-platform changes — the clean-build CI on the
full platform matrix is the authoritative oracle.** An agent must not report a
rename/config change "verified" on the strength of a warm local audit; it must
wait for clean CI. This is the precise blind spot that let F60 and F61 slip their
mac-only audits, now generalized to the build-config class.

## Empirical evidence (Cobrust 2026-05-28)

The cobra-rebrand CI run failed on **both** platforms with two unrelated issues,
**neither** caught by the warm-build macOS paired audit:

- **ubuntu**: a lib doctest →
  `error: extern location for <crate> does not exist: target/debug/deps/lib<crate>.rlib`.
  Root cause: a bare `[lib] name` × the toolchain's *merged-doctests* harness ×
  a **clean** build — the merged-doctest binary tried to resolve the crate rlib
  before it was built, an ordering bug that only bites cold builds. The local
  audit passed only because a warm rlib already existed.
- **macOS**: a size benchmark →
  `Could not read file magic` (a truncated `.o`). Root cause: a **cold** full
  rebuild of a now-larger workspace pressured the runner's disk → a truncated
  artifact write. A correctness-irrelevant size *benchmark*, untouched by the
  rebrand.

**Resolutions:** (1) mark the doctest example fence `ignore` — note that
`[lib] doctest = false` was **not honored** under the merged-doctests harness, so
the per-fence marker was the reliable mechanism; the example stays as docs,
behaviour verified by the integration suite. (2) `#[ignore]` the size-benchmark
tests (opt-in via `--ignored`) — a heavy-temp-I/O benchmark must not gate CI
(F59-style determinism). **SHA:** `d355b8f`.

## Detection rule

> For any rename / `[lib] name` / workspace-restructure / toolchain change,
> require a **clean-build** CI pass on the **full platform matrix** before
> declaring it verified — a warm-build local/paired audit cannot vet cold-build
> ordering or full-rebuild resource pressure. And: no heavy temp-I/O **benchmark**
> may sit in the gating suite (F59).

CI candidate: a periodic `cargo clean` + cold-build job, so cold-build ordering
fragilities surface on a schedule rather than only on the next big config change.

## General Ballast mitigation

1. **Cold-build CI is authoritative for build-config changes.** Warm-build green
   is not a CI-readiness proxy here.
2. **Know your harness quirks.** A config knob (`doctest = false`) may be ignored
   by a newer harness mode; verify the knob actually takes effect, don't assume.
3. **Benchmarks are opt-in, never gates.** Especially resource-heavy ones, which
   double as non-deterministic-CI risks under runner pressure.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F58 / F60 / F61 (this batch) | Same warm-build / single-platform audit blind spot; F62 generalizes it to the build-config-change class |
| F59 (this batch) | The size-bench sub-failure is a direct deterministic-CI (non-gating-benchmark) instance |
| F1 — Declared rules without enforcement | Parent family: "vet config changes on cold CI" implicit; no gate |
