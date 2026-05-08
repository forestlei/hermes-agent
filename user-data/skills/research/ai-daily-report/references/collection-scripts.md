### Phase 1: Data Collection (run daily)

Collect fresh data from all enabled sources. This is the "information monitoring" step.

```bash
TODAY=$(date +%Y-%m-%d)
DATA_DIR=~/.hermes/ai-daily-report/shared/collections/$TODAY
mkdir -p "$DATA_DIR"

# 1. Collect arXiv papers (latest in key categories)
# Use the arxiv skill's API patterns
curl -s "https://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.LG&sortBy=submittedDate&sortOrder=descending&max_results=50" | python3 -c "
import sys, xml.etree.ElementTree as ET, json
ns = {'a': 'http://www.w3.org/2005/Atom'}
root = ET.parse(sys.stdin).getroot()
papers = []
for entry in root.findall('a:entry', ns):
    arxiv_id = entry.find('a:id', ns).text.strip().split('/abs/')[-1]
    title = entry.find('a:title', ns).text.strip().replace('\n', ' ')
    published = entry.find('a:published', ns).text[:10]
    authors = ', '.join(a.find('a:name', ns).text for a in entry.findall('a:author', ns))
    summary = entry.find('a:summary', ns).text.strip()[:300]
    cats = [c.get('term') for c in entry.findall('a:category', ns)]
    papers.append({
        'arxiv_id': arxiv_id, 'title': title, 'published': published,
        'authors': authors, 'abstract': summary, 'categories': cats,
        'source': 'arxiv', 'collected_at': '$TODAY'
    })
json.dump(papers, open('$DATA_DIR/papers.json', 'w'), indent=2, ensure_ascii=False)
print(f'Collected {len(papers)} papers')
"

# 2. Collect HuggingFace Daily Papers (community-curated, with upvotes)
python3 << 'PYEOF'
import urllib.request, ssl, json, os
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {"User-Agent": "Mozilla/5.0"}
url = "https://huggingface.co/api/daily_papers"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
    data = json.loads(resp.read().decode('utf-8'))
# Filter to recent papers (last 7 days)
from datetime import datetime, timedelta
cutoff = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d')
hf_papers = []
for item in data:
    pub_date = item.get('publishedAt', '')[:10]
    if pub_date >= cutoff:
        paper = item.get('paper', {})
        hf_papers.append({
            'arxiv_id': paper.get('id', ''),
            'title': paper.get('title', ''),
            'published': pub_date,
            'authors': ', '.join(a.get('name', '') for a in paper.get('authors', [])[:5]),
            'abstract': paper.get('ai_summary', item.get('summary', ''))[:500],
            'categories': paper.get('ai_keywords', [])[:5],
            'upvotes': paper.get('upvotes', 0),
            'hf_comments': item.get('numComments', 0),
            'source': 'huggingface',
            'collected_at': os.environ.get('TODAY', '')
        })
hf_papers.sort(key=lambda x: x['upvotes'], reverse=True)
out_dir = os.environ.get('DATA_DIR', '.')
with open(os.path.join(out_dir, 'hf_papers.json'), 'w') as f:
    json.dump(hf_papers, f, indent=2, ensure_ascii=False)
print(f'Collected {len(hf_papers)} HF Daily Papers (last 7 days)')
PYEOF

# 3. Collect vendor blog RSS feeds (major AI announcements)
python3 << 'PYEOF'
import urllib.request, ssl, json, xml.etree.ElementTree as ET, os
from datetime import datetime, timedelta

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {"User-Agent": "Mozilla/5.0"}

BLOG_FEEDS = {
    "openai": "https://openai.com/blog/rss.xml",
    "deepmind": "https://deepmind.google/blog/feed/",
    "google-research": "https://research.google/blog/rss/",
    "huggingface": "https://huggingface.co/blog/feed.xml",
    "microsoft-research": "https://www.microsoft.com/en-us/research/feed/",
    "nvidia": "https://developer.nvidia.com/blog/feed/",
}

cutoff = (datetime.utcnow() - timedelta(days=3)).strftime('%Y-%m-%d')
all_articles = []

for source, feed_url in BLOG_FEEDS.items():
    try:
        req = urllib.request.Request(feed_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            raw = resp.read().decode('utf-8')
        root = ET.fromstring(raw)
        items = root.findall('.//item')
        for item in items:
            title = item.findtext('title', '').strip()
            pub_date = item.findtext('pubDate', '')
            link = item.findtext('link', '')
            desc = item.findtext('description', '')[:300]
            # Parse date
            try:
                dt = datetime.strptime(pub_date[:25], '%a, %d %b %Y %H:%M:%S')
                date_str = dt.strftime('%Y-%m-%d')
            except:
                date_str = pub_date[:10]
            if date_str >= cutoff:
                all_articles.append({
                    'source': source,
                    'title': title,
                    'url': link,
                    'published': date_str,
                    'description': desc,
                    'severity': '🔥' if any(kw in title.lower() for kw in ['release', 'launch', 'announce', 'gpt', 'claude', 'gemini', 'llama', 'model']) else '📌'
                })
    except Exception as e:
        print(f"⚠️ {source}: {str(e)[:60]}")

all_articles.sort(key=lambda x: x['published'], reverse=True)
out_dir = os.environ.get('DATA_DIR', '.')
with open(os.path.join(out_dir, 'vendor_blogs.json'), 'w') as f:
    json.dump(all_articles, f, indent=2, ensure_ascii=False)
print(f'Collected {len(all_articles)} vendor blog articles (last 3 days)')
PYEOF

# 4. Collect GitHub trending projects
# Method A: gh CLI (if available)
gh search repos --language=python --stars=>50 --updated=>$(date -d '7 days ago' +%Y-%m-%d) --sort=stars --limit=30 --json name,description,stargazersCount,url,topics > "$DATA_DIR/github.json"

# Method B: GitHub API topic search (proven effective — 246 unique repos from 10 topics on 2026-05-03)
# Uses created:>DATE filter to focus on new projects with high growth rate
# NOTE: Unauthenticated GitHub API = 10 req/min. Use 12-15s delays between topic queries.
# Most important topics listed FIRST so they're collected before rate limit hits.
python3 << 'PYEOF'
import urllib.request, json, os, time
from datetime import datetime, timedelta

date_filter = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
topics = ["ai", "llm", "machine-learning", "deep-learning", "nlp", 
          "computer-vision", "transformer", "diffusion", "reinforcement-learning", "rag"]

seen_repos = set()
all_projects = []
for i, topic in enumerate(topics):
    try:
        q = urllib.request.quote(f"created:>{date_filter} topic:{topic} sort:stars-desc")
        url = f"https://api.github.com/search/repositories?q={q}&per_page=30"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github.v3+json"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        for repo in data.get("items", []):
            full_name = repo.get("full_name", "")
            if full_name not in seen_repos:
                seen_repos.add(full_name)
                all_projects.append({
                    "full_name": full_name,
                    "description": repo.get("description", ""),
                    "stargazers_count": repo.get("stargazers_count", 0),
                    "forks_count": repo.get("forks_count", 0),
                    "language": repo.get("language", ""),
                    "topics": repo.get("topics", []),
                    "created_at": repo.get("created_at", ""),
                    "html_url": repo.get("html_url", ""),
                    "source_query": topic
                })
        print(f"  {topic}: {len(data.get('items', []))} results")
        # 13s delay to stay under 10 req/min unauthenticated limit
        if i < len(topics) - 1:
            time.sleep(13)
    except Exception as e:
        if '403' in str(e):
            print(f"  {topic}: RATE LIMITED, stopping")
            break
        print(f"  ⚠️ {topic}: {str(e)[:60]}")

out_dir = os.environ.get('DATA_DIR', '.')
with open(os.path.join(out_dir, 'github_ai.json'), 'w') as f:
    json.dump(all_projects, f, indent=2, ensure_ascii=False)
print(f'Collected {len(all_projects)} GitHub AI projects from {len(topics)} topic queries')
PYEOF

# 5. Scan blogwatcher feeds for new articles
blogwatcher-cli scan 2>/dev/null
blogwatcher-cli articles --all --category "AI" 2>/dev/null > "$DATA_DIR/feeds-ai.txt" || true
blogwatcher-cli articles --all 2>/dev/null > "$DATA_DIR/feeds-all.txt" || true

# 6. Collect from tracked repos (github-tracker memory)
if [ -d ~/.hermes/github-memory ]; then
    find ~/.hermes/github-memory -name "metadata.json" -exec jq -r '{full_name, stars: .stargazersCount, updated: .pushedAt}' {} \; > "$DATA_DIR/tracked-repos.jsonl" 2>/dev/null || true
fi
```

**Important:** All collection data goes to `shared/collections/` so it's accessible to all users and report generation.


### Phase 2: Quality Filtering & Scoring

After collection, filter and score each item:

1. **Paper scoring** — based on Semantic Scholar citation velocity, author reputation, topic relevance, AND HuggingFace upvotes
2. **GitHub project scoring** — based on Heat Score algorithm from github-tracker skill
3. **News/article scoring** — based on source quality score × content depth × timeliness
4. **Paper merge** — arXiv papers and HuggingFace Daily Papers are merged by arXiv ID; HF upvotes boost quality score

```bash
# Score papers using Semantic Scholar citation data
python3 << 'PYEOF'
import json, urllib.request, sys

with open("$DATA_DIR/papers.json") as f:
    papers = json.load(f)

scored = []
for paper in papers[:30]:  # Rate limit: be selective
    arxiv_id = paper["arxiv_id"]
    try:
        url = f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{arxiv_id}?fields=citationCount,influentialCitationCount,year"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            citations = data.get("citationCount", 0)
            influential = data.get("influentialCitationCount", 0)
            # Score: base 50 + citation bonus (capped at 50)
            score = min(50, citations) + min(30, influential * 5) + 20  # 20 base for arXiv recency
            paper["citation_count"] = citations
            paper["influential_citations"] = influential
            paper["quality_score"] = min(100, score)
    except Exception:
        paper["quality_score"] = 50  # Default for new papers without citation data

# Open-source code bonus: +10 if paper has GitHub/code link
for paper in scored:
    abstract = paper.get("abstract", "")
    comments = paper.get("comments", "")
    # Check for GitHub links in abstract or comments
    import re
    github_pattern = r'https?://github\.com/[\w\-]+/[\w\-]+'
    code_pattern = r'(?:code|source|implementation|repo)[:\s]*(https?://\S+)'
    github_match = re.search(github_pattern, abstract + " " + comments)
    code_match = re.search(code_pattern, abstract + " " + comments, re.IGNORECASE)
    if github_match:
        paper["github_url"] = github_match.group(0)
        paper["quality_score"] = min(100, paper.get("quality_score", 50) + 10)
        paper["has_code"] = True
    elif code_match:
        paper["code_url"] = code_match.group(1)
        paper["quality_score"] = min(100, paper.get("quality_score", 50) + 10)
        paper["has_code"] = True
    scored.append(paper)

# Sort by quality score descending
scored.sort(key=lambda x: x["quality_score"], reverse=True)

with open("$DATA_DIR/papers.json", "w") as f:
    json.dump(scored, f, indent=2, ensure_ascii=False)

print(f"Scored {len(scored)} papers, top: {scored[0]['title'][:60] if scored else 'none'}")
PYEOF
```


### Phase 3: Store High-Value Items

Papers and projects exceeding quality thresholds are stored for deep analysis:

```bash
# Store top papers (quality_score >= 75)
python3 << 'PYEOF'
import json, os
from pathlib import Path

with open("$DATA_DIR/papers.json") as f:
    papers = json.load(f)

PAPERS_DIR = Path("~/.hermes/ai-daily-report/shared/papers").expanduser()
stored = 0
for paper in papers:
    if paper.get("quality_score", 0) >= 75:
        paper_dir = PAPERS_DIR / paper["arxiv_id"].replace("/", "_")
        paper_dir.mkdir(parents=True, exist_ok=True)
        # Save metadata
        with open(paper_dir / "metadata.json", "w") as f:
            json.dump(paper, f, indent=2, ensure_ascii=False)
        # Create summary template
        if not (paper_dir / "summary.md").exists():
            with open(paper_dir / "summary.md", "w") as f:
                f.write(f"# {paper['title']}\n\n")
                f.write(f"**arXiv:** {paper['arxiv_id']}\n")
                f.write(f"**Authors:** {paper['authors']}\n")
                f.write(f"**Published:** {paper['published']}\n")
                f.write(f"**Quality Score:** {paper.get('quality_score', 'N/A')}\n\n")
                f.write(f"## Abstract\n\n{paper['abstract']}\n\n")
                f.write(f"## Key Contributions\n\n<!-- To be filled by agent -->\n\n")
                f.write(f"## Relevance\n\n<!-- To be filled by agent -->\n")
        stored += 1

print(f"Stored {stored} high-quality papers for deep analysis")
PYEOF

# Store hot GitHub projects (stars > 100 AND recent activity)
python3 << 'PYEOF'
import json, os
from pathlib import Path

with open("$DATA_DIR/github.json") as f:
    projects = json.load(f)

PROJECTS_DIR = Path("~/.hermes/ai-daily-report/shared/projects").expanduser()
stored = 0
for proj in projects:
    stars = proj.get("stargazersCount", 0)
    if stars >= 100:
        name = proj.get("name", "unknown")
        owner = proj.get("url", "").split("/")[-2] if "/" in proj.get("url", "") else "unknown"
        proj_dir = PROJECTS_DIR / f"{owner}--{name}"
        proj_dir.mkdir(parents=True, exist_ok=True)
        with open(proj_dir / "metadata.json", "w") as f:
            json.dump(proj, f, indent=2, ensure_ascii=False)
        if not (proj_dir / "summary.md").exists():
            with open(proj_dir / "summary.md", "w") as f:
                f.write(f"# {owner}/{name}\n\n")
                f.write(f"**URL:** {proj.get('url', 'N/A')}\n")
                f.write(f"**Stars:** {stars}\n")
                f.write(f"**Description:** {proj.get('description', 'N/A')}\n\n")
                f.write(f"## Why Notable\n\n<!-- To be filled by agent -->\n\n")
                f.write(f"## Key Features\n\n<!-- To be filled by agent -->\n")
        stored += 1

print(f"Stored {stored} hot GitHub projects for deep analysis")
PYEOF
```

### Phase 1b: Chinese AI Sources Collection (国内信息源采集)

**Problem solved**: 国内动态不再只依赖量子位，从9个RSS源 + 2个HTML解析源 + HF中文过滤采集。

```python
# === CHINESE AI SOURCES COLLECTION ===
# Run after Phase 1, saves to $DATA_DIR/cn_news.json
import urllib.request, ssl, json, os, re, xml.etree.ElementTree as ET
from datetime import datetime, timedelta

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

DATA_DIR = os.path.expanduser("~/.hermes/ai-daily-report/shared/collections/" + datetime.now().strftime('%Y-%m-%d'))
os.makedirs(DATA_DIR, exist_ok=True)

# AI keyword filter for Chinese content
AI_KEYWORDS = ['AI', 'ai', 'AI', '人工智能', '大模型', 'LLM', 'GPT', 'Claude', 'Gemini', 
               'DeepSeek', 'deepseek', '智能', '模型', 'Agent', 'agent', 'ChatGPT', 'OpenAI',
               '机器学习', '深度学习', '神经网络', 'Transformer', 'Qwen', '文心', '豆包',
               'Kimi', 'GLM', '智谱', '通义', 'AIGC', '多模态', 'RAG', '微调', '推理',
               '开源模型', 'API', 'Token', 'GPU', '芯片', '算力', '训练', '对齐', 'RLHF',
               'Llama', 'Llama', 'Mistral', 'Anthropic', 'Copilot', '具身智能', '人形机器人']

def is_ai_related(title, desc=""):
    text = (title + " " + desc).lower()
    return any(kw.lower() in text for kw in AI_KEYWORDS)

def parse_rss_feed(source_name, feed_url, category, quality_score, ai_filter=True):
    """Parse an RSS feed and return AI-filtered articles."""
    articles = []
    try:
        req = urllib.request.Request(feed_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            raw = resp.read().decode('utf-8', errors='ignore')
        root = ET.fromstring(raw)
        items = root.findall('.//item')
        for item in items:
            title = (item.findtext('title', '') or '').strip()
            link = (item.findtext('link', '') or '').strip()
            desc = (item.findtext('description', '') or item.findtext('content:encoded', '') or '')[:500]
            pub_date = item.findtext('pubDate', '')
            
            if not title or len(title) < 5:
                continue
            
            # Filter: only AI-related content
            if ai_filter and not is_ai_related(title, desc):
                continue
            
            articles.append({
                'source': source_name,
                'title': re.sub(r'<[^>]+>', '', title),  # Strip HTML
                'url': link,
                'published': pub_date,
                'description': re.sub(r'<[^>]+>', '', desc)[:300],
                'category': category,
                'quality_score': quality_score,
                'region': 'cn'
            })
    except Exception as e:
        print(f"  ⚠️ {source_name}: {str(e)[:60]}")
    return articles

# === RSS FEEDS (verified working) ===
RSS_SOURCES = [
    # (name, url, category, quality_score, ai_filter)
    ("极客公园AI", "https://www.geekpark.net/rss?tag=AI", "AI产业", 86, False),
    ("极客公园", "https://www.geekpark.net/rss", "AI产业", 84, True),
    ("量子位", "https://www.qbitai.com/feed", "AI科普", 85, True),
    ("AI科技评论/雷锋网", "https://www.leiphone.com/feed", "AI学术", 83, True),
    ("36氪", "https://36kr.com/feed", "AI产业", 82, True),
    ("钛媒体", "https://www.tmtpost.com/rss.xml", "AI产业", 80, True),
    ("少数派", "https://sspai.com/feed", "AI工具", 78, True),
    ("IT之家", "https://www.ithome.com/rss/", "科技资讯", 75, True),
    ("开源中国", "https://www.oschina.net/news/rss", "AI工程", 76, True),
]

all_cn_articles = []
for name, url, cat, score, ai_filter in RSS_SOURCES:
    articles = parse_rss_feed(name, url, cat, score, ai_filter)
    print(f"  {name}: {len(articles)} AI articles")
    all_cn_articles.extend(articles)

# === HTML PARSE SOURCES (vendor blogs without RSS) ===

# DeepSeek updates
# NOTE: api-docs.deepseek.com/news returns 404 as of 2026-05-03. Use /updates instead.
try:
    req = urllib.request.Request("https://api-docs.deepseek.com/updates", headers=headers)
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    # Extract update entries (date + model name pattern)
    updates = re.findall(r'Date:\s*(\d{4}-\d{2}-\d{2}).*?<h[23][^>]*>(.*?)</h[23]>', html, re.DOTALL)
    cutoff_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    for date_str, title in updates:
        title_clean = re.sub(r'<[^>]+>', '', title).strip()
        if date_str >= cutoff_date and title_clean:
            all_cn_articles.append({
                'source': 'DeepSeek官方',
                'title': title_clean,
                'url': 'https://api-docs.deepseek.com/updates',
                'published': date_str,
                'description': f'DeepSeek官方发布: {title_clean}',
                'category': '厂商动态',
                'quality_score': 95,
                'region': 'cn'
            })
    print(f"  DeepSeek官方: {len([a for a in all_cn_articles if a['source']=='DeepSeek官方'])} updates")
except Exception as e:
    print(f"  ⚠️ DeepSeek: {str(e)[:60]}")

# Qwen blog (GitHub Pages / qwen.ai)
# NOTE: Do NOT scrape https://huggingface.co/Qwen with urllib — it returns raw JSON, not clean HTML.
# Use the HF API instead for structured model data:
try:
    req = urllib.request.Request("https://huggingface.co/api/models?author=Qwen&sort=lastModified&direction=-1&limit=10", headers=headers)
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        qwen_models = json.loads(resp.read().decode('utf-8'))
    for m in qwen_models:
        model_id = m.get('id', m.get('modelId', ''))
        title = f"模型更新: Qwen/{model_id}"
        all_cn_articles.append({
            'source': 'Qwen官方',
            'title': title,
            'url': f"https://huggingface.co/{model_id}",
            'published': m.get('lastModified', '')[:10],
            'description': f"Qwen模型更新: {model_id}, Downloads: {m.get('downloads', 0)}, Likes: {m.get('likes', 0)}",
            'category': '厂商动态',
            'quality_score': 93,
            'region': 'cn'
        })
    print(f"  Qwen官方(HF API): {len(qwen_models)} model updates")
except Exception as e:
    print(f"  ⚠️ Qwen: {str(e)[:60]}")

# === HuggingFace Blog Chinese Vendor Filter ===
try:
    req = urllib.request.Request("https://huggingface.co/blog/feed.xml", headers=headers)
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        raw = resp.read().decode('utf-8')
    root = ET.fromstring(raw)
    CN_VENDOR_KEYWORDS = ['Qwen', 'DeepSeek', 'ChatGLM', 'GLM', 'Yi-', 'Baichuan', 
                          'MiniMax', 'InternLM', 'Alibaba', 'Alibaba Cloud', 'Baidu',
                          'Zhipu', 'Moonshot', 'Kimi', 'SenseTime', 'ByteDance']
    for item in root.findall('.//item')[:50]:
        title = (item.findtext('title', '') or '').strip()
        link = (item.findtext('link', '') or '').strip()
        desc = (item.findtext('description', '') or '')[:300]
        if any(kw in title+desc for kw in CN_VENDOR_KEYWORDS):
            all_cn_articles.append({
                'source': 'HuggingFace(中文厂商)',
                'title': title,
                'url': link,
                'published': item.findtext('pubDate', ''),
                'description': re.sub(r'<[^>]+>', '', desc)[:300],
                'category': '厂商动态',
                'quality_score': 90,
                'region': 'cn'
            })
    print(f"  HuggingFace(中文厂商): {len([a for a in all_cn_articles if a['source']=='HuggingFace(中文厂商)'])} posts")
except Exception as e:
    print(f"  ⚠️ HuggingFace CN: {str(e)[:60]}")

# === Dedup by title similarity ===
def dedup_articles(articles, threshold=0.85):
    """Simple dedup: remove near-duplicate titles."""
    seen = []
    unique = []
    for a in articles:
        title_norm = re.sub(r'\s+', '', a['title'].lower())
        is_dup = False
        for s in seen:
            # Simple overlap ratio
            overlap = len(set(title_norm) & set(s)) / max(len(set(title_norm) | set(s)), 1)
            if overlap > threshold:
                is_dup = True
                break
        if not is_dup:
            seen.append(title_norm)
            unique.append(a)
    return unique

all_cn_articles = dedup_articles(all_cn_articles)

# Sort by quality_score desc, then by source diversity
all_cn_articles.sort(key=lambda x: x['quality_score'], reverse=True)

# Save
out_path = os.path.join(DATA_DIR, 'cn_news.json')
with open(out_path, 'w') as f:
    json.dump(all_cn_articles, f, indent=2, ensure_ascii=False)

# Summary
source_counts = {}
for a in all_cn_articles:
    source_counts[a['source']] = source_counts.get(a['source'], 0) + 1

print(f"\n=== Chinese AI Sources Collection Summary ===")
print(f"Total AI articles: {len(all_cn_articles)}")
for src, cnt in sorted(source_counts.items(), key=lambda x: -x[1]):
    print(f"  {src}: {cnt}")
print(f"Saved to: {out_path}")
```

**Key design decisions**:
1. **AI关键词过滤** — 36氪/IT之家等综合媒体AI占比低（5-7%），必须过滤否则噪音太大
2. **极客公园AI标签** — `?tag=AI` 参数直接获取AI分类RSS，AI占比67%，质量最高
3. **厂商HTML解析** — DeepSeek/Qwen无RSS，用正则提取更新日志/博客标题
4. **HuggingFace中文过滤** — 中国厂商常在HF首发模型，从HF blog RSS中过滤中文厂商相关
5. **去重** — 同一新闻可能被多个源报道，标题相似度>0.85去重
6. **区域标记** — 所有中文源标记`region: cn`，日报生成时可按区域分组

### Phase 1c: RSSHub Sources (需Docker实例)

**前提**：RSSHub Docker实例需在本机运行：`docker run -d --name rsshub -p 1200:1200 -e CACHE_TYPE=memory -e CACHE_EXPIRE=3600 -e ACCESS_KEY=hermes2026 --restart unless-stopped diygod/rsshub:latest`

```python
# === RSSHUB SOURCES COLLECTION ===
# Requires local RSSHub Docker on port 1200
import urllib.request, json, os, re, xml.etree.ElementTree as ET

DATA_DIR = os.path.expanduser("~/.hermes/ai-daily-report/shared/collections/" + datetime.now().strftime('%Y-%m-%d'))
os.makedirs(DATA_DIR, exist_ok=True)

RSSHUB_KEY = "hermes2026"
RSSHUB_BASE = "http://localhost:1200"

headers = {"User-Agent": "Mozilla/5.0"}

# Test RSSHub availability (container may be running but routes return 503)
rsshub_available = False
try:
    req = urllib.request.Request(f"{RSSHUB_BASE}/", headers=headers)
    with urllib.request.urlopen(req, timeout=5) as resp:
        if resp.status == 200:
            # Container up, but test a route too (503 pattern during off-peak)
            try:
                test_req = urllib.request.Request(f"{RSSHUB_BASE}/huggingface/blog", headers=headers)
                with urllib.request.urlopen(test_req, timeout=10) as test_resp:
                    rsshub_available = test_resp.status == 200
            except:
                rsshub_available = False  # Container up but routes returning 503
except:
    pass

if not rsshub_available:
    print("⚠️ RSSHub not available on localhost:1200, skipping RSSHub sources")
else:
    RSSHUB_FEEDS = [
        # (name, path, category, quality_score, ai_filter)
        ("36氪AI频道(RSSHub)", f"/36kr/information/AI?key={RSSHUB_KEY}", "AI产业", 86, False),
        ("36氪快讯(RSSHub)", f"/36kr/newsflashes?key={RSSHUB_KEY}", "AI产业", 80, True),
        ("HuggingFace博客(RSSHub)", f"/huggingface/blog?key={RSSHUB_KEY}", "厂商动态", 90, False),
    ]

    rsshub_articles = []
    for name, path, cat, score, ai_filter in RSSHUB_FEEDS:
        try:
            url = f"{RSSHUB_BASE}{path}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode('utf-8')
            root = ET.fromstring(raw)
            items = root.findall('.//item')
            for item in items:
                title = (item.findtext('title', '') or '').strip()
                link = (item.findtext('link', '') or '').strip()
                desc = (item.findtext('description', '') or '')[:300]
                pub_date = item.findtext('pubDate', '')
                if not title or len(title) < 5:
                    continue
                if ai_filter and not is_ai_related(title, desc):
                    continue
                rsshub_articles.append({
                    'source': name,
                    'title': re.sub(r'<[^>]+>', '', title),
                    'url': link,
                    'published': pub_date,
                    'description': re.sub(r'<[^>]+>', '', desc)[:300],
                    'category': cat,
                    'quality_score': score,
                    'region': 'cn' if '36' in name or '氪' in name else 'en'
                })
            print(f"  {name}: {len([a for a in rsshub_articles if a['source']==name])} items")
        except Exception as e:
            print(f"  ⚠️ {name}: {str(e)[:60]}")

    # Load existing cn_news.json and merge
    cn_news_path = os.path.join(DATA_DIR, 'cn_news.json')
    if os.path.exists(cn_news_path):
        existing = json.load(open(cn_news_path))
        existing.extend(rsshub_articles)
        # Re-dedup
        existing = dedup_articles(existing)
        with open(cn_news_path, 'w') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        print(f"  Merged RSSHub articles into cn_news.json (total: {len(existing)})")
    else:
        with open(cn_news_path, 'w') as f:
            json.dump(rsshub_articles, f, indent=2, ensure_ascii=False)
        print(f"  Created cn_news.json with RSSHub articles ({len(rsshub_articles)})")
```

### Phase 1d: Vendor Changelog HTML Parsing (Additional)

```python
# === VENDOR CHANGELOG PARSING (智谱/百度千帆) ===
# These vendors have structured changelog pages

# 智谱AI - new releases page
try:
    req = urllib.request.Request("https://open.bigmodel.cn/dev/api/cn/update/new-releases", headers=headers)
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    # 智谱 uses Nextra/Next.js, look for structured data
    # Extract model mentions (GLM-5.1, etc.)
    model_updates = re.findall(r'GLM-[\d.]+[A-Za-z\-]*', html)
    model_updates = list(set(model_updates))  # dedup
    for model in model_updates[:5]:
        all_cn_articles.append({
            'source': '智谱AI官方',
            'title': f'{model} 更新发布',
            'url': 'https://open.bigmodel.cn/dev/api/cn/update/new-releases',
            'published': datetime.now().strftime('%Y-%m-%d'),
            'description': f'智谱AI官方发布: {model}',
            'category': '厂商动态',
            'quality_score': 91,
            'region': 'cn'
        })
    print(f"  智谱AI官方: {len(model_updates[:5])} model updates")
except Exception as e:
    print(f"  ⚠️ 智谱AI: {str(e)[:60]}")

# 百度千帆 - update page (has JSON tree with dates)
try:
    req = urllib.request.Request("https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um1w9y59n", headers=headers)
    with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    # Extract recent dates with surrounding context
    recent = re.findall(r'"updatedAt":"(2026-\d{2}-\d{2})[^}]{0,500}?"title":"([^"]+)"', html)
    cutoff = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    baidu_count = 0
    for date_str, title in recent:
        if date_str >= cutoff and title and len(title) > 3:
            all_cn_articles.append({
                'source': '百度千帆官方',
                'title': title[:80],
                'url': 'https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um1w9y59n',
                'published': date_str,
                'description': f'百度千帆平台更新: {title[:60]}',
                'category': '厂商动态',
                'quality_score': 89,
                'region': 'cn'
            })
            baidu_count += 1
    print(f"  百度千帆官方: {baidu_count} updates (last 7 days)")
except Exception as e:
    print(f"  ⚠️ 百度千帆: {str(e)[:60]}")
```

**Key design decisions**:
1. **AI关键词过滤** — 36氪/IT之家等综合媒体AI占比低（5-7%），必须过滤否则噪音太大
2. **极客公园AI标签** — `?tag=AI` 参数直接获取AI分类RSS，AI占比67%，质量最高
3. **厂商HTML解析** — DeepSeek/Qwen无RSS，用正则提取更新日志/博客标题
4. **HuggingFace中文过滤** — 中国厂商常在HF首发模型，从HF blog RSS中过滤中文厂商相关
5. **去重** — 同一新闻可能被多个源报道，标题相似度>0.85去重
6. **区域标记** — 所有中文源标记`region: cn`，日报生成时可按区域分组
7. **RSSHub本地Docker** — 36氪AI频道/快讯/HuggingFace博客通过RSSHub获取，需Docker实例在localhost:1200运行
8. **智谱/百度千帆更新日志** — 结构化更新页面，提取模型名和更新标题
9. **RSSHub降级** — 如Docker实例不可用，跳过RSSHub源，不影响其他采集

### Phase 1e: Model Leaderboard & Pricing Collection (周报用，每周采集)

**来源**：openlm.ai（LM Arena镜像）+ artificialanalysis.ai（模型对比）

```python
# === MODEL LEADERBOARD & PRICING COLLECTION ===
# Run weekly (not daily — data changes less frequently)
# Saves to $DATA_DIR/model_leaderboard.json and $DATA_DIR/model_pricing.json

import urllib.request, ssl, json, os, re
from datetime import datetime

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

DATA_DIR = os.path.expanduser("~/.hermes/ai-daily-report/shared/collections/" + datetime.now().strftime('%Y-%m-%d'))
os.makedirs(DATA_DIR, exist_ok=True)

# --- Source 1: openlm.ai (curl-friendly, LM Arena mirror) ---
# Contains: 80+ models with Elo/Coding/Vision/AAII/MMLU-Pro/ARC-AGI/Organization/License
try:
    req = urllib.request.Request("https://openlm.ai/chatbot-arena/", headers=headers)
    with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    
    # Parse the sortable table
    table_match = re.search(r'<table class=sortable>(.*?)</table>', html, re.DOTALL)
    if table_match:
        table_html = table_match.group(1)
        rows = re.findall(r'<tr>(.*?)</tr>', table_html, re.DOTALL)
        models = []
        for row in rows:
            cells = re.findall(r'<td>(.*?)</td>', row, re.DOTALL)
            if cells and len(cells) >= 9:
                clean_cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
                models.append({
                    'model': clean_cells[1],
                    'elo': clean_cells[2],
                    'coding_elo': clean_cells[3],
                    'vision_elo': clean_cells[4],
                    'aaii': clean_cells[5],
                    'mmlu_pro': clean_cells[6],
                    'arc_agi': clean_cells[7],
                    'organization': clean_cells[8],
                    'license': clean_cells[9] if len(clean_cells) > 9 else '',
                    'open_source': '✅' in clean_cells[1] or clean_cells[9] in ['MIT', 'Apache 2.0']
                })
        
        with open(os.path.join(DATA_DIR, 'model_leaderboard.json'), 'w') as f:
            json.dump(models, f, indent=2, ensure_ascii=False)
        print(f"✅ openlm.ai: {len(models)} models with Elo/Coding/Vision/AAII scores")
    else:
        print("⚠️ openlm.ai: no table found")
except Exception as e:
    print(f"⚠️ openlm.ai: {str(e)[:80]}")

# --- Source 2: artificialanalysis.ai (needs browser_navigate, not curl) ---
# Contains: 218+ models with Intelligence/Price/Speed/Latency/Context Window
# COLLECTION METHOD: Use browser_navigate to load the page, then browser_console to extract data
# This cannot be done via curl — it's a Next.js SPA behind Cloudflare
#
# Example extraction via browser_console:
#   (() => {
#     const allRows = document.querySelectorAll('table tr');
#     const data = [];
#     for (let i = 1; i < allRows.length; i++) {
#       const cells = allRows[i].querySelectorAll('td');
#       if (cells.length >= 5) {
#         data.push({
#           model: cells[0]?.textContent.trim().substring(0, 60),
#           context: cells[1]?.textContent.trim(),
#           creator: cells[2]?.textContent.trim().replace(/\s+/g, ' ').split(' ').pop(),
#           intelligence: cells[3]?.textContent.trim(),
#           price: cells[4]?.textContent.trim(),
#           speed: cells[5]?.textContent.trim(),
#           latency: cells[6]?.textContent.trim()
#         });
#       }
#     }
#     data.sort((a, b) => (parseInt(b.intelligence) || 0) - (parseInt(a.intelligence) || 0));
#     return JSON.stringify(data);
#   })()
#
# Save result to $DATA_DIR/model_pricing.json

print("\n⚠️ artificialanalysis.ai requires browser_navigate + browser_console (manual or cron with browser toolset)")
print("   Run separately: browser_navigate → browser_console → save to model_pricing.json")
```

**周报生成时使用**：
- `model_leaderboard.json` → 生成"🏆 模型竞争格局"板块（Top 25 Elo + Coding分榜 + 中国模型排名）
- `model_pricing.json` → 生成"💰 模型API价格对比"板块（智能/价格/速度/延迟四维对比）

### Phase 1f: Industry Data Collection (月报+周报用)

**来源**：layoffs.fyi（科技裁员）+ GitHub Releases（产品更新）+ YouTube RSS（AI视频）

```python
# === INDUSTRY DATA COLLECTION ===
# Run monthly for layoffs data, weekly for product releases

import urllib.request, ssl, json, os, re, xml.etree.ElementTree as ET
from datetime import datetime

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

DATA_DIR = os.path.expanduser("~/.hermes/ai-daily-report/shared/collections/" + datetime.now().strftime('%Y-%m-%d'))
os.makedirs(DATA_DIR, exist_ok=True)

# --- Source 1: layoffs.fyi (curl can get summary stats) ---
try:
    req = urllib.request.Request("https://layoffs.fyi/", headers=headers)
    with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    
    # Extract: "92,272 tech employees laid off · 98 tech companies w/ layoffs"
    stats_match = re.search(r'([\d,]+)\s+tech employees laid off.*?(\d+)\s+tech companies', html)
    layoffs_data = {
        'collected_at': datetime.now().strftime('%Y-%m-%d'),
        'year': datetime.now().year,
        'source': 'layoffs.fyi'
    }
    if stats_match:
        layoffs_data['total_laid_off'] = int(stats_match.group(1).replace(',', ''))
        layoffs_data['company_count'] = int(stats_match.group(2))
        print(f"✅ layoffs.fyi: {layoffs_data['total_laid_off']:,} employees, {layoffs_data['company_count']} companies")
    
    with open(os.path.join(DATA_DIR, 'layoffs_summary.json'), 'w') as f:
        json.dump(layoffs_data, f, indent=2, ensure_ascii=False)
        
except Exception as e:
    print(f"⚠️ layoffs.fyi: {str(e)[:80]}")

# --- Source 2: GitHub Releases (for key AI products) ---
PRODUCT_REPOS = [
    ("openclaw", "openclaw/openclaw"),
    ("claude-code", "anthropics/claude-code"),
    ("gemini-cli", "google-gemini/gemini-cli"),
    ("hermes-agent", "nousresearch/hermes-agent"),
]

all_releases = []
for name, repo in PRODUCT_REPOS:
    try:
        url = f"https://api.github.com/repos/{repo}/releases?per_page=5"
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            releases = json.loads(resp.read().decode('utf-8'))
        
        for r in releases[:5]:
            all_releases.append({
                'product': name,
                'repo': repo,
                'tag': r.get('tag_name', ''),
                'name': r.get('name', ''),
                'published': r.get('published_at', '')[:10],
                'body': (r.get('body', '') or '')[:500],
                'url': r.get('html_url', '')
            })
        print(f"  ✅ {name}: {len(releases[:5])} recent releases")
    except Exception as e:
        print(f"  ⚠️ {name}: {str(e)[:60]}")

with open(os.path.join(DATA_DIR, 'product_releases.json'), 'w') as f:
    json.dump(all_releases, f, indent=2, ensure_ascii=False)
print(f"✅ Total: {len(all_releases)} product releases collected")

# --- Source 3: YouTube AI Channel RSS ---
YOUTUBE_CHANNELS = {
    "lev-selector": "UCA4GfsgbI09cLzonTKryC6g",  # Lev Selector - AI Updates Weekly
}

all_videos = []
for name, channel_id in YOUTUBE_CHANNELS.items():
    try:
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        req = urllib.request.Request(rss_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            raw = resp.read().decode('utf-8')
        
        root = ET.fromstring(raw)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
        
        for entry in root.findall('.//atom:entry', ns):
            title = entry.findtext('atom:title', '', ns)
            link = entry.find('atom:link', ns)
            link_href = link.get('href', '') if link is not None else ''
            published = entry.findtext('atom:published', '', ns)
            video_id = entry.findtext('yt:videoId', '', ns)
            
            if title and published:
                all_videos.append({
                    'channel': name,
                    'title': title,
                    'url': link_href or f"https://www.youtube.com/watch?v={video_id}",
                    'published': published[:10],
                    'video_id': video_id
                })
        print(f"  ✅ {name}: {len([v for v in all_videos if v['channel']==name])} recent videos")
    except Exception as e:
        print(f"  ⚠️ {name}: {str(e)[:60]}")

with open(os.path.join(DATA_DIR, 'youtube_ai.json'), 'w') as f:
    json.dump(all_videos, f, indent=2, ensure_ascii=False)
print(f"✅ Total: {len(all_videos)} YouTube videos collected")
```

**不可用的信息源记录**：

| 源 | 问题 | 替代方案 |
|----|------|----------|
| lmarena.ai | Cloudflare封杀curl和browser | ✅ openlm.ai/chatbot-arena（同数据，curl可采集） |
| trueup.io/layoffs | Cloudflare验证拦截 | ✅ layoffs.fyi（可获取统计摘要） |
| Product Hunt API | 需OAuth token认证 | 📌 未来申请token后可用 |
| artificialanalysis.ai | Next.js SPA，curl返回HTML空壳 | ✅ browser_navigate + browser_console提取 |

**周报新增板块建议**：

| 板块 | 数据源 | 频率 | 采集方式 |
|------|--------|------|----------|
| 🏆 模型竞争格局 | openlm.ai + artificialanalysis.ai | 每周 | curl + browser |
| 💰 模型API价格对比 | artificialanalysis.ai | 每周 | browser |
| 🔧 产品版本更新 | GitHub Releases API | 每周 | curl (API) |
| 📉 行业人才趋势 | layoffs.fyi | 每月 | curl + browser |
| 📺 AI视频周报 | YouTube RSS | 每周 | curl (RSS) |
