## User-Shared Articles Workflow

When the user shares an AI-related article link (from any platform: WeChat, Toutiao, Twitter, etc.), **always** execute this 4-step flow:

### Step 1: Fetch & Read Full Content
- Use `curl` with mobile User-Agent to fetch the article HTML
- Extract article title, author, publish date, and body text
- For JavaScript-rendered pages, try extracting from `<script id="RENDER_DATA">` or `application/ld+json` metadata
- Summarize the article's core content for the user

### Step 2: Add to Today's Daily Report
- Add a `## 🔖 用户推荐文章` section at the **end of the report** (before the footer), as a standalone section
- If the section already exists, append to it; if not, create it
- Format each article as:
  ```markdown
  **N. [文章标题](url)** — 作者名
  - 评分: XX/100 (准确XX | 深度XX | 原创XX | 可读XX)
  - 简介: 一句话摘要
  ```
- Place user-recommended articles in this dedicated section to give them prominence
- **Multi-user note:** The report file is in `shared/reports/daily/`, so articles from all users appear in the same report

### Step 3: Quality Scoring (0-100)
Evaluate the article across these 4 dimensions (each 0-25, total 0-100):
| Dimension | Max | Criteria |
|-----------|-----|----------|
| Accuracy | 25 | Factual correctness, no hallucinated claims |
| Depth | 25 | Technical depth vs surface-level summary |
| Originality | 25 | Original analysis vs rehash of public info |
| Readability | 25 | Clear structure, good writing quality |

**Scoring calibration (per dimension, 0-25):**
- 20-25: Excellent (top-tier research/analysis, comparable to best-in-class publications)
- 15-19: Good (solid content, above average)
- 10-14: Average (adequate but unremarkable)
- 5-9: Below average (shallow, derivative, or poorly written)
- 0-4: Poor (inaccurate, misleading, or unreadable)

**Total score thresholds:**
- ≥ 80: Register as auto-collection source
- 70-79: Track but don't auto-collect (may upgrade later)
- < 70: Record only, low priority

**Note:** The `quality_score` object in registry.json stores sub-dimensions on a 0-100 scale (multiplied by 4 for display), but the actual scoring is done on the 0-25 scale. This means a dimension scored 20/25 appears as 80/100 in the registry.

### Step 4: Register High-Quality Publishers (Score ≥ 80)
If the article scores ≥ 80, add the publisher to `shared/sources/registry.json`:
```json
{
  "source_id": "platform-author-name",
  "name": "作者名",
  "platform": "今日头条/微信公众号/知乎/...",
  "url": "作者主页URL",
  "category": "AI科普/AI学术/AI产业/...",
  "quality_score": 82,
  "description": "简要描述其内容特点",
  "added_date": "YYYY-MM-DD",
  "notable_articles": [
    {
      "title": "文章标题",
      "url": "文章URL",
      "date": "YYYY-MM-DD",
      "tags": ["tag1", "tag2"]
    }
  ]
}
```

### Pitfalls for User-Shared Articles
- **Don't skip the fetch** — Always read the actual article, don't guess content from the URL
- **Don't add low-quality sources** — Only publishers with score ≥ 80 go into the registry
- **Don't forget to update the report** — The article must appear in today's daily report file
- **Handle paywalled/JS-heavy pages** — Try `application/ld+json` or `<meta>` tags for metadata when full content is inaccessible
- **Respect the user's sharing intent** — If they share it, it's important enough to include
- **Sources must be at author/UP level** — Not platform level. "飞鱼迪@今日头条" not just "今日头条". Include `author_url` linking to the author's profile page.
- **Quality scoring must include 4 sub-dimensions** — accuracy, depth, originality, readability (each 0-100, plus weighted total)
- **Projects/skills can be independently indexed** — In registry.json under a `projects` key, separate from `sources`. Projects and sources can overlap (same item in both) without conflict.
- **Scoring calibration for user-shared articles** — Score holistically based on: content depth & accuracy (primary), originality of analysis (secondary), writing quality (tertiary). Academic papers with solid data get 85+, practical open-source tools 75-85, shallow rehashes <70. When the same author appears multiple times, their score reflects their best work.
- **Duplicate author detection** — When an article's author is already in the registry, respond with "✅已收录" notation. When new, respond with "🆕新信息源". Track total source count.
- **Batch article handling** — When user shares articles one at a time in quick succession, fetch each immediately upon receipt, score it, check source registry, and respond concisely. Don't defer processing.

### Step 5: Record Skill Evolution per User

When a user's article sharing leads to a skill evolution (new source added, new project indexed, or skill knowledge updated), record it in the user's isolated skill-evolution directory:

1. **Identify the user** — Use the platform user ID from the session context (e.g., `ou_d366ba075912a3865430a7fe7020454b` for Feishu)
2. **Ensure user directory exists** — Create `users/<user-id>/skill-evolution/` if not present
3. **Create evolution record** — For each skill change triggered by this user:
   ```bash
   EVOLUTION_ID="ev-$(date +%Y%m%d-%H%M%S)"
   USER_DIR=~/.hermes/ai-daily-report/users/<user-id>
   mkdir -p "$USER_DIR/skill-evolution/$EVOLUTION_ID"
   ```
4. **Write metadata.json** in the evolution directory:
   ```json
   {
     "evolution_id": "ev-20260412-143000",
     "user_id": "<user-id>",
     "trigger": "article_share",
     "trigger_url": "https://m.toutiao.com/article/xxx",
     "type": "source_added | project_indexed | skill_updated",
     "timestamp": "2026-04-12T14:30:00+08:00",
     "merged": false,
     "summary": "Added toutiao-feiyudi as information source (score: 82)"
   }
   ```
5. **Update user's evolution index** — Append to `users/<user-id>/skill-evolution/index.json`
6. **Update users/index.json** — Increment the user's `skill_evolution_count` and `articles_shared`

**Evolution merge:** When a user's evolution is validated over time (e.g., their added source consistently produces high-quality content), set `merged: true` in the evolution record and update the shared skill accordingly.

### Toutiao Article Extraction (via toutiao-article-fetcher skill)

**Primary method:** Use the `toutiao-article-fetcher` skill for all Toutiao article operations. It provides a battle-tested fetch pattern, verification pipeline, and scoring rubric validated across 20+ articles.

**When to use toutiao-article-fetcher:**
- User shares any `m.toutiao.com/article/` or `m.toutiao.com/w/` URL
- Daily cron needs to collect from tracked Toutiao sources
- Any article quality evaluation requiring GitHub/arXiv verification

**Integration points (toutiao-article-fetcher → ai-daily-report):**

| TAF Capability | ADR Integration |
|---|---|
| Fetch pattern (urllib + Android UA) | Replaces deprecated curl method |
| GitHub repo verification (API + fallbacks) | Feeds into ADR traceability system (L1→L2 upgrade) |
| arXiv paper verification (API + direct fetch) | Feeds into ADR traceability system |
| Content scoring (depth×0.35 + orig×0.30 + acc×0.20 + read×0.15) | Supplements ADR's Authority-based scoring for user articles |
| Marketing/fabrication detection | Feeds into ADR source pruning decisions |
| 微头条 /w/ URL handling | Extends ADR collection coverage |

**TAF Scoring → ADR Source Evaluation Bridge:**
When TAF scores an article, map to ADR's source evaluation:
- TAF accuracy ≥ 80 → ADR Authority ≥ 20 (verified source)
- TAF depth ≥ 70 → ADR Depth ≥ 20 (substantial analysis)
- TAF originality ≥ 60 → ADR Uniqueness ≥ 7 (original insights)
- TAF score ≥ 80 → eligible for ADR auto-collection source
- TAF score 70-79 → track in ADR but don't auto-collect
- TAF score < 70 → one-time inclusion in daily report, no source tracking

**Dual Registry Bridge:**
- TAF registry: `~/.hermes/sources/registry.json` (toutiao_sources, arxiv_sources, github_sources, special_topics)
- ADR registry: `~/.hermes/ai-daily-report/shared/sources/registry.json` (sources, projects)
- **Bridge rule:** When TAF adds a source with score ≥ 80, also add to ADR registry under `sources` with key `toutiao-{author-name}`
- **Bridge rule:** When ADR cron discovers a new Toutiao source, also add to TAF registry for manual evaluation tracking
- **Sync check:** Weekly report generation should verify both registries are consistent

**TAF as ADR Collection Source (Phase 1 Extension):**
Add to daily collection workflow after vendor blogs:
```python
# 6. Collect from tracked Toutiao sources (via toutiao-article-fetcher)
# For each source in ~/.hermes/sources/registry.json toutiao_sources with avg_score >= 70:
#   - Fetch author's latest articles from their Toutiao profile page
#   - Extract article content using TAF fetch pattern
#   - Score using TAF rubric
#   - High-scoring articles (>= 70) feed into daily report
#   - Very high-scoring articles (>= 80) trigger wiki ingest
```

**Critical rules (from TAF experience):**
- **NEVER use `browser_navigate` for Toutiao** — Returns JS-heavy pages without useful content
- **NEVER use `curl` for Toutiao** — Deprecated; use execute_code with urllib.request
- **Anti-scraping headers are mandatory** — Without Referer + Cookie, requests return verification page
- **GitHub API Chinese character URLs** — MUST use `urllib.parse.quote()` for Chinese search terms
- **"开源" claimed but no repo found** → accuracy ≤ 30, flag as potential fabrication
- **"核心功能推测"** in article → SEO spam, score ≤ 25
- **Fabricated project claims** (e.g., "DeepSeek发布了Mega MoE" but no such repo) → verify by listing org's actual repos, accuracy ≤ 25
- **微头条 /w/ URLs** — Content in images, only og:title available; use arXiv cross-reference when paper keywords detectable
- **Batch processing** — Fetch each URL immediately, batch scoring + registry updates
- **Response truncation** — Keep summaries under 2000 chars, split with (1/N) format


### ClawFeed — AI新闻摘要工具（可集成信息抓取方案）

**项目地址：** https://github.com/kevinho/clawfeed
**定位：** 开源AI新闻摘要工具，"Stop scrolling. Start knowing."

**核心能力（与AI日报互补）：**
1. **多源聚合**：Twitter/X（用户及列表）、RSS/Atom、HackerNews、Reddit、GitHub Trending、直接网站抓取、自定义API — 覆盖了AI日报手动采集的大部分源
2. **多频率摘要**：4小时/每日/每周/每月 — 与AI日报的日报/周报/月报节奏对齐
3. **Source Packs**：信息源包打包分享，社区一键安装 — 可作为AI日报信息源发现的补充渠道
4. **Mark & Deep Dive**：标记+AI深度挖掘 — 与AI日报的深度分析流程类似
5. **可定制摘要逻辑**：编辑 `templates/` 下提示词模板（curation-rules.md, digest-prompt.md）— 可定制为AI日报专用过滤规则
6. **多格式输出**：RSS、JSON Feed、HTML — 可作为AI日报的采集上游
7. **REST API**：完整API支持摘要、认证、书签、信息源管理 — 可编程集成
8. **OpenClaw/Zylos AI代理集成**：可作为Hermes Agent技能运行

**与AI日报的集成方案：**
- **方案A（轻量）**：部署ClawFeed作为信息预筛选层，其RSS/JSON Feed输出作为blogwatcher的输入源
- **方案B（深度）**：将ClawFeed作为Hermes Agent技能集成，直接调用其REST API获取聚合摘要，替代部分手动采集脚本
- **方案C（参考）**：借鉴ClawFeed的Source Packs机制，在AI日报中实现类似的信息源分享和一键安装功能

**技术栈：** Python + SQLite + PWA + REST API
**适用场景：** 当AI日报需要扩展信息源覆盖面时，ClawFeed的多源聚合能力可作为补充采集层

### Current Toutiao Source Registry (20 sources as of 2026-04-15)

Persisted at `~/.hermes/ai-daily-report/shared/sources/registry.json`. Key sources by category:

**AI学术 (3):** AI科技评论(88), 机器之心Pro(87), 娱圈玩家(75)
**AI科普 (2):** 量子位(85), 人工智能科普站(82)
**AI产业 (1):** 36氪(86)
**AI工程 (3):** Phodal(83), InfoQ(78), VibeCoder(80)
**AI工具 (9):** 逛逛GitHub(82), AIGC小玩童(76), 不秃头程序员(72), 网文成神笔记(74), Yietion(70), 自由海浪(68), 黎明破晓(70), 李飞飞的飞-vtxf(58), 一行人(55)

### Source Deduplication & Publisher-Level Tracking

**Critical requirement:** All information sources must be tracked at the **publisher/author level** (头条号、微博版主、微信公众号、X/Twitter博主), NOT at the platform level. When a user shares an article from a publisher already in the registry, the response MUST alert: "⚠️ 该信息源已添加：[平台] [版主/作者名]"

**Publisher-level source key format:**
- 今日头条: `toutiao-{author-name}` (e.g., `toutiao-量子位`, `toutiao-不秃头程序员`)
- 微博: `weibo-{author-name}`
- 微信公众号: `wechat-{account-name}`
- X/Twitter: `x-{handle}` (e.g., `x-_akhaliq`)

**Ranking & categorization:** Sources are ranked by quality_score and categorized into:
- AI学术 (academic papers, research analysis)
- AI科普 (popular science, technology explanation)
- AI产业 (industry news, product releases)
- AI工具 (open source tools, developer utilities)
- AI工程 (engineering practices, system design)

**When user shares an article:**
1. Extract author/publisher name from article metadata
2. Check `shared/sources/registry.json` for existing source with same `platform` + `author`
3. If exists: alert user "⚠️ 该信息源已添加：{platform} {author}，评分{score}" and skip registry update
4. If new: score, register, and confirm
