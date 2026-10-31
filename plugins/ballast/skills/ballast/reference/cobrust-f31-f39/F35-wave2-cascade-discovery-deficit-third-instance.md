---
catalogue_id: F35
title: "Wave-2 cascade discovery deficit — third-instance corroboration of F33 in method-dispatch infrastructure"
family: cascade-discovery-gap (F33 corroboration)
severity: P2
status: ratified_2026-05-17
empirical_project: Cobrust v0.3.0 Phase G Wave 2 (ADR-0052d-prereq)
cobrust_local_id: F32-candidate (0052d-prereq-impl-blocker.md)
date_ratified: 2026-05-17
second_corroborator: structural (ADR §"Precedence" authorship vs. parser source mismatch)
---

# F35 — Wave-2 cascade discovery deficit (F33 third-instance corroboration)

## Symptoms

A sub-ADR for method-dispatch infrastructure contains a §"Precedence" clause
that states "no parser change needed: existing path already produces the
required AST shape." The DEV agent implements the method-dispatch additions
and hits a structural parser blocker — the borrow-operand validator explicitly
rejects the very AST shape the §"Precedence" clause claimed was already
supported.

This is the third instance of the same cascade-discovery deficit pattern
(F33 first instance: `Str`-ownership predicate flip; F34 second instance:
bidirectional unify; F35: parser-cap boundary in method-dispatch prereq).

## Root cause

The ADR's §"Precedence with 0052a `&s`" was authored as **forward-looking
reasoning** ("the design will produce this shape") rather than **verified
current-state** ("at current HEAD, the parser accepts this"). The author
ran a logical deduction on the parser structure; the deduction was correct
for the _intended_ design but incorrect for the _current_ implementation
which had a Wave-1 cap that blocked the shape.

Structural asymmetry: ADR authors reason about intended system state; the
DEV agent implements against actual source state. Any divergence between
intended and actual state produces a blocker that appears only at impl time.

## SOP fix — forward-looking ADR text must be flagged

Add a tagging convention to ADR text:

```markdown
> **[VERIFIED-AT-HEAD]** The parser admits `&(s.method())` at call site
> `parser.rs::validate_borrow_operand` — grep confirms `Call` is accepted.

vs.

> **[FORWARD-LOOKING]** Once ADR-0052d ships, the parser will admit
> `&(s.method())` by extending `validate_borrow_operand` to accept method-form.
```

Any ADR clause about a "no parser change needed" or "existing path already
handles X" assertion must be tagged `[VERIFIED-AT-HEAD]` with a grep result
OR tagged `[FORWARD-LOOKING]` acknowledging a future dependency.

The DEV agent's dispatch contract should require: "for any `[VERIFIED-AT-HEAD]`
clause in the ADR, re-verify the claim at current branch HEAD before
implementing against it."

## Evidence

Cobrust ADR-0052d-prereq Wave 2, 2026-05-17:

- ADR-0052d-prereq §"Precedence with 0052a `&s`" (lines 117-121) stated:
  > "No parser change needed: the existing `parser.rs:1239-1249` Attribute
  > production + `parser.rs:1105-1110` borrow-operand validator already
  > produce `Unary(Borrow, Call(Attr(s, "method"), args))` for `&s.method(args)`."

- Actual source (verified at HEAD `1643776` on `feature/0052d-prereq-dev`):
  `crates/cobrust-frontend/src/parser.rs::validate_borrow_operand` at line
  1134-1139 explicitly rejects `ExprKind::Call { .. }` with error message:
  > "borrow of a call-result is not supported in Wave-1 (ADR-0052a §8 cap)"

- Test `f30wit_method_03_borrow_precedence_binds_tighter_than_method_call`
  fails at parse time with this error.

- DEV correctly filed the blocker finding and deferred `f30wit_method_03` to
  the ADR-0052d follow-up sprint (Path C), rather than making unauthorized
  parser changes.

## What DEV did right

The DEV agent's response to this F35 instance was correct:

1. Hit the blocker; recognized it as outside the dispatch scope.
2. Filed `findings/0052d-prereq-impl-blocker.md` immediately.
3. Did NOT make unauthorized parser changes to fix the test.
4. Deferred the failing test with a clear ADR forward-reference.
5. Shipped all other method-dispatch tests green (2/3 `f30wit_method` + all
   25 well-typed + 13 ill-typed + 5 e2e tests).

This is the intended "STOP-and-file" behavior. The finding is about the
upstream ADR authoring process (forward-looking claim not tagged), not the
DEV agent's handling.

## Cross-references

- F33 (predicate-flip cascade discovery deficit) — first instance; F35 is
  the third corroboration of the same pattern across different domains.
- F34 (wrapper-type bidirectional unify) — second instance.
- Cobrust finding: `docs/agent/findings/0052d-prereq-impl-blocker.md`
- Cobrust ADR: `docs/agent/adr/0052d-prereq-method-dispatch.md`
  §"Precedence with 0052a `&s`" (stale claim documented)

## Status

Ratified 2026-05-17. `[VERIFIED-AT-HEAD]` vs `[FORWARD-LOOKING]` tagging
convention proposed for Cobrust ADR authoring standard. Third-instance
corroboration (after F33 and F34) validates the cascade-discovery-deficit
pattern is a systemic Ballast failure mode, not project-specific.
