#!/usr/bin/env bash
# Sync ~/.claude/ contents → ~/projects/n24q02m/ public profile repo.
#
# Per CLAUDE.md rule "~/.claude SYNC LÊN REPO PUBLIC n24q02m/n24q02m":
# - Sync: CLAUDE.md, AGENTS.md, 10 personal skills, distillation tools
# - SKIP: 3-party vendor installs (gstack/claude-bug-bounty/ui-ux-pro-max) — managed by upstream
# - SKIP: audit-logs/, memory/ (private)
# - SKIP: settings.json with credentials
#
# Usage: ./sync-to-n24q02m.sh [--dry-run]

set -euo pipefail

CL="${HOME}/.claude"
N24="${HOME}/projects/n24q02m"
DRY_RUN="${1:-}"

if [[ ! -d "$N24" ]]; then
  echo "ERROR: n24q02m repo not found at $N24"
  exit 1
fi

run() {
  echo "  + $*"
  if [[ "$DRY_RUN" != "--dry-run" ]]; then
    eval "$@"
  fi
}

# Personal skills only (10) — not 3-party
PERSONAL_SKILLS=(
  ai-ml
  error-recurrence-guardrail
  fullstack-dev
  infra-devops
  mcp-dev
  product-growth
  reading-web-exports
  recurring-task-promoter
  session-transcript-extraction
  superpower-private-repo
)

# Distillation tools (P1-P5 outputs)
DISTILLATION_SCRIPTS=(
  distill_inventory.py
  test_distill_inventory.py
  distill-inventory.sh
  extract_inline_scripts.py
  test_extract_inline_scripts.py
  revert_inline_scripts.py
  orphan_analyzer.py
  test_orphan_analyzer.py
  sync-to-n24q02m.sh
  README.md
)

echo "=== Sync ~/.claude/ → n24q02m repo ==="
echo "Mode: ${DRY_RUN:-LIVE}"
echo ""

echo "Step 0: Ensure claude/ subdir structure exists (Pattern A reorg)"
mkdir -p "$N24/claude/skills" "$N24/claude/claude-code/scripts" 2>/dev/null || true
echo ""

echo "Step 1: Sync CLAUDE.md + AGENTS.md to claude/"
run "cp $CL/CLAUDE.md $N24/claude/CLAUDE.md"
run "cp $CL/AGENTS.md $N24/claude/AGENTS.md"
echo ""

echo "Step 2: Sync 10 personal skills to claude/skills/"
for skill in "${PERSONAL_SKILLS[@]}"; do
  src="$CL/skills/$skill"
  dst="$N24/claude/skills/$skill"
  if [[ -d "$src" ]]; then
    run "rm -rf $dst"
    run "cp -r $src $dst"
  fi
done
echo ""

echo "Step 3: Sync distillation tools to claude/claude-code/scripts/"
for script in "${DISTILLATION_SCRIPTS[@]}"; do
  src="$CL/scripts/$script"
  if [[ -f "$src" ]]; then
    run "cp $src $N24/claude/claude-code/scripts/$script"
  fi
done
echo ""

echo "Step 4: Show git status"
cd "$N24" && git status --short | head -30
echo ""

echo "=== Sync done. Review diff + commit manually. ==="
