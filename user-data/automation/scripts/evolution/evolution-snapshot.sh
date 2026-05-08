#!/bin/bash
# Evolution Snapshot - 进化前快照
# 用途：在重要变更前创建状态快照

set -e

SKILLS_DIR="$(cd ~/.hermes/skills && pwd)"
SNAPSHOT_DIR="$SKILLS_DIR/evolution/snapshots"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "📸 Creating evolution snapshot: $TIMESTAMP"

mkdir -p "$SNAPSHOT_DIR"
SNAPSHOT_PATH="$SNAPSHOT_DIR/pre-$TIMESTAMP"
mkdir -p "$SNAPSHOT_PATH"

# 快照所有SKILL.md文件
if [ -d "$SKILLS_DIR" ]; then
  mkdir -p "$SNAPSHOT_PATH/skills"
  find "$SKILLS_DIR" -name "SKILL.md" -exec bash -c 'cp "{}" "$SNAPSHOT_PATH/skills/$(echo "{}" | sed "s|/|_|g")"' \;
  echo "  ✓ SKILL.md files"
fi

# 创建元数据
cat > "$SNAPSHOT_PATH/metadata.json" <<EOF
{
  "timestamp": "$TIMESTAMP",
  "type": "pre-evolution",
  "git_commit": "$(cd $SKILLS_DIR && git rev-parse HEAD 2>/dev/null || echo 'none')"
}
EOF

echo "✅ Snapshot created: $SNAPSHOT_PATH"
echo "$SNAPSHOT_PATH"
