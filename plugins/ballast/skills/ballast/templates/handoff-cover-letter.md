<!-- Template for a handoff cover letter.
     Used when one agent (often external review) hands a multi-task
     plan to a CTO or sub-agent. The letter is the "north star" they
     read first. -->

---
to: <recipient role, e.g. "CTO of <project> next session">
from: <sender, e.g. "review-claude (third-party audit window)">
date: YYYY-MM-DD
subject: <plan name, e.g. "0.1.0-beta release — 2-day plan">
trigger: <verbatim quote of what triggered this handoff, often a user
         message>
---

# <plan name>

## Cover note

<2-3 sentences: who you are, why you wrote this, what the recipient
should expect from this handoff>

Full handoff pack at:
<absolute path to handoff folder>

**You (recipient) only do:**
- <high-level responsibility 1, e.g. strategic decisions>
- <responsibility 2, e.g.守闸 + merge>

**All writing (drafts, prompts, ADRs) is already done.** You sign off,
adjust if needed, and execute.

---

## Wedge / Strategic anchor

> <one-paragraph statement of WHY this plan exists and what it locks
> in strategically. If recipient disagrees with this anchor, the rest
> of the plan needs revisiting before execution.>

## Timeline

### Day / Phase 1

| Hour | Action | Who |
|---|---|---|
| 0-1 | <action> | <recipient solo / sub-agent> |

### Day / Phase 2

| Hour | Action | Who |
|---|---|---|
| ... | ... | ... |

## Handoff pack contents (use order)

### Read first
1. **`COVER_LETTER.md`** ← this file
2. **`<core deliverable doc>.md`** ← read after cover

### Day 1 morning
3. **`<paste-ready file 1>.md`** — paste to <repo location>
4. ...

### Day 1 afternoon (sub-agent dispatch)
5. **`dispatches/<task-1>-<role>.md`** — Agent tool spawn, model=<X>, run_in_background=<bool>
6. ...

### Day 2 (recipient solo finalization)
7. **`<final asset>.md`** — <action>

## Recipient's irreducible decisions (you can't delegate)

1. **<decision 1>**: <options + recommendation>
2. **<decision 2>**: <options + recommendation>
3. **<decision 3>**: <options + recommendation>

If you change any of these from the recommended default, **ping me in
chat** before executing — downstream tasks may need adjustment.

## Risk points (sender flagged)

### Risk 1: <risk name>

<description>

**Mitigation**: <what's already in place to handle this>

### Risk 2: ...

## Sender commitment (standby model)

I'm available in chat session for:
- <commitment 1, e.g. re-drafting any text recipient doesn't like>
- <commitment 2, e.g. reviewing P9-COMPLETION reports>

I do **not**:
- <boundary 1, e.g. write to main repo directly>
- <boundary 2>

## Closing

<1-2 sentence rationale for why this plan is achievable, what's the
final success criterion, and "go" message>

— <sender signature + role + date>
