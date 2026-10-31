---
name: Ballast failure modes catalogue (F1-F30)
description: Concrete failure modes encountered in real Ballast projects with empirical evidence, root cause analysis, recovery patterns, and prevention mechanisms. F1 Sediment Family (9 sub-forms) + F2-F30 individual entries. Cobrust N=1 surfaced F1.0-F1.2 + F2-F24; Cobrust Studio N=2 (M0-M5) surfaced F1.3, F1.4, F25-F28; Cobrust Studio M6/M7 cycle surfaced F1.5 (candidate) + F29 (candidate). Add F31+ as your project hits new failure modes.
type: reference
version: 1.2.7
date: 2026-05-12
status: active
relates_to: [skill:SKILL.md §"Failure modes catalogue", case-study:cobrust-multi-agent-experience.md, case-study:cobrust-studio-experience.md, reference:evals-first-development.md, reference:context-window-strategy.md, reference:cross-session-memory-architecture.md]
---

# Failure modes catalogue

> Concrete failure modes encountered in real Ballast projects, with
> recovery patterns. Each entry references a specific case-study artifact.
>
> Add to this catalogue as your project hits new failure modes —
> negative results are first-class, including process failures.

---

## F1 — Declared rules without enforcement — **"F1 Sediment Family"** (**P0 SOP gap, 9 sub-forms confirmed**)

> **Status upgraded to "F1 Sediment Family" parent pattern** after 6 distinct
> sub-forms observed across Cobrust 11-day experiment, 2 additional sub-forms
> (F1.3 local-vs-CI gate drift, F1.4 README-vs-release-tag drift) confirmed on
> Cobrust Studio's 21-hour N=2 dogfood (M0-M5), and 1 additional sub-form
> (F1.5 test-corpus structural blind spot) surfaced in Cobrust Studio M6 cycle.
> F1 is the single most common systemic failure in Ballast-flavor projects. Original
> 3 sub-forms (F1.0 / F1.1 / F1.2) remain as implementation-level instances;
> F1.3 + F1.4 extend to enforcement-scaffold drift; F1.5 extends to test-corpus
> coverage gaps on re-derive paths. New sub-forms F16, F17, F18 extend the family
> to identity, self-reporting, and attribution-policy dimensions — all share the
> same root: **declaration ≠ enforcement, and enforcement scope silently lags
> reality.**
>
> **Family pattern one-liner**: Claim is written somewhere (constitution,
> schema frontmatter, KPI card, attribution policy, auto-memory). No
> automated mechanism verifies the claim. Claim gets violated within 1–3
> turns. Violation is invisible until an auditor manually checks.
>
> See F16 (identity drift), F17 (self-report fidelity gap), F18 (attribution
> policy without dir-scope enforcement) for the three new sub-forms; F1.3
> (local-vs-CI gate drift), F1.4 (README-vs-release-tag drift) for the two
> Studio M0-M5-surfaced scaffold-level sub-forms; F1.5 (test-corpus structural
> blind spot on re-derive paths) for the M6-surfaced sub-form.

### F1.0 — Snapshot sediment ("重写忘删")

### Symptoms

State doc has self-contradictory sections:
- §"Currently in-flight" says "ZERO sub-agent" while §"In-flight at
  this turn" lists 3 active worktrees
- §"ADR roster" table ends at 0034 while §"Phase E milestones" cites
  ADR-0035 as merged
- HEAD field reads stale SHA from N commits ago

### Root cause

When updating the snapshot, agent writes new content but doesn't
delete obsolete sections. Each turn adds a layer; sediment accumulates.

### Recovery

1. Stop. Do not dispatch further sprints until snapshot reconciled.
2. Three-way reconcile: `git log -10` + `ls findings/` + `ls adr/`
   compared against snapshot's claims.
3. Delete obsolete sections (don't preserve stale residue).
4. Add `schema_invariant` frontmatter. The enforceable form is the one
   in `reference/adopting-gates.md`: every ADR and finding file appears
   exactly once, `base_head` is an ancestor of HEAD, and each
   verification grade is `offline`, `review`, `deployed`, `live`, or
   `not-run`. Do not require the snapshot SHA to equal `git log -1`.
5. Run `scripts/check_ballast_docs.py` in CI. A declared invariant
   without that script is F1.1. (`scripts/snapshot-lint.sh` was a name
   in earlier drafts; it is not the script this repo ships.)

### Evidence

Cobrust 8th close-out review §"5 处 stale fact"; 9th review §"3 处
新 cracks"; 10th review §"sediment 第三次".

### Prevention going forward

The schema-invariant rule is necessary but not sufficient. Stronger:
add CI lint that validates the invariant. Without lint, declared
invariants are documentation only.

### F1.1 — Declared schema_invariants without CI lint

**Symptoms**: snapshot.md frontmatter declares
```yaml
schema_invariant: |
  HEAD SHA must equal `git log -1 --format=%h main` at write time.
  Every ADR mentioned must appear in §ADR roster.
```
But there's no script that verifies these. Each invariant gets violated
within 1-2 turns of being declared.

**Root cause**: invariants are documentation; documentation is not
enforcement.

**Evidence**: Cobrust 9th + 11th reviews. After 9th review fix added
schema_invariant block to snapshot frontmatter, the 11th-review multi-agent
audit found:
- Invariant 5 (HEAD SHA) violated: snapshot says `6008634`, real `06df4b4`
  (14 commits behind)
- Invariant 2 (every finding mentioned in ledger): ADR-0035 mis-pinned
  to "prompt-design" propagated to 2 files (real ADR is 0036)
- Lifecycle mismatch: msgpack finding `status: open` despite being
  closed by `99ebc54`

**Recovery**: invariants must compile to script assertions. Run
`scripts/check_ballast_docs.py` in CI. It checks roster bijection,
`base_head` ancestry, a resolvable `last_verified_commit`, and evidence
grades. It does **not** fail when the recorded SHA is merely older than
`HEAD`: equality with `git log -1` is red on the commit that records an
honest snapshot, which is why that check gets deleted. A stale-but-ancestor
SHA is still stale prose. Make that visible with a `not-run` grade or a
re-stamped `last_verified_commit`, not with an equality rule you cannot
keep.

### F1.2 — Constitution rules with partial-scope enforcement

**Symptoms**: constitution declares "Code change ⇒ both doc trees in
same commit" (Cobrust §3.3). Project ships `scripts/doc-coverage.sh`
that enforces this. **But the script's check scope only covers
M0..M14 baseline ADRs (0001..0029)**. Anything past — ADR-0030..0039
in Cobrust's case — silently skips the gate.

**Root cause**: doc-coverage rules are written for milestones known at
script-creation time. New milestones add ADRs/findings, but the script
doesn't auto-extend.

**Evidence**: Cobrust 11th-review §H2 (anchored at HEAD ~`06df4b4`, 2026-05-10).
At that time, `grep -rE "ADR-003[0-9]" docs/human/` returned **0 hits** —
ADR-0030..0039 were not in zh+en doc trees. Triple-tree drift was
systemic for all post-M14 work, but doc-coverage.sh was silent on it.
(Note 2026-05-12: this specific grep has since changed as later doc
sync added ADR-0030..0039 mentions, but the systemic pattern remains
the F1.2 instance — the verification step was hardcoded against a
specific milestone range and went stale.)

**Recovery**: doc-coverage scripts must auto-discover scope via
`ls docs/agent/adr/00*.md` patterns, not hardcode milestone lists.
Same applies to any "rule covers M0-M<N>" pattern — it will go stale
the moment M<N+1> lands.

### F1.3 — Local-vs-CI gate definition drift (sub-form of F1.2)

**Symptoms**: a project enforces "N gates green before merge" at two
layers — `scripts/doc-coverage.sh` (developer-local fast feedback) and
the GitHub Actions workflow (canonical merge gate). The mandate is
nominally identical at both layers, but the two layers define the
gate-set differently. Local script reports "all 6 gates passed"; CI
fails the PR on a 7th gate the local script never ran. The developer
sees a green local run + a red CI run and cannot reconcile them
without reading both scripts side-by-side.

**Concrete shapes seen**:
- Local `doc-coverage.sh` runs fmt/clippy/build/test + 2 doc-shape
  checks (6 steps). CI workflow runs the same 6 + a separate
  `cargo fmt --check` job (7 jobs). Local passes; CI fails on fmt
  drift because the local script never ran fmt-check.
- Local script runs `cargo test --workspace`; CI runs `cargo test
  --workspace --all-features`. Feature-gated test fails only in CI.
- Local script uses one cargo binary; CI uses pinned toolchain
  version. Toolchain-specific lint fails only in CI.

**Root cause**: structurally identical to F1.2 (constitution rules
with partial-scope enforcement), but applied to the enforcement
*scaffold itself*. The "N gates" rule is declared in the project
constitution; the enforcement layer has two implementations (local
script + CI workflow), and their definitions of "N" diverge silently.
Without a meta-check that script-set ⊆ CI-set, drift is invisible
until the next CI red.

**Evidence**: Cobrust Studio M5.8 sprint, 2026-05-12. Persona auditor
Sarah v2 caught the gap: local `scripts/doc-coverage.sh` reported "6
gates passed"; the GitHub Actions matrix-CI workflow added at M5 (per
Sarah v1 dispatch) ran `cargo fmt --check` as a separate job and
failed on the same SHA the local script approved. Resolution: §5b
added to `doc-coverage.sh` to run `cargo fmt --check` alongside the
existing gates, restoring script ⊇ CI invariant. See Studio case
study §4.2 and persona-driven §M5.8.

**Recovery**:
1. Establish the invariant **script ⊇ CI** (the local script runs at
   least every check the CI workflow runs).
2. Add a meta-check: a small CI job that fails if any check in
   `workflows/*.yml` lacks a corresponding step in `doc-coverage.sh`
   (grep-driven; brittle but bounds the drift).
3. When CI fails on a gate the local script didn't run, the fix is
   to extend the local script in the same PR, not to silently rely
   on CI catching it.

**Prevention going forward**: in the SAME PR that introduces a new
CI job, extend the local enforcement script to run it. The "N gates"
mandate must name a single source of truth (the local script) and
treat CI as the canonical re-runner of that script — not as a parallel
gate-set. See F26 (recursive enforcement-script closure) for the
multi-layer-review discipline this implies.

### F1.4 — Doc-coverage script enforces what it knows, README-vs-release-tag drifts silently (sub-form of F1.0)

**Symptoms**: a project's `scripts/doc-coverage.sh` enforces invariants
on artifacts it knows about — module-doc `last_verified_commit:` SHA
reachability, ADR roster completeness, findings frontmatter shape. The
script is rigorous on its declared scope. Meanwhile, the public README
ships claims that **the script has no clause for**:
- README badge shows version `vX.Y.Z` while the latest pushed tag is
  `vX.Y.(Z+1)` (badge-vs-tag drift)
- README §"Install" describes a single-platform tarball while
  `release.yml` builds a 5-platform matrix (asset-coverage drift)
- README §"Compare to X" cites old positioning while the current
  positioning was updated 3 commits ago (narrative drift)

The script is green; the public surface is stale. Discovery happens
only when a persona auditor or new visitor reads the README cold.

**Root cause**: F1.0 family — the script enforces what it knows to
enforce. Its declared scope (module-doc / ADR / finding) is rigorous;
its undeclared scope (README ↔ latest tag, README ↔ release.yml
matrix, README ↔ current positioning) is unenforced. The script
doesn't know to enforce these; nobody told it to.

**Evidence**: Cobrust Studio post-v0.1.3 sprint, persona auditor Sarah
v2 R9 finding (2026-05-12). README §"Releases" badge displayed
`v0.1.2` and §"Install" described a single-platform `aarch64-apple-darwin`
tarball, AFTER v0.1.3 had shipped with a 5-platform `release.yml`
matrix (Linux + macOS x86_64/aarch64 + Windows). `doc-coverage.sh`
green; `last_verified_commit:` rigorous on every module-doc; README
content not under any gate. See Studio case study §M5.8 and Sarah-v2
R9.

**Rule of thumb**:

> **What the doc-coverage script doesn't enforce, drifts. The script
> enforces what it knows to enforce. Anything outside its declared
> scope is on human discipline alone — i.e., it will drift.**

**Recovery**:
1. For every public-facing artifact (README, release notes, landing
   page), enumerate the claims that are bound to a current-tag value
   (badge SHA, asset names, platform matrix, version string).
2. Add a `scripts/doc-coverage.sh` clause per claim:
   - Badge SHA must equal `git describe --tags --abbrev=0`
   - Every asset URL in README must resolve via `gh api`
   - Every platform mentioned in README must appear in
     `.github/workflows/release.yml` matrix
3. Mark previously-aspirational claims (e.g. "single-platform tarball"
   wording) as ASPIRATIONAL per F1's generalized prevention rule, or
   add the enforcement.

**Prevention going forward**: when introducing a new public-facing
claim (README §"Install", release notes), in the same commit add the
script clause that enforces the claim. F1 family applied to public
surface, not just internal scaffolding. Composes with F19
(release-readiness independent install-test) and F8 (marketing
overreach without citation): F19 verifies the install path runs; F8
verifies marketing claims have citations; F1.4 verifies README claims
track current tag.

### Generalized prevention going forward (P0 SOP)

> **Any project-level rule without an automated check is security
> theater.** When you write a rule (in constitution, ADR, schema
> frontmatter, snapshot invariant, conventions doc), in the SAME
> commit add the script that enforces it. If you can't enforce it,
> mark the rule "ASPIRATIONAL" not "REQUIRED".
>
> If the enforcement scope is bounded ("checks ADR-0001..0029"), the
> rule will go stale the moment scope is exceeded. Auto-discover
> scope (glob ADR files, find by frontmatter, etc.) instead.

This is **non-negotiable** in Ballast — equivalent severity to atomic-commit
discipline and CLI fail-fast. A project with declared-but-not-enforced
rules will accumulate F1 sediment indefinitely.

---

## F2 — Codegen vs MIR layer divergence

### Symptoms

ADR §"Decision" §"Implementation map" specifies `crates/cobrust-codegen/`
file paths. P9 sub-agent reports successful fix landed in
`crates/cobrust-mir/`. The fix is correct, but the §Decision was wrong
about the layer.

### Root cause

When a bug's symptom is "if vs while diverge" or "function call vs
non-function call diverge", the natural hypothesis points at codegen
(the last-mile translation). But "if vs while" is often a MIR
construction issue (how blocks are sequenced and terminated), not a
codegen IR-emission issue.

### Recovery

1. P9 reports finding via §"Layer correction" addendum (don't rewrite
   §Decision — preserve audit trail).
2. Update SOP catalogue: future codegen-divergence ADRs default to
   dump MIR + CLIF before locking implementation map.
3. ADR §Decision §"Implementation map" lists *both* layers as
   investigation candidates, not just codegen.

### Evidence

Cobrust ADR-0033 (Ty::None inference) and ADR-0035 (lower_condition
primitive). Both spiked at codegen, both fixed at MIR. "2 strikes =
systemic blind spot" — promoted to runbook section.

### Prevention going forward

Add a "Codegen vs MIR pre-flight" SOP: any ADR §Decision proposing a
codegen change must include CLIF + MIR dumps for failing inputs in
§"Context" §"Evidence", explicitly ruling out the upper layer.

---

## F3 — Two bugs one fix (root primitive missed)

### Symptoms

Bug A: trigger pattern X, wrong value type T. Filed as separate finding.
Bug B: trigger pattern Y (different), wrong value type T (same).
Filed as separate finding.

If you fix Bug A by patching X-handling, Bug B remains. If you fix B,
A remains. **Both are surface manifestations of one root cause** in a
shared inference / fallback path.

### Root cause

Type inference / dispatch / fallback pass has a wrong default for one
class of inputs. Both X and Y trigger that path.

### Recovery

1. When two finding hypothesize the same wrong-value-type, **compare
   their root-cause sections** for overlap.
2. Find the shared primitive (e.g. `lower_condition`,
   `infer_return_type` fallback).
3. Refactor the primitive at the root layer — fix both bugs in one
   edit.
4. Document as "two-bugs-one-fix" methodology finding for reuse.

### Evidence

Cobrust ADR-0033 Option C: both `Ty::None Float→I8` (Bug A) and
`i64-mod-2 → I8 narrow-type` (Bug B) closed by threading
`inferred_locals` through `operand_ty` + `rvalue_ty` with fixed-point.

### Prevention going forward

Ballast §4 verification gates: when reviewing a finding's root-cause
hypothesis, scan all open findings for matching wrong-value-types.
If 2+ match, prioritize root-primitive fix over surface patches.

---

## F4 — Quarantine pollution (audit on broken baseline)

### Symptoms

Audit sub-agent #1 reports "L2.behavior PARTIAL-FAIL" while another
sprint #2 is mid-flight fixing a known codegen bug. The audit's
"fail" signal is contaminated — root cause might be the codegen
bug being fixed, not the audit subject.

### Root cause

Audit started before known-bad-baseline was patched. Audit's findings
will need re-validation post-patch.

### Recovery

1. SendMessage to in-flight audit agents: "your baseline is dirty,
   await codegen fix merge before reporting [P9-COMPLETION]".
2. Have a written **quarantine SOP**: which sprints can run on which
   baselines.
3. Codegen sprint completes → SendMessage audit agents: "fixed at
   <SHA>, re-run validation, then report".

### Evidence

Cobrust `findings/audit-1-codegen-pollution-quarantine-sop.md`.

### Prevention going forward

CTO 守闸 protocol: before dispatching an audit sprint, check that:
- No codegen / MIR / type-system sprints are in flight
- All recently-merged sprints have completed 5-gate
- HEAD is at a known-clean SHA, not mid-merge

---

## F5 — Silent miscompile (verifier reject + binary still emit)

### Symptoms

User runs `tool build foo.cb`. Output: "Cranelift verifier error:
inst441 (...) type mismatch". Then: "linked /tmp/foo". User runs
`/tmp/foo` and gets wrong stdout.

### Root cause

Tool's CLI catches the verifier error (prints it), but doesn't
propagate the Err — continues to emit a binary anyway. Binary may run
but produce wrong values.

### Recovery

1. P0 priority: CLI fail-fast. Verifier rejection → propagate Err →
   exit non-zero.
2. Add regression test: feed a known-bad IR, assert exit code ≠ 0
   AND no binary written.

### Evidence

Cobrust commit `78ca779` "P0 CLI hardening — lock verifier-reject
exit-3"; finding `codegen-i8-i64-mismatch-at-4-blocks.md` §"Bug 2".

### Prevention going forward

Ballast §4 verification gates: every verifier in the pipeline must
contract that "verifier Err" → "tool exit ≠ 0", and this contract is
itself tested via a negative test.

---

## F6 — Push permission 403 / namespace assumption

### Symptoms

External review agent or sub-agent runs `git push origin feature/X`.
Result: HTTP 403 "permission denied". Push aborts; review work isn't
visible at remote.

### Root cause

Repo namespace is `Org-X/repo`, not `org-x/repo`. Or the agent's
account has read-only access. Or the repo isn't public yet.

### Recovery

1. Discover via `git push --dry-run` or by asking the human directly.
2. All dispatch prompts that say "git push" should be "open PR via
   `gh pr create`" — never assume push permission.
3. Hooks that fail on 403 should degrade to info-level, not abort the
   shell session.

### Evidence

Cobrust 10th review post-T1.1 cleanup discovery. Actual namespace was
`Cobrust-lang/cobrust`, not `cobrust/cobrust` (review-claude assumed).

### Prevention going forward

Ballast §1 Topology: external review agent's prompt always specifies
"do not push; draft PRs only". External review runs `git push
--dry-run` first; on 403, reports through chat instead of attempting
push retry.

---

## F7 — Strategic blindness (only tactical reviews)

### Symptoms

After 10+ reviews, every review is "snapshot is stale" / "codegen
edge case" / "this sprint missed a footnote". Zero reviews ask "what
problem is this project actually solving?" / "who's the user?" / "1-year
plan?".

The project may be technically sound but strategically lost.

### Root cause

Tactical review is naturally what the codebase invites — there's
always something incomplete. Strategic review takes effort; humans
forget to schedule it.

### Recovery

1. Force a strategic review every N tactical reviews. Cobrust
   experience: N = 10 was too high; recommended N = 5.
2. Strategic review writes 6/12/60-month plan in falsifiable form.
3. Compare current sprint roadmap against plan; identify drift.

### Evidence

Cobrust 10th review (this skill's birthplace; the review user
triggered with "一直局限于短期目标"). Without this trigger, project
would have continued tactical-only indefinitely.

### Prevention going forward

Ballast §5 mandates a strategic review every N=5 tactical reviews.
Calendar reminder if no strategic review in last 5 turns. Strategic
review must produce 6/12/60-month plan with falsifiable success
criteria; "deferred" lists without trigger + done-means + effort are
fantasy not plan.

---

## F8 — Marketing overreach (claims without citation)

### Symptoms

README says "5-50× faster" or "scales to millions of users" or "10x
fewer bugs". No citation, no benchmark file, no measurement methodology.

### Root cause

Marketing copy gets drafted by agents that didn't run the benchmarks.
Numbers are pulled from competitor literature ("Mojo says 35,000×")
or from human aspirations.

### Recovery

1. Replace specific claims with measured ranges + citation.
2. Example: "5-50× faster" → "9-14× faster on tomli (T1.1 measured
   vs CPython 3.11 tomllib, see ADR-0039)".
3. Apply to all public-facing copy: README, blog posts, slide decks.

### Evidence

Cobrust post-T1.1 cleanup §T2.B: "5-50× faster" walked back to
empirical measurement. Caught by external claude-desktop, not
review-claude (whose draft introduced the overreach).

### Prevention going forward

Ballast §4 verification gates extend to marketing copy: any "X is faster
than Y" or "scales to N" claim cites a specific experiment file.
"Faster than competitor" without measurement = walked back claim
liability.

---

## F9 — Wrong root-cause hypothesis cited in ADRs

### Symptoms

Finding §"Root-cause hypothesis" guesses "bug is in X layer".
Subsequent ADR §Decision §"Implementation map" cites X layer.
Empirical fix lands in Y layer (one up). ADR has retro-active layer
correction.

### Root cause

Finding hypothesis sections aren't marked as speculative. Other
documents quote them as ground truth.

### Recovery

1. ADR §"Layer correction" addendum (preserve audit trail).
2. Update finding to mark §"Root-cause hypothesis" as
   "speculative — verify before quoting".
3. Update finding-template to require speculative mark up front.

### Evidence

Cobrust ADR-0033 + ADR-0035 both: spike at codegen, fix at MIR.
review-claude owned this in 8th review.

### Prevention going forward

Finding-template.md mandates `## Root-cause hypothesis (speculative — verify before quoting)`. ADRs that quote a hypothesis must state
"per finding X §Hypothesis (speculative)" not "per finding X
§Hypothesis (ground truth)".

---

## F10 — Cargo registry lock contention at high parallelism

### Symptoms

3+ parallel sub-agents, each running `cargo build` in their own
worktree. One sprint times out at exit 144 (SIGUSR2). Others
succeed slowly. Total wall-clock is 2-3× what it should be.

### Root cause

Cargo's global registry index uses a single lock under
`~/.cargo/registry/index/`. Parallel cargo runs serialize on this
lock. Beyond N=4 simultaneous, contention becomes pathological.

### Recovery

1. Cap parallelism at N=4 simultaneous sub-agents (Cobrust ADR-0002
   constitutional ceiling).
2. Sprint scheduling: if 4 already running, queue rather than fire.
3. Cargo offline mode (`cargo build --offline`) avoids index lock but
   requires pre-warmed cache.

### Evidence

Cobrust topology finding (`findings/multi-agent-cobrust-topology.md`).
Witnessed once at 6-way parallel during M-batch sprint.

### Prevention going forward

Ballast §1 Topology: 4-way parallel sub-agent ceiling. CTO dispatch
counter; if 4 concurrent, queue.

---

## F11 — Skip-pattern scattered across test files

### Symptoms

3 different test files have 3 different skip patterns:
- `real_llm_smoke.rs`: `if env::var("USER_CODEX_API_KEY").is_err() return`
- `audit_3a_tomli.rs`: similar but slightly different message
- `msgpack_pyo3.rs`: `if !python3_present() return` with yet another helper

Each new test file adds yet-another-skip-helper. Eventually maintenance
debt.

### Root cause

No shared `cobrust-test-utils` crate with `skip_if_missing(env_var)`
/ `skip_if_no_python3()` helpers. Each P7 invents its own.

### Recovery

1. Don't refactor in the middle of a sprint (out of scope).
2. Add `good-first-issue` to extract shared helpers when convenient.
3. New test files should grep first for existing skip patterns and
   reuse if found.

### Evidence

Cobrust post-T1.1 cleanup sprint — review-claude flagged 3 skip
patterns scattered, marked as "out-of-scope-but-flagged".

### Prevention going forward

Ballast §3 Documentation discipline: when a P7 introduces a 2nd
implementation of a pattern (e.g. 2nd skip helper), flag in PR
review. CTO can choose: refactor now (extract helper) or accept debt
+ file `good-first-issue`.

---

## F12 — Thinking-model output starvation (TWO SUB-FORMS)

### F12.0 — Configuration trap (output-disciplined thinking model)

#### Symptoms

LLM A returns 20/20 oracle pass on translation task. LLM B same prompt
returns 0/20. Naive interpretation: "B is dumber than A".

#### Root cause

LLM B is a **thinking model** with REASONABLE output discipline. It
allocates ~15-25% of completion budget for output, but the experimental
default `max_tokens=4096` is too tight for verbose reasoning + output.

`finish_reason=length`, no output emitted, but with budget increase
(8K-16K) model reaches output stage and produces correct code.

#### Recovery

1. Inspect raw response for `<think>` block + finish_reason
2. If `finish_reason=length` AND thinking-class: increase `max_tokens` to 16K-32K
3. Re-run; if produces correct output → confirmed F12.0 (configuration trap)

#### Evidence

Hypothetical for Cobrust scope; gpt-o1 / claude-opus-thinking are
typical examples. Cobrust experiment with **gpt-5.5 at 4K** ran
correctly so didn't hit this trap (output-disciplined alignment).

### F12.1 — Convergence failure (output-undisciplined thinking model)

#### Symptoms

Same as F12.0 surface: thinking model returns 0/20, `finish_reason=length`.
**But** budget increase (4K → 16K) does NOT help — still 0/20, still
all budget consumed by reasoning, still 0 output tokens.

#### Root cause

LLM has reasoning capability but **lacks output convergence
discipline**. Reasoning tokens scale with budget, never converge to
"commit to draft and emit". Model keeps exploring design alternatives
indefinitely.

Trace evidence (visible in `<think>` block when raw response inspected):
- N restarts of the same function definition (e.g. "let me reconsider")
- Multiple internal code drafts within `<think>`
- Reconsidering side concerns ("should comments be included", "is X
  available in std")
- Final draft (if any) reached only as budget runs out

#### Recovery

Budget increase does NOT work. Use one of:

1. **Convergence-directive prompt prefix** (try first):
   ```
   You must emit your final answer within N tokens. After
   ≤<budget*0.7> tokens of reasoning, commit to your draft and
   produce output.
   ```
2. **Provider exclusion**: if convergence directive doesn't help, do
   not use this provider for production translation backends. Cost is
   high (284 sec / 17K tokens for 0 output observed for minimax-m2.7
   at 16K) and consensus mode collapses.
3. **Consensus voter resilience**: treat "no output" as `None` vote,
   weight other providers more heavily; don't penalize correct providers
   when one peer fails.

#### Evidence

Cobrust LLM A/B comparison experiment, 16K rerun 2026-05-11:

- minimax-m2.7-highspeed at max_tokens=4096: 0/20, 4096 reasoning / 0 output
- minimax-m2.7-highspeed at max_tokens=16384: **still 0/20**, 16384 reasoning / 0 output, 7 restarts of `pub fn dedent` visible in `<think>`, last complete draft reached at 71880 chars with only 1 byte budget remaining
- Per sub-agent: "reasoning is not getting closer to convergence as budget grows; it's just exploring more design alternatives"

`<external LLM bench experiment data, not in this repo>` §"Fair rerun"

### How to distinguish F12.0 vs F12.1 empirically

**Run the budget escalation test**: 4K → 16K → 32K. If pass rate
improves with budget → F12.0 (configuration trap). If stays at 0/20
across all 3 → F12.1 (convergence failure, exclude or prompt-engineer).

**Don't** predict outcome from theory; theory said "budget bigger =
better output" before this experiment. Refuted at 16K. **Always run
the verification.**

### Prevention going forward

Cobrust ADR-0004 router must:
- Maintain per-provider **convergence-class registry** (not just `thinking_model: bool`):
  - `non_thinking` (standard, 4K)
  - `thinking_disciplined` (gpt-o1, claude-thinking; 8K-16K)
  - `thinking_undisciplined` (minimax-m2.7-highspeed; needs prompt or exclude)
- Track per-provider **cost-per-successful-translation**, deprioritize
  high-cost-per-failure providers
- Support **convergence-directive prompt prefix** as opt-in for
  undisciplined providers
- Consensus voter accept "no output" as None vote

## F13 — Plan-vs-execute coherence gap (smaller-model failure)

### Symptoms

LLM produces compile-clean code that fails specific oracle test cases.
Inspecting the model's `reasoning_content` (chain-of-thought), the model
**correctly identified in prose** the rule that the failing cases test — but
the emitted code does NOT implement that rule.

### Root cause

Smaller-parameter LLMs compensate weight-deficit with verbose reasoning.
During reasoning they enumerate edge cases correctly. During code emission,
attention drops back to "common path" patterns and edge-case rules are
omitted. The plan and the execution diverge silently.

### Recovery

1. For closed-loop verification (L0..L3 gate-driven systems): repair loop
   catches the gap; smaller models are acceptable inside such systems.
2. For one-shot use: smaller models are NOT trustworthy.
3. Mitigation: prompt include "after reasoning, list each rule from your
   reasoning, then for each rule emit the code that implements it" as a
   forcing function.

### Evidence

Cobrust LLM A/B comparison 2026-05-11, gpt-5.4-mini run:

> "model 'thought hard' (6773 reasoning tokens, ~1.5× visible code length),
> even noted in reasoning_content: 'whitespace-only line turns into an
> empty line, which keeps the newline count intact'. It correctly identified
> the normalization step in prose **but forgot to actually emit code** for it.
> Pure planning-to-execution gap. 16/20 oracle pass; 4 cases failing on
> truly-empty-line edge."

`<external LLM bench experiment data, not in this repo>` §"Mini's plan-vs-execute coherence gap"

### Prevention going forward

Ballast §1 multi-agent audit + Cobrust LLM Router:
- Track per-model **plan-vs-execute coherence**: % of test cases failing
  on rules the model explicitly identified in reasoning_content
- For closed-loop translators: smaller models OK with verifier+repair-loop
- For one-shot: rank models by coherence, prefer high-coherence even if
  more expensive

---

## F14 — Endpoint silent model swap

### Symptoms

LLM gateway returns successful response but `response.model` field
differs from `request.model`. E.g. requested `gpt-5.2`, response says
`"model": "gpt-5.4"`. Same with `gpt-5.3-codex` → `gpt-5.4`.

### Root cause

LLM gateways (codex, OpenRouter, Together, etc.) often aggregate multiple
upstream models. They may:
- Advertise N models on `/v1/models` but actually serve M < N (some are
  deprecated / removed but still listed)
- Alias certain model_ids to a "current best" backend (`gpt-5.2` → silently
  routes to `gpt-5.4`)
- Rate-limit certain models and silently fall back to others under load

### Critical implications

1. **A/B comparison invalidated** when 2 supposedly-different models actually
   share backend. Comparing "gpt-5.2 vs gpt-5.5" can become "gpt-5.4 vs
   gpt-5.5" without telling you.
2. **Consensus mode broken**: ADR-0004 §"consensus mode" assumes n=2 votes
   from genuinely-different models. If both votes come from same backend
   (silently aliased), it's 1 vote with 2 wrappers — false consensus.
3. **deterministic_id broken**: hash(source + toolchain + router_decisions)
   doesn't capture gateway aliasing. Same hash, two different request
   model_ids, gateway might serve different backend at different times.

### Recovery

1. Router MUST verify `response.model == request.model` after every dispatch
2. Log warning on mismatch; fail-fast if `strict_model_match: true` config
3. Ledger entry must record BOTH `request.model` and `response.model` (Cobrust
   ledger schema needs `backend_model` field added to ADR-0031)
4. deterministic_id must hash the FULL request body (not just user prompt)
   so gateway-injected presets affect the build_id

### Evidence

Cobrust LLM A/B comparison 2026-05-11:
- Requested `gpt-5.2`, response.model = "gpt-5.4"
- Requested `gpt-5.3-codex`, response.model = "gpt-5.4"
- Same backend (gpt-5.4), 3 different request.model values, **3 different
  output qualities** (20/20 vs 0/20 vs 20/20) — gateway preset injection
  inferred but unverified

### Prevention going forward

Cobrust ADR-0004 amendment:
- Add `silent_swap_check: bool = true` to provider config
- Router compares request.model vs response.model after every call
- Ledger schema (ADR-0031) extended with `request_model` + `backend_model` separate fields
- Provider documentation flag `known_aliasing: true | false`

Ballast §1 multi-agent audit:
- For any LLM-result audit, include "model_returned consistency check" as
  a verification dimension
- Don't trust `/v1/models` list as ground truth for what's served

---

## F15 — Single-difficulty A/B overgeneralization (bench methodology failure)

### Definition

An LLM A/B comparison run on a single task difficulty tier concludes
"model X is not measurably better than model Y." That conclusion is then
used to make routing decisions. A second experiment at a harder task tier
refutes the conclusion — the gap only appears at the harder tier.

### Symptoms

- Round 1 report: "5.5 not measurably better than 5.4 on this task"
- Recommendation based on Round 1: "use 5.4 as default (saves 13% tokens)"
- Round 2 result: at harder task, 5.4 = 50/51 vs 5.5 = 51/51 — gap now
  visible (2% accuracy advantage at hard tier)
- Downstream: Cobrust ADR-0004 / ADR-0007 routing recommendation potentially
  incorrect if adopted after Round 1 only

### Root cause

The "no measurable difference" claim is tier-local, not universal. Easy
tasks don't differentiate models because both produce correct output at
ceiling — no headroom to distinguish alignment quality. Hard tasks expose
ceiling: model X reaches 51/51, model Y plateaus at 50/51 due to one
genuinely tricky edge case.

Pattern: researcher runs minimum viable experiment (N=1 difficulty tier),
gets a clean result ("equal"), stops there. The stopping rule is implicit:
"if they're equal, no need for more data." This is epistemically wrong for
model comparison — absence of difference at easy tier is not evidence of
absence at hard tier.

### Evidence

Cobrust LLM A/B comparison 2026-05-11:

- **Round 1** (textwrap.dedent, stateless leaf fn, ~90 LOC): gpt-5.4 = 20/20,
  gpt-5.5 = 20/20. Conclusion: "5.5 not measurably better than 5.4 on this
  task."
- **Round 2** (urllib.parse.urlparse, 7 mutually-dependent fns, ~266 LOC,
  stateful + cross-fn dependency): gpt-5.4 = 50/51, gpt-5.5 = 51/51.
  "Round 2 result REFUTES that generalization."

Source: `<external LLM bench experiment data, not in this repo>` §"Round 2" and §"Own #6"

Own #6 (analysis file): "Single-difficulty experiment cannot generalize
to 'model X better than Y' claims."

### Rule of thumb

> **"Equal at easy" ≠ "equal at hard."**
> Any model comparison claiming "no measurable difference" is invalid unless
> it includes at least 2 difficulty tiers (simple stateless leaf + complex
> stateful multi-function). Document which tier the claim applies to. Never
> let a tier-1 result alone drive production routing decisions.

### Recovery

1. Re-run comparison at ≥1 harder task tier before finalizing routing.
2. Label every model-comparison claim with the task tier it covers:
   `"on stateless leaf tasks"`, `"on 7-fn stateful cluster"`, etc.
3. Routing table entries should specify tier scope:
   - stateless leaf → 5.4 (both equal, prefer cheaper)
   - stateful / complex multi-fn → 5.5 or consensus (5.5 wins at hard tier)
   - cross-lib L2 fuzz → consensus best-of-2 (genuinely different alignment)

### Prevention going forward

Ballast bench methodology (see `BENCH-METHODOLOGY-v1.md` §3 "10-axis framework"):

- **Multi-tier coverage** is a mandatory axis in any model A/B experiment.
- Stopping rule: experiments conclude only when ≥2 tiers are compared AND
  both show same directional result (or tier-split is explicitly documented).
- Any ADR routing recommendation cites the tier(s) at which the comparison
  was measured.

---

## F16 — Post-compaction P10 identity drift (F1 Sediment Family, identity sub-form)

> **F1 sub-form.** Declaration: skill description asserts CTO-level identity
> and read-only authority boundary. Enforcement: none that survives context
> compaction. Result: post-compaction agent slips from P10 CTO to P7
> hands-on coder.

### Definition

An agent's role identity (CTO, reviewer, orchestrator) is declared in a
skill description or dispatch prompt. That declaration is never anchored in
auto-memory or any survives-compaction storage. After a context compaction
event, the identity declaration is lost from the active context. The agent
drifts toward default behavior (hands-on coding) in absence of the
role-anchoring reminder.

### Symptoms

- CTO agent dispatches sub-agents correctly for first N turns
- Context compaction event (long session, many tools calls, explicit `/compact`)
- Post-compaction: agent begins writing implementation code directly, not
  delegating; stops producing ADR spikes; stops verifying P9 completions
  against gate criteria
- Duration: 15–30 minutes of drift before human notices and corrects
- Recovery trigger: user explicitly re-states role ("你是 CTO，不是在写代码")

### Root cause

1. Role identity is declared in skill description (loaded at session start).
   Skill description does not survive compaction — it's conversation context,
   not persistent memory.
2. Auto-memory files (MEMORY.md, project_state_snapshot.md) anchor project
   state (commits, ADRs, test counts) but do NOT anchor the agent's
   behavioral role constraints.
3. Default LLM behavior absent role context: code-writing is the path of
   least resistance. CTO abstract-planning requires active constraint.

### Evidence

Cobrust Day 11, ~15:00: CTO post-compaction 20-minute episode of hands-on
coding. Observed in current review-claude session: Ballast methodology skill
declares "A4 of review-claude audit team, read-only against main repo."
Without this declaration surviving compaction, drift to general-purpose
tool-calling is inevitable.

Pattern is structural: F16 predicts that any sufficiently long CTO or
review-claude session will drift post-compaction, regardless of skill
description quality, unless identity is also anchored in auto-memory.

### Rule of thumb

> **Any declared role that must survive a compaction event must be written
> into auto-memory, not only into a skill description.**
>
> Corollary: compaction resilience is a first-class property of role
> design. Test it: deliberately compact context mid-session and verify the
> agent still behaves consistently.

### Recovery

1. Add a "role anchor" block to the project's `MEMORY.md`:
   ```
   - [CTO role constraints](cto_role_constraints.md) — identity boundaries
     that MUST survive compaction; read immediately when context compacted
   ```
2. `cto_role_constraints.md` lists: role level (P10 CTO), prohibited actions
   (writing implementation code directly, skipping ADR spike), required
   behaviors (4-way parallel dispatch max, Phase 1 spike before every P9).
3. On session resume post-compaction, reading `MEMORY.md` → following its
   links restores role context, not just project-state context.

### Prevention going forward

Ballast §6 Workflow Discipline: "Role identity constraints must be anchored in
auto-memory, not only in skill descriptions. Skill descriptions serve
initialization; auto-memory survives compaction."

Add a "compaction resilience check" to any Ballast project setup: on first
turn after `/compact`, the agent should read `MEMORY.md` before taking any
action, and MEMORY.md must include role anchor links.

---

## F17 — Sub-agent KPI self-report fidelity gap (F1 Sediment Family, self-report sub-form)

> **F1 sub-form.** Same family as F1.1 (declared invariants without
> enforcement) and M10 SHA hallucination. The claim is in a self-authored
> report; the claim is not ground-truthed against repo state.

### Definition

An agent (sub-agent or CTO) generates a completion report claiming specific
quantitative deliverables ("Memory 沉淀: 3 items codified", "N ADRs added",
"tests: 2,541 passing"). The claim is written from internal state / memory /
prior context, not freshly verified against the repo. The actual repo state
does not match the claim.

### Symptoms

- CTO completion card says "Memory 沉淀: X codified failure modes"
- `grep -rn "F<X>" docs/agent/` returns 0 hits
- Snapshot says "tests: 2,541" but `cargo test --workspace` returns 2,611
- ADR roster claims 39 entries but `ls docs/agent/adr/*.md | wc -l` = 37
- Audit sub-agent says "findings/ directory reviewed" but grep shows it missed
  3 recently-added finding files

### Root cause

Self-reports are written from the agent's context state (what it remembers
writing this session) rather than from fresh repo inspection. Two failure
modes:

1. **Memory drift**: agent accurately recalls what it intended to write but
   not what actually landed on disk (edit failed silently, wrong path, wrong
   content).
2. **Scope creep**: agent's self-description expands to include things "in
   progress" or "in context" that aren't yet committed to the repo.

This is structurally identical to F1.1 (declared invariants without CI lint):
the self-report is a declaration; there is no enforcement step (grep/wc)
that verifies the declaration against ground truth before the report is
signed off.

### Evidence

Cobrust Day 11 review session: CTO post-compaction KPI card claimed
"Memory 沉淀: X codified" referring to Ballast failure mode entries. Actual
grep of `./reference/failure-modes-catalogue.md`
showed the claimed entries were not present — zero matching content for
the claimed F-numbers.

Same pattern as M10 sub-agent SHA hallucination (`m10-sha-pin-hallucination`
finding): agent wrote SHA pins confidently from context-state; actual GitHub
Actions resolved the pins to 404 (fake 40-char hex). F17 is the self-report
analog of that implementation failure.

Reference: MEMORY.md note "[Verify quantitative claims at smoke-check]" —
CTO memory file explicitly encodes this lesson, confirming it has recurred
enough to warrant permanent memory entry.

### Rule of thumb

> **Any quantitative claim in a completion report must be ground-truthed
> with a verification command before the report is signed.**
>
> Template for every sub-agent completion block:
> ```
> ## Verification (run before submitting this report)
> - [ ] grep -c "F<N>" <catalogue_path> → expected: ≥1 hit per claimed entry
> - [ ] ls <findings_dir>/*.md | wc -l → expected: N (matches "N findings added" claim)
> - [ ] cargo test --workspace --locked 2>&1 | tail -3 → actual test count
> ```

### Recovery

1. When auditing a self-report, grep every quantitative claim before trusting it.
2. P9/P7 dispatch prompts must include a "Verification block" section that
   requires the sub-agent to run verification commands and paste raw output
   as evidence before `[P9-COMPLETION]` / `[P7-COMPLETION]`.
3. CTO 守闸 protocol: do not merge a sprint without independently verifying
   the claimed test count via `cargo test --workspace --locked`.

### Prevention going forward

Ballast dispatch prompt template (`templates/dispatch-prompt-p9.md`):

- Add mandatory §"Verification commands (run before submitting)" section
- Sub-agent must paste raw command output (not paraphrase) for every
  quantitative claim: test count, finding count, LOC added, ADR numbers
- CTO's role at merge: spot-check ≥1 quantitative claim per sprint, not
  trust all claims at face value

MEMORY.md note "Verify quantitative claims at smoke-check" is already
present in Cobrust project memory — this F17 entry codifies the pattern
for the Ballast catalogue so it applies to any future Ballast project.

---

## F18 — Attribution policy without dir-scope enforcement (F1 Sediment Family, scope sub-form) [CANDIDATE]

> **F18 is a candidate entry** — pattern observed once with partial evidence.
> Promote to confirmed when second instance observed in a different project.
> F1 Sediment Family sub-form: policy declares scope ("review-claude owns
> findings/"), enforcement is human convention only, agent in adjacent role
> violates scope because policy isn't mechanically enforced.

### Definition

An attribution or ownership policy declares that agent A owns files in
directory D ("findings/ entries are review-claude original drafts").
The policy does not have a mechanical enforcement mechanism (file
permission, CI lint, commit hook). A second agent (P7 sonnet, sub-agent
P9) writes to or edits files in D as part of an adjacent task, violating
the policy without receiving any error.

### Symptoms

- README §Attribution says "all findings/ entries are review-claude authored"
- P7 sonnet sub-agent edits a file in `findings/` or a section of README that
  review-claude owns as part of a broader cleanup sprint
- No error; the edit succeeds; the attribution becomes stale
- Discovery: only via manual audit comparing file commit history vs
  `discovered_by` frontmatter

### Root cause

Directory ownership is policy-level (documented in README), not
enforcement-level (file permissions, git attributes, CI lint). P7 agents
given a broad scope ("fix all stale content") do not distinguish
policy-owned files from general-purpose files. Without enforcement,
the policy is documentation only — F1 family pattern applied to
attribution rather than schema invariants.

### Evidence

Cobrust Day 11 (2026-05-11), early afternoon: a P7 sonnet sub-agent
dispatched for a broad cleanup sprint edited README narrative sections
that review-claude considered its own authoring territory. The
boundary violation was paraphrased in the review-claude session's
own-up log (review-claude session 4bb35f43, paraphrased as: "P7 broad-
cleanup spawn edited review-claude's narrative §F without scope-
exclusion guard in dispatch prompt"). The literal handoff-README
text content at that line had evolved over multiple turns, so the
canonical citation is the pattern description, not a verbatim quote.

The attribution policy was stated in `review-claude-handoff/README.md`
§"Attribution policy": "findings/ entries are review-claude originals —
each file's `discovered_by:` frontmatter marks source." P7 had no
machine-enforcement signal preventing the edit (no CODEOWNERS, no
dispatch-prompt-level exclusion list).

Note: This is a **candidate F18** because (a) it was observed in a single
session, (b) the root-cause was partially ambiguous (was it P7 ignoring
policy or policy not being communicated in the dispatch prompt?). A
cleaner second instance would confirm the pattern.

### Rule of thumb

> **Directory ownership policies must have mechanical enforcement, not just
> documentation.**
>
> Options in ascending strength:
> 1. Include explicit "do not edit files in X/" in every dispatch prompt that
>    could touch adjacent files (cheapest, but still relies on agent reading)
> 2. `.github/CODEOWNERS` + branch protection: require review from owner on
>    any PR touching the owned directory
> 3. CI lint: any commit touching `findings/*.md` that doesn't have
>    `discovered_by: review-claude` in frontmatter → fail
>
> Option 1 is the minimum. Options 2–3 scale to higher-stakes directories.

### Recovery

1. Add explicit "do not edit" guards to dispatch prompts for any sprint
   touching files adjacent to owned directories.
2. After any broad cleanup sprint, audit owned directories via
   `git log --oneline --diff-filter=M -- findings/*.md` to spot unexpected
   edits.
3. If edit occurred: restore file from `git show HEAD~1:findings/file.md`,
   re-apply only the legitimate changes.

### Prevention going forward (for Ballast projects adopting this pattern)

When declaring attribution/ownership policies:
1. List the enforcement mechanism in the policy statement itself:
   "findings/ is review-claude-owned — CODEOWNERS enforces review"
2. If no enforcement mechanism: mark the policy "ASPIRATIONAL" per F1's
   generalized prevention rule
3. Any dispatch prompt for a broad-scope sprint (cleanup, doc pass, README
   refresh) must include a §"Excluded paths — do not edit" section listing
   owned directories

---

## F19 — Public-facing onboarding text written but never independently install-tested (F1 Sediment Family, install-test sub-form)

> **F1 sub-form, confirmed**. Same family as F1.1 (declared invariants without enforcement). The text claims an install path; the install path is never executed in a clean shell by the writer. F19 is high-blast-radius: failures land on every new user's first impression, not on internal dev productivity.

### Definition

A release artifact (README quickstart, release notes, GitHub Release body, install script, `cargo install` command, `curl -L` URL) ships to public users without anyone running the documented commands in a clean shell before publish. The text passes review by being read; it fails reality by being run.

### Symptoms

- `README.md` says `cargo install foo-cli` but the package is not on crates.io (path-deps not published) → user gets `error: could not find foo-cli in registry`
- Release notes list `cobrust-v0.1.1-x86_64-apple-darwin.tar.gz` but `release.yml` never built that target → user gets HTTP 404
- README's dynamic URL builder via `$(uname -sm | tr ' ' '-')` builds `Darwin-arm64.tar.gz` but the actual asset is named `aarch64-apple-darwin` → 404 on Apple Silicon Macs
- GitHub Release body references action SHAs that don't resolve (typo'd / hallucinated commit hash) → CI red on the release branch
- Quick-start uses `curl -L ... | tar xz` but server doesn't follow redirect on plain `-L` without `-fsSL` → empty extraction, opaque error

### Root cause

Two compounding patterns:

1. **Author writes from intent**: "this is how install should work" — writer's mental model of the asset naming convention or registry state, not the actual file on disk / artifact in release.
2. **No clean-shell verification step**: standard PR review reads the README diff in GitHub UI. Reviewer does not `cd /tmp && bash <(paste commands)`. So the text passes review by being plausible, not by being executable.

Same structural pattern as F1.1: declaration (install path) + missing verification step (run in clean shell). F17 (self-report fidelity) is the report analog; F19 is the user-onboarding analog. Both are F1 family.

### Evidence

Cobrust 24-hour window 2026-05-10 → 2026-05-11, three consecutive instances:

1. **M10 hallucinated SHA pins (v0.1.0 tag)**: M10 sub-agent SHA-pinned 4 GitHub Actions to fake 40-char hex with confident `# v4.2.2` comments. 13/14 CI jobs failed at action resolution, leaving v0.1.0 tag with red CI for ~4 hours until user spotted. Recovery: revert to tag form (`@stable`, `@v4`).
2. **v0.1.1 install path 404 (release notes)**: release notes listed `cargo install cobrust-cli` (package not on crates.io, path-deps unpublished) and curl URL `cobrust-v0.1.1-x86_64-apple-darwin.tar.gz` (release.yml never built x86_64-apple-darwin). Mei persona audit + Layer 3 review-claude curl test caught both. Recovery: change install command to `cargo install --git ...`, remove non-existent asset URL.
3. **v0.1.2 release-readiness audit (mechanism validated)**: §A.3 dispatched a release-readiness sub-agent before public announcement. Agent ran the documented curl commands in clean shell, surfaced friction (`curl -L` without `-fsSL` left empty extractions on some platforms). Friction was fixed pre-release **and back-ported to v0.1.1's notes** (`4baea69 docs(release): back-port -fsSL curl flag to v0.1.1 release notes`). This is the closure cycle: BLOCK → fix → re-test → GO. **First validated execution of F19's prevention mechanism in the wild.**

### Rule of thumb

> **Any public-facing install / quickstart / release command must pass independent execution in a clean shell before publish.**
>
> Mandatory release-readiness gate:
> ```
> # In a /tmp/release-test-<sprint> directory with no env vars from dev box:
> 1. Run each `cargo install` / `curl -L` / install command verbatim from the doc
> 2. For each URL: curl -fsSL -o /tmp/check.tar.gz <URL> ; echo "HTTP $?"
> 3. For each command: confirm exit 0 + expected stdout
> 4. Block merge if any command fails
> ```
> Spawn a dedicated **release-readiness agent** for this — not the same agent that wrote the docs (avoid F1.1 self-attestation pattern).

### Recovery

1. **Immediate**: if a 404 install URL is in a published release, edit the release body via `gh release edit <tag> --notes-file <fixed>.md` and force-push a docs commit on main. Tag itself is immutable, but body + asset uploads are not.
2. **Workspace version**: if `Cargo.toml` workspace.package.version was not bumped before tag, the prebuilt binary will report wrong version → user files bug → confidence damaged. Bump version BEFORE tag in every release SOP.
3. **Backport friction fixes** to prior releases: if you find `curl -L` should have been `curl -fsSL`, back-port via `gh release edit v0.1.1` so old release pages also fix. Don't leave half the user base hitting a known-fixed friction.

### Prevention going forward

In every project adopting Ballast:

1. **Add release-readiness as a tier-0 verification step** in `cto_operations_runbook.md` §"Dispatching a new P9": for any commit touching `README.md` / `docs/releases/*.md` / GitHub Release body / `release.yml`, spawn a P7 sonnet release-readiness agent that runs install commands in a clean shell and reports `[P7-RELEASE-READY-VERDICT] GO / BLOCK`.
2. **Release-readiness agent prompt template** in `templates/dispatch-prompt-p7.md` (release-readiness flavor): the agent's job is to be skeptical of the docs it's auditing, run every command verbatim, paste raw exit codes + sizes as evidence.
3. **CI lint** (stretch): a release-time CI gate that resolves each URL/asset listed in release notes via `gh api` and fails if any returns 404. This is the F1 family enforcement mechanism.

### Closure: BLOCK → fix → GO cycle as validation

The validation that F19's mitigation works is itself empirical: v0.1.2's release-readiness audit produced a BLOCK verdict, the friction was fixed (back-port + new asset naming), the next audit returned GO. The system worked. Any project adopting this pattern should expect: first 1-2 releases produce BLOCK verdicts; over time, BLOCKs become rare because the writing convention internalizes the verification step.

---

## F20 — Constitution mandate written but workflow never aligned (F1 Sediment Family, mandate-vs-workflow sub-form)

> **F1 sub-form, confirmed**. A project constitution declares a binding rule ("test-first development", "atomic commits", "no `unwrap()` in non-test code"). The dispatch SOP, daily workflow, and reviewer checklist never align to enforce the rule. The constitution becomes aspirational marketing; the workflow runs unconstrained.

### Definition

The project's foundational document (CLAUDE.md, constitution, README §Principles) states a binding development rule. Implementation of that rule requires a corresponding step in the workflow: dispatch prompt template field, CI gate, pre-commit hook, reviewer checklist item. The workflow step is missing or unenforced. Code continues to be written without violating the constitution textually (no one disputes the rule), but the rule is never actually exercised.

### Symptoms

- Constitution §"Test-first": "failing test before implementation" — but every sprint's commits show `feat(X): implementation + tests in same commit`. Test-first ordering is impossible to verify from the diff.
- Constitution §"Atomic commits, code + tests + docs same commit" — but findings get added in separate doc-cleanup commits days later.
- Constitution §"No `unwrap()` in non-test code; use `expect("rationale")` instead" — `grep -r 'unwrap()' crates/*/src/` returns N hits, none with rationale.
- Project memory `feedback_subagent_model_tier.md` says "Opus for hard / sonnet for easy / haiku NEVER" — but P9 dispatch prompts consistently use sonnet without difficulty assessment, occasional spawns of haiku for trivial doc rewrites.

### Root cause

Two compounding patterns:

1. **Mandate is text-level, not workflow-level**: writing the rule in CLAUDE.md feels like enforcing it. But the rule exists in agents' context only at session start; after compaction or sub-agent spawn, the rule is not re-asserted.
2. **No enforcement scaffold built alongside the rule**: when the constitution is drafted, the corresponding CI lint / dispatch prompt field / commit hook is not built in the same PR. The rule is declared; the enforcement is "we'll add it later."

This is the meta-pattern of F1 Sediment Family applied to the project's own ground rules. Every other F1 sub-form (F1.0 schema invariants, F1.1 declared without CI, F16 identity preamble in skill not memory, F17 self-report fidelity, F18 attribution scope, F19 install commands) is an instance of this F20 meta-pattern: declared without enforcement at the right layer.

### Evidence

Cobrust 9-day pre-2026-05-11 period: CLAUDE.md §6 stated "Test-first for compiler internals: failing test before implementation." Every P9 sprint from M3 through M12 used a single P7 sonnet agent writing impl + tests in the same commit. No commit log shows tests committed before impl. The constitution mandate was fact-violated for 9 consecutive days without anyone (including review-claude) spotting it.

Discovery: 2026-05-11, project owner posed the question "CTO 只管开发不管测试, 不太好, 他手底下应该每个开发都再配一个 sonnet 测试" — owner-spotted constitution gap, not agent-spotted. Review-claude's analysis (this catalogue's parallel session) confirmed: CLAUDE.md §6 mandate without dispatch-prompt workflow alignment = F20 instance.

Resolution: 2026-05-11 same-day codification of D0-D5 difficulty matrix + mandatory dev/test pair workflow (separate test agent + dev agent, test-first ordering, P9 reviews corpus between) into:

- `feedback_subagent_model_tier.md` §"Extension 2026-05-11" (memory enforcement)
- `cto_operations_runbook.md` §"Dispatching a new P9" + §"Dev/test pair pattern" (SOP enforcement)
- Ballast `templates/dispatch-prompt-p9.md` (template enforcement)

Validation: Cobrust W2 sprint (the first sprint after codification) executed with TDD ordering visible in commit log:

```
ca4c37c tests(adr-0044): W2 Phase 2 failing test corpus per ADR-0044 (TDD step 1)
2eb4fca feat(stdlib+codegen+cli+types): wire source-level input/read_line/argv per ADR-0044 W2 Phase 2 (TDD dev step)

d337cf0 tests(adr-0044): W2 Phase 3 LeetCode oracle-match corpus (TDD step 1)
0145e8b feat(examples): W2 Phase 3 — 10 LeetCode .cb programs (TDD dev step, ADR-0044 stdin/argv usage)
```

The TDD step 1 commits land before TDD dev step commits in temporal order. **First executed test-first sprint after 12 days of constitution mandate fact-violated.** F20 is closed for Cobrust via execution evidence, not just documentation.

### Rule of thumb

> **Every binding constitution rule must have a paired enforcement step in the same PR that introduces it.**
>
> Enforcement layers in ascending strength:
> 1. Mandate appears in dispatch prompt template (workflow text)
> 2. Mandate appears in auto-loaded project memory (survives compaction)
> 3. Mandate has a CI lint / commit hook / pre-commit check
> 4. Mandate is enforced by the tool itself (e.g. `cobrust build` rejects code with `unwrap()`)
>
> Aim for layer 3+ on critical rules. Layer 1 alone = F20 instance waiting to happen.

### Recovery

When discovering an F20 instance:

1. **Locate the mandate text**: which paragraph in which doc?
2. **Identify the workflow gap**: which dispatch prompt template / SOP / CI file should enforce this?
3. **Add the enforcement in the next PR**, not "later". Same-day codification is the minimum.
4. **Backfill validation**: after enforcement is added, run one sprint that exercises the enforced path; verify the enforcement actually fires (e.g. CI rejects bad commit).

### Prevention going forward

In every new constitution / CLAUDE.md / project rules document:

1. After each rule, add a `**Enforced by**: <CI lint / dispatch prompt field / memory entry / N/A — aspirational>` line.
2. If `Enforced by: N/A — aspirational` appears, flag for future codification or downgrade the rule to "guidance" rather than "mandate".
3. Periodic constitution audit (quarterly): grep every mandate, verify each has a working enforcement mechanism.

This is itself a meta-application of Ballast: the project's own development discipline must be Ballast-managed.

---

## F21 — Cross-session AI agent identity overload (F1 Sediment Family, identity-namespace sub-form)

> **F1 sub-form, confirmed**. A symbolic agent handle ("review-claude", "the CTO", "studio-reviewer") is used across multiple distinct AI sessions/contexts as if it were a stable identity. Audit trail becomes ambiguous: claims attributed to handle X may originate from session A, B, or C, each with different context and authority.

### Definition

A natural-language handle is adopted as the de-facto name for a role (audit reviewer, CTO, tech lead). Multiple distinct AI sessions assume the same handle when fulfilling that role at different times or in parallel. Cross-session artifacts (documents, findings, commit messages) attribute work to "review-claude" without disambiguating which session. Future readers cannot distinguish whether a claim came from a session with deep project context vs. a fresh session with shallow context.

### Symptoms

- Document signed "— review-claude, 2026-05-11" appears in a directory; another document also signed "— review-claude, 2026-05-11" appears with conflicting analysis
- A handoff doc claims "review-claude audited the project across 7+ review rounds" — but the actual author was a different session that synthesized the prior rounds from transcripts, not the session that performed them
- Commit message says `Co-Authored-By: review-claude` — git log cannot distinguish which session
- Project memory references "review-claude" as if it were a single persistent agent, when in practice it's been multiple sessions with different context depths

### Root cause

Three compounding patterns:

1. **Symbolic-handle reuse**: humans naming AI roles (review-claude, CTO, tech-lead-p9) creates an implicit identity. Distinct sessions, when assigned that role, adopt the handle as their own.
2. **No session-ID attribution in artifacts**: documents/commits sign with the handle, not with `handle (session XYZ)` or `handle (timestamp)`. Audit trail collapses across sessions.
3. **Cross-session learning illusion**: readers assume "review-claude knows" things from prior sessions because the handle is consistent. But each session has fresh context unless explicitly fed prior artifacts.

This is F1 family because: the role is declared (review-claude is the auditor), the identity is not enforced (no scheme to distinguish session-A's review-claude from session-B's). Audit attribution drifts.

### Evidence

Cobrust 2026-05-11 evening: project owner asked claude-desktop to draft a Cobrust Studio handoff. Claude-desktop drafted a multi-hundred-line document signing it "— review-claude, 2026-05-11". A separate Claude Code session (the parallel one auditing Cobrust live, session ID `4bb35f43...`) was also active that day and had been signing its own artifacts "review-claude". The Studio handoff cited an external "multi-turn review-claude session" — but the original session that performed those reviews did not write the handoff; claude-desktop did, citing the parallel session's prior work.

Result: future readers of the Studio handoff cannot tell which review-claude session authored each claim, when, with what context. The handle "review-claude" became identity-overloaded between at least 2 concurrent sessions on the same day.

The cleanly-locatable artifact instances on disk: `review-claude-handoff/handoff-pack/dispatches/claude-desktop-integrated-handoff.md` (claude-desktop integration record) + 5+ findings under `review-claude-handoff/findings/` with `discovered_by:` frontmatter, and Ballast's own `docs/agent/conventions.md` §"Identity hygiene (F21 closure)" prescribing session-ID-stamped attribution going forward.

### Rule of thumb

> **Symbolic AI role handles must carry session-ID or timestamp attribution in any persistent artifact.**
>
> Naming convention:
> - In documents: `— review-claude (session 4bb35f43, 2026-05-11)`
> - In commits: `Co-Authored-By: review-claude-session-4bb35f43 <noreply@anthropic.com>`
> - In findings: frontmatter `discovered_by: review-claude (session 4bb35f43)`
> - Reserve plain "review-claude" for the abstract role; never use it bare in attribution.
>
> Stronger: when spawning a new internal review agent, give it a distinct handle (e.g. `studio-reviewer-001`) rather than reusing "review-claude". Reserve "review-claude" for the originating external audit window.

### Recovery

When discovering an F21 instance in existing artifacts:

1. Audit document signatures: identify which actually came from which session.
2. Where ambiguous: leave the original signature, append `(provenance: see commit <SHA> for session metadata)`.
3. Going forward, prefix new artifacts with explicit session ID.

### Prevention going forward

In every Ballast project:

1. At the start of a session that will produce persistent artifacts, declare the session ID. Stamp every commit / finding / ADR with that ID.
2. Distinct roles get distinct handles. "review-claude" is the role; "review-claude (session 4bb35f43)" is the agent instance. Documents reference the latter.
3. If multiple sessions of the same role are concurrent: choose disambiguating suffixes (`review-claude-A`, `review-claude-B`, or session-ID).

This convention applies to any AI agent role that produces persistent artifacts in a multi-session project. The cost is one extra string per signature; the benefit is unambiguous audit trail forever.

---

## F22 — Coverage drive without bug-fix cadence (mitigation pattern validated, F1 Sediment Family suppression sub-form)

> **F1 sub-form, candidate → validated-as-suppressed**. F22 is the negative pattern a Ballast project hits when it scales a stress-test corpus (N → 5N → 10N programs) without applying fix-pack between scales. ADR-0047 (LeetCode coverage strategy) was authored as the explicit F22 mitigation, and the LC-100 → Option H decision was the empirical validation that the mitigation works.

### Definition

The temptation to run "all 3816 LeetCode problems" / "all 500 test cases" / "all N stress-test inputs" *before* triaging and fixing bugs from the first batch. The result: each subsequent batch hits the same N bug-patterns as the first, multiplying the surface defect count without surfacing new failure modes. Bug-pattern density per batch saturates after ~100 programs; the next 3700 are mostly re-discovery of the same gaps.

### Symptoms

- A coverage-drive sprint exits with 3000+ test programs but only 5-7 distinct bug-patterns
- Triage time grows quadratically with batch size (more programs to classify into same patterns)
- "Pass rate" stays roughly flat across scales (e.g. 77% at N=100 stays 75-80% at N=500 absent fix-pack)
- Fix-pack debt accumulates: each unfixed pattern blocks ~N/k programs per round, with k ≈ patterns

### Root cause

Coverage-as-throughput optimism: the assumption that running more cases surfaces more bugs. In practice, the bug-pattern distribution is heavy-tailed — the first ~100 programs of any reasonable sample surface ~80% of patterns. Continuing past saturation is re-discovery.

ADR-0047 codified the **ramp gate**: pass rate < 70% → HOLD (fix-pack), 70-90% → conditional GO (fix-pack-OR-ramp evidence-driven), ≥ 90% → SKIP back to other work (gap-saturated, no Tier B ROI).

### Evidence

**LC-100 Tier A discovery sweep (2026-05-12)**: P9 opus + 4 P7 sonnet TDD pairs ran 100 programs across 10 algorithm categories. Initial result 77/100 with 3 distinct failure patterns (Pattern A codegen rodata literals, Pattern B list[str] type gap, Pattern C test corpus oracle defects).

**ADR-0047 ramp logic predicted**: 77% is the conditional zone — Option G (immediate Tier B) vs Option H (fix-pack first). P9 + review-claude both recommended Option H based on F22 mitigation principle: don't ramp the same defect distribution to 5N scale.

**Option H executed** at commits `2d952e0` (Sprint 1 Pattern C fix, +15 programs) + `2a8bdc0` (Sprint 2 Pattern A C-ABI fix, +7 programs) = 99/100 stable. Post-fix-pack pass rate 99/100 = 99% triggers ADR-0047's SKIP-back-to-W1 gate — Tier A is gap-saturated, Tier B has no ROI.

**Validation**: F22 was NOT fired because the mitigation existed and was followed. The reverse-evidence (counterfactual: had ADR-0047 not existed, P9 likely would have ramped to 500 programs and re-discovered the same 3 patterns at ~75-defect scale, wasting ~5-10× agent-time).

### Rule of thumb

> **Stress-test corpus growth (N → 5N) MUST be gated by current-batch pass rate.**
>
> Decision logic:
> - < 70% pass: HOLD; fix-pack the patterns surfaced; re-baseline at N before ramping
> - 70-90% pass: conditional GO with bug-fix-cost check — if fix-pack > 1 day, ramp anyway; if ≤ 1 day, fix first
> - ≥ 90% pass: SKIP — corpus is gap-saturated for this language area; ramping has no ROI

Time-cap the discovery sweep at the same time: ADR-0047 capped Tier A at 1-2 day. Without a time-cap, F22 manifests as "ramp anyway because the test feels useful". The cap forces the gate decision.

### Recovery

If F22 has already fired (you ramped before fixing):

1. **Triage all failures into pattern groups** (ADR-0047 Phase 3-style). Aim for 3-7 distinct patterns; if more, the test corpus is noisy.
2. **Identify the high-multiplicity patterns**: which 2-3 patterns account for ≥ 80% of failures? Fix those first.
3. **Re-baseline at the smaller scale (e.g. N) after the fix-pack**. Confirm pass rate ≥ 90% before considering further ramp.
4. **Document the cost lesson** as a finding — "we ramped to 5N before fix-pack and lost ~K agent-hours to repeated triage."

### Prevention going forward

For any future stress-test corpus design:

1. **ADR the ramp strategy before generating the corpus** (per ADR-0047 template). Include the gate thresholds.
2. **Build the time-cap into the dispatch prompt**. P9 sub-agents that exceed cap MUST escalate, not auto-ramp.
3. **Track bug-pattern density per batch**. When it falls below ~1 new pattern per 50 programs, you've hit saturation.
4. **Reverse-evidence is real evidence**. When F22 doesn't fire, document the counterfactual cost saved.

---

## F23-A — Oracle authorship without independent verification (F1 Sediment Family, oracle-verify sub-form)

> **F1 sub-form, confirmed**. Same family as F1.1 (declared invariants without enforcement) and F17 (sub-agent KPI self-report fidelity), but specific to **the test oracle itself** rather than the implementation under test. The pattern: the agent authoring the test corpus mentally executes the algorithm and writes both the algorithm description AND the expected output. Without an independent verifier (a reference implementation), arithmetic / DP-trace / tree-encoding mistakes get encoded directly into the oracle — silently invalidating the test gate.

### Definition

A P7-TEST sonnet agent produces a test corpus (`test.toml` cases + algorithm paraphrase in README) by mental execution of the algorithm. The expected output field is the agent's mental computation result — no independent verification path runs. Bugs in the agent's mental execution become bugs in the oracle.

The downstream effect: a P7-DEV agent's `solution.cb` may be algorithmically correct, but fails the oracle because the oracle itself is wrong. Triage misclassifies this as a "language gap" instead of a "test corpus defect", wasting language-implementation effort on a test-author mistake.

### Symptoms

- Algorithm-style stress-test corpus shows 15-30% failures concentrated in arithmetic / DP-trace / graph-traversal categories
- DEV agent's failing solutions look algorithmically reasonable on careful read
- Quick reference-implementation check (running the algorithm in Python by hand) confirms DEV output is correct and the oracle is wrong
- "Pattern: test corpus defects" emerges as a primary failure class in triage

### Root cause

Mental execution is unreliable for non-trivial algorithms. Even high-quality LLM agents have non-zero error rate when computing:
- DP transitions for sequences > ~10 elements
- BFS / DFS over trees with > ~5 levels
- Modular arithmetic chains
- Bit manipulation edge cases
- String parsing with escape sequences

The author of the algorithm description and the author of the expected output are the same agent in the same session — confirmation bias guarantees the oracle agrees with the agent's mental model, not with reality.

### Evidence

**LC-100 Tier A failure triage**: 15 of 23 initial failures (65%) were oracle-authorship defects, not language gaps. Concrete examples (from `lc100-pattern-c-test-corpus-defects.md`):

- coin-change DP: agent computed DP[5] = 2 mentally; actual algorithm returns 1
- BFS level-count: agent encoded "depth = 3" for a tree where actual BFS returns 4 (off-by-one on root)
- Roman-to-int: agent's mental arithmetic on "MCMXCIV" yielded 1995 instead of 1994 (subtraction-rule miscount)
- Climbing-stairs: agent encoded fib(N+1) instead of fib(N) (off-by-one on base case)

15 corrections were derivable post-hoc by running reference Python implementations against the same inputs. The author's mental execution had been the sole oracle source — no second pass.

**Codified mitigation: ADR-0047a verify.py mandate** (2026-05-12). Every Tier B program must ship with a `verify.py` reference Python implementation that runs against the `test.toml` corpus and confirms the oracle before the DEV phase begins.

### Rule of thumb

> **The test oracle author MUST run an independent verification (different code path, ideally different agent) before declaring the corpus ready.**
>
> Concrete forms:
> 1. **Reference-implementation pattern (lightweight, default)**: P7-TEST authors a `verify.py` reference Python impl in the same sprint; runs it against test cases; commits only when all match.
> 2. **CPython differential pattern (heavyweight, for numerical / library translations)**: oracle is computed by an authoritative external implementation; agent encodes the input + the differential check, not the expected output.
> 3. **Hand-verified pattern (lowest scale, ≤ 5 cases)**: human reviewer hand-traces each case; works only at small N.

For algorithm-style corpora (LeetCode shape), Form 1 (verify.py) is the empirically validated default.

### Recovery

When F23-A fires (oracle defects discovered post-hoc):

1. **Triage**: separate corpus-defect failures from language-gap failures. The corpus-defect class shows DEV output looking algorithmically reasonable.
2. **Author reference impls** (Python, Rust, or pseudocode) for the affected cases; run them against the corpus.
3. **Fix the corpus, not the implementation**, for any case where reference impl confirms DEV output.
4. **Re-run the full corpus** post-fix; confirm pass rate change matches the corrected-defect count.

### Prevention going forward

In any future stress-test corpus dispatch:

1. **Update dispatch templates**: P7-TEST prompt MUST include verify.py authoring as a step before test.toml finalization (per ADR-0047a pattern).
2. **Sprint exit gate**: `[P7-TEST-CORPUS-READY]` report MUST include per-program `verify_py_matches: yes/no` rows.
3. **CI extension (stretch)**: a release-readiness-style harness re-runs verify.py against test.toml at corpus-edit time, catching oracle drift between sprints.

---

## F23-B — Synthetic stress test distribution drift from real-world (F1 Sediment Family, distribution-coverage sub-form) [CANDIDATE, UNMEASURED]

> **F1 sub-form, candidate**. A stress-test corpus is hand-picked or algorithmically generated to exercise a specific surface (e.g. "10 algorithm categories × 10 programs each"). The resulting bug-pattern distribution may diverge from what real-world programs in the same language would surface. The corpus's coverage claim ("we tested 100 programs") may not generalize to "the language handles 100% of similar real-world programs."

### Definition

A discovery sweep's bug-distribution is a function of the corpus's input-distribution. If the corpus's distribution differs from production-distribution, the bug-set found is unrepresentative — both falsely confident (missing bugs that real programs would surface) and falsely alarming (surfacing bugs that real programs never trigger).

For Cobrust LC-100: 10 algorithm categories × 10 paraphrased programs each is a synthetic distribution. Real-world Python programs (e.g. tomli, msgpack, dateutil) have very different structure — heavy on string parsing, library boilerplate, error-handling, less on DP/graph/numerical algorithms.

### Symptoms (predicted, not yet validated)

- Stress-test discovery surfaces N bug-patterns; real Python lib translation later surfaces M ≠ N bug-patterns
- Bug-pattern overlap between synthetic and real-world is < 70%
- "Pass rate at N synthetic programs ≥ 90%" does NOT imply "pass rate on real Python libs ≥ 90%"

### Root cause

Distribution mismatch:

- **Synthetic-leaning bias**: algorithm-style problems exercise control flow + arithmetic + small data structures. Real Python programs exercise string manipulation + I/O + library interop more heavily.
- **Length distribution**: LeetCode programs typically 20-100 LOC. Real Python files are 200-2000 LOC with multi-module imports.
- **Error-handling absence**: algorithm-style problems usually have well-defined inputs; real programs need defensive error handling, validation, malformed input recovery.

A 99/100 pass rate on synthetic corpus doesn't bound the failure rate on production-distribution programs.

### Evidence

**Unmeasured at LC-100 Tier A close (2026-05-12)**. Empirical validation requires running translated real Python libraries (T1.1 tomli, msgpack, dateutil) against the same Cobrust compiler that achieves 99/100 on LC-100, then comparing bug-pattern overlap.

Hypothesis: pattern overlap will be < 60%. Real-Python translation will surface string-handling + library-interop bugs that LC-100 doesn't probe; LC-100 surfaces algorithmic-edge bugs that real Python rarely hits.

The candidate becomes "confirmed F23-B" when this measurement happens.

### Rule of thumb

> **A stress-test pass rate is a function of the test corpus distribution. To bound real-world failure rates, run additional probes on the actual production distribution (or a sample of it).**
>
> Practical forms:
> 1. **Cross-distribution validation**: after a synthetic corpus closes, run a smaller (~10-30) real-distribution sample. Compare bug-pattern overlap.
> 2. **Real-distribution prioritization**: if real-world coverage is the goal, prioritize real-distribution corpus design over synthetic.
> 3. **Cite distribution explicitly**: marketing / release messaging "Cobrust passes N/M LeetCode" must qualify "(synthetic algorithm-style corpus; real Python lib translation rates vary)".

### Recovery

If F23-B is suspected (synthetic pass rate is high but real-world deployment has issues):

1. **Build a real-distribution sample**: ~30 representative programs from production code or real libraries.
2. **Run against the same compiler**; classify failures.
3. **Pattern-overlap analysis**: which patterns appear in both? Which only in synthetic? Which only in real-world?
4. **Update marketing / release messaging** to cite the appropriate distribution.

### Prevention going forward

When designing future stress-test corpora:

1. **Declare the corpus distribution in the dispatch ADR**. "10 algorithm categories × 10 programs each" is a synthetic-leaning distribution and must be acknowledged as such.
2. **Add a real-distribution sample at Phase 4** of any large coverage sweep. Even 10-20 real programs validate the synthetic pass rate's generalizability.
3. **Marketing copy must qualify**: "99/100 on synthetic algorithm corpus" not "99% language coverage." F8 (marketing overreach) prevention.

### Status

**Candidate**, awaiting empirical measurement post-T1.1 real-LLM E2E on msgpack / dateutil / requests / click. When pattern-overlap data lands, this entry promotes to confirmed.

---

## F24 — Stress-test pass via primitive-as-everything simulation (F1 Sediment Family, coverage-fidelity sub-form)

> **F1 sub-form, confirmed**. Related to F23-A (oracle-without-verify) and F23-B (distribution drift) but distinct: F24 is about **what the implementation under test actually exercises**. The pass rate metric becomes semantically vacuous when programs route around a missing language feature using a primitive type (list as linked-list / dict as tree / list-as-stack-as-queue) — the language passes the test but doesn't actually implement the structure the test category claims to cover.

### Definition

A stress-test corpus organized by feature category (e.g. "10 linked-list problems / 10 tree problems / 10 hash-set problems") shows a high pass rate. But inspection of the actual program implementations reveals they all use a single primitive type (`list[i64]`, `array<T>`) as the data backbone, simulating the richer category-named structure via index arithmetic or value-arrays. The language never actually compiled a real linked-list / tree / set type — the test passed via simulation, not via real coverage of the claimed feature category.

### Symptoms

- Stress-test categories named after data structures show high pass (e.g. "10/10 linked list", "9/10 binary tree")
- All "linked list" .cb programs share a comment like `# Algorithm: store values in an array then two-pointer / index manipulate`
- Tree problems use level-order index encoding (`parent = (i-1)/2`) on a flat array, not real tree nodes
- Hash-set problems use dict-with-1-as-value, not a Set type
- `grep -r 'struct.*Node\|struct.*Tree\|enum.*List' src/` returns nothing matching real recursive types

### Root cause

The corpus author (P7-TEST or human spec author) selects categories by their algorithmic shape ("LinkedList problems", "Binary Tree problems") but the corpus's pass condition is "expected stdout matches actual stdout" — which is achievable by **any** correct algorithm regardless of data structure. The cheapest correct implementation often routes through a primitive the language already supports, bypassing the structure the category implicitly claims.

Without an explicit constraint "this category MUST use a recursive struct" or "this category MUST allocate K Tree nodes", the pass rate measures algorithmic correctness, not feature-category coverage.

This is F1 family because: the coverage claim ("we tested 10 linked list problems") is declared, but no enforcement mechanism verifies the language actually exercised linked-list semantics. The declaration drifts from the enforced reality.

### Evidence

**Cobrust LC-100 Tier A close (2026-05-12, HEAD 459b820)**: 99/100 pass rate. Linked-list problems inspection:

```cobrust
# examples/leetcode-stress/045-linked-list-palindrome/solution.cb
# Algorithm: store all values in an array, then two-pointer compare from both ends
fn main() -> i64:
    let vals = list_new(n)
    # ... list_set / list_get loops, two-pointer arithmetic
```

```cobrust
# examples/leetcode-stress/047-merge-k-sorted-lists/solution.cb
# Algorithm: store all lists in a flat array, then selection-sort via K pointers
fn main() -> i64:
    let flat = list_new(10000)
    let offsets = list_new(k + 1)
    # ... index arithmetic, no Node struct
```

```cobrust
# examples/leetcode-stress/050-rotate-linked-list/solution.cb
# Algorithm: values in array, rotate by index
```

All linked-list programs use `list_new / list_set / list_get` flat-array simulation. Same pattern across the 10 linked-list + 10 tree + N hash-set programs.

Cobrust language as of HEAD 459b820:
- `grep -rE 'LinkedList|TreeNode|HashSet' crates/cobrust-stdlib/src/` returns Rust-side `HashSet<T>` internal wrappers but **no source-level (`.cb`-visible) types** for LinkedList / Tree / Set
- `grep -rE 'struct.*ref|recursive struct' crates/cobrust-types/src/` returns nothing matching source-level recursive struct support

Conclusion: the 99/100 pass rate is **valid as algorithmic stress test** but **does not bound the language's recursive-type support**. The two metrics diverge; the corpus's category names suggest coverage that the language did not actually achieve.

### Rule of thumb

> **Coverage claims by feature category MUST be verified at the implementation surface, not just the output surface.**
>
> Concrete forms:
> 1. **Type-asserting pass condition**: corpus per-program asserts that the .cb solution uses the claimed type (e.g. `solution.cb` for LinkedList must contain `struct.*Node` or import the stdlib `LinkedList`). Static check at sprint exit gate.
> 2. **Feature-category audit**: P9 Phase 3 triage explicitly inspects K random programs per category for primitive-simulation pattern. If > 50% use the same primitive, flag the category as "simulated, not really tested".
> 3. **Counterfactual sample**: write 1-2 programs per category that DELIBERATELY use the claimed type. If they don't compile, the category was never really covered.

For Cobrust LC-100: forms 1+2 should have fired during P9 Phase 3 triage. Recovery: track the gap as explicit tech debt with a pre-tag blocker (per ADR-0045 user-traction milestone gate pattern).

### Recovery

When F24 has fired (your stress-test passes mask a real coverage gap):

1. **Document the tech debt explicitly**. Write a finding citing per-category simulation patterns observed. Cite specific .cb files.
2. **Set a binding pre-tag gate**: the next major-version release (v0.X+1.0) MUST NOT ship until the simulated categories have real-type implementations. Codify in an ADR.
3. **Dispatch the tech debt sprint**: design + implement the missing language features (recursive struct + ref semantics + stdlib LinkedList/Tree/Set generics) + retrofit a subset of programs (3-5 per category) to use the real types.
4. **Re-baseline pass rate on retrofit subset**: confirm the language really compiles and runs the typed implementations. Pass rate on retrofit subset is the honest coverage metric.

### Prevention going forward

For future stress-test corpus design:

1. **Categorize by data structure constraint, not just by algorithm**. "10 programs that MUST use struct Node" not "10 programs about linked lists" — the difference is enforcement.
2. **Sprint exit gate per-category**: static analysis confirms each program in a category exercises the claimed feature.
3. **Cross-reference language ADRs**: if your corpus has a "tree" category, but the language doesn't have an ADR for recursive struct support, the category is fictional until that ADR lands.

This pattern composes with F19 (install-not-tested): both reflect a gap between **what the artifact claims** and **what was actually verified**. F19 is on user-facing surface (install commands), F24 is on test-coverage surface (category claims). Both close by the same principle: independent verification of the claim against reality.

---

## F25 — Tag → audit → patch as a release pattern under AI velocity (discipline, not failure)

> **Discipline entry, not a defect pattern**. F25 is the empirically validated
> *legitimate-and-disciplined* form of what would otherwise read as "shipping
> broken tags". The pattern only becomes anti-pattern when its three preconditions
> (honest CHANGELOG, audit-as-experiment, K-bound convergence) are violated —
> see §"When F25 degrades into anti-pattern" below. Catalogued here because under
> AI velocity (~2.5×-10×) the first tag will not be the publishable one, and the
> right discipline is to *plan for K patch tags* rather than aim for shippable-on-first-try.

### Definition

Under AI-velocity acceleration, a project ships its first tag with the
expectation that the **first release-readiness audit will reveal an enforcement
gap that intent-driven self-checks missed**. The pattern is:

```
Tag v0.1.<N>                                  ← experiment substrate
    ↓
Release-readiness audit in clean shell         ← observation
    ↓ (BLOCK)
Finding filed + patch + tag v0.1.<N+1>        ← learning
    ↓
Re-audit
    ↓ (GO)
Announce, publish notes
```

Each tag is the experiment; each audit is the observation; each patch is
the learning. The pattern's success metric is **bounded convergence after K
patches**, not "first tag is perfect". For Cobrust Studio: K=2 (v0.1.0 broken
→ v0.1.1 broken → v0.1.2 usable, in 6 hours wall-clock).

### Symptoms (legitimate form)

- Multiple consecutive patch-tags in a single calendar day (v0.1.0 → v0.1.1
  → v0.1.2 in 6 hours)
- Each tag has its own CHANGELOG entry naming the gap explicitly
  ("v0.1.1 stale Cargo.lock; cargo build --locked exit 101")
- Each tag has a corresponding finding under `docs/agent/findings/` filed
  before the next patch
- README §"Honest status" or equivalent names the patch dance up front
  for users
- Total K is bounded (typically 2–3); convergence is not "endless patch
  spiral"

### When F25 degrades into anti-pattern

F25 becomes a defect pattern (and should be filed as a separate finding)
when any of the following hold:

1. **No honest CHANGELOG**: subsequent tag silently overwrites prior
   without naming the broken state. Users cannot distinguish which tags
   to skip. *Recovery*: amend CHANGELOG at the next patch; never delete
   the prior tag's broken state.
2. **Audit-as-ceremony, not audit-as-experiment**: the release-readiness
   audit is rubber-stamping rather than truly running install commands
   in a clean shell. Same F19 (release-readiness untested) instance,
   wearing a release-pattern costume.
3. **K unbounded**: more than ~3 patch tags without convergence suggests
   the project is missing a structural fix (the F20/F26 enforcement
   layer the patches are nominally closing). *Recovery*: stop tagging;
   land the enforcement-script fix; re-tag once.

### Root cause

AI-velocity acceleration buys experimental cycles, not shippable-first-try.
Under a 5-day human plan compressed to 2 days, the writer's mental model of
"what will install correctly" diverges from the actual artifact more than
under a 5-day human cadence. The release-readiness audit (F19's prevention
mechanism) catches the divergence; the patch closes it. The pattern is
*the right discipline* for AI velocity — but only with the three preconditions
above honored.

### Evidence

Cobrust Studio 2026-05-12, three consecutive tags in 6 hours wall-clock
(case study §3.4, §3.5, §4.1):

1. **v0.1.0** (commit `a722e09`, tag `0a7fd3e`): SPA fallback regression
   (`Path<String>` on `Router::fallback`) shipped. Post-tag CTO 守闸
   release-readiness audit ran hermetic Playwright against
   `./target/release/cobrust-studio` built from main HEAD; 13/14 e2e specs
   failed. Finding `m4-release-readiness-spa-fallback-extractor.md` filed
   P0.
2. **v0.1.1** (commit `15b6f46`): SPA fallback fixed via `Uri` extractor.
   Stale Cargo.lock shipped; `cargo build --workspace --locked` exit 101.
   `release-tarball.sh` errored; CHANGELOG names the gap.
3. **v0.1.2** (commit `7ea9ae3`): Cargo.lock regenerated + `doc-coverage.sh`
   §6 hardened with paired exit-code + FAILED-grep gate. Release-readiness
   audit returned GO. First usable tag.

CHANGELOG names each broken tag explicitly; README §"Honest status" names
the patch dance up front. All three preconditions honored. K=2 (within
the bounded convergence claim).

### Rule of thumb

> **Under AI velocity, plan for K=2 patch tags before first usable. The
> right discipline is fast experimental cycle: tag, audit in clean shell,
> patch the gap, re-tag.**
>
> Hard preconditions for the pattern to remain legitimate-and-disciplined:
>
> 1. **Honest CHANGELOG**: each broken tag named with its gap; no quiet
>    retag.
> 2. **Audit-as-experiment**: the release-readiness audit must actually
>    run commands in a clean shell, not read the README.
> 3. **K-bound convergence**: K ≤ 3 typical. If K > 3, the underlying
>    enforcement-script layer is missing — stop tagging, fix the
>    enforcement, re-tag once.

### Recovery

When F25 is firing (legitimate use):

1. After each patch tag, file a finding naming the gap as an instance
   of F19/F20/F26 (which enforcement layer was missing).
2. Update `scripts/doc-coverage.sh` or equivalent enforcement script
   in the same PR as the patch, closing the gap structurally — not
   just fixing the symptom.
3. Verify convergence: each subsequent patch should close a *different*
   gap. Two consecutive patches closing the same gap = K-bound violated,
   stop tagging.

When F25 has degraded into anti-pattern (quiet retag / endless spiral):

1. Audit CHANGELOG: name every prior broken state retroactively.
2. Locate the missing enforcement layer (the F20 instance the patches
   are nominally closing); land it; re-tag once.
3. Communicate to users: "we shipped K tags rapidly; here is what
   each one fixed; here is the structural fix we landed at v0.1.<K+1>".

### Prevention going forward

Adopt F25 as an explicit release pattern in `cto_operations_runbook.md`
§"Tagging policy" for any AI-velocity project:

- Plan for K=2 patch tags in the release window.
- Spawn the release-readiness agent (F19) on **every** tag push, not
  just the planned "final" one.
- CHANGELOG template includes a §"This tag is known-broken; upgrade to
  v0.1.<N+1>" section for any tag the audit returned BLOCK on.
- README §"Honest status" names the current usable tag, not the latest
  tag — users can find both with `git tag --sort=-creatordate`.

This composes with F19 (release-readiness untested — F25's audit step
*is* an F19 prevention exercise) and F20 (constitution-vs-workflow
alignment — each patch is an F20 closure landed in the same PR as the
fix).

---

## F26 — Recursive enforcement-script closure required (F1 Sediment Family, orthogonal-failure sub-form)

> **F1 sub-form, confirmed**. Direct refinement of F20 (constitution-vs-workflow
> alignment). F20 closure is not one-shot; every enforcement layer needs its
> own paired review against orthogonal failure modes on the same code path.
> A doc-coverage gate hardened against pattern X can ship green against pattern
> Y on the same operation. Studio's `doc-coverage.sh` §6 evolution is the
> empirical substrate: two patches before the §6 gate stopped letting things
> through.

### Definition

An enforcement script (CI lint, doc-coverage gate, pre-commit hook) is
written or hardened to catch failure mode X on operation Op. The script
appears correct against X. The script ships green against failure mode Y
on the same operation Op — Y being a different shape of the same underlying
contract violation that X manifests. Each enforcement layer needs its own
paired orthogonal-failure review until the failure-mode class no longer
recurs.

### Symptoms

- An F20 closure (script hardened against bug pattern X) ships green
  against bug pattern Y the same week
- The script's invariant is declared once ("no test failures shipped") but
  the operation has multiple orthogonal failure shapes (FAILED summary line
  emitted vs exit code only vs hang vs panic vs OOM)
- "Two strikes" pattern: same script, same invariant, two consecutive
  bypasses through different failure modes
- Auditor's review of the script reads correct against the failure mode
  that motivated the script's creation, but doesn't scan for orthogonal
  failure modes on the same code path

### Root cause

Enforcement-script authors close the failure mode that triggered the script.
They do not scan the same operation for other failure modes that would
bypass the new check. The script's coverage is local to the bug; the
contract's coverage is global to the operation. Closing X without checking
Y leaves the layer half-closed.

This is structurally a recursive application of F20 (constitution-vs-workflow:
mandate vs workflow has a gap). F26 is F20 applied to the workflow itself
— the enforcement layer is a workflow, the workflow has a gap, the gap
becomes a new finding, the new closure may itself have a gap.

### Evidence

Cobrust Studio `doc-coverage.sh` §6 evolution (2026-05-12; case study §3.5
and §4.2):

| Stage | Enforcement | Gap revealed | Closure tag |
|---|---|---|---|
| Pre-M4.1 | `grep '^test result' \| wc -l` | Counts both `ok` and `FAILED` as "result" lines; 9 failing tests shipped as "22 test groups all green" | A4 merge `8d5475f` shipped 9 failing integration tests under green-gate |
| M4.1 | `grep -c '^test result: FAILED'` | Misses non-zero exit without summary line (e.g. `cargo build --locked` exit 101 from lockfile mismatch) | v0.1.1 tag `15b6f46` shipped broken |
| v0.1.2 | Paired: `if ! cargo test ...` AND FAILED-grep | Both classes now caught | v0.1.2 tag `7ea9ae3` first usable |

Each fix was complete against the bug class it was designed for. But the
enforcement layer had orthogonal failure modes (FAILED-line emit-ing vs
not-emit-ing on `cargo test --locked`) that needed their own paired review.

A second F26 instance landed in M5.8: `doc-coverage.sh` §5b added `cargo
fmt --check` after Sarah-persona v2 caught local "6 gates passed" while
CI's separate `cargo fmt --check` job failed on the same SHA — the §5b
gate was missing because the §6 gate's authoring scope was "test-failure
shape", not "any orthogonal pre-merge check the project also runs in CI".
Same F26 pattern, different orthogonal failure axis.

### Rule of thumb

> **When closing an F20 instance, scan for orthogonal failure modes on the
> same code path BEFORE declaring the closure complete.**
>
> Ask explicitly: "could my enforcement layer still pass under a different
> failure shape of the same operation?" If yes, the closure is partial.
>
> Common orthogonal axes to enumerate per operation:
>
> | Operation | Orthogonal failure axes |
> |---|---|
> | `cargo test --locked` | exit code ≠ 0 / FAILED summary line / hang / panic / OOM / lockfile mismatch / build error |
> | Frontmatter SHA check | absent / placeholder string ("HEAD") / wrong hex shape / hex-shaped but unreachable / wrong-branch SHA |
> | README install command | URL 404 / URL redirect needs -fsSL / asset name typo / wrong-arch asset / missing dependency |
> | CI matrix job | platform missing / runner image deprecated / cache miss balloons time / artifact upload silently truncated |

### Recovery

When F26 fires (a closure shipped, then a sibling failure bypassed it):

1. **Add the paired check to the same script in the same PR**. Don't
   wait for the next sprint.
2. **Enumerate orthogonal failure axes for the operation** (use the table
   above as starting point; extend per project).
3. **Add a "deliberately-broken-input test" in CI**: feed the enforcement
   script a fixture for each orthogonal failure mode; assert exit ≠ 0.
   This is the F20 §"Rule of thumb" layer-3 enforcement applied to F26.
4. **Document the closure as a finding**: `<script>-orthogonal-<mode>-closure.md`
   naming the prior closure that missed the orthogonal mode.

### Prevention going forward

In every project's enforcement-script authoring SOP:

1. **Script-level review checklist**: every new check has a §"Orthogonal
   failure modes considered" comment block enumerating the operation's
   failure axes and which the check covers vs which it explicitly delegates
   to other checks.
2. **Layered review discipline**: F20 closure dispatches must include a
   `[P7-ORTHOGONAL-SCAN]` step before declaring closure — scan the script
   against the orthogonal-axes table for the operation it gates.
3. **Layer 4 enforcement** (the F20 §"Prevention going forward" layer-4
   extension Studio surfaced): "orthogonal-failure review against every
   paired-gate enforcement" is a first-class layer in the enforcement
   stack.

F26 generalizes beyond test gates. Same logic applies to schema invariants
in frontmatter (different shape of violation), CI lint scripts (different
shape of bad input), and dispatch-prompt template fields (different shape
of agent shortcut). Anywhere a workflow is itself an enforcement layer,
F26 applies.

---

## F27 — Continuous persona testing as dev-loop primitive (discipline, not failure)

> **Discipline entry, not a defect pattern**. F27 catalogues the validated
> dev-loop form of Ballast v1.2.1's "persona simulation as 5th audit dimension".
> v1.2.1 introduced persona simulation as a *pre-release* audit pattern.
> Studio's M5 cycle validated the *continuous* variant: persona → concrete PR
> → land → re-spawn persona → verify gap closed → next PR. Pattern emerges
> as a dev-loop primitive, not a one-shot pre-release ceremony.

### Definition

Persona simulation is dispatched as **a dev-loop step** in the same
cadence as test-runs and lint-runs, not as a pre-release audit. Each
persona round produces concrete findings; each finding maps to exactly
one PR ({README edit, ADR addendum, finding, doc fix, code fix}); the
PR lands; a fresh persona round verifies the gap is closed. The loop
runs continuously across releases, not once-per-release.

Loop shape:

```
Persona Vn dispatched (Mei v1 / Aleksandr v1 / Sarah v1)
    ↓
Findings filed; each maps to exactly one PR
    ↓
PRs land within hours (not next release cycle)
    ↓
Persona V(n+1) dispatched against the same persona profile
    ↓
Verify prior gaps closed; surface new gaps (typically post-rewrite, the
README has new vocabulary that wasn't in V1)
    ↓
Next round of PRs
```

### Symptoms (legitimate form)

- Multiple persona rounds per persona profile within a single release
  window (Mei v1 → Mei v2 → Mei v3)
- Each persona round's findings have a 1:1 mapping to PRs that land
  before the next round
- README / positioning evolves measurably between rounds (a Mei v1
  finding "what's an ADR?" → README v2 has §"Methodology vocabulary"
  → Mei v2's response no longer flags vocabulary)
- Persona finding-rate decreases per round (V1 produces ~10 findings,
  V2 ~5, V3 ~2; saturation)
- Persona dispatch is a P7 step in the dispatch SOP, not a pre-tag
  ceremony

### Root cause for the pattern's value

Internal review agents (P7-REVIEW) maintain *internal* coherence — "is
the code sound?". Persona agents simulate *external* coherence — "would
a real user understand this?". Internal review cannot catch external-
coherence gaps because the internal reviewer has the same context as
the writer. Only an agent that starts cold (persona simulation with
explicit fresh-context constraint) can probe the external surface.

Continuous (vs pre-release-only) cadence matters because each README
rewrite surfaces *new* external-coherence gaps. The vocabulary that
replaces the old vocabulary may itself be opaque to the persona. Only
re-running the persona against the new version closes the loop.

### Evidence

Cobrust Studio M5 cycle, 2026-05-12 (case study §4.3):

- **Mei v1** (Python data scientist target user) → 4 findings: vocabulary
  confusion ("what's an ADR?"), missing "why not Linear/Notion?",
  install path assumes `rustup`, "is this production-ready?".
- **README rewrite** (`339e1ab`): §"Methodology vocabulary" table added;
  §"Why this and not Linear + git?" comparison; §"Honest status"
  section naming patch dance; §"Looking for design partners" with
  concrete asks.
- **Mei v2** → vocabulary confusion resolved; new gap: "Honest-status"
  placement was buried mid-page; persona-naming was visible to users.
- **README v2 rewrite**: "Honest-status" moved to top of README;
  persona-naming removed from public-facing copy.

Aleksandr loop (Rust skeptic):

- **Aleksandr v1** → F-05 dead deps catch (`unicode-normalization`, `uuid`,
  `hex`, `tracing` lifted from upstream but unused); missing CI matrix.
- **2 PRs landed** (`339e1ab` dead-deps removal + `58cbe94` matrix CI).
- **Aleksandr v2** → next PR filed: Windows test matrix (Sarah's release.yml
  added Windows tarball builds, but the test matrix only covered Linux +
  macOS).

Sarah loop (OSS evaluator / tech-lead):

- **Sarah v1** → bus-factor flag, no SECURITY.md, no CONTRIBUTING.md.
- **PRs landed**: CI matrix + release pipeline + design-partner template.
- **Sarah v2** → verdict updated 6mo-watch → 3mo-watch; flagged R8
  (closed-feedback-loop, see F28) and R9 (README-vs-release drift, see
  F1.4).

All three persona profiles ran 2 rounds within a 4-hour window after
v0.1.2. Finding-rate decreased per round (V1: 10 items; V2: 4 items).
~15 concrete PR items in 90 min total persona dispatch time. ~7 landed
in the same wave.

### Rule of thumb

> **Persona simulation is a dev-loop primitive, not a pre-release
> ceremony. Run it continuously, with finding-rate as the saturation
> signal.**
>
> Five preconditions for legitimate continuous persona testing:
>
> 1. **Personas richly defined**: years of experience, prior burned-by
>    experiences, current frustrations — not "a Python dev".
> 2. **Specific scenario per round**: "you have 30 min on HN", not
>    "evaluate this README".
> 3. **Stay-in-character constraint** in prompt: no "as an AI..."
>    breakouts.
> 4. **Structured output fields** aligned to persona's actual decision:
>    "would I upvote?", "what would I PR if I had an afternoon?".
> 5. **1:1 finding-to-PR mapping**: each finding maps to exactly one of
>    {README edit, ADR addendum, finding, doc fix, code fix}. Findings
>    mapping to "no action / acknowledged" are research findings (file
>    for case study), not product findings.
>
> Saturation signal: when finding-rate falls below ~2 new findings per
> persona round, the persona profile has reached coverage saturation
> for the current artifact. Pause this profile; rotate in a different
> persona; resume when the artifact changes substantially.

### Recovery

When the pattern degrades (persona output not driving PRs):

1. Audit the finding→PR mapping. If >30% of findings map to "no action",
   the persona prompt is producing generic feedback, not decision-bound
   feedback. Tighten constraints 1-5 above.
2. Audit finding-rate. If V2 produces *more* findings than V1, the
   intervening rewrite surfaced new gaps — that's the pattern working.
   If V2 produces the same findings, the rewrite missed the gap.

### Prevention going forward

In every Ballast project's dispatch SOP:

1. **Persona-as-step in dispatch template**: after every README / public
   surface PR, dispatch the relevant persona profiles before the next
   wave starts.
2. **Persona finding-rate tracked per round**: record rate-of-new-findings
   in the case study or operations log; saturation triggers profile
   rotation.
3. **Persona prompts versioned**: keep persona prompts in `templates/
   personas/<profile>.md` so V1 and V2 use the same persona profile
   text; only the scenario differs.

F27 composes with F28 (persona-simulation-as-validation epistemic risk)
— F27 is the legitimate dev-loop form; F28 names the failure mode that
emerges when F27's loop becomes the *substitute* for external grounding
rather than an internal-coherence check. The two entries must be read
together.

---

## F28 — Persona-simulation-as-validation epistemic risk (closed-feedback-loop sub-form)

> **Confirmed failure mode, surfaced by Studio Sarah v2 as risk R8**. F28 is
> the failure mode F27 (continuous persona testing) regresses into when
> persona simulation becomes the *primary* validation surface, with no
> out-of-distribution grounding from actual external users or independent
> teams. The feedback loop is internally consistent and externally untested.

### Definition

A project's release-readiness validation pipeline consists of:

- Internal review agents (P7-REVIEW)
- Persona simulation agents (Mei / Aleksandr / Sarah)
- The project's own maintainer 守闸

All agents are spawned by the same maintainer / harness / methodology. No
agent is *out-of-distribution* with respect to the project's training context.
The persona-simulation loop (F27) iterates: persona → README rewrite →
persona again → README v2. Each iteration is internally coherent. None of
the iterations are validated against an actual external user, an independent
team running the methodology, or a real-world install attempt by someone
who has never read the project's prompts.

The closed-feedback-loop is the failure mode: **the methodology that built
the tool is also auditing the tool, with no external grounding**.

### Symptoms

- Persona rounds converge to "PASS-watch" verdicts without any actual
  external user contact
- Persona-driven README rewrites optimize for what the persona simulation
  responds to, not what an actual external reader would respond to
- Case study artifacts cite the persona output as validation evidence
  ("Mei v2 confirms the README is now accessible"), with no follow-up
  external user reading
- The project's methodology section (Ballast-style) cites the project itself
  as the methodology's N=2 dogfood, and the project's own personas
  validate the methodology — circular validation chain
- From a tech-lead vendor-eval standpoint: the project looks suspicious
  because the methodology that built the tool is the same methodology
  auditing the tool

### Root cause

Persona agents are LLMs simulating users. Their training distribution overlaps
with the maintainer's distribution. When the maintainer rewrites the README
to address persona findings, the rewrite's vocabulary and framing are
calibrated to *what the persona simulation responds to* — which is
calibrated to *what the underlying LLM family interprets as accessible*.

This is structurally a closed feedback loop: the optimizer (maintainer +
LLM) and the evaluator (persona LLM) share latent space. Improvements
along the persona-validated axis may or may not correspond to improvements
along the actual-external-user axis. Without out-of-distribution input,
the loop converges to a local optimum in the shared latent space.

The methodology (Ballast v1.2.1) explicitly recognizes this risk by treating
persona simulation as a *dev-loop variant* (F27) — but the case study's
"PASS-watch" verdicts and methodology's own self-validation through the
persona loop *do* exhibit the closed-loop pattern absent external grounding.

### Evidence

Cobrust Studio Sarah v2 risk R8 (2026-05-12; persona dispatch artifact
referenced in case study §4.5 and §10):

Sarah-persona v2 explicitly raised R8 as a tech-lead-vendor-eval finding:
the maintainer is running 2-round continuous persona tests as a substitute
for external review; personas are agents simulating users; the Mei v1 →
Mei v2 → README-rewrite-to-hide-persona-names loop is a closed feedback
system with no external grounding. Ballast calls this "dev-loop variant" and
treats it as legitimate. Sarah v2 says: from a tech-lead vendor-eval
standpoint, it's exactly the failure mode that makes a project suspicious
— the methodology that built the tool is also auditing the tool, with no
out-of-distribution input.

Cobrust + Studio N=2 case-study chain (case study §10):

> *"The Ballast methodology distilled from Cobrust (N=1) was the experimental
> substrate for Studio (N=2). The result confirms: core invariants hold
> under acceleration."*

Both case studies were authored by the same maintainer's agent harness.
The "N=2 validation" is methodologically a closed-loop self-validation
until a third, independent team runs Ballast on a project the maintainer
did not author.

### Rule of thumb

> **Persona simulation cannot substitute for actual external grounding.
> A persona-validated artifact is internally coherent; it is not
> externally validated.**
>
> Required external-grounding sources, in increasing strength:
>
> 1. **Eventual external persona dispatch**: a persona agent dispatched
>    by a *different maintainer* on a *different harness*, with no
>    access to the project's own prompts. The "external persona" is
>    still an LLM simulation, but it's no longer the same harness.
> 2. **Actual external user contact**: a real person (named, attributable,
>    not anonymous) installs the project from a clean shell, reports
>    back. One real user is worth ~10 persona rounds.
> 3. **N=3+ independent case studies**: another team adopts the
>    methodology on a project the methodology's author did not touch,
>    reports outcomes. N=3 is the minimum to move from "self-validated"
>    to "externally validated".
>
> Until at least source 1 lands, every persona-simulation-driven
> validation claim must carry a **"closed-loop self-validation" caveat**
> in the case study, README, and methodology document.

### Recovery

When F28 is firing (a project relies on persona simulation as primary
validation):

1. **Add closed-loop caveat to case study and README**: explicitly name
   that the validation is internal; persona simulation is a dev-loop
   step, not external grounding.
2. **Solicit at least one external user**: design-partner outreach, HN
   post, conference demo. One real-user data point breaks the closed
   loop.
3. **Track N independent applications of the methodology**. Cobrust
   Studio is N=2 by the same maintainer. The methodology becomes
   externally validated at N=3 by an independent team.
4. **Distinguish "internal coherence claim" from "external validation
   claim"** in all marketing and case-study copy. F8 (marketing
   overreach) applies: "persona-validated" is a weaker claim than
   "user-validated" and must be qualified accordingly.

### Prevention going forward

In every Ballast project that uses continuous persona testing (F27):

1. **Case-study template includes §"External grounding status"**: enumerate
   which validation sources (persona only / external persona / external
   user / independent team) have been exercised.
2. **README "Validated against" claims must cite the strongest source
   exercised**, not the most flattering. "Validated against persona
   simulation" is honest; "user-validated" without an actual user is
   F8-class overreach.
3. **Active outreach for external grounding**: a design-partner template,
   a SECURITY.md, a CONTRIBUTING.md — anything that channels external
   contact. Bus-factor 1 projects (Studio is one) cannot escape F28
   without active outreach.
4. **Methodology document carries the same caveat**: Ballast itself must
   name "N=2 validated by same maintainer; awaiting N=3 independent
   adoption" until that adoption lands.

F28 is the structural risk that makes F27 (continuous persona testing)
both valuable and dangerous. F27 is the right discipline for internal
coherence; F28 is what happens when F27's loop is treated as external
validation. The two entries close together: F27 names the legitimate
form, F28 names the failure mode, and the prevention is to always run
F27 with the F28 caveat attached.

---

---

## F1.5 — Test-corpus structural blind spot (re-derive path gap) [CANDIDATE] (F1 Sediment Family, coverage sub-form)

> **Candidate entry — confirmed once in Cobrust Studio M6 cycle (2026-05-12).** F1
> Sediment Family sub-form. Same root as F1.0 (declared invariants without
> enforcement), but the enforcement mechanism (unit tests) exists and passes —
> the gap is that the tests don't cover the *path being claimed* in the ADR, only
> the *happy path* that bypasses the claimed path. Promote from candidate if a
> second instance is observed in a different Ballast project.

### Definition

An ADR declares a wire-format or protocol invariant that involves a
**re-construct / re-derive / re-open** path: *"packed field X enables
re-derive"* / *"packed salt enables re-construct the key at restart"* /
*"serialised blob enables re-validate at next login"*. The unit test corpus
tests the happy path — `seal()` then `open()` using the same in-memory key
object — which passes trivially. No test exercises the re-derive path: extract
field X from blob → re-derive key from extracted X + passphrase → open blob
with re-derived key. Bugs in the packed field's content (wrong value packed
vs value used for derivation) are structurally invisible to the unit test
corpus, because the happy path never exercises the extraction step.

### Symptoms

- ADR §"Wire format" or §"Decision" contains language like: "packed salt
  enables re-derive at restart", "serialised token ID enables re-validate",
  "blob header encodes the derivation parameters for session recovery"
- Unit tests for the module pass 100% (all happy-path; no re-derive tests)
- Integration tests pass (they exercise API-level round-trips but use the
  same session without a drop+re-login)
- Bug manifests in Playwright E2E or production when a real user drops their
  session and re-enters their passphrase — the re-derive produces a different
  key, AEAD open fails, user sees "wrong passphrase" on a correct passphrase
- The bug is NOT findable by code review alone — the implementation looks
  correct (it packs a salt, it derives from a salt) without tracing the
  specific values

### Root cause

The test corpus was designed to verify the cryptographic operations (derive,
seal, open, tamper-detect) in isolation. None of the tests simulate the
sequence of operations a real user performs across a session boundary: seal
with key K → drop K from memory → extract packed-salt from blob → re-derive
K' from passphrase + packed-salt → open blob with K'. The test corpus is
correct against its own test design; the test design is incomplete against the
ADR's claimed invariant.

This is a structural gap, not an oversight: the developer who wrote the tests
wrote correct tests for the function signatures. The gap is that the ADR's
"packed salt enables re-derive" claim implies a test pattern that the natural
test design does not produce unless explicitly prompted by the ADR's Done-means
criteria.

### Recovery

1. When ADR §"Done means" is written, scan §"Wire format" and §"Decision"
   for any "packed X enables re-Y" language.
2. For each such claim, add a required test that exercises the re-Y path
   end-to-end: seal → extract X from blob output → re-Y(passphrase, X) →
   open. This test should pass before Phase 2 is declared complete.
3. If the bug is already shipped, the fix is to correct the packed value
   (ensure packed value = value used for derivation, not a newly-generated
   value) and add the re-derive test.

### Evidence

Cobrust Studio M6 (2026-05-12): `SessionKey::seal()` generated a fresh random
salt on each call and packed it into the blob header, but `SessionKey` was
derived from a different salt at login time. The 6 unit tests in ADR-0007's
Done-means tested seal+open on the same key — none tested re-derive from blob.
Playwright login-aead.spec.ts test 2 (restart + re-login) caught the bug the
same day as v0.2.0. Fixed at commit `3753a2b` (`SessionKey` now carries its
`derive_salt`; `seal()` packs `self.salt`). New test
`seal_then_re_derive_then_open_round_trips` locks the contract.

Case study: `cobrust-studio-experience.md §11.3`.

### Prevention going forward

When writing ADR §"Done means" for any module with a wire format:

1. Scan §"Wire format" for "packed X enables re-Y" clauses
2. For each such clause, add a required Done-means test of the form:
   ```
   <module>_packed_<X>_enables_re_<Y>:
     derive key K from (passphrase, fresh-salt)
     sealed = K.seal(payload)
     extracted_X = sealed[..len(X)]
     K2 = re_derive(passphrase, extracted_X)
     assert K2.open(sealed) == payload
   ```
3. This test class is orthogonal to tamper-detection tests (which also
   flip bits in X but don't re-derive from the flipped X) and to happy-path
   seal-open tests. All three are necessary; none is sufficient.

The general principle: **any ADR claim that references "packed field enables
reconstruct" implies a test that exercises the reconstruction path, not just
the forward path**. If the Done-means criteria don't name this test explicitly,
the claim is declared but not enforced — F1 Sediment Family.

---

## F29 — Cross-platform runner-pool dependency as a release-infra failure mode [CANDIDATE]

> **Candidate entry — confirmed twice in Cobrust Studio (v0.1.3 and v0.2.0,
> both 2026-05-12) and closed at v0.2.1.** Distinct from F1.0 (code/doc
> invariants without enforcement) because the failure is not in code or
> documentation but in the infrastructure layer that executes the release.
> Promote from candidate if a second instance is observed in a different
> Ballast project.

### Definition

A release workflow declares N build targets (platforms, architectures,
OS variants) via a CI matrix. The workflow code is correct. One or more
targets depend on a **GitHub-hosted runner pool** (or equivalent
infrastructure service) with insufficient queue depth, unpredictable
availability, or a specific runner generation that has been deprioritised
in the provider's scheduling. Multiple consecutive releases ship N-1 (or
fewer) successful artifacts for the affected targets, despite no code
changes between attempts.

### Symptoms

- `cargo build --target=X` succeeds locally on the developer's machine
- CI build for the same `--target=X` completes 0/N or times out when using
  runner label `old-generation` (e.g. `macos-13` Intel)
- The release workflow shows the target job as "queued" for 30+ minutes
  before eventually timing out or completing with a stale artifact
- The pattern recurs across multiple release tags (same missing target,
  same runner label)
- No code change produces a fix; only a runner label change resolves it

### Root cause

GitHub-hosted runner pools for older or less-popular runner generations
(`ubuntu-20.04`, `macos-13`, `windows-2019`) have smaller pool sizes than
current-generation runners. During peak CI periods or for projects with
infrequent cache warming, the queue wait time can exceed job timeouts.
The release workflow is correct; the infrastructure serving it is the
bottleneck.

For macOS specifically: GitHub maintains separate pools for Intel
(`macos-13`) and Apple Silicon (`macos-14`/`macos-15`). Apple Silicon runners
are currently more abundant and have shorter queue times. Rust supports
cross-compilation from Apple Silicon → Intel via
`--target=x86_64-apple-darwin` natively, making the pool substitution
transparent to the build output.

### Recovery

1. Identify the stalling target (check CI logs for long queue times vs
   build times).
2. Check if the runner can be substituted with a higher-availability
   alternative while keeping the `--target` flag unchanged (e.g.
   `macos-13` → `macos-14 --target=x86_64-apple-darwin`).
3. Verify that the language's toolchain supports the cross-compile path
   (Rust: yes for Apple Silicon → Intel via LLVM; Go: yes; Python: depends
   on C extensions).
4. Patch release.yml with the new runner label. Ship as a patch tag with
   no code changes (infrastructure-only patch is acceptable; see §11.4 of
   `cobrust-studio-experience.md`).
5. Validate by observing the next release: if all N targets ship first-time
   green, the runner pool was the root cause.

### Evidence

Cobrust Studio:
- v0.1.3 (2026-05-12): `x86_64-apple-darwin` build job stalled on
  `macos-13` runner; release shipped 4/5 platform tarballs.
- v0.2.0 (2026-05-12): same pattern; 4/5 tarballs.
- Sarah v3 audit predicted: "if this stalls again, consider whether the
  cross-compile setup needs to change."
- v0.2.1 (2026-05-12): `.github/workflows/release.yml` patched to
  `runner: macos-14` (with existing `--target=x86_64-apple-darwin` flag).
  **All 5 platforms green first-time.** Runner pool was confirmed root cause.

Case study: `cobrust-studio-experience.md §11.4`.

### Prevention going forward

When writing a multi-platform release workflow for the first time:

1. Check the GitHub Actions runner availability documentation for each
   runner label in the matrix. Note which generations are "current" vs
   "legacy."
2. For any target that uses a legacy runner generation, prefer cross-compilation
   from a current-generation runner if the toolchain supports it.
3. Add a comment in release.yml citing the runner substitution rationale:
   ```yaml
   # macos-14 used instead of macos-13 to avoid Intel runner pool
   # queue stalls. --target=x86_64-apple-darwin provides cross-compile.
   # See cobrust-studio v0.2.1 / Ballast F29.
   runner: macos-14
   ```
4. The "no CODE tag→patch dance" rule applies: infrastructure-only patches
   between release tags are acceptable when the audit predicted the failure
   mode. CHANGELOG the change explicitly as "infrastructure patch, no code
   changes."

**Ballast §4 ("tag → audit → patch") extends to the infrastructure layer.**
A release-infra failure mode (runner pool stall, action version deprecation,
Docker image removal) is a legitimate release regression that warrants its
own patch tag with honest CHANGELOG. It is NOT a code quality failure; it
DOES count against the release readiness gate if it blocks one or more
declared targets from shipping.

---

## F30 — Projection docs outrank the canonical snapshot (F1 Sediment Family, doc-authority sub-form)

> **F1 sub-form, confirmed.** The repo declares a canonical state record, but day-to-day editing happens in the more visible projection docs (`README`, agent guidance, operator docs). The projections drift ahead of the canonical source, so future agents inherit a persuasive but false narrative.

### Definition

A project has one document intended to be the canonical statement of current repo state, phase, verification surface, or next target. Other docs are projection layers derived from it. In practice, contributors update the projection docs first because they are easier to notice or more user-facing. The canonical doc lags, and the declared authority order silently inverts.

### Symptoms

- `README` says the project is in phase N while snapshot still says phase N-1
- Agent guidance lists commands or constraints not yet reflected in the canonical state doc
- A close-out report claims docs are synced, but only the projection docs changed
- Future agents cold-start from the stale canonical doc and make wrong dispatch or review decisions

### Root cause

Two compounding patterns:

1. **Visibility bias**: people naturally update the doc they are already reading (`README`, CLAUDE-like guidance, release notes), not the denser state ledger.
2. **Truthfulness is declared, not operationalized**: the project says "snapshot is canonical" but does not enforce update order or require a synchronized close-out set.

This is an F1-family pattern because the authority rule exists only as prose until the workflow makes it executable.

### Evidence

ADD Studio methodology codified the countermeasure explicitly after repeated emphasis during Wave 1 → Wave 2 close-out:
- `docs/agent/snapshot.md` named as canonical repo-state record
- `README.md` and `CLAUDE.md` named as projection layers
- close-out rule: update snapshot first, then synchronize the affected projections before the work is considered done

This is important because the repo's current phase, verification commands, and next target all appear in multiple top-level docs. Without a canonical-first rule, the most visible doc would naturally outrank the truth source.

### Rule of thumb

> **If a project has a canonical state document, every projection doc must be downstream of it in both authority and update order.**
>
> Close-out sequence:
> 1. Update canonical snapshot/state ledger
> 2. Update every dependent projection doc
> 3. Run doc verification
> 4. Only then report completion

### Recovery

When F30 fires:

1. Stop editing projection docs in isolation.
2. Reconcile the canonical state doc against repo reality first.
3. Diff every named projection doc against the canonical state and remove contradictions.
4. Add an explicit close-out checklist entry so future sprints cannot skip the sync.

### Prevention going forward

For any Ballast project that uses ADRs/findings/snapshot discipline:

1. Name the canonical doc explicitly in both the snapshot template and the top-level guidance docs.
2. Add a close-out rule that starts with the canonical doc and ends only when projections match.
3. Make documentation verification part of the required gate surface for doc-affecting work.
4. Treat "docs truthfulness" as a deliverable owned during dispatch, not as polish after the merge.

---

## Cobrust empirical corroboration batches (F31+)

Findings beyond F30 are organized as **per-era batch sub-directories**, each
empirically corroborated by a distinct Cobrust multi-agent run and anchored to
Cobrust commit SHAs. They are kept out of this file's body to preserve its
F1-F30 spine; consult the batch READMEs for slot maps, family clustering, and
evidence:

- `cobrust-f31-f39/` — F31-F40, Cobrust Phase F.3 → Phase I (2026-05-16/19).
- `cobrust-f41-f43/` — F41-F43, Cobrust Phase G/J (2026-05-19/20): source-surface
  leakage + device-name redaction + SPOF heavy-build host.
- `cobrust-f44-f70/` — F44-F72 (F45a sub-form; F52/F57 intentionally skipped) +
  two pattern docs (`cross-compile-target-enablement-pattern.md`,
  `ecosystem-import-chain-pattern.md`) + `methodology-deltas.md`, Cobrust v0.6.0 →
  v0.7.0 (2026-05-22/29) plus the 2026-05-29/30 dynamic-Workflow session (F71 +
  Delta 8 close + Delta 9) plus the 2026-05-30 ADR-0080/ADR-0081 FastAPI-real impl
  run (F72 + Deltas 10-11): CI-as-oracle hardening, stub/parity false-pass family,
  cross-target enablement (incl. F71 wasm-typed-call ABI fuzzer + F72 killed-runner
  CI flake), ecosystem-import chain, and 11 Ballast process deltas (incl.
  dynamic-Workflow orchestration as the default dev mode + the Elegance Law +
  mutation-prove-a-tripwire + slice-to-smallest-gated-increment). See
  `cobrust-f44-f70/README.md` and the sibling `workflow-orchestration-patterns.md`.

These batch slot numbers are Cobrust local IDs and may not align 1:1 with this
file's F-numbering (e.g. f31-f39 re-mapped local IDs onto free upstream slots).

---

## Catalogue maintenance

This catalogue is alive — add to it as you encounter new failure modes.

When adding:
1. Use `F<N>` next free number
2. Symptoms / Root cause / Recovery / Evidence / Prevention sections
3. Evidence section MUST cite a specific case-study artifact (not
   "I think we hit this once")
4. Submit via PR; reviewer should verify the failure mode is
   distinct from existing F1-F30 (and from existing F1 Sediment
   Family sub-forms F1.0-F1.5, F16, F17, F18, F19, F20, F21)

If a failure mode becomes obsolete (e.g. tool now prevents it
automatically), don't delete — mark as "superseded by <SOP>" and link.
