---
name: hermes-update-verify
description: Hermes Agent 版本更新部署验证清单（轻量版3分钟 + 全量版70分钟）
version: 1.0
category: devops
triggers:
  - hermes update
  - 版本更新
  - 部署验证
---

# Hermes Agent 部署验证清单（轻量版）

> 适用场景：`hermes update` 后快速确认部署正常 | 预计耗时：**3分钟**

## 更新前（30秒）

- [ ] 记录版本号：`hermes version`
- [ ] 备份config：`cp ~/.hermes/config.yaml /tmp/config.yaml.bak`

## 更新后验证（3分钟）

### 1. 静态检查（30秒）

```bash
hermes version
python -c "import run_agent; from tools.registry import registry; print(f'{len(registry._tools)} tools OK')"
pip check
```

### 2. 核心测试（1分钟）

```bash
cd ~/hermes-agent && source venv/bin/activate
python -m pytest tests/run_agent/ tests/agent/ tests/tools/ -q --tb=line -x
```

### 3. 冒烟验证（1.5分钟）

```bash
hermes chat "Read pyproject.toml and tell me the version" 2>&1 | head -5
ps aux | grep "[h]ermes.*gateway" && echo "✓ Gateway alive"
hermes cron list 2>&1 | head -5
grep -c "ERROR" ~/.hermes/logs/gateway.log 2>/dev/null || echo "0"
```

## 🚨 不过就回滚

```bash
cp /tmp/config.yaml.bak ~/.hermes/config.yaml
git checkout <旧版本>
pip install -e .
```

## 📎 全量测试版

如需51项完整验证清单（含L0-L6六层、平台适配器、生产冒烟等），参见 `references/full-checklist.md`。

*轻量版 v1.0 | 2026-04-20*

## LLM重试机制配置（from llm-retry-config）

> 已完成的修改，适用于 Hermes Agent LLM 重试机制调优。

### 已修改文件
- `run_agent.py` 约9250行：`max_retries` 从3改为5
- `agent/retry_utils.py` 中 `jittered_backoff` 已正确实现指数退避

### 退避参数
- 无效响应重试：base_delay=5.0, max_delay=120.0 → 5s→10s→20s→40s→80s
- 异常错误重试：base_delay=2.0, max_delay=60.0 → 2s→4s→8s→16s→32s
- 公式：base_delay * 2^(attempt-1) + jitter

### 验证
- tests/test_retry_utils.py: 9 passed
- 重试相关测试: 13 passed
