---
doc_kind: finding
finding_id: F70
title: "A library's DEFAULT feature set is an implicit host-target assumption that breaks on the first constrained cross-target"
family: F4-Cross-Target (feature-matrix sub-form)
severity: P1
status: candidate
empirical_project: Cobrust v0.7.0 WASM enablement (ADR-0075 Phase 2 Sprint D/E, 2026-05-29)
cobrust_local_id: F70 (f70-cobrust-stdlib-wasm32-feature-flag-gap.md)
cobrust_sha: 446016c
resolution_adr: ADR-0075 (RV+WASM target enablement)
related: [F66, F67, F60, F61]
---

# F70 — Default features are an implicit host-target assumption

## Hypothesis

The codegen layer is target-agnostic and the new target's std builds, so a
constrained cross-target (here `wasm32-wasip1`) should compile the runtime stdlib
once the linker/sysroot plumbing is in place. The falsifiable claim:
*`cargo build -p <stdlib> --target=<new-target>` succeeds with default features
once cross-cc is wired.*

## Method

1. Wire build.rs cross-cc + a `wasm32-cross-smoke` CI job (Sprint D, commit
   `446016c`).
2. Run the live CI smoke (run `26595424952`), not just host-skip-gated tests.
3. On failure, partition the failure modes.

## Result

The live smoke surfaced **two independent blockers**, neither in the
target-agnostic codegen:

**Blocker A — sysroot absent (toolchain-API boundary, F66-sibling).** The cross-cc
step, not the stdlib build, failed:

```
/usr/include/stdint.h:26:10: fatal error: 'bits/libc-header-start.h' file not found
cobrust build: runtime-helper compilation failed via `clang-18`
  (cross-target: Some("wasm32-wasip1"))
```

apt's `clang-18` invoked `--target=wasm32-wasip1` with **no** wasi-sysroot, fell
back to host glibc includes, and pulled a glibc-only header with no wasm
equivalent. The ADR assumption "`clang --target=wasm32-wasip1` bundles the
wasi-sysroot automatically" is **false for the apt clang distribution** — true
only for clang builds that ship a wasi-sysroot (e.g. wasi-sdk's own clang).

**Blocker B — the default feature trio (this finding's core).** `cobrust-stdlib`'s
`default = ["mimalloc-alloc", "tokio-runtime", "llm-router"]` pulls three trees
that cannot build for `wasm32-wasip1`:

| Default feature | Pulls | Why it fails on wasm32-wasip1 |
|---|---|---|
| `mimalloc-alloc` | C `mimalloc` via `cc` | thread-local + OS-page C code; no wasm build |
| `tokio-runtime` | `tokio` → `mio` | `mio` is an epoll/kqueue/IOCP reactor; WASI p1 has no socket syscalls |
| `llm-router` | `reqwest`/`hyper` → TLS + sockets | network stack; no WASI p1 socket API |

The decisive observation: **the hello-world path needs none of them.** Building
`--no-default-features` works because the print path
(`print` → `io::print` → `std::io::stdout().write_all()`) routes through
`std::io`/`std::alloc` only, and every wasm-incompatible module is *already*
behind a Cargo-feature `#[cfg]` that the no-default-features build excludes.

Sprint E resolved A (vendored wasi-sdk-25 sysroot, SHA-pinned, + `--sysroot`
plumbing in build.rs) and *mitigated* B (keep `--no-default-features` for the
cross-build), but **deferred** the real fix: making `cargo build --target=wasm32`
succeed with default features. The CLI does **not** yet pass `--no-default-features`
on its own cross-build subprocess — it works in CI only because the CI step
pre-builds the archive with the flag, short-circuiting the subprocess. On a clean
machine, `cobrust build --target=wasm32-wasip1` would still hit the default-trio
failure.

## Conclusion

Reusable lessons for any multi-target / multi-crate project:

- **A library's default feature set encodes an implicit "host-like target"
  assumption.** Defaults are tuned for the common (native) target — a native
  allocator, a thread reactor, a network stack. The first constrained cross-target
  (wasm, bare-metal, no_std) is where that assumption fires as a hard build break.
  Treat `default = [...]` as a target-portability liability, not a convenience.
- **The minimal path often needs none of the defaults.** Before doing feature
  surgery, check what the actual done-means (hello-world) requires.
  `--no-default-features` is frequently the correct *contract* for a constrained
  target, and a well-`#[cfg]`'d crate makes it free — every incompatible module is
  already gated, so no `#[cfg(target_arch="wasm32")]` source guards are needed.
- **Per-target default selection has no native Cargo mechanism.** Cargo's
  `[target.'cfg()'.dependencies]` gates *deps*, not *default features*. Closing the
  gap requires a driver-level decision: have the CLI auto-pass `--no-default-features`
  (+ a `wasm-min` feature) when the triple is constrained, so end-users never hit
  the raw default-trio failure. **Wire this in the driver, not in docs** — the docs
  mitigation leaves a clean-machine landmine.
- **Live cross-smoke partitions failures the host-test can't see.** The same
  "only the live run reveals it" pattern as F66 (triple normalization) and F67
  (fixture shape): both F70 blockers were invisible to host-skip-gated tests.
  Always partition a live cross-failure into independent blockers before
  attributing it to one cause.

## Detection rule

For each constrained cross-target, add a CI step that runs the stdlib cross-build
with **default features ON** (allowed to fail, non-blocking) alongside the
`--no-default-features` build. A green default-features cross-build promotes the
target to "ergonomic"; a red one is the explicit signal that the driver must
inject the constrained feature set. Separately, the driver's cross-build
subprocess must pass the constrained feature flags itself — never rely on a
CI-prebuilt archive to mask the subprocess default.

## Cross-references

- Cobrust finding `f70-cobrust-stdlib-wasm32-feature-flag-gap.md`; Sprint D commit
  `446016c`. Source: `crates/cobrust-stdlib/Cargo.toml:20` (the default trio),
  `lib.rs:119-141` (the `#[cfg(feature=...)]` module gates), `runtime.rs:18-20`
  (the gated `#[global_allocator]`).
- F66 / F67 — the RISC-V siblings on the same cross-enablement path (triple
  normalization, fixture shape); F70's Blocker A is the wasm analogue of the
  toolchain-API-boundary lesson.
- F60 — LLVM backend missing file-IO externs (a related "the minimal path needs a
  surface the default build didn't provide" gap).
- `cross-compile-target-enablement-pattern.md` — the staged playbook; F70 is the
  feature-matrix stage's empirical evidence.
