---
catalogue_id: F58
title: "A 'magic' config string is passed verbatim to a library that never interprets it — benign on one platform, hard-aborts on another"
family: false-abstraction (front-end convention assumed of a back-end API) + platform-divergent test
severity: P2 (user-facing on the affected platform; CI-aborting)
status: ratified_2026-05-27
empirical_project: Cobrust ADR-0070 §X.3 LLVM-default follow-up (2026-05-27)
cobrust_local_id: F58 (f58-llvm-target-cpu-native-not-resolved.md)
date_ratified: 2026-05-27
cobrust_sha: d276076
related: [F56, F59, F60, F61]
---

# F58 — "native" passed verbatim to an API that doesn't resolve it

## Pattern

A configuration value carries a **convention that a front-end tool resolves**,
but the code passes it **verbatim to a lower-level library API that does not**.
The string looks like it works because the library tolerates the unknown value
by falling back to *something* — and on the platform the author tested, that
fallback happens to be benign. On another platform the same fallback is
catastrophic (loses a capability, hard-aborts the process).

The trap: a value like `"native"`, `"auto"`, `"default"`, `"latest"` *reads* as
self-documenting and the author assumes the API interprets it. The API actually
treats it as an opaque unknown.

## Root cause

Two layers:

- **False abstraction / convention leakage**: `"native"` (auto-detect host CPU)
  is a convention that *driver tools* (clang/llc, package managers, etc.)
  implement by calling a host-detection helper *themselves* before invoking the
  library. The raw library API has no such logic. The author's doc comment even
  *claimed* the API auto-detected — claim-vs-landed-behaviour drift (F35-family):
  the comment described intended behaviour the code never implemented.
- **Platform-divergent benign fallback**: the unknown-value fallback degraded
  gracefully on one host (a 64-bit-capable generic subtarget on Apple silicon)
  and fatally on another (lost 64-bit mode on the x86_64 CI runner → hard abort).
  The author's single-platform test could not see the divergence.

## Why this matters for Ballast

This couples two Ballast failure threads:

1. **Resolve conventions yourself at the boundary.** If your config accepts a
   value whose meaning is "ask the environment," you must *call the resolution
   helper* — never assume a downstream library does it. Self-documenting strings
   are the most likely to hide this gap precisely because they read as obviously
   correct.
2. **A single-platform pass is necessary, not sufficient.** The benign fallback
   on the author's machine is a false-green; the cross-platform CI run is the
   authoritative oracle (see F60/F61/F62 — the same single-platform-audit blind
   spot recurs across the whole §X.3/§X.4 arc).

## Empirical evidence (Cobrust 2026-05-27)

`build_target_machine` passed the Tier-2 `target_cpu` field verbatim:

```rust
let cpu = spec.target_cpu.as_deref().unwrap_or("generic");
target.create_target_machine(&triple, cpu, "", opt, ...)  // "native" passed raw
```

LLVM's `create_target_machine` does **not** interpret `"native"`; only front-end
tools resolve it via `getHostCPUName()`. The unknown-CPU + empty-feature-string
subtarget was benign on macOS aarch64 (test passed 3/3) but on the ubuntu-latest
x86_64 runner it lost 64-bit mode and aborted the entire test run:

```
LLVM ERROR: 64-bit code requested on a subtarget that doesn't support it!
```

This was a real user-facing bug, not just a test artifact: `cobrust build
--target-cpu=native` would abort on those CPUs. **Resolution:** expand `"native"`
ourselves via the host-detection helpers, passing LLVM a recognized CPU name + an
explicit feature string carrying 64-bit mode; named CPUs pass verbatim, `None`
keeps the `"generic"` baseline. The CI ubuntu run is the authoritative oracle for
the abort fix (unreproducible on the macOS host). **SHA:** `d276076`.

## Detection rule

> For every config value whose semantics are "ask the environment" (`native`,
> `auto`, `host`, `latest`), verify the code path *resolves it explicitly* via a
> host/environment helper before handing it to a library — never assume the
> library interprets the convention. Audit doc comments that claim auto-detection
> against the actual call (F35 claim-vs-landed drift).

CI candidate: a smoke that exercises each such config value **on every target
platform's CI**, since the benign-vs-fatal divergence is platform-specific.

## General Ballast mitigation

1. **Resolve at the boundary.** Convention-bearing strings get expanded by your
   code at the point of config parsing, not assumed of the callee.
2. **Distrust self-documenting magic strings.** They read as obviously-working
   and so escape scrutiny; they are the highest-risk class for this gap.
3. **Cross-platform CI is authoritative for codegen/target config.** A green
   single-platform audit cannot see a platform-divergent fallback.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F60 / F61 / F62 (this batch) | Same single-platform-audit blind spot: mac-green, ubuntu-red, cross-platform CI authoritative |
| F56 (this batch) | Sibling in the §X.3 detection-gate cascade |
| F59 (this batch) | Adjacent CI-determinism: a value/service whose behaviour the runner controls gating CI |
| F1 — Declared rules without enforcement | Parent family: "resolve conventions at the boundary" implicit; no gate |
