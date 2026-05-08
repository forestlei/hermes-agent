---
name: kyc-screener
description: "KYC合规筛查Agent — 开户文档解析，自动运行规则引擎，标记材料缺口和合规风险。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services)
license: Apache 2.0
status: available
tags: [compliance, kyc, aml, onboarding, risk-screening]
source: https://github.com/anthropics/claude-for-financial-services
inputs: 客户身份文件、受益人声明、机构背景调查材料
outputs: KYC核查清单、风险评分、合规缺口报告
---

# KYC Screener — KYC合规筛查技能

## 核心工作流

### Phase 1: 材料收集

**个人客户：**
- 有效身份证件（身份证/护照）
- 地址证明（水电费账单/银行对账单）
- 税务居民身份（CRS/FATCA声明）
- 资金来源证明（薪资单/房产证明/投资记录）

**机构客户：**
- 公司注册证书
- 法人身份证件
- 受益人声明（UBO，>25%股权）
- 公司章程
- 董事会决议
- 反洗钱政策声明

**解析工具：**
- `ocr-and-documents` 技能处理扫描件/PDF
- `mcp_vibe_trading_read_document` 解析PDF文本

### Phase 2: 身份核验

**核实清单：**
- [ ] 身份证件真实、有效期有效
- [ ] 人脸识别（如有）
- [ ] PEP（政治敏感人士）筛查
- [ ] UN/OFAC制裁名单筛查
- [ ] 不良记录筛查（欺诈、犯罪）

**筛查数据源：**
- OFAC SDN List（美国）
- UN Security Council Sanctions List
- EU Sanctions Map
- 中国制裁名单（商务部/央行）
- PEP数据库（Thomson Reuters / Dow Jones）

```python
# PEP筛查示例（伪代码）
def screen_pep(name, database):
    matches = database.fuzzy_search(name, threshold=0.85)
    for match in matches:
        if match.is_politically_exposed:
            return PEP_FLAG(match.level, match.position)
    return CLEAR
```

### Phase 3: 风险评级

**评分维度：**

| 维度 | 权重 | 高风险指标 |
|------|------|-----------|
| 客户类型 | 20% | 信托/空壳公司 |
| 地域风险 | 25% | 高风险国家（FATF灰名单） |
| 行业风险 | 20% | 博彩、武器、加密货币 |
| 资金来源 | 25% | 不明/复杂 |
| 交易模式 | 10% | 异常频繁/大额 |

**风险等级：** 低风险（Green）/ 中风险（Yellow）/ 高风险（Red）

### Phase 4: 材料完整性检查

**KYC文档清单：**
```
基础KYC（必须）：
□ 有效身份证件
□ 地址证明
□ 税务居民声明（CRS/FATCA）

增强KYC（高风险必须）：
□ 资金来源证明
□ 受益人声明（UBO）
□ 董事会决议
□ 进一步尽职调查（EDD）
```

**缺口标记：** 自动标记缺失文件 + 截止日期

### Phase 5: 合规报告

**输出报告：**
```
KYC审核报告 — [客户名称]

一、客户信息
- 客户类型：[个人/机构]
- 风险评级：[低/中/高]
- 审核状态：[通过/待补充/拒绝]

二、身份核验
□ 通过 □ 异常（见备注）

三、制裁筛查
□ 无匹配 □ PEP命中 □ 制裁名单命中

四、材料完整性
□ 完整 □ 缺失（见清单）

五、合规建议
[通过 / 补充材料 / 拒绝 / 转交合规经理]
```

## 适用场景关键词
- `/kyc` — KYC审核
- `合规筛查` — compliance screening
- `开户审核` — onboarding review
- `反洗钱` — AML
- `受益人` — UBO

## 重要提示
- KYC审核结果需由合规官员确认，不可仅依赖AI判断
- 涉及制裁名单命中的情况，必须立即上报
- 各国KYC要求不同，需结合当地法规（如中国央行反洗钱规定、欧盟AMLD6）
