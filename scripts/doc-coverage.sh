#!/usr/bin/env bash
# scripts/doc-coverage.sh — Ballast repo doc-coverage gate
#
# Enforces Ballast §3 documentation mandate on this repo itself:
# - Every docs/human/zh/*.md has a parallel docs/human/en/*.md (and vice versa)
# - Parallel files have matching filenames
# - Reference files in plugins/ballast/skills/ballast/reference/
#   have YAML frontmatter
#
# Exits non-zero on coverage failure. Pre-commit hook + CI both should run this.

set -euo pipefail

REPO_ROOT="${1:-$(git rev-parse --show-toplevel)}"
cd "$REPO_ROOT"

# Color output (skip if not a TTY)
if [ -t 1 ]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[1;33m'
  NC='\033[0m'
else
  RED='' GREEN='' YELLOW='' NC=''
fi

errors=0

echo "Ballast doc-coverage gate"
echo "----------------------"

# ----------------------------------------------------------------------------
# Inv 1: docs/human/zh/<file> ⟺ docs/human/en/<file> parity
# ----------------------------------------------------------------------------
echo ""
echo "[Inv 1] Bilingual parity (zh ⟺ en)"

if [ ! -d docs/human/zh ] || [ ! -d docs/human/en ]; then
  echo -e "  ${YELLOW}Warning: docs/human/{zh,en} missing — skipping parity check${NC}"
else
  # Build sorted lists
  zh_files=$(find docs/human/zh -maxdepth 2 -name '*.md' -exec basename {} \; | sort)
  en_files=$(find docs/human/en -maxdepth 2 -name '*.md' -exec basename {} \; | sort)

  # Diff zh against en
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    if [ ! -f "docs/human/en/$f" ]; then
      echo -e "  ${RED}error${NC}: docs/human/zh/$f has no parallel docs/human/en/$f"
      errors=$((errors + 1))
    fi
  done <<< "$zh_files"

  # Diff en against zh
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    if [ ! -f "docs/human/zh/$f" ]; then
      echo -e "  ${RED}error${NC}: docs/human/en/$f has no parallel docs/human/zh/$f"
      errors=$((errors + 1))
    fi
  done <<< "$en_files"

  if [ "$errors" -eq 0 ]; then
    zh_count=$(echo "$zh_files" | grep -c . || true)
    en_count=$(echo "$en_files" | grep -c . || true)
    echo -e "  ${GREEN}OK${NC}: $zh_count zh + $en_count en files, all parallel"
  fi
fi

# ----------------------------------------------------------------------------
# Inv 2: reference files have YAML frontmatter
# ----------------------------------------------------------------------------
echo ""
echo "[Inv 2] Reference file frontmatter"

ref_dir="plugins/ballast/skills/ballast/reference"
if [ -d "$ref_dir" ]; then
  for f in "$ref_dir"/*.md; do
    [ -f "$f" ] || continue
    first_line=$(head -1 "$f")
    if [ "$first_line" != "---" ]; then
      echo -e "  ${RED}error${NC}: $f missing YAML frontmatter (first line not '---')"
      errors=$((errors + 1))
    fi
  done

  if [ "$errors" -eq 0 ] || [ -z "${seen_inv2_err:-}" ]; then
    ref_count=$(find "$ref_dir" -name '*.md' | wc -l | tr -d ' ')
    echo -e "  ${GREEN}OK${NC}: $ref_count reference file(s) all have frontmatter"
  fi
fi

# ----------------------------------------------------------------------------
# Inv 3: ADR files (if any) zero-padded monotonic
# ----------------------------------------------------------------------------
echo ""
echo "[Inv 3] ADR numbering (zero-padded monotonic)"

adr_dir="docs/agent/adr"
if [ -d "$adr_dir" ]; then
  adr_count=$(find "$adr_dir" -name '[0-9][0-9][0-9][0-9]-*.md' | wc -l | tr -d ' ')
  if [ "$adr_count" -gt 0 ]; then
    # Just verify each ADR filename starts with 4 digits
    bad_count=$(find "$adr_dir" -name '*.md' -not -name '_*' \
      | grep -cv '/[0-9][0-9][0-9][0-9]-' || true)
    if [ "$bad_count" -gt 0 ]; then
      echo -e "  ${RED}error${NC}: $bad_count ADR file(s) not zero-padded 4-digit prefixed"
      errors=$((errors + 1))
    else
      echo -e "  ${GREEN}OK${NC}: $adr_count ADR file(s) properly numbered"
    fi
  else
    echo -e "  ${YELLOW}info${NC}: no ADRs yet (acceptable for a fresh repo)"
  fi
else
  echo -e "  ${YELLOW}info${NC}: docs/agent/adr/ doesn't exist (acceptable)"
fi

# ----------------------------------------------------------------------------
# Inv 4: adopting-project snapshot gate still fails when it should
# ----------------------------------------------------------------------------
echo ""
echo "[Inv 4] Snapshot gate self-test"

if ! python3 scripts/check_ballast_docs.py --self-test; then
  echo -e "  ${RED}error${NC}: scripts/check_ballast_docs.py --self-test failed"
  errors=$((errors + 1))
fi

# ----------------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------------
echo ""
echo "----------------------"
if [ "$errors" -eq 0 ]; then
  echo -e "${GREEN}doc-coverage: PASS${NC}"
  exit 0
else
  echo -e "${RED}doc-coverage: FAIL ($errors errors)${NC}"
  exit 1
fi
