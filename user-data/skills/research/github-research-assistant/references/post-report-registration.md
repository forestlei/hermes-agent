# Post-Report GitHub Memory Registration

> Established 2026-05-05 after discovering 4 projects from daily/weekly reports were missing from github-memory, causing "search not found" issues.

## Problem

GitHub projects analyzed in daily/weekly/monthly reports were not being registered into the `~/.hermes/github-memory/` knowledge base. This caused:
- Projects discussed in reports becoming unsearchable in the topic collection
- Duplicate research effort when the same project appears in future sessions
- Incomplete topic coverage in the knowledge base

## Mandatory Registration Rule

**Any GitHub project that is recommended/featured in a report MUST be registered into github-memory.**

### Scope
- 🚀GitHub趋势 section's top picks
- 🔖用户推荐文章 with detailed project analysis
- User-shared links that receive detailed analysis
- Any project that the report highlights with a recommendation

### NOT in scope
- Projects that merely appear in raw collection data (hundreds of items)
- Projects only mentioned in passing without analysis

### Threshold
- stars ≥ 100 OR received detailed analysis (regardless of stars)

### Registration Process

```bash
# 1. Check if already registered
ls ~/.hermes/github-memory/<topic>/<owner>/<repo>/metadata.json

# 2. If not, create directory
mkdir -p ~/.hermes/github-memory/<topic>/<owner>/<repo>/

# 3. Create metadata.json
cat > ~/.hermes/github-memory/<topic>/<owner>/<repo>/metadata.json << 'EOF'
{
  "full_name": "owner/repo",
  "stars": 12345,
  "topics": ["ai", "agent"],
  "features": ["feature1", "feature2"],
  "desc": "Project description",
  "lang": "Python",
  "added_date": "2026-05-05",
  "source": "daily-report-2026-05-05",
  "feature_tags": ["tag1", "tag2"]
}
EOF

# 4. Update _index.yaml — add repo to appropriate topic's repos list

# 5. Sync
bash ~/.hermes/scripts/auto-sync-data.sh "register: owner/repo"
```

### Topic Assignment

Use existing categories when possible:
- 智能体项目 — Agent frameworks, orchestration
- AI基础设施 — Training, inference, serving
- 工具与资源 — Dev tools, utilities, awesome lists
- AI应用平台 — End-user platforms
- pptx生成 — Presentation generation
- 数据工程AI项目 — Data pipelines, ETL
- 安全与隐私 — Security, privacy, sandboxing
- AI研究 — Research papers with code
- 开发工具 — IDE extensions, CLI tools
- 开源硬件 — Hardware projects

### Cross-References

- `ai-daily-report` skill Phase 3 has the full pipeline integration for automated registration during report generation
- `github-research-assistant` skill's "Post-Report Registration" section defines the rule for manual/ad-hoc research
- Both skills enforce the same registration rules

## Historical Missed Projects (2026-05-05)

These 4 projects were found in reports but missing from github-memory:
1. **GitNexus** (35,797⭐) — GitHub activity visualization tool → 工具与资源
2. **arscontexta** (3,288⭐) — Agentic note-taking → 工具与资源
3. **awesome-codex-skills** (6,716⭐) — Codex skills collection → 工具与资源
4. **openai/skills** (18,292⭐) — OpenAI official skills → 工具与资源

All 4 were registered on 2026-05-05.
