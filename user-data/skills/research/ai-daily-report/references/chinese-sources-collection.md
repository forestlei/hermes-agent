# 国内信息源采集方案与源多样性规则

## 问题诊断

2026-05-01 发现日报"国内动态"部分100%来自量子位，原因是：
1. cron采集管道只主动采集英文厂商RSS + 量子位RSS
2. 20个今日头条注册源全靠用户手动分享触发
3. 国内厂商（Qwen/DeepSeek/智谱等）无可用RSS

## 解决方案：三层架构

### Layer 1: 中文科技媒体RSS（9个，已验证）

| 源 | RSS URL | AI占比 | 评分 | 采集方式 |
|----|---------|--------|------|----------|
| 极客公园AI | https://www.geekpark.net/rss?tag=AI | 67% | 86 | rss(全量) |
| 极客公园 | https://www.geekpark.net/rss | 27% | 84 | rss+AI过滤 |
| 量子位 | https://www.qbitai.com/feed | 40% | 85 | rss+AI过滤 |
| AI科技评论/雷锋网 | https://www.leiphone.com/feed | 25% | 83 | rss+AI过滤 |
| 36氪 | https://36kr.com/feed | 7% | 82 | rss+AI过滤 |
| 钛媒体 | https://www.tmtpost.com/rss.xml | 22% | 80 | rss+AI过滤 |
| 少数派 | https://sspai.com/feed | 30% | 78 | rss+AI过滤 |
| IT之家 | https://www.ithome.com/rss/ | 5% | 75 | rss+AI过滤 |
| 开源中国 | https://www.oschina.net/news/rss | 6% | 76 | rss+AI过滤 |

### Layer 2: 国内厂商更新页（2个，HTML解析）

| 源 | URL | 评分 | 采集方式 |
|----|-----|------|----------|
| DeepSeek官方 | https://api-docs.deepseek.com/updates | 95 | html_parse(正则提取日期+模型名) |
| Qwen官方 | https://qwenlm.github.io/blog/ | 93 | html_parse(正则提取h2/h3标题) |

### Layer 3: HuggingFace中文厂商过滤

| 源 | RSS URL | 评分 | 采集方式 |
|----|---------|------|----------|
| HuggingFace(中文厂商) | https://huggingface.co/blog/feed.xml | 90 | rss+中文厂商关键词过滤 |

**过滤关键词**: Qwen, DeepSeek, ChatGLM, GLM, Yi-, Baichuan, MiniMax, InternLM, Alibaba, Baidu, Zhipu, Moonshot, Kimi, SenseTime, ByteDance

## 采集脚本

完整代码见 `references/collection-scripts.md` 中的 "Phase 1b: Chinese AI Sources Collection" 部分。

**AI关键词过滤列表**（用于综合媒体RSS的AI内容过滤）：
```
AI, ai, 人工智能, 大模型, LLM, GPT, Claude, Gemini, DeepSeek, deepseek, 
智能, 模型, Agent, agent, ChatGPT, OpenAI, 机器学习, 深度学习, 神经网络, 
Transformer, Qwen, 文心, 豆包, Kimi, GLM, 智谱, 通义, AIGC, 多模态, 
RAG, 微调, 推理, 开源模型, Token, GPU, 芯片, 算力, 训练, 对齐, RLHF,
Llama, Mistral, Anthropic, Copilot, 具身智能, 人形机器人
```

## 源多样性规则（日报生成时强制执行）

### 规则1：同源占比限制
- **国内动态**部分：同一来源最多3条新闻
- **行业动态**部分：同一来源最多5条新闻
- 超出部分降级到"📋其他动态"或舍弃

### 规则2：最低源数量
- **国内动态**部分：至少来自3个不同来源
- 如果可用源<3个，在报告中标注"⚠️国内源覆盖不足，建议添加更多信息源"

### 规则3：优先级排序
1. 厂商官方动态（DeepSeek/Qwen等，评分90+）→ 一手信息
2. AI垂直媒体（量子位/AI科技评论，评分83+）→ 深度分析
3. 科技综合媒体AI版（极客公园AI/36氪，评分80+）→ 行业视角
4. 综合媒体AI过滤（IT之家/钛媒体/少数派，评分75+）→ 补充视角

### 规则4：跨源去重
- 同一新闻被多个源报道时，保留质量评分最高的源
- 在标题旁标注"[多源报道: N个源]"提示信息可靠性

## 不可用的源（已测试失败）

### 国内厂商博客（无RSS/无法解析）
- 智谱AI (bigmodel.cn) — 全JS渲染，无RSS
- 文心一言 (yiyan.baidu.com) — 无RSS，纯产品页
- 豆包 (doubao.com) — 无RSS，纯产品页
- Kimi (platform.moonshot.cn) — 无RSS，纯API文档
- MiniMax (minimaxi.com) — 无RSS
- 商汤研究院 (research.sensetime.com) — DNS不可达
- 阶跃星辰 (platform.stepfun.com) — 无博客

### 中文科技媒体（无RSS）
- 机器之心 (jiqizhixin.com) — 无RSS，全JS渲染API不可用
- 新智元 — 微信公众号为主，无独立RSS
- InfoQ中文 — API返回451/500
- CSDN AI — 无RSS

### RSS Bridge（公共实例不可用）
- RSSHub公共实例 (rsshub.app) — 全返回403
- feeddd.org — WeChat RSS桥接，搜索功能受限

## 未来改进方向

1. **自建RSSHub实例** → 解锁机器之心/新智元/InfoQ中文等源
2. **微信公众号桥接** → 通过feeddd/RSSHub获取机器之心Pro/新智元等高质量公众号
3. **头条搜索API** → 对注册表中的头条源做定时搜索采集
4. **更多厂商HTML解析** → 智谱/百度/字节等官网动态页解析

## RSSHub本地实例（2026-05-01部署）

**Docker命令**：
```bash
docker run -d --name rsshub -p 1200:1200 -e CACHE_TYPE=memory -e CACHE_EXPIRE=3600 -e ACCESS_KEY=hermes2026 --restart unless-stopped diygod/rsshub:latest
```

### 已验证可用的RSSHub路由

| 源 | RSSHub路径 | 条目数 | 说明 |
|----|-----------|--------|------|
| 36氪AI频道 | /36kr/information/AI?key=hermes2026 | 30 | AI专用feed，质量高 |
| 36氪快讯 | /36kr/newsflashes?key=hermes2026 | 20 | 快讯流，时效性极高 |
| HuggingFace博客 | /huggingface/blog?key=hermes2026 | 14 | 中国厂商常在此首发 |

### 需Puppeteer的路由（暂不可用）
- /wechat/mp/articles/{id} — 微信公众号（需Puppeteer）
- /weibo/search/hot — 微博热搜（需Puppeteer）
- /toutiao/* — 头条（大部分路由需用户ID或Puppeteer）

### 已失效的路由
- /jiqizhixin/articles — 机器之心（NotFoundError）
- /geekpark/articles — 极客公园（API变更404）
- /infoq/topic/ai — InfoQ（empty）

## 额外厂商更新页（HTML解析，Phase 1d）

| 源 | URL | 解析方式 | 评分 |
|----|-----|---------|------|
| 智谱AI更新日志 | https://open.bigmodel.cn/dev/api/cn/update/new-releases | 正则提取GLM-*模型名 | 91 |
| 百度千帆更新 | https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um1w9y59n | 正则提取updatedAt+title | 89 |

**智谱解析**：Nextra/Next.js渲染，用 `GLM-[\d.]+[A-Za-z\-]*` 正则提取模型名，最新包含GLM-5.1, GLM-4.7等
**百度千帆解析**：JSON树结构中有updatedAt和title字段，2026-04有41条更新记录

## 头条号ID查找与标注规则

### 查找方法（已验证可靠）

1. 浏览器访问 `https://so.toutiao.com/search/?keyword=账号名&dvpf=pc&pd=user`（`pd=user` 直接搜用户标签，更准确）
2. 搜索结果中用户卡片的链接格式：`https://sou.toutiao.com/search/jump?url=https://www.toutiao.com/c/user/数字ID/`
3. 用浏览器Console提取：`Array.from(document.querySelectorAll('a')).filter(a=>a.href.includes('jump')&&decodeURIComponent(a.href).includes('/c/user/')).map(a=>({text:a.textContent.substring(0,40),id:(decodeURIComponent(a.href).match(/\/c\/user\/(\d+)/)||[])[1]}))`
4. 也可直接导航到用户主页，从 `window.location.href` 读取 `/c/user/数字ID/`

**批量查找**：在浏览器Console中用 `fetch()` 批量搜索，从返回HTML中正则匹配 `/c/user/(\d{8,20})`。注意需在同域下执行（否则CORS限制）。

### 已注册的头条号ID（registry.json toutiao_uid字段）

| 账号 | toutiao_uid | 粉丝量级 |
|------|------------|---------|
| 机器之心Pro | 3134187068 | 33.6万 |
| AI科技评论 | 6487824072 | 21万 |
| 36氪 | 3757989448 | 大号 |
| 量子位 | 53624121633 | — |
| 逛逛GitHub | 2810006047832116 | 4569 |
| Phodal | 5858489098 | 7871 |
| VibeCoder | 1534555398876824 | 161 |
| 璞奇 | 97056077034 | — |
| InfoQ | 63915309916 | — |
| 人工智能科普站 | 4487544493587256 | 6571 |
| AIGC小玩童 | 106173110551 | — |
| 不秃头程序员 | 111041630540 | — |
| Yietion | 3531225146067326 | — |
| 自由海浪 | 86465328800 | — |
| 黎明破晓 | 3386099520252423 | — |
| 李飞飞的飞-vtxf | 923191326814334 | — |
| 一行人 | 78170349127 | — |
| 娱圈玩家 | 553781989227566 | — |
| 网文成神笔记 | unknown（未找到） | — |
| AI-GitHub | unknown（未找到） | — |

### 日报标注规则

引用头条文章时必须标注作者头条号ID，格式：`作者名(ID:xxxxx)`。ID从registry.json的 `toutiao_uid` 字段获取。

## 不可用方案详细记录

### Sogou微信搜索
- URL: https://weixin.sogou.com/weixin?type=2&query=xxx
- 问题: 反爬虫机制，urllib请求触发验证页面
- 状态: ❌ 不可用

### feeddd.org
- 问题: JS渲染SPA，API返回HTML空壳；高频请求触发SSL握手失败
- 状态: ❌ urllib不可用

### WeRSS (werss.app)  
- 问题: JS渲染SPA，搜索API无返回
- 状态: ❌ urllib不可用

### 今日头条搜索API
- URL: /api/search/content/?keyword=xxx
- 问题: 需cookie认证，返回data:null, shark_decision:"reject"
- 头条热榜API(/hot-event/hot-board/)可用但AI占比极低
- 头条分类feed API(channel_id=93124)可用但AI过滤后0条
- 状态: ❌ 搜索不可用，分类feed低价值

### 传歌(chuansongme.com)
- 问题: HTTP 515（反爬）
- 状态: ❌ 不可用
