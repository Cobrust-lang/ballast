---
catalogue_id: F46
title: "Package not installable — build-host paths and unbundled runtime assets bake into the release artifact, so it works on the build machine and is 100% broken on a fresh one"
family: F1-Sediment (packaging-discipline sub-form) + F35-ClaimDrift
severity: P1 (every distributed artifact non-functional for end users)
status: ratified_2026-05-22
empirical_project: Cobrust Phase O wheel distribution (v0.5.1 + v0.5.2, 2026-05-22)
cobrust_local_id: F46 (f46-wheel-not-installable-runtime-stdlib-gap.md)
cobrust_sha: c55f859 (finding) → resolution in v0.6.0 (ADR-0069)
resolution: current_exe()-rooted asset lookup + bundle runtime/stdlib into the tarball + post-package extract-and-run smoke gate
related: [F44, F45, F45a, F49, F1-Sediment, F35-ClaimDrift]
---

# F46 — Package not installable: fresh-environment assumption leaks

## Pattern

A release artifact carries **build-host assumptions** that hold only on the
machine that built it:

- A compile-time-baked absolute path (`env!("CARGO_MANIFEST_DIR")`,
  `__file__`-relative roots, hardcoded `/home/runner/...`) used at *runtime* to
  locate assets.
- Runtime dependencies (C source, prebuilt archives, data files, templates) that
  the package format **does not bundle** — they exist only in the build
  workspace.

The artifact works perfectly when tested from the build workspace (the paths
resolve, the assets are on disk) and is **100% broken** the instant it is
extracted onto a fresh machine. The source-built install path masks the gap
indefinitely because the build directory still exists locally.

## Root cause

A **fresh-environment assumption that was never tested in a fresh environment.**

- **Compile-time path baked into a runtime lookup.** A constant that resolves to
  the CI runner's workspace (`/.../runner/work/<repo>/<repo>/...`) gets compiled
  into the binary and consulted at run time on the user's machine, where that
  directory never existed and was garbage-collected hours after release.
- **Package schema omits runtime assets.** The tarball packages only the
  binaries; the runtime C files and prebuilt static archive the binary needs are
  not in the package. Even a correct lookup would find nothing on disk.
- **F1-Sediment**: the path-lookup code predates cross-machine distribution by
  months (assets were always workspace-internal). The distribution sprint shipped
  wheels *without rewriting the lookup chain* — the old assumption silently
  carried forward.
- **F35-ClaimDrift**: "wheel bundles the binaries" was *technically true* (they
  appear in the tarball) but *materially false* (the binary cannot compile a
  single source file).

## Why this is critical for Ballast / agent-driven projects

An agent verifies its work where it works: the build workspace. "It runs" is true
there and false everywhere else. No amount of building, testing, or CI-green on
the *build* machine can catch a fresh-environment gap — only an explicit
"extract the shipped artifact onto a clean machine/dir and run it" step can.
This is the packaging twin of F45's object-emit-vs-behavior gap: "binary appears
in tarball" is the necessary-but-not-sufficient gate; "binary works zero-config
for a stranger" is the real one.

## Empirical evidence (Cobrust v0.5.1 + v0.5.2, 2026-05-22)

Reproduced by downloading the published wheel onto a fresh dir:

```bash
mkdir /tmp/test && cd /tmp/test
tar xzf cobrust-v0.5.2-<target>.tar.gz
echo 'fn main() -> i64: print("hello"); return 0' > hello.cb
./cobrust run hello.cb
# error: Internal error: cannot locate runtime/cobrust_main.c (checked
#   /Users/runner/work/cobrust/cobrust/crates/cobrust-cli/runtime/cobrust_main.c)
```

The error message itself prints the **CI runner's workspace path** — a directory
that existed only during the build job and was already gone. Root causes
confirmed: `build.rs` used `env!("CARGO_MANIFEST_DIR")` for a runtime lookup; the
fallback chain walked the build workspace `target/`; the tarball schema packaged
binaries only, no runtime C files, no prebuilt archive. The source-built path
(`cargo install --git`) kept working on the build machine and masked the gap
through every prior release.

## Detection rule (CI gate)

**Every release pipeline MUST extract the produced artifact and run it from a
fresh directory before upload** — never test the build-workspace binary.

```bash
# Post-package smoke gate (release.yml), BEFORE artifact upload:
cd "$(mktemp -d)"
tar xzf "$TARBALL"
echo 'fn main() -> i64: print("smoke"); return 0' > t.cb
./cobrust run t.cb | grep -q smoke || { echo "FAIL: shipped artifact broken on fresh dir"; exit 1; }
```

Recurrence rule: **any** packaging change (add a binary, change tarball schema,
adjust layout, switch compression) re-runs this gate — they all share the
fresh-environment-fragility class.

## Resolution path

1. **Root asset lookup at `current_exe()`**, not at a compile-time build path —
   resolve assets relative to the installed binary's own location, with the
   build-workspace path only as a last-resort dev fallback.
2. **Bundle every runtime dependency** into the package under a stable layout
   (FHS-ish `bin/` `lib/` `share/`); the binary looks them up relative to itself.
3. **Add the post-package extract-and-run smoke gate** to the release pipeline.
4. **Audit question for any distributable**: "If I delete the build workspace and
   hand the tarball to a stranger, does it work zero-config?" If unproven, it's
   unproven — add the gate.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F45 / F45a — Stub silently shipped | Sibling: "object-emit green ≠ end-user working." F45 at the codegen layer, F46 at the packaging layer — same necessary-but-not-sufficient gate confusion |
| F44 — CI cache stale-green | Sibling: CI green on every build job; release pipeline had no post-package smoke step; nothing caught the broken artifact |
| F49 — Fresh-workspace identity leak | Direct sibling: both are "fresh-environment assumptions leak" — F49 leaks the OS-default git identity, F46 leaks the build-host filesystem layout |
| F35 — Commit-msg vs diff drift | Parent: "bundles the binaries" technically true, materially false at user level |
| F1 — Declared rules without enforcement | Parent: "the package must be self-contained" is common sense; no gate enforced it at release-pipeline authorship time |
