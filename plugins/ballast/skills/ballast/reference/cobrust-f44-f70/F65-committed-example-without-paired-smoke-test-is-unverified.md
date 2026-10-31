---
catalogue_id: F65
title: "A flagship example committed without a paired end-to-end smoke test doesn't even compile — and hides a stack of layered gaps no one hit because nothing ran it"
family: F1-Sediment (unverified-artifact sub-form) + fixture-name-vs-behavior drift
severity: P1 (a 'MUST-ship' demo that never worked)
status: ratified_2026-05-29
empirical_project: Cobrust Z.8 REST-blog demo + E2E harness sprint (2026-05-28/29)
cobrust_local_id: F65 (f65-z8-rest-blog-demo-multiple-gaps.md)
date_ratified: 2026-05-29
cobrust_sha: a6ee367 (demo draft), 447c22e (F65 resolution — demo lives)
related: [F36, F37, F59, F63]
---

# F65 — A committed example with no paired smoke test is unverified

## Pattern

A **flagship example / demo** is committed to the repo as a marketing-grade
"this is what the system can do" artifact, with **no test that actually runs it
end-to-end**. It does not even compile. Worse, beneath the surface failure sit
**multiple independent, layered gaps** — each blocking, each only discoverable
after the previous one is cleared — between what the example *assumes* is wired
and what the system *actually* exposes. The example's name and prose promise a
working capability; the body delivers something that has never been executed.

The gaps stack like an onion: fix the surface compile error and the *next* gap
(a missing manifest method) fires; fix that and the *next* (wrong persistence
semantics) fires; then a missing setup step; then a feature the demo's own
acceptance criteria require that the demo never implemented. Each is invisible
until you force a real run.

## Root cause

- **No paired smoke test.** The demo-authoring sprint shipped the artifact
  without a test that compiles-and-runs it, so nothing ever exercised it. The
  "demo exists" signal was mistaken for "demo works."
- **Name-vs-behavior drift (F36)**: the filename/title promise a working feature
  ("REST blog demo"); the body doesn't deliver one. A passing-test count would
  give false comfort — except there *was* no test.
- **Accepted-debt hedge deflected the audit (F37)**: a README hedge ("run this
  once all dependencies are green") was read as license to *not* try to build it
  now — so no one ran the obvious `build <example>` before committing.

## Why this matters for Ballast

A demo is the highest-visibility artifact a project ships — and an unverified one
is a **landmine**: it will be the first thing a new user or a downstream agent
tries, and it will fail on them. The Ballast rule is sharp: **a committed example is
not a deliverable until a paired smoke test compiles-and-runs it in CI.** "Looks
right in review" cannot substitute for "executed end-to-end," because the gaps
here were *integration* gaps (source ↔ manifest binding, persistence semantics,
missing setup) that no amount of reading the source reveals.

The **right-route** that *did* surface the gaps is itself the lesson: a *follow-up
E2E-harness sprint* — writing the test the demo-authoring sprint skipped — forced
a real compile and uncovered every gap. "Discovered while authoring the harness"
is the canonical mechanism; the durable fix is to **make the harness part of the
demo-authoring sprint**, not a later archaeology pass.

## Empirical evidence (Cobrust 2026-05-28/29)

A "MUST-ship" REST-blog demo was committed (`a6ee367`). The first real
`build <example>` failed at type-check:

```
type error: UnknownMethod { type_name: "...Request...", method_name: "body", ... }
```

A deeper audit found **five** distinct, independently-blocking gaps:

1. **G1** — `req.body()` not in the framework's request manifest (the Rust struct
   had it; the language-surface binding didn't). *Load-bearing.*
2. **G2** — `app.run(host, port)` not in the manifest (only a background-serve
   variant was surfaced).
3. **G3** — an in-memory DB opened *per handler call* yields a fresh empty
   database every request (no shared state) — wrong persistence semantics.
4. **G4** — the schema/table was never created at startup → "no such table" on
   first request even if G3 were fixed.
5. **G5** — the demo implemented only 2 of the 4 routes its own acceptance
   criteria (the harness done-means) required — demo and acceptance criteria were
   **not co-designed**.

Each gap was masked by the absence of any executing test. The README's
"run-when-deps-green" hedge (F37) and the name promising a working blog (F36)
deflected scrutiny.

**Resolution (`447c22e`)**: a single demo-repair sprint closed all five — added
the missing manifest methods + ABI shims (G1/G2), switched to a file-backed DB
with explicit startup schema creation (G3/G4), added the two missing route
handlers (G5) — and shipped **4 live E2E tests, 0 ignored**, covering the full
POST → GET-by-id → GET-list → DELETE → GET-404 round-trip against the real demo
binary. (Several encoding workarounds were documented as queued follow-ups rather
than scope creep.) The demo now compiles, serves real requests, and is guarded by
its harness.

## Detection rule

> No example / demo may be committed as a deliverable without a **paired smoke
> test that compiles-and-runs it end-to-end in CI**. The smoke test's acceptance
> criteria and the demo's feature set must be **co-designed** (write the harness
> done-means alongside the demo, not after). A demo whose paired test must be
> `#[ignore]`'d is *unverified debt* and must cite a finding + a deferral home —
> never ship silent.

CI candidate: a check that every file under the examples directory is referenced
by at least one (non-ignored) test target.

## General Ballast mitigation

1. **Smoke-test-with-the-demo, not after.** The harness is part of the
   demo-authoring sprint's done-means; the "later E2E sprint" is how gaps rot
   silent.
2. **Co-design demo + acceptance criteria.** The G5 scope mismatch (demo
   implemented fewer routes than its own done-means) is what un-co-designed
   artifacts produce.
3. **Treat integration gaps as undetectable by review.** Source ↔ manifest
   binding, persistence semantics, and missing-setup gaps surface only on a real
   run — reading the source cannot find them.
4. **Distrust "run-it-later" hedges (F37).** A README caveat that defers
   verification is a deflection of the verification obligation, not a discharge
   of it.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F36 (Cobrust) — fixture-name-vs-behavior drift | Direct parent: the demo's name promised behavior the body didn't deliver |
| F37 (Cobrust) — silent-rot-on-accepted-debt | The README "run-when-green" hedge deflected the gap audit; the unran demo silently rotted |
| F59 / F63 (this batch) | Sibling "verify it for real" thread: F59 (don't let unverified externals gate CI), F63 (SOPs must match reality), F65 (examples must be executed) |
| F1 — Declared rules without enforcement | Parent family: "examples must work" implicit; the gate is a paired-smoke-test CI check |
