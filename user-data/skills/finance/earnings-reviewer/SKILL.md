---
name: earnings-reviewer
description: "财报分析Agent — 财报发布后自动解析业绩、调整模型、更新研报。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services)
license: Apache 2.0
status: available
tags: [equity-research, earnings, financial-analysis, model-update]
source: https://github.com/anthropics/claude-for-financial-services
inputs: 股票代码、财报发布日、EPS/营收实际 vs 预期
outputs: 财报点评、模型更新（Excel）、投资评级建议
---

# Earnings Reviewer — 财报分析技能

## 核心工作流

### Phase 1: 财报数据抓取

**数据来源：**
- `mcp_tradingagents_get_a_share_stock_data` — 历史OHLCV
- `mcp_tradingagents_get_a_share_news` — 最新公告
- akshare `stock_yjbb_em` — 业绩报表
- 上交所/深交所官方公告（web search）

**抓取内容：**
- 营收、EBITDA、净利润
- EPS 实际 vs 一致预期（Wind/Bloomberg一致预期）
- 指引（guidance）vs 市场预期
- 分业务/地区拆分

### Phase 2: 业绩归因分析

**同比/环比拆解：**
- 收入增长驱动：量？价？结构？
- 毛利率变化原因
- 费用率控制效果
- 非经常性损益影响

### Phase 3: 模型更新

**更新财务模型：**
- 将实际数据填入Excel模型
- 重新计算DCF/LBO关键变量
- 敏感性分析（上调/下调假设）

**使用工具：** Python（openpyxl）自动写Excel，或 `stock-analysis-akshare` 技能

### Phase 4: 研报生成

**财报点评模板：**
```
[公司名] [季/年]报点评：超预期/符合/低于预期

核心数据：
- 营收：¥XX亿（同比+XX%）
- 归母净利润：¥XX亿（同比+XX%）
- EPS：¥XX

超预期点：
1. ...

低于预期点：
1. ...

调整：
- 目标价：¥XX → ¥XX
- 评级：维持[买入/持有/卖出]

风险：...
```

### Phase 5: 评级复盘

- 对比实际 vs 一致预期
- 分析误差来源（过于乐观/悲观）
- 更新盈利预测模型

## 适用场景关键词
- `/earnings` — 财报分析
- `业绩点评` — earnings review
- `财报` — earnings report
- `模型更新` — model update

## 数据源
- 财报：akshare, 交易所公告（web search）
- 一致预期：wind数据、机构研报（web search）
- 评级：HF Daily Papers、券商研报
