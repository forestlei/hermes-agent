# Weekly Report Generation Workflow (Battle-Tested)

Actual execution sequence from 2026-W18 cron run. Follow this order for reliable weekly report generation.

## Pre-conditions

- Pre-processing job (凌晨3:00) has already aggregated 7 days of data into `.draft/` directory
- Files expected: `{period}-data.json`, `{period}-papers-scored.json`, `{period}-projects-scored.json`, `{period}-news-classified.json`, `{period}-news.json`, `{period}-pre-summary.txt`, `{period}-pre-analysis.json`
- Period format: `2026-W18` (ISO week)

## Step 1: Verify Pre-processing Results

```python
import os, json
from datetime import datetime, timedelta

base_dir = os.path.expanduser("~/.hermes/ai-daily-report/shared")
draft_dir = os.path.join(base_dir, "reports/weekly/.draft")

# Read pre-summary
with open(os.path.join(draft_dir, "{period}-pre-summary.txt")) as f:
    print(f.read())

# Read pre-analysis
with open(os.path.join(draft_dir, "{period}-pre-analysis.json")) as f:
    pre_analysis = json.load(f)
    # Check: missing_day, data_coverage, trends, top_papers_preview, top_projects_preview
```

Key checks:
- All 7 days have data (check `data_coverage`)
- If Sunday data missing → run lightweight collection (HF papers + GitHub + HN only, skip arXiv)
- If pre-summary says "无需补充采集" → proceed directly

## Step 2: Fix Data Issues

### 2a. Recalculate project growth rates (stars_per_day often 0.0)

```python
from datetime import datetime

with open(os.path.join(draft_dir, "{period}-projects-scored.json")) as f:
    projects = json.load(f)

for p in projects:
    stars = p.get('stargazers_count', 0)
    created = p.get('created_at', '')
    try:
        created_date = datetime.strptime(created[:10], '%Y-%m-%d')
        days_old = max((datetime.now() - created_date).days, 1)
        p['stars_per_day'] = round(stars / days_old, 1)
    except:
        p['stars_per_day'] = 0

projects.sort(key=lambda x: (x.get('quality_score', 0), x.get('stars_per_day', 0)), reverse=True)

with open(os.path.join(draft_dir, "{period}-projects-scored.json"), 'w') as f:
    json.dump(projects, f, ensure_ascii=False, indent=2)
```

### 2b. Extract GitHub links from paper abstracts

```python
import re

with open(os.path.join(draft_dir, "{period}-papers-scored.json")) as f:
    papers = json.load(f)

for p in papers:
    abstract = p.get('abstract', '') or ''
    gh_match = re.search(r'github\.com/[\w\-/]+', abstract, re.IGNORECASE)
    if gh_match and not p.get('github_links'):
        p['github_links'] = [gh_match.group(0)]

with open(os.path.join(draft_dir, "{period}-papers-scored.json"), 'w') as f:
    json.dump(papers, f, ensure_ascii=False, indent=2)
```

## Step 3: Generate Report Sections (Sequential execute_code)

### 3a. Papers Section

- Read `{period}-papers-scored.json`
- Handle mixed author formats: `name = a if isinstance(a, str) else a.get("name", "Unknown")`
- Classify themes with priority-ordered rules (safety > multimodal > agent > reasoning > ...)
- Build Top 20 table with columns: #, 论文, 作者, 类别, 评分, HF↑, 开源, 主题
- Write deep analysis for Top 3 (NOT abstract regurgitation)
- Use single quotes for Python strings containing Chinese quoted terms
- Save to `{period}-papers.md`

### 3b. Projects Section

- Read `{period}-projects-scored.json`
- Handle None descriptions: `(p.get('description', '') or '')[:55]`
- Build Top 20 table with columns: #, 项目, ⭐ Stars, 增长率, 语言, 描述
- Write deep analysis for Top 3 (why it exploded, architecture, niche, competition)
- Save to `{period}-projects.md`

### 3c. News Section

- Read `{period}-news-classified.json`
- Don't rely on pre-classification (90%+ will be "uncategorized")
- Manually curate 6-8 key global events from high-severity items
- For CN news: apply source diversity rules (≤3 per source, ≥3 sources)
- Build 国内动态 as a table with columns: #, 动态, 来源, 日期
- Save to `{period}-news.md`

### 3d. Leaderboard Section (🏆 模型竞争格局 — WEEKLY ONLY)

- Read `leaderboard.json` and `model_pricing.json` from `shared/collections/YYYY-MM-DD/`
- If files don't exist for current week, collect first (see `references/collection-scripts.md` Phase 1e)
- Build Arena Elo Top 15 table (Model/Elo/Coding/Vision/AAII/MMLU-Pro/ARC-AGI/Org/License)
- Build 🇨🇳 Chinese models sub-table (filter by org: DeepSeek/Alibaba/Baidu/Z.ai/Moonshot/ByteDance/Xiaomi/MiniMax/Tencent/Meituan)
- Build 💰 API pricing table (sorted by intelligence index, include price/speed/latency/context/value ratio)
- Write 3-5 key insights (格局变化/中国模型进展/性价比分析/开源vs闭源/趋势)
- Save to `{period}-leaderboard.md`

**⚠️ CRITICAL: After updating templates/cron/skill docs for leaderboard, you MUST also regenerate the actual report and deliver it. Updating the pipeline ≠ delivering the result. Close the loop: update → regenerate → deliver.**

### 3e. Trends Section

- Use pre-analysis trends + paper/project theme distribution
- Write 3 technical trends + 3 ecosystem trends + 4 directions to watch
- Cross-reference with papers and projects for evidence
- Save to `{period}-trends.md`

## Step 4: Assemble Full Report

```python
# Read all section files
sections = ['papers', 'projects', 'news', 'leaderboard', 'trends']
section_content = {}
for s in sections:
    with open(os.path.join(draft_dir, f"{period}-{s}.md")) as f:
        section_content[s] = f.read()

# Build overview + theme analysis
# Build source quality table
# Build deep analysis queue
# Assemble: title → overview → 🎯theme → papers → projects → 🏆leaderboard → news → trends → source quality → deep queue
# Save to shared/reports/weekly/{period}.md
```

Title format: `AI 周报 — YYYY年第NN周 (MM-DD ~ MM-DD)`

## Step 5: PDF + Feishu Delivery

1. md → HTML (markdown lib with tables extension) → PDF (weasyprint Python API)
2. Upload PDF to Feishu (multipart/form-data, file_type=pdf)
3. Send file message to chat
4. Send text summary (≤500 chars) as companion message
5. PDF filename must be ASCII: `AI-Weekly-Report-{period}.pdf`

## Step 6: Wiki Update

1. Create `~/wiki/weekly/{period}.md` with wikilinks
2. Update `~/wiki/overview.md` with week summary
3. Update `~/wiki/index.md` with week entry

## Common Failure Points

| Step | Failure | Fix |
|------|---------|-----|
| Author formatting | TypeError on `join(authors)` | Handle str/dict mixed formats |
| Description NoneType | AttributeError on `.lower()` | Use `(x or '').lower()` |
| Stars_per_day all 0 | Wrong sort order | Recalculate from created_at |
| String quoting | SyntaxError with Chinese quotes | Use single-quote Python strings |
| Source diversity | >3 items from one source | Count and trim during curation |
| News classification | 90% uncategorized | Manually curate from 🔥 items |
