---
name: financial-services
description: "Anthropic Financial Services — 10个专业金融Agent + 8个垂直插件，覆盖投资银行、股权投资、基金运营、财富管理、合规场景。Apache 2.0开源。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services, 8500+ stars)
license: Apache 2.0
status: available
tags: [investment-banking, equity-research, private-equity, wealth-management, fund-admin, compliance, financial-modeling]
source: https://github.com/anthropics/claude-for-financial-services
parent: https://github.com/anthropics/claude-for-financial-services
---

# Anthropic Financial Services for Hermes Agent

> ⚠️ **重要免责声明**：本仓库所有Agent均为"起草工作成果供专业人士审核"的设计定位，不构成投资建议、法律建议或任何专业认证结论。所有输出均需由合格专业人士审核确认。

**原始仓库：** https://github.com/anthropics/claude-for-financial-services（Apache 2.0, 8500+ ⭐）

---

## 已集成的Agent技能（10个）

| Agent | 功能 | 类别 |
|-------|------|------|
| `pitch-agent` | 可比分析 + LBO + Pitch Deck | 投行 |
| `meeting-prep-agent` | 客户会议简报 | 投行 |
| `market-researcher` | 行业深度研究 | 研究 |
| `earnings-reviewer` | 财报解析 + 模型更新 | 研究 |
| `model-builder` | DCF / LBO / 三表Excel | 建模 |
| `valuation-reviewer` | GP估值审核 + LP报告 | PE运营 |
| `gl-reconciler` | 总账自动对账 | 基金运营 |
| `month-end-closer` | 月末结账 + 应计项目 | 基金运营 |
| `statement-auditor` | LP报表审计 | 基金运营 |
| `kyc-screener` | 合规开户筛查 | 合规 |

## 已集成的垂直插件（8个）

| 插件 | 功能 |
|------|------|
| `financial-analysis` | 核心分析框架整合 |
| `investment-banking` | 投行ECM/M&A/DCM工作流 |
| `equity-research` | 权益研究框架 |
| `private-equity` | PE全周期管理 |
| `wealth-management` | 财富管理/私行 |
| `fund-admin` | 基金行政管理 |
| `operations` | 交易/结算/清算运营 |
| `lseg-sp-global` | LSEG & S&P Global数据连接 |

## 快速开始

```bash
# 查看所有金融技能
/hermes skills list | grep finance

# 加载投行技能
/skill pitch-agent

# 加载PE技能
/skill private-equity

# 加载KYC合规技能
/skill kyc-screener
```

## 使用示例

```
# 制作一份新能源公司的Pitch Deck
/skill pitch-agent
> 分析[公司名]的LBO可行性，目标赛道：新能源汽车

# 财报季：批量分析10家重点公司
/skill earnings-reviewer
> 分析贵州茅台、宁德时代、比亚迪最新季度财报

# PE投后：审核GP月度估值包
/skill valuation-reviewer
> 审核[基金名称]2026年Q1估值包

# 月末：自动对账
/skill gl-reconciler
> 对账2026年4月总账数据
```

## 数据源（通过已有MCP）

| 场景 | MCP/工具 |
|------|---------|
| A股行情/财务 | `mcp_tradingagents`, `mcp_akshare` |
| 港股/美股 | `mcp_vibe_trading` |
| 技术分析 | `stock-analysis-akshare` |
| 量化分析 | `mcp_vibe_trading` (backtest/factor) |
| 研报解析 | `mcp_vibe_trading_read_document` |
| PDF处理 | `ocr-and-documents` |
| 邮件（财报通知） | `himalaya` |
| 报告生成 | `html-ppt-skill` |

## 与现有技能的关系

本技能是对现有技能库的增强，非替代关系：

- `stock-analysis-akshare` → 保留，专注A股技术分析
- `pv-competitive-analysis` → 保留，光伏行业深度分析
- `vibe-trading` MCP → 保留，主力量化分析平台
- `financial-services` → 本技能，提供金融全场景顶层框架

## 数据源集成（11个MCP，原始列表）

FactSet、S&P Global、Morningstar、Moody's、PitchBook、LSEG、Daloopa、Aiera、MT Newswires、Chronograph、Egnyte

> 注：上述为Anthropic官方集成的商业数据源。Hermes版本通过现有MCP（tradingagents/vibe-trading）提供等效数据覆盖，商业数据源需单独授权。

## 更新日志

- **2026-05-08**: 初始移植完成（10 Agent + 8 垂直插件），来源：anthropics/claude-for-financial-services
