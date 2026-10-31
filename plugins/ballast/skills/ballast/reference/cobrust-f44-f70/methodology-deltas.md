---
doc_kind: methodology-deltas
batch_id: cobrust-f44-f70
title: "Methodology deltas since the f41-f43 Ballast snapshot — topology / dispatch / audit refinements forced by the Cobrust v0.7.0 multi-agent run + the 2026-05-29/30 dynamic-Workflow session + the 2026-05-30 FastAPI-real impl run"
date: 2026-05-30
empirical_project: Cobrust v0.6.0 → v0.7.0 multi-agent run (2026-05-22 → 2026-05-29) + the 2026-05-29/30 dynamic-Workflow session (Delta 8 close + Delta 9) + the 2026-05-30 ADR-0080/ADR-0081 FastAPI-real impl run (Deltas 10-11)
prior_snapshot: cobrust-f41-f43 (catalogue through F43; PR follow-up to F31-F40)
status: methodology-evolution (NOT findings — these refine Ballast's own dispatch/audit discipline)
related: [F41, F42, F43, F44, F64, F71, F72, finding:f35-sibling-commit-msg-vs-diff-drift, F36, F37, F61]
---

# Methodology deltas since f41-f43

These are NOT failure-mode findings. They are **refinements to Ballast's own
topology, dispatch, and audit discipline** — Deltas 1-7 and the first run of Delta 8
were empirically forced during the Cobrust v0.6.0 → v0.7.0 multi-agent run; **Delta
8's session-wide close (experiment → default) and Delta 9 (the Elegance Law) come
from the follow-on 2026-05-29/30 dynamic-Workflow session; Deltas 10 (mutation-prove
a tripwire) and 11 (slice an ADR-phase to the smallest independently-gated increment)
come from the 2026-05-30 ADR-0080/ADR-0081 FastAPI-real impl run.** A finding says
"the system did X wrong"; a methodology delta says "the way we *run* the multi-agent
process should change."

Each section: **what changed → why (the empirical trigger) → how to apply.**
Cobrust commit SHAs are cited as evidence, not pasted.

---

## Delta 1 — All-top-tier sub-agents (supersedes the tier matrix)

**What changed.** Every dispatched sub-agent — author *and* audit — uses the top
model. The earlier tier matrix (top model for hard tasks, mid model for
well-scoped/mechanical, never the cheapest) is **retired**. There is no longer a
"this task is simple enough for the mid tier" branch.

**Why.** A single day's run with mid-tier authors produced a cluster of
correlated regressions: a stale version claim copied verbatim from a 5-day-old
draft into two separate PR bodies; a committer-identity leak from an unconfigured
fresh workspace (the F49 class); and an author/audit *race* where the mid-tier
author finished after the audit's polling window, so the audit reported a verdict
against a stale snapshot. The common thread: mid-tier agents under-verify exactly
the cross-cutting invariants (version freshness, identity hygiene, "is my own
output current?") that Ballast relies on the dispatch layer to uphold. The cost
delta of the top tier is dwarfed by the cost of catching and rewriting these.

**How to apply.**
- Every sub-agent dispatch sets the model explicitly to the top tier. No
  defaulting, no "this one's mechanical."
- This binds the **audit side too** — an independent audit on a weaker model than
  the author it reviews is structurally backwards.
- The only carve-out is *not a tier choice*: truly mechanical edits the dispatcher
  can do directly (Delta 2's sub-threshold band) need no sub-agent at all.
- *Evidence (Cobrust):* mid-tier failure cluster 2026-05-22 (stale `v0.3.0` PR
  bodies, F49-class identity leak, audit-vs-author race); top-tier produced the
  v0.6.0 subcommand-collapse impl + multiple design ADRs clean first-pass.

---

## Delta 2 — Dispatcher-as-context-custodian (raw work is offloaded by default)

**What changed.** The orchestrating lead (the "CTO" role) dispatches *raw work*
rather than doing it personally, governed by an explicit threshold table. The lead
keeps only the strategic tier: dispatch ordering, report synthesis, audit-verdict
evaluation, merge/tag decisions, and direct user dialogue.

**Why.** This is **not** a token-cost optimization — it is a *context-density*
optimization. The lead's context holds the load-bearing strategic state (design
rationale, sprint sequencing, the accumulating failure-mode ledger). When that
context nears the auto-compaction threshold, raw prose and raw code compress
*lossily* — the strategic detail is what gets summarized away. Brief sub-agent
reports + decisions compress far better (high signal per token). Doing a 300-line
doc personally burns scarce, compression-fragile context for output a sub-agent
would have produced equivalently.

**How to apply.** Threshold table (dispatch vs. do-it-directly):

| Work | Action |
|---|---|
| 1-2 line typo / SHA stamp / single-Edit fix | Lead may do directly |
| Single-file edit < 30 lines, no conflict | Lead OK (gray zone) |
| Single-file edit ≥ 30 lines | **Dispatch** |
| Multi-file edit (any line count) | **Dispatch** |
| ANY source / impl-file edit | **Dispatch** (+ heavy-build route if applicable) |
| New file ≥ 30 lines / full file > 100 lines | **Dispatch** |
| ADR / findings / README / bilingual docs | **Dispatch** |
| Emergency triage (disk full, branch broken) | Lead fast-acts — speed > offload |

- The anti-pattern to watch: running 5+ Edit calls on one file in a row is, in
  aggregate, "writing the section personally" — dispatch it instead.
- *Evidence (Cobrust):* the rule landed *after* the lead personally wrote a
  ~300-line bilingual README (~5-8k context spent unnecessarily); codified as the
  P10-strict-dispatcher discipline 2026-05-18.

---

## Delta 3 — Mandatory independent post-author audit (pre-merge by default)

**What changed.** Every author dispatch (ADR / impl / test corpus / release prep /
user-facing doc) pairs with an **independent, read-only audit by a different
agent before merge**. Self-review by the author — or by the orchestrating lead who
framed the work — is declared structurally insufficient.

**Why.** The author's (and the framer's) context is biased toward the verdict
"this is done"; they rationalize away the very drift an audit should catch. The
discipline hardened in two steps:
1. *Two tiers.* Tier-1 audits the specific commit/branch just produced. Tier-2 is a
   periodic project-wide sweep (cross-ADR terminology drift, anchor-freshness
   sample, `#[ignore]` accumulation outside the documented honest-debt set,
   wiki-link integrity, supersedes-chain consistency). Tier-1 *by construction*
   misses cross-cutting drift; Tier-2 exists to catch it.
2. *Retroactive is more expensive than pre-merge.* A retro-audit must re-read
   merged content and diff it against original intent — strictly more work than
   gating before the merge.

**How to apply.**
- Audit agent is read-only, top-tier (Delta 1), and a *different* physical agent
  than the author.
- Verdict vocabulary: GO / GO-WITH-FINDINGS / BLOCK. Findings are applied before
  merge.
- **Batch similar surfaces into one audit** (e.g., several same-shape ADRs → one
  combined audit dispatch) — independence is preserved, dispatch count is not.
- Tier-2 cadence triggers: every version bump, every phase closure, every ~10 ADR
  additions, or any cross-cutting smell the Tier-1 auditor self-detects.
- Tier-1 must include the **fixture-name-vs-behavior gate** (a named fixture must
  exercise the shape its name promises, else rename / replace / `#[ignore]` with a
  gap-queue reason).
- Tier-1 must include the **tripwire-mutation gate** (Delta 10): for any
  negative / regression-tripwire test the change relies on, mutation-prove it —
  does it go RED when the guarded property is violated? A green negative test is
  unproven protection until a mutation makes it fail.
- *Evidence (Cobrust):* the gap that motivated the rule was a 3-merge run shipped
  without audit; the v0.7.0 run dispatched a dedicated read-only retro-audit of the
  whole arc (`8a3e8bf..936f13c`) as a first-class wave member.

---

## Delta 4 — Dependency-manifest staging is part of the atomic commit

**What changed.** The "atomic commit = code + tests + docs" rule gains an explicit
line: **a dependency change stages its lockfile in the same commit.** This is now a
pre-commit checklist item demanded in the dispatch prompt, not assumed.

**Why.** An agent adds a dependency, stages only the manifest, and the local build
silently regenerates the lockfile. The locked CI build then rejects *any* lockfile
drift, and a single missed lockfile line fan-out-fails the entire gate cluster
(build + lint + test) with an opaque lockfile-mismatch error — a failure whose
message points at the lock, not at the missing `git add`. This is the F64
generalization: easily-verified pre-flight checks must be *demanded explicitly* in
the prompt template, because agents reliably forget them under sprint tempo (same
shape as the F49 identity pre-flight).

**How to apply.**
- Pre-commit hard check, pasted into any dependency-touching dispatch: after any
  build invocation, run a lockfile status check; if the lockfile changed and the
  commit doesn't include it, stage it before committing.
- Generalize beyond one ecosystem: *any* generated-from-manifest pin file
  (lockfiles, resolved-dependency snapshots) belongs in the same commit as the
  manifest edit. CI runs locked; the dispatcher must too.
- *Evidence (Cobrust):* F64 remediation `73aa3bb` (one-line lockfile entry for a
  dev-dependency added in `1b05ae3`); promoted to a mandatory pre-commit runbook
  line + dispatch-template item 2026-05-28.

---

## Delta 5 — Chain-generality claims are verified against the diff, not trusted

**What changed.** When an author claims a change touched only certain layers (e.g.,
"0 changes to the front-end IR, 0 to the mid IR, N to codegen"), the integrator
**verifies the claim against the actual diff** (a per-layer numstat over the
commit range) before trusting it. Applied *proactively*, not only after a suspected
regression.

**Why.** This is the F35-sibling guard (commit-message-vs-diff drift) promoted from
a reactive finding to a routine integration step. Authors re-scope mid-sprint and
the commit subject keeps the *original* framing; a reader of the log then believes
a layer was touched that wasn't (or vice-versa). The risk is highest for doc-only
and test-only sprints whose original spec described impl intent. A green test count
gives false comfort about *where* the change actually landed.

**How to apply.**
- Integrator computes a per-layer diff stat over the commit range and confirms it
  matches the author's locality claim.
- If scope narrowed mid-sprint, the commit subject must describe the **final diff**,
  not the original dispatch spec; original framing goes in the body or an ADR note.
- Keep an instances ledger of recurrences — accumulating evidence is the case for
  promoting the manual check to a CI guard.
- *Evidence (Cobrust):* `7100849` (a `feat(...cb-mirror)` subject over a doc+test-
  ignore diff); recurrence `d29470f` (`fix(cli/build)` subject over a test-only
  diff — `build.rs` untouched), surfaced by the v0.7.0 arc retro-audit.

---

## Delta 6 — Deterministic-CI / CI-infra-hardening playbook

**What changed.** "CI is the authoritative oracle" (the f41-f43 SPOF lesson, F43)
is made concrete with a hardening playbook for the cloud CI itself, plus a standing
rule: **no test that depends on host disk pressure, parallel-build filesystem
timing, or an external network service may gate CI.**

**Why.** As the project's single authoritative gate, CI inherits a new class of
*non-determinism* failures — green/red driven by infrastructure weather rather than
code correctness. Left unaddressed these are indistinguishable from real
regressions and erode trust in the gate (the F44 stale-green / F59 external-flake
family). Each item below was forced by a concrete CI failure.

**How to apply (playbook items, each with its trigger):**
- **Runner disk exhaustion** → add a disk-reclaim step (e.g.
  `jlumbroso/free-disk-space`) to heavy jobs. *Watch its side-effects*: the
  reclaim action autoremoved a system library the toolchain build needed, forcing
  an explicit re-install of that library afterward. (Cobrust `f514e83` add,
  `92988b1` the libzstd re-install fix.)
- **Redundant in-flight runs** → a concurrency group with cancel-in-progress, so a
  new push cancels the stale run instead of racing it (the F44 orphaned-run mask).
  (Cobrust `a6ee367`.)
- **Parallel-cross-build filesystem-visibility race** (a file written by a
  subprocess not yet visible to the next step on some OSes) → retry-with-backoff on
  the existence check rather than failing once. (Cobrust `55f651b`.)
- **Supply-chain / reproducibility** → SHA-pin third-party CI actions *and*
  downloaded toolchains/SDKs (verify the digest of the fetched archive). (Cobrust
  pins the disk-reclaim action by commit SHA; F70 SHA256-pins a downloaded SDK
  archive.)
- **External-service / disk-heavy benchmark tests** → `#[ignore]` and run opt-in;
  they assert health of a third party or of runner disk, not code correctness.
  (Cobrust F59 external HTTP smoke; F62 size benchmark.)
- **Standing rule:** a green *warm-build local* audit is necessary, not
  sufficient — cold-build CI on every target platform is the authoritative oracle.
  Several gaps surfaced only on cold/clean cross-platform builds (F62 cold-build
  doctest ordering; the X.3/X.4 detection-gate cascade).

---

## Delta 7 — Honest-signal discipline: fix true positives by removal, never mask

**What changed.** A *true-positive* quality signal (a genuinely-unused dependency,
a real lint) is resolved by **removing the cause**, never by silencing the gate
with an ignore/allow directive. Masking is reserved strictly for *false* positives,
and even then must carry a justification comment.

**Why.** This is the F44 stale-green failure mode *in reverse*. F44 taught that a
gate reporting green while a real defect lurks erodes trust in the gate. Masking a
true positive does the same thing deliberately: it trains the eye (human and agent)
to treat that gate's output as noise, so the next *real* hit is also waved through.
An accepted-debt mask is only honest when it cites a specific deferral with a
reason — otherwise it is silent rot (the F37 family).

**How to apply.**
- Unused dependency, dead code flagged by a true-positive lint → delete it.
- Reach for an ignore/allow only when the signal is demonstrably a false positive;
  pair it with a one-line rationale at the directive site.
- An accepted-debt `#[ignore]` must name a specific reason and a deferral target,
  never a bare suppression.
- Add the corresponding detection gate so the class can't silently regress (e.g. an
  unused-dependency CI job).
- *Evidence (Cobrust):* dead-dependency *removed* in `e21f728` (and a 7-crate
  unused-dep cleanup `1914d32`) rather than allow-listed; the unused-dep CI gate
  was rolled out alongside the F44 finding.

---

## Delta 8 — Dynamic-Workflow orchestration (meta; experiment 2026-05-29 → default 2026-05-30)

**What changed.** The back-port that first exercised this — parallel author
fan-out → synthesis → impl → independent audit — was executed by a **deterministic
orchestration script** (a Claude Code dynamic Workflow) rather than by the
orchestrating lead hand-managing each dispatch. First recorded as a Ballast
methodology *data point*, not a ratified practice. **The follow-on
2026-05-29/30 session promoted it from experiment arm to the *default* Cobrust dev
mode** — see the session-wide empirical close below. The concrete reusable shape
(six patterns + the honest-framing guards + the self-improvement chain) is
distilled in `reference/workflow-orchestration-patterns.md`.

**Why (the hypothesis under test).** The dispatch/audit deltas above (1–7) all
exist to patch failure surfaces created by a human-or-agent lead *juggling*
concurrent dispatches: stale snapshots, author/audit races (Delta 1), context
lossy-compaction (Delta 2), skipped audits (Delta 3), forgotten pre-flight checks
(Delta 4). A deterministic script encodes the fan-out → synthesis → impl → audit
topology as code, removing the juggling. **Open question:** does deterministic
orchestration measurably reduce the lead-juggling failure surface versus
hand-managed dispatch — and what *new* surface (rigid topology, harder mid-run
re-scoping, an orchestration script that is itself un-audited code) does it
introduce?

**How to apply / what to watch.**
- Treat deterministic orchestration as an *experiment arm* alongside hand-managed
  dispatch; compare on the failure surfaces Deltas 1–7 enumerate.
- The orchestration script is code — it is subject to Delta 3 (independent audit)
  like any other authored artifact; an un-audited orchestrator is a new SPOF.
- A fixed topology cannot mid-run re-scope the way a lead can; log cases where the
  rigid pipeline forced a worse decomposition than a human would have chosen.
- *Evidence (Cobrust):* the v0.7.0 methodology back-port + a paired Cobrust advance
  step were run via a dynamic Workflow as a stability experiment, 2026-05-29.

**Empirical result — first run (post-run, attribution-corrected).** The first run
produced a clean parallel-fan-out consolidation (4 authors → synthesis, accurate,
complete) and a high-quality `impl` artifact (the §2.5 error-rendering fix). It had
ONE gap: the `impl` agent left its work uncommitted, skipped a format gate, and the
downstream independent-audit stage therefore returned `BLOCK` on incomplete
information.

The lead's *first* read was a design flaw ("single-shot impl needs a nudge-loop").
That attribution was **wrong**. Root cause was a **transient socket/network failure
mid-agent** — the same infra-failure class as `F40-stream-watchdog-false-stall-signal`
and the 529 / stream-watchdog sub-agent deaths seen elsewhere in the same project.
The orchestration *topology* held; the `impl` work itself was sound (the lead's
integration was cosmetic finishing — apply formatter, commit, fix one self-citing SHA).

The sharpened lesson — the **first real new surface** deterministic orchestration
introduces is **no built-in resilience to transient agent failure**:

- A bare `agent()` whose process dies (socket / 529 / watchdog) returns a truncated
  or errored result, which a downstream stage (here, the audit) then consumes as if
  it were a real deliverable — producing a misleading verdict on a non-failure.
- **Refinement:** wrap failure-prone stages so a truncated/errored agent result is
  *detected and re-dispatched* before any downstream stage consumes it (retry-with-
  backoff on agent error; treat an unparseable/empty result as a retry trigger, not
  a finding). The impl→audit edge specifically must not let a network-killed impl
  poison the audit.
- This does **not** invalidate the topology — it says a production orchestrator needs
  the same transient-failure retry discipline that hand-managed dispatch gets for free
  (the lead simply re-dispatches a died agent). Encode it once, in the script.
- *Corrected by:* human review of the run's impl-agent transcript, 2026-05-29 — the
  error was a socket close, not a reasoning/quality gap.

**Empirical close — the session-wide result (experiment → default, 2026-05-30).**
A single intensive 2026-05-29/30 Cobrust session then ran the dispatch loop
*almost entirely* as dynamic Workflows rather than hand-managed dispatch — the
**session's workflow run was ~11 workflows**: a Ballast F44-F70 back-port, a §2.5
error-UX fix, a Ballast docs-enrich, then a product pipeline (an ecosystem-operators
phase, the F71/WASM enablement, a backend-strategy ADR, an HTTP-middleware layer, a
second ecosystem-operators phase, a numerical-library strategy ADR, and a linalg
phase). This is the close-out that promotes Delta 8 from *experiment arm* to the
**default dev mode**:

- **The last several workflows ran fully autonomous** — audit verdict `GO`, **zero
  lead-side finishing**, just push + CI. (Contrast the first run above, which
  needed cosmetic lead integration after the socket death.)
- **The audit gate earned its keep** — it caught real issues a less-disciplined
  flow would have shipped: (a) the **network-socket-truncated impl deliverable** →
  `BLOCK` (the first-run gap above, which became the `robust()` refinement); (b) a
  **dogfood overclaim** — the methodology's *own* enriched docs asserting uncitable
  product statistics, violating **Ballast §4 no-overclaim applied to ITS OWN docs** →
  `GO_WITH_FINDINGS`; (c) a **latent false-green bug** — an unresolved
  dotted-attribute chain that *built and ran* with garbage values, caught at the
  **TEST stage** (test-first-PAIR-as-script). Each verdict changed what the script
  did next; none was ceremony.
- **The self-improvement chain** (the methodology improving itself across runs):
  workflow-1's socket death → the **socket-resilience refinement** (`robust()`
  retry-wrap) was folded into **every subsequent workflow → no further
  socket-truncation failure**. Then the **honest-framing guards** (claim-vs-diff +
  chain-generality honesty — an agent must report the *real* git-numstat, not
  falsely claim "0 mir/codegen" for a change that legitimately touches those layers)
  were folded in. Then the **ELEGANCE LAW** (Delta 9 below) was folded into every
  backend/ecosystem audit rubric. Each run's failure became the next run's built-in
  guard — research-product co-evolution at the orchestration layer.

These results do **not** retract the two standing caveats: a fixed topology still
cannot mid-run re-scope (log cases where the rigid pipeline forced a worse
decomposition), and the orchestration script is **itself authored code** — subject
to Delta 3 independent audit like any other artifact (an un-audited orchestrator is
a new SPOF). The reusable patterns are catalogued in
`reference/workflow-orchestration-patterns.md`; the SKILL.md §"Part 2.5" cross-ref
treats this as the current default rather than an experiment.

---

## Delta 9 — The Elegance Law (the .cb surface is a clean re-design, not a mechanical clone)

**What changed.** A new methodology *principle* (user-mandated): when wrapping a
Rust crate or designing an ecosystem / backend surface, the `.cb` surface is a
**clean re-design that DROPS the accumulated footguns of other languages**
(Flask / FastAPI / Express / pydantic, …) — it is **NOT a mechanical clone** of the
wrapped crate's or the predecessor framework's API. This **extends "Drop from
Python" (CLAUDE.md §2.2) from the language core to the ecosystem surface**, and is
the §2.5 LLM-first principle (the language LLM agents write correctly on the first
try) applied to libraries, not just syntax.

**Why.** The same reasoning that purges GIL / implicit-truthiness / exceptions-as-
control-flow from the *core* applies to the *ecosystem*: a wrapper that faithfully
reproduces another language's footguns inherits its first-try error surface. A
clean re-design is what makes the wrapped surface something an LLM agent gets right
ex ante. Concretely, each ecosystem/backend surface decision should prefer:

- **compile-time-typed validation** over runtime-asserted (drops pydantic-style
  runtime validation surprises);
- **explicit dependencies** over decorator / dependency-injection magic (drops
  FastAPI-style implicit DI);
- **`Result`** over exceptions-as-control-flow;
- **typed routes / bodies** over stringly-typed (drops Flask/Express stringly-typed
  routing);
- **typed composable config** over option-bag sprawl.

**How to apply.**
- **Each ecosystem ADR carries a footgun-ledger** — an explicit list of *which
  specific other-language footgun each surface decision avoids* (e.g. "typed body
  extractor — avoids pydantic's runtime-only validation; avoids Express's
  `req.body` being `any`"). The ledger is the falsifiable record that the surface is
  a re-design, not a clone.
- **Each backend / ecosystem workflow's audit scores `elegant + no-legacy-debt`** —
  a rubric dimension that asks "did this surface drop the predecessor's footguns, or
  mechanically reproduce them?" This was folded into every backend/ecosystem audit
  rubric across the 2026-05-30 session's self-improvement chain (Delta 8 close).
- Cross-check against §2.2 (the "Drop from Python" table) and §2.5 (compile-time-
  catch-errors + maximize-overlap-with-training-data): an elegant ecosystem surface
  surfaces its bugs at type-check time and matches the LLM's correct priors, not the
  predecessor framework's footgun priors.
- *Evidence (Cobrust):* the session's ecosystem/backend workflows (the
  HTTP-middleware layer, the ecosystem-operator phases, the backend-strategy and
  numerical-library strategy ADRs) each shipped under this law — typed routes/bodies
  and explicit deps over the Flask/FastAPI/Express decorator-and-stringly-typed
  defaults, with the per-ADR footgun-ledger as the artifact.

---

## Delta 10 — Mutation-prove a tripwire before relying on it (audit-discipline refinement)

**What changed.** A negative test — or any "regression tripwire" guarding a
property — can be **green for the wrong reason**: it can pass whether or not the bug
it claims to catch is present. The audit-discipline refinement: **before trusting a
tripwire, mutate the guarded code into its buggy form and confirm the test goes RED,
then revert.** A tripwire's protective value is *unproven* until a mutation makes it
fail. This is now a Tier-1 audit checklist item (Delta 3).

**Why.** This sharpens F36/F37's "green-for-the-wrong-reason" family (a fixture /
negative test passing without exercising what it claims) with the *verification
technique*. The empirical case is exact and instructive: in ADR-0081 Phase-1b, the
contract was that a `body.field` runtime read must be **registration-driven, not
type-only** — a type-only dispatch gate would `serde`-cast a null pointer = UB. The
DEV shipped a runtime "no-UB" negative test that asserts the process *survives*. The
audit mutated the gate to the buggy type-only form and the runtime-survival test
**still passed 3/3** — because today every `.cb`-constructed object is a null pointer
*and* the accessor shim null-guards, so the would-be crash was masked. The
runtime-survival test was **false comfort**: it could not distinguish the correct gate
from the buggy one. The real fix was a disassembly / `nm`-based tripwire — the
non-registered field read must emit **no accessor-symbol call** — and that tripwire
was itself mutation-proven (RED under the type-only gate, GREEN on the real code).
The lesson generalizes beyond UB: any test whose *passing* state is also the state a
real regression would produce is not a guard.

**How to apply.**
- For any negative / tripwire test a change relies on, **mutate the guarded property
  to its violated form and confirm RED**, then revert. If it stays green, the test
  proves nothing — replace it with one that *can* fail (here: assert the *absence* of
  a symbol call via disassembly / `nm`, not the survival of the process).
- Prefer a tripwire that observes the **mechanism** (a symbol emitted, a code path
  taken, an artifact shape) over one that observes a **downstream effect** that other
  defenses (null-guards, fallbacks, coincidental platform behavior) can mask.
- The auditor — not only the author — runs the mutation, because the author's context
  is biased toward "my test works" (the Delta 3 independence rationale applies).
- Tier-1 checklist line: *"for any negative/tripwire test the change relies on,
  mutation-prove it: does it go RED when the guarded property is violated?"*
- *Evidence (Cobrust):* ADR-0081 Phase-1b `body.field` dispatch-gate audit
  (2026-05-30) — runtime no-UB test passed under a mutated type-only gate (false
  comfort); the `nm`-based no-accessor-symbol tripwire was mutation-proven RED/GREEN
  and shipped instead.

---

## Delta 11 — An ADR "phase" is a starting unit, not an atomic dispatch unit (dispatch-granularity refinement)

**What changed.** An ADR **phase** is the *starting* decomposition, not the atomic
unit of dispatch. The orchestrator **slices a phase recursively until each increment
is** (a) **independently testable** — a compile-time `well_typed`/`ill_typed` corpus
for a pure type-checker increment, a runtime E2E for a runtime increment; (b)
**independently gated** — the FULL regression suite + CI green; and (c) **ordered so
each unblocks the next**. Each increment ships as its own audited, CI-green commit.

**Why.** A high-blast-radius type-system / object-model feature dispatched as one
"phase" is both untestable-in-isolation (you can't write a tight pass/fail corpus for
four entangled concerns at once) and too large for one audit to reason about
soundly — the exact surfaces Delta 3 (independent audit) and the false-green findings
(F44/F47) warn about. Slicing to the smallest independently-gated increment makes each
step's proof obligation sharp and its blast radius auditable. It also turns a
**discovered prerequisite into its own increment** rather than letting it bloat a
sibling — when a TEST agent uncovers a hidden dependency, that dependency spins out as
a new, separately-gated increment instead of being smuggled into the increment that
found it.

**How to apply.**
- When an ADR-phase increment would be **untestable in isolation** OR **too
  high-blast-radius for one audit**, slice it further before dispatching. The stop
  condition is: *each piece has its own pass/fail proof (compile-time corpus or
  runtime E2E) and its own green full-regression + CI run.*
- Match the proof to the layer: a **pure type-checker** increment gets a
  `well_typed`/`ill_typed` corpus; a **runtime** increment gets an E2E.
- **A TEST agent that discovers a hidden prerequisite spins it into its own
  increment** — do not let the prerequisite bloat the increment that surfaced it (it
  unbalances that increment's audit and hides the prerequisite's own proof).
- This composes with Delta 2 (the lead offloads each increment as its own dispatch)
  and Delta 3 (each increment gets its own pre-merge independent audit).
- *Evidence (Cobrust, 2026-05-30):* ADR-0080 "Phase-1" was sliced into **1a**
  class-field-tracking (compile-time corpus) / **1b-i** class-name→`Adt` resolution
  (compile-time) / **1b-ii** validation-engine (runtime E2E) / **1b-iii**
  OpenAPI-emit (runtime E2E); ADR-0081 "Phase-1" into **1a** `json_response`
  (independent runtime E2E) / **1b** `body.field`-read (the foundational
  dispatch-gate). The Alias-vs-`Adt` non-unification — discovered by 1a's TEST
  agent — became its **own** increment (**1b-i**) rather than bloating another. Each
  shipped as its own audited, CI-green commit.

---

## Cross-references

- f41-f43 batch — `F43-spof-heavy-build-host.md` (CI-as-authoritative-gate, the
  parent of Delta 6) and the F1-Sediment family (Deltas 4, 5, 7 are sediment-class
  pre-flight/honest-signal disciplines).
- This batch's findings — F44 (stale-green; parent of Deltas 6 and 7), F64
  (lockfile staging; parent of Delta 4), F71 (the wasm-typed-call ABI fuzzer
  surfaced during the same session that closed Delta 8 and folded in Delta 9),
  F72 (the killed-runner CI flake surfaced during the same 2026-05-30 run that
  forced Deltas 10 and 11).
- Delta 8 depth — `reference/workflow-orchestration-patterns.md` (the six reusable
  orchestration patterns: `robust()` retry-wrap, test-first-PAIR-as-script,
  audit-schema-verdict, one-workflow-per-working-tree, ≤4-parallel,
  CTO-integrates-after-verdict) and `SKILL.md` §"Part 2.5".
- Delta 9 (Elegance Law) — CLAUDE.md §2.2 ("Drop from Python"), §2.5 (LLM-first
  design principle); the per-ADR footgun-ledger practice.
- Delta 10 (mutation-prove a tripwire) — `reference/cobrust-f31-f39/F36-agent-self-disciplinary-rule-skip.md`
  and `F37-numeric-anchor-degradation-high-churn.md` (the green-for-the-wrong-reason
  family it sharpens), `F61-negative-test-probe-platform-divergent-input.md` (the
  negative-test-validated-on-one-condition-only sibling); folds into the Delta 3
  Tier-1 checklist as the tripwire-mutation gate.
- Delta 11 (slice an ADR-phase to the smallest independently-gated increment) —
  Delta 2 (offload each increment as its own dispatch) + Delta 3 (independent audit
  per increment); the false-green findings F44 / F47 (an un-isolated increment hides
  exactly this class of defect).
- `reference/cobrust-f31-f39/F40-stream-watchdog-false-stall-signal.md` — the
  transient-agent-failure class behind Delta 8's `robust()` refinement.
- Cobrust source: `cto_operations_runbook.md` (dispatch + audit + pre-commit SOPs),
  `feedback_subagent_model_all_opus.md` (Delta 1), `feedback_p10_strict_dispatcher.md`
  (Delta 2), `feedback_post_author_audit_mandatory.md` (Delta 3),
  `f35-sibling-commit-msg-vs-diff-drift.md` (Delta 5).
