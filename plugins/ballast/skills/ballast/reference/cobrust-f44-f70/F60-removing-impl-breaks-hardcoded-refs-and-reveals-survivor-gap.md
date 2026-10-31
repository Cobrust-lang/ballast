---
catalogue_id: F60
title: "Deleting one implementation breaks tooling hardcoded to its path AND reveals the survivor never had a declaration the deleted one carried"
family: parallel-implementation drift + hardcoded-path-in-tooling
severity: P2
status: ratified_2026-05-27
empirical_project: Cobrust ADR-0070 §X.4 Cranelift-removal CI run (2026-05-27)
cobrust_local_id: F60 (f60-llvm-backend-missing-file-io-externs.md)
date_ratified: 2026-05-27
cobrust_sha: 27562c5
related: [F56, F58, F61, F37]
---

# F60 — Removing the reference impl breaks hardcoded tooling and exposes a survivor gap

## Pattern

When a project removes one of two parallel implementations, two failures fire at
once:

1. **Auxiliary tooling hardcoded to the deleted path breaks.** Shell scripts,
   doc-coverage checks, CI guards that `grep <deleted-file>` to verify some
   invariant now fail with "no such file" — they were never repointed.
2. **The survivor turns out to lack something the deleted impl carried.** A
   declaration / capability that lived only in the removed implementation
   silently vanishes. It was latent because the feature it served was never
   exercised end-to-end (its tests were `#[ignore]`'d / unimplemented), so the
   survivor's gap went unnoticed while the now-deleted impl "covered" it on paper.

The removal is again a **detection gate**: it surfaces both the stale tooling
references and the survivor's missing pieces in one CI run.

## Root cause

- **Hardcoded path coupling**: auxiliary gates referenced a specific
  implementation file by name, an F1-Sediment fossil — convenient when written,
  a landmine when the file moves or dies.
- **Asymmetric scaffolding**: the deleted impl had declarations the survivor
  never grew, because the parallel-impl drift (F56) ran in *both* directions — not
  every capability was mirrored, and the unmirrored ones were invisible while
  their feature was dormant.

## Why this matters for Ballast

A removal sprint's blast radius is wider than the deleted source: it includes
every *tooling reference* to the deleted artifact and every *capability* only the
deleted artifact provided. A build-level paired audit that checks only
build/test/clippy/fmt will miss a hardcoded path in a **shell gate** (doc-coverage,
custom guards) — those are exactly the references a compile-level audit does not
see. **Codegen/removal audits must run the full CI gate set**, including the shell
guards, not just the cargo subcommands.

## Empirical evidence (Cobrust 2026-05-27)

The §X.4 Cranelift-AOT-removal run failed `scripts/doc-coverage.sh`: three
hardcoded greps targeted the just-deleted `cranelift_backend.rs`
("No such file or directory"). Two repointed cleanly to the surviving backend;
the third did **not** — because the file-IO runtime-helper declarations (7
symbols: `read_file`, `write_file`, `stdin_read_all`, …) lived *only* in the
deleted Cranelift backend's signature table and were **never** declared in the
LLVM backend. Latent because `file_io_e2e.rs` was 0-passed / 18-ignored
("pre-impl") — the feature was never run end-to-end, so the missing LLVM externs
went unnoticed; only the Cranelift-grepping doc-coverage check referenced them.

**Resolution:** port the 7 file-IO extern declarations to the LLVM backend
(verbatim signatures), repoint all three shell-gate greps to the surviving file.
The end-to-end tests stay `#[ignore]`'d (completing the feature is separate work);
this restores codegen-side parity + the doc-coverage contract. **SHA:** `27562c5`.

**Process note (verbatim lesson):** the §X.4 paired audit was GREEN but did *not*
run `scripts/doc-coverage.sh` — the audit spec omitted it. A hardcoded path in a
shell gate is precisely the reference a build-level audit misses.

## Detection rule

> Before removing any implementation: (1) grep the *whole repo* — including shell
> scripts, CI YAML, and doc-coverage checks — for references to the deleted
> artifact's path/symbols and repoint them; (2) diff the deleted impl's
> declaration/capability set against the survivor's and port anything the survivor
> lacks. A removal audit MUST execute the **full** CI gate set (shell guards
> included), not just build/test/clippy/fmt.

## General Ballast mitigation

1. **Avoid hardcoded impl-file paths in tooling.** Where a gate must reference an
   implementation, make the reference resilient (a glob, a stable symbol, or a
   single configurable constant) so a move/removal is one edit.
2. **Pre-removal parity diff.** The deleted impl's full surface (declarations,
   helper tables, capabilities) must be reconciled with the survivor.
3. **Full-gate-set audits for removal/codegen changes.** Build-level audits do not
   see shell-gate references; run every gate the CI runs.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F56 (this batch) | Same parallel-impl drift; F56 is the unfixed-correctness-pass direction, F60 the missing-declaration direction |
| F58 / F61 / F62 (this batch) | Same single-platform / partial-audit blind spot in the §X.3/§X.4 arc |
| F37 (Cobrust) — silent-rot-on-accepted-debt | The survivor gap hid behind an all-ignored test suite — silent rot |
| F1 — Declared rules without enforcement | Parent family: "repoint references on removal" implicit; no gate |
