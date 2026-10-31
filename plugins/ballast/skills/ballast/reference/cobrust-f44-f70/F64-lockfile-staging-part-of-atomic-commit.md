---
catalogue_id: F64
title: "A dependency edit silently regenerates the lockfile but the agent stages only the manifest — CI's locked-install rejects the drift, fail-cascading every build job"
family: incomplete-atomic-commit (dependency-footprint sub-form) + pre-flight-check-the-dispatcher-forgot
severity: P2 (whole CI red; cheap to diagnose, trivial to fix, easy to repeat)
status: ratified_2026-05-28
empirical_project: Cobrust #151 RAII-tempdir refactor (2026-05-28)
cobrust_local_id: F64 (f64-dev-dep-cargo-lock-staging-miss.md)
date_ratified: 2026-05-28
cobrust_sha: 1b05ae3 (the miss), 73aa3bb (one-line remediation)
related: [F44, F49, F63]
---

# F64 — Lockfile staging is part of the atomic commit

## Pattern

An agent adds (or bumps) a dependency in the manifest. The local build tool
**silently regenerates the lockfile** to match. The agent stages and commits the
manifest plus the substantive source changes — but **not** the auto-regenerated
lockfile line. CI runs its installs with a **locked / frozen** flag (reproducible
builds), which *refuses* to auto-regenerate and **aborts before compiling**. The
result is a **fail-cascade**: every build / lint / test job fails within seconds
with the *same* lockfile-mismatch error, looking like a catastrophic regression —
but it is one root cause wearing N hats.

The "all tests pass locally" signal is genuine and useless: the dev box runs
*unlocked* (auto-regenerating the lockfile in place), while CI runs *locked*. The
two run **different commands**, so local green does not imply CI green.

## Root cause

The commit's **file set was incomplete relative to the change's dependency
footprint**. Adding a dependency is a *two-file* mutation (manifest + lockfile),
but the agent treated it as one. The lockfile change is invisible unless the
agent runs an explicit `status`/`diff` on it after building — and "inspect the
post-build tree" is not the same as "diff the lockfile."

The deeper class: agents reliably do the substantive work and reliably skip the
**boring pre-commit verification step** that catches the boring failure class.
The fix is never "be more careful" — it is "make the verification a
non-skippable line in the dispatch template."

## Why this matters for Ballast

This is the canonical **pre-flight-check-the-dispatcher-forgot-to-demand** pattern
(sibling to identity-check pre-flights, F49). It is cheap (diagnose in minutes,
fix in one line) but **highly repeatable** — every dependency-touching sprint can
re-trigger it — so the value is entirely in *prevention via template*, not in the
individual fix. And the fail-cascade is a diagnostic trap: 6 red jobs scream
"huge regression," when the real signal is the one help-line at the tail of any
build log: *"to generate the lock file without --locked, use --offline instead."*
An agent that reads only "6 failures" wastes budget; one that reads the *tail*
sees a one-line fix.

## Empirical evidence (Cobrust 2026-05-28)

Commit `1b05ae3` added a dev-dependency to one crate's manifest. The local build
auto-regenerated the lockfile to add the matching entry — never `git add`-ed. CI
on the next commit failed across **all 6 substantive jobs** (build/clippy/test ×
2 platforms) within seconds; the non-build jobs (fmt, doc-coverage, udeps, audit)
passed. The ubuntu build log tail:

```
help: to generate the lock file without accessing the network,
      remove the --locked flag and use --offline instead.
##[error]Process completed with exit code 101.
```

Local vs CI invocation diverged exactly as expected:

| layer  | local (no `--locked`)            | CI (`--locked`)                          |
|--------|----------------------------------|------------------------------------------|
| build  | `cargo build --workspace`        | `cargo build --workspace --locked`       |
| clippy | `cargo clippy ...`               | `cargo clippy ... --locked`              |
| test   | `cargo test -p <crate> ...`      | `cargo test --workspace --locked`        |

**Remediation:** a **one-line** addition of the missing lockfile entry (`73aa3bb`)
— no source change, no version churn. **SHAs:** `1b05ae3` (the miss), `73aa3bb`
(fix).

## Detection rule (dispatch-template line — non-negotiable)

> Any agent dispatch that *might* touch dependencies (any manifest's dependency
> sections) MUST include a pre-commit check: after building, run a
> `status`/`diff` on the lockfile; if it shows unstaged changes, `add` it before
> committing. CI runs locked installs and will reject ANY lockfile drift,
> including the silent ones the build tool auto-applies locally.

## General Ballast mitigation

1. **The atomic commit includes the lockfile.** A dependency edit is manifest +
   lockfile, always staged together — same discipline as "commit + tests + docs."
2. **Align dev and CI commands, or expect surprises.** The dev box and CI run
   different flags; the lockfile is the most common place that bites.
3. **Read the log tail, not the failure count.** A fail-cascade of identical
   errors is one root cause; the fix is usually in the last help-line.
4. **Encode the check, don't exhort.** "Be careful with the lockfile" fails; a
   literal `status -- <lockfile>` line in the template succeeds.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F49 (Cobrust) — pre-flight identity check | Same family: a one-command pre-flight the dispatcher must demand explicitly, not hope the agent runs |
| F44 (Cobrust) — CI cache stale-green | Inverse polarity: F44 = warm CI cache hid a real regression; F64 = cold locked CI caught a real drift local warm-cache hid. Shared moral: dev box ≠ CI |
| F63 (this batch) | Direct prequel: F64 occurred *inside* the RAII-refactor sprint that resolves F63 |
| F1 — Declared rules without enforcement | Parent family: "stage the lockfile" implicit; the fix is a template gate |
