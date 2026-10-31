---
catalogue_id: F42
title: "Device-identifying names leaked into git history and repo files via sub-agent memory read-through"
family: F1-Sediment (opsec-boundary sub-form)
severity: P1 (privacy / opsec — identifying info in public repo)
status: ratified_2026-05-19
empirical_project: Cobrust pre-publish privacy sweep (2026-05-19)
cobrust_local_id: F39 (f39-device-name-leakage-in-commits.md)
date_ratified: 2026-05-19
cobrust_sha: d012df9
resolution: git filter-repo force-rewrite + rename + CI grep gate (Option A)
discovered_by: P10 CTO emergency audit — pre-publish privacy sweep
---

# F42 — Device-identifying names leaked into public artifacts via sub-agent memory read-through

## Pattern

Sub-agents writing commit messages, ADRs, and module documentation frequently embed
**device-identifying strings** sourced from operator memory references — hostnames,
IP addresses, SSH port numbers, GPU model SKUs, OS kernel versions, user login names —
into public-repo artifacts that land on `main`. Pre-publish, this leaks operator
infrastructure opsec into a soon-public repository.

The mechanism is a **memory read-through without opsec boundary**:

1. Operator stores concrete connection info in agent memory (e.g., `reference_x86_workstation.md`)
   so they can reconnect quickly between sessions.
2. Sub-agents reading that memory treat the literals as **publishable grounding detail**
   (it "contextualizes" the work) rather than **opsec-sensitive material**.
3. No pre-write rule prohibits embedding these strings. CI does not grep commit/diff text
   for banned patterns.
4. Strings accumulate in commit messages (not trivially rewriteable in a normal git flow),
   ADRs, workflow files, and architecture pages over many sprint sessions.

## Root cause

This is F1-family: the rule "don't embed infrastructure literals in publishable text"
exists as common sense, but no enforcement gate verifies it at write time or CI time.

Two independent contributing factors:

- **Memory-to-artifact boundary ambiguity**: agents correctly use memory to orient
  themselves. The distinction "this literal is ops-private" vs. "this literal is
  publishable" is not enforced at the tool boundary. Any memory read can silently
  propagate private literals into any subsequent write.
- **Commit message irreversibility**: file contents can be edited in place; commit
  messages require history rewrite. The longer the leak persists, the more invasive
  the remediation (force-push, filter-repo, coordinated branch cleanup).

## Empirical evidence (Cobrust 2026-05-19, pre-rewrite)

**Quantified leak inventory:**
- **31 commit messages** across `main` + feature branches contained one or more of:
  `DG-Workstation-2x3090`, `wubingjing`, `112.74.60.44`, `port 10040`, `Linux 6.x kernel`.
- **18 repo files** carried the same strings inline:
  - 8 ADRs
  - 2 architecture pages
  - 4 test files
  - 1 module documentation page
  - 1 spike document
  - 1 GitHub Actions workflow file
- **Workflow filename** `.github/workflows/workstation-gates.yml` itself hinted at
  the host identity tier via its name.

**Remediation executed (Cobrust 2026-05-19):**
- `git filter-repo --replace-text` + `--replace-message` rewrote all branches,
  mapping device-identifying strings to neutral placeholders:
  - hostname → `<self-hosted-runner>`
  - user login → `<runner-user>`
  - IP address → `<runner-ip>`
  - SSH port → `<runner-port>`
  - GPU model SKU → `<gpu-host>`
  - OS kernel version → `linux x86_64 host`
- 18 leftover worktree branches deleted (local + remote).
- Workflow renamed to `.github/workflows/self-hosted-gates.yml`.
- Force-pushed `main` with rewritten history (solo dev, no external consumers,
  operator explicit authorization).
- Ratified at commit `d012df9`.

## Detection rule (CI gate — open as of ratification)

Add a pre-commit / CI grep gate that fails the build if any banned literal reappears:

```bash
# .github/workflows/opsec-lint.yml (or pre-commit hook)
BANNED_PATTERNS=(
  "DG-Workstation"    # specific host class name
  "wubingjing"        # specific user login
  "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+"  # any IPv4 (catch-all)
  "port [0-9]{4,5}"  # explicit SSH port references
  "RTX [0-9]{4}"     # GPU model SKU
  "Linux [0-9]+\.[0-9]+"  # minor kernel version
)
for pattern in "${BANNED_PATTERNS[@]}"; do
  if git diff --cached | grep -qE "$pattern"; then
    echo "OPSEC LINT FAIL: banned pattern '$pattern' in staged diff"
    exit 1
  fi
done
```

Apply to commit messages via `commit-msg` hook as well as file content via `pre-commit`.

## Going-forward rule

When writing commit messages, ADRs, module docs, or any other publishable artifact,
**never** embed:

- Specific hostnames (use `<self-hosted-runner>` or `runner host`).
- Specific user logins (use `<runner-user>` or `the operator account`).
- IP addresses (use `<runner-ip>` or `the runner endpoint`).
- SSH port numbers (use `<runner-port>` or `the SSH port`).
- GPU model SKUs as tier identifiers (use `<gpu-host>` or describe capability: "x86_64 GPU host with CUDA").
- OS minor version + kernel version (use `linux x86_64 host`).

Initials-only references (e.g., "DG verify", "on DG") are acceptable when the
two-letter token does not uniquely identify a public-facing artifact.

## Resolution path

If the leak has already accumulated:

1. **Audit**: `git log --all --oneline | xargs -I{} git show {} -- | grep -E "<pattern>"` to
   quantify the blast radius across all branches and files.
2. **Triage**: separate file-content leaks (patchable in place) from commit-message leaks
   (require filter-repo rewrite).
3. **Rewrite**: `git filter-repo --replace-text replacements.txt --replace-message replacements.txt`
   where `replacements.txt` maps each banned literal to its neutral placeholder.
4. **Branch cleanup**: delete worktree branches that carried unrewritten history.
5. **Gate**: add CI opsec lint as described in the Detection Rule above.
6. **Memory cross-link**: add an in-repo finding file so future agents resuming without the
   operator's memory entry still have the rule available.

## Related findings

| Finding | Relationship |
|---------|--------------|
| F1 — Declared rules without enforcement | Parent family: opsec boundary exists as common sense, but no enforcement gate at write time |
| F43 — SPOF heavy-build host (Cobrust F40) | Same origin: over-reliance on a named private host created both the opsec exposure (F42) and the availability failure (F43) |
| F35 — commit-message scope drift (upstream catalogue) | Adjacent: commit messages carry unintended context; this finding is the opsec variant |
