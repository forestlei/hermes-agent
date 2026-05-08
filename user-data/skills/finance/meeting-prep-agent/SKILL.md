---
name: meeting-prep-agent
description: "投行/PE会议准备Agent — 客户会议前生成简报包，包括公司近况、待讨论议题、行业动态、竞争格局。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services)
license: Apache 2.0
status: available
tags: [investment-banking, meeting-prep, client-briefing, research]
source: https://github.com/anthropics/claude-for-financial-services
inputs: 客户名称、会议议程、上次会议纪要、当前行业热点
outputs: 会议简报（PDF/HTML）、公司概况、行业动态、讨论要点清单
---

# Meeting Prep Agent — 会议准备技能

> ⚠️ **免责声明**：所有材料为投研参考，不构成投资建议。

## 核心工作流

### Phase 1: 客户画像更新

**数据获取：**
- 使用 `mcp_tradingagents_get_a_share_news` 获取客户最新公告
- web search 搜索近期媒体报道、研报覆盖
- 使用 `mcp_vibe_trading_get_market_data` 获取股价表现

**客户画像维度：**
- 近期股价表现 vs 指数基准
- 最新业务进展（产品/渠道/合作）
- 近期融资/并购/高管变动
- 分析师评级变动

### Phase 2: 行业动态扫描

**扫描范围：**
- 政策变化（监管、财税、宏观）
- 行业关键数据发布
- 竞品动态（融资、产品、战略）
- 技术/商业模式创新

**来源：** HF Daily Papers、行业媒体（财新、36氪、华尔街见闻）、Twitter/X KOL

### Phase 3: 上次会议跟进

- 回顾上次会议纪要中的 Action Items
- 标记已完成 / 进行中 / 待跟进项目
- 准备跟进问题

### Phase 4: 简报生成

**使用 `html-ppt-skill` 制作简报：**

1. 议程页（Meeting Agenda）
2. 客户近况（1-2页）
3. 行业今日（1页）
4. 竞品动态（1页）
5. 上次跟进（1页）
6. 讨论要点 & 问题清单（1页）

### Phase 5: 预设问答准备

针对客户可能关注的问题，准备：
- 公司近期股价下跌原因？
- 对竞争对手新产品的看法？
- 下半年业绩指引？

## 适用场景关键词
- `/meeting` — 会议准备
- `客户简报` — 会前briefing pack
- `投行会议` — IBD meeting prep

## 数据源
- 股票行情：mcp_tradingagents, mcp_vibe_trading, akshare
- 新闻：tradingagents news API
- 研报：慧博投研、萝卜投研（web search）
