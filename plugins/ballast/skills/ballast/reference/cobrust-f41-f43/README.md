---
batch_id: cobrust-f41-f43
title: "F41-F43: Cobrust empirical corroboration batch (source-surface leakage + device-name redaction + SPOF build host)"
date: 2026-05-21
cobrust_baseline: Phase J wave-2 FULL CLOSED (main HEAD 53b5ed2 at time of filing)
prior_batch: cobrust-f31-f39 (PR #1, open)
---

# Cobrust F41-F43 batch — README

Three new failure-mode findings empirically corroborated by Cobrust Phase G/J
sprints (2026-05-19/20), submitted as a follow-up to PR #1 (F31-F40 batch).

## Slot mapping

| This batch | Cobrust local ID | Ratified SHA | Incident date |
|------------|-----------------|--------------|---------------|
| **F41** | F38 — source-surface leakage of codegen primitive | `46c0946` | 2026-05-19/20 |
| **F42** | F39 — device-name leakage in commits + repo files | `d012df9` | 2026-05-19 |
| **F43** | F40 — single-point-of-failure heavy-build host | `9cb84b5` | 2026-05-19/20 |

## Finding summaries

### F41 — Source-surface leakage of codegen-internal primitive

A codegen-internal monomorphic name (`print_int`, `print_str`, ...) leaks into the
source-face PRELUDE during a demo sprint and fossilizes as examples accumulate usage
against it. This directly violates the LLM-first training-data-overlap rule: LLMs
trained on Python/Rust write `print(x)`, not `print_int(x)`. Cleanup required 333 LOC
across 4 commits. Resolution: polymorphic dispatch + CI lint on type-suffix PRELUDE names.

**Key metric:** 133 `.cb` call sites + ~200 Rust inline strings refactored.
**Cobrust SHA:** `46c0946` (ADR-0064 ratified).

### F42 — Device-identifying names leaked into git history via sub-agent memory read-through

Sub-agents treating operator memory references (SSH host, IP, port, GPU SKU) as
publishable grounding detail embedded opsec-sensitive strings into 31 commit messages
and 18 repo files before a pre-publish audit caught them. Required `git filter-repo`
history rewrite + force-push. Resolution: going-forward opsec boundary rule + CI grep gate.

**Key metric:** 31 commit messages + 18 repo files rewritten.
**Cobrust SHA:** `d012df9` (Option-A privacy rewrite).

### F43 — Single-point-of-failure heavy-build host

Routing all full-workspace cargo verification through a single SSH-gated workstation
created a pipeline-halting SPOF: when the host died, sub-agents retried silently for 8+
hours consuming tool budget, with no fallback policy. Resolution: DG abandonment — all
heavy gates route to GH Actions CI; Mac local = single-crate quick-feedback only.

**Key metric:** 8+ hour sprint blocked on unavailable SSH host.
**Cobrust SHA:** `d012df9` (DG abandonment, same session as F42 remediation).

## Files in this batch

```
cobrust-f41-f43/
  README.md                                       (this file)
  F41-source-surface-leakage-codegen-primitive.md
  F42-device-name-leakage-public-artifacts.md
  F43-spof-heavy-build-host.md
```

## Relationship to PR #1 (cobrust-f31-f39)

This batch is independent of PR #1. It can be merged before or after PR #1.
The F41-F43 slot numbers were chosen to be free given that PR #1 claims F31-F40
(using upstream F38/F39/F40 for different patterns than the Cobrust local ones).
