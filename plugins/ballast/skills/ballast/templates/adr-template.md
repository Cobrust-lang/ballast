<!-- Template for an ADR (Architecture Decision Record).
     Copy to your project's docs/ tree, replace placeholders, commit
     in the same commit as the implementation it covers. -->

---
doc_kind: adr
adr_id: NNNN          # zero-padded, monotonic; check ls docs/agent/adr/
title: "<5-10 word title>"
status: proposed       # → accepted on merge → superseded if later replaced
date: YYYY-MM-DD
last_verified_commit: TBD  # stamp on merge, then update on revisits
supersedes: []
superseded_by: []
relates_to: []
---

# ADR-NNNN: <Title>

## Context

What's the situation that requires a decision? What constraint /
problem / opportunity makes the status quo untenable?

Cite specific evidence:
- Quote constitution / prior ADR / finding
- Show the failure case (paste actual error / metric)
- Name the people / agents who flagged this

Avoid: "we should add X". State: "X is missing because Y constraint;
without X, Z fails."

## Options considered

Minimum 3 options. If you only thought of 2, you didn't think long
enough.

### Option 1 — <name>
- Pros: ...
- Cons: ...

### Option 2 — <name>
- Pros: ...
- Cons: ...

### Option 3 — <name> (recommended OR rejected)
- Pros: ...
- Cons: ...

For options not chosen, state explicitly: **Rejected because <reason>**.

## Decision

We chose **Option N** because <reason in 1-3 sentences>.

### Implementation map

What touches what:
- `crates/foo/src/bar.rs:line` — change X
- `crates/foo/tests/baz.rs` — add test for Y
- `docs/<tree>/<file>.md` — update Z

(For Cobrust, this is the layer-explicit section. If this ADR proposes
a fix at codegen layer, double-check by dumping MIR first — the
"Codegen vs MIR layer pre-flight" rule.)

### Done means

Falsifiable success criteria. **Not "implementation lands"**, but
"behavior X produces output Y given input Z".

- [ ] Criterion 1 — verifiable command + expected output
- [ ] Criterion 2 — verifiable command + expected output
- [ ] N tests pass; specifically test names listed
- [ ] Doc-coverage gates pass

## Consequences

### Positive
- Outcomes the project gains

### Negative
- Outcomes the project loses (debt, complexity, perf hit)

### Risk
- What could go wrong; what monitoring catches it; what mitigation
  exists

### Neutral / unknown
- Things that need empirical verification post-implementation

## Cross-references

- Prior ADRs that constrain this one
- Findings that motivate this one
- External literature / benchmarks

## Layer correction (post-merge addendum, only if applicable)

If implementation landed at a different layer than §Decision §Implementation
map, document here. Do **not** rewrite §Decision — preserve audit trail.

Example:
> §Decision said "fix in cranelift_backend.rs". Empirical fix landed in
> mir/lower.rs because <root cause moved up a layer>. Reasoning details:
> ...
>
> Lesson: future <category> ADRs default to dump MIR first.
