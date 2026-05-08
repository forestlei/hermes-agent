---
name: github-memory-base
description: Manage GitHub memory knowledge base. Organize tracked repositories by topic, maintain project metadata, and manage the memory directory structure.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Memory, Knowledge Base, Organization]
    capabilities:
      - memory_management
      - topic_organization
      - repo_tracking_setup
      - metadata_management
---

# GitHub Memory Base

You manage a persistent GitHub memory knowledge base. Your job is to organize tracked repositories by topic, maintain project metadata, and keep the memory structure up-to-date.

## Memory Directory Structure

```
~/.hermes/github-memory/
├── _index.md                    # Master repo index (sorted by stars)
├── _index.yaml                  # Master index: topics and all tracked repos
├── _features/
│   ├── tag-index.md             # Feature tag index (human-readable, categorized)
│   └── tag-index.json           # Feature tag index (programmatic access)
├── [topic-name]/
│   ├── _topic.yaml              # Topic metadata (description, created, tags)
│   └── [repo-owner]/
│       └── [repo-name]/
│           ├── metadata.json    # Repository snapshot (includes feature_tags)
│           ├── history/
│           │   ├── stars.json   # Star count over time
│           │   ├── forks.json   # Fork count over time
│           │   └── commits.json # Commit activity over time
│           ├── analysis/
│           │   ├── latest.md    # Most recent analysis
│           │   └── history/     # Past analysis reports
│           └── notes.md         # User notes and observations
```

### Topic Categories (current — 10 topics as of 2026-05-02)

| Topic | Description |
|-------|-------------|
| 智能体项目 | AI Agent frameworks, coding agents, multi-agent systems, agent harness |
| AI基础设施 | Model training/serving, LLM inference, document processing, quantum |
| AI应用平台 | Low-code AI platforms, workflow automation, vertical apps, CMS |
| AI研究 | RL research, reward models, VLA, benchmarks, agent evaluation |
| pptx生成 | PPT/slide generation, paper-to-slides, document conversion |
| 数据工程AI项目 | Data pipelines, ETL, data integration |
| 工具与资源 | Dev tools, MCP servers, awesome lists, design resources, skills, utilities |
| 安全与隐私 | Security, privacy, sandbox, reverse proxy, telemetry blocking, agent isolation |
| 开发工具 | Terminal tools, CLI utilities, web terminal, spreadsheet, performance optimization |
| 开源硬件 | Open-source hardware design, CAD assets, industrial design |

## Core Operations

### 1. Initialize Memory Base

```bash
# Create memory directory structure
mkdir -p ~/.hermes/github-memory
mkdir -p ~/.hermes/github-memory/_history

# Create master index
cat > ~/.hermes/github-memory/_index.yaml << 'EOF'
version: 1.0
created: YYYY-MM-DD
topics: {}
EOF
```

### 2. Add Topic

```bash
# Create topic directory
mkdir -p ~/.hermes/github-memory/[topic-name]

# Create topic metadata
cat > ~/.hermes/github-memory/[topic-name]/_topic.yaml << 'EOF'
name: topic-name
description: Topic description
tags:
  - tag1
  - tag2
created: YYYY-MM-DD
repos: []
EOF
```

### 3. Add Repository to Memory

```bash
# Fetch repo data
gh repo view owner/repo --json name,description,stargazersCount,forksCount,language,topics,createdAt,pushedAt,license,defaultBranch,url,visibility,openIssuesCount,watchersCount

# Create directory structure
mkdir -p ~/.hermes/github-memory/[topic]/[owner]/[repo]/history
mkdir -p ~/.hermes/github-memory/[topic]/[owner]/[repo]/analysis/history

# Create metadata.json
cat > ~/.hermes/github-memory/[topic]/[owner]/[repo]/metadata.json << 'EOF'
{
  "name": "repo-name",
  "owner": "owner",
  "full_name": "owner/repo",
  "url": "https://github.com/owner/repo",
  "description": "...",
  "language": "...",
  "stars": X,
  "forks": Y,
  "topics": [...],
  "license": "...",
  "visibility": "public",
  "default_branch": "main",
  "created_at": "YYYY-MM-DD",
  "pushed_at": "YYYY-MM-DD",
  "first_seen": "YYYY-MM-DD",
  "last_updated": "YYYY-MM-DD",
  "open_issues": Z,
  "watchers": W
}
EOF

# Create initial history files
echo '[]' > ~/.hermes/github-memory/[topic]/[owner]/[repo]/history/stars.json
echo '[]' > ~/.hermes/github-memory/[topic]/[owner]/[repo]/history/forks.json
echo '[]' > ~/.hermes/github-memory/[topic]/[owner]/[repo]/history/commits.json

# Create notes file
cat > ~/.hermes/github-memory/[topic]/[owner]/[repo]/notes.md << 'EOF'
# Notes for owner/repo

## Why I track this project
...

## Key features to remember
...

## Related projects
...

## TODO
- [ ]
EOF

# Update master index
```

### 4. Update Repository Metadata

```bash
# Fetch latest data
gh repo view owner/repo --json stargazersCount,forksCount,pushedAt,openIssuesCount,watchersCount

# Update metadata.json (preserve original fields, update current values)
# Use jq or manual edit to update:
# - stars, forks, watchers, open_issues
# - pushed_at
# - last_updated
```

### 5. Record History Data Point

```bash
# Add star history entry
TODAY=$(date +%Y-%m-%d)
STARS=$(gh repo view owner/repo --json stargazersCount --jq '.stargazersCount')
FORKS=$(gh repo view owner/repo --json forksCount --jq '.forksCount')

# Append to stars.json (JSON array)
jq --arg date "$TODAY" --argjson stars "$STARS" '. += [{date: $date, count: $stars}]' history/stars.json > tmp.json && mv tmp.json history/stars.json

# Append to forks.json
jq --arg date "$TODAY" --argjson forks "$FORKS" '. += [{date: $date, count: $forks}]' history/forks.json > tmp.json && mv tmp.json history/forks.json

# Record commit activity
COMMITS_THIS_MONTH=$(gh api repos/owner/repo/commits?per_page=100 --since=$(date -d "30 days ago" +%Y-%m-%d) --paginate --slurp -q 'length')
jq --arg date "$TODAY" --argjson commits "$COMMITS_THIS_MONTH" '. += [{date: $date, count: $commits}]' history/commits.json > tmp.json && mv tmp.json history/commits.json
```

### 6. List All Tracked Repos

```bash
# List by topic
find ~/.hermes/github-memory -name "metadata.json" | while read f; do
  echo "$(dirname $f | sed 's|.*github-memory/||')"
done

# Get summary stats
find ~/.hermes/github-memory -name "metadata.json" -exec jq -r '.full_name + " | stars:" + (.stars|tostring) + " | forks:" + (.forks|tostring)' {} \;
```

### 7. Remove Repository from Memory

```bash
# Remove repo directory
rm -rf ~/.hermes/github-memory/[topic]/[owner]/[repo]

# Update _index.yaml to remove from topics[].repos
```

### 8. Export Memory Report

```bash
# Generate markdown report of all tracked repos
cat > ~/.hermes/github-memory/_reports/tracked-repos-$(date +%Y%m%d).md << 'EOF'
# GitHub Memory Report

## Summary
- Total Topics: N
- Total Repositories: N
- Report Date: YYYY-MM-DD

## Topics

### topic-name
| Repository | Stars | Forks | Last Updated | Trend |
|------------|-------|-------|--------------|-------|
| owner/repo | X | Y | YYYY-MM-DD | 📈/📉/➡️ |

EOF
```

## Master Index Format (_index.yaml)

```yaml
version: 1.0
created: 2024-01-01
last_updated: YYYY-MM-DD
topics:
  ai-agents:
    description: AI agent frameworks and tools
    tags: [AI, Agents, LLM]
    created: 2024-01-01
    repos:
      - owner/repo-a
      - owner/repo-b
  web-frameworks:
    description: Web application frameworks
    tags: [Web, Frontend, Backend]
    created: 2024-01-01
    repos:
      - owner/repo-c
```

## Workflow: Adding a New Repository

1. **Identify topic** - Does a topic exist? If not, create one
2. **Verify not already tracked** - Check `_index.yaml` and `find ~/.hermes/github-memory -name 'metadata.json'`
3. **Fetch initial data** - Use GitHub API with authentication token from env config
4. **Create directory structure** - `mkdir -p ~/.hermes/github-memory/[topic]/[owner]/[repo]/{analysis,history}`
5. **Create metadata.json** - Include `feature_tags` array for functional capabilities
6. **Generate analysis/latest.md** - Auto-generate from API data (basic info table + description + feature tags + use cases + related projects)
7. **Generate notes.md** - Auto-generate with why-track section, key features, related projects, TODO
8. **Update `_index.yaml`** - Add to topic's repos list
9. **Rebuild feature tag index** - Run tag index rebuild (see below)

## Workflow: Auto-Complete Missing Analysis

When repos exist in github-memory but lack analysis/latest.md or notes.md:

1. **Find incomplete repos**: scan for metadata.json files whose parent directory lacks analysis/latest.md
2. **Read metadata.json** for each incomplete repo
3. **Generate analysis/latest.md** using template:
   - Basic info table (repo, language, stars, forks, license, dates, topic)
   - Project description from GitHub
   - Feature tags (from metadata.json `feature_tags` field)
   - Core capabilities (bulleted list from feature_tags)
   - Use cases (based on topic category)
   - Related projects (based on topic category)
   - Activity status (based on pushed_at date)
4. **Generate notes.md** using template:
   - Why track (based on star count tier + description)
   - Key features (from feature_tags)
   - Related projects
   - Usage experience (placeholder)
   - TODO checklist

## Workflow: Feature Tag Index

The feature tag index enables searching projects by functional capability.

### Rebuild Index

Collect all feature_tags from metadata.json files, build tag → [{full_name, stars, language, topic}] mapping, then write to _features/tag-index.md (categorized, human-readable) and _features/tag-index.json (programmatic access), plus _index.md (all repos sorted by stars).

### Search by Feature Tag

Query the JSON index at `~/.hermes/github-memory/_features/tag-index.json` — each key is a tag, value is an array of repo objects with full_name, stars, language, topic.

### Feature Tag Categories

Tags are organized into categories for the index:
- **AI智能体**: agent-framework, multi-agent, autonomous-agent, coding-agent, browser-automation, etc.
- **LLM/模型**: llm-framework, llm-inference, llm-finetuning, rag, training, deep-learning, etc.
- **PPT/文档**: ppt-generation, document-conversion, pdf-parsing, paper-to-slides, etc.
- **数据/管道**: data-pipeline, etl, data-integration, vector-database, etc.
- **工作流/平台**: workflow-engine, low-code, agent-builder, visual-programming, etc.
- **研究/评测**: rl-rewards, reasoning, sparse-attention, vision-language-action, etc.
- **工具/资源**: mcp-server, code-analysis, knowledge-graph, awesome-list, etc.
- **图像/视频**: stable-diffusion, image-generation, deepfake, etc.
- **金融/垂直**: financial-data, autonomous-driving, career-agent, etc.

## References
- `references/sandbox-landscape-2026-05.md` — AI agent sandbox landscape analysis (E2B/Daytona/Sandcastle/gVisor/Wasmtime etc.), verified star counts, operation coverage scores, standardization gap analysis

## ⚠️ Data Quality: metadata.json Schema Consistency

Some repos were registered with `repo` field instead of `full_name` (legacy format). When scanning metadata.json files:
- Always check for BOTH `meta.get("full_name")` and `meta.get("repo")` — use `full_name` if present, fall back to `repo`
- If a repo has `repo` but not `full_name`, auto-fix by adding `full_name = repo` and writing back
- Known legacy-format repos: `ultraworkers/claw-code`, `openclaw/openclaw`, `nullclaw/nullclaw`
- The index rebuild code should use: `name = meta.get("full_name", meta.get("repo", "unknown"))`

## Workflow: Batch Registration from External Source (YouTube/Toutiao/arXiv)

When analyzing a batch of GitHub projects from an external source (YouTube video, article, paper):

1. **Define batch list** — `new_repos` with full_name, target topic, feature_tags for each
2. **Batch fetch metadata** — Use GitHub API with rate-limit fallback (see `toutiao-article-fetcher/references/github-batch-fetch-strategy.md`)
3. **Create metadata.json** for each repo under `~/.hermes/github-memory/{topic}/{owner}/{repo}/`
   - Include: full_name, description, stars, forks, language, license, topics, tracked_topics, feature_tags, added_date, source
   - `source` field tracks where the project was discovered (e.g., "youtube-video-2026-05-02")
4. **Rebuild all 3 indexes** after registration:
   - `_index.yaml` — master index with topics, repos sorted by stars
   - `_features/tag-index.json` — feature tag → repos mapping
   - `_index.md` — flat list of all repos sorted by stars
5. **Run git sync** — `bash ~/.hermes/scripts/auto-sync-data.sh [commit_msg]`

### Topic Assignment Rules
- Match project to existing topic by description keywords + feature_tags
- If no existing topic fits well, create a new topic directory
- Minimum viable topic: 3+ repos (avoid singletons unless clearly distinct)
- When a new topic has <3 repos, check if existing repos should be moved in from other topics

### ⚠️ Deduplication Before Adding (Critical)
Before creating any new repo entry, **always** scan existing metadata.json files for the same `full_name`. A repo can accidentally be added to multiple topics (e.g., nexu-io/open-design was once added to both 工具与资源 and AI应用平台). Steps:
1. Build `existing_repos` set by walking all metadata.json files and collecting `full_name` (and `repo` as fallback)
2. For each new repo, check `if full_name in existing_repos: skip`
3. If a repo should change topics, move the directory rather than creating a duplicate
4. After batch registration, verify no duplicates with: `find ~/.hermes/github-memory -name metadata.json -exec jq -r '.full_name' {} \; | sort | uniq -d`

### Feature Tag Assignment
- Use existing tags from `_features/tag-index.json` when possible
- New tags should follow kebab-case convention
- Aim for 3-5 tags per repo — enough for searchability, not so many as to dilute

## Three-Dimensional Topic Architecture

The user's topic system has **three dimensions**. GitHub Memory is only one of them. When the user asks about "topics" or "themes", you MUST understand which dimension(s) they mean:

### Dimension 1: Four Permanent Topics (永久话题, Home Base)
Never decay, never archive. Root containers for all content:

| Topic | Scope |
|-------|-------|
| 🧠 知识体系 | llm-wiki, fact-check, source-evolution |
| 📰 信息收集 | RSS + Toutiao + WeChat + cron collection |
| 🔬 AI前沿追踪 | arxiv + GitHub trending + AI daily report |
| 🛠️ 技能体系 | persistent-solver + new skill discovery |

### Dimension 2: Four Work Topics (工作主题, Work Topics)
Deliverable projects with formal records. Full sync to GitHub.

| Topic | Boundary | Status |
|-------|----------|--------|
| 🔧 agent-framework | Agent architecture, tool orchestration, multi-platform gateway, skills, API | 🟢 Active |
| 🔧 news-insight | Full pipeline: collection → provenance → credibility → recommendation → dedup | 🟢 Active |
| 🔧 patent-intelligence | Patent search/analysis/similarity/infringement/valuation, CNIPA+USPTO+EPO | 🟢 Active |
| 🔧 pptx-gen | PPTX generation, conversion, charts, animation, template engine, format interop | 🟢 Active |

Plus 2 archived research topics: ai4science (🟡), ontology-special (🟡)

Work topics live at `~/.hermes/skills/data/topics/{name}/` with README.md + metadata.json + spec/ + reports/ + adr/

### Integration Pattern: Analysis Reports → Work Topic spec/

When a deep analysis report is produced about repos in a topic (e.g., sandbox analysis for agent-framework):

1. **Create `spec/<sub-topic>/` directory** under the work topic (e.g., `topics/agent-framework/spec/sandbox/`)
2. **Place the full report** as `spec/<sub-topic>/<topic>-analysis.md`
3. **Create a README.md** in the same directory with a concise knowledge index (core skeleton, not the full report)
4. **Create a `<topic>-projects.md`** linking to GitHub Memory repos with ⭐/language/mechanism table
5. **Update the work topic's metadata.json** — add the sub-topic to `sub_projects` array
6. **Update the work topic's README.md** — add entry to spec index table + work log

This pattern keeps the full analysis accessible while providing quick-entry points for future sessions.

### Dimension 3: GitHub Memory (10 topics, 142 projects)
Tracked GitHub repos organized by functional category. This is what THIS skill manages.

### Relationship
```
Permanent Topics (WHY) → Work Topics (WHAT) → GitHub Memory (WITH WHAT)
```
Example: "AI前沿追踪" → "news-insight" → "智能体项目" topic's specific repos

### Pitfall
When the user asks "what are the topics?" or "list all themes", they may mean ANY of the three dimensions — or all of them. Always clarify or show all three. Do NOT assume they only mean GitHub Memory topics.

For full topic system documentation including sync rules and granularity, see `references/topic-system-architecture.md`.

## ⚠️ Detail Level for Topic Listings (User Preference)

When the user asks to "list topics" or "show all themes", they expect **FULL detailed content per topic** — not a summary table or overview. The user explicitly corrected this twice: "你要你列出主题的详细内容，你不要回答的那么敷衍". A proper topic listing MUST include:

- Every topic: description, tag list, project count, total stars
- Every project within each topic: full_name, stars, language, description, feature_tags
- Cross-references to related topics and skills
- Do NOT truncate or summarize project lists — show ALL projects

Superficial summaries (just topic names + counts) are NOT acceptable for this class of request.

## Important Notes

- Always use `YYYY-MM-DD` for all dates
- Store raw numbers (not formatted like "1.2k") in JSON
- Keep metadata.json in sync when fetching updates
- Maintain backup of `_index.yaml` before bulk operations
- Use authenticated GitHub API calls to avoid rate limits (token available in env config)
- Store data in `~/.hermes/github-memory/` NOT in project directory
- **Always include `feature_tags` in metadata.json** — this powers the tag index
- **After adding/removing repos, rebuild the feature tag index**
- **When writing files via execute_code sandbox, use base64 encoding for content with special characters** — direct write_file may fail for some paths; use base64 pipe via terminal instead
- **GitHub API rate limit fallback strategy** (no auth token = 60 req/hr):
  - Tier 1: Core REST API `api.github.com/repos/{owner}/{repo}` (primary, 60/hr bucket)
  - Tier 2: Search API `api.github.com/search/repositories?q=repo:owner/repo` (separate rate limit bucket, 10 req/min)
  - Tier 3: Browser snapshot — navigate to `github.com/{owner}/{repo}` and extract info from page HTML
  - When Tier 1 returns 403, immediately switch to Tier 2; when Tier 2 also exhausted, use Tier 3
  - Batch fetch pattern: loop with **0.5-0.6s delay** in `execute_code`, catch 403s, retry failed repos via Tier 2/3
  - ⚠️ **Rate limit hits fast**: 20+ repos in one loop will exhaust Tier 1 within ~30s. For batches >15 repos, consider splitting into 2 `execute_code` calls with a pause between, or accept partial results and note which repos need retry
  - ⚠️ **jq parsing fails silently**: `curl | jq` can return empty output on rate-limit HTML responses, causing `json.loads` to throw `Expecting value`. Always use `curl -s` + `json.loads` directly, NOT piped through jq
  - See also: `toutiao-article-fetcher/references/github-batch-fetch-strategy.md`
- **Metadata.json must include `source` field** tracking where the project was discovered (e.g., "youtube-video-2026-05-02", "toutiao-article")
- **Metadata field inconsistency**: some older repos use `repo` instead of `full_name`. When scanning metadata, always check both: `meta.get("full_name", meta.get("repo", "unknown"))`. When creating new entries, always use `full_name`.
- **_topic.yaml multi-document issue**: some `_topic.yaml` files contain multiple YAML documents separated by `---`, which causes `yaml.safe_load()` to throw `ComposerError`. Use `yaml.safe_load_all()` and take the first document, or parse manually with string splitting.
- **curl + jq pipe can silently fail**: `curl -s URL | jq '.field'` returns empty string when API response is unexpected, causing downstream `json.loads("")` to fail. Prefer raw `curl -s URL` and parse the full JSON in Python, only using jq for quick terminal checks.
- **Index rebuild must handle mixed metadata schemas**: when iterating all metadata.json files, guard against missing keys (`full_name`, `feature_tags`, `tracked_topics`) with `.get()` defaults.
