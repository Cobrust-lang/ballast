---
catalogue_id: F49
title: "Fresh-workspace identity fallback leak — a new repo/clone with no local git identity falls back to OS account + device hostname, leaking real name into public commit metadata"
family: F1-Sediment (opsec-boundary sub-form) + audit-scope-too-narrow
severity: P1 (privacy — real name + device hostname in public, permanent commit metadata)
status: ratified_2026-05-22
empirical_project: Cobrust helper-repo bootstrapping (2026-05-22, three same-day incidents)
cobrust_local_id: F49 (f49-fresh-workspace-committer-identity-fallback-leak.md)
cobrust_sha: 6491614 (finding) ; leak cbc1e0e → rewrite cd2fe04
resolution: set neutral global git identity (defense-in-depth) + per-dispatch identity pre-flight + audit scope follows actual mutation surface
related: [F42, F46, F45a, F1-Sediment]
---

# F49 — Fresh-workspace committer-identity fallback leak

## Pattern

A commit made in a workspace with **no local git identity configured** (a fresh
`git init` in `/tmp`, a `gh repo fork --clone`, any ad-hoc helper repo) falls
through to git's implicit defaults:

- `user.name` ← the OS account display name (often the operator's real name)
- `user.email` ← `${shell_user}@${hostname}` (the device hostname, often
  containing the real name in plaintext)

If that workspace pushes to a **public** repo, the author/committer metadata
permanently exposes real name + device — and unlike file content, commit metadata
survives every clone/fork and is invasive to rewrite (history rewrite +
force-push). This is a *double-leak* (name + device) and *permanent* (public
history).

The trap is that the **canonical** workspace has a correct local identity set, so
all work there is clean — which lulls everyone into assuming identity is handled.
The leak fires only in *new* environments that inherit none of that local state.

## Root cause

A **fresh-environment assumption that the canonical workspace masks.**

- The canonical project workspace had `git config user.name/email` set *locally*
  during initial setup. Every commit there is clean.
- The **global** git config was *empty*. Any repo created *outside* the canonical
  workspace inherited nothing and fell back to the OS-derived identity.
- A prior opsec rule (cf. F42) was scoped to commit-message *text* and ADR *text*
  — it never anticipated commit *metadata* (author/committer fields) as a leak
  surface. The rule had a hole exactly at the fresh-workspace boundary.
- **Audit scope was too narrow** (F45a-class): the post-author audit scanned only
  the canonical repo and never inspected the freshly-created external repos the
  sprint actually mutated.

## Why this is critical for Ballast / agent-driven projects

Sub-agents inherit **no** ambient state from the canonical workspace. A dispatch
that does `git init` / `gh repo fork --clone` in a fresh dir starts with empty
local git config, and the agent — following its SOP — commits and pushes, silently
stamping the OS-default identity onto public history. The defenses are
environment-level (a neutral *global* identity so the default itself is safe) and
dispatch-level (every prompt that creates/clones a repo must set the local
identity before any commit). And the audit must follow the *actual mutation
surface*, not the assumed-default one.

## Empirical evidence (Cobrust 2026-05-22)

**Three independent fresh-workspace leaks fired the same day** before the global
config was set:

1. A new helper repo `git init`'d in `/tmp` by the lead agent — 3 commits leaked
   real name + `${user}@${hostname}`. Rescued by force-push (`cbc1e0e` → `cd2fe04`;
   brand-new repo, no external dependents).
2. A fork-clone in `/tmp` by a sub-agent for an upstream PR — 1 commit leaked;
   rescued JIT by force-push while the PR was still open.
3. A second fork-clone by another sub-agent — leak reached an upstream PR;
   fortuitously neutralized because the upstream used **squash-merge** (GitHub
   attributes the squash commit to the merger's identity, not the source author).

Both sub-agent leaks shared the same cause: the dispatch prompt did **not** inline
an identity-config step (the rule was being authored just-in-time). After the
second same-day leak the operator authorized a permanent fix — a neutral *global*
git identity — verified to make a fresh `/tmp` `git init` inherit the neutral
handle for both author and committer (defense in depth). **Side lesson:**
squash-merge acts as a natural identity-privacy shield for external fork PRs.

## Detection rule (process + per-dispatch)

1. **Per-dispatch pre-flight** before any commit in a non-canonical workspace:

```bash
test "$(git config user.name)"  = "<neutral-handle>" \
 && test "$(git config user.email)" = "<neutral-email>" \
 || { echo "FAIL: git identity not set; refusing to commit"; exit 1; }
```

2. **Dispatch-template requirement**: every prompt containing `git init` or
   `git clone`/`fork` of a non-canonical repo MUST inline:
   `git config user.name <neutral-handle> && git config user.email <neutral-email>`
   (sub-agents inherit no global state — it must be explicit per dispatch).
3. **Set a neutral global identity** so the *default* is safe even when the rule
   is forgotten (defense in depth). (Mutating global git config requires explicit
   operator authorization.)
4. **Audit scope follows mutation surface**: the post-author audit MUST
   `git log --pretty='%an <%ae>'` on **every** external repo the sprint created or
   touched — not just the canonical one — and verify the neutral identity.

## Resolution path

1. **Set the neutral global identity** (with operator authorization) — closes the
   default-fallback hole machine-wide.
2. **Inline the identity-config command** into every repo-creating/cloning
   dispatch template.
3. **Extend the audit** to the actual mutation surface (all external repos).
4. **Prefer squash-merge** for external fork PRs where local fork-commit author
   identity may differ from the desired public attribution.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F42 — Device-name leakage in commit text | Sibling (privacy family): F42 = leak in commit-message *text*; F49 = leak in commit *metadata* (author/committer). Together: any public surface — text, metadata, or external repo — must use a neutral handle |
| F46 — Package not installable | Direct sibling: both are "fresh-environment assumptions leak" — F46 leaks the build-host filesystem layout, F49 leaks the OS-default identity; neither shows up in the canonical/build workspace |
| F45a — Stub catalogue / audit scope | Sibling: audit-scope-too-narrow class — the audit inspected the assumed surface, not the actual mutated surface |
| F1 — Declared rules without enforcement | Parent: "use a neutral identity" was common sense but had no enforcement gate at the fresh-workspace boundary |
