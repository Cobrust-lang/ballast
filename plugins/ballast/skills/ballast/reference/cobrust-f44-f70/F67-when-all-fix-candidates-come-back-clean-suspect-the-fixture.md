---
doc_kind: finding
finding_id: F67
title: "When every plausible fix candidate verifies clean, suspect the test fixture, not the system under test"
family: F3-Diagnosis (mis-located-bug sub-form)
severity: P2
status: ratified
empirical_project: Cobrust v0.7.0 RISC-V enablement (ADR-0075 Phase 1 Sprint B, 2026-05-29)
cobrust_local_id: "commit-message-only — reconstructed from d29470f (no finding file authored)"
cobrust_sha: d29470f
resolution_adr: ADR-0075 (RV+WASM target enablement)
related: [F66, F36, F37, F35]
---

# F67 — All fix candidates clean ⇒ suspect the fixture

## Hypothesis

A CI cross-link step fails with an undefined-symbol error. The dispatch brief
framed three "possible bug" candidates, all in the **build plumbing**:

- (A) `emit()` not receiving the cross triple,
- (B) link-arg ordering dropping the user object,
- (C) cross-stdlib / cross-cc plumbing gap.

Falsifiable claim under test: *the undefined-symbol failure is a plumbing gap in
one of A/B/C.*

## Method

1. Reproduce the CI failure (runs `26588644199` + `26590462193`):

```
/usr/lib/gcc-cross/riscv64-linux-gnu/.../ld: cobrust_main.<triple>.o:
in function `main': undefined reference to `_cobrust_user_main'
```

2. Investigate each candidate A/B/C by direct inspection + host-side cross-emit.
3. Critically: cross-emit a *known-good* source (`examples/hello.cb`, which
   declares `fn main`) on the macOS host and inspect the object symbols.

## Result

**All three plumbing candidates verified clean.** `emit()` received the cross
triple correctly; the link-arg ordering correctly included the user `.o`; the
cross-stdlib + cross-cc plumbing operated exactly as the prior sprint intended.

The smoking gun came from step 3 — the known-good source linked fine:

```
$ cobrust build --target=riscv64gc-unknown-linux-gnu --emit=obj \
    examples/hello.cb -o /tmp/rv-test/hello.o
$ nm /tmp/rv-test/hello.o | grep cobrust_user_main
00000000000000a4 T _cobrust_user_main        # symbol IS emitted
```

The bug was in the **test fixture's source shape**, not the system under test.
The failing test wrote bare top-level code — `print("hello cobrust riscv64")\n` —
with no `fn main`. Codegen emits `_cobrust_user_main` **only** from a `fn main`
body; bare module-level code lowers to an `_cobrust_init_<n>` symbol the C
runtime shim never calls. The C shim's `main()` references `_cobrust_user_main`,
which the fixture never produced → undefined at link.

The one-line fix (commit `d29470f`): wrap the test source in
`fn main() -> i64: ... return 0`. The CI smoke step itself used the correctly
shaped `examples/hello.cb` and was only *blocked behind* the malformed test.

## Conclusion

This is a **diagnostic-discipline** finding, not a code bug. The reusable rule:

- **When every plausible fix candidate comes back clean, the bug is upstream of
  where you're looking — most often in the test fixture / harness, not the system
  under test.** A run of "all candidates verified correct" is itself evidence:
  the failure is real, so if none of your hypotheses hold, the input that
  *triggers* the failure is mis-shaped.
- The cheapest disambiguating experiment is **run the system on a known-good
  input.** If the known-good input passes where the fixture fails, the fixture is
  the bug. Cobrust's `nm hello.o` on the `fn main`-bearing source did this in one
  command and instantly relocated the bug.
- Fixtures encode an implicit contract with the system (here: "source must
  declare `fn main` to emit the entry symbol"). When the contract is undocumented
  or only fossilized in an unrelated test's comment, a new fixture silently
  violates it. This is the F36/F37 family (fixture-name/behavior drift,
  silent-rot) viewed from the diagnosis side: the fixture *looked* like a valid
  program but tested a shape the system doesn't support.

## Detection rule

Before opening a multi-candidate investigation into the system under test,
budget one experiment to run the system on a minimal known-good input. If it
passes, pivot the investigation to the failing fixture. Make implicit
fixture↔system contracts explicit (a `fn main` requirement, a required header,
a setup precondition) in a shared helper or a doc-comment the next fixture author
will see.

## Cross-references

- Cobrust commit `d29470f` (commit-message-only finding; this is the generalized
  reconstruction). Fix: `crates/cobrust-cli/tests/cross_compile_riscv64_e2e.rs`
  (+12/-1 lines, wrap source in `fn main`).
- Codegen contract: `cobrust-codegen/src/llvm_backend.rs:3221-3229` (entry-symbol
  emission gated on `fn main`); pre-existing limitation documented at
  `cobrust-cli/tests/ecosystem_den_e2e.rs:18-19`.
- F66 — the immediately prior seam on the same RISC-V path (real codegen bug);
  F67 is the *next* failure, which superficially looked like another plumbing gap
  but was a fixture artifact. The pair shows the value of not pattern-matching
  "another cross-link error" → "another plumbing fix."
- F36 / F37 — fixture-name-vs-behavior drift + silent-rot (the authorship side of
  the same fixture-contract risk).
