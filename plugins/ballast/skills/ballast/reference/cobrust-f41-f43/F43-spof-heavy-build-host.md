---
catalogue_id: F43
title: "Single-point-of-failure heavy-build host — SSH-gated workstation as sole verification path collapses when host dies"
family: infrastructure-resilience (SPOF sub-form)
severity: P1 (pipeline halt — full sprint blocked on single host availability)
status: ratified_2026-05-20
empirical_project: Cobrust Phase J wave-2 sprint (2026-05-19/20)
cobrust_local_id: F40 (f40-single-point-of-failure-heavy-build-host.md)
date_ratified: 2026-05-20
cobrust_sha: 9cb84b5
resolution: DG abandonment policy — all heavy gates route to GH Actions CI
---

# F43 — Single-point-of-failure heavy-build host

## Pattern

Depending on a single SSH-reachable workstation for full-workspace cargo verification
creates a single point of failure. When the host becomes unavailable — network reset,
ISP interruption, OS issue, power event — the entire heavy-build pipeline collapses
with no fallback path and no clear error escalation.

The failure mode has three compounding layers:

1. **Hard dependency**: all heavy-build gates (`cargo test --workspace`,
   `cargo build --workspace`) route exclusively through the SSH host.
2. **Silent retry loop**: sub-agents follow their SOP and retry the SSH connection
   on failure, consuming tool budget on failed invocations for the duration of the
   outage, without escalating "host is unreachable — route to CI."
3. **No fallback policy**: no written rule exists for "if the SSH host is down, do
   this instead." The agent cannot route around the failure.

## Root cause

This is an **infrastructure resilience gap** compounded by an **F1 Sediment pattern**:

- The policy "heavy builds run on the SSH host" was written once into the dispatch
  SOP (Mode C VERIFY LOOP). It was never given a "what if the host is down?" fallback.
- Sub-agents execute the SOP faithfully, including the retry loop, without the
  meta-rule "if retry > N, escalate and route differently."
- The same implicit coupling that created the F42 opsec leak (over-reliance on a
  named private host) also created this availability failure.

## Why reproducibility matters for Ballast

Per CLAUDE.md §3 dispatch reproducibility, verification must be reproducible by any
contributor. An SSH-credential-gated single host violates this in three ways:

1. **Credential dependency**: new contributor (human or agent) cannot run heavy-build
   gates without SSH credentials to the specific host.
2. **Availability dependency**: the host must be alive, reachable, and fully configured
   (current repo clone, correct Rust toolchain, working PATH).
3. **Opacity**: any of the three failing silently stalls a sprint without a clear
   diagnostic message distinguishing "code is broken" from "host is down."

Any of these three failing silently is indistinguishable from a code regression
until diagnosed — wasting agent time on root-cause analysis of an infra issue.

## Empirical evidence (Cobrust 2026-05-19/20)

**Incident:**
- SSH endpoint failed throughout an 8+ hour session with:
  `kex_exchange_identification: read: Connection reset by peer`
- Sub-agents continued retrying (per Mode C SOP) rather than escalating.
- Tool budget consumed on failed SSH invocations.
- Mac single-crate per-crate verify (`cargo test -p <crate>`) was sufficient to
  unblock the session but was ad-hoc — no policy existed for this fallback.
- Host degradation went unflagged for the full session.

**Archaeology SHA:** `9cb84b5` — the commit where the DG self-hosted-runner
abandonment policy was explicitly documented ("Mac single-crate + CI authoritative").
Related: `d012df9` renamed `workstation-gates.yml` → `self-hosted-gates.yml` in the
same cleanup session.

**Quantified cost:** 8+ hours of sprint time during which no heavy full-workspace
verification was possible; multiple sub-agent dispatches consumed tool budget on
failed SSH retries before escalation.

## Resolution path (adopted 2026-05-20, Cobrust)

**Adopted policy — DG abandonment / GH Actions primary:**

- ALL heavy full-workspace cargo (`cargo test --workspace`, `cargo build --workspace`)
  routes to GH Actions CI (ubuntu-latest + macos-latest matrix).
- Mac local = single-crate quick-feedback only (`cargo test -p <crate>`).
- No SSH credentials in dispatch templates.
- No `ssh -p <port> <user>@<host>` patterns in SOP blocks.

GH Actions is the authoritative 2-OS matrix verifier. It is reproducible,
credential-free, and available to all contributors.

**Dispatch template change:** replace Mode C VERIFY LOOP SSH block with
"push branch → GH Actions CI passes → merge."

## Detection rule (process audit)

Signs that a project has drifted into SPOF-build territory:

1. Any SOP template contains a literal `ssh -p <port> <user>@<host>` command as a
   required verification step.
2. No documented fallback for "what if that host is unreachable."
3. CI definition (`.github/workflows/`) references a `self-hosted` runner with no
   redundancy (single runner label, no runner pool).
4. Sub-agents report "SSH connection refused / reset" but continue retrying rather
   than escalating within 2-3 attempts.

Remediation audit question: "Can a brand-new contributor with only a GitHub account
run every required verification gate?" If no, identify and route around the gap.

## General Ballast mitigation

For any Ballast project that uses a self-hosted runner or SSH-gated build host:

1. **Define the fallback policy in writing** before the first sprint that uses the host.
   Include: escalation threshold (e.g., "3 consecutive SSH failures"), fallback path
   (e.g., "push to GH Actions CI"), and clear ownership.
2. **Use cloud CI as the authoritative gate**. Self-hosted runners are opt-in acceleration,
   never the sole verification path.
3. **No host-specific identifiers in dispatch templates**. SOPs must be portable: any
   runner with the right toolchain should satisfy the gate.
4. **Sub-agent retry cap**: dispatch prompts should include "if this SSH command fails
   N consecutive times, stop retrying and report 'verification offloaded to CI'."

## Related findings

| Finding | Relationship |
|---------|--------------|
| F42 — Device-name leakage (Cobrust F39) | Co-origin: the same named private host created both the opsec exposure (F42) and the availability failure (F43) |
| F37 (Cobrust) — Silent-rot-on-accepted-debt | The host degradation was not escalated; sub-agents silently retried |
| F29 — Cross-platform runner-pool dependency (upstream catalogue) | Adjacent: F29 covers runner-pool failure at the CI-matrix level; F43 covers SSH-gated single host at the sprint-verification level |
| F1 — Declared rules without enforcement | Parent family: "have a fallback" is common sense; no enforcement gate at SOP authorship time |
