# Contributing to Ballast

Ballast evolves the same way it teaches you to evolve your project: ADRs,
findings, atomic commits, doc-coverage on the same change.

## What kinds of contributions are most welcome

| Type | Where it lands | Bar |
|---|---|---|
| New failure mode (F31+) | `reference/failure-modes-catalogue.md` | At least one concrete empirical instance with citation |
| Case study extension | `case-study/<your-project>-multi-agent-experience.md` | Real project, real outcomes, dated entries |
| Template improvement | `templates/<name>.md` | Backwards-compatible OR new template |
| Section refinement in SKILL.md | `SKILL.md` | Cite at least one project where this refinement was tested |
| Translation (e.g. Chinese version) | `SKILL.zh.md` / `reference/*.zh.md` | Parity with English; mark `[WIP]` if partial |

## What we will not merge

- Speculative methodology rules without an empirical instance
- F-pattern proposals that are restatements of existing F1-F30
- "Tone" rewrites that lose specific examples or evidence
- Removal of attribution (e.g. dropping "discovered_by" frontmatter)

## Workflow

1. **Open an issue first** if your change exceeds ~50 lines or touches
   `SKILL.md` structure. We want to align on direction before you invest.
2. **Write the change as if it were a Cobrust commit**: atomic, with the
   doc + code (if any) + cross-references in the same commit.
3. **For F-pattern additions**: include `## FN — Title`, `**Signal**`,
   `**Root cause**`, `**Evidence**` (cite project + commit SHA or
   equivalent), `**Rule of thumb**`. Mirror the existing F1-F30 entry
   shape.
4. **For case studies**: use day-by-day or week-by-week structure. Mark
   counterfactuals (`What would have failed without this discipline:`).
5. **Apply Ballast to your contribution**:
   - If the change affects ≥ 2 files in non-trivial ways, write a short
     ADR (`docs/adr/NNNN-<slug>.md`) in this repo describing the
     rationale.
   - If your change comes from something that broke in your project,
     also write a `findings/` entry citing the incident.

## What this repo is NOT

- Not a place to host your project's ADRs (host those in your own repo)
- Not a discussion forum for AI tooling (use GitHub Discussions of your
  agent runtime project for that)
- Not an Anthropic / OpenAI / etc. official product

## Identity hygiene (per F21)

If you are an AI agent contributing under human direction:

- **Do not sign as "review-claude" or any session-overloaded handle.**
  Use your specific role (e.g. `studio-engineer-session-XYZ` or `Cobrust-CTO`)
  in commit `Co-Authored-By:` lines.
- Reserve `review-claude` for external third-party audit roles only.

This convention is itself a Ballast failure-mode prevention (F21 — cross-
session AI agent identity overload).

## Code of conduct

Be empirical. Be specific. Be brief. Don't accuse. Don't apologize.
Cite the commit / file / instance. Write so a smart engineer two years
from now can pick up your contribution cold.

The same affect Ballast teaches for findings — "this surprised us, here's
what we learned" — applies to interactions in this repo.
