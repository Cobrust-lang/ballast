---
name: Cross-session memory architecture
description: Ballast's distinction between auto-memory, project artifacts, scratch context, and ephemeral state. Codifies what survives session boundaries and how to design new memory entries that don't decay.
type: reference
version: 1.0.0
date: 2026-05-12
status: active
relates_to: [skill:SKILL.md §"Snapshot discipline", reference:context-window-strategy.md, reference:failure-modes-catalogue.md F1 family + F16 + F17]
---

# Cross-session memory architecture

> Ballast's hard-won memory discipline: not everything that lasts deserves to last; not everything ephemeral should be ephemeral. Four storage layers, each with a different persistence contract.

## When this applies

- You're about to write something down and don't know where it goes
- You're designing a new memory file or template
- You're auditing why a piece of project knowledge keeps getting re-derived

If you're producing one commit and done, just commit it. This reference is for projects with state.

## Four storage layers

```
┌──────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: Auto-memory (~/.claude/projects/<proj>/memory/)                  │
│  Survives: all sessions, all hosts (if synced)                            │
│  Auto-loaded at session start via MEMORY.md index                         │
│  Contains: identity preamble, operative rules, cross-session SOPs         │
│  Mutation policy: edit in-place; index entries are one-line hooks         │
├──────────────────────────────────────────────────────────────────────────┤
│ LAYER 2: Project artifacts (repo's docs/ + ADR + findings + snapshot)     │
│  Survives: as long as the repo does                                       │
│  Contains: decisions (ADR), negative results (finding), state (snapshot)  │
│  Mutation policy: ADR immutable once accepted; finding append-only;       │
│                   snapshot updated atomically with HEAD                   │
├──────────────────────────────────────────────────────────────────────────┤
│ LAYER 3: Session scratch (this conversation's working notes)              │
│  Survives: within session only                                            │
│  Contains: in-progress reasoning, intermediate computations, working set  │
│  Mutation policy: free-form; nothing committed unless promoted to L1/L2   │
├──────────────────────────────────────────────────────────────────────────┤
│ LAYER 4: Ephemeral (single tool call output)                              │
│  Survives: only as long as tool result is in context window               │
│  Contains: bash stdout, file read contents, grep results                  │
│  Mutation policy: re-fetch if needed; don't memorialize                   │
└──────────────────────────────────────────────────────────────────────────┘
```

## Decision tree: where does this go?

```
Is it identity, role, or operative rule? ─yes─→ Layer 1 (auto-memory)
                                                  - new file under memory/
                                                  - one-line hook in MEMORY.md
                                                  - frontmatter: type=feedback
  │
  no
  ▼
Is it a binding decision affecting ≥2 files? ─yes─→ Layer 2 (ADR)
                                                     docs/agent/adr/NNNN-*.md
  │
  no
  ▼
Is it a negative result / surprise / failure? ─yes─→ Layer 2 (finding)
                                                      docs/agent/findings/*.md
  │
  no
  ▼
Is it a state fact (HEAD, version, count)? ─yes─→ Layer 2 (snapshot.md)
                                                   project_state_snapshot.md
  │
  no
  ▼
Is it in-progress reasoning this sprint? ─yes─→ Layer 3 (session scratch — comment, message)
  │
  no
  ▼
Is it a one-time output that can be re-fetched? ─yes─→ Layer 4 (ephemeral)
                                                        no memorialization needed
```

When in doubt, **default to Layer 3 scratch**. Promotion to L1/L2 happens deliberately at sprint end, not in the moment.

## Layer 1 (auto-memory) deep dive

### File naming convention

- `feedback_<topic>.md` — operative rules / SOPs / user-mandated guidance (e.g. `feedback_subagent_model_tier.md`, `feedback_p10_post_compaction_identity_recovery.md`)
- `reference_<topic>.md` — pointers to external systems (e.g. `reference_proxy_config.md`)
- `project_state_snapshot.md` — current canonical state (single file, mutated atomically)
- `MEMORY.md` — index (one-line hooks pointing to files above)

### Frontmatter contract

```yaml
---
name: <human-readable title>
description: <one-line trigger for the agent reading the index>
type: feedback | reference | snapshot
originSessionId: <session UUID, optional>
last_verified_date: <ISO date, optional but recommended>
related_memory: [<other_file>.md, ...]
---
```

### MEMORY.md index format

```
- [<file's human title>](file.md) — <one-line hook describing when to read this>
```

Top entries are read-first. Place identity-recovery / role-clarifying files at the top.

### Mutation discipline

Auto-memory mutates in-place (no git history). Therefore:

- Date your edits — `## Extension 2026-05-12: ...` rather than overwriting silently
- Don't delete past sections; mark them `## Deprecated 2026-05-12: was X, now Y because Z`
- One-line description in MEMORY.md must stay accurate; update it when content shifts

### When to add a new memory file vs extend an existing one

Add new file when:
- New topic area not covered by existing file
- File would grow > 200 lines
- The rule applies to a different agent role than existing file's audience

Extend existing file when:
- New sub-rule of an existing rule
- Refinement / amendment to existing operative practice
- The "## Extension <date>:" pattern keeps mutations auditable

## Layer 2 (project artifacts) deep dive

### ADR vs Finding distinction

ADRs are **forward-looking decisions** ("we will do X going forward"). Findings are **backward-looking observations** ("we hit Y; here's what we learned"). They're not interchangeable.

A failure observation (finding) → drives a future decision (ADR). The finding doesn't bind anyone; the ADR does. Don't put binding rules in findings; don't put incident history in ADRs.

### Snapshot.md responsibility

Single source of truth for current project state:

- Current HEAD SHA (auto-updated post-merge)
- ADR roster table (each accepted ADR listed)
- Finding ledger (each finding with status: open / closed)
- Phase / milestone progress
- Binary verification claim (e.g. "cobrust build hello.cb passes at HEAD")

Snapshot has its own enforcement: `scripts/snapshot-lint.sh` validates the invariants are met. Without snapshot-lint, snapshot drifts (F1.1 — declared invariant without enforcement).

## Layer 3 vs Layer 4 boundary

Most agent failures come from **misplacing Layer 3 facts into Layer 4 (forgetting useful state) or Layer 4 facts into Layer 3 (cluttering working memory)**. Examples:

- ❌ Re-reading the same source file 5 times (Layer 4 treated as Layer 3 — already had it, should re-use)
- ❌ Writing intermediate bash output to a memory file (Layer 4 promoted to Layer 1 — bloat)
- ✅ Keeping a running list of "files I've read this turn" in scratch (Layer 3 working set)
- ✅ Discarding `grep -c` count after using it (Layer 4 ephemeral)

## Anthropic-pattern adoption

### MEMORY.md auto-load contract

Anthropic Claude Code auto-loads MEMORY.md at session start. Ballast uses this:

- Memory files are the agent's "world model" at boot time
- Index hooks must be precise — the agent decides which to read based on hooks
- A line-1 entry like `[Identity recovery SOP] — read if post-compaction or fresh session` ensures the right file gets opened

### Anti-pattern: stale memory

Anthropic warns: memory is point-in-time. Don't trust years-old memory entries blindly. Ballast codifies this:

- Frontmatter `last_verified_date` field
- Pre-action verification when memory makes a claim about file paths or current state
- Stale memory entries get marked deprecated, not silently re-relied-upon

## OpenAI-pattern adoption

### Vector store + retrieval (NOT YET in Ballast)

OpenAI's Assistants API does retrieval over uploaded files. Ballast currently relies on the agent's context window + memory; retrieval not adopted.

For Ballast v1.3.0+: consider retrieval if memory + repo content together exceed context budget. Until then, the four-tier model is sufficient.

### Threads (session scoping)

OpenAI threads are persistent multi-session conversations. Ballast's analog: per-project memory folder. Same idea — bound the persistence to the project, not the global model.

## Ballast integration with existing patterns

### Snapshot-lint enforcement loop

Layer 2 snapshot.md has invariants (HEAD freshness, ADR roster completeness). `scripts/snapshot-lint.sh` runs these as Inv 1-4. Pre-commit hook fires snapshot-lint, blocking commits that violate invariants. This is the F1.1 closure mechanism.

### CTO operations runbook is the Layer 1 cookbook

`cto_operations_runbook.md` codifies P9 dispatch SOPs, conflict resolution, gates. It's auto-memory because it must survive session boundaries — every new session running CTO role reads it on bootstrap.

### Identity recovery memory closes F16

`feedback_p10_post_compaction_identity_recovery.md` lives in Layer 1 specifically because identity must survive compaction. The corresponding F-pattern is the negative form of why this memory exists.

## Pitfalls

| Pitfall | Layer confusion | Recovery |
|---|---|---|
| Memory file holds in-progress sprint notes | L3 → L1 leak | Move to a scratch message, promote permanent rule to L1 if it's actually a rule |
| ADR captures incident history | L2-finding → L2-ADR confusion | Rewrite as finding; if a decision was made, separate ADR linking the finding |
| Snapshot.md not updated post-merge | L2 staleness | snapshot-lint pre-commit hook (F1.1 mitigation) |
| "I'll remember to do X" (Layer 3) becomes binding | L3 informal → expected L1 | Either codify in memory or accept it'll be forgotten |
| Re-reading same memory file every turn | L4-style use of L1 | Trust L1 was loaded at session start; don't re-fetch |
| MEMORY.md hook is generic ("various rules") | Index loses dispatch value | Rewrite as specific keyword-dense one-liner |

## Cross-references

- `reference/context-window-strategy.md` — what to put in context (different question than where to put facts)
- `reference/failure-modes-catalogue.md` F1 family + F16 + F17 — anti-patterns this architecture mitigates
- `templates/snapshot-template.md` — Layer 2 snapshot template
- `SKILL.md` §"Snapshot discipline" — the operative discipline this architecture supports
- Anthropic Claude Code memory docs — MEMORY.md auto-load contract
- OpenAI Assistants API — threads + retrieval (for Ballast future consideration)
