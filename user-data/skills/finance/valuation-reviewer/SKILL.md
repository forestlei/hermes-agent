---
name: valuation-reviewer
description: "GP估值审核Agent — 接收GP全套估值包，运行估值模板，审核一致性，输出LP报告草稿。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services)
license: Apache 2.0
status: available
tags: [private-equity, valuation, gp, lp-reporting, fund-admin]
source: https://github.com/anthropics/claude-for-financial-services
inputs: GP估值包（Excel/PDF）、基金持仓明细、估值方法说明
outputs: 估值审核报告、LP报表草稿、异常值标记
---

# Valuation Reviewer — GP估值审核技能

## 核心工作流

### Phase 1: 估值包接收与解析

**接收材料：**
- 基金净值报告（NAV statement）
- 持仓明细（Holdings）
- 估值方法说明（Valuation methodology）
- 上期 vs 本期变化说明

**解析工具：**
- `mcp_vibe_trading_read_document`（PDF解析）
- Python（openpyxl）读取Excel
- `ocr-and-documents` 技能处理扫描件

### Phase 2: 估值方法审核

**主流估值方法核查：**

| 方法 | 适用场景 | 核查要点 |
|------|---------|---------|
| DCF | 稳定现金流 | WACC假设、现金流假设 |
| Market Approach | 有可比公司 | 可比公司选择、倍数选择 |
| Recent Funding | 近期融资 | 融资时间、条款 |
| Asset-based | 重资产 | 资产清单、折旧方法 |

**审核清单：**
- [ ] 估值方法与基金协议一致
- [ ] 可比公司/交易选择合理
- [ ] 重大假设有文档支撑
- [ ] 与上期方法一致（重大变化有说明）

### Phase 3: 持仓层面审核

**单项目核查：**
- 被投公司最新财务数据
- 估值倍数 vs 上期变化（>20%需特别说明）
- 货币换算汇率正确性
- 流动性折价（DLOM）是否合理

### Phase 4: 异常值标记

**自动标记规则：**
- 单项目估值变化 > ±30%
- 方法与同类项目显著不同
- 重大事件（诉讼、融资失败）未披露
- 财务数据明显错误

### Phase 5: LP报告生成

**报告结构：**
```
估值审核总结
├── 基金整体估值变动（QoQ/YoY）
├── 审核通过项目清单
├── 异常标记项目清单（需GP澄清）
├── 建议调整（如有）
└── 附录：方法论说明
```

## 适用场景关键词
- `/valuation` — 估值审核
- `GP审核` — GP valuation review
- `LP报告` — LP reporting
- `净值审核` — NAV review
