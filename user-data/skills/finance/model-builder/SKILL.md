---
name: model-builder
description: "财务建模Agent — DCF、LBO、三表模型，直接生成可编辑Excel文件。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services)
license: Apache 2.0
status: available
tags: [financial-modeling, dcf, lbo, three-statement, excel]
source: https://github.com/anthropics/claude-for-financial-services
inputs: 公司基本信息、历史财务数据、关键假设（增长率/WACC/退出倍数）
outputs: DCF模型Excel、LBO模型Excel、三表联动模型Excel
---

# Model Builder — 财务建模技能

> ⚠️ **免责声明**：模型输出均为参考计算，需专业分析师验证假设合理性。

## 建模类型

### 1. DCF（现金流折现）模型

**输入：**
- 未来N年FCF预测（通常5年）
- 永续增长率（g）
- 加权平均资本成本（WACC）
- 净债务（Net Debt）

**输出：**
- 股权价值 = EV - Net Debt
- 目标价 = 股权价值 / 股数
- 敏感性分析矩阵（±100bps WACC, ±50bps g）

**Excel结构：**
```
Sheet1: 假设（Assumptions）
Sheet2: 利润表预测（P&L）
Sheet3: 现金流量表（Cash Flow）
Sheet4: DCF计算（DCF）
Sheet5: 敏感性分析（Sensitivity）
```

### 2. LBO（杠杆收购）模型

**输入：**
- 收购价格（EV）
- 股权/债权比例（通常30%/70%）
- 贷款利率、还款期限
- 目标EBITDA、增长率
- 退出倍数、年限

**输出：**
- IRR（内部收益率）
- MOIC（资金倍数）
- 债务还款时间表
- 退出价值

**关键公式：**
```
EV = EBITDA × EV/EBITDA倍数
Debt = EV × Leverage%
Equity = EV - Debt
Paydown = Debt × AM% × (1 - TaxRate)
ExitValue = ExitEBITDA × ExitMultiple
IRR = (ExitValue / Equity)^(1/Years) - 1
```

### 3. 三表联动模型

**三张表：**
- 资产负债表（Balance Sheet）
- 利润表（Income Statement）
- 现金流量表（Cash Flow）

**联动逻辑：**
- 净利润 → 资产负债表（留存收益）
- 净利润 → 现金流量表（经营现金流）
- 固定资产折旧 → 现金流 + 资产负债表
- 债务融资 → 三张表联动

## 实现工具

### Python → Excel（推荐）
```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

# 创建工作簿
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Assumptions"

# 写入假设
ws['B1'] = 'WACC'
ws['C1'] = 0.10
ws['B2'] = '永续增长率'
ws['C2'] = 0.025
```

### akshare + 模型
```python
import akshare as ak
# 获取历史财务数据
df = ak.stock_financial_analysis_indicator(symbol="000001")
```

## 适用场景关键词
- `/dcf` — DCF建模
- `/lbo` — LBO建模
- `财务模型` — financial model
- `三表模型` — three-statement model
- `Excel建模` — Excel model

## 限制
- 模型输出需要人工审核假设
- DCF对WACC和永续增长率极度敏感，需做敏感性分析
- 不适用于无稳定现金流的早期公司
