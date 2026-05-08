#!/usr/bin/env bash
# record-change.sh — 记录技能变更到 CHANGELOG.jsonl
# 被 auto-sync-skills.sh 自动调用，也可手动调用
#
# 用法:
#   bash record-change.sh --type <type> --scope <scope> --desc <description> \
#       [--reason <reason>] [--impact <impact>] [--author <author>]
#
# type类型: skill-create, skill-upgrade, skill-delete, knowledge-update,
#           config-change, rollback, baseline, data-update
# scope: 技能名或"global"
# author: agent(默认) 或 user

set -euo pipefail

SKILLS_DIR="${HOME}/.hermes/skills"
CHANGELOG_FILE="${SKILLS_DIR}/CHANGELOG.jsonl"

# 解析参数
TYPE=""
SCOPE=""
DESC=""
REASON=""
IMPACT=""
AUTHOR="agent"

while [[ $# -gt 0 ]]; do
    case $1 in
        --type)    TYPE="$2"; shift 2 ;;
        --scope)   SCOPE="$2"; shift 2 ;;
        --desc)    DESC="$2"; shift 2 ;;
        --reason)  REASON="$2"; shift 2 ;;
        --impact)  IMPACT="$2"; shift 2 ;;
        --author)  AUTHOR="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

# 校验必填参数
if [ -z "$TYPE" ] || [ -z "$SCOPE" ] || [ -z "$DESC" ]; then
    echo "❌ Missing required args: --type, --scope, --desc"
    exit 1
fi

# 生成ID: 时间戳 + 随机后缀
ID_DATE=$(date "+%Y%m%d-%H%M%S")
ID_RAND=$(head -c 3 /dev/urandom | xxd -p 2>/dev/null || echo "$RANDOM")
CHANGE_ID="${ID_DATE}-${ID_RAND}"

# ISO时间戳
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S+00:00")

# 获取当前git commit hash（如果有的话）
cd "$SKILLS_DIR"
COMMIT_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "uncommitted")

# 统计文件变更数
FILES_ADDED=0
FILES_MODIFIED=0
FILES_DELETED=0

if git diff --cached --name-status 2>/dev/null | grep -q .; then
    FILES_ADDED=$(git diff --cached --name-status 2>/dev/null | grep -c "^A" || true)
    FILES_MODIFIED=$(git diff --cached --name-status 2>/dev/null | grep -c "^M" || true)
    FILES_DELETED=$(git diff --cached --name-status 2>/dev/null | grep -c "^D" || true)
fi

# 转义JSON特殊字符
escape_json() {
    echo "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/\t/\\t/g' | tr '\n' ' ' | sed 's/  */ /g; s/^ //; s/ $//'
}

DESC_ESC=$(escape_json "$DESC")
REASON_ESC=$(escape_json "$REASON")
IMPACT_ESC=$(escape_json "$IMPACT")

# 构建JSON记录
RECORD=$(cat <<EOF
{"id":"${CHANGE_ID}","timestamp":"${TIMESTAMP}","type":"${TYPE}","scope":"${SCOPE}","description":"${DESC_ESC}","reason":"${REASON_ESC}","impact":"${IMPACT_ESC}","commit":"${COMMIT_HASH}","files_added":${FILES_ADDED},"files_modified":${FILES_MODIFIED},"files_deleted":${FILES_DELETED},"author":"${AUTHOR}"}
EOF
)

# 追加到CHANGELOG.jsonl
echo "$RECORD" >> "$CHANGELOG_FILE"

echo "📝 Changelog recorded: ${CHANGE_ID} [${TYPE}] ${SCOPE}: ${DESC}"
