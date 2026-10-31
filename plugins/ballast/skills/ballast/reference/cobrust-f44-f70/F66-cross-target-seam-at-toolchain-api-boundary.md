---
doc_kind: finding
finding_id: F66
title: "Cross-target enablement seams live at the toolchain-API boundary, not where the source-level config suggests"
family: F4-Cross-Target (toolchain-API contract sub-form)
severity: P2
status: ratified
empirical_project: Cobrust v0.7.0 RISC-V enablement (ADR-0075 Phase 1 Sprint B, 2026-05-29)
cobrust_local_id: "commit-message-only — reconstructed from 57ebc7e (no finding file authored)"
cobrust_sha: 57ebc7e
resolution_adr: ADR-0075 (RV+WASM target enablement)
related: [F58, F67, F70, F61]
---

# F66 — Cross-target enablement seam lives at the toolchain-API boundary

## Hypothesis

When you add a new compile target, the work you *expect* is config plumbing:
thread a `--target` flag, point the linker at the cross-cc, pick the right
sysroot. The expectation is that the **codegen backend itself is target-agnostic**
because "LLVM/Cranelift already supports that arch." The falsifiable claim under
test: *enabling target T is a build-system-config task, not a backend-API task.*

## Method

1. Target backend already enabled upstream (LLVM 18 ships `riscv64`/`riscv32`
   backends by default; `Target::initialize_all()` registers them).
2. Thread the Rust-convention triple straight through to the backend init:
   `Target::from_triple("riscv64gc-unknown-linux-gnu")`.
3. Run the live cross-smoke (CI run `26585626128`), not just the host-skip-gated
   test.

## Result

The build failed at the backend-init seam, NOT at any config layer:

```
cobrust build: unsupported target: "No available targets are compatible
with triple riscv64gc-unknown-linux-gnu"
```

The triple was rejected *even though the RISC-V backend was registered.* Root
cause (verified by the fix at commit `57ebc7e`):

- Rust convention bakes the ISA profile into the **architecture component**:
  `riscv64gc` (the `gc` = `+m,+a,+f,+d,+c`).
- Upstream LLVM only knows the bare arch names `riscv64` / `riscv32`. ISA
  extensions must travel separately, as `TargetMachine` `target-features`.
- **The decisive detail:** `LLVMGetTargetFromTriple` (the C API) does **not**
  call `Triple::normalize` internally. `clang` and `llc` *do* normalize before
  calling it — so the same triple "works in clang" and fails through the C API.

The fix is a `normalize_triple_for_llvm` helper that rewrites the arch component
to LLVM's vocabulary (`riscv64gc` → `riscv64`) and synthesises the matching
feature string (`+m,+a,+f,+d,+c`), covering every target-lexicon RISC-V variant.
Non-RISC-V triples pass through unchanged (unit test asserts the pass-through for
x86_64 / aarch64-darwin / wasm32-wasip1 — `wasm32` is already a valid LLVM arch
name and needs no normalization).

## Conclusion

The enablement seam was at the **toolchain-API contract boundary**, not in the
config plumbing the planning ADR enumerated. The general lesson for any
multi-target project:

- A toolchain library's "supported targets" list is necessary but not
  sufficient. The **calling convention into that library** (which normalization,
  which feature-string split, which entrypoint contract) is where the real
  enablement work hides, and it is invisible from the source-level target config.
- **"Works in the reference driver (clang/gcc) but fails through the API"** is
  the diagnostic signature of an un-normalized input the driver was silently
  fixing up. When a vendored API rejects an input the canonical CLI tool accepts,
  suspect a normalization/canonicalization step the CLI does and the API doesn't.
- Test the **live cross path**, not just the host-skip-gated unit test. A
  skip-gate that returns early on a dev host (no cross-cc / no qemu) will report
  green while the backend-init seam is still broken. F58 (host `target-cpu=native`
  meaningless under cross), F67 (cross-link fixture shape), and F70 (wasi-sysroot
  absent) are the sibling "only the live run reveals it" gaps in the same sprint.

## Detection rule

For each newly-enabled target, add a backend-init unit test that drives the
*Rust-convention* triple string (the one users actually pass), asserting the
backend accepts it AND that pre-existing targets still pass through unchanged.
This catches the normalization-contract gap at unit-test latency instead of at
the live cross-smoke.

## Cross-references

- Cobrust commit `57ebc7e` (commit-message-only finding; this catalogue entry is
  the generalized reconstruction). Fix in
  `crates/cobrust-codegen/src/llvm_backend.rs` (`normalize_triple_for_llvm` +
  unit test `normalize_triple_for_llvm_riscv_and_passthrough`).
- ADR-0075 §"Combined risk surfaces" predicted "cross-target LLVM triple shape"
  as a risk; this is its concrete realization.
- F67 — the *next* seam along the same path (cross-link), reached only after F66
  unblocked codegen.
- F4-Cross-Target family sibling: `cross-compile-target-enablement-pattern.md`
  (the full staged playbook this finding is one stage of).
