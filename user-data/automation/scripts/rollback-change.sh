#!/usr/bin/env bash
# rollback-change.sh — 回滚技能到指定变更点
#
# 用法:
#   bash rollback-change.sh --id <change-id>          # 回滚到指定变更之前
#   bash rollback-change.sh --scope <skill> --last    # 回滚技能的最后一次变更
#   bash rollback-change.sh --scope <skill> --to <id> # 回滚技能到指定ID
#   bash rollback-change.sh --dry-run --id <id>       # 预览回滚，不执行
#
# 原理: 利用git checkout恢复文件到指定commit的状态
# 回滚后会自动记录一条rollback类型的changelog

set -euo pipefail

SKILLS_DIR="${HOME}/.hermes/skills"
CHANGELOG_FILE="${SKILLS_DIR}/CHANGELOG.jsonl"
cd "$SKILLS_DIR"

# 解析参数
CHANGE_ID=""
SCOPE=""
MODE=""       # "last" or "to"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --id)      CHANGE_ID="$2"; shift 2 ;;
        --scope)   SCOPE="$2"; shift 2 ;;
        --last)    MODE="last"; shift ;;
        --to)      MODE="to"; CHANGE_ID="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

# 如果是 --scope --last 模式，找到该技能最后一次变更的commit
if [ -n "$SCOPE" ] && [ "$MODE" = "last" ]; then
    if [ ! -f "$CHANGELOG_FILE" ]; then
        echo "❌ No changelog found"
        exit 1
    fi
    # 找到该scope最后一条非rollback记录
    LAST_COMMIT=$(python3 -c "
import json
with open('$CHANGELOG_FILE') as f:
    for line in reversed(list(f)):
        r = json.loads(line.strip())
        if r.get('scope') == '$SCOPE' and r.get('type') != 'rollback':
            print(r['commit'])
            break
" 2>/dev/null)

    if [ -z "$LAST_COMMIT" ]; then
        echo "❌ No changelog entry found for scope: $SCOPE"
        exit 1
    fi
    echo "📍 Last change for '$SCOPE' was at commit: $LAST_COMMIT"
    # 回滚到该commit的前一个commit
    TARGET_COMMIT=$(git log --oneline "$LAST_COMMIT~1" -1 2>/dev/null | awk '{print $1}' || echo "")
    if [ -z "$TARGET_COMMIT" ]; then
        echo "❌ Cannot find parent commit of $LAST_COMMIT"
        exit 1
    fi
    echo "📍 Will rollback to commit: $TARGET_COMMIT"
fi

# 如果指定了 --id，找到对应的commit
if [ -n "$CHANGE_ID" ] && [ "$MODE" != "last" ]; then
    if [ ! -f "$CHANGELOG_FILE" ]; then
        echo "❌ No changelog found"
        exit 1
    fi
    TARGET_COMMIT=$(python3 -c "
import json
with open('$CHANGELOG_FILE') as f:
    for line in f:
        r = json.loads(line.strip())
        if r['id'] == '$CHANGE_ID':
            print(r['commit'])
            break
" 2>/dev/null)

    if [ -z "$TARGET_COMMIT" ]; then
        echo "❌ Change ID not found: $CHANGE_ID"
        exit 1
    fi
    echo "📍 Change $CHANGE_ID was at commit: $TARGET_COMMIT"
fi

if [ -z "${TARGET_COMMIT:-}" ]; then
    echo "❌ No target commit determined. Use --id <id> or --scope <skill> --last"
    exit 1
fi

# 确定要恢复的文件范围
if [ -n "$SCOPE" ]; then
    # 只恢复该技能目录下的文件
    RESTORE_PATH="$SCOPE/"
    echo "📦 Restoring only: $SCOPE/"
else
    # 恢复所有变更文件
    RESTORE_PATH=""
    echo "📦 Restoring all files changed since $TARGET_COMMIT"
fi

# 预览变更
echo ""
echo "📋 Files to be restored:"
if [ -n "$RESTORE_PATH" ]; then
    DIFF_FILES=$(git diff --name-only "$TARGET_COMMIT" HEAD -- "$RESTORE_PATH" 2>/dev/null || echo "")
else
    DIFF_FILES=$(git diff --name-only "$TARGET_COMMIT" HEAD 2>/dev/null || echo "")
fi

if [ -z "$DIFF_FILES" ]; then
    echo "   (no differences found)"
    exit 0
fi

echo "$DIFF_FILES" | while read -r f; do
    echo "   $f"
done

# Dry run模式
if $DRY_RUN; then
    echo ""
    echo "🔍 Dry run — no changes made. Run without --dry-run to execute."
    exit 0
fi

# 确认
echo ""
read -rp "⚠️  Confirm rollback to $TARGET_COMMIT? [y/N] " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# 执行回滚
if [ -n "$RESTORE_PATH" ]; then
    git checkout "$TARGET_COMMIT" -- "$RESTORE_PATH" 2>/dev/null
else
    git checkout "$TARGET_COMMIT" -- . 2>/dev/null
fi

echo "✅ Files restored from commit $TARGET_COMMIT"

# 记录rollback changelog
ROLLBACK_DESC="Rollback to commit ${TARGET_COMMIT}"
if [ -n "$SCOPE" ]; then
    ROLLBACK_DESC="Rollback $SCOPE to commit ${TARGET_COMMIT}"
fi

bash ~/.hermes/scripts/record-change.sh \
    --type rollback \
    --scope "${SCOPE:-global}" \
    --desc "$ROLLBACK_DESC" \
    --reason "Manual rollback via rollback-change.sh" \
    --impact "Files restored to state at $TARGET_COMMIT" \
    --author agent

# 同步到GitHub
bash ~/.hermes/scripts/auto-sync-skills.sh

echo "✅ Rollback complete and synced to GitHub"
