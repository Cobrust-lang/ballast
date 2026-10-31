---
catalogue_id: F40
title: "Stream-watchdog false stall signal — long-running sub-agent triggers 600s timeout but ultimately completes all work post-hoc"
family: agent-infrastructure-trust (dispatch-state verification sub-form)
severity: P1 (dispatch economics — prevents costly duplicate work)
status: ratified_2026-05-19
empirical_project: Cobrust v0.3.0 Phase I wave-3 (ADR-0056c)
cobrust_local_id: P7-stream-watchdog-false-stall (from 0056c incident 2026-05-19)
date_ratified: 2026-05-19
second_corroborator: confirmed (two stall signals on two agents; both subsequently completed work)
---

# F40 — Stream-watchdog false stall signal

## Symptoms

A sub-agent dispatch (P9 or general-purpose) is running a long-duration sprint
(multi-crate impl + test corpus + DG verify, typically 30-90 minutes). The
orchestrator (P10) receives a "stream idle timeout" signal or "watchdog stall"
notification at approximately the 600-second mark.

P10 dispatches a second "continuation" agent to complete the reportedly stalled
work. Both the original agent and the continuation agent eventually signal
completion. On inspection:

- The original agent completed ALL work — multiple commits pushed to the branch.
- The continuation agent either duplicated work or ran on a stale baseline.
- The stall signal was **false**: the agent was alive and working throughout
  the watchdog timeout window; it just wasn't streaming output at the
  orchestrator's observation layer.

## Root cause

Long-running sub-agent phases (e.g. `cargo test --workspace` with hundreds of
tests, DG remote compilation, LLVM/Cranelift codegen linking) do not emit
visible output for extended periods. The orchestrator's stream-idle watchdog
interprets silence as stall. The agent is not stalled — it is in a CPU-bound
or IO-bound phase with no intermediate stdout to emit.

Two contributing factors:

1. **Watchdog fires on stdout silence**, not on process liveness. A 10-minute
   `cargo test` run with no output is indistinguishable from a hung process at
   the stream layer.
2. **Orchestrator response to stall is dispatch-based** (send another agent)
   rather than verify-based (check branch state before acting). The dispatch-based
   response transforms a false positive into an expensive double-dispatch.

## SOP fix — verify-before-act protocol

**When a watchdog stall signal fires on a sub-agent dispatch**:

1. **STOP. Do NOT immediately dispatch a continuation agent.**
2. **Check branch state** (3 commands, 30 seconds):
   ```bash
   # Check if the agent pushed any commits
   git log --oneline origin/<branch-name> | head -5
   # Check if DG run logs show completion
   ls -lt /tmp/cobrust-*/  # or equivalent DG output directory
   # Check if the workspace compiles
   cargo check --workspace 2>&1 | tail -5
   ```
3. **Interpret the evidence**:
   - Branch has new commits → agent completed work, stall was false positive.
     Review the commits; decide if more work is needed.
   - Branch has no commits but workspace compiles → agent may have been mid-impl;
     check DG run status before deciding.
   - Branch has no commits and workspace errors → agent likely stalled before
     completing; dispatch continuation.
4. **Only after Step 3**: dispatch continuation if evidence shows genuine stall.

## Evidence

Cobrust ADR-0056c Phase I wave-3 (fn-redef), 2026-05-19:

- **Agent `a2b6ebf2995b88d08`** dispatched for Phase I wave-3 fn-redef impl.
  Stream-watchdog stall signal at ~600s.
- **Agent `aab5aaafa919c0ff3`** dispatched as continuation. Also reported stall.
- **Post-hoc inspection**: original agent `a2b6ebf2995b88d08` eventually pushed
  **6 commits** to `feature/0056c-fn-redef`:
  - `8e28b7f` feat(types): TypeCheckCtx::invalidate_def per-symbol API
  - `1f0f4b3` feat(session): Session::redefine_fn atomic re-bind + REPL UX
  - `9bdf48f` tests(session): fn-redef contract (8 tests, 0056c)
  - `fd4de42` tests(0056c): DG verify fn-redef 8/8 PASS, 0 regression
  - `3626021` docs: Phase I wave-3 fn-redef dual-track (zh + en + agent)
  - `2ae8c52` docs(adr): 0056c ratify accepted
- All 6 commits were post-stall-signal. The agent completed full work including
  DG verify after the watchdog fired.
- The continuation agent `aab5aaafa919c0ff3` ran on a stale baseline — its
  work was redundant and was discarded.

## Cost of false positive without this SOP

- **Wasted continuation dispatch**: ~30-60 min of agent time on redundant work.
- **Merge confusion**: two branches with overlapping work require manual
  resolution.
- **Context burn**: P10 spends context budget managing a "stall recovery" that
  wasn't needed.

## Complementary tool: check-before-act on all signal types

The verify-before-act protocol generalizes: for ANY "something may have gone
wrong" signal (stall, timeout, error message, unexpected silence), check the
artifact state (branch commits, build output, test results) before re-dispatching.

Most "failures" in long-running agent infrastructure are latency mismatches
between agent execution time and orchestrator observation cadence, not genuine
stalls.

## Cross-references

- F36 (agent self-disciplinary rule skip) — F40 is the infrastructure-level
  analogue: the agent (orchestrator) skips the verify step because dispatching
  "feels right" when a stall signal appears.
- `feedback_p9_two_phase_dispatch.md` (Cobrust CTO runbook) — two-phase
  dispatch SOP for genuine stalls (spike-commit + respawn); F40 is the
  pre-condition check that determines whether two-phase dispatch is needed.
- Cobrust commits: `8e28b7f`, `1f0f4b3`, `9bdf48f`, `fd4de42`, `3626021`,
  `2ae8c52` (all pushed post-stall by agent `a2b6ebf2995b88d08`)
- Cobrust merge: `663cd56` (Phase I wave-3 fn-redef full close)

## Status

Ratified 2026-05-19. Verify-before-act protocol added to Cobrust CTO runbook
§"Watchdog stall response." Two independent stall signals on two agents, both
eventually completing work, satisfies second-corroborator requirement.
