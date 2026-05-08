---
name: lseg-sp-global
description: "LSEG & S&P Global 数据连接器 — Refinitiv Eikon、Capital IQ、SP Global Market Intelligence数据接入。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services)
license: Apache 2.0
status: available
tags: [lseg, sp-global, refinitiv, capital-iq, data-connector]
source: https://github.com/anthropics/claude-for-financial-services
---

# LSEG & S&P Global — 数据连接器

## 数据源

### LSEG（Refinitiv / Eikon）
- 实时行情（Equities / Fixed Income / FX / Commodities）
- 公司财务数据（历史 + 预测）
- 衍生品数据
- 新闻（Reuters News）
- 债券/CDS数据

### S&P Global
- Capital IQ
- Market Intelligence
- Ratings（评级）
- 行业研究（BMI）

## MCP集成

### 已有MCP能力（通过现有工具）
| 需求 | 替代方案 |
|------|---------|
| LSEG数据 | `mcp_tradingagents`（A股/港股/美股行情） |
| Capital IQ | `mcp_vibe_trading`（基本面数据） |
| S&P Ratings | web search + 官方API |
| 研报 | HF Daily Papers + web search |

### 理想MCP配置
```yaml
# 如需连接真实LSEG/S&P，需配置：
mcpServers:
  lseg-refinitiv:
    command: python
    args: ["-m", "refinitiv-data"]
    env:
      RDP_LOGIN: your_api_key
  sp-capital-iq:
    command: python
    args: ["-m", "capitaliq"]
    env:
      CIQ_API_KEY: your_api_key
```

## 使用说明

本插件提供：
1. **数据源映射** — 明确各LSEG/S&P数据对应的替代获取方式
2. **API调用模板** — 标准化查询语法
3. **数据质量说明** — 各源数据的覆盖范围和延迟

## 11个MCP集成（原始列表）
1. FactSet
2. S&P Global
3. Morningstar
4. Moody's
5. PitchBook
6. LSEG
7. Daloopa
8. Aiera
9. MT Newswires
10. Chronograph
11. Egnyte

> 注：以上数据源需要各自API密钥。本技能提供使用这些数据的分析框架和最佳实践。
