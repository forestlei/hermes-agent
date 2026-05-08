# Cron Failure Recovery Procedures

When a cron job fails (status=`error`, output shows "(No response generated)"), follow this manual recovery workflow.

## Diagnosis

1. Check cron output: `ls -lt ~/.hermes/cron/output/ | head -10`
2. Read the failed job's log: `cat ~/.hermes/cron/output/<job_id>/<timestamp>.md | tail -50`
3. If output ends with the SKILL.md content + "(No response generated)" → **thinking budget exhaustion** (most common)
4. If output shows a Python traceback → **code execution error**

## Recovery: Thinking Budget Exhaustion

This is the #1 failure mode. The SKILL.md is too large for the model's thinking budget in cron context.

### Step 1: Verify Data Exists

```python
import os, json
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
data_dir = os.path.expanduser(f"~/.hermes/ai-daily-report/shared/collections/{today}")
files = os.listdir(data_dir) if os.path.exists(data_dir) else []
print(f"Data dir: {data_dir}")
print(f"Files: {files}")
print(f"Collection summary exists: {os.path.exists(os.path.join(data_dir, 'collection_summary.txt'))}")
```

If `papers_scored.json` and `github_ai_scored.json` exist → pre-collection succeeded, proceed to manual report generation.

If data is missing or >4 hours old → run collection first (see `references/collection-scripts.md`).

### Step 2: Load and Analyze Data

```python
import json, os
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
data_dir = os.path.expanduser(f"~/.hermes/ai-daily-report/shared/collections/{today}")

with open(os.path.join(data_dir, "papers_scored.json")) as f:
    papers = json.load(f)
with open(os.path.join(data_dir, "github_ai_scored.json")) as f:
    projects = json.load(f)
with open(os.path.join(data_dir, "cn_news.json")) as f:
    cn_news = json.load(f)
with open(os.path.join(data_dir, "hn_stories.json")) as f:
    hn = json.load(f)
with open(os.path.join(data_dir, "vendor_blogs.json")) as f:
    blogs = json.load(f)

# Score GitHub projects by growth rate
for p in projects:
    stars = p.get("stargazers_count", p.get("stars", 0))
    created = p.get("created_at", "")[:10]
    try:
        created_date = datetime.strptime(created, "%Y-%m-%d")
        days_old = max((datetime.now() - created_date).days, 1)
        p["stars_per_day"] = round(stars / days_old, 1)
    except:
        p["stars_per_day"] = 0

# Filter and sort
top_papers = sorted(papers, key=lambda x: x.get("quality_score", 0), reverse=True)[:15]
top_projects = sorted([p for p in projects if p.get("stargazers_count", p.get("stars", 0)) <= 50000],
                      key=lambda x: x.get("stars_per_day", 0), reverse=True)[:20]
ai_cn = [n for n in cn_news if isinstance(n, dict) and n.get("ai_relevant")]
```

### Step 3: Generate Report

Use `write_file` to write the markdown report to:
`~/.hermes/ai-daily-report/shared/reports/daily/YYYY-MM-DD.md`

Follow the template in `references/report-templates-daily.md`.

Key elements:
- Calculate lunar date: `lunardate.LunarDate.fromSolarDate(year, month, day)`
- Title: `AI 日报 — YYYY年MM月DD日 周X 农历X月X日`
- Must include: 🎯核心重点关注分析, 📋综述专题, 🔬重要论文 Top 10, 🚀GitHub趋势, 📰行业动态, 🌏国内动态
- Source diversity rules: same source ≤3 items, ≥3 different sources for 国内动态

### Step 4: PDF + Feishu Delivery

```python
import os, json, urllib.request, markdown, weasyprint

report_path = os.path.expanduser("~/.hermes/ai-daily-report/shared/reports/daily/YYYY-MM-DD.md")
html_path = report_path.replace(".md", ".html")
pdf_path = os.path.expanduser("~/.hermes/ai-daily-report/shared/reports/daily/AI-Daily-Report-YYYY-MM-DD.pdf")

with open(report_path, "r") as f:
    md_content = f.read()

html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code', 'nl2br'])
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

# Upload + send to Feishu (see proven-code-patterns.md for full code)
```

### Step 5: Send Text Summary

After PDF, send a ≤500 char text summary to the Feishu group pointing to the PDF.

## Job ID Reference

| Job | ID | What to do if failed |
|-----|----|--------------------|
| Daily Pre-Collect | `8e7f174335db` | Re-run or manually collect (Phase 1-3) |
| Daily Completion | `6077eae54308` | Manual Phase 4-5 (this doc) |
| Weekly Pre-Process | `25fa22af7d65` | Manual aggregation + scoring |
| Weekly Completion | `1c7ddd6d6eff` | Manual weekly report generation |
| Monthly | `df3f2c2e4aef` | Manual monthly report generation |

## Prevention

The root cause is SKILL.md size. The cron model loads the entire SKILL.md into context before executing. If SKILL.md exceeds ~15KB, thinking budget is exhausted before the model can even start.

**Mitigation strategies:**
1. Move detailed content to `references/` files (already partially done)
2. Keep SKILL.md under 12KB — current size is ~20KB+, needs trimming
3. Cron prompts should explicitly say "Do NOT load the full SKILL.md, only read references/ as needed"
4. Consider splitting into separate skills: `ai-daily-report-collect` and `ai-daily-report-generate`
