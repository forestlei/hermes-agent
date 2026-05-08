### Daily Report Template

Generated every day. Covers the last 24 hours of AI developments.

**Sections that MUST appear in every daily report** (in order):
1. Title + metadata line (sources, collection time)
2. 🎯 核心重点关注分析 (1-2 topics, deep analysis: why important + implications + what's next)
3. 📋 综述专题 (survey papers table)
4. 🔬 重要论文 Top 10 (table with 开源 column + deep analysis for top 3-5)
5. 🚀 GitHub趋势 (table sorted by growth rate + project highlights)
6. 📰 行业动态 (国际: vendor news + HN highlights)
7. 🌏 国内动态 (curated from cn_news.json, source diversity enforced)
8. 🔖 HuggingFace博客精选 (or 🔖用户推荐文章 if user shared articles)
9. 📊 今日数据概览 (collection stats)

**Sections that are NOT generated in daily reports** (skip these):
- 信息源评分更新 (only in weekly)
- 待深度分析 (internal tracking, not reader-facing)
- 🏆模型竞争格局 (only in weekly)

```markdown
# AI 日报 — YYYY年MM月DD日 周X 农历X月X日

> 数据来源：arXiv (cs.AI/CL/LG) · HuggingFace Daily Papers · GitHub Trending · Hacker News · OpenAI/DeepMind/HuggingFace Blog · N个中文信息源
> 采集时间：YYYY-MM-DD HH:MM CST | 报告生成：YYYY-MM-DD HH:MM CST

---

## 🎯 核心重点关注分析

### [话题1标题]

*(2-3段深度解读，不是简单罗列)*

**为什么重要**：这个事件/论文/项目为什么值得关注？解决了什么关键问题或打破了什么认知？

**意味着什么**：对行业/技术路线/竞争格局的潜在影响（2-3句深度分析）

**接下来会怎样**：接下来可能发生什么？哪些方向值得持续跟踪？

*(如有第二个同等重要的话题，重复上述结构)*

---

## 📋 综述专题

| # | 论文 | 主题 | 评分 |
|---|------|------|------|
| 1 | 综述标题 | 主题分类 | ⭐XX |

> 💡 今日综述较少/较多，[一句话点评]

---

## 🔬 重要论文 Top 10

| # | 论文 | 核心问题 | 评分 | 开源 |
|---|------|----------|------|------|
| 1 | 论文标题 | 一句话核心问题 | XX | 🔗GitHub链接 或 — |
| 2 | ... | ... | ... | ... |

### 📝 重点论文深度解读

**1. 论文标题** [arxiv_id]
- **核心问题**：这篇论文要解决什么问题？为什么这个问题重要？
- **方法创新**：与现有方法的关键区别是什么？用了什么新技术/新思路？
- **关键结果**：核心实验指标，相比基线提升多少？
- **潜在影响**：对领域的可能影响

*(重复 Top 3-5 论文)*

---

## 🚀 GitHub趋势

> 筛选条件：`created:>YYYY-MM-DD`，按增长率(stars/day)排序，过滤>50k星巨型仓库

| # | 项目 | ⭐ | 星/日 | 语言 | 简介 |
|---|------|-----|-------|------|------|
| 1 | [owner/repo](url) | X,XXX | XXX.X | Language | 项目简介 |
| 2 | ... | ... | ... | ... | ... |

### 🔍 项目亮点

**owner/repo** (⭐Xk, XXX星/日) — 一句话亮点。2-3句详细说明。

---

## 📰 行业动态

### 🌐 国际动态

**OpenAI**
- 🆕 **标题**：描述 [~OpenAI Blog]

**Google DeepMind**
- 🆕 **标题**：描述 [~DeepMind Blog]

**HuggingFace**
- 🔥 **标题**：描述 [~HF Blog]

### 💬 Hacker News热议

| 话题 | 热度 | 要点 |
|------|------|------|
| 话题 | N⬆ | 一句话要点 |

---

## 🌏 国内动态

> 源多样性：N个来源 | 同源≤3条 | 跨源去重

### 厂商动态

**DeepSeek**
- 💰 **标题**：描述 [来源]

**字节跳动·豆包**
- 🆕 **标题**：描述 [来源]

*(其他厂商按重要性排列)*

### 行业要闻

- 🏢 **标题**：描述 [来源]

### 观点与深度

- 🧠 **标题**：描述 [来源]

---

## 🔖 HuggingFace 博客精选

| 文章 | 要点 |
|------|------|
| 标题 | 一句话要点 |

---

## 📊 今日数据概览

| 指标 | 数值 |
|------|------|
| 采集论文 | X篇 (arXiv X + HF X, 去重后X) |
| 评分≥75论文 | X篇 |
| 采集GitHub项目 | X个 |
| 评分≥75项目 | X个 |
| HN AI相关 | X条 |
| 厂商博客 | X条 (OpenAI✓ DeepMind✓ HF✓ NVIDIA✗ Microsoft✗) |
| 中文AI新闻 | X条 (N个来源) |
| Wiki入库 | X条 (论文X + 项目X + 博客X) |

---

*本报告由 Hermes Agent 自动生成 | 数据采集→质量评分→深度分析→结构化报告*
*源验证级别：✅已验证 [~]AI生成摘要 [?]待验证 ❌已反驳*
```
