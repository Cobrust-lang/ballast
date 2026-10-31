---
catalogue_id: F41
title: "Source-surface leakage of codegen-internal primitive — type-suffix name fossilizes in user-facing API"
family: F1-Sediment (design-surface contamination sub-form)
severity: P1
status: ratified_2026-05-20
empirical_project: Cobrust Phase G sprint (2026-05-19/20)
cobrust_local_id: F38 (f38-source-surface-leakage-codegen-primitive.md)
date_ratified: 2026-05-20
cobrust_sha: 46c0946
resolution_adr: ADR-0064 (print-monomorphization-source-surface-cleanup)
constitutional_binding: CLAUDE.md §2.5 (LLM-first design principle, training-data-overlap rule)
---

# F41 — Source-surface leakage of codegen-internal primitive

## Pattern

A codegen-internal primitive — named by type shape (`<verb>_<type>`, e.g.,
`print_int`, `print_str`) — leaks into the source-face PRELUDE during a
demo sprint. It fossilizes when subsequent waves do not audit the question:
"is this name source-face API or codegen-internal symbol?"

The leak path:

1. Demo sprint needs to prove codegen works → quickest route is direct
   monomorphic names (`print_int`, `print_str`).
2. Demo lands, wave closes, no cleanup ADR authored.
3. Next wave sees the names in PRELUDE, writes examples against them,
   accumulates usage at call sites.
4. By the time an audit catches it, migration cost is non-trivial
   (50-100+ call sites across examples, fixtures, skills).

This is not a logic bug. It is a **design-surface contamination bug**: the
internal implementation vocabulary bleeds into the user vocabulary.

## Root cause

Two independent dynamics compound:

- **Sprint-tempo bias**: demo-ware ships the shortest path to visible output.
  Monomorphic names (`print_int`) are that shortest path. No gate asks "is
  this user-facing?" at demo time.
- **Accumulation drift (F1 Sediment)**: wave-2 onward does not re-examine
  whether PRELUDE entries are source-face intentional. Each usage is another
  call site, each call site raises the migration cost, which raises the
  perceived risk of cleanup, which delays the cleanup further.

## Why this is critical for Ballast / LLM-first projects

Per CLAUDE.md §2.5 (LLM-first design principle, constitutional north star):

> Cobrust is the language LLM agents write correctly on the first try.

The **training-data-overlap rule** is the key binding:

- LLMs trained on Python/Rust write `print(x)` — one of the highest-frequency
  call patterns in any Python corpus.
- `print_int(x)` appears in neither Python nor Rust training data. It is a
  Cobrust-internal artifact.
- Result: LLM generates `print(x)` → `NameError: print_int is not defined` →
  LLM confused by gap between prior and actual API → corrective loop consumes
  tokens and latency for zero semantic value.

Every type-suffix source-face name is a **friction multiplier on every future
LLM-driven generation session** against the codebase.

## Empirical evidence (Cobrust 2026-05-19/20)

**Affected names (Phase E demo era, Cobrust 2026-04):**

| Source-face name (wrong) | Should be    | Internal C-ABI symbol    |
|--------------------------|--------------|--------------------------|
| `print_int`              | `print`      | `__cobrust_print_int`    |
| `print_str`              | `print`      | `__cobrust_print_str`    |
| `print_bool`             | `print`      | `__cobrust_print_bool`   |
| `print_float`            | `print`      | `__cobrust_print_float`  |

**Call-site count at cleanup (ADR-0064 sprint):**
- 133 `.cb` call sites + ~200 Rust inline-source test strings refactored.
- Net source delta ~333 LOC across 4 cleanup commits.

**Sprint commit references (Cobrust main):**
- `c73be4e` — PRELUDE table: remove `print_int`/`str`/`bool`/`float` source-face entries
- `b51b907` — polymorphic `print()` dispatch in `synth_call` + codegen monomorphization
- `5e87e77` — mechanical refactor: 133 `.cb` call sites + Rust inline strings → `print()`
- `46c0946` — Phase 4 fix: `Ty::None` callret locals must dispatch to `__cobrust_println_int`
  not str-buf (caught by regression during cleanup)

**Ratified at:** commit `46c0946` (feature/0064-print-mono, rebased on main 2026-05-20).

**Post-ratification state:**
- Zero `print_int`/`print_str`/`print_bool`/`print_float` call-sites in any `.cb` file
  under `examples/`. Confirmed via `grep -rEn "print_(int|str|bool|float)\(" examples/ --include="*.cb"` → empty.
- LC-100 12/12 maintained (including LC-05 which caught a `Ty::None` dispatch bug exposed by cleanup).
- 5+ integration tests passing for polymorphic `print`.

## Detection rule (CI gate candidate)

For every function listed in the PRELUDE source-face table:

> If the function name matches `<verb>_<type>` where `<type>` ∈
> `{int, str, bool, float, list, dict, set, tuple, ...}`, file an audit issue:
> "should this be polymorphic in source?"

```
for name in PRELUDE.source_face_names:
    if re.match(r'^[a-z_]+_(int|str|bool|float|list|dict|set|tuple)$', name):
        emit_audit_warning(
            f"PRELUDE name '{name}' matches type-suffix pattern — "
            "verify it is source-face intentional, not codegen-internal leakage"
        )
```

Candidate for a lint pass in CI. Zero false-positive risk on a well-curated PRELUDE:
intentional type-suffix names are rare; any hit deserves a justification comment.

## Resolution path

1. **Identify**: grep PRELUDE source-face table for `<verb>_<type>` names.
2. **Classify**: for each hit, determine whether it is source-face intentional
   (user writes it) or codegen-internal (should be hidden behind a polymorphic
   dispatch).
3. **Cleanup sprint**: remove the monomorphic names from PRELUDE; add polymorphic
   dispatch that routes `print(x: T)` to `__cobrust_print_T` post-typecheck.
4. **Mechanical refactor**: batch-rename all call sites (mirrors LC-100 &borrow
   226-site batch pattern — treat as a mechanical sprint, not a semantic one).
5. **Gate**: add CI lint to prevent re-introduction.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F36 — fixture-name-vs-behavior drift (Cobrust F36) | Same family: wave-1 demo-ware fossilizes without audit checkpoint |
| F37 — silent-rot-on-accepted-debt (Cobrust F37) | Same family: accepted debt silently accumulates usage; no discipline at debt boundary |
| F1 — Declared rules without enforcement | Parent family: "design surface should be polymorphic" is common sense; no enforcement gate exists at PRELUDE authorship time |
