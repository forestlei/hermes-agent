#!/usr/bin/env bash
# query-changelog.sh — 查询技能变更日志
#
# 用法:
#   bash query-changelog.sh                          # 最近20条
#   bash query-changelog.sh --all                    # 全部
#   bash query-changelog.sh --scope <skill>          # 按技能名
#   bash query-changelog.sh --type <type>            # 按类型
#   bash query-changelog.sh --since "2026-04-19"     # 指定日期之后
#   bash query-changelog.sh --until "2026-04-20"     # 指定日期之前
#   bash query-changelog.sh --search <keyword>       # 关键词搜索
#   bash query-changelog.sh --id <change-id>         # 查单条
#   bash query-changelog.sh --stats                  # 统计摘要
#   bash query-changelog.sh --json                   # 原始JSON输出
#
# 可组合: --scope persistent-solver --type skill-upgrade --since "2026-04-19"

set -euo pipefail

SKILLS_DIR="${HOME}/.hermes/skills"
CHANGELOG_FILE="${SKILLS_DIR}/CHANGELOG.jsonl"

if [ ! -f "$CHANGELOG_FILE" ]; then
    echo "📭 No changelog found at $CHANGELOG_FILE"
    exit 0
fi

# 解析参数
SCOPE=""
TYPE=""
SINCE=""
UNTIL=""
SEARCH=""
CHANGE_ID=""
SHOW_ALL=false
SHOW_STATS=false
RAW_JSON=false
LIMIT=20

while [[ $# -gt 0 ]]; do
    case $1 in
        --scope)   SCOPE="$2"; shift 2 ;;
        --type)    TYPE="$2"; shift 2 ;;
        --since)   SINCE="$2"; shift 2 ;;
        --until)   UNTIL="$2"; shift 2 ;;
        --search)  SEARCH="$2"; shift 2 ;;
        --id)      CHANGE_ID="$2"; shift 2 ;;
        --all)     SHOW_ALL=true; shift ;;
        --stats)   SHOW_STATS=true; shift ;;
        --json)    RAW_JSON=true; shift ;;
        --limit)   LIMIT="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

# 按ID查单条
if [ -n "$CHANGE_ID" ]; then
    if $RAW_JSON; then
        grep "\"${CHANGE_ID}\"" "$CHANGELOG_FILE" || echo "{}"
    else
        grep "\"${CHANGE_ID}\"" "$CHANGELOG_FILE" | python3 -c "
import sys, json
for line in sys.stdin:
    r = json.loads(line.strip())
    print(f\"📌 {r['id']}\")
    print(f\"   时间: {r['timestamp']}\")
    print(f\"   类型: {r['type']}\")
    print(f\"   范围: {r['scope']}\")
    print(f\"   描述: {r['description']}\")
    if r.get('reason'): print(f\"   原因: {r['reason']}\")
    if r.get('impact'): print(f\"   影响: {r['impact']}\")
    print(f\"   Commit: {r['commit']}\")
    print(f\"   文件: +{r['files_added']} ~{r['files_modified']} -{r['files_deleted']}\")
    print(f\"   作者: {r['author']}\")
" 2>/dev/null || echo "❌ Change ID not found: $CHANGE_ID"
    fi
    exit 0
fi

# 统计模式
if $SHOW_STATS; then
    python3 -c "
import json, sys
from collections import Counter

records = []
with open('$CHANGELOG_FILE') as f:
    for line in f:
        line = line.strip()
        if line:
            try: records.append(json.loads(line))
            except: pass

if not records:
    print('📭 No records')
    exit(0)

print(f'📊 Changelog 统计')
print(f'   总记录数: {len(records)}')
print(f'   时间范围: {records[0][\"timestamp\"][:10]} ~ {records[-1][\"timestamp\"][:10]}')
print()

# 按类型统计
type_counts = Counter(r['type'] for r in records)
print('📋 按类型:')
for t, c in type_counts.most_common():
    print(f'   {t}: {c}')
print()

# 按技能统计
scope_counts = Counter(r['scope'] for r in records)
print('🎯 按技能 (Top 10):')
for s, c in scope_counts.most_common(10):
    print(f'   {s}: {c}')
print()

# 按作者统计
author_counts = Counter(r.get('author', 'unknown') for r in records)
print('👤 按作者:')
for a, c in author_counts.most_common():
    print(f'   {a}: {c}')
" 2>/dev/null
    exit 0
fi

# 过滤查询
python3 -c "
import json, sys

records = []
with open('$CHANGELOG_FILE') as f:
    for line in f:
        line = line.strip()
        if line:
            try: records.append(json.loads(line))
            except: pass

# 过滤
filtered = records
scope = '$SCOPE'
type_f = '$TYPE'
since = '$SINCE'
until = '$UNTIL'
search = '$SEARCH'

if scope:
    filtered = [r for r in filtered if r.get('scope') == scope]
if type_f:
    filtered = [r for r in filtered if r.get('type') == type_f]
if since:
    filtered = [r for r in filtered if r.get('timestamp','')[:10] >= since]
if until:
    filtered = [r for r in filtered if r.get('timestamp','')[:10] <= until]
if search:
    search_l = search.lower()
    filtered = [r for r in filtered if search_l in json.dumps(r, ensure_ascii=False).lower()]

raw_json = $( $RAW_JSON && echo 'True' || echo 'False' )
show_all = $( $SHOW_ALL && echo 'True' || echo 'False' )
limit = $LIMIT

if raw_json:
    for r in filtered:
        print(json.dumps(r, ensure_ascii=False))
else:
    display = filtered if show_all else filtered[-limit:]
    if not display:
        print('📭 No matching records')
    else:
        print(f'📋 Changelog ({len(display)} of {len(filtered)} records)')
        print()
        for r in display:
            desc = r.get('description', '')[:60]
            reason = f' → {r[\"reason\"][:40]}' if r.get('reason') else ''
            files = f'+{r[\"files_added\"]}~{r[\"files_modified\"]}-{r[\"files_deleted\"]}'
            print(f'  {r[\"timestamp\"][:16]}  [{r[\"type\"]}]  {r[\"scope\"]}  {desc}{reason}')
            print(f'    id:{r[\"id\"]}  commit:{r[\"commit\"]}  files:{files}')
" 2>/dev/null
