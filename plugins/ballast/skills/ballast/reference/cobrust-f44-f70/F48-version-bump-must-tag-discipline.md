---
catalogue_id: F48
title: "Version-bump-without-tag — bumping the package version string without also tagging/releasing creates a binary whose announced version has no matching artifact"
family: F35-ClaimDrift (packaging-layer sub-form)
severity: P2 (ambiguous release state; downstream version/artifact mismatch)
status: ratified_2026-05-22
empirical_project: Cobrust v0.6.0 release session (retro audit 2026-05-22)
cobrust_local_id: F48 (f48-version-bump-must-tag-discipline.md)
cobrust_sha: e23d66c (finding)
resolution: version-bump commit must carry a tag-or-checklist; CI gate fails a bump with no matching tag; doc-only sub-agents never bump version
related: [F44, F46, F35-ClaimDrift]
---

# F48 — Version-bump must be accompanied by a tag

## Pattern

A commit bumps the package version string (`version = "X.Y.Z"`) but neither tags
`vX.Y.Z` nor leaves a visible reminder to do so. The version baked into built
binaries now **diverges from the tag/release index**: a user who installs from
source or registry receives a binary announcing a version that has no matching
release artifact. The release state is ambiguous — is `X.Y.Z` released or not?
Nobody can tell from the repository alone.

This is the claim-drift family applied to the version-number-vs-release-artifact
relationship: the version string *claims* a release that the tag index does not
corroborate.

## Root cause

- **Two facts that must move together are allowed to move independently.** The
  version string (in a tracked file) and the tag/release (in the git ref + forge
  release index) have no enforced linkage. Bumping one without the other is
  silently accepted.
- **No write-time or CI-time gate** verifies "if the version changed, a matching
  tag exists (or a deferral is explicitly noted)."
- **Sub-agent scope leakage**: a doc-only or unrelated sub-agent edits the
  workspace version as a side effect, with no intent (or authority) to cut a
  release — the bump happens without anyone owning the release.

## Why this is critical for Ballast / agent-driven projects

In a multi-agent flow, "bump the version" and "cut the release" are easily
separate dispatches — or worse, the bump is an incidental edit inside an
unrelated sprint. Without a gate, the version drifts ahead of the tags, and a
later agent (or user) cannot reconstruct which `X.Y.Z` are real. The same
discipline that catches commit-msg-vs-diff drift (F35) must catch
version-vs-tag drift: the claim (a version number) must be backed by the
artifact (a tag + release).

## Empirical evidence (Cobrust v0.6.0, 2026-05-22)

A v0.6.0 retro audit surfaced the documentation variant of the same drift: ADRs
committed with `last_verified_commit: TBD` — a claim placeholder never backfilled.
The version-discipline gap is the packaging-layer parallel: a version bump with no
matching tag leaves the same kind of dangling, unverifiable claim. Ratified as a
discipline rule with a CI gate candidate (below) from this pattern recognition.

## Detection rule (CI gate)

```bash
# Post-merge / PR check: if the version string changed, a matching tag must exist.
OLD=$(git show HEAD~1:Cargo.toml | grep -m1 '^version')
NEW=$(git show HEAD:Cargo.toml   | grep -m1 '^version')
if [ "$OLD" != "$NEW" ]; then
  TAG="v$(echo "$NEW" | sed 's/version = "//;s/"//')"
  git tag --list "$TAG" | grep -q "$TAG" \
    || { echo "F48 VIOLATION: version bumped to $TAG but no matching tag"; exit 1; }
fi
```

Binding discipline rules:

- A sprint that bumps the version MUST push the matching tag before the session
  ends, **or** the bump commit body MUST contain a visible checklist line
  (`[ ] Tag + publish release vX.Y.Z`) when the tag is intentionally deferred
  (e.g. awaiting CI green).
- **Doc-only / unrelated sub-agents MUST NOT bump the workspace version.** Version
  bumps belong to a release dispatch with a named owner.

## Resolution path

1. **Add the version-vs-tag CI gate** (above) to the release/PR workflow.
2. **Make the bump+tag atomic** in the release SOP: bump, tag, release in one
   owned session — or carry the explicit deferral checklist.
3. **Scope-fence version edits**: dispatch prompts for non-release work forbid
   touching the version string.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F35 — Commit-msg vs diff drift | Parent: F48 is the version-string-vs-release-artifact instance of claim drift |
| F46 — Package not installable | Sibling packaging-discipline: both are "the release pipeline lets an inconsistent/broken artifact reach users" |
| F44 — CI cache stale-green | Sibling: both rely on a missing release-time gate; CI green did not imply a coherent, tagged, installable release |
