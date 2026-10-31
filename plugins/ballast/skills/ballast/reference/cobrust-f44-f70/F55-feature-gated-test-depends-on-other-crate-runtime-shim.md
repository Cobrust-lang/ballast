---
catalogue_id: F55
title: "Feature-gated integration test links a bare artifact that depends on a runtime shim living in another crate — latent until the feature becomes default"
family: F1-Sediment (cross-crate runtime-dependency gap) + detection-gate cascade
severity: P2
status: ratified_2026-05-27
empirical_project: Cobrust ADR-0070 §X.3 LLVM-default flip (2026-05-27)
cobrust_local_id: F55 (TWO source files — f55-dwarf-lldb-linked-harness-no-main-shim.md + f55-linked-exe-smoke-no-main-shim-llvm-flip.md; folded here)
date_ratified: 2026-05-27
cobrust_sha: 9b3b265 (X.3 ratified frontmatter), 81cfc1f (CI LLVM-18 install note)
related: [F54, F56, F60, F37]
---

# F55 — Feature-gated test links an artifact whose runtime shim lives elsewhere

## Cataloguing note (a minor lesson in itself)

This finding was filed **twice** under the same Cobrust local id (`f55-*`, two
separate files) — once framed as the DWARF/lldb harness gap, once as the
linked-exe / no-main-shim gap. They describe the **same** root cause. The
duplication is itself a small Ballast lesson: when two agents (or one agent across
two sessions) file under the same id without checking the existing finding,
the catalogue accretes near-duplicate entries. **Mitigation:** a finding-id
allocation check (grep the findings dir for the next id before writing) belongs
in the dispatch template, same family as F64's lockfile-staging check.

## Pattern

A test is gated behind an opt-in feature flag (or an environment probe) and is
therefore **never executed in the default CI configuration**. The test links a
**bare artifact** produced by crate A, but a symbol that artifact needs (an
entry-point shim, a runtime stub) is provided only by crate B's build path —
unreachable from crate A's integration tests. So the test cannot actually link;
it is broken from birth, but invisible because nothing runs it.

Two masking layers commonly stack:

1. **Feature off by default** → the test file compiles to *zero tests* in CI.
2. **Environment tool absent** (a debugger, a linker variant) → even when the
   feature is on, an early-return probe skips the test on dev machines.

Remove both masks at once — typically by flipping the feature to default in CI
*and* installing the missing tool in the same CI change — and the latent link
failure fires for the first time, often on every platform simultaneously.

## Root cause

The test harness in crate A assumes a complete link environment that only crate
B (the CLI / top-level binary) actually assembles. The shim (e.g. the platform
`main(argc, argv)` C entry that calls into the user body) lives with the
consumer, not the producer. A lower-crate integration test that links a bare
object has no path to that shim → `undefined reference to main` /
`ld returned 1 exit status`.

The deeper issue is **test-scope vs runtime-scope mismatch**: the test exercises
a round-trip (compile → link → run) that is only well-defined at the top of the
crate graph, but it was placed in a leaf crate where the round-trip cannot
complete.

## Why this matters for Ballast

This is the canonical **detection-gate cascade** member (with F54/F56/F58/F60/F61):
a single config change (default-flip + tool install) exposes a fleet of paths
that the previous default never exercised. The flip is the gate *working as
intended* — surfacing latent debt at CI time rather than in production. The
agent's correct response is not "the flip broke things" but "the flip revealed
pre-existing gaps; triage each."

Per honest-debt discipline (F37): a test that cannot pass in the env it's placed
in must carry an explicit `#[ignore = "reason; deferred to <path>"]` citing the
finding — never silently rot or get deleted (which loses the intent record).

## Empirical evidence (Cobrust 2026-05-27)

Three `dwarf_lldb_smoke` tests
(`lldb_linked_str_frame_variable`, `lldb_linked_option_none`,
`lldb_linked_option_some_int`) in `crates/cobrust-codegen/tests/` linked a bare
codegen object to spawn a debugger against it. The platform `main` shim
(`cobrust-cli/runtime/cobrust_main.c`) is unreachable from a `cobrust-codegen`
integration test:

```
/usr/bin/ld: Scrt1.o: in function `_start': undefined reference to `main'
collect2: error: ld returned 1 exit status
```

Latent since the DWARF feature landed (Phase L wave-3). Masked by: (1) the `llvm`
feature was off by default, so the whole file compiled to 0 tests on CI; (2) the
debugger (`lldb-18`) was absent on dev hosts, so the tests skipped locally. The
§X.3 flip turned `llvm` on in CI *and* the CI LLVM-18 apt/brew package shipped
the debugger — both masks gone at once → link failure on both ubuntu and macOS.

**Resolution:** `#[ignore]` the 3 linked tests with a full-rationale reason
string citing this finding; object-level DWARF coverage is retained by sibling
non-linked tests that inspect the emitted object directly. The linked round-trip
is deferred to the CLI integration path that already wires the shim.

**SHAs:** `9b3b265` (X.3 ratified frontmatter), `81cfc1f` (CI LLVM-18 install note).

## Detection rule

> Every feature-gated integration test that **links an executable** must either
> (a) link through the same runtime-shim path the top-level binary uses, or
> (b) carry `#[ignore]` with a finding citation if it needs an environment the
> default CI lacks. Audit *all* feature-gated test files when flipping the
> feature to default — each is a blind spot until the flip.

## General Ballast mitigation

1. **Place round-trip tests at the crate that owns the full link/runtime env.**
   A leaf crate cannot test a link that requires a top-of-graph shim.
2. **Audit every `#[cfg(feature = "X")]` test file before flipping X to default.**
   The flip is a known cascade trigger; pre-flip review is cheaper than post-flip
   CI red.
3. **Honest-debt the unpassable tests** with `#[ignore = "...; deferred to <home>"]`
   — keep the intent, lose the false-green.
4. **Add a finding-id allocation check** to the dispatch template to avoid the
   duplicate-id accretion this finding itself exhibited.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F54 / F56 / F58 / F60 / F61 (this batch) | Same detection-gate cascade exposed by the §X.3/§X.4 flip + removal |
| F37 (Cobrust) — silent-rot-on-accepted-debt | Resolution discipline: unpassable test must cite an `#[ignore]` reason |
| F1 — Declared rules without enforcement | Parent family: "test where the env supports it" is implicit; no gate at authorship |
