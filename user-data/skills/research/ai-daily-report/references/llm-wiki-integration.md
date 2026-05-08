### llm-wiki Integration (Automated Post-Collection Pipeline)

The AI daily report uses the llm-wiki skill as its knowledge backbone. **Wiki ingest is now a mandatory step after data collection and scoring, before report generation.**

#### Pipeline: Collection → Scoring → Wiki Ingest → Report Generation

```
Phase 1: Collection (arXiv, GitHub, RSS, blogs, user articles)
    ↓
Phase 2: Quality Scoring & Filtering
    ↓
Phase 3: Wiki Ingest (NEW — automated)
    ├─ Papers with quality_score ≥ 75 → wiki ingest
    ├─ GitHub projects with stars ≥ 100 → wiki ingest
    ├─ User-shared articles with score ≥ 70 → wiki ingest
    ├─ Vendor blog articles (🔥 major) → wiki ingest
    └─ Survey/review papers → wiki ingest (always, regardless of score)
    ↓
Phase 4: Report Generation (uses wiki for cross-referencing)
    ↓
Phase 5: Wiki Update (post-report)
    ├─ Update overview.md with daily synthesis
    ├─ Create/update daily/ page
    └─ Rebuild graph if significant changes
```

#### Wiki Ingest Rules (Automated — No User Confirmation Needed)

**What gets ingested automatically:**
| Item Type | Threshold | Wiki Actions |
|-----------|-----------|-------------|
| arXiv paper | quality_score ≥ 75 | `raw/papers/` + `sources/` + entity/concept pages |
| Survey paper | ANY (always ingest) | `raw/papers/` + `sources/` + dedicated concept page |
| GitHub project | stars ≥ 100 | `sources/` + entity page |
| User-shared article | score ≥ 70 | `raw/articles/` + `sources/` + entity/concept pages |
| Vendor blog (🔥 major) | severity = 🔥 | `raw/articles/` + `sources/` |
| Vendor blog (📌 notable) | severity = 📌 | `raw/articles/` + `sources/` (only if from top-10 vendor) |

**What does NOT get ingested:**
- Papers with quality_score < 75 (unless survey)
- GitHub projects with stars < 100
- User articles with score < 70
- Routine vendor blog posts (📋 severity)
- Duplicate items (check fingerprint before ingest)

#### Wiki Ingest Implementation (execute_code)

After Phase 2 scoring, run this automated ingest:

```python
import os, json, hashlib, re
from datetime import datetime

WIKI = os.path.expanduser("~/wiki")
DATA_DIR = os.path.expanduser("~/.hermes/ai-daily-report/shared/collections/" + datetime.now().strftime('%Y-%m-%d'))

def fingerprint(title, source):
    """Generate dedup fingerprint"""
    return hashlib.sha256(f"{title}|{source}".encode()).hexdigest()[:16]

def check_duplicate(fp):
    """Check if already ingested in wiki"""
    log_path = os.path.join(WIKI, "log.md")
    if os.path.exists(log_path):
        with open(log_path) as f:
            return fp in f.read()
    return False

def ingest_paper(paper):
    """Ingest a paper into wiki"""
    fp = fingerprint(paper['title'], paper.get('arxiv_id', ''))
    if check_duplicate(fp):
        return None
    
    arxiv_id = paper.get('arxiv_id', paper.get('arxiv_id_normalized', 'unknown'))
    slug = arxiv_id.replace('/', '_')
    
    # 1. Save raw source
    raw_path = os.path.join(WIKI, "raw/papers", f"{slug}.md")
    with open(raw_path, 'w') as f:
        f.write(f"# {paper['title']}\n\n")
        f.write(f"arXiv: {arxiv_id}\n")
        f.write(f"Authors: {paper.get('authors', 'N/A')}\n")
        f.write(f"Published: {paper.get('published', 'N/A')}\n")
        f.write(f"Quality Score: {paper.get('quality_score', 'N/A')}\n\n")
        f.write(f"## Abstract\n\n{paper.get('abstract', 'N/A')}\n")
    
    # 2. Create source summary
    src_path = os.path.join(WIKI, "sources", f"paper-{slug}.md")
    with open(src_path, 'w') as f:
        f.write(f"---\ntitle: \"{paper['title']}\"\ncreated: {datetime.now().strftime('%Y-%m-%d')}\nupdated: {datetime.now().strftime('%Y-%m-%d')}\ntype: source\ntags: [paper, {paper.get('is_survey', 'no') == 'confirmed' and 'survey' or 'research'}]\nsources: [raw/papers/{slug}.md]\nfingerprint: {fp}\n---\n\n")
        f.write(f"# {paper['title']}\n\n")
        f.write(f"**arXiv:** {arxiv_id} | **Score:** {paper.get('quality_score', 'N/A')}\n\n")
        f.write(f"## Key Claims\n\n- (extracted from abstract)\n\n")
        f.write(f"## Connections\n\n- Related to: [[...]]\n\n")
    
    # 3. Log
    with open(os.path.join(WIKI, "log.md"), 'a') as f:
        f.write(f"\n## [{datetime.now().strftime('%Y-%m-%d')}] ingest | paper:{arxiv_id} ({fp})\n")
    
    return slug

def ingest_project(project):
    """Ingest a GitHub project into wiki"""
    name = project.get('full_name', project.get('name', 'unknown'))
    fp = fingerprint(name, 'github')
    if check_duplicate(fp):
        return None
    
    slug = name.replace('/', '--')
    
    # 1. Create source summary
    src_path = os.path.join(WIKI, "sources", f"project-{slug}.md")
    with open(src_path, 'w') as f:
        f.write(f"---\ntitle: \"{name}\"\ncreated: {datetime.now().strftime('%Y-%m-%d')}\nupdated: {datetime.now().strftime('%Y-%m-%d')}\ntype: source\ntags: [project, github]\nsources: []\nfingerprint: {fp}\n---\n\n")
        f.write(f"# {name}\n\n")
        f.write(f"**Stars:** {project.get('stargazers_count', project.get('stargazersCount', 0))} | **Language:** {project.get('language', 'N/A')}\n\n")
        f.write(f"## Why Notable\n\n- {project.get('description', 'N/A')}\n\n")
        f.write(f"## Connections\n\n- Related to: [[...]]\n\n")
    
    # 2. Log
    with open(os.path.join(WIKI, "log.md"), 'a') as f:
        f.write(f"\n## [{datetime.now().strftime('%Y-%m-%d')}] ingest | project:{name} ({fp})\n")
    
    return slug

def ingest_article(article):
    """Ingest a user-shared or vendor blog article into wiki"""
    title = article.get('headline', article.get('title', 'unknown'))
    source = article.get('author', article.get('source', 'unknown'))
    fp = fingerprint(title, source)
    if check_duplicate(fp):
        return None
    
    slug = re.sub(r'[^a-z0-9\u4e00-\u9fff]+', '-', title.lower())[:50].strip('-')
    
    # 1. Save raw source
    raw_path = os.path.join(WIKI, "raw/articles", f"{slug}.md")
    with open(raw_path, 'w') as f:
        f.write(f"# {title}\n\n")
        f.write(f"Author: {source}\n")
        f.write(f"URL: {article.get('url', 'N/A')}\n")
        f.write(f"Date: {article.get('datePublished', article.get('published', 'N/A'))}\n\n")
        f.write(f"## Content\n\n{article.get('body', article.get('description', 'N/A'))}\n")
    
    # 2. Create source summary
    src_path = os.path.join(WIKI, "sources", f"article-{slug}.md")
    with open(src_path, 'w') as f:
        f.write(f"---\ntitle: \"{title}\"\ncreated: {datetime.now().strftime('%Y-%m-%d')}\nupdated: {datetime.now().strftime('%Y-%m-%d')}\ntype: source\ntags: [article, {article.get('category', 'news')}]\nsources: [raw/articles/{slug}.md]\nfingerprint: {fp}\n---\n\n")
        f.write(f"# {title}\n\n")
        f.write(f"**Author:** {source} | **Score:** {article.get('quality_score', article.get('score', 'N/A'))}\n\n")
        f.write(f"## Key Claims\n\n- (extracted from article)\n\n")
        f.write(f"## Connections\n\n- Related to: [[...]]\n\n")
    
    # 3. Log
    with open(os.path.join(WIKI, "log.md"), 'a') as f:
        f.write(f"\n## [{datetime.now().strftime('%Y-%m-%d')}] ingest | article:{title[:50]} ({fp})\n")
    
    return slug

# === MAIN: Run automated ingest after collection ===
ingested = {'papers': 0, 'projects': 0, 'articles': 0, 'skipped': 0}

# Ingest papers
papers_path = os.path.join(DATA_DIR, "papers.json")
if os.path.exists(papers_path):
    with open(papers_path) as f:
        papers = json.load(f)
    for p in papers:
        score = p.get('quality_score', 0)
        is_survey = p.get('is_survey', 'no') in ('confirmed', 'likely')
        if score >= 75 or is_survey:
            result = ingest_paper(p)
            if result:
                ingested['papers'] += 1
            else:
                ingested['skipped'] += 1

# Ingest GitHub projects
gh_path = os.path.join(DATA_DIR, "github.json")
if os.path.exists(gh_path):
    with open(gh_path) as f:
        projects = json.load(f)
    for proj in projects:
        stars = proj.get('stargazers_count', proj.get('stargazersCount', 0))
        if stars >= 100:
            result = ingest_project(proj)
            if result:
                ingested['projects'] += 1
            else:
                ingested['skipped'] += 1

# Ingest vendor blog articles (major only)
blogs_path = os.path.join(DATA_DIR, "vendor_blogs.json")
if os.path.exists(blogs_path):
    with open(blogs_path) as f:
        blogs = json.load(f)
    for blog in blogs:
        if blog.get('severity') == '🔥':
            result = ingest_article(blog)
            if result:
                ingested['articles'] += 1
            else:
                ingested['skipped'] += 1

print(f"Wiki ingest complete: {ingested}")
```

#### Post-Report Wiki Update

After generating the daily report, update the wiki:

1. **Create `daily/YYYY-MM-DD.md`** — mirror of the daily report with wikilinks added
2. **Update `overview.md`** — revise the living synthesis to reflect today's developments
3. **Update `index.md`** — add any new pages created during ingest
4. **Entity/concept page creation** — For items that appear in 2+ sources or are central to one source, create dedicated entity or concept pages with cross-references
5. **Weekly graph rebuild** — On Mondays (weekly report day), rebuild `graph/graph.json` and `graph/graph.html`

#### Querying Wiki Before Report Generation

Before generating a report, query the wiki for context:

1. **Read `overview.md`** — get the current state of knowledge
2. **Search for recurring topics** — check if today's top papers/projects relate to existing wiki entities/concepts
3. **Cross-reference** — when a paper cites a project already in the wiki, link them in the report
4. **Detect trends** — if multiple sources mention the same entity/concept, it's a trend worth highlighting

This makes reports smarter over time — they build on accumulated knowledge rather than treating each day in isolation.
