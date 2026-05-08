---
name: source-evolution
description: "信息源进化：按群维度隔离信息源、按群+用户双维度评分、自动发现与淘汰"
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [reasoning, source, evolution, information, group-isolation, scoring]
    related_skills: [core-thinking, group-thinking, source-prospector, concept-discovery]
    category: reasoning
    config:
      restricted_channels:
        description: "Bind this skill to restricted channels via channel_skill_bindings in config.yaml"
---

# Source Evolution — 信息源进化引擎

## 概述

信息源的进化管理技能。核心变更：从全局共享信息源升级为按群维度隔离、按群+用户双维度评分的分层体系。

## 三级数据模型

```
L0 全局 (profile)     → ~/.hermes/skills/research/source-evolution/
L1 群维度 (chat_id)   → ~/.hermes/groups/{chat_id}/
L2 群内用户 (user_id)  → ~/.hermes/groups/{chat_id}/users/{user_id}/
```

### 查询顺序

```
L2(群内用户偏好) → L1(群信息源) → L0(全局基线)
```

### 继承机制

- 群信息源 = 全局信息源 ∪ 群专属信息源
- 用户评分 = 群评分 × 用户偏好权重
- 缺少群维度数据时，退化为全局模式

## 七维评分体系

每个信息源在 7 个维度上评分（1-10分）：

| 维度 | 含义 | 群维度影响 |
|------|------|-----------|
| **relevance** | 与群主题的相关度 | 高 — AI群评分AI源高，财经群评分财经源高 |
| **quality** | 内容质量（准确性、深度、原创性） | 中 — 质量是客观的，但群偏好影响权重 |
| **timeliness** | 时效性（更新频率、响应速度） | 低 — 时效性较客观 |
| **diversity** | 信息多样性（视角、来源、方法） | 中 — 不同群需要不同类型的多样性 |
| **reliability** | 可靠性（历史准确率、稳定性） | 低 — 可靠性较客观 |
| **accessibility** | 可获取性（是否付费、是否需要翻墙） | 中 — 不同群用户可能访问能力不同 |
| **cost** | 获取成本（时间、金钱、计算资源） | 中 — 不同群对成本的敏感度不同 |

### 三级评分

1. **全局基线分** — 所有群共享的初始评分
2. **群维度评分** — 在群内重新评估 relevance（最关键维度）
3. **用户偏好权重** — 用户对信息源的个性化权重调整

**综合评分公式**:
```
final_score = Σ(dimension_score × weight) × user_preference_factor
```

## 信息源生命周期

### Tier 分级

| Tier | 含义 | 条件 | 采样频率 |
|------|------|------|---------|
| Tier 1 | 核心源 | 综合评分 ≥ 8.0 | 每次执行 |
| Tier 2 | 重要源 | 综合评分 6.0-8.0 | 每次执行 |
| Tier 3 | 备选源 | 综合评分 4.0-6.0 | 每3次执行 |
| Tier 4 | 观察源 | 新注册源（观察期30天） | 每5次执行 |
| Tier 5 | 淘汰源 | 综合评分 < 4.0 持续14天 | 停止采样 |

### 生命周期流程

```
新发现 → Tier 4(观察) → 评分稳定 → 升级到 Tier 1-3
                              │
                              └─ 评分持续低 → 降级到 Tier 5(淘汰)
```

### 自动发现机制

在群聊讨论中，当以下信号出现时触发新信息源发现：

1. **用户分享链接** — 提取域名，评估为新源候选
2. **频繁引用某来源** — 统计引用频率，超过阈值触发评估
3. **讨论中暴露信息缺口** — "没人提到X方面的信息" → 搜索相关源
4. **L3 价值发现揭示新需求** — 价值链需要新类型的数据支撑

### 淘汰机制

信息源在以下条件下被淘汰：

1. **持续低分** — 综合评分 < 4.0 持续 14 天
2. **不可访问** — 连续 3 次采样失败
3. **质量下降** — reliability 维度评分下降 ≥ 3 分（可能是源方变更）
4. **群维度淘汰** — 群内 relevance 评分 < 3.0 持续 7 天（群专属淘汰，不影响全局）

## 群间信息源传播

```
Group A 新源 → global discovered 池 → Group B 的 source-evolution 评估 → 决定是否引入
```

- 一个群发现的高质量源进入全局候选池
- 其他群的 source-evolution 独立评估是否适合引入
- **不自动同步** — 每个群独立决策，避免跨群噪音

## 数据存储格式

### 群信息源 (sources.json)

```json
{
  "chat_id": "oc_6ed1cc645057da3bbe93c6120219a61e",
  "sources": {
    "arxiv-ai": {
      "url": "https://arxiv.org/list/cs.AI",
      "tier": 1,
      "scores": {
        "relevance": 9.2,
        "quality": 8.5,
        "timeliness": 7.0,
        "diversity": 6.5,
        "reliability": 9.0,
        "accessibility": 8.0,
        "cost": 9.0
      },
      "discovered_at": "2026-04-15",
      "last_sampled": "2026-04-30",
      "sample_count": 45,
      "origin": "global"
    }
  }
}
```

### 用户偏好 (preferences.json)

```json
{
  "user_id": "ou_d366ba075912a3865430a7fe7020454b",
  "source_weights": {
    "arxiv-ai": 1.2,
    "techcrunch": 0.8
  },
  "topic_interests": ["LLM", "RLHF", "推理优化"],
  "risk_preference": "moderate"
}
```

## 与 core-thinking 的协作

1. **core-thinking Step 3 (价值发现)** — source-evolution 提供信息源支撑
2. **core-thinking Step 4 (价值链验证)** — source-evolution 提供证据链的数据源
3. **core-thinking 反哺 L1** — 价值发现揭示新信息源需求 → source-evolution 注册新源
4. **group-thinking 群记忆沉淀** — 新发现的信息源 → 触发 source-evolution 注册

## 使用时机

- 需要为群采集特定领域的信息时
- 评估新信息源的质量时
- 定期审视信息源健康度时
- 群讨论中暴露信息缺口时
- 价值链需要新数据支撑时
