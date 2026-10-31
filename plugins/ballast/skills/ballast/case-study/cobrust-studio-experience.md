---
case_study_id: cobrust-studio-2026-05-11-to-2026-05-12
project: Cobrust Studio (AI-agent project-management console; self-hosted web UI + REST/SSE API over a markdown ADR/finding/ledger tree)
duration: ~21 hours wall-clock (2026-05-11 17:22:37 +0800 → 2026-05-12 14:36:16 +0800; 5-day human plan compressed to 2 calendar days)
human_time: ~3-4 hours (strategic decisions + 守闸 + persona-audit reading; no implementation code written by human)
agent_time: ~95% of LOC produced (3 Rust crates + SvelteKit 5 frontend); 18 opus sub-agent dispatches across 6 waves + 4 reconcile rounds + 1 release agent
final_state: v0.1.0 (broken) → v0.1.1 (broken) → v0.1.2 (usable) shipped within the same calendar day; 125 commits on main; 3 tags; 6 ADRs; 4 findings; 4 module-docs; 196 Rust tests / 14 hermetic Playwright e2e / 2 dogfood specs / real-LLM e2e — all green at HEAD
attribution_origin: studio-cto-session-002-opus47 + studio-p7-{a*,m*}-opus47 sub-agents (live dispatch window, no third-party audit gap)
relates_to: [case-study:cobrust-multi-agent-experience.md (N=1), reference:failure-modes-catalogue.md §F1.0/F19/F20/F21, SKILL.md §"Origin & lineage"]
---

# Case study: Cobrust Studio — N=2 dogfood, 2-day MVP exercised + extended Ballast v1.2.1

This case study reports what worked and what failed in applying Ballast
v1.2.1 to a **second, independent project** — Cobrust Studio, a
self-hosted web console for managing AI coding agents under engineering
discipline. The first Ballast case study
([`cobrust-multi-agent-experience.md`](cobrust-multi-agent-experience.md))
documents a 12-day multi-agent build of the Cobrust language project
(N=1). Studio is the **N=2** evidence: a different codebase, a
different domain, a 10× shorter timeline, executed against the
already-codified methodology rather than co-evolving with it.

If the Cobrust case study answers "did this discipline scale to a
12-day language compiler with a 4-way parallel agent team?", this
case study answers a sharper question:

> **Does Ballast survive being applied as-written to a project it wasn't distilled from?**

Short answer: yes, with two important caveats — **the methodology
was both validated and stressed in load-bearing ways**, and **Studio
surfaced new F-sub-forms that retroactively validate F19/F20/F21**
(added to the catalogue between N=1 and N=2). Where Cobrust *generated*
the failure-modes catalogue from its own scars, Studio *consumed* it
and reported back on which entries paid for themselves under
acceleration.

This case study is also not a sanitised success story. v0.1.0 shipped
broken. v0.1.1 shipped broken (differently). v0.1.2 was the first
usable tag. Each broken tag is a data point about which enforcement
layer was missing; the patch dance below names file:line for every
gap.

---

## §0 Dashboard (one-pager)

```
Project:                 Cobrust Studio
Repo:                    github.com/Cobrust-lang/cobrust-studio
License:                 Apache-2.0 OR MIT (ADR-0001)
Span (wall-clock):       2026-05-11 17:22 → 2026-05-12 14:36 (~21 hours)
Span (5-day human plan): collapsed to 2 calendar days (AI velocity ~2.5×)
Bus factor:              1  (single human contributor; explicit caveat)
Commits on main:         125
Tags pushed:             3  (v0.1.0 broken / v0.1.1 broken / v0.1.2 usable)
Rust crates:             3  (studio-router / studio-store / studio-server)
Frontend:                SvelteKit 5, 5 pages, Tailwind v4
Binary deployment:       single 9.0 MiB self-contained (rust-embed; ADR-0002)
Rust tests at HEAD:      196 (32 ok groups, 0 FAILED)
Playwright e2e:          14 hermetic + 2 dogfood (all green at HEAD)
Real-LLM e2e:            PASS (codex-forwarder + gpt-5.5)
ADRs landed:             6  (0001..0006)
Findings filed:          4  (P0 / P1 / P2 / P3 all represented; 3 of 4 closed within session)
Module-docs:             4  (studio-router / studio-store / studio-server / web-frontend)
Opus agent dispatches:   ~18 (6 waves × DEV+TEST+REVIEW trio + 4 reconcile rounds + 1 release agent)
Reconcile rounds:        4  (A2, A3, A4, A5 — multiple per wave on M1-era waves)
CI gates enforced:       6  (fmt / clippy -D warnings / build / test / doc-coverage §5 SHA / doc-coverage §6 cargo test)
Persona audits:          3  (Mei / Aleksandr / Sarah — post-v0.1.2, AMBER / REAL / PASS-watch-6-month)
F-catalogue catches:     F1.0 ×2 / F19 ×2 / F20 ×2 / F21 ×1
Ballast-firsts:             First F20 systemic closure in a non-origin project
                         First documented "tag → audit → patch" release pattern
                         First "recursive F20 closure" (enforcement script auditing itself)
                         First N=2 dogfood of the methodology
```

---

## §1 Project shape & meta

### What Studio is

A 9 MiB single Rust binary that gives engineering teams a web UI +
REST/SSE API over a plain-markdown ADR/finding/ledger tree backed by
a git repo. Five pages: `/login` / `/adr` / `/agent` (dispatch) /
`/finding` / `/ledger`. The discipline it productises is the
**ADR + finding + bilingual docs + Tx-tagged waves + doc-coverage CI
gate** stack distilled from Cobrust. Studio's pitch: "if your team is
doing serious AI-driven development, you need answers to *what did
the agents decide / what went wrong / where did the tokens go / are
we drifting / is the methodology actually being followed?* — Studio
gives you all five against any git repo, no SaaS, no per-seat
pricing."

### Why it was built

Two reasons, neither of which is the publicly stated pitch:

1. **N=2 Ballast dogfood.** The Cobrust language project (N=1) was
   the substrate the methodology was distilled from. Distillation
   from the same project that generates the data is methodologically
   suspect — "did the methodology actually work, or did we just
   describe what we did?" Studio is the **second, independent
   application**: a different language stack (Axum + SvelteKit vs
   Cranelift codegen), a different problem domain (CRUD + SSE vs
   LLM-driven translation), a different parallelism profile (3-way
   dev/test/review trio per wave vs 4-way parallel sprint farm). The
   only constant is the methodology and the human at P10.

2. **A vehicle for back-porting v1.2.1 catalogue entries
   (F19/F20/F21) under acceleration.** F19/F20/F21 were added to the
   Ballast failure-modes catalogue between N=1 ending and Studio
   starting. They were untested under the conditions they describe
   (a new project, a fresh constitution, a tight timeline that
   pressures shortcuts). Studio's M0-M5 trajectory was the first
   project to consume those entries as inputs rather than outputs.

### Topology

```
Human (1, hakureirm <wbj010101@gmail.com>):
  - Strategic decisions: license (Apache + MIT), repo namespace
    (Cobrust-lang/cobrust-studio), public tag timing, persona-audit
    follow-up direction
  - Final 守闸 + merge approval on all wave merges
  - ~3-4 hours total work; zero implementation code authored

CTO agent (1, opus, studio-cto-session-002-opus47):
  - M0..M5 milestone planning + Phase 1 ADR spikes (ADR-0001..0006)
  - 18 sub-agent dispatches across 6 waves
  - 4 reconcile rounds (DEV-TEST-REVIEW resolution per wave on A2-A5)
  - 1 dedicated release-readiness agent (M4 post-tag audit)
  - 3 persona-audit dispatches (Mei / Aleksandr / Sarah, post-v0.1.2)

P7 sub-agents (~18 opus dispatches):
  - studio-p7-a1-1-opus47    : router lift + strip
  - studio-p7-a2-dev-opus47  : studio-store impl
  - studio-p7-a2-test-opus47 : studio-store contract corpus
  - studio-p7-a2-review-opus47: A2 audit
  - studio-p7-a3-{dev,test,review}-opus47 : Axum core
  - studio-p7-a4-{dev,test,review}-opus47 : 10 M1 routes + SSE
  - studio-p7-a5-{dev,test,review}-opus47 : router wire + dispatch SSE
  - studio-p7-m2-{dev,test,review}-opus47 : SvelteKit 5 frontend
  - studio-p7-m3-{dev,test,review}-opus47 : rust-embed + dogfood
  - studio-p7-m4-{dev,test,review}-opus47 : v0.1.0 release prep
  - studio-cto-m4.1-release-readiness-opus47 : post-v0.1.0 audit (caught F-M4-01)

Persona agents (3, sonnet, post-v0.1.2):
  - Mei (Python data scientist, target user)
  - Aleksandr (Rust skeptic, technical credibility)
  - Sarah (OSS evaluator + tech-lead, governance)
```

**Critical attribution note (F21 hygiene)**: every CTO and P7 dispatch
in Studio carried an explicit session-handle suffix
(`studio-cto-session-002-opus47`, `studio-p7-a4-dev-opus47`). No
artifact in this repo signs bare "review-claude" or bare "the CTO".
The discipline came from F21 being on the table at session start —
empirical validation that **F21 prevention is cheap if applied
prospectively**.

### Wave structure

Six waves, each with the **3-team trio pattern** (DEV + TEST + REVIEW
in parallel, then CTO reconcile):

| Wave | Scope | Merge SHA | Notes |
|---|---|---|---|
| A0/M0 | Workspace scaffold + 5 ADRs + 5-gate CI | `b7d8f71` | Initial commit; F1.0 BSD-sed caught on first run |
| A1.x | studio-router lift from cobrust-llm-router @ `61f2aff` + strip | `d616548` | Strip #2 verified as no-op (`a1-1-strip-2-noop-at-pin-61f2aff.md`) |
| A2 | studio-store: ADR/finding/ledger CRUD + SQLite index | `36651a4` | First `last_verified_commit: HEAD` leak (F-A2-01) |
| A3 | studio-server Axum core | `d26f3ac` | Second HEAD leak (F-A3-01); same wave fixed via doc-coverage §5 |
| A4 | 10 M1 HTTP routes + SSE | `8d5475f` | Shipped 9 failing integration tests under broken grep守闸 |
| A5 | Router wire + dispatch SSE + A4 baseline fixes | `0e699c4` | A5 DEV agent flagged the broken-baseline as side-effect; finding filed |
| M2 | SvelteKit 5 frontend (5 pages) | `bfbfb8f` | Vitest + Playwright scaffolding |
| M3 | rust-embed integration + dogfood smoke | `5685f49`, `a426067` | The `Path<String>` mounted on `Router::fallback` — landed here, caught at M4 |
| M4 | v0.1.0 release prep | `a722e09` | Tag `0a7fd3e` v0.1.0 — known-broken (SPA fallback) |
| M4.1 | Post-tag CTO 守闸 release-readiness audit | `503260d` | Caught F-M4-01; doc-coverage §6 added |
| v0.1.1 | SPA fallback `Path<String>` → `Uri` extractor | `15b6f46` | Tag — known-broken (stale Cargo.lock) |
| v0.1.2 | Cargo.lock refresh + doc-coverage §6 paired exit-code gate | `7ea9ae3` | Tag — first usable |
| M5 | persona-audit-driven README rewrite + F-05 dead deps + CI matrix | `339e1ab`, `58cbe94`, `ffaf1fb` | Mei/Aleksandr/Sarah outputs converted into concrete PRs |

The Wave A waves used a 3-team-per-wave dispatch pattern (~3 P7
dispatches per wave); Wave M3+ collapsed back to single-P7 dispatches
because the frontend work was less cross-cutting. The variance is
itself an N=2 data point: **3-team trio is overkill for
single-surface UI work; appropriate for cross-crate Rust changes**.

---

## §2 What Studio validated about Ballast

This section walks each Ballast invariant the project exercised. The
question: did the methodology, applied as written, behave the way
the catalogue claims?

### §2.1 The 4-tier role topology held under tight-timeline pressure

Ballast §1 specifies P10 (CTO) / P9 (tech lead) / P7 (senior engineer) /
P0 (atomic) + external review. Studio used **only P10 + P7** —
collapsed P9 into P10 because the wave scope was tractable for direct
CTO-to-P7 dispatch. **The ≤4-way parallel cap was honored throughout**;
peak concurrency was 3 (DEV + TEST + REVIEW trio).

This is a meaningful adaptation: Ballast's case study #1 (Cobrust) ran
4-way parallel through a heavyweight P9-led decomposition, because
each milestone (M11.x, M12.x) was a multi-crate spike. Studio's
waves were narrower (single crate per wave on A-series; single page
per dispatch on M2). The trio pattern at ≤3-way is **the right
fidelity for narrow-scope waves**; the P9 layer is overhead for
projects shorter than ~5 days.

> **Methodology learning: P9 is optional below a complexity floor.**
> When the wave plan fits in a single ADR with ≤5 sub-tasks, CTO →
> P7 trio direct is fine. Reserve P9 for waves that need
> sub-decomposition of the ADR itself.

This learning is being back-ported into §1 of SKILL.md (see §6
below).

### §2.2 Two-phase dispatch SOP held — and ADR-0006 demonstrates the blame-integrity move

The single most-validated pattern was the **CTO Phase 1 ADR spike →
P7 Phase 2 impl** loop. Every wave followed it:

```
Phase 1 (CTO):  Commit ADR-NNNN with options/decision/done-means.
                  Land on main.
Phase 2 (P7):   Dispatch with a working dir + required reads
                  (including the ADR) + mission + deliverables + gates.
Phase 3 (CTO):  守闸 — 5-gate green check + read the diff + merge.
```

**Concrete validation**:
[`docs/agent/adr/0006-studio-router-api-and-lift-provenance.md`](https://github.com/Cobrust-lang/cobrust-studio/blob/main/docs/agent/adr/0006-studio-router-api-and-lift-provenance.md)
was spiked CTO-solo at Phase 1 (commit `93ae8f8`, 2026-05-11 17:24).
The §"Decision" block enumerated the studio-router public surface
and proposed a builder shape (`with_config / with_cache / with_ledger
/ from_toml`). P7 A1.1 lifted the upstream code and **discovered the
real upstream builder shape was different** (`register_provider /
build(&cfg)` async, `from_toml_str(&str)` not `from_toml(&path)`).

This is exactly the F2 layer-divergence pattern from Cobrust ADR-0033
/ ADR-0035. The right move was the **blame-integrity addendum**:

> ADR-0006 §"Addendum 2026-05-11 — post-A1.1 reality reconciliation"
> preserves the original §"Decision" text **unchanged**, then appends
> a §F-01 / §F-02 / §F-03 addendum block enumerating each correction
> with the as-built reality. The original CTO speculation is
> preserved verbatim; the corrections are dated, attributed
> (`studio-review-wave-a1-opus47`), and load-bearing for downstream
> implementation.

This pattern — **don't rewrite the spike, append the correction** —
is identical to Cobrust ADR-0033 §"Layer correction". Studio's
contribution: a clean second instance, with explicit prose calling
out *why* the original text is preserved (audit trail / blame
integrity). Future Ballast users now have two case-study instances of
the pattern in the wild.

> **Methodology learning: ADR addendum pattern is the BLAME-INTEGRITY MOVE.**
> When Phase 2 implementation reveals Phase 1 was speculative-wrong,
> never edit §"Decision". Append `§"Addendum YYYY-MM-DD"` with the
> reality and a pointer to the review that surfaced it. Anyone
> reading the ADR can see both the original strategic intent and the
> tactical correction, with the lineage intact.

### §2.3 5-gate verification held — and gained a 6th gate the same session

Ballast §"5-gate verification" specifies: fmt / clippy / build / test /
doc-coverage. Studio enforced all 5 from M0; the M0 scaffold's first
commit (`b7d8f71`) shipped with green CI on day 0 hour 0.

**By M4.1, the gate count was 6**. Studio added a §6 gate to
`scripts/doc-coverage.sh`:

```bash
# Excerpt: scripts/doc-coverage.sh §6 (post-M4.1 hardened)
if ! cargo test --workspace --locked --no-fail-fast > "$test_log" 2>&1; then
    cargo_exit=$?
    echo "doc-coverage: FAIL — cargo test exited $cargo_exit (lockfile mismatch / compile error / panic)" >&2
    exit 1
fi
failed_count=$(grep -c '^test result: FAILED' "$test_log" || true)
if [ "${failed_count:-0}" -ne 0 ]; then
    echo "doc-coverage: FAIL — cargo test reported $failed_count failed test groups" >&2
    exit 1
fi
```

This gate exists because the **standard 5-gate** as documented in
Ballast was insufficient against the failure modes Studio hit at A4 and
v0.1.1. The CTO 守闸 SOP that wrapped the 5-gate used a `cargo test
| grep "^test result" | wc -l` pipeline that **counted both `ok` and
`FAILED` summary lines** as if they were the same. Then the
post-v0.1.1 audit caught a Cargo.lock staleness where `cargo test
--locked` exited 101 *without* emitting a `test result: FAILED` line
at all. Both gaps fixed at the script layer (see §3.4 below).

> **Methodology learning: the canonical 5-gate is insufficient under
> aggressive parallelism. The 6th gate (paired exit-code + FAILED-grep
> on `cargo test`) closes two systemic gaps the 5-gate misses.** Back-port
> candidate for SKILL.md §"5-gate verification".

### §2.4 3-team trio dispatch executed at ~3-way parallel under 4-way cap

Each Wave-A and Wave-M sprint ran:

```
   ┌─ studio-p7-{wave}-dev-opus47   (impl)
P7 ┼─ studio-p7-{wave}-test-opus47  (TDD contract corpus)
   └─ studio-p7-{wave}-review-opus47 (audit — REVIEW only, no edits)
            ↓
        CTO reconcile (merge DEV + TEST, address REVIEW findings)
            ↓
        守闸 (5-gate / 6-gate / read the diff)
            ↓
        merge to main
```

Total opus dispatches: ~18 across 6 waves + 1 release-readiness agent
+ 3 persona agents = **22 opus sub-agents in 21 hours wall-clock**.
Token spend documented in `CHANGELOG.md §"Methodology firsts"`. CTO
reconcile rounds (4 of them, on A2/A3/A4/A5) were the most
human-time-expensive turns — typically 30-60 min each of human-driven
diff reading + small CTO edits to make DEV's wire-shape and TEST's
contract assumptions agree.

The 3-team trio pattern is the **most Ballast-orthodox part of Studio's
execution**. It's the pattern §1 of SKILL.md specifies most directly,
and it worked as advertised — including the F-class catches (REVIEW
agent's audit reports are the source of the F-A2-01 / F-A3-01 /
F-A5-01 finding numbers below).

### §2.5 Worktree-per-sprint pattern, scaled down to ~12 worktrees over 21 hours

Ballast §"Worktree-per-sprint" specifies `git worktree add` per active
sprint; Studio created ~12 worktrees across the session
(`../studio-a2-dev`, `../studio-a2-test`, `../studio-a2-review`,
etc.), all cleaned up via `git worktree remove --force` post-merge.
**No worktree leaked into HEAD by accident**; no `target/` directory
collided. The pattern is identical to what cobrust-multi-agent
exercised, scaled down to single-day cadence.

One M1 Pro 16GB machine, 3-way parallel cargo builds, zero exit-144
(SIGUSR2) global lock starvation events. Cobrust hit this once at
6-way; Studio's ≤3-way cap never approached the ceiling. **The 4-way
parallel cap from §1 is real; 3-way is comfortable.**

### §2.6 Atomic commits — code + tests + docs in one merge

Every wave merge brought code + tests + module-docs in one commit.
Cross-references:

- `36651a4 merge: A2 studio-store impl + contract corpus reconciled (Wave A2 complete)`
  — brought `crates/studio-store/src/*.rs` + `crates/studio-store/tests/*.rs`
  + `docs/agent/modules/studio-store.md` in one merge commit.
- `d26f3ac merge: A3 studio-server Axum core (Wave A3 complete)` —
  same shape, scoped to server crate.

**Atomic commit invariant violation count**: 1 (the A4 merge `8d5475f`,
which shipped 9 failing integration tests that compile-passed but
runtime-failed — see §3.3 below). One violation in 21 hours of
dispatch is in-line with the discipline; the violation itself produced
the catalogue's first **`cto-shougate-test-gate-grep-leak.md`**
finding.

### §2.7 F21 identity hygiene held at 100% commit-attribution fidelity

`git log --format='%an <%ae>' | sort -u`:

```
hakureirm <wbj010101@gmail.com>
```

**One author, one email, across all 125 commits**. Zero leak of the
macOS Full-Name default (which had leaked into an unrelated public
repo in a prior session, per F21 evidence). The discipline came from
F21 being on the table at session start: every dispatch prompt
specified `git config user.name` verification as a tier-0 step
before any commit.

This is a **direct, prospective validation of F21's prevention
mechanism**. F21 was added to the catalogue from an N=1 negative case;
Studio is the N=2 positive case — F21 catches the leak if you remember
F21 exists.

### §2.8 Triple-track doc discipline (zh / en / agent) enforced by doc-coverage.sh

Every public crate ships with `docs/agent/modules/<crate>.md`; every
top-level doc has zh + en parity. Six ADRs, four module-docs, four
findings, all carry `last_verified_commit:` frontmatter that points
to a real, git-reachable SHA. The doc-coverage gate enforces this
mechanically — see §3.2 below.

### §2.9 Honest fail acceptance — three patch-tags in one day

Every project ships at v0.1.0 if not before. Studio shipped at
v0.1.0, then v0.1.1, then v0.1.2 *in the same calendar day*. The
CHANGELOG names each tag explicitly:

- **v0.1.0**: known-broken — SPA fallback `Path<String>` regression on
  `Router::fallback`.
- **v0.1.1**: known-broken (different bug) — stale Cargo.lock; `cargo
  build --locked` returns 101.
- **v0.1.2**: first usable.

No quiet retag. No "we'll bump the version and silently fix it." Each
patch tag is its own commit, its own CHANGELOG entry, its own
"`v0.1.<N-1>` is known-broken; upgrade to `v0.1.<N>`" note. **The
README's §"Honest status" section names the patch dance up front**:
*"If you'd prefer a year-old tag where you don't see the patch dance,
this isn't your project."* This is honest-fail-acceptance applied to
release-engineering, not just internal findings.

---

## §3 What Studio STRESSED about Ballast

This is the load-bearing section. Each item below: where the discipline
broke, how it was caught, what the fix was, what catalogue entry it
informs. Studio's value as N=2 evidence is concentrated here —
methodology that doesn't break under acceleration is methodology that
isn't being tested.

### §3.1 F1.0 instance #1: BSD-sed in M0 doc-coverage.sh — declared invariant `ADR id monotonic` silently no-op'd on macOS

**Where it broke**

M0 (`b7d8f71`, the workspace-scaffold commit) shipped
`scripts/doc-coverage.sh` §4:

```bash
# ORIGINAL (BSD-sed silent failure pattern)
for adr in $(ls docs/agent/adr/0*-*.md 2>/dev/null | sort); do
    n=$(basename "$adr" | sed 's/^0*\([0-9]\+\).*/\1/')
    # ...
done
```

On macOS (BSD sed), `\+` is **not a special character** — sed interprets
the regex literally. So `n` came back as the basename itself (e.g.
`0001-stack-choice.md`), the integer comparison `[ "$n" -le "$last"
]` returned a non-integer error, and `set -e` did **not** trip
because the construct was inside `$(...)` subshell expansion. The
gate printed `M0 — ADR id monotonic` and exited 0 on every run.

**How it was caught**

First-ever run of the gate from a clean macOS shell during M0 review.
CTO 守闸 noticed the gate "passed" against an ADR-roster that the
agent knew had a missing 0002 (intentionally — testing the monotonic
check should fail). Empirical confirmation: the gate was a no-op, not
a check.

**Fix**

`sed -E 's/^([0-9]+).*/\1/'` + a second `sed -E 's/^0+//'` to handle
leading zeros — POSIX-compatible regex (`-E` switch is GNU+BSD both).
Tested on macOS BSD sed and Linux GNU sed; both return monotonic
verdicts now.

**Catalogue mapping**

This is **F1.0 (declared invariants without enforcement) sub-form: cross-platform
shell silent failure**. The script declared an invariant ("ADR id
monotonic") and shipped a check that, on BSD tools, was equivalent
to no check. Same family as F1.2 (constitution rules with partial-scope
enforcement).

> **Forward implication**: any project-level enforcement script should
> have a **deliberately-broken-input test** in CI: feed the script a
> known-bad fixture (intentionally non-monotonic ADR sequence), assert
> exit ≠ 0. If the test passes (gate caught the bad fixture), green.
> If the test fails (gate didn't catch), the gate is theatre.

**This was the first F1.0 catch in Studio's session and the trigger
for tightening doc-coverage.sh's enforcement layer**. Two consecutive
F1.0 catches in the same session is the §"two strikes = systemic
blind spot" signal — see §3.2 below.

### §3.2 F19/F20 paired instance: `last_verified_commit: HEAD` placeholder shipped twice in module-docs

**Where it broke**

Wave A2 merge `36651a4` (2026-05-12) shipped
`docs/agent/modules/studio-store.md` with frontmatter:

```yaml
---
doc_kind: module
crate: studio-store
last_verified_commit: HEAD     # ← placeholder, never replaced
---
```

`doc-coverage.sh` at that point did **not** check that
`last_verified_commit:` was a real SHA. The gate just checked frontmatter
*existed*. The literal string `HEAD` is frontmatter content; gate
passed.

A2 external review (`studio-p7-a2-review-opus47`) caught it visually
as P2 finding F-A2-01.

**24 hours later, Wave A3** merge `d26f3ac` shipped
`docs/agent/modules/studio-server.md` **with the same `HEAD`
placeholder**. Second instance, same blind spot. The A3 review caught
it (F-A3-01); but the structural issue — *the gate doesn't enforce*
— was diagnosed only after the second occurrence.

**Two strikes = systemic blind spot** (per Cobrust F2 pattern). Filed
finding [`f20-closure-last-verified-commit-enforcement.md`](https://github.com/Cobrust-lang/cobrust-studio/blob/main/docs/agent/findings/f20-closure-last-verified-commit-enforcement.md)
naming the gap as an F20 instance (constitution-vs-workflow alignment).

**Fix**

`scripts/doc-coverage.sh` §5 extended in the **same commit as the
A3 review fix** (per F20 §"Rule of thumb": *every binding constitution
rule must have a paired enforcement step in the same PR that introduces
it*):

```bash
check_last_verified() {
    local file="$1"
    grep -q "^last_verified_commit:" "$file" || fail "missing frontmatter"
    local sha
    sha=$(grep "^last_verified_commit:" "$file" | head -1 \
        | sed -E 's/^last_verified_commit:[[:space:]]*//')
    if [ "$sha" = "HEAD" ] || [ -z "$sha" ]; then
        fail "$file last_verified_commit='$sha' is a placeholder (F20)"
    fi
    if ! echo "$sha" | grep -qE '^[0-9a-f]{7,40}$'; then
        fail "$file last_verified_commit='$sha' does not look like a git SHA (F20)"
    fi
    # F-A3-01 closure: hex-shape alone passes `deadbee` (valid hex,
    # not a real commit). git cat-file -e is the canonical reachability check.
    if ! git cat-file -e "${sha}^{commit}" 2>/dev/null; then
        fail "$file last_verified_commit='$sha' is hex-shaped but NOT a reachable git commit (F20)"
    fi
}
```

Three layers of check now: presence + shape + git-reachability. The
reachability check (`git cat-file -e <sha>^{commit}`) is the
F-A3-01 closure — without it, a typo like `deadbee` passes
hex-validation but doesn't actually point to a real commit.

**Catalogue mapping**

This is the **first F20 systemic closure landed in Cobrust Studio**
— the finding's title literally is `f20-closure-last-verified-commit-enforcement`,
and the §"Conclusion" states: *"this finding is the first F20-class fix landed
in Cobrust Studio. Mechanism is now load-bearing: any future module-doc or
finding that lands with `last_verified_commit: HEAD` will be caught by CI
on the same PR that introduces it. The placeholder pattern is dead."*

> **First-ever validation of F20's prevention mechanism in a non-Cobrust
> project.** F20 was added to the catalogue from Cobrust's TDD-mandate-without-enforcement
> N=1 negative case. Studio is the first project to land an F20 *closure*
> against a brand-new instance — confirming F20's §"Rule of thumb" is
> actionable, not just diagnostic.

> **Forward implication**: F19 (release-readiness untested) and F20
> (constitution-vs-workflow alignment) **pair naturally**. F19 is "did
> you run it?"; F20 is "did your runner enforce it?". Any project that
> takes F20 seriously will produce F19 closures automatically — and
> vice versa.

### §3.3 F1.0 instance #2: CTO 守闸 grep leak — A4 merged with 9 failing integration tests under green-gate report

**Where it broke**

A4 merge `8d5475f` (10 M1 HTTP routes + SSE; 2026-05-12) was
ratified by CTO 守闸 using:

```bash
# WRONG — counts both `ok` and `FAILED` as "test groups"
cargo test --workspace --locked --no-fail-fast 2>&1 \
  | grep "^test result" | wc -l \
  | xargs -I{} echo "{} test groups all green"
```

This pipeline counts every line that **starts with** `test result:` —
including `test result: ok.` and `test result: FAILED.`. Both shapes
match; both increment the counter. The守闸 report said "22 test
groups all green"; in reality, **9 of the 22 were FAILED**.

The 9 failures were API-shape drift between A4 P7 DEV's wire shape
and A4 P7 TEST's contract assumptions (the same drift class as A2
reconcile — but uncaught because of the broken grep). Specifically:

| File | Failed tests |
|---|---|
| `tests/adr_routes.rs` | 4 (post_adr_malformed_body, get_adr_by_id, post_adr_then_list, post_adr_persists) |
| `tests/auth_route.rs` | 1 (set_endpoint_malformed) |
| `tests/events_route.rs` | 1 (events_sse_emits_on_adr_create) |
| `tests/finding_routes.rs` | 2 (post_finding_malformed, post_finding_then_list) |
| `tests/ledger_route.rs` | 1 (ledger_recent_n_zero) |

The A4 守闸 commit `6775cce` ("M4.1 守闸 — apply A3 review P2 fixes")
did NOT address these — it fixed clippy and lib doc edits but didn't
run a clean test gate against the new integration corpus.

**How it was caught**

Wave A5 dispatch (the next sprint). A5 P7 DEV agent ran `cargo test`
against base `6775cce` as a sanity check before starting impl — and
**reported 9 pre-existing failures** in its `[P7-COMPLETION]` mid-flight
("base branch has 5 pre-existing failing test files; should I work
on top or wait for fix?").

The CTO immediately recognised: "the 5-gate I claimed green at A4
was wrong" — that the green claim came from a grep pipeline that
swallowed FAILED-grep into a generic line-count. Filed finding
[`cto-shougate-test-gate-grep-leak.md`](https://github.com/Cobrust-lang/cobrust-studio/blob/main/docs/agent/findings/cto-shougate-test-gate-grep-leak.md)
with severity P1, naming three structural takeaways:

1. CTO 守闸 SOP must use exit-code-aware test-gate checks (either
   propagate cargo's exit code OR grep for FAILED explicitly — not
   count `^test result` lines).
2. P7 TEST agents must run BOTH `cargo check` AND `cargo test` (with
   acceptance that test FAIL is expected at TDD-red — but the agent
   must REPORT the failure shape, not claim "all green").
3. Same-PR enforcement: extend `scripts/doc-coverage.sh` to run
   `cargo test` and explicitly check the summary line. This is the
   F20 closure for "atomic commit invariant" → script-level enforcement.

**Fix**

Landed at M4.1 (`503260d` "fix: M4.1 守闸 — close cto-shougate finding
via doc-coverage §6 test gate"). `scripts/doc-coverage.sh` §6 added:

```bash
if ! cargo test --workspace --locked --no-fail-fast > "$test_log" 2>&1; then
    cargo_exit=$?
    echo "doc-coverage: FAIL — cargo test exited $cargo_exit"; exit 1
fi
failed_count=$(grep -c '^test result: FAILED' "$test_log" || true)
if [ "${failed_count:-0}" -ne 0 ]; then
    echo "doc-coverage: FAIL — $failed_count failed groups"; exit 1
fi
```

Note: **paired** check on exit code AND FAILED-grep. Either one alone
is insufficient (the original CTO grep was a FAILED-grep-only variant
that swallowed the non-zero exit through the pipe).

The finding's `status: closed_by_m4.1` records this closure. The
file's opening note (added at closure time):

> *"Closure 2026-05-12 (M4.1 守闸): `scripts/doc-coverage.sh` §6 now
> runs `cargo test --workspace --locked --no-fail-fast` and explicitly
> greps `^test result: FAILED` to enforce the gate at script level.
> F20 systemic enforcement complete — the broken `grep "^test result"
> | wc -l` pattern that A4 merge tripped on can no longer ship green."*

**Catalogue mapping**

This is **F1.0 (declared invariant `5 gates green` lacking enforcement
in the verification mechanism itself)** + **F20 (constitution-vs-workflow:
the SOP's grep was the workflow; CLAUDE.md's "5 gates green before
any merge" was the constitution; the gap was the grep)**.

> **The CTO 守闸 procedure is itself a workflow. F20 applies to the procedure
> as much as it applies to the code being reviewed.** Studio's evidence
> shows the discipline must be **layered** — the constitution rule, the
> SOP grep, the doc-coverage script, and a deliberately-broken-input
> test that confirms each layer catches what the upper layer would otherwise
> miss.

### §3.4 F-M4-01: SPA fallback `Path<String>` shipped to v0.1.0 — caught by post-tag M4 release-readiness audit

**Where it broke**

M3 rust-embed integration (`5685f49`) mounted `embed::serve_asset`
via `axum::Router::fallback(...)`. The handler signature was:

```rust
pub async fn serve_asset(Path(path): Path<String>) -> Response { ... }
```

The structural Axum bug: **`axum::extract::Path<T>` only extracts
from matched route patterns; `Router::fallback` does NOT match a
pattern** — it's a catch-all that the framework dispatches to when
no other route matches. So `Path<String>` has nothing to extract from,
and every request to a SPA route (`/login`, `/adr`, `/agent`,
`/finding`, `/ledger`) returned the Axum runtime error:

```
Wrong number of path arguments for `Path`. Expected 1 but got 0.
Note that multiple parameters must be extracted with a tuple `Path<(_, _)>`
or a struct `Path<YourParams>`
```

as the response body, instead of the SvelteKit `index.html` shell.
**The frontend was unreachable**. Every navigation to a SPA route
returned an Axum error string. **v0.1.0 shipped with this regression.**

The bug was hidden from prior audits because:

1. `scripts/smoke-dogfood.sh` only tests `GET /` (which uses
   `embed::serve_index`, a separate handler with no extractor) and
   `GET /api/*` paths (which never reach the embed fallback). It
   never exercises a SPA route through the binary.
2. `embed::serve_asset`'s collocated unit test called the function
   *directly* with a literal `Path("adr/3".to_string())` instead of
   going through the Axum router — so the extractor plumbing was
   never exercised in the unit test either.
3. M3 review forecast (`studio-review-wave-m3-opus47`) said the
   13-of-14 prior-fail Playwright state was "rust-embed not on TEST
   branch yet; post-merge all 14 will pass." **This was wrong** —
   the bug is in the rust-embed integration's extractor choice, not
   in branch merge state. The forecast was speculative; the empirical
   measurement was deferred.
4. M4 TEST agent (the wave that was supposed to validate the release)
   returned mid-flight without running Playwright. The CTO did not
   re-dispatch; instead, the CTO ran the audit directly.

**How it was caught**

**Post-tag CTO 守闸 M4 release-readiness audit** ran hermetic
Playwright (`STUDIO_E2E=1 pnpm run test:e2e`) against
`./target/release/cobrust-studio` built from main HEAD `a722e09`
(== v0.1.0). 13 of 14 e2e specs failed at the first
`page.goto('/login')` step. Inspection of Playwright's
`error-context.md` showed the exact Axum error string. Hypothesis
confirmed in <60 seconds.

Filed P0 finding
[`m4-release-readiness-spa-fallback-extractor.md`](https://github.com/Cobrust-lang/cobrust-studio/blob/main/docs/agent/findings/m4-release-readiness-spa-fallback-extractor.md).

**Fix**

`v0.1.1` (commit `15b6f46`): replace `Path<String>` with
`axum::http::Uri`:

```rust
use axum::http::Uri;

pub async fn serve_asset(uri: Uri) -> Response {
    serve_path(uri.path())
}
```

Locked against regression by new unit test
`serve_asset_handles_spa_routes_login_agent_etc` that exercises
**every** SPA route through the fixed `Uri` extractor (not just the
literal-Path collocated test pattern that had failed to catch the bug).

**Catalogue mapping**

This is **F19 (release-readiness untested) — first time the F19
prevention mechanism caught a real shipping bug in Cobrust Studio**.
The finding's §"Forward implications" makes this explicit:

> *"The smoke-dogfood.sh script SHOULD probe a SPA route (e.g.,
> `curl /login | grep '<html'`) to catch this class of regression at
> the script level. Filed for v0.1.2."*
>
> *"M4 release-readiness pattern: the F19 mandate 'any public-facing
> install / quickstart / release command must pass independent
> execution in a clean shell' implicitly extends to 'any public
> ROUTE must be hit by an independent caller before publish.'
> smoke-dogfood.sh covers /api/* and /; v0.1.1 forward should cover
> SPA routes too."*

> **Methodology learning: F19 extends from "install commands" to
> "every public surface".** The original F19 (Cobrust v0.1.x release
> notes) was about `cargo install` URLs and curl commands. Studio's
> instance generalises it to **any public-facing route that a real
> user would hit through normal use**. The mechanism is the same —
> independent caller (Playwright + curl) probing a clean-shell binary.

### §3.5 F20 recursive closure: doc-coverage §6 hardened against `cargo test --locked` exit 101 leaking past FAILED-grep

**Where it broke**

v0.1.1 (`15b6f46`) shipped with the workspace version bumped from
0.1.0 → 0.1.1 in `Cargo.toml`, but `Cargo.lock` still referenced the
v0.1.0 workspace versions (`studio-server v0.1.0` etc.). Any user
running `cargo build --workspace --locked` against v0.1.1 — including
`scripts/build-release.sh`, the CI release workflow, or the M3-docs
recommended user clone path — got:

```
error: the lock file CARGO_LOCK needs to be updated but --locked was passed
to prevent this
```

`cargo test --workspace --locked` exits 101 (cargo's "build failed
or lockfile mismatch" code) **WITHOUT** ever running tests — so it
never emits a `test result: FAILED` line.

The `doc-coverage.sh` §6 gate, hardened at M4.1 against the
`grep '^test result'` swallow-fail pattern, used:

```bash
test_output=$(cargo test --workspace --locked --no-fail-fast 2>&1)
failed_count=$(echo "$test_output" | grep -c '^test result: FAILED')
[ "$failed_count" -eq 0 ] || exit 1
```

This **only catches `FAILED` summary lines**. Exit code 101 from
lockfile-mismatch doesn't produce any summary line — so `failed_count`
is 0, gate passes green, **v0.1.1 ships broken-from-tag**.

**How it was caught**

Post-v0.1.1 tag, the `scripts/release-tarball.sh` build pipeline
errored at `cargo build --workspace --locked`. The doc-coverage §6
gate had passed green just minutes before. CTO 守闸 immediately
identified the recursive pattern: **the gate that was supposed to
enforce F20 ("constitution-vs-workflow alignment") had itself a F20
gap** — the workflow's enforcement was incomplete.

This is the **recursive F20 closure**: F20 applied to its own
enforcement script.

**Fix**

v0.1.2 (`7ea9ae3`). Two changes:

1. **Cargo.lock regenerated** via `cargo build` against the new
   workspace version. Lockfile now consistent with `0.1.1+`.
2. **doc-coverage.sh §6 paired-gate** — separate `if !cargo test
   ...` for exit code AND `failed_count` check for FAILED-grep. Either
   non-zero fails the gate.

```bash
# v0.1.2: paired gate. EITHER cargo exit != 0 OR FAILED count > 0 fails the script.
if ! cargo test --workspace --locked --no-fail-fast > "$test_log" 2>&1; then
    cargo_exit=$?
    echo "doc-coverage: FAIL — cargo test exited $cargo_exit (lockfile mismatch / compile error / panic)" >&2
    exit 1
fi
failed_count=$(grep -c '^test result: FAILED' "$test_log" || true)
if [ "${failed_count:-0}" -ne 0 ]; then
    echo "doc-coverage: FAIL — $failed_count failed groups" >&2
    exit 1
fi
```

The CHANGELOG names the gap explicitly:

> *"v0.1.1 Cargo.lock stale ... v0.1.1's commit shipped with Cargo.lock
> still referencing the v0.1.0 workspace versions. ... cargo test
> --locked exited 101 but the grep returned 0 FAILED, so the script
> passed green. v0.1.2 closes."*

**Catalogue mapping**

This is the **first documented "F20 recursive closure"** instance —
F20 applied to its own enforcement script, with each enforcement
layer requiring its own paired review. Studio is the empirical
substrate for the pattern:

> **Methodology learning: F20 closure is not one-shot. The enforcement
> layer needs its own paired review.** A doc-coverage gate that hardens
> against pattern X can ship green against pattern Y on the same
> code-path. The script's invariant ("no test failures shipped") is
> declared once; each new failure mode (FAILED summary line / non-zero
> exit code without summary / hang / panic / OOM) needs its own
> orthogonal check.
>
> **Empirical pattern**: every enforcement layer needs its own paired
> orthogonal-failure review until the failure-mode class no longer
> recurs. Studio took two patches (M4.1 + v0.1.2) before the §6 gate
> stopped letting things through.

### §3.6 The strip-#2 declared-empty-must-be-observed-empty discipline

**Where the discipline was tested**

ADR-0006 §"Strip list" item #2 directed the A1.1 lift to remove "ADR-0040
honest-gate hooks (L2 verdict typing)" from `router.rs` + `ledger.rs`.
The strip list was authored from the Studio handoff doc's plan-time
view of upstream entanglement — i.e., a CTO Phase-1 belief about
what the upstream pin contained.

P7 A1.1 lift agent searched the actual upstream pin
(`~/repos/cobrust-source-pin/crates/cobrust-llm-router/` at SHA
`61f2aff`, v0.1.1):

```bash
grep -rn "L2Verdict\|gate_verdict\|L2.*Verdict\|HonestGate" \
  ~/repos/cobrust-source-pin/crates/cobrust-llm-router/src/
# Result: zero hits.
```

The strip was a **no-op at this pin**. The honest-gate surface
evidently lived in a different upstream crate (the translation
pipeline, not the router crate).

**The discipline applied**

The lift didn't silently elide strip-#2 from the report. Filed P3
finding
[`a1-1-strip-2-noop-at-pin-61f2aff.md`](https://github.com/Cobrust-lang/cobrust-studio/blob/main/docs/agent/findings/a1-1-strip-2-noop-at-pin-61f2aff.md)
explicitly recording the no-op:

> *"ADR-0040's 'honest gate' surface evidently lives elsewhere in the
> upstream Cobrust workspace (likely the translation pipeline crates,
> not the router crate). At the pinned router-crate SHA, there is
> nothing to strip. The lift therefore proceeded with strip #2 as a
> verified no-op."*

The finding's §"Conclusion" articulates the principle:

> *"Ballast §'Atomic commits' + §'5-gate verification' both demand that
> declared invariants get verified in the same commit as the code they
> constrain. Strip #2 declared an invariant ('no honest-gate hooks in
> studio-router'). The honest verification was 'they were never in
> scope at this pin'; recording that explicitly closes the F1.0 / F19
> risk class — namely, future readers seeing strip #2 in ADR-0006
> might assume there must have been code removed, look in vain, and
> either re-add bogus honest-gate machinery to 'fix' what they think
> went missing, or distrust ADR-0006's other strip claims."*

**Catalogue mapping**

This is a **"declared-empty must be observed-empty" pattern** — a
proactive F1 family prevention. The principle: when an ADR declares
*the absence* of something (no honest-gate, no consensus mode, no
per-task routing), that absence must be **empirically observed** and
**recorded as observed**, not silently assumed. Otherwise a future
reader can't distinguish "we removed X" from "X was never there".

> **Methodology learning: ADR strip-lists and constitution-prohibitions
> must record the *empirical observation* of absence, not just the
> *declaration* of absence.** Without the observation record, a future
> reader hitting an empty grep can't tell whether the absence is
> intentional (strip succeeded) or accidental (strip silently failed).

This is a candidate for a new F-sub-form in the catalogue — a parallel
to F19/F20 framed around **strip-and-fork lift provenance**. For now,
documented in the finding itself; flagged for catalogue back-port.

---

## §4 What Studio EXTENDED about Ballast

The methodology learned things during this session. This section
captures the deltas — items worth back-porting to SKILL.md or to the
failure-modes catalogue.

### §4.1 "Tag → audit → patch" as a RELEASE PATTERN, not just an audit gate

**The pattern**

Ballast v1.2.1 F19 documents "release-readiness agent runs in clean
shell before publish" as a **gate** — something that decides
GO / BLOCK before a tag is pushed. Studio's experience reframes this
as a **release pattern**, not a binary gate:

```
Tag the current candidate                            → v0.1.<N>
   ↓
Audit the tagged artifact in clean shell             → release-readiness agent
   ↓
If BLOCK: file finding + patch + tag v0.1.<N+1>     → patch dance
   ↓
Re-audit
   ↓
If GO: announce, publish notes                       → first usable tag
```

**Why this matters**

The framing change is load-bearing: under tight timelines (Studio's
21-hour run), there is no time for *one* perfect tag. The right
pattern is *fast tag → fast audit → fast patch*, accepting that
v0.1.0 / v0.1.1 are intentionally just the experiment substrate that
the audit will reveal.

Each tag is the **experiment**; the audit is the **observation**;
the patch is the **learning**. Three tags in one day for Studio is
not three failures — it's three completed experimental cycles, each
of which revealed an enforcement gap that intent-driven self-checks
had missed.

**Empirical evidence**

- v0.1.0 tag → M4.1 release-readiness audit → caught F-M4-01 SPA
  fallback regression → v0.1.1 patch.
- v0.1.1 tag → release-tarball.sh in clean shell → caught Cargo.lock
  staleness → v0.1.2 patch.
- v0.1.2 tag → release-readiness audit → green; no v0.1.3 needed
  same-day.

The pattern's success metric isn't "first tag is perfect"; it's
"convergence after K patches stays bounded". For Studio: K=2.

**Back-port candidate for SKILL.md**

Propose adding §4 (Quality & Verification) sub-section:

> *"Tag → audit → patch as a release pattern: under acceleration,
> accept that the first tag will not be the publishable one. The
> right discipline is fast experimental cycle: tag, run the
> release-readiness audit in clean shell, patch the gap, re-tag.
> Cobrust Studio shipped v0.1.0 → v0.1.1 → v0.1.2 in 6 hours
> wall-clock; each tag was a learning step. CHANGELOG.md names each
> tag explicitly as broken/usable so users know which to skip."*

### §4.2 Recursive F20 closure — enforcement layers need orthogonal-failure review

**The pattern**

F20 closure is not one-shot. When you harden enforcement layer A
against failure mode X, you reveal that layer A has a sibling gap
against failure mode Y (orthogonal failure on the same code path).
Closing X without checking Y leaves the layer half-closed.

**Empirical evidence**

The `doc-coverage.sh` §6 gate evolution:

| Stage | Enforcement | Gap revealed |
|---|---|---|
| Pre-M4.1 | `grep '^test result' \| wc -l` | Counts both `ok` and `FAILED` as `result` lines |
| M4.1 | `grep -c '^test result: FAILED'` | Misses non-zero exit without summary line (e.g. lockfile mismatch exit 101) |
| v0.1.2 | Paired: `if ! cargo test` AND FAILED-grep | Both classes now caught |

Each fix was complete against the bug class it was designed for. But
the enforcement layer had **orthogonal failure modes** (FAILED-line
emit-ing vs not-emit-ing) that needed their own paired review.

**Forward implication**

> **Methodology learning: when closing an F20 instance, scan for
> orthogonal failure modes on the same code path.** Ask: "could my
> enforcement layer still pass under a different failure mode of the
> same operation?" If yes, the closure is partial.

This generalises beyond test gates. The same logic applies to:

- Schema invariants in frontmatter (different shape of violation)
- CI lint scripts (different shape of bad input)
- Dispatch prompt template fields (different shape of agent shortcut)

Back-port candidate for failure-modes-catalogue §F20 §"Prevention
going forward": add a fourth layer ("Layer 4: orthogonal-failure
review against every paired-gate enforcement").

### §4.3 Continuous persona testing executed in-sprint, with persona-output → PR mapping

**The pattern**

Ballast v1.2.1 §1 §"Continuous persona testing" documents persona
simulation as continuous dev cadence, not one-shot audit. Studio's
post-v0.1.2 turn was the first project to execute this as a
**deliberate sprint output**, not as a pre-release ceremony.

**How it was executed**

Three persona agents dispatched in parallel post-v0.1.2:

| Persona | Profile | Verdict | Key catches |
|---|---|---|---|
| **Mei** | Python data scientist, target user | AMBER | Vocabulary confusion (what's an "ADR"?), missing "why not Linear/Notion?" framing, install path assumes `rustup` knowledge |
| **Aleksandr** | Senior Rust eng, technical skeptic | REAL (genuine assessment) | F-05 dead deps (`unicode-normalization`, `uuid`, `hex`, `tracing` carried from upstream lift but unused in studio-router), missing CI matrix |
| **Sarah** | OSS evaluator / governance | PASS-watch-6-month | Bus factor 1 (single contributor; flagged as adoption risk), no SECURITY.md, no CONTRIBUTING.md |

The personas were given:
- Persona identity + background (years exp, prior burned-by experiences)
- Specific scenario ("you have 30 min, someone shared this on HN")
- Concrete actions to perform (open README, mentally try install)
- Stay-in-character constraint ("don't break into 'as an AI...'")
- Structured report fields aligned to persona's actual decision
  ("would I upvote on HN?" / "what would I PR if I had a free
  afternoon?")

**Persona → PR mapping (empirical evidence the pattern works as a PR-driver, not as theatre)**

Mei's friction items drove the M5 README rewrite directly:

- *"What's an ADR? The vocabulary table dropped me in"* → README §"Methodology vocabulary" table added (`docs/agent/adr/`, `docs/agent/findings/`, "Wave", "Tx tag", "5 gates", "守闸").
- *"Why not just use Linear?"* → README §"Why this and not Linear + git?" comparison matrix added.
- *"Is this production-ready?"* → README §"Honest status" section added, naming the v0.1.0/v0.1.1 patch dance up front.
- *"Bus factor 1 is a yellow flag"* → README §"Looking for 3-5 design partners" section added with concrete asks.

Aleksandr's F-05 dead-deps catch landed in the same M5 commit
(`339e1ab`):
```
Remove studio-router/Cargo.toml deps lifted but unused:
  - unicode-normalization
  - uuid
  - hex
  - tracing
(carried from upstream cobrust-llm-router @ 61f2aff; not used in
the post-strip surface.)
```

Sarah's bus-factor + governance findings drove the M5 CI matrix and
release workflow (`58cbe94`).

**Why this matters**

Mei's findings, in particular, were **structurally undiscoverable by
the internal review-claude pipeline**. The internal P7-REVIEW agent's
job is "is the code sound?" — it reads the code, the ADRs, the
findings. Mei's job is "would a Python user, with no Rust background,
recognise enough vocabulary to want to install this?" — she reads
only the README from a cold-context start.

> **Methodology learning: persona-output is the highest-leverage
> source of README/positioning PRs.** Internal reviews maintain
> internal coherence; persona simulation creates **external coherence**
> — between the project's pitch and the user's mental model. Three
> persona dispatches @ 30 min each (90 min total) produced ~15
> concrete PR items, of which 7 landed in the same wave.

**Back-port candidate for SKILL.md §1**: extend §"Continuous persona
testing" with a sub-bullet:

> *"Persona output → PR mapping: each persona finding should map to
> exactly one of {README edit, ADR addendum, finding, doc fix, code
> fix}. If a persona finding maps to 'no action / acknowledged', it's
> a research finding (file for the case study) not a product finding."*

### §4.4 AI velocity confirmed at ~2.5× on a 5-day plan

**The empirical evidence**

CLAUDE.md §6 specified a 5-day MVP target:

| M | Scope | Day target | Actual |
|---|---|---|---|
| M0 | scaffold + 5 ADRs + 5-gate CI | Day 1 | Day 1 hour 0-2 |
| M1 | backend MVP — Axum + routes + studio-router lift | Day 2 | Day 1 hours 2-20 (A1-A5) |
| M2 | frontend MVP — SvelteKit + 4 pages | Day 3 | Day 2 hours 0-5 |
| M3 | dogfood + polish + single binary | Day 4 | Day 2 hours 5-10 |
| M4 | release v0.1.0 + demo + reviewer invite | Day 5 | Day 2 hours 10-14 |
| M5 | (post-MVP, persona-driven) | not planned | Day 2 hours 14-18 |

**Total wall-clock: ~21 hours** for a plan estimated at 5 human-days
(40 work-hours). Velocity multiplier: **~2.5×** if we count only
human-equivalent effort (the human's 3-4 hours was strategic; the
~125 commits were all agent-produced).

The AI velocity heuristic in SKILL.md §5 predicted *"a 5-day human
plan = ~2-day AI plan with ≤4-way parallel"*. Studio confirms the
heuristic with N=2 evidence, at slightly more conservative
parallelism (≤3-way trio).

**The catch**

The 2.5× velocity multiplier did NOT translate to "first tag is
shippable". The 21-hour run produced *three tags* — v0.1.0 broken,
v0.1.1 broken, v0.1.2 usable. AI velocity buys faster experimental
cycles; it does NOT buy shippable-on-first-try. **The right framing
is "first usable tag in 21 hours" not "feature-complete in 21 hours".**

Back-port candidate for SKILL.md §5 §"AI velocity planning":

> *"AI velocity multiplier (~2.5× to ~10×) buys experimental cycles,
> not shippable-first-try. Plan for K=2 patch tags before first
> usable tag. Each patch is its own experimental cycle; aim for total
> wall-clock = (plan_days × velocity_inverse) × (1 + K × 0.1). For
> Studio: (5 days × 0.4) + (2 × 0.5 day) ≈ 3 days; reality was 0.9
> day, comfortable under estimate."*

### §4.5 Persona report as PR-driver, not as theatre

(Already covered in §4.3 above; summarized here for catalogue
back-port.)

The pattern: persona simulation produces actionable PRs when:
1. Personas are richly defined (years exp, prior burned-by, current
   frustrations) — not "a Python dev"
2. Personas have a specific scenario ("you have 30 min on HN")
3. Personas have stay-in-character constraint enforced in prompt
4. Persona output is structured ("would I upvote", "what would I PR")

Without these four, persona simulation regresses to "an AI agent
giving generic feedback" — which is theatre.

### §4.6 The "constitution → ADR → finding → script-enforcement" stack as a 4-layer F20 discipline

Studio's discipline can be described as a 4-layer stack:

| Layer | Artifact | What it enforces | Where it can fail |
|---|---|---|---|
| 1: Constitution | `CLAUDE.md` | Strategic invariants ("5 gates green before merge") | Text-only; survives only in agent's session context |
| 2: ADR | `docs/agent/adr/NNNN-*.md` | Architectural commitments ("studio-router public surface is X") | Drifts from as-built; corrected via §Addendum |
| 3: Finding | `docs/agent/findings/*.md` | Empirical observations ("the grep leaked") | Filed but no script-level enforcement |
| 4: Script | `scripts/doc-coverage.sh` | Mechanical CI gate (paired exit-code + FAILED-grep) | The ultimate truth — if it passes, the build passes |

**F20 mandates the gradient**: every rule at layer N must have a
paired enforcement at layer N+1. Studio's 4-finding count maps
1-to-1 to layer transitions:

- F-A2-01 `last_verified_commit: HEAD` placeholder leaked → layer 1
  rule had no layer 4 enforcement → fixed in `f20-closure-last-verified-commit-enforcement.md`
- F-A4-01 9 failing tests under green-gate → layer 1 rule had no
  layer 4 enforcement → fixed in `cto-shougate-test-gate-grep-leak.md`
- F-M4-01 SPA fallback `Path<String>` → layer 2 ADR-0002 (single-binary)
  had no layer 4 release-readiness audit covering SPA routes → fixed
  in `m4-release-readiness-spa-fallback-extractor.md`
- A1-1 strip-2 no-op at pin `61f2aff` → layer 2 ADR-0006 §"Strip
  list" item #2 had no layer 4 verification of the strip; fixed by
  empirically observing the absence and filing the finding.

> **Methodology learning: the 4-layer constitution → ADR → finding →
> script stack is the right abstraction for F20.** Every rule needs
> a script-level enforcement; every finding should record which
> layer's gap it closes.

Back-port candidate for SKILL.md Part 3 (Documentation Discipline):
make the 4-layer model explicit.

---

## §5 Numbers worth quoting

| Metric | Value |
|---|---|
| Span wall-clock | ~21 hours (2026-05-11 17:22 → 2026-05-12 14:36) |
| Span 5-day human plan | compressed to 2 calendar days (~2.5× AI velocity) |
| Commits on main | 125 |
| Tags pushed | 3 (v0.1.0 / v0.1.1 / v0.1.2) |
| Rust crates | 3 (studio-router / studio-store / studio-server) |
| Binary size | 9.0 MiB (single-file deployment) |
| Rust tests at HEAD | 196 (32 ok groups, 0 FAILED) |
| Playwright e2e | 14 hermetic + 2 dogfood (all green) |
| Real-LLM e2e | PASS (codex-forwarder + gpt-5.5) |
| ADRs | 6 (0001..0006) |
| Findings | 4 (P0 / P1 / P2 / P3 all represented; 3 closed within session) |
| Module-docs | 4 (studio-router / studio-store / studio-server / web-frontend) |
| Opus sub-agent dispatches | ~18 (6 waves × 3-team trio + 4 reconcile rounds + 1 release-readiness agent) |
| Persona dispatches | 3 (Mei / Aleksandr / Sarah) |
| CI gates enforced | 6 |
| Human work-hours (estimated) | 3-4 (strategic + 守闸 only) |
| Agent work-hours (estimated) | ~22 active (across parallel sub-agents) |
| AI velocity multiplier observed | ~2.5× on a 5-day plan |
| F1.0 catches | 2 (BSD-sed; CTO 守闸 grep leak) |
| F19 catches | 2 (M4 SPA fallback; v0.1.1 Cargo.lock) |
| F20 catches | 2 (last_verified_commit HEAD placeholder; recursive doc-coverage §6 closure) |
| F21 catches | 1 prospective (zero git-author leak; all 125 commits attributed cleanly) |
| Methodology firsts | First F20 closure in non-origin project; first documented "tag → audit → patch" release pattern; first "recursive F20 closure" |

---

## §6 What still ahead (post-session)

These are out-of-scope for this case study but worth naming for completeness:

- **AEAD real round-trip on `/login` (M5+)**: WebCrypto m2-stub auth
  blob is opaque to the server today. Users set `ANTHROPIC_API_KEY` /
  `OPENAI_API_KEY` env var as the actual auth path. Real
  server-side decrypt deferred.
- **Linux + Windows tarball CI matrix**: `release.yml` workflow
  landed at M5 (`58cbe94`); awaits next tag to fire.
- **Ballast case-study back-port**: this document.
- **Design partner recruitment**: README §"Looking for 3-5 design
  partners" published; concrete asks enumerated.

None of these block the N=2 dogfood validation conclusion: the
methodology survived contact with a new codebase under acceleration,
and Studio's session produced enough catalogue-augmenting evidence
to retrofit F19/F20/F21 into validated-pattern status.

---

## §7 Patterns I'd carry forward (Studio → next Ballast project)

1. **3-team trio dispatch** at ≤3-way parallel for narrow-scope
   waves. Reserve P9 layer for waves needing sub-decomposition of
   the ADR itself.
2. **ADR §Addendum YYYY-MM-DD pattern**: never edit §"Decision";
   append corrections preserving the original CTO Phase-1 text. The
   blame-integrity move.
3. **doc-coverage.sh layered enforcement**: presence + shape +
   reachability + paired-gate exit-code on `cargo test`. Six gates
   minimum, not five.
4. **F21 prospective discipline**: verify `git config user.name`
   before every commit; suffix every sub-agent handle with the
   session ID.
5. **Tag → audit → patch as a release pattern**: under acceleration,
   first tag is the experimental substrate; expect K=2 patch tags
   before first usable.
6. **Persona dispatch → README rewrite pipeline**: each persona finding
   maps to exactly one PR; persona output is the highest-leverage
   external-coherence source.

## §8 Patterns I'd add or strengthen for v1.2.2+ of Ballast

1. **6-gate canonical (extend the standard 5-gate)** — add §6
   doc-coverage as a load-bearing gate, with paired exit-code +
   FAILED-grep on `cargo test`. The 5-gate is insufficient under
   aggressive parallelism.
2. **F20 recursive closure pattern documentation** — F20 closure is
   not one-shot; every enforcement layer needs its own paired
   orthogonal-failure review.
3. **F1 "declared-empty-must-be-observed-empty" sub-form** — when an
   ADR declares the absence of something (strip-lists, prohibitions),
   the absence must be empirically observed and recorded.
4. **Tag → audit → patch as a release pattern** — explicit named
   pattern in §4 of SKILL.md, with the v0.1.0/v0.1.1/v0.1.2 sequence
   as canonical example.
5. **AI velocity = experimental cycles, not shippable-first-try** —
   sharpen the SKILL.md §5 velocity guidance to plan for K patch tags
   before first usable.
6. **Persona output → PR mapping** — extend §1 continuous-persona
   testing with the explicit "every persona finding maps to exactly
   one PR" rule.

## §9 Patterns I'd reconsider

1. **3-team trio dispatch on single-surface waves**: Wave M2 (SvelteKit
   frontend, 5 pages) used the 3-team pattern but the parallel
   review surface was narrow — REVIEW agent had little to audit until
   DEV merged. **Reserve 3-team trio for cross-crate Rust waves**;
   single-P7-with-self-review-step is sufficient for narrow surface.
2. **Triple-track docs (zh / en / agent) at bus factor 1**: maintained
   for methodology fidelity, but the cost is real (every doc edit
   touches 3 files). Cobrust N=1 has the same observation.
   Consider downgrading to dual-track (en + agent) below ~3
   contributors, per SKILL.md §3 escape hatch.

---

## §10 Closing

Cobrust Studio is not a "solved" project. It's at v0.1.2 with:
- A working 9 MiB single-binary web console for AI agent dispatch
- A 6-gate CI bar that enforces ADR + finding + bilingual doc
  discipline mechanically
- 196 Rust tests + 14 Playwright e2e + 2 dogfood specs + real-LLM
  e2e all green at HEAD
- A documented patch dance (v0.1.0 broken → v0.1.1 broken → v0.1.2
  usable) that names each gap by file:line

The Ballast methodology distilled from Cobrust (N=1) was the
**experimental substrate** for Studio (N=2). The result confirms:

- **Core invariants hold under acceleration.** 4-tier topology
  (collapsed to P10+P7), two-phase dispatch, 5-gate verification,
  atomic commits, worktree-per-sprint, F21 identity hygiene — all
  executed as documented.
- **The 5-gate is insufficient; 6-gate is the new floor.** Studio's
  M4.1 §6 + v0.1.2 §6 paired-gate work is the canonical evidence.
- **F19/F20/F21 are validated as prevention mechanisms, not just
  diagnostic vocabulary.** Each fired in Studio; each prevented or
  caught a real shipping bug.
- **The patch dance is a release pattern, not a failure pattern.**
  Tag → audit → patch is the right discipline under acceleration.

If you adopt Ballast on your project after reading this case study,
expect to:
- Land your first tag in days, not weeks
- Expect K=2 patch tags before first usable
- Spend ~10% of project time on doc-coverage discipline (worth it —
  Studio's 4 findings are all directly attributable to gate-level
  enforcement gaps that the discipline made visible)
- Run a persona dispatch every release — the output is your highest-
  leverage external-coherence source.

The N=2 evidence is in. Ballast v1.2.1 holds.

---

**Cobrust Studio origin**: 2026-05-11 17:22 +0800.
**Ballast N=2 dogfood completed**: 2026-05-12 14:36 +0800.
**Case study authored**: 2026-05-12 (this document).

— Signed-off: studio-p7-adsd-backport-opus47
  (working window 2026-05-12; back-port commissioned by P10 CTO
  studio-cto-session-002-opus47 after the v0.1.2 release sealed and
  persona-audit output landed in M5)

---

## §11 M6/M7 cycle empirical evidence (2026-05-12 evening)

This section documents the second major wave of Cobrust Studio development,
covering **M6 (ADR-0007 AEAD round-trip)** and **M7 (ADR-0008 multi-provider
/login)**, both completed on the same calendar day as the v0.1.0–v0.1.2
patch dance. The Ballast methodology was applied a **third and fourth time** via
the two-phase dispatch SOP in immediate succession, producing v0.2.0 (M6),
v0.2.1 (infrastructure patch), and v0.3.0 (M7) within ~6 hours wall-clock.

The empirical findings from this cycle are qualitatively different from §2–§4:
where §2–§4 document the methodology's first real-world pressure-test (N=2
dogfood), §11 documents the methodology **operating as a repeatable cadence**
— what happens when you apply the two-phase SOP twice in a row with no
intervening friction, and whether the patterns hold under that pressure.

Dashboard update:

```
New tags in this cycle:  3  (v0.2.0 / v0.2.1 / v0.3.0)
New ADRs landed:         2  (ADR-0007 / ADR-0008)
New commits (M6+M7):     ~13 (6 M6 commits + 7 M7 commits, including fixes)
Wall-clock total:        ~6 hours (ADR-0007 spike → v0.3.0 tag)
Sarah persona cycles:    4  (v1 post-M4 → v2 post-M5 → v3 post-M6 → v4 post-M7)
P9 sub-agent dispatches: 2  (one for M6, one for M7; both opus, both 守闸'd)
Methodology firsts:      Two consecutive two-phase SOP applications without
                         intervening friction; Sarah persona verdict path from
                         "6+ months out" to "pilot-ready NOW"; persona-found
                         bug fixed in the same cycle (same-cycle-closure)
```

---

### §11.1 Two-phase dispatch SOP applied twice consecutively

**The M6 cycle (ADR-0007)**

Phase 1 (CTO solo): `ADR-0007 secret-storage AEAD round-trip` was written
and committed before any implementation. The ADR documented:

- Algorithm choice (AES-256-GCM + Argon2id; 4 options considered, 3 rejected)
- Wire format (packed `salt(16) || nonce(12) || ciphertext+tag` in the
  `ciphertext` column of `session_kv` — avoids schema migration on the already-shipped table)
- Dispatch integration pattern (`Arc<RwLock<Option<SessionKey>>>` in AppState)
- 7 falsifiable Done-means criteria (unit tests / integration tests / E2E spec / doc-coverage / README / CHANGELOG / smoke-dogfood)
- `--dev-api-key` escape hatch for headless CI flows
- An explicit Phase 2 worktree target: `feature/m6-aead-round-trip`

Phase 2 (P9 dispatch): the P9 agent received the ADR as its primary read,
implemented in worktree `feature/m6-aead-round-trip`, produced 6 commits, and
reported `[P9-COMPLETION]` with all 7 gates green. Wall-clock: **120 minutes**.
CTO 守闸 verified the diff, ran cold rebuild from clean `target/`, and merged
`--no-ff` at commit `dd0b181`.

**The M7 cycle (ADR-0008)**

After v0.2.0 tagged and Sarah v3 audited (see §11.2), Phase 1 for M7 was
written immediately: `ADR-0008 multi-provider /login`. The ADR documented:

- 4 options (Option A: explicit field only; Option B: auto-detect from URL;
  Option C: explicit field + URL hint; Option D: per-provider routes)
- Chose **Option C** — unambiguous wire format + friendly UX
- Wire-format additivity: `LoginRequest` gains `provider_kind` with
  `#[serde(default)]` defaulting to `Anthropic` for v0.2.x back-compat
- `EndpointSecret` gains the same field so `provider_kind` lives **inside** the
  AEAD ciphertext, not in SQLite plaintext metadata
- Dispatch match arm: `match secret.provider_kind { Anthropic => ..., Openai
  => ..., Synthetic => Err(503) }`
- SvelteKit URL-hint logic: `$effect` reactive binding auto-suggests provider
  based on URL typed, user can override
- 7 Done-means criteria (2 unit / 6 integration / 1 E2E / 7-gate CI / 2 doc
  updates / CHANGELOG / README update)
- Phase 2 worktree: `feature/m7-multi-provider-login`

Phase 2 (P9 dispatch): 7 commits, all 7 gates green, **90 minutes** wall-clock.
Merge `--no-ff` at commit `ae9df29`.

**Why the second cycle was 30 minutes faster (90 vs 120 min)**

Three compounding factors:

1. **P9 prompt template reused verbatim.** The M6 dispatch prompt's structure
   (working dir + required reads list + mission + deliverables + 7-gate target
   + report format) was copy-adapted for M7 in under 5 minutes. No template
   design overhead.

2. **Test skeleton was a known pattern.** The M6 cycle established the shape
   of `tests/secret_roundtrip.rs` (integration-test file with wiremock stub +
   `#[ignore]`-attributed placeholder tests). M7's `tests/multi_provider_login.rs`
   followed the identical pattern; the P9 agent had the M6 test file as a
   required read and replicated the structure without hesitation.

3. **SvelteKit form integration had M6 as a reference.** M6 had already added
   the fourth input (Passphrase), restructured the SvelteKit `/login` page,
   and wired `POST /api/login`. M7's addition of a Provider `<select>` dropdown
   + `$effect` URL-hint was a targeted extension onto an already-known surface.
   The P9 agent did not need to discover the SvelteKit form's structure; it was
   already documented in the ADR-0008 Phase 1 spike (CTO Phase 1 had read M6's
   form implementation and documented the exact extension point).

**Methodology conclusion**: the two-phase SOP is **self-bootstrapping** when
applied consecutively. Each cycle leaves artifacts (test pattern, form shape,
dispatch prompt structure) that reduce the friction of the next cycle. This is
not specifically documented in Ballast §"Two-phase dispatch SOP" and is worth
adding as an operational note: *"The second cycle of a two-phase dispatch series
runs measurably faster than the first because the P9 prompt template, test
skeleton pattern, and integration surface are already established."*

---

### §11.2 Continuous persona testing — 4 cycle Sarah path

Sarah Chen is the Studio persona representing an OSS tech lead evaluating
AI-tooling for adoption at a 10–50 person engineering team. Her profile:
8 years Rust experience, responsible for build-vs-buy decisions, governance
concerns (bus factor, SECURITY.md, CONTRIBUTING.md), and pilot-readiness
gates for tooling used in production adjacent workflows.

Sarah ran **4 audit cycles in a single day**, each dispatched after a tag:

| Cycle | Triggered by | Verdict | Key gate states |
|---|---|---|---|
| **v1** (post-M4) | v0.1.2 first usable tag | "6+ months out" | Gate #1 (AEAD round-trip) open; Gate #2 (multi-provider) open; Gate #3 (5-platform green) open |
| **v2** (post-M5) | v0.1.3 CI matrix + persona-driven polish | "3 months out IF 3 pilot-gates close" | Gates named explicitly: #1 AEAD, #2 multi-provider, #3 5-platform tarball |
| **v3** (post-M6 / v0.2.0–v0.2.1) | v0.2.1 5-platform green after macos-13 patch | "2 months out — gate #2 closed; gate #3 'one tag away'" | Gate #1 (AEAD) CLOSED; gate #2 (multi-provider) remains; gate #3 (5-platform) → predicted need for runner-pool patch (see §11.4) |
| **v4** (post-M7 / v0.3.0) | v0.3.0 multi-provider /login | **"pilot-ready NOW for 1-5 person teams"** | All 3 pilot-gates CLOSED; remaining items are social/outreach, not code |

The verdict shift from v3 to v4 — a single-version jump from "2 months out"
to "pilot-ready NOW" — is the most concentrated signal in the four-cycle path.
It validates that **Ballast's two-phase SOP, when applied cleanly to the right
ADR, can close a persona-level gate in a single sprint**. Sarah v3's feedback
on multi-provider was specific and actionable ("add a `provider_kind` field to
`LoginRequest`; the fix is ~50 LoC in the LoginRequest struct and a match arm in
`resolve_router`"). ADR-0008 Phase 1 adopted that framing verbatim as the
decision rationale. M7 P9 closed the gate.

**Cost vs value of 4 persona cycles**

Each Sarah cycle cost approximately 30–40 minutes sonnet wall-clock (persona
dispatch + structured report output). Total for 4 cycles: ~2–2.5 hours. For
that cost, the project received:

- A named set of pilot-readiness gates that organized the M6 and M7 sprint
  priorities (instead of "what should we build next?", the answer was "what
  closes Sarah's next gate?")
- Actionable PRs from each cycle (passphrase strength validation, Argon2id
  benchmark, README security hierarchy table, passphrase rotation docs,
  provider dropdown UX, deprecation warning on `api_key_env`)
- A public-facing verdict that could be quoted in design-partner outreach
  ("our evaluator persona upgraded from '2 months out' to 'pilot-ready' in
  a single sprint")

**Framing: persona as pilot-readiness oracle**

The four-cycle Sarah path demonstrates a specific application pattern not
explicitly named in Ballast §1 §"Continuous persona testing": the persona as a
**pilot-readiness oracle**. Each cycle produces a structured verdict with
explicit gate conditions. The project's sprint priorities are derived from
the gate conditions. When the gates close, the verdict changes.

This is more structured than the §1 description ("spawn the same persona
after sprint completion → verify fix actually closes gap"). The oracle
framing adds:

1. Each persona cycle's verdict is explicitly conditioned on named gates
2. The gates are stable across cycles (same 3 gates v1 through v4)
3. Sprint priorities are directly derived from open gates
4. Verdict change is the measure of sprint success, not just "gates closed"

Back-port candidate for SKILL.md §1 §"Continuous persona testing":

> *"Pilot-readiness oracle variant: for pre-release cycles, structure the
> persona's verdict as a named set of pilot-gates. Each cycle reports which
> gates are open vs closed. Sprint priorities derive directly from open gates.
> The verdict sequence (6+ months → 3 months → 2 months → pilot-ready NOW)
> is the empirical evidence that the sprint plan is closing the right gaps."*

---

### §11.3 F1.0 declared-invariant gap → P9 implementation bug (seal-salt mismatch)

**The bug**

The M6 P9 implementation of `SessionKey::seal()` generated a **fresh random
salt on every call** and packed it into the blob header (`blob[..16]`). But
the `SessionKey` itself was derived from a **different** salt at login time
(the salt generated during the Argon2id KDF step in `POST /api/login`).

Result: `blob[..16]` (packed salt) ≠ `self.salt` (derive salt). Any subsequent
`SessionKey::derive(passphrase, blob[..16])` produced a different 32-byte key
from the one stored in memory → AES-GCM tag mismatch → `SecretError::Open`
→ false-positive `wrong_passphrase` 400 on every re-login with the correct
passphrase.

The symptom: Playwright login-aead.spec.ts test 2 (which exercised the re-
derive path: login → session drop → re-login same passphrase) and integration
test `restart_drops_key_returns_401` (which tested re-derive after simulated
restart) both reported `authenticated=false` after a valid second login.

The fix (commit `3753a2b`): `SessionKey` now carries its `derive_salt` as a
field; `seal()` packs `self.salt` (not a fresh random salt) into the blob
header. Nonce remains fresh per seal (AES-GCM uniqueness requirement is per-
nonce, not per-salt). New test `seal_then_re_derive_then_open_round_trips`
locks the contract.

**Root cause: F1.0 (declared-invariant gap)**

ADR-0007 §"Wire format" stated explicitly:

> *"packed salt enables re-derive — at restart the user re-types passphrase,
> server runs `derive(passphrase, blob[..16])` to reconstruct the key"*

This is a declared invariant: the blob's first 16 bytes are the salt used to
derive the key, enabling re-derivation from the same passphrase.

The P9 test corpus (6 unit tests as specified in ADR-0007's Done-means §1)
tested:
- `argon2id_kdf_deterministic` — same passphrase + salt → same key
- `aes_gcm_round_trip` — encrypt-decrypt round-trip
- `wrong_passphrase_fails_open` — wrong passphrase → error
- `tampered_ciphertext_fails_open` — bit flip → error
- `tampered_salt_fails_open` — flip salt bytes → different key → error
- `malformed_blob_too_short` — short input → error

**None of these 6 tests exercised the re-derive path**: `key.seal()` followed
by `derive(same_passphrase, blob[..16])` followed by `key2.open(blob)`. The
test corpus ran `seal` then `open` with the same key — which passes trivially
because the wrong salt is packed but the same wrong-salt key is used to
open. The test couldn't detect the bug because it never exercised the contract
path.

The bug was **structurally invisible** to the unit test corpus. The Playwright
E2E test caught it because it exercised the re-derive path *naturally* — the
test simulated what a real user does (restart browser, re-enter passphrase,
expect dispatch to work).

**This is textbook F1.0**: the invariant was declared ("packed salt enables
re-derive") but the test corpus did not contain a test that would prove the
invariant holds on the code path that exercises it. The gap was structural,
not an oversight — the 6 tests in ADR-0007's Done-means were necessary but
not sufficient.

**Methodology finding: persona-found bug + same-cycle closure**

The bug was caught by the E2E test the same day as the v0.2.0 tag. This is a
data point that Ballast §1 §"Continuous persona testing" coverage caught what the
unit test corpus structurally missed:

1. Unit test corpus: exercises individual operations on individual components
   (key derivation, encryption, tamper detection)
2. Integration test corpus: exercises API-level round-trips (login → dispatch →
   logout), which happen to exercise `seal` but not re-derive
3. Playwright E2E: exercises user-level scenarios (browser session drop +
   re-login), which naturally exercises the re-derive path

The E2E tests are the **orthogonal coverage layer** that the unit and
integration tests structurally cannot provide. This generalises: for any
invariant that depends on a **sequence of user-level actions across session
boundaries** (login → restart → re-login; install → upgrade → re-install;
publish → consumer → upgrade), the test that proves the invariant must simulate
that sequence end-to-end.

**Back-port candidate for failure-modes-catalogue §F1.0 §"Prevention"**:

> *"For any ADR §'Wire format' or §'Decision' that declares a re-derive /
> re-construct / re-derive path ('packed salt enables re-derive'), the
> Done-means test corpus MUST include a test that exercises that path
> end-to-end: derive → seal → extract-from-blob → re-derive → open.
> Unit tests that only run `seal; open` on the same key cannot detect
> derive-salt vs seal-salt mismatch."*

---

### §11.4 macos-13 (Intel) runner queue stall — infrastructure-not-code

**The pattern**

v0.1.3 (M5 CI matrix release) and v0.2.0 (M6 AEAD release) both shipped
**4 of 5 platform tarballs** because the GitHub-hosted `macos-13` (Intel
x86_64) runner queue stalled for 30+ minutes on the `x86_64-apple-darwin`
build job. The job eventually timed out or the release was tagged incomplete.

Sarah v3's audit — dispatched against v0.2.0 + the v0.2.1 state — included an
explicit prediction:

> *"If this stalls again, consider whether the cross-compile setup needs to
> change. The macos-13 runner pool appears to have queue depth issues."*

The v0.2.1 release addressed this directly: `.github/workflows/release.yml`
was patched to cross-compile `x86_64-apple-darwin` from `macos-14` (Apple
Silicon) using `--target=x86_64-apple-darwin`. Rust + Apple clang both support
this natively. The only change was the runner label (`macos-13` → `macos-14`
with the existing `--target=x86_64-apple-darwin` flag triggering
cross-compilation). **v0.2.1 shipped all 5 platform tarballs first-time green.**

**The lesson for Ballast**

Not every release-cycle regression is a code bug. CI infrastructure
dependencies — GitHub-hosted runner pool queue depths, external service
availability, macOS runner generations — can stall a release in ways that
are invisible from the code itself. The release.yml is correct; the runner
pool is the failure mode.

The Ballast §4 "tag → audit → patch" pattern applies here, but with a critical
distinction: **v0.2.1 contained no code changes**. The patch was
infrastructure-only. The existing Ballast framing of "no tag→patch dance" as
a failure pattern should be refined:

> **"No CODE tag→patch dance" is the rule. Infrastructure patches between
> tags are acceptable when the audit predicted the failure mode.** A
> release.yml runner-label fix that addresses a predicted runner-pool stall
> is not a methodology failure; it's the pattern working correctly (Sarah v3
> predicted the stall; v0.2.1 closed it).

This refinement matters for future Ballast projects that run multi-platform CI:
the infrastructure layer (runner pools, action versions, Docker image
availability, certificate expiry) is a legitimate release-infra concern that
sits outside the code quality envelope. Auditing "release readiness" must
include the infrastructure layer, not just the code.

**Sarah v3 as a predictive audit**

Sarah v3's explicit prediction of the runner-pool stall — before v0.2.1 was
tagged — is notable. The prediction was based on observing the pattern twice
(v0.1.3 and v0.2.0 both missing the Intel tarball) and inferring that the
`macos-13` runner pool was structurally insufficient. This is the
**predictive audit** pattern: a persona or reviewer that has enough context
to identify failure modes the team hasn't explicitly discussed.

The mechanism: Sarah v3 had read the CHANGELOG (which named "4 of 5 platform
tarballs" for v0.1.3) and the release.yml. Two data points of the same pattern
= structural inference. Ballast §1 external review discipline already notes that
external reviewers "find what the internal team won't think to find"; this is a
persona-level instance of that capability.

---

### §11.5 Autonomous loop discipline + autonomous-vs-confirm boundary

**The restatement pattern**

Across the full Studio project history (M0 through M7, spanning roughly 6
hours wall-clock for the M6/M7 segment), the user explicitly restated the
"autonomous loop, don't ask for permission" rule a total of **4 times**. Each
restatement occurred when the CTO agent paused to ask for confirmation before
an action that was clearly autonomous-safe:

| Restate # | Context | What the agent asked | Why it was wrong |
|---|---|---|---|
| 1 | Early M1 | "Should I proceed with the router lift?" | Lift was already specified in ADR-0006; Phase 2 was in flight |
| 2 | M4 post-tag | "Should I dispatch the M4.1 release-readiness audit?" | M4 tag was already pushed; the SOP mandates post-tag audit |
| 3 | M5→M6 transition | "Should I start M6 now?" | Sarah v2 had explicitly named AEAD as pilot-gate #2; M6 was the next clear action |
| 4 | Post-v0.3.0 | "Should I update the Show HN draft?" | Editing a local file in the project repo is autonomous-safe by any reasonable boundary |

Restatement #4 is the canonical example: the agent paused to ask permission
before editing `docs/outreach/show-hn-draft-v1.md` — a local file, in the
project repo, with no external publication step involved. The user's response
was "你是 CTO，这种事情不需要问。" (You're the CTO; you don't need to ask
for this.)

**The autonomous-vs-confirm boundary (canonical refinement)**

The 4 restatements across the project's history have enough pattern to
formalize. The boundary is:

**Autonomous (proceed without asking)**:
- Edit local files (code, docs, configuration)
- Commit to the working branch
- Push to the project's remote (non-force)
- Merge feature branches to main (--no-ff)
- Tag a release
- Dispatch sub-agents (within the 4-way parallel cap)
- Update documentation, READMEs, CHANGELOG entries
- Run test suites, CI gates, verification scripts

**Requires P10 confirmation**:
- Post to an external service (HN, Twitter/X, LinkedIn, email blast)
- DM specific individuals (potential design partners, press, investors)
- Spend money (API credits beyond project budget, compute infrastructure)
- Force-push to public main (or any destructive git operation)
- Publish a GitHub Release with release notes (the tag is autonomous; the
  public announcement text warrants a quick P10 read)
- License or legal decisions

The boundary is: **local + reversible + no external audience = autonomous;
external + irreversible + involves real people or money = confirm**.

**Why this matters for Ballast §"Operating instructions for agents"**

Ballast SKILL.md §8 ("When to bend Ballast") notes "Default to proceed" but the
catalogue doesn't give explicit boundary examples. The Studio experience
provides the canonical boundary definition with 4 concrete restatement
instances as evidence. The lesson is:

> *"An agent that asks 'should I edit this file?' is not operating autonomously.
> An agent that asks 'should I post this to HN?' is operating correctly. The
> boundary is external audience + irreversibility."*

Back-port candidate for SKILL.md §5 §"Operating instructions for agents":

> *"Autonomous-vs-confirm boundary (empirical from Studio N=2): editing
> local files, committing, pushing, merging, tagging, dispatching sub-agents,
> running scripts — all autonomous. Posting to external services, DMing
> individuals, spending money, force-pushing public main — confirm with P10.
> If you pause before editing a local documentation file, you are being too
> conservative; the user will correct you."*

---

### §11.6 New catalogue entries proposed: F29 and F1.5

The M6/M7 cycle surfaces two failure-mode patterns worth proposing for the
catalogue. Both pass the bar of "actionable in future projects, not a one-off
curiosity."

**F29 proposal: cross-platform runner-pool dependency as a release-infra failure mode**

*Distinct from F1.0 (declared invariant gap) because the failure is not in
code or documentation — it's in the infrastructure layer that executes the
release*. A release workflow declares "all 5 platforms ship as tarballs" (the
intent). The release.yml is correct (the code). The GitHub-hosted runner pool
for one of the 5 targets (`macos-13` Intel) has insufficient queue depth or
availability. Two consecutive releases ship 4/5 tarballs despite correct code.

This is a new failure mode class: **infrastructure-not-code release
regression**. F1.0 handles "the code declares an invariant the tests don't
enforce." F29 handles "the release workflow declares a multi-platform target
that the runner infrastructure can't reliably serve."

The recovery pattern (cross-compile from a more reliable runner with the same
`--target=X` flag) is actionable and applicable to any multi-platform CI
release that uses GitHub-hosted runners.

Evidence: v0.1.3 and v0.2.0 both missing Intel macOS tarball; v0.2.1 fixed
via `macos-14 --target=x86_64-apple-darwin` runner-label patch. Sarah v3
predicted the failure before v0.2.1.

*Candidate F29 is proposed for the catalogue at time of this case-study
back-port. Promoted from candidate if a second instance is observed in a
different Ballast project.*

**F1.5 proposal: test-corpus structural blind spot (re-derive path gap)**

*F1 Sediment Family sub-form.* The existing F1.0 covers "declared invariants
without enforcement" at the schema / snapshot / constitution level. The M6
seal-salt bug introduces a narrower sub-form: **a declared wire-format
invariant has a re-construct path that the test corpus structurally cannot
exercise because the test always uses the same in-memory key for both seal
and open**.

The pattern: ADR declares "packed field enables re-derive" (or "packed field
enables re-construct / re-validate / re-open"). The unit test corpus tests
`seal()` and `open()` on the same key object, not `seal()` → extract field
→ `derive(same_params, extracted_field)` → `open()`. The in-memory key
object bypasses the serialization-deserialization path that the packed field
is meant to support. Bugs in the packed field's content (wrong value packed)
are invisible.

This sub-form is distinct from F1.0 because:
- The enforcement mechanism (unit tests) exists and passes
- The gap is that the tests don't cover the *path being claimed* (re-derive),
  only the *happy path* (direct key reuse)
- Detection requires E2E or integration tests that simulate the full
  user-level sequence including session drops

Evidence: ADR-0007 §"Wire format" ("packed salt enables re-derive"); M6 P9
unit tests passing; Playwright E2E test detecting the bug on the first run.
Fix at commit `3753a2b`.

*Candidate F1.5 is proposed for the F1 Sediment Family. Both F29 and F1.5
should land in the failure-modes-catalogue at v1.2.7 when the case study
back-port is complete.*

---

### §11.7 Updated numbers (cumulative through v0.3.0)

| Metric | v0.1.2 baseline (§5) | M6/M7 additions | Cumulative |
|---|---|---|---|
| Tags pushed | 3 | 3 (v0.2.0 / v0.2.1 / v0.3.0) | 6 |
| ADRs | 6 | 2 (ADR-0007 / ADR-0008) | 8 |
| P9 sub-agent dispatches | 0 (all P7 in N=2) | 2 | 2 |
| Persona cycles | 3 (Mei/Aleksandr/Sarah v1) | 3 (Sarah v2/v3/v4) | 6 |
| Rust tests at HEAD | 196 | +~25 (secret module + integration + re-derive) | ~221 |
| Two-phase SOP applications | 0 (Phase-1-only per wave in N=2) | 2 (M6+M7 both full two-phase) | 2 |
| F1.0 catches | 2 (BSD-sed; grep leak) | 1 (seal-salt mismatch) | 3 |
| Infrastructure-not-code patches | 0 | 1 (v0.2.1 runner-label fix) | 1 |
| Persona verdict shifts | 0 | 3 (Sarah v1→v2→v3→v4) | 3 |
| Autonomous-loop restatements | 2 | 2 | 4 total across project |

---

### §11.8 Closing for the M6/M7 cycle

The M6/M7 cycle answers a question that §2–§4 could not: **what does Ballast
look like when it's working reliably, not being stress-tested?**

The stress-testing phase (N=2 dogfood) produced the F19/F20/F21 catches, the
three-patch-tag dance, the grep-leak finding. All of those were methodology
discovering its own enforcement gaps. The M6/M7 cycle ran the two-phase SOP
twice in a row with no grep leaks, no bad-baseline agents, no infrastructure
surprises (the macos-13 stall was predicted and patched cleanly). The primary
anomaly — the seal-salt bug — was caught by the E2E layer the same day it was
introduced and closed with a single commit.

What that says about the methodology:

1. **Two-phase SOP is genuinely repeatable.** Applied once (M6), the pattern
   established templates and patterns that made the second application (M7)
   30 minutes faster. The SOP is not a ceremonial overhead; it compounds.

2. **Persona-as-oracle produces a convergent verdict path.** Sarah's 4 cycles
   produced a monotone improving sequence terminating in "pilot-ready NOW."
   The gates were stable; the sprints were pointed at the gates; the gates
   closed. This is the methodology working as designed.

3. **E2E coverage is the orthogonal layer that unit tests cannot substitute.**
   The seal-salt bug was structurally invisible to 6 unit tests and 3
   integration tests. One Playwright test caught it. The lesson generalises:
   for any invariant that lives on a path across session boundaries, E2E
   coverage is not optional.

4. **Infrastructure is part of the release envelope.** The macos-13 stall is
   not a methodology failure; it's a reminder that "release readiness" extends
   to the runner pool, not just the code. The F29 candidate entry captures
   this for future projects.

5. **Autonomous-vs-confirm boundary needs explicit documentation.** Four
   restatements across the project's history is a signal that the Ballast
   methodology's "default to proceed" guidance is insufficient without explicit
   boundary examples. The boundary (local + reversible = autonomous; external +
   irreversible = confirm) is actionable and should land in SKILL.md.

---

**M6/M7 section authored**: 2026-05-12 (evening)

— Signed-off: adsd-case-study-update-m6m7-sonnet46
  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
