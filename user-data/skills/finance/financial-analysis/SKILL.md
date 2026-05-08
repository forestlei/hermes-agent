---
name: financial-analysis
description: "金融分析垂直插件 — 整合投行、PE、权益研究、财富管理场景的核心分析框架与工具链。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services)
license: Apache 2.0
status: available
tags: [finance, financial-analysis, framework]
source: https://github.com/anthropics/claude-for-financial-services
---

# Financial Analysis — 金融分析垂直插件

本插件整合所有金融场景的核心分析框架，是投资银行、股权投资、财富管理、基金运营的底层技能库。

## 核心框架速查

### 估值框架
- DCF（现金流折现）
- LBO（杠杆收购）
- Comps（可比公司）
- Precedents（先例交易）
- NAV（资产净值）
- SOTP（分部估值）

### 财务分析框架
- 三表联动模型
- 杜邦分析（ROE分解）
- 收益质量分析
- 资本结构分析
- 现金流质量分析

### 行业分析框架
- PESTEL（政策/经济/社会/技术/环境/法律）
- 波特五力
- SWOT（ strength/ weakness/ opportunity/ threat）
- 生命周期分析

### 风险管理框架
- VaR（在险值）
- 敏感性分析
- 情景分析（Base/Bull/Bear）

## 工具链

| 工具 | 用途 |
|------|------|
| `mcp_vibe_trading` | A股/港股/美股数据、分析、回测 |
| `mcp_akshare` | A股实时行情、财务数据 |
| `stock-analysis-akshare` | A股技术分析 |
| `himalaya` | 邮件（财报通知） |
| `html-ppt-skill` | 分析报告可视化 |

## 安装的Agent技能
本插件自动加载以下技能：
- `pitch-agent` — Pitch Deck制作
- `market-researcher` — 行业研究
- `earnings-reviewer` — 财报分析
- `model-builder` — Excel建模
- `valuation-reviewer` — 估值审核

## 使用示例
```
/financial-analysis     — 查看本技能帮助
/pitch [公司] [赛道]    — 制作Pitch Deck
/research [行业]        — 行业深度研究
/earnings [股票代码]    — 财报点评
/model [公司] [类型]    — DCF/LBO建模
```
