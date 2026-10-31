---
catalogue_id: F45
title: "Stub silently shipped — a 'Wave-N stub' fallthrough compiles + links but no-ops at runtime, and 'feature-complete' cascades over it from adjacent landings"
family: F37-SilentRot (declared-coverage ≠ actual-coverage sub-form) + F35-ClaimDrift
severity: P1 (most-user-visible surface ships broken under a feature-complete claim)
status: ratified_2026-05-22
empirical_project: Cobrust Phase K LLVM backend (v0.5.0 tag 2026-05-18, caught 2026-05-22)
cobrust_local_id: F45 (f45-llvm-backend-wave1-stub-silently-shipped.md)
cobrust_sha: c8ba2bd (broken release HEAD) → 1adf3af (wave-2 fixtures land)
resolution: stdout-diff differential gate + "Wave-N stub must cross-reference a tracked debt" contract
related: [F44, F45a, F46, F37-SilentRot, F35-ClaimDrift]
---

# F45 — Stub silently shipped

## Pattern

A code path carries an explicit `// Wave-N stub` (or `// TODO`, `// deferred`)
comment and falls through to a **no-op that still type-checks, compiles, and
links** — e.g. returns a null pointer or writes `0` to the destination. The
surface produces *no observable side effect* at runtime but passes every
compile-time gate. Meanwhile, adjacent feature landings each get a docs update,
and "feature-complete" **cascades** over the stub region because no landing ever
re-audited that specific surface.

The release ships claiming parity while the most user-visible behavior (here:
stdout from `print`) is silently absent.

## Root cause

- **(a) "Stub" / "deferred" comments are not tracked tasks.** A deferral that
  cites "follow-up sub-task" without filing a tracked issue / `#[ignore]`'d test
  / open spec pretends to be temporary while it becomes permanent.
- **(b) The differential gate ran at the wrong layer.** Fixtures asserted
  "artifact emitted, non-empty" — a *necessary-but-not-sufficient* condition.
  They never asserted "the produced binary prints what the reference
  implementation's binary prints." Object-emit-success masked runtime no-op.
- **(c) Feature-complete cascade.** Five adjacent sub-features shipped, each with
  a docs update that re-checked only its own surface. The cross-cutting runtime
  surface was audited at *none* of those landings.
- **(d) Claim reflects the latest dispatch, not cumulative state** (F35-ClaimDrift
  at release scope): release notes echoed the most-recent wave's landing rather
  than the cumulative runtime surface of the whole subsystem.

## Why this is critical for Ballast / agent-driven projects

A multi-agent project builds one surface per dispatch. Without a gate that proves
the *whole* assembled artifact behaves, each agent legitimately reports "my piece
landed," docs aggregate those reports into "complete," and nobody is responsible
for the seam. The stub is invisible precisely because every individual claim was
true — the falsehood lives only in the *aggregation*. For an LLM-first language
this is acute: the model emits the canonical `print(x)`, observes nothing, and
files a silent-defect report against a release that advertised correctness.

## Empirical evidence (Cobrust v0.5.0, 2026-05-18 → 22)

- v0.5.0 tagged + released with an opt-in backend flag. `print("hi")` AOT-compiled
  via that backend → **empty stdout**. `print(fib(40))` computed (CPU spun) but
  never printed.
- Two stub regions in `llvm_backend.rs` at the release HEAD `c8ba2bd`: an
  extern-name call fallthrough that dropped the call and wrote `0`, and a
  `Constant::Str` lowering that returned a null pointer (every string-typed local
  null). **Both carried explicit "Wave-1 stub" comments** citing a deferral ADR —
  but the follow-up wave the comment promised was never filed.
- The reference backend (Cranelift) had shipped these surfaces fully months
  earlier; the asymmetry was never re-checked before tagging.
- 30 differential fixtures all asserted "object file emitted, non-empty" — none
  asserted stdout-equivalence between the two backends.
- Resolution: a deferral ADR scoping the missing wave (`34e5aca`), the
  implementation (`89de141`), and **7 `stdlib_io_*` fixtures that diff one
  backend's stdout against the other's** (`1adf3af`), shipped as a hotfix release.

## Detection rule (CI gate)

1. **Differential gate at the behavior layer, not the artifact layer.** For every
   surface where two implementations should agree, assert
   `actual.stdout == reference.stdout` (run both binaries), never merely
   "artifact non-empty."
2. **Stub-annotation contract.** Every `// Wave-N stub` (or `TODO`/`deferred`)
   comment in shippable code MUST cross-reference exactly one of: a tracked
   `#[ignore = "deferred to <ID>"]` test in the same module, a specific issue
   URL, an open spec/ADR with `status: proposed`, or a finding URN. A bare stub
   comment with no back-reference is a silent-rot signal. Grep candidate:

```bash
# Flag any stub/deferred comment with no tracking reference:
grep -rEn '(Wave-[0-9]+ stub|TODO|deferred)' src/ \
  | grep -vE '(#\[ignore|issues/|ADR-[0-9]|finding:)' \
  && echo "FAIL: untracked stub/deferral — fossilization risk"
```

3. **Honest-cite at release scope.** Any "feature-complete / parity" claim MUST
   enumerate: which implementations are claimed at parity, and *per surface*
   whether it is working vs stub, with a pointer to the behavior-layer test that
   proves it.

## Resolution path

1. **Identify**: grep for stub/deferral comments lacking a tracking reference.
2. **Classify**: which are genuinely temporary (file the tracked debt) vs
   permanently shippable as no-op (rare; document why).
3. **Add behavior-layer fixtures** for each claimed surface before re-claiming parity.
4. **Extend the post-author audit SOP** with a "differential behavior check for
   any release tagged with an opt-in backend/feature flag" item.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F44 — CI cache stale-green | Sibling: "green ≠ working" — F44 at the cache layer, F45 at the assertion layer (object-emit green masks runtime no-op) |
| F45a — Stub catalogue systemic | Child: confirms this exact pattern across the *full* extern surface, not just stdout |
| F46 — Wheel not installable | Sibling: "artifact appears in package" ≠ "artifact works for end users" — same object-emit-vs-behavior gap at the packaging layer |
| F37 — Silent-rot-on-accepted-debt | Parent: a stub with no `#[ignore]` is the rot signal |
| F35 — Commit-msg vs diff drift | Parent: claim reflects latest dispatch, not cumulative state |
