# Chinese Information Source Dead Ends

**Purpose**: Prevent future sessions from re-testing sources that are confirmed broken. Last updated: 2026-05-04.

## WeChat Official Account Bridges (All Failed)

| Service | URL | Failure Mode | Verdict |
|---------|-----|-------------|---------|
| feeddd.org | https://feeddd.org/feeds | JS-rendered SPA; API returns HTML shell; SSL handshake failures on repeat requests | ❌ unusable via urllib |
| WeRSS | https://werss.app | JS-rendered SPA; search API returns empty | ❌ unusable via urllib |
| Sogou WeChat | https://weixin.sogou.com/weixin?type=2&query=xxx | Anti-scraping: triggers CAPTCHA/verification page on urllib requests | ❌ blocked |
| chuansongme | https://chuansongme.com | HTTP 515 (anti-bot) | ❌ blocked |
| RSSHub /wechat/mp/articles/{id} | localhost:1200/wechat/mp/... | Requires Puppeteer (Chrome) not installed in Docker image | ❌ needs Puppeteer |

**Conclusion**: WeChat 公众号 (机器之心Pro, 新智元, AI科技评论) currently has NO automated collection path. Only manual user-shared articles work.

## Toutiao (今日头条) APIs (All Failed)

| API | URL | Failure Mode | Verdict |
|-----|-----|-------------|---------|
| Search API | /api/search/content/?keyword=xxx | Returns `data:null, shark_decision:"reject"` — needs cookie auth | ❌ needs auth |
| Hot Board | /hot-event/hot-board/ | Returns 50 items but 0 AI-related (general news only) | ⚠️ too noisy |
| Category Feed | /api/pc/feed/?channel_id=93124 | Returns items but 0 match AI keywords | ⚠️ low AI ratio |
| RSSHub /toutiao/user/{id} | localhost:1200/toutiao/user/xxx | NotFoundError regardless of ID format (numeric or username). Route is broken upstream in RSSHub. | ❌ broken route |

**How to get Toutiao user IDs** (for when route is fixed):
1. Browser: visit `https://so.toutiao.com/search/?keyword=账号名` → click "用户" tab → click profile → URL = `/c/user/{数字ID}/`
2. Known: 量子位 = `53624121633`
3. From shared article links: extract source_id from article metadata

**Alternative**: 36氪AI频道 via RSSHub (`/36kr/information/AI`) provides similar AI industry coverage.

## Vendor Sites Without RSS (All SPAs)

| Vendor | URL | Issue | Workaround |
|--------|-----|-------|-----------| 
| 智谱AI | open.bigmodel.cn | Full SPA, no server-rendered content | ✅ Changelog page has GLM-* model names extractable via regex |
| 百度文心/千帆 | cloud.baidu.com | SPA but JSON tree has structured updatedAt+title | ✅ Regex extraction from HTML JSON tree |
| 字节豆包 | team.doubao.com | SPA, no blog/changelog section found | ❌ no extractable content |
| MiniMax/海螺 | hailuoai.com | SPA, 660KB HTML with no structured data | ❌ no extractable content |
| Kimi/Moonshot | platform.moonshot.cn | SPA, API docs only | ❌ no blog |
| 阶跃星辰 | platform.stepfun.com | 404 on blog pages | ❌ no blog |
| Qwen (HuggingFace page) | huggingface.co/Qwen | Returns raw JSON, not clean HTML | ✅ Use HF API: `/api/models?author=Qwen&sort=lastModified&direction=-1&limit=5` |

## Chinese Tech Media RSS Issues (Updated 2026-05-04)

| Media | URL | Failure Mode | Verdict |
|-------|-----|-------------|---------|
| 机器之心 | https://www.jiqizhixin.com/rss | **SSL certificate expired** (`[SSL: CERTIFICATE_VERIFY_FAILED]`) | ❌ SSL broken; try with `ctx.check_hostname=False` or skip |
| 36氪 | https://www.36kr.com/feed | **XML mismatched tag** (line 6, col 245) | ❌ unparseable XML; use RSSHub `/36kr/information/AI` instead |
| 雷锋网 | https://www.leiphone.com/feed | **XML undefined entity** (line 18, col 361) | ⚠️ try stripping CDATA first: `re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', text)` |
| AIBase | https://www.aibase.com/rss | **404 Not Found** | ❌ dead; removed from source list |
| 站长之家 | https://www.chinaz.com/rss.xml | **XML mismatched tag** (line 37, col 2) | ❌ unparseable |
| 新智元 | WeChat only | No website RSS | ❌ WeChat bridge needed |
| InfoQ中文 | API | Returns 451/500 | ❌ blocked |
| CSDN AI | No RSS | — | ❌ |

## RSSHub Issues (Updated 2026-05-04)

| Instance | URL | Failure Mode | Verdict |
|----------|-----|-------------|---------|
| rsshub.app (public) | https://rsshub.app/... | **403 Forbidden** on all routes | ❌ blocked; only local Docker works |
| Local Docker (port 1200) | http://localhost:1200/... | **503 Service Unavailable** during off-peak hours (container down) | ⚠️ check with `docker ps --filter name=rsshub` before use |
| RSSHub /toutiao/user/{id} | localhost:1200/toutiao/user/xxx | NotFoundError regardless of ID format | ❌ broken route upstream |

## Vendor Blog RSS Issues (Updated 2026-05-04)

| Vendor | URL | Failure Mode | Verdict |
|--------|-----|-------------|---------|
| NVIDIA | https://nvidianews.nvidia.com/rss | **Malformed XML** (syntax error line 5) | ❌ unparseable |
| Microsoft Research | https://www.microsoft.com/en-us/research/feed/ | **403 Forbidden** | ❌ blocked |
| DeepSeek /news | https://api-docs.deepseek.com/news | **404 Not Found** | ✅ Use `/updates` instead |
| Anthropic Blog | — | **404** | ❌ dead |
| Meta AI | — | **404** | ❌ dead |
| Mistral | — | **404** | ❌ dead |
| xAI | — | **403** | ❌ blocked |

## Working Chinese RSS Feeds (Verified 2026-05-04)

| Media | URL | Items | Notes |
|-------|-----|-------|-------|
| IT之家 | https://www.ithome.com/rss/ | ~60 | ✅ Reliable, needs AI keyword filter |
| 开源中国 | https://www.oschina.net/news/rss | ~50 | ✅ Reliable, needs AI keyword filter |
| 少数派 | https://sspai.com/feed | ~10 | ✅ Reliable, low volume |
| 钛媒体 | https://www.tmtpost.com/rss.xml | ~17 | ✅ Works, needs AI keyword filter |

**These 4 are the ONLY reliably parseable Chinese RSS feeds.** All others have XML/SSL/404 issues.

## Working Alternatives Summary

Instead of the dead ends above, use:
- **IT之家**: Direct RSS at `https://www.ithome.com/rss/` (60 items, filter for AI)
- **开源中国**: Direct RSS at `https://www.oschina.net/news/rss` (50 items, filter for AI)
- **少数派**: Direct RSS at `https://sspai.com/feed` (10 items, filter for AI)
- **钛媒体**: Direct RSS at `https://www.tmtpost.com/rss.xml` (17 items, filter for AI)
- **DeepSeek**: HTML parse `https://api-docs.deepseek.com/updates`
- **Qwen**: HF API `https://huggingface.co/api/models?author=Qwen&sort=lastModified&direction=-1&limit=5`
- **智谱**: Regex extract from `https://open.bigmodel.cn/dev/api/cn/update/new-releases`
- **百度千帆**: Regex extract from `https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um1w9y59n`
- **HuggingFace CN vendors**: API `https://huggingface.co/api/models?author={vendor}&sort=lastModified&direction=-1&limit=5` for Qwen, deepseek-ai, THUDM, 01-ai, internlm, baichuan-inc, fnlp
- **36氪AI**: RSSHub `/36kr/information/AI` (when Docker is up; direct RSS broken)
