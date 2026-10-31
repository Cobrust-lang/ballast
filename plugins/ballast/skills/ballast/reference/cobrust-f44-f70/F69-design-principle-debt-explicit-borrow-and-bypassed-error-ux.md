---
doc_kind: finding
finding_id: F69
title: "Constitutional-principle debt: a 'we'll honor it later' design north star silently erodes at every new call site"
family: F1-Sediment (design-principle-erosion sub-form)
severity: P1
status: open
empirical_project: Cobrust v0.7.0 (CLAUDE.md §2.5 LLM-first principle, observed 2026-05-29)
cobrust_local_id: "F69 — not yet filed in Cobrust repo; forward-looking catalogue entry"
cobrust_sha: 936f13c
constitutional_binding: CLAUDE.md §2.5 (LLM-first — training-data-overlap + Direction A borrow shortcut + Direction B error-UX-prints-the-fix)
related: [F41, F37, F36]
---

# F69 — Constitutional-principle debt erodes at every new call site

## Hypothesis

A project adopts a north-star design principle (Cobrust §2.5: *"the language an
LLM agent writes correctly on the first try"*, with binding sub-rules: maximize
training-data overlap, eliminate `clone()`/borrow clutter (Direction A), and make
error messages print the FIX not just the diagnosis (Direction B)). The
falsifiable risk: *a principle that is stated but not enforced by a gate will be
violated by every increment that ships under deadline, and the violations
accumulate exactly like ordinary technical debt (F1-Sediment) — except the debt
is against a constitutional commitment, so it silently invalidates the project's
core value claim.*

## Method (observation, not yet a fix)

Inspect two §2.5 surfaces against new code shipped in the ecosystem-import +
target-enablement sprints (HEAD `936f13c`):

1. **Direction A — borrow shortcut / training-data overlap.** Grep handle-method
   and stdlib-builtin call sites in shipped `.cb` examples.
2. **Direction B — error UX prints the fix.** Inspect the `cobrust build` error
   path against the dedicated `error_ux` renderer that already exists.

## Result

**Debt surface 1 — explicit `&` borrow contradicts the training-data prior.**
Shipped examples force an explicit `&` on the receiver of stdlib/handle calls:

```
# examples/coil_p0/main.cb
let m: f64 = coil.mean(&a)        # numpy training data is np.mean(a) — no &
let s: f64 = coil.std(&a)
# examples/z8_rest_blog/main.cb
if list_len(&parts) < 2:          # Python is len(parts) — no &
let title = list_get(&parts, 0)
if str_len(&title) == 0:
```

This is the single largest §2.5 friction surface. An LLM trained on numpy/Python
writes `coil.mean(a)` / `len(parts)`; the `&a` shape appears in neither corpus, so
every generation against these APIs incurs a borrow-checker correction loop for
zero semantic value. §2.5 Direction A names this as the top-priority deficit; it
remains unaddressed and accretes a new violating call site with every example
shipped — the F41 fossilization dynamic, applied to a *borrow convention* instead
of a *function name*.

**Debt surface 2 — the build path bypasses the existing fix-suggesting renderer.**
`cobrust-cli/src/build.rs:118-120` dumps the raw `Debug` of type/MIR errors:

```rust
let typed = type_check(&hir).map_err(|e| BuildError::Type(format!("type error: {e:?}")))?;
let mut mir = mir_lower(&typed).map_err(|e| BuildError::Type(format!("MIR error: {e:?}")))?;
```

Meanwhile `cobrust-cli/src/error_ux.rs` already exposes a full renderer with
`type_err_with_hint`, `syntax_with_hint`, and a `suggestion` channel — and
`check.rs` / `main.rs` already route through it. The `build` command alone emits
`{e:?}`, the exact "diagnosis without the fix" anti-pattern §2.5 Direction B
forbids. The fix machinery exists; the build path simply doesn't call it.

## Root-cause hypothesis (speculative — verify before quoting)

Both surfaces share the F1-Sediment mechanism: the principle is real and binding,
but **no CI gate or authorship checkpoint enforces it**, so each deadline-driven
increment takes the locally-cheapest path (emit `&a` because the ABI is
by-reference; `format!("{e:?}")` because it compiles) and the global principle
erodes one call site at a time. The likely locations: a missing source-surface
sugar pass for by-reference ecosystem-method receivers (Direction A), and a
one-site renderer swap at `build.rs:120` (Direction B).

## Conclusion

Forward-looking, status **open**. The reusable lessons for any
principle-driven project:

- **A stated principle is not a kept principle.** A north star with no enforcement
  gate is F1-Sediment waiting to happen — it degrades exactly like undeclared
  tech debt, but the cost is higher because it silently falsifies the project's
  headline value proposition (here: "LLMs write it right first try").
- **Audit the principle's own surfaces, not just feature correctness.** Tests
  pass and demos run while the `&a` shape and the `{e:?}` dump quietly violate the
  constitution. Correctness gates don't catch principle erosion; you need a
  dedicated principle-conformance check.
- **When the fix machinery already exists (error_ux), un-routed call sites are
  the cheapest possible debt to repay** — and the most embarrassing to leave,
  because there's no "we haven't built it yet" excuse. Grep for the raw-Debug
  bypass pattern across every consumer, not just the one the principle was first
  wired into.

## Detection rule (CI gate candidates)

- **Direction A:** lint `.cb` example/fixture corpus for `&<ident>` in
  ecosystem-method / stdlib-builtin argument position; each hit is a §2.5-A audit
  issue until a by-reference-receiver sugar lands.
- **Direction B:** grep the compiler-driver crate for `format!("{...:?}")` /
  `{e:?}` in user-facing error construction; every hit that does NOT route
  through the `error_ux` renderer is a §2.5-B violation. Pin the allowed
  error-construction entrypoints; fail CI on raw-Debug error text reaching stderr.

## Cross-references

- CLAUDE.md §2.5 Directions A (borrow shortcut) + B (error UX prints the fix).
- Source: `examples/coil_p0/main.cb` (the `&a` shape),
  `crates/cobrust-cli/src/build.rs:118-120` (raw `{e:?}` dump),
  `crates/cobrust-cli/src/error_ux.rs` (the bypassed fix-suggesting renderer,
  already used by `check.rs` + `main.rs`).
- F41 — same fossilization dynamic for a type-suffix function name; F69 is its
  borrow-convention + error-surface analogue.
- F37 / F36 — silent-rot + fixture-name drift: the broader family of "stated
  intent silently diverges from shipped reality with no gate to catch it."
