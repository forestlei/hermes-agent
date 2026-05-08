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
