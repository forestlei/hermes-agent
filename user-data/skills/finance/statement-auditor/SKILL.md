---
name: statement-auditor
description: "LP报表审计Agent — 分配_statement/资金流水核查，识别异常波动，输出审计意见。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services)
license: Apache 2.0
status: available
tags: [fund-admin, lp-statement, audit, private-equity]
source: https://github.com/anthropics/claude-for-financial-services
inputs: LP报表（PDF/Excel）、基金分配明细、资金流水
outputs: 审计报告、异常标记、疑问清单
---

# Statement Auditor — LP报表审计技能

## 核心工作流

### Phase 1: 材料接收

**接收材料：**
- LP Statement（PDF/Excel）
- 资金流水（银行对账单）
- 分配明细（Capital Call / Distribution notices）
- 估值报告（Valuation report）

**解析工具：**
- `mcp_vibe_trading_read_document`（PDF）
- Python（openpyxl）读Excel
- `ocr-and-documents` 处理扫描件

### Phase 2: 分配核查（Capital Call / Distribution）

**核查逻辑：**
```python
# 验证资本调用
expected_call = committed_capital * unfunded_commitment_pct
actual_call = sum(distribution_notices['type' == 'capital_call'])

# 验证分配
expected_dist = total_value - GP_carried_interest - expenses
actual_dist = sum(LP_statement['distributions'])
```

**核查要点：**
- LP出资进度与认缴承诺一致
- 分配顺序符合LPA条款（Preferred Return → Carried Interest → Return of Capital）
- GP管理费计算正确（通常2%/NAV或1.5%/Committed Capital）

### Phase 3: 资金流水核对

**核对清单：**
- 每笔Capital Call有对应银行收款
- 每笔Distribution有对应银行付款
- 费用支出有原始凭证
- 投资款项与被投公司收款匹配

### Phase 4: 异常波动检测

**自动标记规则：**
```python
# 重大变化标记
if abs(change_pct) > 0.20:  # 超过20%变化
    flag_anomaly("NAV变动超20%", period)

# 可疑模式检测
if multiple_distributions_without_investment:
    flag_anomaly("密集分配但无新投资")

if fees_above_threshold(fees > NAV * 0.03):
    flag_anomaly("管理费超3% NAV")
```

### Phase 5: 审计意见生成

**审计报告模板：**
```
LP报表审计报告 — [基金名称] — [期间]

一、总体意见
[无保留意见 / 保留意见 / 否定意见]

二、分配核查
✓ 已核查 / ✗ 异常项

三、资金流水
✓ 已核对 / ✗ 差异项

四、异常标记
1. [描述] — [建议]
2. ...

五、待澄清问题
1. [问题] — [截止日期]
```

## 适用场景关键词
- `/audit` — 报表审计
- `LP审计` — LP statement audit
- `分配核查` — distribution verification
- `基金审计` — fund audit
