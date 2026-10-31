---
name: Evals-first development discipline
description: Build the evaluation harness before the feature. Anthropic's central claim "evals are the moat" applied to Ballast. Every public capability gets a falsifiable test before implementation, not after.
type: reference
version: 1.0.0
date: 2026-05-12
status: active
relates_to: [skill:SKILL.md §"Wave + Tx pattern", reference:failure-modes-catalogue.md F19+F20]
---

# Evals-first development

> **Anthropic central claim**: "Evals are the moat. Better evals beat better models."
> Ballast adopts this: every Cobrust public capability has a falsifiable acceptance signal **before** the impl Tx fires. This is the positive form of F20 (constitution-vs-workflow alignment) — workflow enforces the rule by requiring the eval to fail-then-pass.

## When this applies

For any task type:

- Adding a new public API surface (CLI flag, language feature, stdlib fn)
- Translating a Python library (every entrypoint = its own eval slice)
- Migrating an internal API (eval guards behavior preservation)
- Performance-claim release (eval = repeatable benchmark)
- LLM-driven anything (eval is the only way to detect prompt drift)

Skip evals only for:

- One-shot scripts with no future maintenance
- Doc-only changes (release-readiness verify is its own form, see F19)
- Strict refactors with full test coverage already

## Anthropic-pattern adoption

### Eval as code, not document

Anthropic's evals are runnable artifacts — `pytest`-style scripts, JSON-line inputs/outputs, scoring functions. Not markdown narratives.

Ballast shape:

```
project-root/
├── evals/
│   ├── <feature-name>/
│   │   ├── cases.jsonl          # one (input, expected) per line
│   │   ├── score.py             # scoring fn (exact / fuzzy / LLM-judge)
│   │   ├── run.sh               # entrypoint
│   │   └── REPORT.md            # last-run summary, machine-updated
│   └── README.md                # eval directory index
```

### Eval categories (Anthropic taxonomy)

| Category | When | Example for Cobrust |
|---|---|---|
| **Exact match** | Deterministic output | `cobrust build hello.cb` exit 0 + stdout `hello, world` |
| **Fuzzy match** | Allows whitespace / order drift | TOML round-trip; output equivalent under canonicalization |
| **Regex / structural** | Format known, content variable | Compiler error messages match pattern `/error\[\w+\]:/` |
| **LLM-judge** | Open-ended (docs, NL output) | Translated library's docstrings preserve original meaning |
| **Differential** | Compare against oracle | `cobrust-tomli.parse(s)` == `cpython tomllib.loads(s)` for 1000+ fuzz inputs |

Differential evals are Ballast's strongest pattern — already baked in for tomli T1.1. Generalize.

### Minimum eval bar (Anthropic guideline)

- **≥ 50 cases** per public capability
- **≥ 10 adversarial cases** (boundary conditions, malformed input, edge encodings)
- **Reproducible**: `bash evals/<name>/run.sh` exits non-zero on regression
- **Cheap**: full eval suite runs in < 5 min, fuzz suite in < 30 min

### Eval delta as merge gate

The Anthropic moat is enforced via: **PR must report eval delta**.

```
[P9-COMPLETION] eval-delta block (required for any merge touching public surface):
- evals/<name>/cases.jsonl: +N cases (was M, now M+N)
- pass rate before: <X>/<M> → after: <Y>/<M+N>
- adversarial cases: +K new (was J, now J+K)
- regression check: 0 prior cases newly failing
- if ANY prior case newly fails → BLOCK merge until justified or fixed
```

CTO 守闸 protocol: spot-check the eval delta. Don't merge sprints that touch public surface without an eval-delta block.

## OpenAI-pattern adoption

### Function/tool eval (structured-output enforcement)

OpenAI's strongest practice: **if your agent emits structured output, eval the structure**.

For Ballast: any sub-agent reporting `[P9-COMPLETION]` should emit a JSON-shaped block. CTO can machine-parse + verify required fields present.

```
[P9-LC100-COMPLETION]
```yaml
phase_1_adr: { sha: 3839742, status: accepted }
phase_2_buckets:
  - { name: B1, pass: 27, compile_fail: 2, runtime_fail: 1 }
  - { name: B2, pass: 24, compile_fail: 4, runtime_fail: 2 }
  - { name: B3, pass: 22, compile_fail: 5, runtime_fail: 3 }
  - { name: B4, pass: 9,  compile_fail: 1, runtime_fail: 0 }
total_pass: 82
total_fail: 18
ramp_recommendation: GO_TIER_B
bug_patterns_top5:
  - { signature: "i8/i64 mismatch in nested if", count: 4, finding: lc100-i8-i64-nested-if }
  - ...
```

CTO `yq` or `jq` the YAML; verify fields; spot-check 3 random bugs.

### OpenAI Evals framework (open source)

OpenAI Evals repo (github.com/openai/evals) is well-documented. Ballast shouldn't reinvent — adopt their core types:

- `match` — exact substring
- `fuzzy_match` — token / whitespace tolerant
- `model_graded` — LLM-as-judge with own evaluator model
- `code_run` — execute generated code, compare output

Ballast's `score.py` per-eval-folder can wrap OpenAI Evals primitives.

## Ballast integration with existing patterns

### Wave + Tx + eval delta

Existing pattern: every Wave merge has 5-gate green (fmt / clippy / build / test / doc-coverage).

Add 6th gate for any public-surface Wave: **eval delta non-regression**. New cases land + 0 prior cases newly failing.

This 6th gate is the systemic closure of F20 (constitution mandate without workflow alignment). It makes "evals first" a binding mandate, not aspiration.

### Eval-first vs TDD-pair (already in Ballast)

These are complementary, not competing:

- **TDD-pair** (Phase 2 in dispatch): test agent writes test corpus first, dev agent implements to pass. Per-feature TDD.
- **Eval-first** (Phase 0 in sprint): eval harness exists before the feature is dispatched. Per-public-surface lifetime guard.

TDD pair tests that the impl matches the test corpus this sprint. Evals catch that impl still matches behavioral contract across sprint history.

### Finding ↔ eval bidirectional

When a finding is discovered (e.g. `lc100-i8-i64-nested-if`), the **same sprint that fixes the bug must add an eval case that catches it next time**. This is the prevention layer beyond the documentation layer.

`docs/agent/findings/<slug>.md` must have a §"Eval case added" section listing the line in `evals/<feature>/cases.jsonl` that catches this specific failure.

## Concrete template

Inline template (copy this into your project's `evals/<feature>/REPORT.md` — a dedicated `templates/eval-template.md` may be split out in a future Ballast release):

```
---
name: <feature>-evals
description: <one-line behavior under eval>
date: <date>
last_verified_commit: <SHA>
case_count: <N>
adversarial_count: <K>
oracle: <Python lib | manual | differential against ...>
---

# Evals: <feature>

## Behavior under eval

<2-3 sentences. The falsifiable claim about what the feature does.>

## Eval suite layout

- `cases.jsonl` — N input cases with expected output
- `score.py` — scoring function (cite category: exact / fuzzy / regex / model_graded / code_run)
- `run.sh` — entrypoint, exits non-zero on regression

## Adversarial cases (subset of cases.jsonl)

<list the K cases that target edge conditions; identify them by line index>

## Last run

| Field | Value |
|---|---|
| Date | <date> |
| Commit | <SHA> |
| Pass | <pass> / <total> |
| New failures vs prior | <K> |
| Regression status | <PASS / FAIL> |

## Pitfalls

- LLM-judge eval drifts if evaluator model changes. Pin evaluator model in `score.py`.
- Differential evals need pinned oracle version. Document oracle version in frontmatter.
```

## Pitfalls

| Pitfall | Symptom | Recovery |
|---|---|---|
| Evals as documentation, not runnable code | `cases.jsonl` exists but no `run.sh` | Promote to runnable in 1 PR or delete |
| Eval coverage cliff: tons of easy cases, no adversarial | All cases pass on first try | Demand `adversarial_count ≥ N/5` in frontmatter |
| LLM-judge instability | Same case gives different verdict on rerun | Pin evaluator model + temperature 0 + cache responses |
| Differential eval oracle drift | Oracle library version bumps and evals silently re-baseline | Pin oracle version in frontmatter + verify in CI |
| Eval delta forgotten in PR | Sub-agent completion report omits eval-delta block | Make `[P9-COMPLETION]` template require the block |

## Cross-references

- `SKILL.md` §"Wave + Tx commit tags" — eval delta is the 6th gate
- `reference/failure-modes-catalogue.md` F19 (release install-not-tested) — eval-first is the systemic prevention
- `reference/failure-modes-catalogue.md` F20 (constitution-vs-workflow) — eval-first IS the workflow that enforces "test-first" mandate
- Anthropic: https://www.anthropic.com/engineering (search "evals")
- OpenAI Evals: https://github.com/openai/evals
