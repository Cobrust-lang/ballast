---
doc_kind: finding
finding_id: F72
title: "A killed-runner CI flake (OOM / timeout / infra) looks like a code failure but isn't — its RELIABLE signature is an EMPTY failure log (no error line, no exit-code line); the step conclusion can be blank OR 'failure'"
family: F4-Cross-Target (non-deterministic-CI sub-form)
severity: P2 (one red job on a green commit; cheap to diagnose once the signature is known, easy to misdiagnose as a code bug)
status: candidate
empirical_project: Cobrust ADR-0080/ADR-0081 FastAPI-real impl run (2026-05-30)
cobrust_local_id: F72 (f72-killed-runner-ci-flake-blank-step-empty-log.md)
cobrust_sha: a1c9d83
related: [F44, F59, F62, F64]
---

# F72 — Killed-runner CI flake: blank step + empty log ≠ code bug

## Pattern

One CI job goes red on a commit whose siblings are green, but the failure has **no
diagnosable content**: the failing job's **step conclusion is BLANK** (neither
`success` nor `failure`) and `gh run view --log-failed` returns **empty**. A killed
runner — OOM-killed, hard-timed-out, or otherwise reaped by the infrastructure —
**never flushes its step logs**, so the platform records the job as failed but has no
step result or log to show. The red badge looks like a regression; there is nothing in
the log because no command actually reported an error — the process was killed
out from under the runner.

This is an **environmental / infra failure**, not a code defect, and the absence of
log content is itself the tell.

## Why this is distinct from F64 (and how to tell them apart at a glance)

F64 (lockfile `--locked` mismatch) is the *other* "a build job goes red" finding in
this batch, and the two are diagnosed by opposite signatures:

| | **F72 — killed runner** | **F64 — lockfile `--locked` mismatch** |
|---|---|---|
| step conclusion | **BLANK _or_ `failure`** — UNRELIABLE: a killed runner manifests as either, so do NOT key on it | **`failure`** (the command ran and exited non-zero) |
| `--log-failed` | **EMPTY** (runner died before flushing) | **LOGGED** error + a help-line at the log tail |
| root cause | runner OOM / timeout / infra reap | a real, reproducible drift in the committed tree |
| reproduces locally? | **no** (local re-run + CI re-run pass) | **yes** (the locked command fails identically locally) |
| fix | re-run the job; if it recurs, reduce the step's resource pressure | one real edit (stage the lockfile) |

The single most discriminating question: **does the failing step have a logged
error?** A logged error → a real failure to read (F64-class). A blank step + empty log
→ a killed runner (F72-class). Reading "1 job failed" without reading *whether the step
produced a log* is how a killed-runner flake gets misdiagnosed as a code bug and burns
a debugging budget.

## Root cause

CI runners are finite-memory, finite-time sandboxes. A memory-heavy or long-running
step (a full `--all-targets` build that compiles every test/bench/bin target at once is
the canonical offender — its peak RSS is far above a plain library build) can transiently
exceed the runner's ceiling and be killed by the platform. Because the kill is external
to the build process, no command emits an error and no step result is written — the job
is simply marked failed with empty internals. The failure is a function of **runner
weather** (concurrent load, memory headroom on that particular VM), not of the commit,
so it is **non-deterministic**: the same commit re-run on a fresh runner passes.

## Why this matters for Ballast

A green/red CI signal is the agent's strongest correction loop (the F44 thesis). A
killed-runner flake injects a **red that carries no information** — and an agent that
treats every red as a code defect will hunt a bug that does not exist, or worse,
"fix" working code to chase a phantom. The discipline is a two-command diagnosis that
*separates infra noise from code failure* before any code is touched, so the gate stays
trustworthy (the same trust-in-the-gate concern as F44 stale-green and F59
external-service flakes — this is its OOM/timeout sibling).

## Empirical evidence (Cobrust 2026-05-30) — TWO occurrences, TWO step-conclusion forms

The SAME flake — a transient OOM on the memory-heavy `cargo build --workspace
--all-targets --locked (ubuntu-latest)` step — recurred twice on green commits, and the
**step conclusion differed between them**, which is exactly why the step conclusion is
NOT the reliable tell:

- `a1c9d83`: failing step **BLANK conclusion** + empty `--log-failed`.
- `541f348`: failing step **`failure` conclusion** + a log carrying only the `##[group]`
  header — NO `error:`/`error[` line and NO `Process completed with exit code N` line.

Both times, on the same commit, `cargo test (ubuntu)` + `cargo build (macOS)` **passed**.
Diagnosis each time: **reproduce the exact command locally** (`cargo build --workspace
--all-targets --locked` → **exit 0**; `--locked` also rules out an F64 lockfile drift) +
**`gh run rerun <id> --failed`** → **all green**. Both passing = environmental.

**The reliable discriminator is the LOG CONTENT, not the step conclusion:** a real
cargo/rustc error ALWAYS logs an `error:` / `error[` / `could not compile` line AND a
`Process completed with exit code N` line; a killed runner logs neither (at most the step
header). Grep the failed log for those — their absence ⇒ killed runner, whatever the step
conclusion says. (The original "blank step conclusion" signature was one manifestation;
the `541f348` recurrence proved a `failure` conclusion is equally possible.)

## Resolution (recurring fix, Cobrust `3aa32ae`)

Re-running works, but a *recurring* memory-heavy flake earns a structural fix (Delta 6).
The fix here was to **cap build parallelism**: `cargo build --workspace --all-targets
--locked --jobs 2` in ci.yml. The LLVM-statically-linked test binaries spike peak RSS when
many link concurrently; `--jobs 2` bounds concurrency WITHOUT changing the `--all-targets`
target set (the full check is preserved). Escalate to `-j 1` if it ever recurs.

## Detection rule

> When one CI job is red on an otherwise-green commit, **inspect the failing step's LOG,
> not its conclusion**. If `gh run view --log-failed` has NO error line (`error:` /
> `error[` / `could not compile`) and NO `Process completed with exit code N` line —
> regardless of whether the step conclusion is blank or `failure` — treat it as a
> **killed-runner flake (OOM / timeout / infra)**, NOT a code bug. Confirm with two commands: (1) reproduce the
> exact failing command locally — for a build step, `cargo build --workspace
> --all-targets --locked` (the `--locked` also rules out an F64 lockfile bug); (2)
> `gh run rerun <id> --failed`. Both green ⇒ environmental; do not touch code. A
> *logged* error with a `failure` conclusion is the opposite case (read the log tail —
> F64-class).

If a memory-heavy step (a full `--all-targets` build) flakes repeatedly, reduce its
peak pressure (split targets across jobs, add a disk/memory-reclaim step per Delta 6,
or build library and test targets in separate steps) rather than re-running forever.

## General Ballast mitigation

1. **Read the step result, not the job count.** "1 job failed" is not a diagnosis;
   "the failing step has a blank conclusion and empty log" is.
2. **Two-command triage before touching code.** Exact-command local repro (with
   `--locked`) + `--failed` rerun cleanly separates infra noise from a code failure.
3. **A blank-step/empty-log red is information-free by construction** — a killed runner
   cannot tell you what went wrong because nothing went wrong in the build. Don't
   manufacture a bug to explain it.
4. **Recurring memory-heavy flakes get a structural fix** (split the step / reclaim
   resources), not a standing "just re-run it" habit that erodes trust in the gate.

## Cross-references

- Cobrust finding `f72-killed-runner-ci-flake-blank-step-empty-log.md`; surfaced
  during the ADR-0080/ADR-0081 FastAPI-real impl run, 2026-05-30. Evidence commit
  `a1c9d83` (blank `cargo build (ubuntu-latest)`; `--all-targets --locked` local exit
  0 + `--failed` rerun all green).
- **F64** — the contrasting build-job red: a lockfile `--locked` mismatch gives the
  step a `failure` conclusion + a logged help-line, reproduces locally, and is a real
  one-line fix. The signature table above is the at-a-glance discriminator.
- **F44** — CI-as-oracle trust: F44 is a green that lies (stale cache hides a real
  defect); F72 is a red that lies (a killed runner reports failure with no defect).
  Both erode the gate if read naively.
- **F59 / F62** — the non-deterministic-CI siblings: external-service health (F59) and
  cold-build-only fragilities (F62) likewise produce gate results uncorrelated with the
  commit; F72 is the OOM/timeout member of that family.
- Methodology **Delta 6** (deterministic-CI / CI-infra-hardening playbook) — the
  structural fix for a recurring memory-heavy flake (disk/memory reclaim, step split)
  lives there.
