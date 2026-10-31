---
catalogue_id: F44
title: "CI cache stale-green — a cache hit skips lint/build recomputation, so a green checkmark stops meaning 'workspace clean'"
family: F37-SilentRot (declared-coverage ≠ actual-coverage sub-form)
severity: P1 (false-pass — broken state ships under a green badge)
status: ratified_2026-05-27
empirical_project: Cobrust Phase J wave-2 (2026-05-21 → 2026-05-27)
cobrust_local_id: F44 (f44-ci-cache-stale-green-false-pass.md)
cobrust_sha: 41fbef3 (pyo3 blocker cleared) ; lurk window a3a636c → e38dfe4
resolution: clean-target sweep at every phase-close + cargo-udeps gate + consistent --all-targets --no-deps
related: [F45, F45a, F46, F51, F53, F37-SilentRot, F35-ClaimDrift]
---

# F44 — CI cache stale-green / false-pass

## Pattern

A green CI run **does not** prove the workspace is clean. Build caches key on
coarse inputs (commit SHA + lockfile hash). When a push hits a pre-existing
cache entry, the cached fingerprint data is reused and the expensive
recomputation (clippy, full rebuild) is **skipped** — even when source files
changed. The result: real lint/build errors lurk across many commits while
every CI run reports PASS.

This is the canonical "**declared-coverage ≠ actual-coverage**" failure: the
green badge *declares* the gate ran; the cache hit means the gate *didn't*.

## Root cause

Three independent contributing dynamics, any one sufficient:

- **(a) Cache key too coarse.** The cache invalidates on `Cargo.lock` (or
  equivalent lockfile) hash, not on a source-tree / lint-tree hash. A push that
  doesn't touch the lockfile reuses a stale fingerprint and skips the lint step.
- **(b) Interrupted run orphans a failure.** A hung or cancelled CI job can leave
  a run marked in-progress; a subsequent push starts a fresh matrix that masks
  the original failure by orphaning it.
- **(c) Gate scope drift.** Ad-hoc invocations omit a scope flag (`--all-targets`)
  so the library target compiles clean while `bin/` and integration-test targets
  silently accumulate warnings.

## Why this is critical for Ballast / agent-driven projects

The agent's strongest correction signal is the gate result. If a green gate is a
lie, the agent builds confidently on a broken base, and the lie compounds: each
subsequent sprint trusts the cached green and adds more on top. By the time the
truth surfaces (a forced clean rebuild), the debt spans dozens of commits and
the bisect is expensive. A cache is an optimization; **a cache that hides a
failing gate is a correctness bug**, not a performance tradeoff.

## Empirical evidence (Cobrust 2026-05-21 → 27)

- **19 `cobrust-lsp` clippy errors** lurked from `a3a636c` (a hover+completion
  sprint) through ~30 commits to `e38dfe4` (a release candidate stage). Every CI
  run in that window reported **PASS** while local
  `cargo clippy --workspace --all-targets -- -D warnings` returned 19 errors.
- A 132-minute test-job hang (an unrelated fixture incident) plausibly orphaned a
  run and masked the original failure (root cause **(b)**).
- Promotion of the security/unused-dep gates from `continue-on-error` to blocking
  was itself **blocked** by a separately-lurking advisory (a transitive
  dependency CVE) — the act of trying to make the gate honest surfaced more
  hidden debt. The dependency upgrade landed at `41fbef3`, clearing the blocker.

## Detection rule (CI gate)

Run a **cache-busted, full-scope** lint/build at every phase close (or nightly):

```bash
# Bust the cache (rotating stamp or CACHE_BUST secret appended to the cache key),
# then run from a clean target dir:
rm -rf <build-target-dir>
cargo clippy --workspace --all-targets --no-deps -- -D warnings
```

Make `--all-targets --no-deps` (or the equivalent full-scope flags) **invariant**
across every CI invocation — never ad-hoc. Add a companion unused-dependency gate
(`cargo-udeps` or equivalent), since unused deps rot silently by the same
mechanism.

## Resolution path

1. **Enforce full scope consistently**: pin `--all-targets --no-deps` in the
   clippy/build job definition; remove any reduced-scope ad-hoc invocations.
2. **Add a cache-busted clean sweep** at every milestone/phase close, run from a
   freshly-deleted target dir, gating the milestone SHA on zero errors.
3. **Add companion silent-rot gates** (unused deps, dependency advisories) — but
   per F37 discipline, do **not** flip a gate to blocking while it has known
   open violations; that just re-buries the debt. Clear the violation first
   (Cobrust queued a dependency-upgrade sprint), then promote.
4. **Never trust a green for a destructive/irreversible step** (tag, release,
   default-flip) without a clean-room rebuild behind it.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F37 — Silent-rot-on-accepted-debt (Cobrust) | Parent: errors accumulate invisibly; F44 is the infra-caused variant where the *gate itself* hides them |
| F35 — Commit-msg vs diff drift (Cobrust) | Adjacent: claim (CI PASS) diverges from actual landed state |
| F45 / F45a — Stub silently shipped | Same family at the test-assertion layer: object-emit green ≠ runtime-works green |
| F51 — Clippy feature-flag silent-rot | Direct sibling: "CI scope incomplete ≠ all-clean" (feature-gated code never linted) |
| F53 — Default-flip aggregate gap | Sibling: a curated sweep returned GREEN by *excluding* the paths that were broken |
