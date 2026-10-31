---
doc_kind: finding
finding_id: F71
title: "wasm is a free ABI-correctness fuzzer: cross-compiling to a strict-typed target audits the whole extern table at link time"
family: F4-Cross-Target (ABI-correctness sub-form)
severity: P2
status: candidate
empirical_project: Cobrust WASM enablement follow-on (the 2026-05-29/30 dynamic-Workflow session, F71/WASM workflow)
cobrust_local_id: F71 (f71-wasm-typed-call-signature-mismatch.md)
cobrust_sha: c3caa88
resolution_adr: ADR-0075 (RV+WASM target enablement)
related: [F66, F70, F58, F60]
---

# F71 — wasm is a free ABI-correctness fuzzer

## Hypothesis

A runtime extern (`__cobrust_*` FFI surface) whose codegen-emitted call signature
disagrees with the runtime's actual definition is a real defect — but on a
permissive native ELF linker it links and runs anyway, because the native linker
does not type-check call signatures. The falsifiable claim: *a signature
mismatch between the codegen-emitted extern decl and the runtime def is invisible
on native and surfaces only under a target whose call ABI is strictly type-checked.*

## Method

1. Enable `wasm32-wasip1` as a cross-target (the same staged enablement path as
   F66/F67/F70; see `cross-compile-target-enablement-pattern.md`).
2. Run the live wasmtime cross-smoke (not a host-skip-gated unit test) on a
   hello-world-class `.cb` that exercises a runtime extern.
3. On a wasmtime trap, partition the failure: is it a codegen bug, a fixture
   bug, or an ABI-contract bug between codegen and the runtime?

## Result

The native build linked and ran clean. The **wasm32 cross-run trapped** at the
typed-call check:

```
signature_mismatch: ... __cobrust_* expected i32, found i64 ...
```

Root cause: the codegen layer had hard-coded a length argument as `i64` while the
runtime `extern "C"` definition used `usize` — which is **`i64` on a 64-bit native
host but `i32` on `wasm32`**. On the 64-bit ELF target the two widths coincide *and*
the linker would not have rejected them even if they hadn't, so the mismatch was
doubly invisible. On `wasm32`, where `usize == i32`, the emitted `i64` call site no
longer matches the imported function's declared type, and wasm's strict typed-call
validation traps before execution.

The decisive observation: this is **not** a wasm-specific bug. It is a latent
native-tolerated ABI defect in the `__cobrust_*` extern table that wasm merely
*surfaced for free*. The same sloppiness on any other width-sensitive extern would
have been equally invisible on native and equally caught by the wasm typed-call
check.

## Conclusion

Reusable lessons for any project with a hand-written FFI / extern surface:

- **A permissive native linker is not an ABI oracle.** ELF (and most native
  linkers) link `extern` calls by *name*, not by *signature*. A codegen/runtime
  signature disagreement — wrong integer width, wrong arg count, wrong pointer
  width — links and runs, producing either coincidentally-correct results (when
  widths happen to coincide) or silent garbage (when they don't). The defect is
  real the whole time; the native target just never reports it.
- **A strict-typed cross-target audits the WHOLE extern table for ABI
  correctness, for free.** `wasm32`'s typed-call validation rejects every call
  whose signature doesn't match the imported function's declared type. Cross-
  compiling to it is therefore a *zero-extra-effort fuzzer over every `__cobrust_*`
  extern* — every width/arity/pointer mismatch that native tolerates becomes a
  hard, located trap. (`wasm-bindgen`/`wasm32` is the most accessible such target;
  CHERI and some sanitizer ABIs are stricter-still siblings.)
- **`usize`/`isize` is the canonical trap.** Pointer-width integer types are the
  most common source of native-tolerated, wasm-caught mismatches because their
  width *changes* across the host/wasm32 boundary while a hard-coded `i64` does
  not. Audit every extern that passes a length / count / index / pointer-width
  value: the runtime should use the width-portable type and codegen must emit the
  matching one per target, never a hard-coded 64-bit width.
- **Same "only the live cross-run reveals it" pattern as the rest of the batch.**
  Like F66 (triple normalization), F67 (fixture shape), and F70 (sysroot +
  feature matrix), this was invisible to host-side tests and surfaced only on the
  live cross-smoke. Partition a live cross-failure into independent causes
  (codegen / fixture / ABI-contract) before attributing it to one.

## Detection rule

Add a `wasm32` (or other strict-typed-target) **cross-smoke that exercises the
runtime extern surface** to CI, gated non-blocking first per the cross-enablement
playbook. Treat its `signature_mismatch` traps as a standing ABI-correctness lint
over the entire `__cobrust_*` extern table — a green wasm cross-run is evidence
the extern signatures are width-consistent end-to-end, which no native build can
attest. Independently, codegen must derive width-sensitive extern arg types from
the target pointer width, never hard-code `i64`.

## Cross-references

- Cobrust finding `f71-wasm-typed-call-signature-mismatch.md`; surfaced during the
  WASM enablement follow-on in the 2026-05-30 dynamic-Workflow session. Resolved in
  Cobrust `c3caa88` — codegen derives the length-arg width (`usize_ty`) from the
  target pointer width across the emitted `__cobrust_*` externs (i64 native, i32
  wasm32), rather than hard-coding i64.
- F66 / F67 / F70 — the RISC-V + WASM cross-enablement siblings on the same path;
  F71 is the ABI-correctness stage of that staged enablement.
- F60 — LLVM backend missing file-IO externs (a related "the extern surface didn't
  match what the target needed" gap on the same `__cobrust_*` table).
- F58 — `target-cpu=native` magic string, the other "native-meaningful value is
  wrong under cross" sibling.
- `cross-compile-target-enablement-pattern.md` — the staged playbook; F71 adds the
  ABI-correctness dividend of stage 5 (live cross-run) to its "combined risk
  surfaces / pointer width" checklist row.
