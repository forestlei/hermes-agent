#!/usr/bin/env bash
# auto-sync-skills.sh — 自动将技能目录的改动同步到GitHub
# 规则：每次 skill_manage 调用后必须执行此脚本
#
# 功能:
# 1. 检测 ~/.hermes/skills/ 下的文件变动
# 2. 自动记录变更到 CHANGELOG.jsonl
# 3. 自动 git add + commit + push
# 4. commit message 包含变更摘要

set -euo pipefail

SKILLS_DIR="${HOME}/.hermes/skills"
cd "$SKILLS_DIR"

# 检查是否有远程仓库
HAS_REMOTE=$(git remote | grep -c "^origin$" || true)

# 检查是否有未提交的变更
if git diff --quiet 2>/dev/null && git diff --cached --quiet 2>/dev/null; then
    # 没有变更，静默退出
    exit 0
fi

# 获取变更摘要
CHANGED_FILES=$(git diff --name-only 2>/dev/null; git diff --cached --name-only 2>/dev/null | sort -u)
CHANGED_COUNT=$(echo "$CHANGED_FILES" | grep -c "." || true)

# 生成commit message
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# 提取变更的技能名
SKILL_NAMES=$(echo "$CHANGED_FILES" | grep -oP '^\w+/\K[^/]+|^[^/]+(?=/)' | sort -u | head -10 | tr '\n' ', ' | sed 's/,$//')

if [ -n "$SKILL_NAMES" ]; then
    MSG="auto: update skills [$SKILL_NAMES] ($CHANGED_COUNT files) @ $TIMESTAMP"
else
    MSG="auto: skills update ($CHANGED_COUNT files) @ $TIMESTAMP"
fi

# 自动记录变更到 CHANGELOG.jsonl
# 推断变更类型
CHANGE_TYPE="knowledge-update"  # 默认
if echo "$CHANGED_FILES" | grep -q "SKILL.md"; then
    CHANGE_TYPE="skill-upgrade"
fi
if echo "$CHANGED_FILES" | grep -q "RULES.md\|\.gitignore"; then
    CHANGE_TYPE="config-change"
fi
if echo "$CHANGED_FILES" | grep -q "data/"; then
    CHANGE_TYPE="data-update"
fi

# 为每个变更的技能记录changelog
if [ -n "$SKILL_NAMES" ]; then
    IFS=',' read -ra SKILL_ARRAY <<< "$SKILL_NAMES"
    for skill in "${SKILL_ARRAY[@]}"; do
        skill=$(echo "$skill" | xargs)  # trim
        [ -z "$skill" ] && continue
        bash ~/.hermes/scripts/record-change.sh \
            --type "$CHANGE_TYPE" \
            --scope "$skill" \
            --desc "Auto-detected change via sync" \
            --reason "Triggered by auto-sync-skills.sh" \
            --author agent 2>/dev/null || true
    done
else
    bash ~/.hermes/scripts/record-change.sh \
        --type "$CHANGE_TYPE" \
        --scope "global" \
        --desc "Auto-detected change ($CHANGED_COUNT files)" \
        --reason "Triggered by auto-sync-skills.sh" \
        --author agent 2>/dev/null || true
fi

# Git add + commit
# 清理普通主题的spec/目录（不应同步到GitHub）
if [ -d "data/topics" ]; then
    for topic_dir in data/topics/*/; do
        if [ -f "$topic_dir/metadata.json" ]; then
            topic_type=$(python3 -c "
import json
try:
    with open('$topic_dir/metadata.json') as f:
        d = json.load(f)
    print(d.get('type', 'research'))
except: print('research')
" 2>/dev/null || echo "research")
            if [ "$topic_type" != "work" ] && [ -d "$topic_dir/spec" ]; then
                git rm -r --cached "$topic_dir/spec" 2>/dev/null || true
                rm -rf "$topic_dir/spec"
                echo "  📚 $(basename $topic_dir): removed spec/ (research topic)"
            fi
        fi
    done
fi

git add -A
git commit -m "$MSG" 2>/dev/null || true

# Push
if [ "$HAS_REMOTE" -gt 0 ]; then
    BRANCH=$(git branch --show-current 2>/dev/null || echo "master")
    git push origin "$BRANCH" 2>/dev/null || echo "WARNING: push failed (check auth/network)"
fi

echo "✅ Skills synced: $CHANGED_COUNT files changed"
