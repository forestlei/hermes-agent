---
name: pitch-agent
description: "投行Pitch Agent — 可比公司分析、LBO建模、Pitch Deck制作。从行业研究到完整融资材料输出。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services)
license: Apache 2.0
status: available
tags: [investment-banking, comps, lbo, pitch-deck, valuation, financial-modeling]
source: https://github.com/anthropics/claude-for-financial-services
inputs: 公司/项目基本信息、目标融资规模、行业赛道、交易类型（股权/债权/并购）
outputs: Pitch Deck（PDF/HTML）、可比公司分析表、LBO模型、目标公司估值范围
---

# Pitch Agent — 投行Pitch制作技能

> ⚠️ **免责声明**：本技能输出的所有材料均为草稿，需专业投行人员审核确认。不构成任何投资建议。

## 核心工作流

### Phase 1: 公司 & 行业初步研究

**数据获取（MCP工具）：**
- 使用 `mcp_vibe_trading_get_market_data` 获取可比公司历史行情
- 使用 `mcp_akshare_*` 获取A股可比公司数据（如适用）
- 使用 web search 收集行业研报、竞品动态

**研究维度：**
- 公司业务模式、核心竞争力、市场份额
- 行业规模、增速、周期性、政策环境
- 可比公司估值区间（EV/EBITDA, P/E, P/S）
- 近两年融资/并购交易案例（ precedents）

### Phase 2: 可比公司分析（Comps）

**输出表格：**
| 指标 | 公司A | 公司B | 公司C | 目标公司 |
|------|-------|-------|-------|---------|
| 营收 (¥M) | | | | |
| EBITDA | | | | |
| EV | | | | |
| EV/EBITDA | | | | |
| P/E | | | | |
| EV/Revenue | | | | |

**工具：** Python（pandas/openpyxl）生成Excel，或 `html-ppt-skill` 生成可视化

### Phase 3: LBO建模

**核心假设：**
- 收购价格（EV）
- 交易结构（股权/债权比例，Leverage倍数）
- 融资成本（Debt rate）
- 退出倍数 / 退出年限
- 现金流假设（EBITDA growth, Capex, Tax）

**输出：** LBO模型 Excel，含：
- 交易假设
- 债务还款时间表
- IRR / MOIC 敏感性分析
- 退出情景分析

**工具：** Python（openpyxl/xlwings）或直接用 akshare 数据喂模型

### Phase 4: Pitch Deck 制作

**使用 `html-ppt-skill` 制作Pitch Deck：**

封面 → 投资亮点 → 行业概览 → 业务模式 → 竞争格局 → 财务摘要 → 融资需求 → 退出路径 → 团队介绍

**每页结构：**
- 标题 + 1-2句核心信息
- 数据可视化（图表）
- 关键结论（call-out）

### Phase 5: 估值总结

综合 Comps + LBO 给出估值范围：
- 低估区间 / 中值 / 高估区间
- 支撑逻辑（3-5条）

## 适用场景关键词
- `/pitch` — 制作Pitch Deck
- `LBO分析` — 杠杆收购建模
- `可比公司` — Comps表格
- `融资材料` — BP/Pitch Deck

## 数据源
- A股：akshare MCP、tradingagents MCP
- 港股/美股：yfinance、mcp_vibe_trading
- 宏观：FRED API（via web search）
- 行业研报：web search + HF Daily Papers

## 限制
- 本技能不提供投资建议，所有输出需人工审核
- Excel模型需要人工验证假设合理性
