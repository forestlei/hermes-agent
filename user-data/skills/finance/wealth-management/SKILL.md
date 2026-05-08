---
name: wealth-management
description: "财富管理垂直插件 — 覆盖高净值客户投顾、资产配置、理财规划、遗产传承场景。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services)
license: Apache 2.0
status: available
tags: [wealth-management, private-banking, financial-advisory, asset-allocation]
source: https://github.com/anthropics/claude-for-financial-services
---

# Wealth Management — 财富管理垂直插件

## 客户分层

| 层级 | 资产规模（USD） | 服务模式 |
|------|---------------|---------|
| Mass | < 100K | 数字化（App/机器人） |
| Affluent | 100K - 1M | 理财顾问 |
| HNW | 1M - 30M | 私人银行/家办 |
| UHNW | > 30M | 家族办公室（Family Office） |

## 核心服务

### 资产配置
- 战略配置（SAA）：长期大类资产比例
- 战术配置（TAA）：中短期偏离
- 个股/基金精选（Security Selection）

### 投资产品
- 股票（A股/港股/美股）
- 债券（利率债/信用债）
- 基金（公募/私募）
- 另类（VC/PE/房地产/对冲基金）
- 衍生品（期权/期货/结构化产品）

### 财富规划
- 税务筹划
- 遗产传承
- 保险规划
- 养老规划

## 适用场景
- 客户风险偏好评估
- 资产配置建议书
- 投资组合回顾
- 产品推荐说明

## 数据源
- `mcp_vibe_trading` — 组合分析
- `mcp_tradingagents` — 市场数据
- `stock-analysis-akshare` — A股分析
