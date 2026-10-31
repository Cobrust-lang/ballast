<!-- Template for a Finding (an empirical observation).
     Copy to your project's docs/<tree>/findings/.
     Findings are first-class even when negative — constitution §5.2:
     "Negative results are documented under findings/, not hidden." -->

---
doc_kind: finding
finding_id: <kebab-case-slug>
last_verified_commit: <SHA at time of writing>
discovered_by: <agent name + context, e.g. "review-claude (LeetCode farm Round 1, LC 263)">
severity: P0 | P1 | P2 | P3
related: [<other finding slugs>, <ADR refs>]
status: open | closed_by_<sprint-id> | partial-closed
---

# Finding: <one-sentence description>

## Hypothesis

What did you expect / want to verify?

State as a falsifiable claim:
- "X should produce Y given input Z"
- "Component C handles inputs of class D correctly"
- "Pipeline P passes gate G on N% of corpus"

If the finding is a *bug discovery*, frame as: "Component should X but
does Y."

## Method

Steps to reproduce:
1. Concrete commands run
2. Inputs used (paste verbatim if small; reference file path if large)
3. Environment (machine, OS, toolchain version)
4. Random seeds if any

This section must be reproducible. If a reader can't follow it
mechanically, you've under-specified.

## Result

What actually happened. **Paste raw evidence**:

```
$ cargo test foo
running 1 test
test foo ... FAILED

failures:

---- foo stdout ----
thread 'foo' panicked at ...
```

Tables for systematic measurements:

| Variant | Input | Expected | Actual | Pass? |
|---|---|---|---|---|
| A | ... | ... | ... | ✓ |
| B | ... | ... | ... | ✗ |

Don't summarize results without providing the raw evidence somewhere
(inline or in a referenced log file). "Worked correctly" without
output is a hand-wave.

## Root-cause analysis (if bug)

For bug findings, hypothesize the cause. **Mark this section as
speculative** — it's a best-guess, not ground truth, until verified by
the fix.

```
## Root-cause hypothesis (speculative — verify before quoting)

Likely cause: <theory>
Likely location: <file:line range>
Likely mechanism: <what specifically goes wrong>
```

This is critical because a finding's root-cause guess often gets cited
in subsequent ADRs. If the guess is wrong (e.g. fix lands at a
different layer), the citation gets stale. Marking it speculative up
front prevents that drift.

## Conclusion

Actionable takeaway:
- Should we fix this? Priority?
- Does this generalize to other parts of the system?
- What follow-up work does this imply?

For closed findings, add §"Resolution" with closing commit SHA.

## Cross-references

- Related ADRs (decisions made because of this finding)
- Related findings (parallel observations)
- Source code locations (file:line)
- External evidence (papers, prior bug reports)

## Resolution (added when closed)

```
status: closed_by_<sprint-id> @ <merge SHA>
```

What changed:
- Code: <commit refs>
- Tests: <new test names>
- Doc: <updated docs>

Cross-link to ADR that codified the fix, if any.
