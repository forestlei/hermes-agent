---
name: gl-reconciler
description: "总账自动对账Agent — 发现账目差异，追溯根本原因，自动路由至相关负责人审批。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services)
license: Apache 2.0
status: available
tags: [fund-admin, gl-reconciliation, accounting, automation]
source: https://github.com/anthropics/claude-for-financial-services
inputs: 总账数据（CSV/Excel）、银行对账单、交易记录
outputs: 对账差异报告、根因分析、审批路由建议
---

# GL Reconciler — 总账对账技能

## 核心工作流

### Phase 1: 数据导入

**支持格式：** CSV、Excel、银行对账单PDF

**数据字段：**
- 日期、摘要、借贷方金额、余额
- 银行交易流水（日期、金额、对手方）

**Python数据处理：**
```python
import pandas as pd

# 读取GL数据
gl_df = pd.read_csv('general_ledger.csv')
bank_df = pd.read_csv('bank_statement.csv')

# 标准化日期格式
gl_df['date'] = pd.to_datetime(gl_df['date'])
bank_df['date'] = pd.to_datetime(bank_df['date'])
```

### Phase 2: 自动匹配

**匹配规则（优先级排序）：**
1. **精确匹配：** 日期 + 金额 + 摘要关键词
2. **金额匹配：** 仅金额一致，日期接近（±3天）
3. **范围匹配：** 一对多（一张GL对多条银行流水）
4. **逆向匹配：** 银行有记录，GL无记录

```python
# 精确匹配
matched = gl_df.merge(bank_df, on=['date', 'amount'], how='inner')

# 未匹配项目
unmatched_gl = gl_df[~gl_df.index.isin(matched.index)]
unmatched_bank = bank_df[~bank_df.index.isin(matched.index)]
```

### Phase 3: 差异分类

| 类型 | 说明 | 优先级 |
|------|------|--------|
| Timing | 记账时间差（如跨月） | 低 |
| Rounding | 小额四舍五入差异 | 低 |
| Missing | 一方完全缺失 | 高 |
| Duplicate | 重复记账 | 高 |
| Error | 金额/账户错误 | 紧急 |

### Phase 4: 根因分析

**自动分析：**
- 按账户类型汇总差异
- 按时间趋势（月末集中出现？）
- 按金额区间分布

**常见根因：**
- 银行未及时到账（境外汇款）
- 跨系统数据延迟
- 汇率折算差异
- 预提/应付未付

### Phase 5: 审批路由

**路由规则：**
- < ¥1,000：自动通过，标记待审
- ¥1,000-10,000：财务经理审批
- > ¥10,000：财务总监审批
- > ¥100,000：CFO审批

**输出：** 差异清单 + 审批路由建议

## 适用场景关键词
- `/reconcile` — 对账
- `GL对账` — general ledger reconciliation
- `银行对账` — bank reconciliation
- `账目差异` — account discrepancy
