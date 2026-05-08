---
name: llm-retry-config
version: 0.1
description: Hermes Agent LLM重试机制配置 - max_retries=5, 指数退避
trigger: retry, 重试, backoff, max_retries
---

# LLM重试机制配置

## 已完成的修改
- `run_agent.py` 约9250行：`max_retries` 从3改为5（已提交到fork分支feature/restricted-channels-v2）
- `agent/retry_utils.py` 中 `jittered_backoff` 已正确实现指数退避

## 退避参数
- 无效响应重试：base_delay=5.0, max_delay=120.0 → 5s→10s→20s→40s→80s
- 异常错误重试：base_delay=2.0, max_delay=60.0 → 2s→4s→8s→16s→32s
- 公式：base_delay * 2^(attempt-1) + jitter

## 测试
- tests/test_retry_utils.py: 9 passed
- 重试相关测试: 13 passed
- 3个预存失败与此改动无关
