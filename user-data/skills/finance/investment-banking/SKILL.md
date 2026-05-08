---
name: investment-banking
description: "投资银行垂直插件 — 覆盖承销、并购咨询、债务融资、ECM交易场景的完整工作流。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services)
license: Apache 2.0
status: available
tags: [investment-banking, ibd, m&a, ECM, DCM]
source: https://github.com/anthropics/claude-for-financial-services
---

# Investment Banking — 投资银行垂直插件

## 业务线覆盖

### IBD（Investment Banking Division）
- **股权融资（ECM）：** IPO、再融资、私募
- **债务融资（DCM）：** 债券、可转债、杠杆融资
- **并购咨询（M&A）：** 买方顾问、卖方顾问、并购融资

### 核心产品

| 产品 | 说明 |
|------|------|
| IPO | 首次公开募股 |
| FPO | 增发 |
| Rights Issue | 配股 |
| CB | 可转债 |
| Bond | 信用债/利率债 |
| M&A Deal | 并购交易 |

## 完整工作流

### ECM工作流
1. 客户pitch → 获得业务
2. 尽职调查（DD）
3. 起草招股说明书（ prospectus）
4. 路演（Roadshow）
5. 定价 & 分配
6. 上市 & 稳定价格期

### M&A工作流
1. 目标筛选（Screening）
2. 初步接触（Approach）
3. 尽调（Due Diligence）
4. 估值 & 谈判
5. 交易结构设计
6. 签约 & 交割

## 安装的Agent技能
- `pitch-agent` — 可比分析 + Pitch Deck
- `meeting-prep-agent` — IBD会议准备
- `model-builder` — 三表模型/DCFLBO

## 核心工具
- `mcp_vibe_trading` — 市场数据
- `akshare` — A股数据
- `html-ppt-skill` — 投行材料制作
