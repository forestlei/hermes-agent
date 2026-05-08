# Proven Code Patterns for AI Daily Report Cron Sessions

Battle-tested code patterns from actual cron runs. Copy these into execute_code blocks.
Each block is SELF-CONTAINED (all imports, all variable definitions).

## Collection Order (CRITICAL)

**Always collect in this order** to maximize data yield despite rate limits:
1. HuggingFace Daily Papers (reliable, 50+ papers, no rate limit)
2. GitHub AI trending (reliable, but 10 req/min unauthenticated — use 12-15s delays between topic queries, collect most important topics first)
3. Hacker News Algolia (reliable)
4. Vendor blog RSS (3/6 work reliably)
5. Chinese AI sources (RSS + HTML parse + HF CN filter)
6. arXiv LAST (high rate-limit risk)

## GitHub Topic Collection (Rate-Limit Safe)

**CRITICAL**: Unauthenticated GitHub API allows only 10 requests/minute. With 7s delays,
only 5/10 topic queries succeed before 403 (confirmed 2026-05-05). Use 12-15s delays.

```python
import urllib.request
import json
import os
import time
from datetime import datetime, timedelta

today = datetime.now().strftime("%Y-%m-%d")
data_dir = os.path.expanduser(f"~/.hermes/ai-daily-report/shared/collections/{today}")
os.makedirs(data_dir, exist_ok=True)

date_30d_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

# Order matters: most important topics first in case of rate limit
# Confirmed 2026-05-07: all 10 topics succeed with 12s delays (261 unique repos)
topics = ['ai', 'llm', 'machine-learning', 'deep-learning', 'nlp',
          'computer-vision', 'reinforcement-learning', 'generative-ai', 'transformer', 'agentic']

all_repos = []
seen_ids = set()

for i, topic in enumerate(topics):
    try:
        url = f"https://api.github.com/search/repositories?q=topic:{topic}+created:>{date_30d_ago}&sort=stars&order=desc&per_page=30"
        req = urllib.request.Request(url, headers={
            "User-Agent": "AI-Daily-Report/2.0",
            "Accept": "application/vnd.github.v3+json"
        })
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        new_count = 0
        for item in data.get('items', []):
            repo_id = item.get('id')
            if repo_id and repo_id not in seen_ids:
                seen_ids.add(repo_id)
                all_repos.append(item)
                new_count += 1

        print(f"  topic:{topic} → {len(data.get('items', []))} results, {new_count} new (total: {len(all_repos)})")

        # 12-15s delay to stay under 10 req/min unauthenticated limit
        if i < len(topics) - 1:
            time.sleep(13)

    except Exception as e:
        if '403' in str(e):
            print(f"  topic:{topic} → RATE LIMITED. Stopping GitHub collection.")
            break
        print(f"  topic:{topic} → Error: {e}")

with open(os.path.join(data_dir, "github_ai.json"), "w") as f:
    json.dump(all_repos, f, ensure_ascii=False, indent=2)
print(f"Total unique repos: {len(all_repos)}")
```

## RSSHub Availability Check (503 Pattern)

RSSHub Docker may be running but return 503 on all routes during off-peak hours.
Always check route availability, not just container status.

```python
import urllib.request

rsshub_base = "http://localhost:1200"
rsshub_available = False

# Check container AND route availability
try:
    req = urllib.request.Request(f"{rsshub_base}/")
    with urllib.request.urlopen(req, timeout=5) as resp:
        if resp.status == 200:
            # Container up, but test a route too
            try:
                test_req = urllib.request.Request(f"{rsshub_base}/huggingface/blog")
                with urllib.request.urlopen(test_req, timeout=10) as test_resp:
                    rsshub_available = test_resp.status == 200
            except:
                rsshub_available = False  # Container up but routes 503
except:
    rsshub_available = False

if not rsshub_available:
    print("⚠️ RSSHub not available (container down or routes 503), skipping RSSHub sources")
```

## HuggingFace Daily Papers Collection

**⚠️ The `?date=YYYY-MM-DD` parameter returns 400 if today's papers aren't ready yet** (common during early morning cron). Use the no-parameter endpoint as primary, with yesterday fallback.

```python
import urllib.request
import json
import os
import re
from datetime import datetime, timedelta

today = datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
data_dir = os.path.expanduser(f"~/.hermes/ai-daily-report/shared/collections/{today}")
os.makedirs(data_dir, exist_ok=True)

hf_papers = []

# Try no-parameter endpoint first (returns most recent available)
try:
    url = "https://huggingface.co/api/daily_papers"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        hf_data = json.loads(resp.read().decode("utf-8"))
    hf_papers = hf_data if isinstance(hf_data, list) else []
    print(f"HF Daily Papers (default): {len(hf_papers)} papers")
except Exception as e:
    print(f"HF Daily Papers (default) failed: {e}")

# Fallback: try yesterday's date explicitly
if not hf_papers:
    try:
        url = f"https://huggingface.co/api/daily_papers?date={yesterday}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            hf_data = json.loads(resp.read().decode("utf-8"))
        hf_papers = hf_data if isinstance(hf_data, list) else []
        print(f"HF Daily Papers (yesterday fallback): {len(hf_papers)} papers")
    except Exception as e:
        print(f"HF Daily Papers (yesterday fallback) failed: {e}")

# Process papers
processed = []
for item in hf_papers:
    paper = item.get("paper", {})
    arxiv_id = paper.get("id", "")
    summary = paper.get("summary", paper.get("abstract", ""))[:500]
    
    # GitHub link detection
    github_link = ""
    if summary:
        gh_match = re.search(r'github\.com/[\w\-/]+', summary, re.IGNORECASE)
        if gh_match:
            github_link = "https://" + gh_match.group(0)
    
    processed.append({
        "arxiv_id": re.sub(r'v\d+$', '', arxiv_id),
        "title": paper.get("title", ""),
        "abstract": summary,
        "authors": [a if isinstance(a, str) else a.get("name", "") for a in (paper.get("authors", []) or [])[:5]],
        "published": paper.get("publishedAt", "")[:10],
        "upvotes": paper.get("upvotes", 0),
        "github_link": github_link,
        "source": "huggingface"
    })

hf_path = os.path.join(data_dir, "hf_papers.json")
with open(hf_path, "w") as f:
    json.dump(processed, f, ensure_ascii=False, indent=2)
print(f"Saved {len(processed)} HF papers")
```

## arXiv Collection (Per-Category — PREFERRED over combined query)

**Strategy**: Per-category queries with 3s delays are more reliable than a single combined query.
Confirmed 2026-05-06: 3/3 categories succeeded, yielding 77 deduped papers.
Combined query sometimes returns fewer results or 429s.

```python
import urllib.request
import json
import os
import time
import xml.etree.ElementTree as ET
import re
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
data_dir = os.path.expanduser(f"~/.hermes/ai-daily-report/shared/collections/{today}")

categories = ["cs.AI", "cs.CL", "cs.LG"]
all_papers = []

for i, cat in enumerate(categories):
    try:
        url = f"http://export.arxiv.org/api/query?search_query=cat:{cat}&sortBy=submittedDate&sortOrder=descending&max_results=30"
        req = urllib.request.Request(url, headers={"User-Agent": "AI-Daily-Report/2.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode("utf-8")
        
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(data)
        
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
            summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")
            id_url = entry.find("atom:id", ns).text.strip()
            arxiv_id = re.sub(r'v\d+$', '', id_url.split("/abs/")[-1])
            published = entry.find("atom:published", ns).text[:10]
            authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
            
            # GitHub link detection
            github_link = ""
            for field in [summary]:
                gh_match = re.search(r'github\.com/[\w\-/]+', field, re.IGNORECASE)
                if gh_match and not github_link:
                    github_link = "https://" + gh_match.group(0)
            
            all_papers.append({
                "arxiv_id": arxiv_id, "title": title, "abstract": summary[:2000],
                "authors": authors, "published": published,
                "url": f"https://arxiv.org/abs/{arxiv_id}",
                "github_link": github_link, "has_code": bool(github_link),
                "source": "arxiv"
            })
        
        print(f"  {cat}: {len(root.findall('atom:entry', ns))} papers")
        if i < len(categories) - 1:
            time.sleep(3)  # 3s delay between categories — sufficient to avoid 429
            
    except Exception as e:
        if '429' in str(e):
            print(f"  {cat}: RATE LIMITED, skipping remaining categories")
            break
        print(f"  {cat}: Error: {e}")

# Dedup by normalized arxiv_id
seen = {}
deduped = []
for p in all_papers:
    if p["arxiv_id"] not in seen:
        seen[p["arxiv_id"]] = p
        deduped.append(p)

papers_path = os.path.join(data_dir, "papers.json")
with open(papers_path, "w") as f:
    json.dump(deduped, f, ensure_ascii=False, indent=2)
print(f"Total unique arXiv papers: {len(deduped)}")
```

## OpenAI RSS XML Cleaning (REQUIRED)

OpenAI RSS frequently fails with "not well-formed (invalid token)". Must apply
aggressive cleaning before parsing. DeepMind and HuggingFace RSS parse cleanly
without this treatment.

```python
import re
import urllib.request
import xml.etree.ElementTree as ET

def fetch_openai_rss():
    url = "https://openai.com/blog/rss.xml"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    
    # Step 1: Strip CDATA sections
    raw = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', raw, flags=re.DOTALL)
    # Step 2: Fix bare ampersands (not already entities)
    raw = re.sub(r'&(?!(amp|lt|gt|quot|apos);)', '&amp;', raw)
    # Step 3: Remove control characters
    raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', raw)
    
    root = ET.fromstring(raw)
    items = []
    for item in root.iter('item'):
        items.append({
            'title': item.findtext('title', '').strip(),
            'url': item.findtext('link', '').strip(),
            'description': (item.findtext('description', '') or '')[:500],
            'published': item.findtext('pubDate', '').strip(),
            'source': 'OpenAI',
            'source_score': 92,
            'quality_score': 0
        })
    return items
```

## Paper Merge (arXiv + HuggingFace)

```python
import json
import os
import re

today = datetime.now().strftime("%Y-%m-%d")
data_dir = os.path.expanduser(f"~/.hermes/ai-daily-report/shared/collections/{today}")

with open(os.path.join(data_dir, "papers.json"), "r") as f:
    arxiv_papers = json.load(f)
with open(os.path.join(data_dir, "hf_papers.json"), "r") as f:
    hf_papers = json.load(f)

all_papers = {}
for p in arxiv_papers:
    norm_id = re.sub(r'v\d+$', '', p["arxiv_id"])
    p["arxiv_id"] = norm_id
    p["sources"] = ["arxiv"]
    all_papers[norm_id] = p

for p in hf_papers:
    norm_id = re.sub(r'v\d+$', '', p.get("arxiv_id", ""))
    if not norm_id:
        continue
    if norm_id in all_papers:
        all_papers[norm_id]["sources"].append("huggingface")
        all_papers[norm_id]["hf_upvotes"] = p.get("upvotes", 0)
        if not all_papers[norm_id].get("github_link") and p.get("github_link"):
            all_papers[norm_id]["github_link"] = p["github_link"]
    else:
        p["arxiv_id"] = norm_id
        p["sources"] = ["huggingface"]
        p["hf_upvotes"] = p.get("upvotes", 0)
        all_papers[norm_id] = p

merged = list(all_papers.values())
with open(os.path.join(data_dir, "papers_merged.json"), "w") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)
```

## Heuristic Paper Scoring

```python
def score_paper_heuristic(paper):
    score = 50  # base
    sources = paper.get("sources", [])
    if "arxiv" in sources and "huggingface" in sources:
        score += 10  # Cross-verified
    elif "huggingface" in sources:
        score += 5

    upvotes = paper.get("hf_upvotes", 0)
    if upvotes >= 50: score += 15
    elif upvotes >= 20: score += 10
    elif upvotes >= 5: score += 5

    if paper.get("github_link"):
        score += 10

    cats = paper.get("categories", [])
    if "cs.AI" in cats: score += 5
    if "cs.CL" in cats: score += 5

    title = paper.get("title", "").lower()
    high_impact = ["foundation model", "large language model", "llm", "gpt",
        "multimodal", "reasoning", "agent", "rlhf", "alignment", "scaling",
        "emergent", "benchmark", "survey", "comprehensive review", "world model",
        "video generation", "code generation", "mathematical", "chain-of-thought",
        "rag", "reinforcement learning", "diffusion", "moe", "inference",
        "efficient", "distillation", "quantization"]
    for kw in high_impact:
        if kw in title:
            score += 3
            break

    is_survey = False
    survey_kw = ["survey", "review", "comprehensive", "systematic", "taxonomy",
                 "landscape", "overview", "benchmark"]
    for kw in survey_kw:
        if kw in title:
            is_survey = True
            score += 5
            break

    return min(score, 100), is_survey
```

## GitHub Project Scoring (Growth-Rate Based)

```python
from datetime import datetime

def score_github_project(repo):
    stars = repo.get("stars", 0)
    forks = repo.get("forks", 0)

    if stars > 50000:
        return 0  # Filter mega-repos

    try:
        created_date = datetime.strptime(repo.get("created_at", "")[:10], "%Y-%m-%d")
        days_old = max((datetime.now() - created_date).days, 1)
        stars_per_day = stars / days_old
    except:
        stars_per_day = 0

    score = 30
    if stars_per_day >= 100: score += 30
    elif stars_per_day >= 50: score += 25
    elif stars_per_day >= 20: score += 20
    elif stars_per_day >= 10: score += 15
    elif stars_per_day >= 5: score += 10
    elif stars_per_day >= 1: score += 5

    if stars >= 10000: score += 15
    elif stars >= 5000: score += 12
    elif stars >= 1000: score += 10
    elif stars >= 500: score += 7
    elif stars >= 100: score += 5

    if forks >= 500: score += 10
    elif forks >= 100: score += 7
    elif forks >= 20: score += 3

    repo["quality_score"] = min(score, 100)
    repo["stars_per_day"] = round(stars_per_day, 1)
    return score
```

## PDF Generation + Feishu Delivery

```python
import os
import json
import urllib.request
import markdown
import weasyprint

# 1. md → HTML → PDF
report_path = os.path.expanduser("~/.hermes/ai-daily-report/shared/reports/daily/YYYY-MM-DD.md")
html_path = report_path.replace(".md", ".html")
pdf_path = report_path.replace(".md", "-daily-report.pdf").replace("YYYY-MM-DD", "AI-Daily-Report-YYYY-MM-DD")

with open(report_path, "r") as f:
    md_content = f.read()

html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'nl2br'])

# Minimal styling (keep compact)
html_full = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
body{{font-family:-apple-system,"Noto Sans SC",sans-serif;max-width:800px;margin:40px auto;padding:20px;line-height:1.6;color:#333;font-size:14px}}
h1{{color:#1a1a2e;border-bottom:3px solid #16213e;padding-bottom:10px;font-size:22px}}
h2{{color:#16213e;border-bottom:1px solid #e0e0e0;padding-bottom:5px;font-size:18px}}
table{{border-collapse:collapse;width:100%;margin:15px 0;font-size:12px}}
th,td{{border:1px solid #ddd;padding:8px;text-align:left}}
th{{background-color:#16213e;color:white}}
tr:nth-child(even){{background-color:#f8f9fa}}
</style></head><body>{html_body}</body></html>"""

with open(html_path, "w") as f:
    f.write(html_full)

weasyprint.HTML(filename=html_path).write_pdf(pdf_path)

# 2. Upload to Feishu (MUST use http.client, NOT urllib.request for file upload)
# ⚠️ urllib.request.Request returns HTTP 400 on multipart file uploads to Feishu.
# http.client.HTTPSConnection works correctly. Confirmed 2026-05-06.
import http.client
import uuid

env_path = os.path.expanduser("~/.hermes/.env")
feishu_app_id = feishu_app_secret = ""
with open(env_path, "r") as f:
    for line in f:
        line = line.strip()
        if line.startswith("FEISHU_APP_ID="):
            feishu_app_id = line.split("=", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("FEISHU_APP_SECRET="):
            feishu_app_secret = line.split("=", 1)[1].strip().strip('"').strip("'")

# Get token (urllib.request is fine for JSON-only requests)
token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
token_data = json.dumps({"app_id": feishu_app_id, "app_secret": feishu_app_secret}).encode("utf-8")
req = urllib.request.Request(token_url, data=token_data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=15) as resp:
    tenant_token = json.loads(resp.read().decode("utf-8"))["tenant_access_token"]

# Upload file via http.client (urllib.request fails with 400 on multipart)
with open(pdf_path, "rb") as f:
    file_content = f.read()

boundary = uuid.uuid4().hex
body = b''
body += f'--{boundary}\r\n'.encode('utf-8')
body += b'Content-Disposition: form-data; name="file_type"\r\n\r\n'
body += b'pdf\r\n'
body += f'--{boundary}\r\n'.encode('utf-8')
body += b'Content-Disposition: form-data; name="file_name"\r\n\r\n'
body += b'AI-Daily-Report-YYYY-MM-DD.pdf\r\n'
body += f'--{boundary}\r\n'.encode('utf-8')
body += b'Content-Disposition: form-data; name="file"; filename="AI-Daily-Report-YYYY-MM-DD.pdf"\r\n'
body += b'Content-Type: application/pdf\r\n\r\n'
body += file_content
body += f'\r\n--{boundary}--\r\n'.encode('utf-8')

conn = http.client.HTTPSConnection("open.feishu.cn")
conn.request("POST", "/open-apis/im/v1/files", body=body, headers={
    "Authorization": f"Bearer {tenant_token}",
    "Content-Type": f"multipart/form-data; boundary={boundary}"
})
resp = conn.getresponse()
upload_result = json.loads(resp.read().decode("utf-8"))
file_key = upload_result["data"]["file_key"]
conn.close()

# Send file message (http.client for consistency)
chat_id = "oc_6ed1cc645057da3bbe93c6120219a61e"
msg_content = json.dumps({"file_key": file_key})
send_data = json.dumps({"receive_id": chat_id, "msg_type": "file", "content": msg_content}).encode("utf-8")

conn = http.client.HTTPSConnection("open.feishu.cn")
conn.request("POST", "/open-apis/im/v1/messages?receive_id_type=chat_id", body=send_data, headers={
    "Authorization": f"Bearer {tenant_token}", "Content-Type": "application/json; charset=utf-8"
})
resp = conn.getresponse()
resp_json = json.loads(resp.read().decode("utf-8"))
conn.close()

# Send text summary (≤500 chars)
summary = "📋 AI 日报 — YYYY年MM月DD日 周X\n\n🎯 核心关注：...\n🔬 Top论文：...\n🚀 GitHub趋势：...\n📰 行业：...\n📎 完整报告见上方PDF"
msg_content_text = json.dumps({"text": summary})
send_data_text = json.dumps({"receive_id": chat_id, "msg_type": "text", "content": msg_content_text}).encode("utf-8")

conn = http.client.HTTPSConnection("open.feishu.cn")
conn.request("POST", "/open-apis/im/v1/messages?receive_id_type=chat_id", body=send_data_text, headers={
    "Authorization": f"Bearer {tenant_token}", "Content-Type": "application/json; charset=utf-8"
})
resp = conn.getresponse()
conn.close()
```

## Weekly Data Aggregation (Battle-Tested)

When `aggregate-report-data.py` fails (known bug: `dedup_news` assumes all items are dicts), use this manual aggregation code.

```python
import os
import json
import re
from datetime import datetime, timedelta

# Configuration — adjust period and days for each weekly run
today = datetime.now()
last_monday = today - timedelta(days=today.weekday() + 7)
last_sunday = last_monday + timedelta(days=6)
iso_week = last_monday.isocalendar()
period = f"{last_monday.strftime('%Y')}-W{iso_week[1]:02d}"

all_days = [(last_monday + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
pre_days = all_days[:6]  # Mon-Sat
missing_day = all_days[6]  # Sunday

base_dir = os.path.expanduser("~/.hermes/ai-daily-report/shared/collections")
draft_dir = os.path.expanduser("~/.hermes/ai-daily-report/shared/reports/weekly/.draft")
os.makedirs(draft_dir, exist_ok=True)

# === AGGREGATE PAPERS (arxiv + huggingface, dedup by normalized arxiv_id) ===
all_papers = {}
for day in all_days:
    day_dir = os.path.join(base_dir, day)
    for fname in ["papers.json", "hf_papers.json"]:
        fpath = os.path.join(day_dir, fname)
        if not os.path.exists(fpath):
            continue
        try:
            with open(fpath, 'r') as f:
                papers = json.load(f)
            if not isinstance(papers, list):
                continue
            for p in papers:
                if not isinstance(p, dict):
                    continue  # DEFENSIVE: skip non-dict items
                aid = re.sub(r'v\d+$', '', p.get('arxiv_id', ''))
                if not aid:
                    continue
                if aid not in all_papers:
                    p['arxiv_id'] = aid
                    p['collected_days'] = [day]
                    all_papers[aid] = p
                else:
                    all_papers[aid]['collected_days'].append(day)
                    upvotes = p.get('upvotes', p.get('hf_upvotes', 0))
                    if upvotes and not all_papers[aid].get('hf_upvotes'):
                        all_papers[aid]['hf_upvotes'] = upvotes
                    if not all_papers[aid].get('github_link') and p.get('github_link'):
                        all_papers[aid]['github_link'] = p['github_link']
        except Exception as e:
            print(f"  ⚠️ {day}/{fname}: {e}")

papers_list = list(all_papers.values())

# === AGGREGATE GITHUB PROJECTS (dedup by full_name) ===
all_projects = {}
for day in all_days:
    day_dir = os.path.join(base_dir, day)
    for fname in ['github_ai.json', 'github.json', 'github_scored.json']:
        fpath = os.path.join(day_dir, fname)
        if not os.path.exists(fpath):
            continue
        try:
            with open(fpath, 'r') as f:
                projects = json.load(f)
            if not isinstance(projects, list):
                continue
            for p in projects:
                if not isinstance(p, dict):
                    continue  # DEFENSIVE
                name = p.get('full_name', p.get('name', ''))
                if not name:
                    continue
                if name not in all_projects:
                    p['full_name'] = name
                    p['collected_days'] = [day]
                    all_projects[name] = p
                else:
                    all_projects[name]['collected_days'].append(day)
                    new_stars = p.get('stargazers_count', p.get('stargazersCount', 0))
                    old_stars = all_projects[name].get('stargazers_count', all_projects[name].get('stargazersCount', 0))
                    if isinstance(new_stars, int) and isinstance(old_stars, int) and new_stars > old_stars:
                        all_projects[name]['stargazers_count'] = new_stars
        except Exception as e:
            print(f"  ⚠️ {day}/{fname}: {e}")

projects_list = list(all_projects.values())

# === AGGREGATE NEWS (handles nested structures defensively) ===
all_news = []
for day in all_days:
    day_dir = os.path.join(base_dir, day)
    for fname in ['news.json', 'cn_news.json', 'vendor_blogs.json', 'hn_news.json', 'hn_stories.json']:
        fpath = os.path.join(day_dir, fname)
        if not os.path.exists(fpath):
            continue
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
            items = []
            if isinstance(data, list):
                items = [item for item in data if isinstance(item, dict)]
            elif isinstance(data, dict):
                for key in ['news', 'feeds', 'articles']:
                    if key in data and isinstance(data[key], list):
                        items.extend([item for item in data[key] if isinstance(item, dict)])
                if not items:
                    items = [data]
            for item in items:
                item['collected_day'] = day
                item['source_file'] = fname
                all_news.append(item)
        except Exception as e:
            print(f"  ⚠️ {day}/{fname}: {e}")

# Dedup news by title
seen_titles = set()
deduped_news = []
for n in all_news:
    title = n.get('title', '')
    if not title or len(title) < 5:
        continue
    title_norm = re.sub(r'\s+', '', title.lower())[:50]
    if title_norm not in seen_titles:
        seen_titles.add(title_norm)
        deduped_news.append(n)

# Save all intermediate files
for name, data in [
    (f"{period}-papers.json", papers_list),
    (f"{period}-projects.json", projects_list),
    (f"{period}-news.json", deduped_news),
]:
    with open(os.path.join(draft_dir, name), 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Period: {period}, Papers: {len(papers_list)}, Projects: {len(projects_list)}, News: {len(deduped_news)}")
```

Key differences from `aggregate-report-data.py`:
- **Defensive `isinstance(item, dict)` checks** on every list item before accessing dict methods
- **Nested structure handling** — tries `data["news"]`, `data["feeds"]`, `data["articles"]` keys
- **HF upvotes merge** — preserves upvotes from hf_papers.json when merging with papers.json
- **Star count tracking** — keeps highest star count across collection days

## cn_news.json Append Pattern (CRITICAL)

**Each `execute_code` block runs in its own scope.** If you collect RSS feeds in one block and vendor HTML/API data in another, you MUST load existing cn_news.json and APPEND, not overwrite.

```python
import json, os

cn_news_path = os.path.join(data_dir, "cn_news.json")

# ✅ CORRECT: Load existing, append new items
existing = []
if os.path.exists(cn_news_path):
    with open(cn_news_path, "r") as f:
        existing = json.load(f)

new_items = [...]  # Your newly collected items
existing.extend(new_items)

with open(cn_news_path, "w") as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

# ❌ WRONG: Overwrites previous block's data
cn_news = new_items  # Lost all RSS data from previous block!
with open(cn_news_path, "w") as f:
    json.dump(cn_news, f, ensure_ascii=False, indent=2)
```

**Confirmed 2026-05-07**: 195 RSS items were silently lost when vendor HTML data was saved in a separate block that initialized `cn_news = []` instead of loading from file.

## Paper Theme Classification (Priority-Ordered)

A single keyword check misclassifies (e.g., "security reasoning" → "推理" instead of "安全与对齐"). Use priority-ordered rules checking title+abstract together:

```python
def classify_paper(p):
    title = p.get('title', '').lower()
    abstract = (p.get('abstract', '') or '').lower()
    text = title + ' ' + abstract
    
    # Priority-ordered: check specific domains first, then general
    if any(kw in text for kw in ['safety', 'alignment', 'red team', 'jailbreak', 'harmful', 'manipulation']):
        return '安全与对齐'
    if any(kw in text for kw in ['multimodal', 'vision', 'image', 'video', 'speech', 'audio', 'visual']):
        return '多模态'
    if any(kw in text for kw in ['agent', 'agentic', 'autonomous', 'tool use', 'planning']):
        return '智能体'
    if any(kw in text for kw in ['retrieval', 'search', 'rag', 'retriever']):
        return '检索与RAG'
    if any(kw in text for kw in ['reasoning', 'chain-of-thought', 'math', 'logic']):
        return '推理'
    if any(kw in text for kw in ['benchmark', 'evaluation', 'dataset']):
        return '评测与基准'
    if any(kw in text for kw in ['training', 'fine-tun', 'rlhf', 'dpo', 'grpo', 'reinforcement']):
        return '训练与微调'
    if any(kw in text for kw in ['efficient', 'quantiz', 'compress', 'pruning', 'distill', 'on-device']):
        return '效率优化'
    if any(kw in text for kw in ['robot', 'embodied', 'world model', 'physical']):
        return '具身智能'
    if any(kw in text for kw in ['medical', 'clinical', 'health', 'drug']):
        return '医疗AI'
    if any(kw in text for kw in ['code', 'programming', 'software']):
        return '代码智能'
    return '其他'
```

## Chinese News Curation (Source Diversity Enforcement)

After collecting cn_news.json (all items have quality_score=0 from pre-collection), curate for the report:

```python
import os, json
from collections import defaultdict

# Step 1: Filter AI-relevant items
ai_keywords = ['AI', 'ai', '人工智能', '大模型', 'LLM', 'GPT', 'Claude', 'Gemini', '模型',
    '深度学习', '机器学习', 'OpenAI', 'DeepSeek', '通义', '千问', '文心', '豆包', '智谱',
    'Kimi', 'ChatGPT', 'Copilot', 'Agent', '智能体', '多模态', '推理', '训练', '微调',
    '开源', 'HuggingFace', 'transformer', 'NVIDIA', '英伟达', '芯片', 'GPU', '算力',
    '字节跳动', '百度', '阿里', '腾讯', '华为', '商汤', 'Anthropic', 'xAI',
    'Mistral', 'Llama', 'Qwen', '机器人', '自动驾驶', '语音', '视觉',
    'Sora', 'Midjourney', 'Stable Diffusion', '生成式', 'AIGC', 'RAG',
    '强化学习', '对齐', '安全', 'red team', 'benchmark', '基准']

cn_ai_items = []
for item in cn_news:
    title = item.get('title', '')
    desc = item.get('description', '') or ''
    if any(kw in title + ' ' + desc for kw in ai_keywords):
        cn_ai_items.append(item)

# Step 2: Filter out low-value vendor junk pages
vendor_junk = ['Documentation Index', '平台定位', '平台优势', '模型矩阵', '开发套件',
               'Skip to main', 'Change Log', '费用说明', '学习路径', '了解']
cn_ai_items = [item for item in cn_ai_items
               if not any(junk in item.get('title', '') for junk in vendor_junk)]

# Step 3: Enforce source diversity (max 3 per source)
source_count = defaultdict(int)
cn_curated = []
for item in cn_ai_items:
    source = item.get('source', 'Unknown')
    if source_count[source] < 3:
        cn_curated.append(item)
        source_count[source] += 1
```

## Key Lessons

- **Always re-import everything** in each execute_code block — `import os`, `import json`, `import re`, etc. The sandbox is fresh every call.
- **arXiv is unreliable** during cron. HuggingFace is the primary paper source; arXiv is a bonus.
- **Save intermediate results** to files after every successful step, so partial progress survives failures.
- **The `write_file` tool** is better than `execute_code` for the final report markdown — avoids string escaping issues.
- **Feishu credentials** live in `~/.hermes/.env`, NOT in environment variables. Read them fresh each time.
- **Feishu file uploads MUST use `http.client`** — `urllib.request.Request` returns HTTP 400 on multipart/form-data uploads to `/im/v1/files`. Use `http.client.HTTPSConnection` with manually constructed multipart body. JSON-only requests (token, messages) work fine with urllib.
- **aggregate-report-data.py has a known bug** — `dedup_news()` crashes on mixed-type lists. Use the manual aggregation code above as a fallback.
