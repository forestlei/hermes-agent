---
name: market-researcher
description: "市场研究Agent — 行业/主题深度研究，输出行业概览、竞争格局、同行对标、机会清单。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services)
license: Apache 2.0
status: available
tags: [equity-research, market-research, industry-analysis, competitive-landscape]
source: https://github.com/anthropics/claude-for-financial-services
inputs: 目标行业/赛道、研究主题、时间范围
outputs: 行业研究报告、竞争格局图、公司对标表、投资机会清单
---

# Market Researcher — 市场研究技能

## 核心工作流

### Phase 1: 行业界定 & 规模测算

**研究框架（PESTEL）：**
- 政治/政策（Policy）
- 经济（Economic）
- 社会（Social）
- 技术（Technology）
- 环境（Environmental）
- 法律（Legal）

**市场规模测算方法：**
- TAM / SAM / SOM 分层
- 渗透率法 vs 人均消费法
- 历史增速外推

### Phase 2: 竞争格局分析

**工具：** 
- 波特五力模型
- 竞争定位图（2x2矩阵）
- 市场份额变化趋势

**数据来源：**
- 公司年报/半年报（PDF解析）
- 行业协会数据
- 第三方报告（艾瑞、IDC、Gartner等）

### Phase 3: 行业驱动因素 & 风险

**上行驱动：** 技术突破、政策支持、需求爆发、并购整合
**下行风险：** 监管收紧、经济下行、技术替代、竞争恶化

### Phase 4: 关键公司深度分析

对行业内3-5家核心公司分析：
- 业务模式、收入结构
- 核心竞争力（护城河）
- 财务表现（营收/利润率/增速）
- 估值水平

### Phase 5: 投资机会 & 风险评级

- **机会清单：** 按确定性/弹性排序
- **风险清单：** 主要矛盾和尾部风险
- **跟踪指标：** 哪些数据点需要持续监控

## 适用场景关键词
- `/research` — 行业研究
- `市场研究` — sector deep dive
- `竞争格局` — competitive landscape
- `行业报告` — industry report

## 数据源
- 公司财报：mcp_vibe_trading_read_document（PDF解析）
- 宏观数据：FRED API、国家统计局
- 行业数据：web search、行业报告网站
- 股价/估值：mcp_tradingagents, akshare
