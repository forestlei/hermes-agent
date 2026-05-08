### HuggingFace Daily Papers Collection (NEW — High Priority Source)

**Why this source matters:** HuggingFace Daily Papers is community-curated — papers are submitted and upvoted by practitioners, providing a quality signal that arXiv alone cannot. Papers with high upvotes (≥50) are almost always significant.

**API endpoint:** `https://huggingface.co/api/daily_papers`
- Returns ~50 papers per call, covering the last ~2 weeks
- Each paper has: `id` (arXiv ID), `title`, `upvotes`, `ai_summary`, `ai_keywords`, `authors`, `publishedAt`
- Upvotes are the strongest quality signal — use for ranking
- `ai_summary` and `ai_keywords` provide pre-analyzed metadata (useful for report generation, but mark as `[~]` since AI-generated)

**Collection rules:**
1. **Merge with arXiv papers** — HF papers often overlap with arXiv collection. When merging:
   - If same `arxiv_id` exists in both sources, keep the arXiv version as primary but ADD `hf_upvotes` and `hf_ai_keywords` fields
   - HF-only papers (not in arXiv feed) should be added with `source: 'huggingface'`
   - **CRITICAL: Normalize arXiv IDs before comparing** — arXiv API returns IDs with version suffixes (e.g., `2604.09459v1`), while HF returns without (e.g., `2604.09459`). Strip the `vN` suffix before dedup: `aid = re.sub(r'v\d+$', '', arxiv_id)`. Without this, 0 papers will match and all HF papers appear as "HF-only" even when they exist in the arXiv feed.
   - **Authors field type varies by source** — arXiv API returns authors as a list of dicts `[{'name': '...'}]`, HF returns as comma-separated string. Use `.get('authors', [])` and check `isinstance(authors, list)` before processing.
2. **Quality scoring boost** — Papers with HF upvotes get a boost:
   - ⬆️ ≥200: +15 to quality score (near-certain significance)
   - ⬆️ ≥100: +10
   - ⬆️ ≥50: +5
   - ⬆️ ≥20: +2
3. **Use `ai_keywords` for categorization** — Better than arXiv categories for practical relevance
4. **Use `ai_summary` for report generation** — Can supplement (NOT replace) your own analysis. Always mark HF-generated summaries as `[~]`

**Integration in daily report:**
- In the paper table, add a ⬆️ column showing HF upvotes for papers that have them
- Papers with ⬆️ ≥100 should be prioritized for deep analysis section
- Note: HF Daily Papers API does NOT require authentication

### Vendor Blog RSS Collection (NEW — Critical for Industry News)

**Why this matters:** Vendor blogs are the PRIMARY source for major AI announcements (new model releases, policy changes, safety updates). They are more reliable and timely than secondary news sources.

**Verified working RSS feeds:**
| Source | Feed URL | Status | Typical Content |
|--------|----------|--------|-----------------|
| OpenAI Blog | `https://openai.com/blog/rss.xml` | ✅ 935 articles | Model releases, API updates, policy |
| DeepMind Blog | `https://deepmind.google/blog/feed/` | ✅ 100 articles | Gemini updates, research, safety |
| Google Research | `https://research.google/blog/rss/` | ✅ 100 articles | Research papers, benchmarks |
| HuggingFace Blog | `https://huggingface.co/blog/feed.xml` | ✅ 762 articles | New models, tools, datasets |
| Microsoft Research | `https://www.microsoft.com/en-us/research/feed/` | ✅ 10 articles | Research, Azure AI |
| NVIDIA Developer | `https://developer.nvidia.com/blog/feed/` | ✅ 100 articles | GPU, inference, deployment |
| 量子位 | `https://www.qbitai.com/feed` | ✅ | Chinese AI industry news |
| 36氪 | `https://36kr.com/feed` | ✅ | Chinese AI industry news |

**Not working (as of 2026-04-14):**
| Source | Status | Note |
|--------|--------|------|
| Anthropic Blog | ❌ 404 | No public RSS; check `https://www.anthropic.com/research` manually |
| Meta AI Blog | ❌ 404 | No RSS; check `https://ai.meta.com/blog/` manually |
| Mistral Blog | ❌ 404 | No RSS; check `https://mistral.ai/blog` manually |
| xAI Blog | ❌ 403 | Blocked; check `https://x.ai/blog` manually |
| 机器之心 RSS | ❌ XML error | Returns HTML not RSS; use web scraping instead |
| AI科技评论 | ❌ DNS error | Site may be down; check later |

**Collection rules:**
1. **Collect daily** — Fetch all RSS feeds, filter to articles from the last 3 days
2. **Severity classification** — Auto-classify based on title keywords:
   - 🔥 Major: title contains "release", "launch", "announce", "GPT", "Claude", "Gemini", "Llama", "model", "breakthrough"
   - 📌 Notable: everything else from vendor blogs (vendor blogs are inherently notable)
3. **Dedup with HN/量子位** — Same announcement may appear in multiple sources; merge and credit all sources
4. **Chinese vendor blogs** — 36氪 RSS works; 机器之心/量子位 need alternative methods (量子位 RSS works via `https://www.qbitai.com/feed`)
5. **Manual checks for non-RSS vendors** — Anthropic, Meta AI, Mistral, xAI should be checked via browser or web_extract when possible

### Industry News Collection (CRITICAL — Must Follow)

**Problem:** Previous reports only used Hacker News, resulting in non-AI content (Docker issues, old emails) and missing real industry news.

**Multi-source industry news collection:**

1. **Vendor blogs (highest priority)** — Check these FIRST for major announcements:
   - OpenAI Blog: `https://openai.com/blog` — New model releases, policy changes, research
   - Anthropic Blog: `https://www.anthropic.com/research` — Claude updates, safety research
   - Google DeepMind: `https://deepmind.google/blog/` — Gemini updates, research breakthroughs
   - Meta AI: `https://ai.meta.com/blog/` — Llama releases, open-source tools
   - Hugging Face: `https://huggingface.co/blog` — New models, datasets, tools
   - Mistral: `https://mistral.ai/blog` — Model releases, API updates
   - Chinese vendors: 百度文心, 阿里Qwen, 字节豆包, 智谱, DeepSeek, 月之暗面Kimi

2. **AI-native news sources:**
   - 机器之心: `https://www.jiqizhixin.com/` — Chinese AI news, most authoritative
   - 量子位: `https://www.qbitai.com/` — Chinese AI industry news
   - The Verge AI section, TechCrunch AI, Reuters AI

3. **Severity classification for industry news:**
   - 🔥 **重大 (Major)**: New model release, billion-dollar funding, regulatory change, major acquisition, safety incident
   - 📌 **重要 (Notable)**: Significant feature update, new benchmark result, notable open-source release, executive move
   - 📋 **一般 (Routine)**: Minor updates, opinion pieces, general discussion

4. **Filtering rules:**
   - MUST be AI-related — reject stories about Docker, general tech, politics unless directly AI-impacting
   - MUST have happened within the report period — no old news
   - Prefer primary sources (vendor blogs, official announcements) over secondary reporting
   - Chinese AI news is EQUALLY important as English — do not deprioritize

5. **Minimum standard:** Daily report must have at least 2-3 items from vendor blogs or AI-native news sources. If HN is the only source, the industry news section is incomplete.
