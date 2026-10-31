---
catalogue_id: F61
title: "A negative/error-path test used a real-but-environment-dependent input — the 'guaranteed-to-fail' case actually succeeds on some platforms"
family: non-deterministic CI (platform-divergent test-input sub-form)
severity: P2
status: ratified_2026-05-27
empirical_project: Cobrust ADR-0070 §X.4 Cranelift-removal sprint (2026-05-27)
cobrust_local_id: F61 (f61-xtensa-target-platform-divergent-test.md)
date_ratified: 2026-05-27
cobrust_sha: 27562c5
related: [F58, F59, F60, F63]
---

# F61 — "Guaranteed-unsupported" probe wasn't guaranteed

## Pattern

A test asserts a **negative / error path** — "input X must be rejected" — and
picks a *real* value of X expected to always fail. But the rejection depends on
**environment-varying capability**: on one platform the value is genuinely
unsupported (test passes), on another the toolchain happens to support it (the
operation *succeeds*, the `expect_error` assertion fails). The negative test was
only ever validated on the author's platform, where the value's unsupported-ness
was coincidental, not guaranteed.

The error: using a *real, named* entity (a real CPU arch, a real codec, a real
locale, a real feature) as a "this will surely be rejected" probe. Real entities'
support sets vary across builds and platforms — they make poor invariant inputs.

## Root cause

A negative test needs an input that is **invariantly** in the error class on
*every* platform. A real-but-niche value (Cobrust's case: an LLVM *experimental*
target) is in the error class only where the toolchain omits it. Pick instead a
**structurally impossible** value — one no build can ever accept — so the
rejection is platform-invariant.

Compounding: the test was authored and audited on a single platform where the
divergence was invisible. A single-platform audit *structurally cannot* catch a
platform-divergent assertion.

## Why this matters for Ballast

This is the deterministic-CI thread (with F59/F63) applied to **negative tests**,
which are easy to under-think: "this obviously fails, ship it." But the failure
must be guaranteed by *construction*, not by the author's local toolchain
configuration. And it reinforces the cross-platform-audit rule (F58/F60/F62): for
codegen/target/platform-sensitive changes, the cross-platform CI run is the
authoritative oracle — a green single-platform audit is necessary, not sufficient.

## Empirical evidence (Cobrust 2026-05-27)

Two regression probes for an "unsupported target" error were repointed to
`xtensa-unknown-none-elf`. The macOS author run and the mac-only paired audit
both passed; CI then failed on ubuntu:

- **macOS** (`brew llvm@18`): Xtensa backend not registered → target rejected →
  error produced → tests pass.
- **ubuntu** (`apt llvm-18`): Xtensa (an LLVM *experimental* target) *is*
  registered → target accepted → emit proceeds, no error → `unwrap_err()` panics
  / the `contains("xtensa")` assert fails.

**Resolution:** force the host triple's architecture to `Unknown` — an arch with
**no backend in any LLVM build** — so target construction is rejected
deterministically on every platform. The message assertion was loosened to check
the (deterministic) triple string rather than a hard-coded arch name. **SHA:**
`27562c5`.

**Process note:** two §X.4 follow-on findings (F60 doc-coverage, F61 xtensa) both
slipped the paired audit because it ran on macOS only — platform-sensitive
assertions must use platform-invariant inputs, and the ubuntu CI run is the
authoritative oracle.

## Detection rule

> A negative / error-path test must use an input that is in the error class by
> **construction** on every platform (a structurally impossible value), never a
> real-but-niche entity whose support varies across toolchain builds. Audit
> `expect_error` / `unwrap_err` assertions whose input is a real named arch /
> codec / feature / locale — those are platform-divergence risks.

CI candidate: run the negative-test suite on the **full platform matrix**; a
negative test that passes on one platform and fails on another is by definition
using a divergent input.

## General Ballast mitigation

1. **Construct the failure, don't borrow it.** Use an impossible/synthetic input
   so rejection is invariant — not a real value that "should" be unsupported.
2. **Cross-platform CI is authoritative for platform-sensitive tests.** A green
   single-platform audit cannot see a divergent assertion.
3. **Treat negative tests with the same rigor as positive ones.** "It obviously
   errors" is the assumption that hides the divergence.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F59 / F63 (this batch) | Same deterministic-CI thread: external service (F59) and host-specific path (F63) likewise leak non-determinism into the gate |
| F58 / F60 / F62 (this batch) | Same single-platform-audit blind spot; cross-platform CI authoritative |
| F1 — Declared rules without enforcement | Parent family: "negative-test inputs must be invariant" implicit; no gate |
