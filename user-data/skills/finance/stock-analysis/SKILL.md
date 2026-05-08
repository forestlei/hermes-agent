---
name: stock-analysis
description: A股股票分析与黄金走势预测 — 数据获取、技术指标计算、可视化、趋势分析
version: 0.1
created: 2026-04-12
status: available
---

# A股股票分析与黄金走势预测技能

## 研究状态
✅ 工具和MCP服务器搜索已完成
⬜ MCP服务器安装与配置
⬜ Python环境搭建（AkShare + TA-Lib）
⬜ 技能代码编写与测试

## 用户需求
- 分析A股市场股票走势
- 预测黄金走势

## 最佳工具和MCP服务器

### A股数据源（Python库）
- **AkShare** (github.com/akfamily/akshare, 18K⭐) — 最强大的免费A股数据接口，覆盖股票/期货/基金/宏观/黄金
- **efinance** (github.com/Micro-sheep/efinance, 3.5K⭐) — 轻量级基金/股票/债券/期货数据
- **BaoStock** — A股历史数据接口

### A股专用MCP服务器
- **mcp-aktools** (github.com/aahl/mcp-aktools, 372⭐) — 🏆 股票/加密货币数据查询分析MCP
- **akshare-one-mcp** (github.com/zwldarren/akshare-one-mcp, 147⭐) — 基于akshare-one的A股MCP
- **akshare_mcp_server** (github.com/ttjslbz001/akshare_mcp_server, 50⭐)
- **stock-data-mcp** (github.com/openstockdata/stock-data-mcp) — 多源数据聚合，支持A股/港股/美股，自动故障转移
- **stock-mcp** (github.com/huweihua123/stock-mcp, 127⭐) — 专业金融市场MCP，支持A股/美股/加密货币

### 全球股票/黄金MCP服务器
- **yahoo-finance-mcp** (github.com/Alex2Yang97/yahoo-finance-mcp, 262⭐) — Yahoo Finance MCP，覆盖全球市场含黄金
- **financial-datasets/mcp-server** (1.9K⭐) — 金融数据集MCP，美股为主
- **momentum-mcp** (github.com/mphinance/momentum-mcp, 17⭐) — 类Bloomberg终端，股票筛选+技术分析MCP

### A股分析Web应用（参考架构）
- **StockAnal_Sys** (github.com/lc2panda/StockAnal_Sys, 815⭐) — Flask+AKShare的AI辅助股票分析系统
- **stock-backtrader-web-app** (239⭐) — Streamlit+AKShare+Backtrader回测系统

### 技术分析库
- **kand** (github.com/kand-ta/kand, 539⭐) — Rust/Python/WASM技术分析库，极快
- **TA-Lib** — 经典C语言技术指标库，150+指标

## 推荐方案

### A股分析技能
- **数据源**：AkShare + efinance
- **MCP服务器**：mcp-aktools（首选）或 akshare-one-mcp
- **技术指标**：TA-Lib / kand
- **功能**：实时行情、K线、技术指标、基本面、资金流向

### 黄金走势预测技能
- **数据源**：AkShare（含黄金期货/现货数据）+ Yahoo Finance（全球金价）
- **MCP服务器**：yahoo-finance-mcp + momentum-mcp
- **功能**：金价走势、技术指标、宏观关联分析、趋势预测

## ✅ 已完成
2026-04-15: pandas, numpy, matplotlib, akshare 已安装成功(akshare 1.18.55)。可直接用Python脚本分析A股。

## ⬜ 待完成

---

## AkShare Implementation Workflow

For the concrete akshare-based analysis pipeline (data fetching, technical indicator calculation, and trading signal logic), see `references/akshare-implementation.md`.

Quick reference — the workflow covers:
1. **Data fetching**: `ak.stock_zh_a_hist()` for OHLCV data
2. **Technical indicators**: MA, MACD, RSI, KDJ, Bollinger Bands (pure pandas, no TA-Lib dependency)
3. **Fundamentals**: `ak.stock_zh_a_spot_em()` for real-time quotes, `ak.stock_individual_info_em()` for company info
4. **Trading signals**: Decision table mapping indicator combinations to buy/hold/reduce/watch recommendations
5. **Caveats**: akshare API may change; technical analysis is reference-only, not investment advice
