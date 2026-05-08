---
name: equity-research
description: "权益研究垂直插件 — 覆盖买方/卖方权益研究、行业覆盖、股票推荐、研报生成的完整工作流。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services)
license: Apache 2.0
status: available
tags: [equity-research, sell-side, buy-side, stock-picking]
source: https://github.com/anthropics/claude-for-financial-services
---

# Equity Research — 权益研究垂直插件

## 卖方研究（Sell-Side）vs 买方研究（Buy-Side）

| 维度 | 卖方（券商） | 买方（基金） |
|------|-------------|-------------|
| 目标 | 产生交易佣金 | 产生投资回报 |
| 受众 | 机构投资者 | 内部投资决策 |
| 输出 | 研报、评级、目标价 | 内部备忘录、投资建议 |
| 覆盖 | 宽覆盖（几百只） | 集中覆盖（几十只） |

## 研究框架

### 自上而下（Top-Down）
宏观 → 行业 → 公司 → 个股

### 自下而上（Bottom-Up）
个股基本面 → 行业 → 宏观

### 核心指标
- EPS（每股收益）
- BVPS（每股净资产）
- ROE（净资产收益率）
- EBITDA
- FCF（自由现金流）
- EV/EBITDA, P/E, P/B, P/S

## 安装的Agent技能
- `market-researcher` — 行业研究
- `earnings-reviewer` — 财报分析
- `model-builder` — DCF建模

## 数据源
- `mcp_tradingagents` — A股基本面+新闻+情绪
- `mcp_vibe_trading` — 行情+因子分析
- `akshare` — A股数据
- HF Daily Papers — 学术研报
