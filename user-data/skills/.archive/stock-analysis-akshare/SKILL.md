---
name: stock-analysis-akshare
description: 使用akshare分析A股股票 — 数据获取、技术指标计算、趋势分析、操作建议
version: 1.0
created: 2026-04-15
status: available
---

# A股股票分析 (akshare版)

## 前置条件
- Python已安装，akshare, pandas, numpy, matplotlib已安装

## 分析流程

### 1. 获取股票数据
```python
import akshare as ak
import pandas as pd
import numpy as np

# 获取日K线数据 (近1年)
symbol = "300055"  # 万邦达
df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date="20250415", end_date="20260415", adjust="qfq")
```

### 2. 计算技术指标
```python
# 均线
df['MA5'] = df['收盘'].rolling(5).mean()
df['MA10'] = df['收盘'].rolling(10).mean()
df['MA20'] = df['收盘'].rolling(20).mean()
df['MA60'] = df['收盘'].rolling(60).mean()

# MACD
ema12 = df['收盘'].ewm(span=12, adjust=False).mean()
ema26 = df['收盘'].ewm(span=26, adjust=False).mean()
df['DIF'] = ema12 - ema26
df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()
df['MACD'] = 2 * (df['DIF'] - df['DEA'])

# RSI
delta = df['收盘'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()
rs = avg_gain / avg_loss
df['RSI'] = 100 - (100 / (1 + rs))

# KDJ
low_min = df['最低'].rolling(9).min()
high_max = df['最高'].rolling(9).max()
rsv = (df['收盘'] - low_min) / (high_max - low_min) * 100
df['K'] = rsv.ewm(com=2, adjust=False).mean()
df['D'] = df['K'].ewm(com=2, adjust=False).mean()
df['J'] = 3 * df['K'] - 2 * df['D']

# 布林带
df['BOLL_MID'] = df['收盘'].rolling(20).mean()
df['BOLL_UP'] = df['BOLL_MID'] + 2 * df['收盘'].rolling(20).std()
df['BOLL_DOWN'] = df['BOLL_MID'] - 2 * df['收盘'].rolling(20).std()

# 成交量均线
df['VOL_MA5'] = df['成交量'].rolling(5).mean()
df['VOL_MA10'] = df['成交量'].rolling(10).mean()
```

### 3. 获取基本面数据
```python
# 实时行情
realtime = ak.stock_zh_a_spot_em()
stock_info = realtime[realtime['代码'] == symbol]

# 个股信息
info = ak.stock_individual_info_em(symbol=symbol)
```

### 4. 分析输出模板
输出以下维度的分析：
- **当前价格与涨跌**
- **均线系统**：多空排列判断
- **MACD**：金叉/死叉、红绿柱变化
- **RSI**：超买(>70)/超卖(<30)
- **KDJ**：金叉/死叉、J值极端
- **布林带**：位置与开口方向
- **成交量**：放量/缩量
- **综合操作建议**

### 5. 操作建议判断逻辑
| 条件 | 建议 |
|------|------|
| MA5>MA10>MA20>MA60 + MACD金叉 + RSI<70 | 买入/持有 |
| MA5<MA10<MA20<MA60 + MACD死叉 | 减仓/观望 |
| RSI>80 + 价格触及BOLL上轨 | 短线减仓 |
| RSI<20 + 价格触及BOLL下轨 | 关注抄底机会 |
| 放量突破MA60 | 趋势转强信号 |
| 缩量跌破MA60 | 趋势转弱信号 |

## 注意事项
- akshare接口可能变动，如报错需检查API更新
- 技术分析仅供参考，不构成投资建议
- 需结合大盘走势、板块热点、公司基本面综合判断
