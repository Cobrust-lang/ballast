---
catalogue_id: F59
title: "A test depending on a live external service gates CI — a third party's health, not the code's correctness, decides green/red"
family: non-deterministic CI (external-dependency sub-form)
severity: P2 (flaky CI; erodes trust in the signal)
status: ratified_2026-05-27
empirical_project: Cobrust Z.5 (std.json) CI run (2026-05-27)
cobrust_local_id: F59 (f59-external-httpbin-test-gates-ci.md)
date_ratified: 2026-05-27
cobrust_sha: 8b810e7
related: [F61, F63, F37, F44]
---

# F59 — External-service dependency gates CI

## Pattern

A test in the always-run suite makes a **live request to a third-party network
service** and hard-asserts on the response. CI green then means "the code is
correct *and* a remote host happened to be healthy at test time." When the
service is down, rate-limited, or degraded, CI goes red for reasons unrelated to
the change under test — and worse, a *passing* run gives false confidence that
masks real regressions behind an unrelated network flake.

A subtle sub-trap: an "offline-safe" guard that only checks **reachability** is
insufficient. Services are frequently *reachable but degraded* (up, but returning
503 / rate-limited / malformed bodies). A probe that returns early only on a
connection error still lets a 200-expecting assertion fire against a 503.

## Root cause

The deterministic-CI contract — **green must mean "workspace correct," never "a
third party was healthy"** — was violated by placing a network-dependent assertion
in the gating suite. The offline-skip logic, where it existed, modeled only the
binary up/down case, not the up-but-unhealthy case that real services exhibit
under load.

## Why this matters for Ballast

CI is the agent's ground-truth oracle: a sub-agent reads "CI red" as "my change
broke something" and a synthesis agent reads "CI green" as "safe to merge." An
external-service flake poisons both readings. The agent burns diagnostic budget
root-causing a "regression" that is actually a remote 503, or merges on a green
that was luck. The fix is structural, not "retry harder": **no test that depends
on an external network service may gate CI.**

## Empirical evidence (Cobrust 2026-05-27)

`l3_optional_httpbin_smoke` made a live request to `httpbin.org` and asserted
`status_code == 200`. On one CI run the macOS job, the local dev run, and all
prior runs passed — but the ubuntu job failed because httpbin returned non-200
under load. The change actually under test (a JSON-stdlib sprint) was unrelated
and passed its own E2E tests. The existing "skip if offline" guard only handled
the probe-error (unreachable) case; httpbin was *reachable yet degraded*, so the
probe succeeded and the hard `assert_eq!(.., 200)` fired.

**Resolution:** (1) `#[ignore]` the test — external-service smoke becomes opt-in
(`cargo test -- --ignored` / a dedicated network CI job), making CI deterministic
w.r.t. the third party; (2) widen the skip path so when run opt-in it clean-skips
on unreachable, request error, non-200, *and* malformed body — only a fully
healthy response reaches the assertion. **SHA:** `8b810e7`.

## Detection rule

> No test in the always-run / gating suite may make a live request to a
> third-party network service. Such tests must be `#[ignore]`'d (opt-in) or gated
> behind an explicit env/feature, and run in a dedicated network job. An
> "offline-safe" guard must clean-skip on the full degraded spectrum
> (unreachable, error, bad status, malformed body), not just unreachability.

CI candidate: grep the gating test suite for external hostnames / live-URL
literals and fail review if any are reached unconditionally.

## General Ballast mitigation

1. **Quarantine external-service tests behind `#[ignore]` or a feature flag.**
   They are valuable as opt-in smokes, never as gates.
2. **Model "up but degraded," not just "up."** Real services rate-limit and 503;
   a reachability probe is not a health check.
3. **Hermetic-by-default.** Prefer a recorded fixture / local mock for the gating
   suite; reserve live calls for an explicit, non-gating job.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F61 / F63 (this batch) | Same deterministic-CI thread: a platform-divergent probe (F61) and a host-specific path (F63) likewise leak non-determinism into the gate |
| F37 (Cobrust) — silent-rot-on-accepted-debt | CI-determinism discipline: green must mean correct, enforced via explicit `#[ignore]` |
| F44 (Cobrust) — CI cache stale-green | Sibling: another way CI green stops meaning "workspace correct" |
| F1 — Declared rules without enforcement | Parent family: "CI must be deterministic" implicit; no authorship gate |
