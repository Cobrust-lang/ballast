---
catalogue_id: F37
title: "Numeric-anchor degradation in ADRs under high-churn surface files"
family: F1-Sediment (doc-tree decay sub-family)
severity: P2 (doc correctness)
status: ratified_2026-05-18
empirical_project: Cobrust v0.3.0 Phase G batch (ADR-0052a-g)
cobrust_local_id: F34 (f34-pre-candidate-numeric-anchor-degradation-high-churn.md)
date_ratified: 2026-05-18
discovered_by: project-wide Tier-2 review-claude ab88ae5a4ec1ab490
second_corroborator: Phase H batch ADRs 0055c + 0055d adopted symbol anchors explicitly
---

# F37 — Numeric-anchor degradation in ADRs under high-churn surface files

## Symptoms

ADRs cite `file:NNN` (file path + line number) as cross-references to source
code locations. A few weeks later, every cited line number in those ADRs is
wrong by 50-200+ lines. The drift is invisible: no compile error, no runtime
failure. A reader follows the anchor and sees adjacent code that's
plausibly-related but not the intended site — so the drift goes unnoticed until
a dedicated anchor audit.

High-churn files (compiler crates receiving frequent impl additions) exhibit
this most severely because every sprint that adds arms or methods to existing
functions shifts ALL downstream line numbers.

## Root cause

Author writes ADR at time T₀, cites `check.rs:1532` (the correct line at T₀).
The file grows continuously as subsequent sprints add variant arms and impl
blocks in the same file. At T₀+N days, the line cited in the ADR has drifted
by the cumulative growth of all code added above that line. The drift is
cumulative and monotonic during active development.

F27-style "verified-at-HEAD" discipline catches drift on an INDIVIDUAL author
dispatch — but silent drift accumulates between audits.

## Quantitative evidence

Cobrust Phase G batch (ADR-0052a-g), verified 2026-05-18 by project-wide Tier-2
sweep (`ab88ae5a4ec1ab490`):

- `crates/cobrust-types/src/check.rs` grew **60-80% during Phase G**
- `crates/cobrust-cli/src/error_ux.rs` grew from ~547 to ~1194 LOC (+118%)

Stale anchors found:
- **ADR-0052b**: ~16 stale `check.rs:NNN` anchors + 6 stale `error_ux.rs:NNN`
- **ADR-0052d-prereq**: `check.rs:920` → actual location L1008 (Δ +88 lines)
- **ADR-0052g**: anchors pinned at `1fbed82` still valid (4-day delta only)
- **Total**: ~24 stale anchors in 2 ADRs after ~14 days of active development

## SOP fix — symbol anchors over numeric

Prefer `file::symbol` over `file:NNN` for any ADR cross-reference to source
code in actively-developed files:

**Wrong (numeric anchor — drifts with file growth)**:
```markdown
See `crates/cobrust-types/src/check.rs:1532` — the `synth_expr` match arm
that handles `ImplicitTruthiness`.
```

**Correct (symbol anchor — survives line-number drift)**:
```markdown
See `check.rs::TypeError::ImplicitTruthiness arm` in `synth_expr`.
```

or:

```markdown
See `check.rs::Ctx::synth_expr` (the `ImplicitTruthiness` match arm).
```

Symbol anchors survive line-number drift because they reference stable
identifiers (function names, variant names, struct fields) rather than
absolute positions. Conventional in Rust-doc culture — `rustdoc`
cross-references are symbol-based.

**High-churn file list** (as of Cobrust v0.3.0 — update for your project):
Files receiving >10% LOC growth per sprint are high-churn. Use symbol anchors
unconditionally for these. Numeric anchors are acceptable only for files that
are considered stable (no active development in the current phase).

**Second option — SHA-pin numeric anchors** (acceptable for point-in-time
references):
If a numeric anchor is load-bearing (exact line matters for the argument), pin
it to a specific commit SHA:
```markdown
At `check.rs:920` (as of `1fbed82`, 2026-05-14) — note: this line drifts
with ongoing development; prefer symbol form for long-lived references.
```

## Phase H adoption as second corroborator

Phase H batch ADRs 0055c + 0055d explicitly adopted symbol-anchor convention
throughout (e.g. `check.rs::Ctx::synth_expr`, `check.rs::Ctx::synth_call`
over numeric `check.rs:NNN` form). Tier-1 audit `af22fcdedbd1976d5` Lane 2
documented this adoption as a load-bearing design decision for ADR longevity.

Two-phase evidence (Phase G first-instance + Phase H explicit adoption)
satisfies the second-corroborator requirement.

## Cross-references

- F31 (ADR scope-reality divergence) — F37 is the doc-maintenance analog:
  F31 catches scope gap at authorship time; F37 catches anchor gap at
  maintenance time.
- F36 (agent self-disciplinary rule skip) — numeric-anchor-write may itself
  be an F36 instance: the agent knows the symbol-anchor convention but judges
  "numeric is clearer here."
- Cobrust finding:
  `docs/agent/findings/f34-pre-candidate-numeric-anchor-degradation-high-churn.md`
- Cobrust ADRs: `docs/agent/adr/0052b-*.md`, `docs/agent/adr/0055c-*.md`,
  `docs/agent/adr/0055d-*.md`

## Status

Ratified 2026-05-18. Symbol-anchor convention adopted in Cobrust ADR authoring
standard for Phase H+ batch. Existing numeric anchors remain until next Tier-2
audit sweep (v0.4.0 ship). High-churn file list maintained in CTO runbook.
