#!/bin/bash
# auto-sync-data.sh — 同步Hermes运行时数据到两个GitHub仓库
# 1. forestlei/hermes-data (独立数据仓库)
# 2. forestlei/hermes-skills data/ 子目录 (技能+数据一体化)
#
# 主题同步策略：
#   🔧 工作主题 (type=work): 全量同步 (README.md + metadata.json + spec/)
#   📚 普通主题 (type=research): 仅同步索引 (README.md + metadata.json)
#
# 用法: bash ~/.hermes/scripts/auto-sync-data.sh [commit_message]
set -e

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
source "$HERMES_HOME/.env" 2>/dev/null || true

COMMIT_MSG="${1:-auto: sync runtime data $(date +%Y-%m-%d_%H%M)}"

echo "=== Hermes Data Sync ==="

# 辅助函数：根据主题类型决定同步范围
sync_topic() {
    local src_dir="$1"  # 源目录
    local dst_dir="$2"  # 目标目录
    local topic_name=$(basename "$src_dir")

    # 读取 metadata.json 中的 type 字段
    local topic_type="research"  # 默认为普通主题
    if [ -f "$src_dir/metadata.json" ]; then
        topic_type=$(python3 -c "
import json, sys
try:
    with open('$src_dir/metadata.json') as f:
        d = json.load(f)
    print(d.get('type', 'research'))
except: print('research')
" 2>/dev/null || echo "research")
    fi

    mkdir -p "$dst_dir"

    if [ "$topic_type" = "work" ]; then
        # 🔧 工作主题：全量同步
        cp -rf "$src_dir"* "$dst_dir/" 2>/dev/null || true
        echo "  🔧 $topic_name (work): full sync"
    else
        # 📚 普通主题：仅同步索引
        cp -f "$src_dir/README.md" "$dst_dir/" 2>/dev/null || true
        cp -f "$src_dir/metadata.json" "$dst_dir/" 2>/dev/null || true
        # 清理目标中可能残留的 spec/ 目录
        rm -rf "$dst_dir/spec"
        echo "  📚 $topic_name (research): index only"
    fi
}

# ==========================================
# 1. 同步 hermes-data 独立仓库
# ==========================================
DATA_REPO="/tmp/hermes-data-build"

echo "[1/2] Syncing hermes-data repo..."

# 更新数据文件
mkdir -p "$DATA_REPO/sources"
mkdir -p "$DATA_REPO/topics/ai4science"
mkdir -p "$DATA_REPO/topics/ontology-special"
mkdir -p "$DATA_REPO/reports/daily"
mkdir -p "$DATA_REPO/github-projects"

# 信息源
cp -f "$HERMES_HOME/sources/registry.json" "$DATA_REPO/sources/legacy-registry.json" 2>/dev/null || true
cp -f "$HERMES_HOME/ai-daily-report/shared/sources/registry.json" "$DATA_REPO/sources/daily-report-registry.json" 2>/dev/null || true

# 研究主题（旧格式：articles.json）
cp -f "$HERMES_HOME/sources/ai4science/articles.json" "$DATA_REPO/topics/ai4science/" 2>/dev/null || true
cp -f "$HERMES_HOME/sources/ontology-special/articles.json" "$DATA_REPO/topics/ontology-special/" 2>/dev/null || true

# 主题（新格式：按 type 字段决定同步范围）
if [ -d "$HERMES_HOME/skills/data/topics" ]; then
    for topic_dir in "$HERMES_HOME/skills/data/topics"/*/; do
        topic_name=$(basename "$topic_dir")
        # 跳过旧格式（只有articles.json的目录）
        if [ -f "$topic_dir/metadata.json" ] || [ -f "$topic_dir/README.md" ]; then
            sync_topic "$topic_dir" "$DATA_REPO/topics/$topic_name"
        fi
    done
fi

# GitHub项目库
rm -rf "$DATA_REPO/github-projects"
cp -rf "$HERMES_HOME/github-memory" "$DATA_REPO/github-projects" 2>/dev/null || true

# 日报（只含最终报告）
cp -f "$HERMES_HOME/ai-daily-report/shared/reports/daily/"*.md "$DATA_REPO/reports/daily/" 2>/dev/null || true

# Git操作
cd "$DATA_REPO"
CHANGES=$(git status --short | wc -l)
if [ "$CHANGES" -gt 0 ]; then
    git add -A
    git commit -m "$COMMIT_MSG"
    git push origin main
    echo "  hermes-data: pushed $CHANGES changes"
else
    echo "  hermes-data: no changes"
fi

# ==========================================
# 2. 同步 hermes-skills data/ 子目录
# ==========================================
SKILLS_REPO="$HERMES_HOME/skills"

echo "[2/2] Syncing hermes-skills/data/..."

cd "$SKILLS_REPO"

# 更新data子目录
mkdir -p data/sources
mkdir -p data/topics/ai4science
mkdir -p data/topics/ontology-special
mkdir -p data/github-projects

# 信息源
cp -f "$HERMES_HOME/sources/registry.json" data/sources/legacy-registry.json 2>/dev/null || true
cp -f "$HERMES_HOME/ai-daily-report/shared/sources/registry.json" data/sources/daily-report-registry.json 2>/dev/null || true

# 研究主题（旧格式）
cp -f "$HERMES_HOME/sources/ai4science/articles.json" data/topics/ai4science/ 2>/dev/null || true
cp -f "$HERMES_HOME/sources/ontology-special/articles.json" data/topics/ontology-special/ 2>/dev/null || true

# 主题（新格式：已在data/topics/中，但需按类型清理普通主题的spec/）
if [ -d "data/topics" ]; then
    for topic_dir in data/topics/*/; do
        topic_name=$(basename "$topic_dir")
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
                rm -rf "$topic_dir/spec"
                echo "  📚 $topic_name (research): removed spec/ from sync"
            fi
        fi
    done
fi

# GitHub项目库
rm -rf data/github-projects
cp -rf "$HERMES_HOME/github-memory" data/github-projects 2>/dev/null || true

# Git操作
CHANGES=$(git status --short | wc -l)
if [ "$CHANGES" -gt 0 ]; then
    git add -A
    git commit -m "[evolution] data: $COMMIT_MSG"
    git push origin master
    echo "  hermes-skills: pushed $CHANGES changes"
else
    echo "  hermes-skills: no changes"
fi

echo "=== Sync Complete ==="
