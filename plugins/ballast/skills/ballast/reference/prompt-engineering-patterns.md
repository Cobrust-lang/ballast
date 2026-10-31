---
name: Prompt engineering patterns for sub-agent dispatch
description: Distilled prompt engineering patterns from Anthropic and OpenAI public guidance, adapted for Ballast sub-agent dispatch context. Covers chain-of-thought, few-shot, structured output, role priming, anti-hallucination guards.
type: reference
version: 1.0.0
date: 2026-05-12
status: active
relates_to: [skill:SKILL.md §"Two-phase dispatch", templates:dispatch-prompt-p7.md + dispatch-prompt-p9.md]
---

# Prompt engineering patterns

> When you spawn a sub-agent, the prompt is your only lever. A sub-agent with a poorly written prompt cannot recover at runtime — there's no second chance. This reference codifies the patterns Anthropic and OpenAI publicly recommend, adapted to Ballast's sub-agent dispatch context.

## When this applies

- Writing any P9 or P7 dispatch prompt
- Designing a new sub-agent role
- Diagnosing why a sub-agent went off the rails
- Auditing existing dispatch templates for gaps

Not for: writing user-facing docs, marketing copy, or release notes (different audience, different goals).

## Core principles (Anthropic + OpenAI consensus)

### P1 — Explicit role + scope first

Start every sub-agent prompt with:

```
You are <ROLE> delivering <SPECIFIC SCOPE>.
Your deliverable is <ARTIFACT>.
You do NOT do <BLACKLIST: e.g. "modify files outside crates/cobrust-mir/">.
Time budget: <DURATION>.
```

Role priming concentrates the agent's behavior. Without it, generic Claude / GPT defaults take over — verbose, hedging, broad-scoped.

### P2 — Required-reads section before mission

Sub-agents have no prior context. List the exact files they must read before starting work:

```
REQUIRED READS (read all before any tool call):
- /abs/path/to/relevant/ADR.md
- /abs/path/to/spec.md
- /abs/path/to/existing/test_surface.rs
```

Absolute paths. Not "look in the docs folder."

### P3 — Mission expressed as a verifiable claim

Bad: "Implement stdin support."

Good: "Implement `input(prompt: str) -> str` such that the test corpus in `crates/cobrust-stdlib/tests/input_corpus.rs` passes with 0 failures."

A verifiable claim has: a specific surface (`input(...)`), an acceptance signal (test corpus), and a measurable outcome (0 failures). The agent can self-check progress against this.

### P4 — Anti-hallucination guards

Three guards Anthropic specifically calls out:

1. **"Cite or admit"**: "When making a quantitative claim (test count, file count, SHA), include the verifying command in the same response. If you don't have the command result, say 'unverified'."
2. **"No phantom paths"**: "If you reference a file path, only reference paths returned by an actual tool call this session. Don't invent plausible-looking paths."
3. **"Match-or-mismatch"**: "When the user provides a value and you echo it back, ensure character-for-character match. If your output differs even by case or whitespace, flag the discrepancy explicitly."

### P5 — Output structure first, content second

OpenAI's structured-output discipline: define the output schema before describing what goes in each field.

Bad: "Return a completion report with all the details."

Good:
```
Report format (must include these exact section headers):

[P7-MISSION-COMPLETION]
- Branch: <name>
- Final SHA: <40-char hex>
- Gate verdicts:
  - fmt: <pass | fail with count>
  - clippy: <pass | fail with count>
  - build: <pass | fail>
  - test: <pass | fail with count>
  - doc-coverage: <pass | fail>
- Empirical evidence:
  - <command>: <output snippet>
- Followups: <bullet list>
- Escalations: <bullet list or "none">
```

The agent fills the slots. Structure resists drift.

## Pattern catalogue

### PT1 — Chain-of-thought elicitation

Anthropic + OpenAI: explicit "think step by step" works on hard tasks but hurts on simple ones.

Use for: design decisions, debugging, ambiguous specs.
Skip for: well-scoped impl tasks (TDD pair handles the structure).

Form:
```
Before writing code, write 3-5 sentences answering:
1. What does the spec actually require?
2. What's the simplest implementation that meets the spec?
3. What edge cases must the impl handle?
4. What's an alternative implementation, and why was it rejected?
5. What's the test that would catch a regression here?

Then write the code.
```

### PT2 — Few-shot examples (for output format)

When you want the sub-agent's output to follow a specific format, **show 1-2 examples in the prompt itself**.

Form:
```
Example completion report (do NOT copy these literal values; use this STRUCTURE):

[P7-EXAMPLE-COMPLETION]
- Branch: feature/foo-bar
- Final SHA: abcd1234abcd1234abcd1234abcd1234abcd1234
- Gate verdicts:
  - fmt: pass (0 diff)
  - clippy: pass (0 warnings)
  - ...
```

Anti-pattern: telling without showing. "Return a structured report" without an example produces freeform prose.

### PT3 — Role priming with negative example

Form:
```
You are a P9 tech lead. Your deliverable is Task Prompts for P7 sub-agents.

You do NOT:
- Edit source files yourself (that's P7 work)
- Run cargo test on feature branches (that's P7 work)
- Push to remote on feature branches (that's P7's deliverable)
- Ask the user about decisions covered by the constitution

You DO:
- Draft ADRs for design decisions (~3 hr opus solo work)
- Spawn P7 sub-agents for impl
- Review their completion reports
- Merge cleanly after independent gate verification
```

The negative blacklist concentrates the agent's behavior more reliably than the positive whitelist alone.

### PT4 — Structured output via JSON / YAML block

When downstream parsing is needed (CTO will `yq` the result):

```
After the human-readable report, append a YAML block with these fields:

```yaml
status: success | partial | failed
final_sha: <40-char hex>
gates:
  fmt: { pass: true, count: 0 }
  clippy: { pass: true, count: 0 }
  build: { pass: true }
  test: { pass: true, total: 2611, failed: 0 }
  doc_coverage: { pass: true }
followups:
  - <string>
escalations:
  - <string>
```
```

Both human-readable and machine-parseable.

### PT5 — Refusal / escalation conditions

Tell the agent when to STOP and report instead of continuing:

```
STOP and report to CTO if any of:
- The ADR's "Done means" is unreachable with the spec as written
- The spec contradicts another ADR — escalate the conflict
- 600s+ stream-idle on cargo test (likely environment issue)
- > 50 retry attempts on any single failing test (root cause is deeper)

In these cases, report partial work + ask for guidance. Don't loop indefinitely.
```

### PT6 — Self-verification block

Before submitting completion, agent must verify own claims (Anthropic anti-hallucination):

```
VERIFICATION (run these commands and paste raw output before submitting):
- git log --oneline main..HEAD | head -5
- cargo test --workspace --locked 2>&1 | tail -3
- bash scripts/doc-coverage.sh 2>&1 | tail -3
- grep -c "F<N>" reference/failure-modes-catalogue.md (if claiming N entries)
```

The agent's claim only counts if verification command output is pasted alongside.

## Ballast-specific patterns

### PT7 — Difficulty self-rating (per D-matrix)

Every P9 dispatch must include:

```
DIFFICULTY-RATING (mandatory):
- D-RATING: D0 / D1 / D2 / D3 / D4 / D5
- RATIONALE: <2-3 sentences citing specific crates/files/edge cases>
- MODEL-DEV: sonnet | opus
- MODEL-TEST: sonnet | opus | n/a
- PAIR: yes (D1/D2/D3/D5) | no (D0/D4)
```

This pattern catches model-tier mismatches before agent spawn.

### PT8 — Identity hygiene (F21 closure)

For agents producing persistent artifacts:

```
Sign commits and documents with your SESSION ID, not your role handle alone.

Wrong: `Co-Authored-By: review-claude`
Right: `Co-Authored-By: review-claude (session 4bb35f43)`

Wrong: "— CTO, 2026-05-12"
Right: "— CTO session XYZ, 2026-05-12"
```

### PT9 — Release-readiness guard (F19 closure)

For any commit touching user-facing artifact:

```
Before declaring this Tx done, spawn a P7 sonnet release-readiness agent
to clean-shell-verify install commands in this commit's changes. See
cto_operations_runbook.md §"Release-readiness agent".

Do NOT self-attest "the install command works" without independent
verification. F17/F19 closure mechanism.
```

## Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Generic role ("you are a helpful AI") | Sub-agent over-explains, hedges, asks unnecessary questions | Replace with specific role + scope (P1) |
| Mission as a verb without scope | Sub-agent expands work indefinitely | Reframe as verifiable claim (P3) |
| No required-reads list | Sub-agent makes up plausible-but-wrong file paths | Required-reads with absolute paths (P2) |
| "Be thorough" | Long, low-density output | Demand structured output (P5 / PT4) |
| No escalation conditions | Sub-agent retries forever | PT5 explicit STOP conditions |
| No verification block | Claims drift from reality (F17) | PT6 mandatory verification |
| No difficulty rating | Model tier mismatch (F20 family) | PT7 mandatory D-rating |
| Generic sign-off "review-claude" | Cross-session identity overload (F21) | PT8 session-ID stamping |

## Anti-patterns (cross-reference to F-patterns)

- **F13 (plan-vs-execute coherence gap)**: prompt says "do X carefully" but doesn't specify what "carefully" looks like in execution. Fix: PT5 + PT6 explicit verification.
- **F17 (KPI self-report fidelity)**: agent claims completed work without verification. Fix: PT6 mandatory verification block.
- **F19 (install-not-tested)**: prompt asks agent to write docs but doesn't require execution verification. Fix: PT9 release-readiness guard.
- **F21 (cross-session identity overload)**: agent signs with bare role handle. Fix: PT8 session-ID stamping.

## Cross-references

- `templates/dispatch-prompt-p9.md` — P9 template applies these patterns
- `templates/dispatch-prompt-p7.md` — P7 template applies these patterns
- `reference/failure-modes-catalogue.md` — anti-patterns these prompts mitigate
- `reference/evals-first-development.md` — verification block ↔ eval delta
- Anthropic prompt engineering guide: https://www.anthropic.com/engineering
- OpenAI prompt engineering best practices: https://platform.openai.com/docs/guides
