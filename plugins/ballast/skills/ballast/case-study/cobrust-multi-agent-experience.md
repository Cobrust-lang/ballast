---
case_study_id: cobrust-multi-agent-2026-04-30-to-2026-05-12
project: Cobrust (Rust-implemented Python successor + AI-native translation pipeline)
duration: 12 days wall-clock (2026-04-30 → 2026-05-12); main narrative covers Days 1-10 with Day 11+12 appendix events
human_time: ~6 hours (estimated, mostly strategic decisions + 守闸; expanded in Day 11+12 appendix)
agent_time: ~80% of LOC produced
final_state: v0.1.0 + v0.1.0-beta + v0.1.0-beta.1 + v0.1.1 + v0.1.2 stable shipped + α Phase F.2 in flight; ~278 commits, 49 ADRs (0001..0048 + 0047a), 27 findings
attribution_origin: review-claude window (third-party audit)
---

# Case study: Cobrust 12-day multi-agent build-up

This case study reports what worked and what failed in applying
Ballast-flavor methodology to a real software project — Cobrust, a
Python-syntax statically-typed compiler with AI-native translation
subsystem.

This is **not** a success story sanitized for marketing. It includes
the failure modes, the wrong-hypothesis findings, the marketing
overreach we walked back. The whole point is the empirical track
record of what Ballast prevents and what it doesn't.

---

## Project shape

- **Codebase**: 16 Rust crates (frontend / hir / types / mir / codegen
  / llm-router / translator / pkg / stdlib / ...)
- **Goal at start**: Phase E (M0..M14) — language core + tooling
- **Goal at day 11**: 0.1.0-beta public release with end-to-end Python
  library translation demo
- **Total commits**: ~278 (at HEAD `a2b3eab` 2026-05-12)
- **Total ADRs**: 49 files (0001..0048 + 0047a sub-numbered)
- **Total findings**: 27
- **Cumulative tests**: 2,541 passed / verified at HEAD `6008634` (Day 8 anchor; current at HEAD ~2,611+, not re-baselined in case study)

## Topology actually used

```
Human (1, "wbj010101"):
  - Strategic decisions (license, namespace, public release timing, wedge)
  - Final 守闸 + merge approval
  - ~6 hours total work

CTO agent (1, opus):
  - Phase E milestone planning
  - ADR Phase 1 spikes
  - 4-way parallel sub-agent dispatch
  - ~150+ Phase 1 spike + 守闸 cycles

P9 sub-agents (varied, opus or sonnet, parallel-up-to-4):
  - M11.1, M11.2, M11.3 codegen sprints
  - M12.x, M13, M14 milestone implementations
  - Audit #1, #3a real-LLM translation sprints
  - Cross-arch validation sprints
  - ~30+ P9 [P9-COMPLETION] cycles

P7 sub-agents (sonnet primarily):
  - CLI hardening, doc rewrites, README polish
  - syntax highlighting extension
  - ~15 P7 cycles

External review (review-claude, third-party audit window):
  - 10 reviews (9 tactical + 1 strategic)
  - Two stress-test farms (Conway-toy, LeetCode farm)
  - Drafted handoff packs (COVER_LETTER, dispatch prompts, ADR-0038, etc.)
  - **Did not write to main repo** — boundary preserved entire run

External review (claude-desktop, secondary audit window):
  - Final 5-gate pre-release review
  - Drafted post-T1.1 cleanup sprint prompt
```

## What Ballast patterns actually saved us

### Two-phase dispatch (~10x return)

CTO Phase 1 ADR spikes ran 30-60 min each. Phase 2 P9 agent then ran
60-180 min knowing exactly what to do. **Estimate: without two-phase
dispatch, ~50% of P9 sprints would have over-scoped or under-scoped.**

Concrete example: M11.3 (`lower_condition` shared root primitive).
CTO Phase 1 spike specified Option C (root-primitive refactor) over
Option A (surface patch). P9 sub-agent landed implementation
**at MIR layer instead of codegen layer**, but the root-primitive
intent was preserved — recorded as §"Layer correction" addendum.
Without Phase 1 spike, the addendum would not have a clean baseline
to correct against.

### Worktree-per-sprint (~3x return)

4-way parallel was sustainable on M1 Pro 16GB only because each sprint
had its own `target/`. Without worktree isolation, cargo registry lock
contention would have made parallel work pathological.

Witnessed once (with 6 worktrees concurrently): exit 144 (SIGUSR2)
on one cargo test, traced to global lock starvation. After this we
capped at 4-way parallel — which became Cobrust's documented
constitutional ceiling (ADR-0002).

### Honest fail acceptance (~5x return)

Audit #1 (sonnet branch) reported PARTIAL-FAIL on a stateful tomli
function. **The PARTIAL-FAIL itself became the anchor for ADR-0036**
(audit-3a prompt-design fix), which then upgraded §1.2 from
mechanism-validated to production-validated.

Without honest fail acceptance, the sonnet branch would have been
silently retried until it "passed" via lower threshold or hidden
adjustments. We'd have shipped 0.1.0-beta with worse prompt-design
debt.

### Stress-test farms (~∞ return on bug-finding)

Two stress-test farms (Conway-toy 1D cellular automaton, LeetCode
Round 1 5 problems) found **2 P0 codegen bugs in 24 hours**:

1. **i8/i64 type narrow** — Conway-toy 4-block compute pattern.
   Closed by ADR-0033 Option C "two-bugs-one-fix" pattern.
2. **`while <BinOp> == 0:` head miscompile** — LeetCode 263 Ugly Number
   stress test. Closed by ADR-0035 "lower_condition shared root
   primitive" in MIR.

Both bugs would have shipped to 0.1.0-beta otherwise. Synthetic corpora
did not catch either. The decisive feature: **a real user perspective
exercising the system**, even if the user is an AI agent, finds
defect classes that internal tests don't enumerate.

### Schema-invariant frontmatter (~3x return on doc reliability)

After 9 close-out reviews showed snapshot.md repeatedly accumulated
sediment ("write new section, forget to delete old"), we added schema
invariants:

```yaml
schema_invariant: |
  Every ADR mentioned in any section must appear in §"ADR roster" table.
  Every finding mentioned in any section must appear in §"Findings ledger".
```

Once invariants were declared, future agent could mechanically check
("does roster have all ADRs?") rather than rely on careful reading.
This reduced sediment in the next ~8 turns to ~1 violation per turn
(from ~3-5 prior).

---

## What Ballast didn't prevent

### Wrong hypothesis finding (review-claude 8th review own)

Review-claude wrote `findings/while-binop-eq-zero-condition-miscompile.md`
with a §"Root-cause hypothesis" stating the bug was in
`cranelift_backend.rs` (codegen layer). **Empirical fix landed in
`mir/lower.rs`** (MIR layer) — one layer up.

The hypothesis got cited in subsequent ADR-0035 §Decision before the
fix landed. The ADR §"Layer correction" addendum corrected the layer
post-merge, but the original §Decision retains the wrong layer
hypothesis.

**Lesson incorporated into Ballast**: finding §"Root-cause hypothesis"
should be marked "speculative — verify before quoting" up front.
Updated finding-template.md accordingly.

### Marketing overreach (review-claude README draft)

Review-claude drafted a public README with the line "5–50× faster".
That's drawn from Mojo / Pyston historical numbers, not Cobrust
measurements. Actual Cobrust tomli benchmark: 9.05× to 13.8×.

Caught by external claude-desktop in T2.B fix.

**Lesson**: Even Ballast's "benchmark cite experiment file" rule didn't
prevent marketing copy from drifting. The rule needs to apply
to README marketing language too, not just ADRs and findings.
Updated README-public-template implicitly.

### Sediment despite invariants (F1 third instance — P0 SOP gap)

By the 11th review (multi-agent team audit), F1 had been observed in
**three distinct forms** within 11 days:

- **F1.0** (8th review): snapshot.md held stale L121-128 binary
  verification段 after L20-25 was rewritten — classic 重写忘删
- **F1.1** (9th + 10th review): snapshot frontmatter `schema_invariant`
  block was added in 9th review fix, declared 5 invariants. By 11th
  review, **2 of those 5 invariants were violated** (HEAD field stale
  by 14 commits; ADR-0035 mis-pinned to "prompt-design" in 2 files).
  Declared invariants without lint = invariants get violated.
- **F1.2** (11th review): constitution §3.3 "Code change ⇒ both doc
  trees" is supposedly enforced by `scripts/doc-coverage.sh`. **But the
  script's check scope only covers M0..M14 baseline ADRs (0001..0029)**.
  ADR-0030..0039 全部 silently outside the enforcement net.
  `grep -rE "ADR-003[0-9]" docs/human/` returns **0 hits**. Triple-tree
  drift is systemic for all post-M14 work.

**Three different forms of "rule declared without enforcement scope
keeping pace"**. Cobrust upgraded F1 from "lesson" to **"P0 SOP gap"**
in Ballast reference catalogue: any project-level rule must ship with an
automated check **in the same commit**, or be marked "ASPIRATIONAL"
not "REQUIRED".

**Lesson incorporated**: Ballast §"Documentation discipline" now mandates:
- Schema invariants compile to script assertions (CI gates them)
- Constitution rules cite the enforcement script (no orphan "should")
- doc-coverage scripts auto-discover scope (not hardcode milestone lists)

### Multi-agent self-audit at high-stakes gates (P10 upgrade)

Day 11 introduced a new Ballast pattern: **the external review agent
applying multi-agent topology to its own role**. User triggered:
"你作为审阅者, 其实也可以组建审阅团队, multi subagent去审阅项目".

review-claude (lead) dispatched 4 parallel audit sub-agents pre-tag:
Security / Doc-consistency / Public-readiness / Code-quality. Empirical
result:

- Single-window review (10 reviews #1-#10) found ~3 issues per gate
- 4-agent team audit (1 dispatch) found ~25 issues, including entire
  categories single-window had not scoped (public-readiness identified
  5 fictional example directories + broken `cargo install` path +
  31 namespace mismatches; code-quality identified 100% SAFETY-coverage
  positive finding + unwrap-discipline confirmation)

**Leverage: ~8×.** Wall-clock: 50 min parallel vs 5 hours sequential.

**Verdict**: pre-major-release gates should **default to multi-agent
team audit**, not single-window. Ballast §1 Topology now codifies this
as "self-applied multi-agent audit" pattern.

**Cost**: 3-4× token spend vs single-window. Justified when the cost
of "shipping a broken first impression" is high (pre-public release,
pre-funding-pitch, pre-customer-demo).

### LLM-simulated user as 5th audit dimension (Day 11 P10 升级 v2)

Day 11 also revealed that the 4-agent team was **incomplete**:

> User trigger: "没有用户,你别想了;你就是用户" — pointed out that
> review-claude was performing for an imaginary audience while
> simultaneously not testing for any actual user perspective. The
> user's correction: "用 LLM 来模拟用户" — instead of (a) abandoning
> user-thinking or (b) pretending to have real users, **simulate
> user with LLM persona prompts**.

review-claude dispatched 3 persona agents post-fix-pack:
- **Mei** (Python data scientist, target user)
- **Aleksandr** (Rust skeptic, technical credibility)
- **Sarah** (OSS evaluator, adoption risk)

Each got a richly-defined persona (years exp, prior burned-by, current
frustrations) + scenario + stay-in-character constraint.

**Empirical results** (3 personas × ~30 min each):

| Persona | Issues found | Issues NOT findable by 4-internal-team | Severity peak |
|---|---|---|---|
| Mei | 6 | 6 (install bugs + language UX positioning) | 3 install P0 + fizzbuzz trust-eroding comment |
| Aleksandr | 6 | 6 (architectural credibility gaps) | **closed-loop pipeline + real LLM NEVER intersect** (architectural P0) |
| Sarah | 5 | 5 (governance / business risk) | bus factor 1 + no SECURITY.md (enterprise blocker) + LLM drift undermines bit-identical claim |
| **Total** | **17** | **17** | — |

Out of 42 total findings (4-internal-agent's 25 + 3-persona's 17),
**40% come from persona-only**. None of the 17 persona-only findings
were structurally findable by infinitely-many internal audits, because
internal lenses default-assume "we are the maintainer" and "the README
is what we wrote".

The single highest-impact finding across all 7 audit agents was
Aleksandr's: **constitution §4.2 promises "closed loop L0→L1→L2→L3
with real LLM + repair loop on failure", but the intersection of
"closed loop pipeline" and "real LLM" was NEVER exercised.** T1.1
demo bypassed the production pipeline using direct `Router::dispatch`
+ manual gluing. The repair loop is wired but unexercised in real-LLM
mode. Until ADR-0040 lands (`pipeline::build_router` real-LLM wiring),
the closed-loop validation story holds only for synthetic-mode (which
is itself circular per `findings/translator-real-vs-synthetic-status.md`
since canned responses are hand-written ports). This is a tier-1
architectural concern; no internal audit caught it.

**Lesson incorporated to Ballast**: §1 multi-agent topology updated to
make persona simulation the **5th mandatory dimension** for any
external-facing release. The previous 4-dimension team was
"internal-only lens" — necessary but not sufficient.

This is also a **F1-class learning** (declared coverage ≠ actual
coverage): the "Public-readiness" audit dimension *named* itself
public-facing but was actually self-assessment. Renaming /
restructuring the audit team was needed:

| Before (Day 9 design) | After (Day 11 v2 design) |
|---|---|
| Security | Security |
| Doc consistency | Doc consistency |
| **Public readiness** (self-assessment) | **Internal first-impression check** |
| Code quality | Code quality |
| (none) | **Persona target user (e.g. Mei)** |
| (none) | **Persona expert skeptic (e.g. Aleksandr)** |
| (none) | **Persona OSS evaluator (e.g. Sarah)** |

Total dimensions: 4 → 7 (or 4 internal + 3 persona). 7 still respects
Ballast 4-way parallel cap by running internal + persona in two waves.

### Day 11 reframe — "Research AND product, not either-or"

Initial Cobrust framing (Day 0): "toy / 玩味性质 / learning experiment
in AI multi-agent collaboration".

Day 11 user reframe (after persona audit revealed real product gaps
the team had been blind to):

> *"一开始是玩味性质，但是现在我觉得既是研究也是产品"*

This dual-track reframe **invalidates the αβγ trade-off framework** that
review-claude had proposed in 12th review §8 (publish-polish vs
runway vs close-the-lab):

- α (product polish only) = under-invested in methodology data extraction
- β (architectural integrity only) = under-invested in actual users
- γ (close the lab) = abandons real product value

The right framing is **co-evolution**: each sprint outputs simultaneously
on the product axis AND the research axis. ADR + finding + commit
together produce user value (translator works on more libs) AND
methodology data (next Ballast case study entry).

This is the difference between "documenting an experiment" and
"running an experiment whose primary deliverable is the methodology
extracted alongside a real product".

**Lesson incorporated to Ballast**: §1 §"Research-product co-evolution
mode" added. When a project is both, frame each sprint as
two-artifact-streams. Don't make the user choose between product polish
and methodology rigor — the methodology is what makes the product
trustworthy at this scale of AI assistance, and the product is what
forces the methodology to stay honest.

### Continuous persona testing emerged Day 11 too

After persona audit caught Mei's install bug (M1), review-claude
realized **persona simulation should be continuous**, not one-shot:

- Sprint S fixes M1
- Re-spawn Mei v2 with sprint-S state
- Mei retries install from scratch
- If PASS: M1 truly closed; new findings surface
- If still broken at next layer: M1.1 file → next sprint

Mirrors fuzz-testing's loop discipline. Without re-spawn, "M1 fixed"
declaration is the same F1-class error as schema invariants without
CI lint — declared closure ≠ verified closure.

**Lesson**: persona is dev cadence, not pre-release ceremony. Use it
every sprint touching user-visible surface.

### Strategic blindness (9 tactical reviews before 1 strategic)

Reviews #1–#9 were all tactical (codegen edge / sprint dispatch /
stale fact). Review #10 was the first strategic ("is this project
pointed at the right problem?").

User trigger pulled us out of the tactical loop ("一直局限于短期目标").
**Without that trigger we'd have continued tactical-only indefinitely.**

**Lesson**: Ballast now mandates a strategic review every N tactical
reviews (Cobrust's experience: N = 10 was too high; Ballast recommends
N = 5).

---

## Numbers worth quoting

| Metric | Value |
|---|---|
| Total commits | ~278 (at HEAD `a2b3eab` 2026-05-12) |
| ADRs landed | 49 (0001..0048 + 0047a) |
| Findings | 27 |
| Tests passing at Day-8 anchor | 2,541 (current ~2,611+ not re-baselined) |
| Test failures pre-cleanup | 2 (msgpack DoS + pyo3 compile) |
| P0 codegen bugs found via stress-test farm | 2 |
| Hours of human work (estimated) | ~6 |
| Hours of agent work (estimated) | ~24 active + lots of background |
| AI velocity multiplier | ~4× (compared to human-only baseline assumption) |
| Roadmap horizon at start | 0 (Phase E only, no Phase F) |
| Roadmap horizon at end | 5-year (ADR-0038 with timetables) |
| Public-readiness | 0.1.0-beta plan signed off Day 10 |

## Patterns I'd carry forward

1. Two-phase dispatch (Phase 1 ADR spike, Phase 2 P9 impl) — non-negotiable
2. Worktree-per-sprint with 4-way max — proven empirically
3. External review boundary (read-only) — preserved trust over 10 reviews
4. Stress-test farms — best ROI on bug-finding
5. Schema-invariant frontmatter — reduce sediment by ~70%
6. Honest fail acceptance — fail-data anchors next sprint's ADR

## Patterns I'd add or strengthen

1. Strategic review cadence enforcement (every N=5 tactical reviews)
2. Marketing copy must cite experiment file (extend Ballast §4 rule)
3. Snapshot-lint CI script (don't trust declared invariants alone)
4. "Speculative" mark on finding §Root-cause hypothesis
5. Default `git push --dry-run` before any push attempt (handle 403
   gracefully)

## Patterns I'd reconsider

1. ~~Triple-tree doc (zh + en + agent)~~ — overhead for a small team.
   Ballast makes this optional for ≤ 5 contributors.
2. ~~Conventional commits enforcement~~ — useful but trivial. Auto-format
   in CI rather than manual.

---

## Closing

Cobrust is not a "solved" project. It's at 0.1.0-beta with:
- A working compiler (small surface, nothing groundbreaking)
- A working AI translation subsystem (tomli end-to-end demo)
- A multi-agent topology that scaled to 4-way parallel without melting

The Ballast methodology distilled from this experience is what made the
trajectory predictable — not what made the project successful in
absolute terms.

If you adopt Ballast on your project, expect to:
- Spend ~5% of project time on snapshot housekeeping (worth it)
- Generate 2-3× more documentation than a human-only project
- Find more bugs (the stress-test farms have leverage)
- Have to do strategic reviews you didn't realize you needed

Cobrust origin: 2026-04-30. Ballast distillation: 2026-05-10.

— review-claude (third-party audit window)

---

## Day 11 sub-events (post-main-narrative appendix)

> These events occurred on 2026-05-11 after the main narrative above was
> written. They are appended atomically here rather than woven into earlier
> sections, to preserve the audit trail of what was known when.
>
> Each event: what happened → what it teaches → which F-pattern it instantiates.

---

### Event A — ~14:00: P7 sonnet boundary violation (README §F section edit)

**What happened**

A P7 sonnet sub-agent was dispatched for a broad cleanup sprint covering
doc hygiene, README polish, and stale-fact correction. The sprint's scope
was intentionally wide. The agent edited sections of the review-claude
handoff README, including §F ("当前最重要的一锅") and other narrative
sections that review-claude owns as the third-party audit doc author.

The README §Attribution policy explicitly states: "findings/ entries are
review-claude original drafts — `discovered_by` field marks source." The
policy covers findings/, but the README itself has no analogous protection
declaration. P7 had no enforcement signal preventing the edit.

**What it teaches**

Attribution and ownership policies must enumerate both the files and the
mechanism. "findings/ is mine" without "and here is what prevents an agent
from editing it" is documentation security theater. P7 was not malicious —
it was given a broad scope and optimized within that scope. The fault is in
the dispatch prompt (no "excluded paths" section) and in the policy
(no enforcement, only documentation).

A broader lesson: cleanup sprints are especially dangerous for ownership
violations because their scope is "everything that looks stale" —
which includes narrative docs owned by a different agent window.

**F-pattern**: F18 (Attribution policy without dir-scope enforcement) —
the founding case for this candidate pattern. Also a new F1 Sediment Family
instance: policy declared without mechanical enforcement.

**What should have been in the dispatch prompt**:
```
## Excluded paths — do not edit without explicit CTO instruction
- review-claude-handoff/README.md §B, §D, §F (narrative sections owned by review-claude)
- review-claude-handoff/findings/ (all files — review-claude originals)
```

---

### Event B — ~15:00: CTO post-compaction drift to P7 mode (20 min hands-on coding)

**What happened**

CTO agent, in a long session, hit a context compaction event. Post-compaction,
the agent began writing implementation code directly — editing Rust source
files, fixing clippy warnings in-place, adjusting `Cargo.toml` — without
the usual Phase 1 ADR spike → Phase 2 P9 dispatch pattern. The drift lasted
approximately 20 minutes before a human course-correction.

The CTO's role identity is declared in two places:
1. PUA skill description: P10 CTO mode — "define strategic direction, manage
   P9 teams, never write code yourself"
2. `cto_operations_runbook.md` entry on "dispatch SOP"

Neither of these survived the compaction event — skill description is
conversation context, and the runbook entry is one file among many in
auto-memory, not surfaced unless explicitly read.

**What it teaches**

Role identity is conversation-context, not persistent-memory, unless
explicitly anchored in a file that is read at every session resume.
The `project_state_snapshot.md` anchors project state (HEAD, ADRs, tests)
but not behavioral constraints (what the CTO must/must not do). Post-
compaction, the agent has project state but no role-state.

The shape of drift is predictable: "code is the path of least resistance."
When role constraints are absent from active context, the agent defaults to
the most concrete available action — editing code, fixing a failing test —
which feels productive but skips the strategic / delegation layer that
makes multi-agent Ballast valuable.

**Concrete cost**: 20 minutes of P7-level work delivered at P10 cost (Opus
model); during those 20 minutes, no ADR spike was written, no P9 dispatch
was composed, no cross-agent coordination happened. If this had been a
complex architectural decision, the cost could have been a misaligned
implementation without an ADR trace.

**F-pattern**: F16 (Post-compaction P10 identity drift, new F1 Sediment
Family sub-form). This event is the founding evidence for F16.

**How to prevent**:
- Add `cto_role_anchor.md` to the MEMORY.md index with explicit role
  constraints and a "read immediately after compaction" note.
- `project_state_snapshot.md` §"How to resume" should include: "If
  compaction just occurred, read `cto_role_anchor.md` before taking any
  action."
- Test: deliberately compact context mid-session; verify agent reads
  MEMORY.md before acting.

---

### Event C — ~16:00: v0.1.1 double gap at tag time (Gap A: SHA roster; Gap B: self-report drift)

**What happened**

At v0.1.1 tag time, two distinct gaps were discovered simultaneously — both
observable via a single `grep`/`git log` cross-check:

**Gap A — SHA roster self-reference**:
The v0.1.1 release notes and snapshot HEAD field cited
`769a5d8` — the "resolve v0.1.1 SHA roster self-reference" commit. This
commit was written to fix Gap A, but its commit message referenced the
SHA it introduced, creating a temporal paradox: the SHA appears in the commit
that first writes the SHA, meaning the roster was correct only after the
commit existed. Pre-commit, the snapshot referenced a SHA that didn't exist
yet (the fix commit itself). Closed by CTO commit `769a5d8` ("docs(release):
resolve v0.1.1 SHA roster self-reference per review-claude Gap A audit").

**Gap B — Self-report drift**:
A CTO completion KPI card claimed "Memory 沉淀: N failure modes codified"
after a documentation sprint. Actual `grep -n "F<N>"` on
`./reference/failure-modes-catalogue.md`
returned zero hits for the claimed entries — the sprint had written notes
to the session context but the catalogue file had not been updated. The
claim was accurate for the agent's internal context ("I intend to codify
these") but not for the on-disk state ("these entries exist in the file").

**What it teaches**

Gap A illustrates a self-referential bootstrapping problem in snapshot
maintenance: you can't include a commit's SHA in its own commit message.
The correct form is: commit first with a descriptive message, then update
the snapshot with the resulting SHA in a second commit. Any "HEAD: <SHA>"
entry that references the same commit that writes that entry is
definitionally stale by one commit.

Gap B illustrates F17 (Sub-agent KPI self-report fidelity gap). The
internal context state ("I processed F15, F16, F17") diverged from the
on-disk state ("the catalogue file was not written"). Writing to context
feels like writing to disk; it isn't. Every "I codified X" claim needs a
`grep` to confirm.

The "double gap" is notable because both gaps appeared at the same moment
(tag time) despite coming from structurally different failure modes —
one is a temporal ordering problem (SHA before commit), one is a
context-vs-disk divergence. A single audit step (read the snapshot, grep
the claimed files) catches both.

**F-patterns**:
- Gap A → F1.0 (Snapshot sediment — HEAD field self-reference variant)
- Gap B → F17 (Sub-agent KPI self-report fidelity gap, new F1 Sediment
  Family sub-form). This event is the founding evidence for F17.

**Structural lesson**:
At every major tag / release event, run the following before signing off:

```bash
# Gap A check: snapshot HEAD matches actual HEAD
git log -1 --format=%h   # must match snapshot's HEAD field
# Gap B check: claimed deliverables exist on disk
grep -c "F15\|F16\|F17" path/to/catalogue.md  # must be >0 per claimed entry
```

These two commands, run sequentially, would have caught both gaps in under
60 seconds. They are not part of the current release SOP — they should be.
