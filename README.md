# Ballast

> **Ballast**（压舱石）is a working discipline for multi-week projects where agents write most of the code. It is the righting mass: ADRs, findings, and the failure-mode catalogue that keep speed from turning into sediment.
>
> Agent 负责写。压舱石负责别翻。
>
> One way of doing agent-driven development — not the name of the category, and not a framework. Previously called Agent-Driven Software Development (ADSD).
>
> Distilled from running a multi-agent Rust compiler project
> where AI agents wrote ≥ 70% of the code under human strategic direction.
> The founding distillation snapshot is a 12-day intensive run; the source
> project kept running well past that window, and the failure-mode catalogue
> grew with it — from the original F1–F30 to F1–F70 across three later
> corroboration batches, plus 8 methodology deltas.

[![License: Apache 2.0 / MIT](https://img.shields.io/badge/license-Apache--2.0%20OR%20MIT-blue.svg)](#license)
[![Failure modes: F1–F70](https://img.shields.io/badge/failure--modes-F1%E2%80%93F70-orange.svg)](#how-the-methodology-has-evolved)
[![Methodology deltas: 8](https://img.shields.io/badge/methodology--deltas-8-orange.svg)](#how-the-methodology-has-evolved)
[![Audit topology: 8-dimension](https://img.shields.io/badge/audit-8--dimension-orange.svg)](#how-the-methodology-has-evolved)
[![Status: battle-tested, not orthodoxy](https://img.shields.io/badge/status-battle--tested-blue.svg)](#status)

## What this is

Ballast is **not a framework**. It's a documented working style that survived
contact with reality. The founding window — a 12-day intensive run
(2026-04-30 → 2026-05-12) — produced ~278 commits, ~2,611 tests, 49 ADRs
(0001..0048 + 0047a), 27 findings, the original **F1–F30** failure-mode
catalogue, and 2 P0 codegen bugs caught via organic stress test, shipping
through `v0.1.2` stable publicly.

That was the *distillation snapshot*, not the finish line. The source project
kept running well past the 12-day window, and every new failure mode it hit
got back-ported here. The catalogue grew from the original **F1–F30** to
**F1–F70** across three later corroboration batches (`cobrust-f31-f39` /
`cobrust-f41-f43` / `cobrust-f44-f70`, with an F45a sub-form; F52/F57 are
intentional gaps in the source project's local numbering), plus **8
methodology deltas** that refine how Ballast *runs* the multi-agent process.

Ballast codifies the discipline that kept the project coherent across all of it:
ADRs as decision capture, findings as negative-result memory, bilingual docs
by default, wave-based delivery, an all-top-tier sub-agent dispatch rule, an
**8-dimension pre-release audit topology** (4 internal lenses + 3 user personas
+ deep-source-read), mandatory independent post-author audit, and
release-readiness verification before any public-facing change.

## When to use Ballast

- You're managing a software project where AI agents do most of the coding
  (≥ 70% of LOC produced by agents)
- You run **3+ parallel sub-agents** and need a way to prevent sediment /
  drift / silent regressions
- You're doing **stateful project management** (multi-week / multi-sprint),
  not one-shot tasks
- The project has external stakeholders (release notes, public roadmap,
  contributors) that need an honest narrative

Ballast is **overkill** for one-shot prompt → answer flows, single-developer
IDE-loop coding (Cursor / Claude Code already handle), and < 3-agent
simple workflows.

## How the methodology has evolved

Ballast wasn't designed up front — it accreted from successive runs of the source
project, each era adding failure modes and dispatch refinements. The catalogue
grew in four batches; reading them in order shows the methodology hardening
against problems it didn't know it had yet.

```mermaid
flowchart LR
    A["<b>F1–F30</b><br/>Founding 12-day run<br/>2026-04-30 → 05-12<br/>~278 commits · 49 ADRs<br/>v0.1.2 shipped"]
      --> B["<b>F31–F40</b><br/>v0.3.0 cadence<br/>cascade-discovery deficit<br/>+ self-rule-skip<br/>+ false-stall watchdog"]
    B --> C["<b>F41–F43</b><br/>Phase G/J sprints<br/>source-surface leakage<br/>+ opsec redaction<br/>+ build-host SPOF"]
    C --> D["<b>F44–F70</b><br/>v0.6.0 → v0.7.0 run<br/>2026-05-22 → 05-29<br/>CI-as-oracle hardening<br/>+ stub/parity false-pass<br/>+ cross-target enablement"]
    D --> E["<b>8 Methodology Deltas</b><br/>how Ballast <i>runs</i><br/>all-top-tier dispatch ·<br/>mandatory audit ·<br/>dynamic-Workflow mode"]
```

The arc, in one line each:

- **F1–F30 (the distillation snapshot)** — the founding catalogue: snapshot
  sediment, silent miscompile, strategic blindness, the F1 "declared-rule ≠
  enforced" sediment family. Distilled from the 12-day intensive run.
- **F31–F40** — corroborated on the `v0.3.0` cadence: cascade-discovery deficit
  (a predicate flip leaves latent consumers), agents skipping rules they just
  wrote, commit-message-vs-diff scope drift, the 600s stream-watchdog false-stall
  signal.
- **F41–F43** — Phase G/J: a codegen-internal primitive leaking into the source
  surface (LLM-first training-data-overlap violation), device-name opsec leakage
  into git history, and the single-point-of-failure heavy-build host.
- **F44–F70** — the largest later batch: CI-cache stale-green, backend stubs
  silently shipped, type-conditional codegen emitting wrong output, fresh-workspace
  identity leak, and a whole cross-target-enablement family (the source project
  added new compile targets, and each enablement seam surfaced a failure mode).
- **8 Methodology Deltas** — not failure modes but refinements to how Ballast
  *dispatches and audits*: all-top-tier sub-agents (the tier matrix is retired),
  dispatcher-as-context-custodian, mandatory independent post-author audit,
  lockfile-staging in the atomic commit, chain-generality verified against the
  diff, a CI-infra-hardening playbook, honest-signal discipline, and the newest —
  **dynamic-Workflow orchestration** (deterministic fan-out → synthesis → impl →
  audit scripts, with a socket-resilience refinement after a transient agent death
  poisoned a downstream audit verdict).

The **8-dimension audit topology** also matured across these eras: 4 internal
lenses (security / doc-consistency / public-readiness / code-quality) + 3 user
personas (target user / skeptic expert / evaluator) + a dimension-free
deep-source-read pass that reads source line-by-line with no lens. See
[`SKILL.md`](./plugins/ballast/skills/ballast/SKILL.md) Part 1 for
the full topology and its empirical leverage table.

Full evidence (per-finding Cobrust commit SHAs + the methodology-deltas doc)
lives under
[`reference/`](./plugins/ballast/skills/ballast/reference/) — see
[Repository layout](#repository-layout).

## Install

### As a Claude Code plugin (recommended)

```
/plugin marketplace add Cobrust-lang/ballast
/plugin install ballast@ballast
```

After install, invoke via `/ballast` or let Claude pick it
automatically based on context — the description-triggered activation fires
for multi-agent dispatch planning, ADR drafting, F1–F70 failure-mode triage,
pre-release audit team design, and similar prompts.

### As a personal skill (fallback, no plugin system)

If you can't or don't want to use `/plugin install`:

```sh
mkdir -p ~/.claude/skills
git clone --depth 1 https://github.com/Cobrust-lang/ballast.git /tmp/ballast-src
cp -r /tmp/ballast-src/plugins/ballast/skills/ballast ~/.claude/skills/
rm -rf /tmp/ballast-src
```

### Read-only (no install)

The methodology is plain markdown. Just read
[`plugins/ballast/skills/ballast/SKILL.md`](./plugins/ballast/skills/ballast/SKILL.md)
top-to-bottom (~30 min read). Install matters only if you want Claude to
invoke it automatically based on conversation context.

## Repository layout

```
ballast/
├── .claude-plugin/
│   └── marketplace.json                       # Self-hosted single-plugin marketplace catalog
├── plugins/
│   └── ballast/                                  # Plugin root (matches marketplace.json source)
│       ├── .claude-plugin/
│       │   └── plugin.json                    # Plugin manifest
│       └── skills/
│           └── ballast/      # Skill — auto-discovered by Claude Code
│               ├── SKILL.md                   # Main methodology document (~30 min read)
│               ├── reference/
│               │   ├── failure-modes-catalogue.md  # F1-F30 anti-patterns with empirical evidence
│               │   ├── cobrust-f31-f39/        # F31-F40 corroboration batch (v0.3.0 cadence)
│               │   ├── cobrust-f41-f43/        # F41-F43 corroboration batch (Phase G/J)
│               │   ├── cobrust-f44-f70/        # F44-F70 batch + 2 pattern docs + methodology-deltas.md
│               │   ├── evals-first-development.md       # Cross-pollination (v1.2.0)
│               │   ├── context-window-strategy.md       # Long-session context tiers
│               │   ├── cross-session-memory-architecture.md  # 4-layer memory model
│               │   ├── prompt-engineering-patterns.md   # Role priming, anti-hallucination
│               │   └── cost-monitoring-discipline.md    # Cost as a diagnostic signal
│               ├── case-study/
│               │   ├── cobrust-multi-agent-experience.md   # The founding case study (N=1)
│               │   └── cobrust-studio-experience.md        # N=2 dogfood (M0-M7 cycle)
│               └── templates/
│                   ├── adr-template.md        # Architecture Decision Record
│                   ├── finding-template.md    # Negative result / failure capture
│                   ├── dispatch-prompt-p9.md  # Tech Lead sub-agent dispatch
│                   ├── dispatch-prompt-p7.md  # Senior Engineer sub-agent dispatch
│                   ├── handoff-cover-letter.md  # Cross-session handoff
│                   └── snapshot-template.md   # Project state snapshot
├── CONTRIBUTING.md
├── LICENSE-APACHE
├── LICENSE-MIT
└── README.md                                  # this file
```

## Quick start (after install)

1. Read [`SKILL.md`](./plugins/ballast/skills/ballast/SKILL.md) for the full methodology (~30 min read).
2. Read [`reference/failure-modes-catalogue.md`](./plugins/ballast/skills/ballast/reference/failure-modes-catalogue.md) for the founding **F1–F30** anti-patterns you'll likely hit. Don't re-derive them.
3. Skim the corroboration batches under [`reference/`](./plugins/ballast/skills/ballast/reference/) — [`cobrust-f31-f39/`](./plugins/ballast/skills/ballast/reference/cobrust-f31-f39/), [`cobrust-f41-f43/`](./plugins/ballast/skills/ballast/reference/cobrust-f41-f43/), and [`cobrust-f44-f70/`](./plugins/ballast/skills/ballast/reference/cobrust-f44-f70/) (which also carries the [`methodology-deltas.md`](./plugins/ballast/skills/ballast/reference/cobrust-f44-f70/methodology-deltas.md) — read this if you're choosing a dispatch/audit topology).
4. Read [`case-study/cobrust-multi-agent-experience.md`](./plugins/ballast/skills/ballast/case-study/cobrust-multi-agent-experience.md) to see Ballast applied in practice (warts and all).
5. Copy the relevant template from [`templates/`](./plugins/ballast/skills/ballast/templates/) into your project's `docs/agent/` tree.
6. Start writing ADRs as decisions actually happen — not speculatively.

## Documentation

User-facing docs are in [`docs/human/`](./docs/human/) (zh + en parallel per Ballast §3 bilingual mandate). Agent-facing meta-conventions for this repo are in [`docs/agent/`](./docs/agent/).

### Bilingual user docs

| Topic | 中文 | English |
|---|---|---|
| Getting started — 30-min onboarding | [`docs/human/zh/getting-started.md`](./docs/human/zh/getting-started.md) | [`docs/human/en/getting-started.md`](./docs/human/en/getting-started.md) |
| Concept map — mermaid diagrams + narrative | [`docs/human/zh/concept-map.md`](./docs/human/zh/concept-map.md) | [`docs/human/en/concept-map.md`](./docs/human/en/concept-map.md) |

### Agent-facing meta-conventions

- [`docs/agent/conventions.md`](./docs/agent/conventions.md) — repo structure, frontmatter contracts, bilingual mandate enforcement, commit message format, identity hygiene (F21)

### Doc coverage gate

`scripts/doc-coverage.sh` enforces Ballast §3 bilingual mandate on this repo itself: every `docs/human/zh/*.md` MUST have a parallel `docs/human/en/*.md`. Run locally before commits:

```sh
bash scripts/doc-coverage.sh
```

The script also verifies reference files have YAML frontmatter, ADR files are zero-padded monotonic, and `scripts/check_ballast_docs.py --self-test` passes. That self-test is the methodology repo's copy of the adopting-project snapshot gate (roster exactly once, `base_head` ancestry, resolvable `last_verified_commit`, evidence grades, chosen drift axis). An adopting project runs `python3 scripts/check_ballast_docs.py` on its own root. See [`reference/adopting-gates.md`](./plugins/ballast/skills/ballast/reference/adopting-gates.md).

## Origin

Ballast was extracted from the [Cobrust](https://github.com/Cobrust-lang/cobrust)
project, a Rust-implemented Python successor with an AI-native compiler.
The **distillation snapshot** is the founding intensive run: first commit
2026-04-30 → `0.1.0-beta` tag 2026-05-10 → `0.1.0` stable 2026-05-11, with
`v0.1.2` + α Phase F.2 following — ~278 commits over 12 wall-clock days,
coordinated by multiple parallel Claude agents (Opus 4.7 and Sonnet 4.6) via
the methodology you'll find in
[`SKILL.md`](./plugins/ballast/skills/ballast/SKILL.md).

The project **did not stop there.** It kept running well past the 12-day
window, and the
[`reference/`](./plugins/ballast/skills/ballast/reference/)
batches (F31–F40, F41–F43, F44–F70 + 8 methodology deltas) back-port every new
failure mode and dispatch refinement that continued run produced — taking the
catalogue from the original F1–F30 to **F1–F70**. The 49-ADR / 27-finding /
12-day figures describe the founding window; treat them as a **floor**, not the
current total. (The origin project's later product milestones live in the
separate [Cobrust](https://github.com/Cobrust-lang/cobrust) repo and are not
re-measured here.)

The case study at [`case-study/cobrust-multi-agent-experience.md`](./plugins/ballast/skills/ballast/case-study/cobrust-multi-agent-experience.md)
documents both what worked and what broke. The failure modes catalogue
(now F1–F70) captures lessons we'd rather not re-learn.

## Status

**Validation N = 2**: Cobrust (this methodology's birthplace, sustained from
the founding 12-day run through every later corroboration batch) plus a
second-project dogfood, Cobrust Studio (M0–M7 cycle), captured in
[`case-study/cobrust-studio-experience.md`](./plugins/ballast/skills/ballast/case-study/cobrust-studio-experience.md).
The bulk of the empirical evidence is still single-lineage, so treat the
methodology as well-tested-in-context rather than universally proven.

We are still looking for design partners willing to apply Ballast to an
unrelated third project so the methodology can be tested further outside its
founding context. File an issue describing your project if interested.

Ballast is **battle-tested but not orthodoxy**. Adapt it. The catalogue already
runs **F1–F70**; if you find a failure mode none of those cover, propose the
next slot via a PR — add a finding file under the appropriate
[`reference/`](./plugins/ballast/skills/ballast/reference/) batch
(or open a new batch dir) following the same Symptoms / Root-cause / Recovery /
Evidence format, and cite a real commit as the ground-truth anchor.

## Contributing

See [`CONTRIBUTING.md`](./CONTRIBUTING.md). We use Ballast to evolve Ballast —
contributions follow the same ADR + finding + dispatch discipline the
methodology itself describes.

## License

Licensed under either of

- Apache License, Version 2.0 ([LICENSE-APACHE](./LICENSE-APACHE) or
  http://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](./LICENSE-MIT) or
  http://opensource.org/licenses/MIT)

at your option.

### Contribution

Unless you explicitly state otherwise, any contribution intentionally
submitted for inclusion in the work by you, as defined in the Apache-2.0
license, shall be dual licensed as above, without any additional terms or
conditions.

## Acknowledgements

The methodology is shaped by patterns from:

- [Linear Method](https://linear.app/method) — calm-tech + cycles
- [TigerBeetle Way](https://tigerstyle.dev) — assertion discipline + deterministic simulation testing
- [Stripe internal playbook](https://stripe.com/blog) — memos over meetings
- [Basecamp Shape Up](https://basecamp.com/shapeup) — appetite-based scoping
- [OpenTelemetry semantic conventions](https://opentelemetry.io) — observability vocabulary
- [SLSA v1.1](https://slsa.dev) — provenance attestation
- [Astral's `uv` / `ruff`](https://astral.sh) — single-tool wedge UX

None of these tools or organizations endorse Ballast; the methodology
borrows ideas, not affiliation.
