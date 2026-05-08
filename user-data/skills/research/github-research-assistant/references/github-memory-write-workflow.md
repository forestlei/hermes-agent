# GitHub Memory Write Workflow (2026-05-06)

How to register/update projects in `~/.hermes/github-memory/` — the persistent GitHub project knowledge base.

## Directory Structure

```
~/.hermes/github-memory/
├── _index.yaml          # Master index: all repos by topic
├── _index.md            # Markdown table view (auto-generated from _index.yaml)
├── _features/
│   ├── tag-index.json   # Cross-repo feature tag index
│   └── tag-index.md     # Human-readable tag index
├── <topic>/             # e.g., 智能体项目, 工具与资源, AI基础设施
│   ├── _topic.yaml      # Per-topic metadata (optional)
│   └── <owner>/
│       └── <repo>/
│           ├── metadata.json   # Project metadata (REQUIRED)
│           ├── notes.md        # Freeform notes (optional)
│           ├── history/
│           │   ├── stars.json  # Star count time series
│           │   └── forks.json
│           └── analysis/
│               └── history/
```

## metadata.json Schema

```json
{
  "name": "repo-name",
  "owner": "owner",
  "full_name": "owner/repo",
  "url": "https://github.com/owner/repo",
  "description": "Project description from GitHub API",
  "language": "TypeScript",
  "stars": 60672,
  "forks": 5236,
  "topics": ["ai", "skills", "coding"],
  "license": "MIT",
  "visibility": "public",
  "created_at": "2026-02-03",
  "pushed_at": "2026-04-30",
  "first_seen": "2026-05-06",
  "last_updated": "2026-05-06",
  "open_issues": 15,
  "archived": false,
  "feature_tags": ["skills-ecosystem", "claude-code", "coding-agent"],
  "source": "youtube-video-2026-05-01",
  "tier": "tracking"
}
```

**Key fields**:
- `feature_tags`: Array of domain-specific tags for cross-repo search. Use kebab-case.
- `source`: Where this project was discovered (article URL, video ID, etc.)
- `tier`: "core" (P0, actively used), "recommended" (P1, evaluated positively), "tracking" (P2, monitoring)
- `first_seen` / `last_updated`: ISO date strings for tracking freshness

## Registration Workflow (Step by Step)

### 1. Check for duplicates
```bash
# Check if metadata.json already exists
find ~/.hermes/github-memory -path "*/owner/repo/metadata.json"
# Or grep _index.yaml
grep "owner/repo" ~/.hermes/github-memory/_index.yaml
```
If exists → skip or update (if stars changed significantly).

### 2. Create directory and metadata.json
```python
import json, os
from datetime import date

topic = "工具与资源"  # Choose from existing topics
owner = "mattpocock"
repo = "skills"
base = os.path.expanduser(f"~/.hermes/github-memory/{topic}/{owner}/{repo}")
os.makedirs(base, exist_ok=True)

metadata = {
    "name": repo,
    "owner": owner,
    "full_name": f"{owner}/{repo}",
    "url": f"https://github.com/{owner}/{repo}",
    "description": "Skills for Real Engineers. Straight from my .claude directory.",
    "language": "Shell",
    "stars": 60672,
    "forks": 5236,
    "topics": [],
    "license": "MIT",
    "visibility": "public",
    "created_at": "2026-02-03",
    "pushed_at": "2026-04-30",
    "first_seen": str(date.today()),
    "last_updated": str(date.today()),
    "open_issues": 15,
    "archived": False,
    "feature_tags": ["skills-ecosystem", "claude-code", "coding-agent"],
    "source": "youtube-video-2026-05-01",
    "tier": "tracking"
}

with open(os.path.join(base, "metadata.json"), "w") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)
```

### 3. Update _index.yaml
Add `- owner/repo` to the appropriate topic's `repos` list. Maintain alphabetical order within each topic.

```yaml
# In _index.yaml, under the topic:
工具与资源:
  repos:
    - ...existing...
    - mattpocock/skills    # Add in alphabetical position
```

Also update `last_updated` at the top of the file.

### 4. Update _index.md
Append a row to the markdown table in the appropriate topic section. Format:
```markdown
| N | owner/repo | ⭐stars | language | description | feature_tags |
```

### 5. Update _features/tag-index.json
Add new feature tags from the project. The tag-index maps tags → list of repos.

### 6. Run auto-sync
```bash
bash ~/.hermes/scripts/auto-sync-data.sh "register: owner/repo"
```

## Topic Categories (as of 2026-05-06)

| Topic | Description | Current Count |
|-------|-------------|---------------|
| 智能体项目 | AI agent frameworks, skills-first architectures | ~45 |
| AI基础设施 | LLM serving, training, infra | ~21 |
| 工具与资源 | Dev tools, awesome lists, skill repos | ~25 |
| AI应用平台 | End-user AI platforms | ~11 |
| pptx生成 | Presentation generation | ~12 |
| 数据工程AI项目 | Data engineering + AI | ~10 |
| 安全与隐私 | Security, sandbox, privacy | ~10 |
| AI研究 | Research repos | ~5 |
| 开发工具 | Dev tooling | ~6 |
| 开源硬件 | Open hardware | ~1 |

**When no topic fits**: Create a new topic directory and add to _index.yaml.

## Star Threshold Rules

**General projects**: ⭐≥500 to register
**Skills/skill-ecosystem projects**: ⭐≥200 to register (relaxed threshold — skills are niche but high-value)

Rationale: Skills ecosystem is extremely long-tailed. A 200⭐ skill repo may be more relevant than a 5000⭐ generic tool. The relaxed threshold captures emerging skills before they cross 500⭐.

**Promotion rule**: Projects registered at ⭐≥200 are automatically promoted to full github-memory status when they reach ⭐≥500. The daily update script should check and re-tier.

## Batch Registration Pattern

When registering multiple projects at once (e.g., from a YouTube video or article analysis):

1. **Batch fetch** via GitHub API (use Python urllib with SSL context, 0.5s sleep between calls)
2. **Dedup check** — grep all repo names against _index.yaml at once
3. **Create all metadata.json files** in a single execute_code block
4. **Update _index.yaml once** — add all new repos to their topics
5. **Update _index.md once** — append all new rows
6. **Rebuild _features/tag-index.json** — regenerate from all metadata.json files
7. **Single auto-sync** at the end

**⚠️ Rate limit management**: GitHub API unauthenticated = 60 req/hr. For 16+ repos, use the multi-fallback strategy (API → Search API → HTML scraping → browser). See SKILL.md "Multi-Fallback Strategy for Batch Repo Fetching".

## Skills Ecosystem Layer Mapping

Skills ecosystem projects map to specific Agent framework layers:

| Layer | Projects | Feature Tags |
|-------|----------|-------------|
| **L7** (人机交互) | iamzhihuix/skills-manage (1.6K⭐) | `skills-manager`, `desktop-app`, `l7-human-interaction` |
| **L5** (编排/技能) | mattpocock/skills (60K⭐), openai/skills (18K⭐), cloudflare/skills (1.4K⭐) | `skills-ecosystem`, `coding-agent`, `l5-orchestration` |
| **L2** (原语/规则) | WRITING.md conventions, agent-style rules | `writing-convention`, `agent-style`, `l2-primitives` |
| **Cross-layer** | nexu-io/open-design (27K⭐, 19 Skills), google-labs-code/design.md (11K⭐) | `design-md`, `skills-ecosystem`, `visual-identity` |

When registering skills ecosystem projects, always add both the domain tag (e.g., `skills-ecosystem`) AND the layer tag (e.g., `l5-orchestration`) to `feature_tags`.
