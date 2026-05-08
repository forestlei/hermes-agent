---
name: month-end-closer
description: "月末结账Agent — 自动完成应计项目、过账、滚动预测，生成差异说明。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services)
license: Apache 2.0
status: available
tags: [fund-admin, month-end, accounting, accruals, roll-forward]
source: https://github.com/anthropics/claude-for-financial-services
inputs: 本月交易数据、历史月度数据、预算/预测数据
outputs: 结账清单、应计项目表、差异分析报告
---

# Month-End Closer — 月末结账技能

## 核心工作流

### Phase 1: 结账前准备清单

**标准结账清单：**
- [ ] 所有银行对账单已接收
- [ ] GL未清项已对账
- [ ] 员工报销已处理
- [ ] 固定资产折旧已计提
- [ ] 预提费用已计算
- [ ] 收入/成本已截止

### Phase 2: 应计项目（Accruals）

**常见应计项：**

| 类型 | 计算方法 | 科目 |
|------|---------|------|
| 工资 | 月薪 × 12 / 365 × 在职天数 | 应付工资 |
| 奖金 | 奖金池 × 实际完成% | 应付奖金 |
| 租金 | 月租金 / 30 × 天数 | 应付租金 |
| 水电 | 上月账单 × 本月天数 / 上月天数 | 应付水电费 |
| 税费 | 实际税基 × 税率 | 应交税费 |

```python
# 应计工资示例
monthly_salary = 500000  # 月薪总额
workdays_in_month = 22
accrual_days = 15  # 截止到15号
accrued_salary = monthly_salary / workdays_in_month * accrual_days
```

### Phase 3: 滚动预测（Roll-Forward）

**资产负债表滚动：**
```
期末余额 = 期初余额 + 本期变动
期末现金 = 期初现金 + 经营现金流 + 投资现金流 + 融资现金流
```

**P&L 截止：**
- 确认所有收入已开票
- 确认所有成本已入账
- 跨期调整（prepayments/deferrals）

### Phase 4: 差异分析（Variance Analysis）

**实际 vs 预算：**
```python
# 差异分析
variance = actual - budget
variance_pct = variance / budget

# 重大差异标记（>5%）
if abs(variance_pct) > 0.05:
    flag_for_review()
```

**差异归因：**
- 价格因素 vs 数量因素
- 一次性 vs 持续性
- 可控 vs 不可控

### Phase 5: 结账报告

**月度结账报告结构：**
```
结账完成报告 — [YYYY年MM月]
├── 关键财务指标
│   ├── 营收完成率
│   ├── 毛利率
│   └── 净利润
├── 结账状态
│   ├── ✓ 所有对账完成
│   ├── ✓ 应计项目已计提
│   └── ✓ 报表已生成
├── 重大差异清单
└── 下月待处理事项
```

## 适用场景关键词
- `/close` — 月末结账
- `结账` — month-end close
- `应计项目` — accruals
- `滚动预测` — roll-forward
- `差异分析` — variance analysis
