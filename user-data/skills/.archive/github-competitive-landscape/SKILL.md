---
name: github-competitive-landscape
description: Multi-competitor landscape analysis for a GitHub project — compare one project against 5-10 competitors, analyze architecture evolution via CHANGELOG/code, and determine market positioning. Goes beyond pairwise comparison to ecosystem-level analysis.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Competition, Landscape, Architecture, Ecosystem, Analysis]
    capabilities:
      - multi_competitor_comparison
      - architecture_evolution_tracking
      - market_positioning_analysis
      - competitive_moat_identification
---

# GitHub Competitive Landscape Analysis

Analyze a project's competitive position within its ecosystem — not just pairwise comparison, but full landscape mapping with architecture evolution tracking.

## When to Use

- User shares an article about a GitHub project and wants to know "how does it compare?"
- Need to determine if a project has a unique moat or is "broad but shallow"
- Analyzing whether a project's architecture direction is sustainable
- Answering "are there similar tools?" or "does this space need a unified entry point?"

## Workflow

### Phase 1: Identify & Score the Source Article

1. Fetch article content (use `toutiao-article-fetcher` for Toutiao URLs)
2. Extract the GitHub repo name from the article
3. Score the article quality: Depth(35%) + Originality(30%) + Accuracy(20%) + Readability(15%)
4. Note any inaccuracies (wrong star counts, wrong feature counts, PR-like tone) — these affect trust

### Phase 2: Map the Competitive Landscape

**Batch all GitHub API calls in a single `execute_code` block** to avoid rate limits (60 req/hr unauthenticated).

```python
import urllib.request, ssl, json, base64

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def github_api(path):
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/vnd.github.v3+json"
    })
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

# Batch fetch all competitor repos
repos = ["owner/main-repo", "competitor1/repo", "competitor2/repo", ...]
for repo_name in repos:
    repo = github_api(f"/repos/{repo_name}")
    if "stargazers_count" in repo:
        print(f"📦 {repo_name} ⭐{repo['stargazers_count']} 🍴{repo['forks_count']} | {repo.get('language')} | {repo.get('license',{}).get('spdx_id','N/A')}")
        print(f"   Topics: {repo.get('topics',[])}")
        print(f"   Created: {repo.get('created_at','')[:10]} | Updated: {repo.get('updated_at','')[:10]}")
```

**Finding competitors when you don't know them all:**
- Use multiple search queries with different keyword combinations
- Search in the target project's README/topics for category keywords
- Check "similar projects" sections in READMEs
- Look at what the article mentions as alternatives

```python
queries = [
    "RAG+preprocessing+stars:>1000",
    "document+ingestion+framework+stars:>500",
    "data+pipeline+orchestration+AI+stars:>500",
]
for q in queries:
    results = github_api(f"/search/repositories?q={q}&sort=stars&order=desc&per_page=5")
    if "items" in results and results["items"]:
        for item in results["items"][:5]:
            print(f"  {item['full_name']} ⭐{item['stargazers_count']} | {item.get('description','')[:120]}")
```

### Phase 3: Architecture Evolution Analysis

This is the key differentiator — don't just compare current state, trace how the project evolved.

**3a. Read CHANGELOG.md** — reveals version-by-version architecture shifts:
```python
changelog = github_api("/repos/owner/repo/contents/CHANGELOG.md")
if "content" in changelog:
    content = base64.b64decode(changelog["content"]).decode('utf-8')
    # Extract version themes and architecture decisions
```

**3b. Read directory tree** — reveals actual code organization vs claimed architecture:
```python
tree = github_api("/repos/owner/repo/git/trees/main?recursive=1")
# Look for: plugin/, adapter/, provider/, engine/, registry/ patterns
# These reveal whether it's "vertical integration" or "plugin architecture"
```

**3c. Read base/abstract classes** — reveals the extensibility model:
```python
# Check for base.py, abc classes, plugin interfaces
content = github_api("/repos/owner/repo/contents/src/adaptors/base.py")
if "content" in content:
    code = base64.b64decode(content["content"]).decode('utf-8')
    # Look for: ABC subclasses, abstractmethod, register() patterns
```

**3d. Read ROADMAP.md** — reveals intended direction:
```python
roadmap = github_api("/repos/owner/repo/contents/ROADMAP.md")
```

### Phase 4: Competitive Moat Analysis

For each competitor, identify:
1. **What it does best** (its specialized strength)
2. **What it doesn't do** (gaps the main project fills)
3. **Architecture model** (vertical integration vs plugin/ecosystem vs orchestration layer)

Key questions to answer:
- Is the main project a **specialized tool** or an **orchestration layer**?
- Does it have a unique moat that no competitor covers?
- Is its architecture direction sustainable? (vertical integration = diminishing returns; plugin architecture = ecosystem leverage)
- What's the "WordPress moment" — when should it open up to plugins?

### Phase 5: Ecosystem Gap Analysis

Answer the meta-question: **Does this space need a unified entry point?**

Framework:
1. Map the **three layers** of the pipeline (e.g., Parse → Clean/Structure → Load/Index)
2. Identify which layers have dominant tools and which are fragmented
3. Determine if there's a "standard interface" that would enable orchestration
4. Compare with analogous ecosystems that solved this (e.g., Airflow/dbt for data engineering)
5. Identify who is best positioned to become the orchestrator

## Output Format

### Competitive Landscape Table
| Tool | ⭐ | Positioning | Coverage | Key Moat | Key Weakness |
|------|-----|------------|----------|----------|-------------|

### Architecture Evolution Timeline
- v1.x: [what it was]
- v2.x: [what changed]
- v3.x: [current direction]

### Moat Assessment
- Unique strengths no competitor has
- Risks from vertical integration vs plugin architecture

### Ecosystem Verdict
- Whether the space needs a unified entry point
- Who is best positioned to become it
- What architectural shift would be needed

## Pitfalls

- **Don't confuse "has abstract base classes" with "has plugin architecture"** — ABCs for internal code organization ≠ third-party plugin interface. Check for: plugin registration mechanism, plugin discovery, plugin isolation.
- **Don't trust article claims at face value** — verify star counts, feature counts, and architecture claims against actual GitHub data. Articles often inflate numbers.
- **Batch all GitHub API calls** — 60 req/hr unauthenticated limit. Plan all lookups upfront, execute in one `execute_code` block.
- **Search queries need experimentation** — try the project name, name+domain-keyword, name+author. First query often misses.
- **CHANGELOG is more reliable than README** — README describes aspirations; CHANGELOG reveals what actually shipped and when.
- **Star count ≠ quality** — a newer project with fewer stars may have better architecture. Look at commit velocity, contributor count, and code organization.
