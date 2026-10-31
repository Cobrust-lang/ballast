---
name: Context-window strategy for long agent sessions
description: Positive practices for organizing a multi-hour / multi-week agent session so the context stays useful across compaction events. Complements F16 (post-compaction identity drift) by codifying what should be in memory, what should be re-derivable, what's transient.
type: reference
version: 1.0.0
date: 2026-05-12
status: active
relates_to: [skill:SKILL.md §"Snapshot discipline", reference:failure-modes-catalogue.md F16, reference:cross-session-memory-architecture.md]
---

# Context-window strategy

> Long sessions degrade. Compaction is automatic but lossy. The agent that survives the compaction is the one whose **identity, current state, and operative rules are in the persistent layer**, not the transcript. This reference codifies what goes where.

## When this applies

- Any session expected to run > 50K tokens or > 4 hours wall-clock
- Any agent role that should survive context compaction (CTO, P9 tech lead, review-claude)
- Any project where memory files / snapshot files / handoff docs exist

If you're a one-shot agent (< 5 tool calls, single deliverable), this reference is overkill — just execute and return.

## Three-tier model

Adopt three explicit context tiers. Every piece of information lives in exactly one tier:

```
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 1: Persistent (auto-memory, repo, version control)                 │
│  Survives compaction + session restart + machine change                  │
│  - Identity preamble (you are P9 / CTO / review-claude)                 │
│  - Operative rules (D-matrix, dev/test pair, F1-Fxx awareness)          │
│  - Project snapshot (HEAD, ADR roster, finding ledger)                  │
│  - Cross-references (memory file → other memory files)                  │
├────────────────────────────────────────────────────────────────────────┤
│ TIER 2: Session-scoped (this conversation's context)                    │
│  Survives within session but not across sessions                        │
│  - Current sprint's working state (which Tx in progress)                │
│  - Files read this session (don't re-read what you already have)        │
│  - Decisions made this turn (will go to ADR or memory at end of sprint) │
├────────────────────────────────────────────────────────────────────────┤
│ TIER 3: Transient (one tool call at a time)                             │
│  Doesn't need to persist; if needed again, re-fetch                     │
│  - Bash output of intermediate verification                              │
│  - Read-tool output for files not central to decision                   │
│  - Search results, grep outputs                                          │
└────────────────────────────────────────────────────────────────────────┘
```

The discipline: **Tier 1 must be sufficient to bootstrap a fresh session.** A new agent reading only Tier 1 + the current user prompt should be able to make a correct decision about what to do next.

## Anthropic-pattern adoption

### "If you can't answer 'what's my role this session?' in 1 sentence: you've drifted"

From Claude Code docs on subagents: identity must be re-asserted at compaction boundaries. Ballast encodes this in `feedback_p10_post_compaction_identity_recovery.md` (F16 mitigation).

Concrete check: when you receive a message and the prior turn was > 30 turns ago, ask yourself the three questions in `feedback_p10_post_compaction_identity_recovery.md §"Self-check trigger"` before acting.

### Memory file is read on every session start (auto-load)

Anthropic Claude Code auto-loads `MEMORY.md` index every session. Use this:

- `MEMORY.md` = the table of contents (one-line per memory file with hook)
- Each memory file = self-contained chapter
- Read order matters — put the most critical file at line 1 (e.g. identity recovery)

Ballast example: Cobrust's `MEMORY.md` has 14 entries, identity-recovery first, snapshot second, runbook third. New session in Cobrust dir reads index, knows where to look.

### Skill description is the trigger

Anthropic skills auto-activate when description keywords match user prompt. So:

- `description` field = precise + keyword-rich + scoped (NOT generic)
- A skill named "agent dispatch" with description "general agent stuff" won't trigger usefully
- A skill named "agent dispatch" with description "multi-agent dispatch planning, P9 tech lead role, dev/test pair pattern" triggers on the right turns

Keep skill descriptions tight (~30 words), keyword-dense.

## OpenAI-pattern adoption

### Conversation summary turn (Anthropic also uses this)

When approaching context limit, take a deliberate "summary turn":

- List of decisions made this session
- Files modified this session
- Open questions
- Next action

This synthetic message becomes the bootstrap for compaction. Better than letting the system auto-compact a random middle chunk.

Mechanism: just write a paragraph or YAML block titled "## Session checkpoint <timestamp>" with the structure above.

### Cache 友好 (cost optimization)

OpenAI + Anthropic both cache prefix tokens. Strategy:

- Put unchanging context (system prompt, project preamble, tool definitions) FIRST
- Put changing context (recent messages, current task) LAST
- Don't shuffle the order; let cache hit

For Ballast: the auto-loaded memory + skill content sits at session start → cached. New user prompts append → small delta. This is already the right shape.

### Don't re-read files you've already read

OpenAI guidance: assume tool result outputs stay in context for the rest of the session. Don't `Read` the same file twice unless you wrote to it.

Ballast anti-pattern: re-reading SKILL.md or constitution every turn out of nervous-habit wastes context. Trust the agent's memory of recent reads.

## Ballast integration with existing patterns

### Snapshot.md as Tier 1 checkpoint

Ballast's `project_state_snapshot.md` is the canonical Tier 1 checkpoint. It contains:

- HEAD SHA
- ADR roster
- Finding ledger
- Phase F milestones
- Binary verification claim

A fresh session reads snapshot.md and bootstraps situational awareness in ~200 lines. Don't replicate this in transient context.

### Handoff cover-letter as Tier 1 cross-session

When ending a sprint, write a handoff cover-letter (template in `templates/handoff-cover-letter.md`) that becomes the bootstrap for the receiving session. Don't rely on transcript transfer.

### F16 mitigation: identity recovery preamble

Identity is Tier 1. The skill description triggers; the memory file confirms; the operative rules guide. If identity drifts post-compaction → re-read the identity recovery memory.

### Long-session bookkeeping rhythm

Every ~30 tool calls or hourly (whichever first), explicitly:

1. Update snapshot.md with latest HEAD + new ADRs/findings
2. Commit any in-progress work (don't let it rot in working tree)
3. Write a session-checkpoint paragraph (per OpenAI pattern above)
4. Run snapshot-lint to verify the Tier 1 invariants

This rhythm prevents the "20-tool-call-no-checkpoint" cliff where compaction loses critical state.

## Concrete templates

### Session-checkpoint format (insert as message in long sessions)

```yaml
## Session checkpoint <ISO timestamp>

decisions_this_session:
  - <decision 1, with ADR or finding link if applicable>
  - <decision 2>

files_modified:
  - <path>: <one-line change summary>

open_questions:
  - <q1>
  - <q2>

next_action:
  who: <agent role>
  what: <one-sentence action>
  blocking_on: <user拍板 | dependency | timing>
```

### Bootstrap-from-cold prompt (for fresh session resuming work)

When a fresh Claude Code session starts on an in-flight project:

```
First action (mandatory before any tool):
1. Read MEMORY.md (table of contents)
2. Read project_state_snapshot.md (HEAD + roster + ledger)
3. Read cto_operations_runbook.md (SOPs)
4. Read feedback_subagent_model_tier.md (D-matrix)
5. Then look at user's prompt + decide what to do
```

If MEMORY.md doesn't exist in the project, refuse to act until user clarifies role / project.

## Pitfalls

| Pitfall | Symptom | Recovery |
|---|---|---|
| Re-reading the same file 10× per session | Tool call waste, slow turns | Track read files in working memory; trust prior reads |
| Putting transient bash output in memory | Memory file grows unbounded | Memory is for stable facts; transient goes to scratch |
| Identity in skill description only (F16) | Post-compaction drift to executor mode | Mirror identity preamble in auto-memory; F16 mitigation |
| Tier 1 file never updated as project evolves | Snapshot becomes lying narrative | Pre-commit hook runs snapshot-lint |
| Cache-busting by shuffling system prompt order | Token cost inflates | Lock system prompt order; mutations go to user-turn |

## Cross-references

- `reference/cross-session-memory-architecture.md` — what goes in memory vs ADR vs finding vs snapshot
- `reference/failure-modes-catalogue.md` F16 — post-compaction identity drift (the negative form)
- `templates/snapshot-template.md` — Tier 1 bootstrap doc
- `templates/handoff-cover-letter.md` — cross-session handoff
- Anthropic Claude Code docs: subagents, MEMORY.md auto-load, plan mode
- OpenAI: cache optimization guidance + summary turn pattern
