---
catalogue_id: F63
title: "Tests create temp dirs without RAII cleanup — artifacts accumulate unbounded in a host-specific temp root the cleanup SOP didn't name"
family: resource-leak (unbounded test-artifact accumulation) + SOP claim-vs-reality drift
severity: P2 (silent disk exhaustion over weeks/months)
status: ratified_2026-05-28 (cleanup done; RAII refactor deferred → see F64)
empirical_project: Cobrust disk-pressure incident (2026-05-28)
cobrust_local_id: F63 (f63-cobrust-test-tempdir-accumulation-macos-var-folders.md)
date_ratified: 2026-05-28
cobrust_sha: 4089cd8 (incident), 1b05ae3 (RAII refactor sprint)
related: [F59, F61, F64]
---

# F63 — Unbounded test-artifact accumulation in a host-specific temp root

## Pattern

Integration tests create per-run temp directories with a **raw path +
create-dir** idiom (no RAII cleanup wrapper) and most do **not** delete them on
exit. Each run leaves another directory behind, full of compile/link output. Over
weeks of CI-and-local runs, thousands of orphaned dirs accumulate and silently
consume tens-to-hundreds of GB. The OS may eventually garbage-collect by mtime,
but that is best-effort and not guaranteed.

A second, compounding trap: the cleanup SOP names the **wrong root**. The OS's
real temp root for the test framework's "temp dir" primitive is **host/platform
specific** (on macOS: `/var/folders/<UUID>/T/`, not `/tmp`). The runbook said
`/tmp`, so the SOP's "clean the temp artifacts" step never touched the directory
where 99% of the bytes actually lived — claim-vs-reality drift, but in an
**operations document** rather than code.

## Root cause

- **No RAII cleanup**: tests used a raw `temp_dir().join(...)` + `create_dir_all`
  pattern; only a minority used the framework's RAII temp-dir type that
  auto-deletes on drop. Tests that exit (pass or fail) leak their directory.
- **Host-specific temp root**: the framework's temp-dir primitive resolves to a
  platform-dependent root. An SOP written against a hardcoded `/tmp` is silently
  wrong on the platform whose root differs.

## Why this matters for Ballast

A multi-agent project runs its test suite *constantly* — every sub-agent verify,
every CI job, every local check. An un-cleaned per-run tempdir is therefore a
slow leak with a high multiplier. It surfaces as a confusing "disk full" that
stalls *all* work (no build, no test) with no obvious culprit, since no single
run is responsible. And the operations runbook that should rescue you is itself
drifted — pointing at the wrong path — so the documented recovery step appears to
do nothing.

## Empirical evidence (Cobrust 2026-05-28)

Disk hit 99% full. The cleanup SOP's step 1 (`cargo clean`) freed ~37 GB —
insufficient. Step 2 ("clean `/tmp/cobrust-*`") found almost nothing, because on
macOS the framework's temp dirs live under `/var/folders/<UUID>/T/`:

```
/var/folders/dv/.../T = 156G
  cobrust-* dirs: 22928 directories
```

Each was a per-(pid + test-name) tempdir from a past run (names like
`cobrust-<sprint>-<test>-<pid>`), holding compile output + a linked executable
(~1 MB+ each). ~22,928 runs over months ≈ 156 GB. Cleanup
(`find /var/folders/.../T -maxdepth 1 -name 'cobrust-*' -type d -exec rm -rf {} +`)
freed 156 GB; with `cargo clean`, ~188 GB total, first time back under the 20%
free-space target.

**Resolutions:** (1) immediate cleanup; (2) update the cleanup SOP to scan the
**host-specific roots** (`$TMPDIR`, `/tmp`, `/var/folders`) on macOS; (3)
**long-term** refactor the tempdir idiom to the RAII auto-delete type — deferred
to a dedicated sprint (`1b05ae3`), which in turn surfaced F64 (its dev-dep
lockfile-staging miss). **SHA:** `4089cd8` (incident).

## Detection rule

> Every test that creates a temp directory MUST use an RAII auto-cleanup wrapper
> (delete-on-drop), never a raw create-dir that relies on OS garbage collection.
> Cleanup SOPs MUST name the **host-specific** temp root for each supported
> platform (macOS `/var/folders/<UUID>/T/`, not just `/tmp`).

CI candidate: a guard that fails if a test source uses the raw-temp-dir idiom
instead of the RAII wrapper (Cobrust added a `cli-tempdir-guard.sh`-style check).

## General Ballast mitigation

1. **RAII-by-default for test scratch.** Auto-delete on scope exit; never trust
   the OS to clean up after the suite.
2. **Audit operations SOPs against reality on every supported platform.** A
   hardcoded path in a runbook is a claim that drifts; verify the cleanup step
   actually reaches the bytes (F35-family drift, in ops docs).
3. **Monitor disk as a first-class signal.** A constantly-running test suite is a
   slow leak amplifier; surface free-space before it stalls all work.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F64 (this batch) | Direct sequel: the RAII-refactor sprint that resolves F63's long-term fix is where F64's lockfile-staging miss occurred |
| F59 / F61 (this batch) | Deterministic-CI sibling thread; F63 is the host-specific-path member (a path the SOP didn't name) |
| F1 — Declared rules without enforcement | Parent family: "clean up test scratch" + "SOPs match reality" implicit; no gate |
