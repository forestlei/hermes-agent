#!/bin/bash
# Evolution Verify - 进化后验证

set -e

SKILLS_DIR="$(cd ~/.hermes/skills && pwd)"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "🔍 Verifying evolution: $TIMESTAMP"

ERRORS=0
WARNINGS=0

# 检查技能目录
SKILL_COUNT=$(find "$SKILLS_DIR" -name "SKILL.md" | wc -l)
echo "  ✓ Found $SKILL_COUNT skill(s)"

# 检查git状态
if cd "$SKILLS_DIR" && git rev-parse --git-dir > /dev/null 2>&1; then
  CHANGED_FILES=$(git status --porcelain | wc -l)
  if [ "$CHANGED_FILES" -eq 0 ]; then
    echo "  ✓ Working directory clean"
  else
    echo "  ⚠ $CHANGED_FILES uncommitted file(s)"
    ((WARNINGS++))
  fi
else
  echo "  ✗ Not a git repository"
  ((ERRORS++))
fi

# 检查remote
if cd "$SKILLS_DIR" && git remote get-url origin > /dev/null 2>&1; then
  echo "  ✓ Remote configured"
else
  echo "  ⚠ No remote configured"
  ((WARNINGS++))
fi

echo ""
echo "📋 Status: $([ $ERRORS -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL") (errors=$ERRORS, warnings=$WARNINGS)"
exit $ERRORS
