---
name: operations
description: "运营垂直插件 — 覆盖交易运营、结算运营、清算运营的核心工作流。"
version: 1.0.0
author: Hermes Agent (ported from anthropics/claude-for-financial-services)
license: Apache 2.0
status: available
tags: [operations, trading-operations, settlement, clearing]
source: https://github.com/anthropics/claude-for-financial-services
---

# Operations — 运营垂直插件

## 运营类型

### 交易运营（Trading Operations）
- 交易指令管理（Order Management）
- 交易确认（Trade Confirmation）
- 交易匹配（Trade Matching）

### 结算运营（Settlement Operations）
- 券款对付（DvP）
- 交割指令（Delivery Instruction）
- 失败管理（Fail Management）

### 清算运营（Clearing Operations）
- 净额头寸计算
- 保证金管理（Margin）
- 风险监控

## A股特有流程
- T+1结算制度
- 中证登结算
- 沪深港通清算

## 关键系统
- OMS（Order Management System）
- PMS（Portfolio Management System）
- BMS（Billing Management System）

## 安装的Agent技能
- `gl-reconciler` — 账目对账
- `month-end-closer` — 月末运营结账
