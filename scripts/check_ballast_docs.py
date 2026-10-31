#!/usr/bin/env python3
"""Ballast snapshot gate for an adopting project.

Checks the promises that are cheap to keep mechanically true:

- snapshot ``base_head`` is an ancestor of ``HEAD`` (equality is allowed,
  but it is not required: the commit that records the snapshot makes
  equality false while ancestry stays true)
- every ADR file and every finding file appears exactly once in the
  snapshot roster, and every roster id has a file
- ``last_verified_commit`` is a 40-character SHA that is an ancestor of
  ``HEAD``. ``TBD``, empty, and a shortened SHA fail. No document id is
  exempt
- ``## Verification summary`` appears once, and every claim's Grade is
  ``offline``, ``review``, ``deployed``, ``live``, or ``not-run``
- ``drift_axis`` is ``bilingual`` or ``audience``. Audience mode requires
  the two declared directories to contain the same ``*.md`` names

Fails closed: an unexpected exception is an error, never a pass.

This methodology repo is not itself a project snapshot. ``--self-test``
builds temporary git repositories and is what ``scripts/doc-coverage.sh``
runs. Adopting projects run the script against their own root.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

GRADES = {"offline", "review", "deployed", "live", "not-run"}
SHA = re.compile(r"^[0-9a-fA-F]{40}$")
ADR_NAME = re.compile(r"^(\d{4})-.+\.md$")
FINDING_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class Check:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.error(message)


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    out: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line or line.startswith((" ", "\t", "-")):
            continue
        key, value = line.split(":", 1)
        out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def section_bodies(text: str, title: str) -> list[str]:
    matches = list(re.finditer(r"^## (.+?)\s*$", text, re.M))
    bodies: list[str] = []
    for index, match in enumerate(matches):
        if match.group(1) != title:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        bodies.append(text[start:end])
    return bodies


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def tables(body: str) -> list[tuple[list[str], list[list[str]]]]:
    found: list[tuple[list[str], list[list[str]]]] = []
    header: list[str] | None = None
    rows: list[list[str]] = []
    in_table = False
    for line in body.splitlines():
        if line.strip().startswith("|"):
            cells = split_row(line)
            if not in_table:
                header = cells
                rows = []
                in_table = True
                continue
            if is_separator(cells) and not rows:
                continue
            rows.append(cells)
            continue
        if in_table and header is not None:
            found.append((header, rows))
            header = None
            rows = []
            in_table = False
    if in_table and header is not None:
        found.append((header, rows))
    return found


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def head_sha(root: Path, check: Check) -> str:
    result = git(root, "rev-parse", "HEAD")
    if result.returncode != 0:
        check.error("snapshot gate requires a git repository with a HEAD commit")
        return ""
    return result.stdout.strip()


def is_ancestor(root: Path, sha: str) -> bool:
    return git(root, "merge-base", "--is-ancestor", sha, "HEAD").returncode == 0


def require_sha(check: Check, label: str, value: str, root: Path) -> None:
    if not SHA.fullmatch(value or ""):
        check.error(f"{label} must be a 40-character SHA, found {value!r}")
        return
    if not is_ancestor(root, value):
        check.error(f"{label} {value} is not an ancestor of HEAD")


def roster_ids(body: str, pattern: re.Pattern[str]) -> list[str]:
    ids: list[str] = []
    for header, rows in tables(body):
        if not header:
            continue
        for row in rows:
            if row and pattern.fullmatch(row[0]):
                ids.append(row[0])
    return ids


def check_verification(check: Check, text: str) -> None:
    bodies = section_bodies(text, "Verification summary")
    check.require(len(bodies) == 1, f"## Verification summary must appear exactly once, found {len(bodies)}")
    if len(bodies) != 1:
        return
    graded = [(header, rows) for header, rows in tables(bodies[0]) if "Grade" in header]
    check.require(len(graded) == 1, f"verification summary must contain exactly one Grade table, found {len(graded)}")
    if len(graded) != 1:
        return
    header, rows = graded[0]
    grade_at = header.index("Grade")
    for row in rows:
        if len(row) <= grade_at or not row[0]:
            check.error(f"verification row is missing a claim or Grade cell: {row!r}")
            continue
        grade = row[grade_at]
        if grade not in GRADES:
            check.error(
                f"verification grade {grade!r} is not one of {', '.join(sorted(GRADES))}"
            )


def check_audience(check: Check, root: Path, meta: dict[str, str]) -> None:
    for key in ("audience_human_dir", "audience_agent_dir"):
        check.require(key in meta, f"snapshot drift_axis audience requires {key}")
    if "audience_human_dir" not in meta or "audience_agent_dir" not in meta:
        return
    dirs: list[Path] = []
    for key in ("audience_human_dir", "audience_agent_dir"):
        raw = meta[key]
        path = Path(raw)
        if path.is_absolute() or ".." in path.parts:
            check.error(f"{key} must be a relative path inside the repository, found {raw!r}")
            return
        resolved = root / path
        check.require(resolved.is_dir(), f"{key} {raw} is not a directory")
        dirs.append(resolved)
    if len(dirs) != 2 or not all(path.is_dir() for path in dirs):
        return
    names = [{item.name for item in path.glob("*.md") if item.is_file()} for path in dirs]
    if names[0] != names[1]:
        missing_agent = sorted(names[0] - names[1])
        missing_human = sorted(names[1] - names[0])
        check.error(
            "audience directories must contain the same markdown names; "
            f"only human has {missing_agent}, only agent has {missing_human}"
        )


def check_root(root: Path) -> list[str]:
    check = Check()
    try:
        snapshot_path = root / "docs" / "agent" / "SNAPSHOT.md"
        check.require(snapshot_path.is_file(), "docs/agent/SNAPSHOT.md is missing")
        if not snapshot_path.is_file():
            return check.errors
        text = snapshot_path.read_text(encoding="utf-8")
        meta = frontmatter(text)
        check.require(meta.get("doc_kind") == "snapshot", "snapshot doc_kind must be snapshot")
        head = head_sha(root, check)
        if head:
            require_sha(check, "snapshot base_head", meta.get("base_head", ""), root)
            require_sha(check, "snapshot last_verified_commit", meta.get("last_verified_commit", ""), root)
        axis = meta.get("drift_axis", "")
        check.require(axis in {"bilingual", "audience"}, f"snapshot drift_axis must be bilingual or audience, found {axis!r}")
        if axis == "audience":
            check_audience(check, root, meta)

        adr_dirs = [root / "docs" / "adr", root / "docs" / "agent" / "adr"]
        check.require(any(path.is_dir() for path in adr_dirs), "docs/adr or docs/agent/adr must exist")
        findings_dir = root / "docs" / "agent" / "findings"
        check.require(findings_dir.is_dir(), "docs/agent/findings must exist")

        adr_files = [path for directory in adr_dirs if directory.is_dir() for path in sorted(directory.glob("[0-9][0-9][0-9][0-9]-*.md"))]
        finding_files = sorted(findings_dir.glob("*.md")) if findings_dir.is_dir() else []

        adr_ids: list[str] = []
        for path in adr_files:
            match = ADR_NAME.fullmatch(path.name)
            if match is None:
                check.error(f"{path.name} is not a zero-padded ADR filename")
                continue
            adr_id = match.group(1)
            adr_ids.append(adr_id)
            doc = frontmatter(path.read_text(encoding="utf-8"))
            check.require(doc.get("doc_kind") == "adr", f"{path.name} must declare doc_kind: adr")
            check.require(doc.get("adr_id") == adr_id, f"{path.name} adr_id must equal {adr_id}")
            for field in ("title", "status", "date", "last_verified_commit"):
                check.require(bool(doc.get(field)), f"{path.name} missing {field}")
            if head and doc.get("last_verified_commit"):
                require_sha(check, f"{path.name} last_verified_commit", doc["last_verified_commit"], root)

        finding_ids: list[str] = []
        for path in finding_files:
            stem = path.stem
            finding_ids.append(stem)
            doc = frontmatter(path.read_text(encoding="utf-8"))
            check.require(doc.get("doc_kind") == "finding", f"{path.name} must declare doc_kind: finding")
            check.require(doc.get("finding_id") == stem, f"{path.name} finding_id must equal {stem}")
            for field in ("severity", "status", "last_verified_commit"):
                check.require(bool(doc.get(field)), f"{path.name} missing {field}")
            if head and doc.get("last_verified_commit"):
                require_sha(check, f"{path.name} last_verified_commit", doc["last_verified_commit"], root)

        adr_sections = section_bodies(text, "ADR roster")
        finding_sections = section_bodies(text, "Findings ledger")
        check.require(len(adr_sections) == 1, f"## ADR roster must appear exactly once, found {len(adr_sections)}")
        check.require(len(finding_sections) == 1, f"## Findings ledger must appear exactly once, found {len(finding_sections)}")
        if len(adr_sections) == 1:
            found = roster_ids(adr_sections[0], re.compile(r"\d{4}"))
            check.require(sorted(found) == sorted(adr_ids), f"ADR roster {found} must match ADR files {adr_ids} exactly once each")
            counts = Counter(found)
            for adr_id, count in counts.items():
                check.require(count == 1, f"ADR {adr_id} appears {count} times in the roster")
        if len(finding_sections) == 1:
            found = roster_ids(finding_sections[0], FINDING_ID)
            check.require(
                sorted(found) == sorted(finding_ids),
                f"findings ledger {found} must match finding files {finding_ids} exactly once each",
            )
            for finding_id, count in Counter(found).items():
                check.require(count == 1, f"finding {finding_id} appears {count} times in the ledger")
        check_verification(check, text)
    except Exception as exc:  # A gate must fail closed, never crash green.
        check.error(f"checker failed: {exc.__class__.__name__}: {exc}")
    return check.errors


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def git_ok(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), "-c", "commit.gpgsign=false", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def init_repo() -> tuple[Path, str]:
    root = Path(tempfile.mkdtemp(prefix="ballast-docs-"))
    subprocess.run(["git", "-C", str(root), "init", "-b", "main"], check=True, capture_output=True, text=True)
    git_ok(root, "config", "user.email", "ballast-fixture@example.com")
    git_ok(root, "config", "user.name", "ballast-fixture")
    git_ok(root, "config", "commit.gpgsign", "false")
    git_ok(root, "commit", "--allow-empty", "-m", "base")
    return root, git_ok(root, "rev-parse", "HEAD")


def adr_text(sha: str, adr_id: str = "0001", title: str = "One authority") -> str:
    return (
        "---\n"
        "doc_kind: adr\n"
        f'adr_id: "{adr_id}"\n'
        f'title: "{title}"\n'
        "status: accepted\n"
        "date: 2026-10-31\n"
        f"last_verified_commit: {sha}\n"
        "supersedes: []\n"
        "superseded_by: []\n"
        "---\n\n"
        f"# ADR-{adr_id}: {title}\n"
    )


def finding_text(sha: str, finding_id: str = "sample-gap") -> str:
    return (
        "---\n"
        "doc_kind: finding\n"
        f"finding_id: {finding_id}\n"
        f"last_verified_commit: {sha}\n"
        'discovered_by: "fixture"\n'
        "severity: P2\n"
        "status: open\n"
        'related: ["0001"]\n'
        "---\n\n"
        "# Finding: sample gap\n"
    )


def snapshot_text(sha: str, axis: str = "bilingual", extra: str = "") -> str:
    return (
        "---\n"
        "doc_kind: snapshot\n"
        f"base_head: {sha}\n"
        f"last_verified_commit: {sha}\n"
        f"drift_axis: {axis}\n"
        f"{extra}"
        "date: 2026-10-31\n"
        "---\n\n"
        "# Fixture snapshot\n\n"
        "## ADR roster\n\n"
        "| ADR | Title | Status |\n"
        "|---|---|---|\n"
        "| 0001 | One authority | accepted |\n\n"
        "## Findings ledger\n\n"
        "| Finding ID | Description | Status |\n"
        "|---|---|---|\n"
        "| sample-gap | a negative result kept on the ledger | open |\n\n"
        "## Verification summary\n\n"
        "| Claim | Grade | Evidence |\n"
        "|---|---|---|\n"
        "| second holder is rejected | live | request log for this wave |\n"
        "| other rates | not-run | not this wave |\n"
    )


def populate(root: Path, sha: str, axis: str = "bilingual", extra: str = "") -> None:
    write(root / "docs/adr/0001-one-authority.md", adr_text(sha))
    write(root / "docs/agent/findings/sample-gap.md", finding_text(sha))
    write(root / "docs/agent/SNAPSHOT.md", snapshot_text(sha, axis, extra))
    (root / "docs/agent/adr").mkdir(parents=True, exist_ok=True)


def commit_all(root: Path, message: str) -> str:
    git_ok(root, "add", "-A")
    git_ok(root, "commit", "-m", message)
    return git_ok(root, "rev-parse", "HEAD")


def expect(name: str, errors: list[str], substring: str | None) -> str | None:
    if substring is None:
        if errors:
            return f"{name}: expected pass, got {errors}"
        return None
    if not any(substring in error for error in errors):
        return f"{name}: expected {substring!r} in {errors}"
    return None


def self_test() -> int:
    failures: list[str] = []
    root, base = init_repo()
    try:
        populate(root, base)
        commit_all(root, "record the wave")
        failures.append(expect("ancestor passes after the snapshot commit", check_root(root), None) or "")

        equal = root / "docs/agent/SNAPSHOT.md"
        text = equal.read_text(encoding="utf-8")
        head = git_ok(root, "rev-parse", "HEAD")
        equal.write_text(text.replace(f"base_head: {base}", f"base_head: {head}", 1), encoding="utf-8")
        failures.append(expect("equality with HEAD still passes", check_root(root), None) or "")
        equal.write_text(text, encoding="utf-8")

        bare = init_repo()[0]
        write(bare / "docs/adr/0001-one-authority.md", "# ADR-0001\n\nNo frontmatter.\n")
        write(bare / "docs/agent/findings/.gitkeep", "")
        write(bare / "docs/agent/SNAPSHOT.md", snapshot_text("a" * 40))
        git_ok(bare, "add", "-A")
        git_ok(bare, "commit", "--allow-empty", "-m", "keep head")
        # The empty commit above may be a second commit; HEAD exists from init.
        failures.append(expect("founding ADR is not exempt", check_root(bare), "0001-one-authority.md must declare doc_kind: adr") or "")
        shutil.rmtree(bare)

        bad = (root / "docs/agent/findings/sample-gap.md").read_text(encoding="utf-8")
        (root / "docs/agent/findings/sample-gap.md").write_text(
            bad.replace(base, "TBD", 1),
            encoding="utf-8",
        )
        failures.append(expect("TBD is not a SHA", check_root(root), "must be a 40-character SHA") or "")
        (root / "docs/agent/findings/sample-gap.md").write_text(bad, encoding="utf-8")

        side = git_ok(root, "rev-parse", "HEAD")
        subprocess.run(["git", "-C", str(root), "checkout", "--orphan", "side"], check=True, capture_output=True, text=True)
        git_ok(root, "commit", "--allow-empty", "-m", "unrelated")
        unrelated = git_ok(root, "rev-parse", "HEAD")
        subprocess.run(["git", "-C", str(root), "checkout", "main"], check=True, capture_output=True, text=True)
        current = (root / "docs/agent/SNAPSHOT.md").read_text(encoding="utf-8")
        (root / "docs/agent/SNAPSHOT.md").write_text(current.replace(base, unrelated, 1), encoding="utf-8")
        failures.append(expect("unrelated base_head fails", check_root(root), "is not an ancestor of HEAD") or "")
        (root / "docs/agent/SNAPSHOT.md").write_text(current, encoding="utf-8")
        del side

        roster = (root / "docs/agent/SNAPSHOT.md").read_text(encoding="utf-8")
        (root / "docs/agent/SNAPSHOT.md").write_text(
            roster.replace("| 0001 | One authority | accepted |\n", "", 1),
            encoding="utf-8",
        )
        failures.append(expect("missing roster row fails", check_root(root), "ADR roster") or "")
        (root / "docs/agent/SNAPSHOT.md").write_text(
            roster.replace(
                "| 0001 | One authority | accepted |\n",
                "| 0001 | One authority | accepted |\n| 0001 | One authority | accepted |\n",
                1,
            ),
            encoding="utf-8",
        )
        failures.append(expect("duplicate roster row fails", check_root(root), "appears 2 times") or "")
        (root / "docs/agent/SNAPSHOT.md").write_text(roster, encoding="utf-8")

        graded = roster.replace("| other rates | not-run | not this wave |\n", "| other rates | passed | copied from last wave |\n", 1)
        (root / "docs/agent/SNAPSHOT.md").write_text(graded, encoding="utf-8")
        failures.append(expect("promoted grade fails", check_root(root), "verification grade 'passed'") or "")

        paired = roster.replace("drift_axis: bilingual\n", "drift_axis: audience\naudience_human_dir: docs/procedure\naudience_agent_dir: docs/agent/procedure\n", 1)
        (root / "docs/agent/SNAPSHOT.md").write_text(paired, encoding="utf-8")
        write(root / "docs/procedure/widget.md", "# widget\n")
        (root / "docs/agent/procedure").mkdir(parents=True, exist_ok=True)
        failures.append(expect("unpaired audience doc fails", check_root(root), "same markdown names") or "")
        write(root / "docs/agent/procedure/widget.md", "# widget\n")
        failures.append(expect("paired audience docs pass", check_root(root), None) or "")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    problems = [failure for failure in failures if failure]
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        print(f"BALLAST_DOCS_SELF_TEST_FAILED cases={len(problems)}")
        return 1
    print("BALLAST_DOCS_SELF_TEST_OK")
    return 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    root = Path(argv[0]).resolve() if argv else Path.cwd()
    errors = check_root(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"BALLAST_DOCS_CHECK_FAILED errors={len(errors)}")
        return 1
    print("BALLAST_DOCS_CHECK_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
