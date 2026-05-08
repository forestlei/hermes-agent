---
name: fund-admin
description: "基金运营垂直插件 — 覆盖基金行政、估值、LP关系、合规报告的全套运营工作流。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services)
license: Apache 2.0
status: available
tags: [fund-admin, fund-operations, lp-relations, compliance]
source: https://github.com/anthropics/claude-for-financial-services
---

# Fund Admin — 基金运营垂直插件

## 基金类型

| 类型 | 说明 |
|------|------|
| PE Fund | 私募股权基金 |
| VC Fund | 风险投资 |
| Hedge Fund | 对冲基金 |
| Mutual Fund | 公募基金 |
| Fund of Funds | 母基金 |

## 核心运营流程

### NAV估值（月度/季度）
- 持仓估值（公开市场）
- 私募估值（模型/第三方）
- 应计费用
- 汇率折算
- 基金净值计算

### LP关系管理
- 定期报告（Quarterly Report）
- 资本调用（Capital Call）
- 分配通知（Distribution Notice）
- K-1 / 税务文件

### 合规报告
- AIFMD（欧盟）
- SEC Filings（美国）
- AMAC备案（中国）

## 安装的Agent技能
- `valuation-reviewer` — NAV估值审核
- `gl-reconciler` — 总账对账
- `month-end-closer` — 月末结账
- `statement-auditor` — LP报表审计

## 关键指标
- NAV（净资产价值）
- DPI（分配倍数）
- TVPI（总回报倍数）
- PME（Public Market Equivalent）
