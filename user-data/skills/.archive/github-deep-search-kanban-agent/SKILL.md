---
name: github-deep-search-kanban-agent
description: Search GitHub for projects combining Kanban board + AI Agent task management. Handles the challenge that this niche intersection returns many low-star repos, and applies quality thresholds.
version: 1.0
created: 2026-04-11
---

# GitHub Deep Search: Kanban + Agent Projects

## When to Use
When searching for open-source projects that combine **Kanban/看板** functionality with **AI Agent/智能体 task management**. This is a niche intersection where naive searches return many low-quality results.

## Key Lessons

### 1. Stars Threshold Matters
- User explicitly required **stars > 1000** as minimum quality bar
- Initial search with `kanban agent` returned projects with only 37-567 stars — all rejected
- Always confirm the user's quality threshold BEFORE presenting results

### 2. Search Strategy for Niche Intersections
Direct keyword search (`kanban+agent`) returns too many early-stage projects. Better approach:

**Step 1: Broad search with multiple query angles**
```
queries = [
    "kanban+stars:>1000",
    "AI+task+management+stars:>1000",
    "project+management+AI+agent+stars:>500",
    "self-hosted+kanban+stars:>5000",
    "AI+workflow+orchestration+stars:>1000",
    "agent+platform+stars:>1000",
]
```

**Step 2: Filter by stars threshold, then manually judge relevance**
- Many high-star results are pure kanban (WeKan, Planka) or pure agent frameworks (LangChain, Dify)
- Must read README to confirm BOTH capabilities exist natively

**Step 3: Deep-dive top candidates** — fetch README for each, verify:
- Is kanban a FIRST-CLASS feature (not just a sidebar)?
- Is Agent orchestration a FIRST-CLASS feature (not just API hooks)?
- Are they designed together, or bolted on after?

### 3. GitHub API Without gh CLI
When `gh` CLI is not installed, use Python urllib directly:
```python
import urllib.request, json
url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=15"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode())
```

For README content:
```python
import base64
readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
# Decode base64 content field
content = base64.b64decode(readme_data['content']).decode('utf-8', errors='replace')
```

**Note**: GitHub API has rate limits (~10 requests/min unauthenticated). Batch wisely.

### 4. Known Quality Projects (as of 2026-04)

| Project | Stars | Kanban | Agent | License | Notes |
|---------|-------|--------|-------|---------|-------|
| BloopAI/vibe-kanban | 24.8K | ✅ Native | ✅ Native | Apache-2.0 | Best fit: plan on kanban, agents execute in workspaces |
| eyaltoledano/claude-task-master | 26.5K | ❌ List only | ✅ Native | MIT+Commons | Popular but no kanban UI |
| cft0808/edict | 14.9K | ✅ Dashboard | ✅ 12 agents | MIT | Creative 三省六部 architecture, needs OpenClaw |
| makeplane/plane | 47.6K | ✅ Full | ⚠️ Added later | AGPL-3.0 | Best project management, agent is not native |

### 5. Presentation Format
Present results in:
1. Comparison table with stars, capabilities, license
2. Separate "pure kanban" projects that lack AI (to avoid confusion)
3. Deep recommendation with trade-offs
4. Always ask user which to deep-dive or deploy
