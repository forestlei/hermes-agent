---
name: source-prospector
description: "信息源主动发现：从现有知识图谱、实体网络、引用链、生态系统中主动挖掘高质量信息源"
version: 1.3.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [reasoning, source, discovery, prospector, citation, entity, timeline, concept, knowledge-graph]
    related_skills: [concept-discovery, source-evolution, blogwatcher, arxiv, llm-wiki, core-thinking]
    category: reasoning
---

# Source Prospector — 信息源主动发现引擎

## 概述

从现有知识图谱、实体网络、引用链和生态系统中**主动**挖掘高质量信息源的技能。

与 `source-evolution` 的分工：**prospector 发现，evolution 管理**。

- `source-evolution`：被动触发（用户分享链接、讨论中暴露缺口）→ 评估 → 生命周期管理（评分、分级、淘汰）
- `source-prospector`：主动出击（从已有实体/引用/生态中挖掘）→ 产出候选源 → 交给 evolution 评估

发现的候选源进入 `source-evolution` 的 **Tier 4（观察源）**，由 evolution 的七维评分体系决定是否升级。

## 核心原则：时间线感知

信息源的质量和可发现性与**时间线**密切相关：

| 时间阶段 | 发现策略 | 典型场景 |
|----------|---------|---------|
| **萌芽期** | 关键词监控 + 领域会议追踪 | 新概念刚出现（如 2023 年的 MoE），只有预印本和会议讨论 |
| **上升期** | 引用链挖掘 + 作者追踪 | 论文开始被引用，社区开始讨论，博客和教程出现 |
| **成熟期** | 生态扫描 + 机构追踪 | 有了框架、工具链、企业采用，信息源多样化 |
| **衰退期** | 活跃度检测 + 替代源发现 | 讨论减少，核心作者转向新话题，需要发现替代视角 |

同一个实体在不同时间阶段需要不同的发现策略。时间线感知是 source-prospector 与通用 feed 发现工具的核心差异。

## 核心机制：概念驱动的发现

六种发现模式（引用链、实体追踪、生态扫描、事件驱动、跨领域演化、关键信号跟踪）回答了"从哪里发现"。但它们都依赖一个前置问题：**发现什么？** 这个问题由独立技能 `concept-discovery` 回答。

### 与 concept-discovery 的协作

```
concept-discovery（发现什么）
  │
  │  提供: 已确认概念列表 + 概念扩展搜索结果 + 概念生命周期状态
  │  消费: source-prospector 的发现结果反馈（新概念、新实体信号）
  │
  ├──→ 模式 1: 引用链挖掘 — 用确认的概念选择起始论文
  ├──→ 模式 2: 实体追踪 — 用概念关联选择追踪哪些实体
  ├──→ 模式 3: 生态扫描 — 用概念覆盖度判断缺失的源类型
  ├──→ 模式 4: 事件驱动 — 用概念时间线判断事件的影响范围
  └──→ 模式 5: 跨领域演化 — 用桥接概念发现跨领域迁移信号
```

**概念驱动的发现管线**（提取 → 验证 → 扩展 → 分析）由 `concept-discovery` 独立管理，包括：
- 关键概念提取（枢纽/前沿/桥接/缺口/衰退概念）
- 核心相关性验证（搜索引擎验证）
- 概念扩展搜索（深度/广度/时间/应用/批判）
- 扩展内容分析（概念密度/信息增量/权威性/时效性/可验证性）
- 反馈闭环（用户确认/拒绝 → 参数调整）
- 领域分化（不同领域有不同的提取范式和验证标准）

source-prospector 从 concept-discovery 获取已确认概念，驱动六种发现模式。发现结果中的新概念和新实体信号反馈给 concept-discovery。

详见 `skills/reasoning/concept-discovery/SKILL.md`。

## 六种发现模式

### 模式 1：引用链挖掘（Citation Mining）

从已知的优质论文/文章出发，沿引用链双向扩展。

**触发条件**：用户阅读一篇论文/文章后，或定期扫描 Tier 1 源的新引用时。

**操作流程**：

```
1. 输入：已知优质源的 ID（arXiv ID / DOI / URL）
2. 向前引用（谁引用了它）：
   curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:ID/citations?fields=title,authors,year,citationCount&limit=20"
3. 向后引用（它引用了谁）：
   curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:ID/references?fields=title,authors,year,citationCount&limit=20"
4. 筛选：citationCount > 阈值 AND 年份在关注范围内
5. 推荐：
   curl -s -X POST "https://api.semanticscholar.org/recommendations/v1/papers/" \
     -H "Content-Type: application/json" \
     -d '{"positivePaperIds": ["arXiv:ID1", "arXiv:ID2"], "negativePaperIds": []}'
6. 输出：候选源列表 → 交给 source-evolution 评估
```

**依赖技能**：`arxiv`（arXiv 搜索 + Semantic Scholar API）

**时间线适配**：
- 萌芽期：关注引用该论文的预印本（新方向信号）
- 上升期：关注高引用论文的引用链（影响力扩散路径）
- 成熟期：关注综述论文的引用（知识体系化信号）

### 模式 2：实体追踪（Entity Tracking）

从已知的作者、机构、公司出发，发现他们新发布的内容和新关联的源。

**触发条件**：定期扫描（cron），或用户提及某实体时。

**操作流程**：

```
1. 输入：实体名称（作者 / 机构 / 公司）
2. 作者追踪：
   curl -s "https://api.semanticscholar.org/graph/v1/author/search?query=NAME&fields=name,hIndex,citationCount,paperCount"
   → 获取 authorId → 查询最新论文
   curl -s "https://api.semanticscholar.org/graph/v1/author/AUTHOR_ID/papers?fields=title,year,citationCount&limit=10"
3. 公司/机构追踪：
   - GitHub 组织新仓库：web_extract(urls=["https://github.com/ORG"])
   - 官方博客新文章：blogwatcher-cli scan "ORG Blog"
   - 新闻提及：web_search("ORG + announcement")
4. 输出：实体新动态列表 → 提取新信息源候选
```

**实体数据来源**：
- `llm-wiki` 的 `entities/` 目录（人物、组织、产品页面）
- `source-evolution` 的 `sources.json`（已有源的作者/机构信息）
- 用户手动添加的实体

**时间线适配**：
- 萌芽期：追踪核心研究者的新方向（他们是最早的信号）
- 上升期：追踪企业/机构的采用动态（商业化信号）
- 成熟期：追踪标准化组织/监管机构（规范化信号）

**同伴对比（Peer Comparison）**：
实体追踪时必须同时追踪同类实体，用于 Beta/Alpha 分离：
- 追踪某公司时，同时追踪同行业 3-5 家可比公司
- 追踪某作者时，同时追踪同领域 2-3 位同行
- 对比目标实体与同伴实体的变化是否同步：
  - 同步变化 → 行业级 beta，需找行业驱动
  - 独立变化 → 实体级 alpha，需找个体驱动
- 示例：追踪百傲化学时，同时追踪同板块芯片股（寒武纪、芯原等），发现涨停是板块级 beta 而非公司级 alpha

### 模式 3：生态扫描（Ecosystem Scanning）

扫描某个领域的信息生态，发现当前缺失的源类型。

**触发条件**：用户请求领域扫描，或定期检查信息源覆盖度时。

**操作流程**：

```
1. 输入：领域/主题
2. 源类型覆盖度检查：
   - 学术论文源：arXiv, Semantic Scholar, Google Scholar
   - 技术博客源：Medium, Substack, 个人博客
   - 社区讨论源：Reddit, HackerNews, Discord
   - 新闻源：科技媒体, 行业媒体
   - 官方源：GitHub, 官方文档, 发布日志
   - 数据源：数据集, 基准测试, API
3. 对每种源类型，检查 source-evolution 中是否已有覆盖
4. 对缺失类型，执行定向搜索：
   - 博客：web_search("TOPIC blog RSS feed")
   - 社区：web_search("TOPIC subreddit OR discord OR forum")
   - GitHub：web_search("TOPIC awesome-list OR topic:TOPIC")
5. 输出：缺失类型 + 候选源 → 交给 source-evolution 评估
```

**时间线适配**：
- 萌芽期：学术论文 + 预印本为主，社区和博客尚未形成
- 上升期：博客和教程开始出现，awesome-list 开始整理
- 成熟期：企业文档、框架教程、标准化文档成为主要源
- 衰退期：社区讨论减少，需要寻找替代视角（如历史分析、跨领域应用）

**标签溢出检测（Label Overflow Detection）**：
生态扫描时必须检测概念标签的实质覆盖率：
- 扫描某主题的信息生态时，统计被归入该标签的实体数量
- 对每个实体，检验其是否满足概念标签的核心定义
- 计算标签溢出率 = 不满足核心定义的实体数 / 总实体数
- 溢出率 > 50% → 概念泡沫警告，需要区分"真受益源"和"纯标签源"
- 示例：太空光伏生态扫描发现 30+ 家公司被归入标签，但大部分无太空光伏技术储备——标签溢出率 > 80%

### 模式 4：事件驱动发现（Event-Driven Discovery）

由外部事件触发的新源发现。

**触发条件**：
- 重大发布（新模型、新框架、新标准）
- 学术会议（NeurIPS, ICML, ICLR 等的论文发布潮）
- 行业事件（融资、收购、政策变化）
- 关键人物发言（高影响力人物在权威场合的发言）
- `core-thinking` L3 价值发现揭示新需求

**操作流程**：

```
1. 输入：事件描述
2. 事件解析：提取关键实体（谁）、领域（什么）、时间线（何时）
3. 事件角色判定（关键步骤——避免近因偏差）：
   a. 检查事件前是否已有同方向趋势（反事实检验）
   b. 如果已有趋势 → 事件是"放大器"，不是"起爆点"
   c. 如果无前趋势 → 事件可能是"起爆点"
   d. 放大器和起爆点的发现策略不同：
      - 起爆点 → 搜索全新领域的源
      - 放大器 → 搜索已有领域的深化源和扩散源
4. 围绕事件发现新源：
   - 会议论文潮：arXiv 搜索 + Semantic Scholar 按会议筛选
   - 新框架发布：GitHub trending + awesome-list 更新
   - 行业事件：新闻源 + 分析师报告 + 社区讨论
   - 关键人物发言：追踪发言者的关联实体 + 概念标签传导
5. 概念标签传导追踪（金融领域特化）：
   a. 识别发言创造的概念标签（如"太空光伏"）
   b. 追踪标签的市场传导路径（发言→媒体→概念统一→资金涌入）
   c. 用标签溢出检测评估概念实质覆盖率
   d. 区分"真受益源"和"纯标签源"
6. 输出：事件相关候选源 + 事件角色标注（起爆点/放大器/无关）→ 交给 source-evolution 评估
```

**与 core-thinking 的协作**：
- `core-thinking` Step 3（价值发现）揭示新信息需求 → 触发 source-prospector 事件驱动发现
- source-prospector 发现的新源 → 通过 source-evolution 进入信息体系 → 支撑后续价值发现

**时间线适配**：
- 事件本身就是时间线节点，发现策略随事件阶段调整
- 事件前：关注预告和预测源
- 事件中：关注实时报道和第一手分析
- 事件后：关注深度分析和影响评估
- **关键教训**：事件后的源发现必须区分"事件驱动的新源"和"已有趋势被事件放大后暴露的源"——后者在事件前就存在，只是未被注意到

### 模式 5：跨领域演化发现（Cross-Domain Evolution）

当一个领域的模式在另一个领域出现时，提前发现新源。

**触发条件**：检测到跨领域模式迁移信号时。

**操作流程**：

```
1. 输入：源领域 + 目标领域 + 迁移模式
2. 在源领域中，找到推动该模式的关键实体（作者、机构）
3. 追踪这些实体在目标领域的新活动
4. 在目标领域中搜索该模式的相关讨论
5. 输出：跨领域候选源 → 交给 source-evolution 评估
```

**示例**：
- Transformer 从 NLP 迁移到 CV → 追踪 NLP 研究者的 CV 论文
- RLHF 从对齐迁移到代码生成 → 追踪对齐研究者的代码生成工作
- MLOps 从软件工程迁移到 AI 工程 → 追踪 DevOps 工具的 AI 适配

**时间线适配**：
- 萌芽期：少数跨领域研究者的预印本
- 上升期：跨领域研讨会和教程出现
- 成熟期：跨领域框架和工具链成熟

### 模式 6：关键信号跟踪（Key Signal Tracking）

**核心问题**：如何知道关键人物发言了？如何知道重大事件发生了？——更关键的是：**什么时候该密集跟踪，什么时候该放松？跟踪密度怎么动态调整？**

#### 6.1 事件生命周期与跟踪密度

跟踪密度不是固定的。一个事件从"可能发生"到"影响消退"，跟踪密度需要经历5个阶段的动态调整：

```
阶段1: 远期观察（事件前7-30天）
  密度：低（每周1次扫描日历）
  操作：确认事件是否会发生，谁会出席

阶段2: 近期预警（事件前1-7天）
  密度：中（每日1次扫描数据源）
  操作：提取关键人物+关键概念，部署监控关键词

阶段3: 实时跟踪（事件当天）
  密度：高（每2小时扫描一次数据源）
  操作：检测发言内容，提取新概念，实时分级

阶段4: 影响确认（事件后1-3天）
  密度：高→中（第1天每2小时，第2-3天每4小时）
  操作：检测市场/社区反应，确认传导路径，检测标签溢出

阶段5: 衰减观察（事件后4-14天）
  密度：低（每周1次）
  操作：检测二次传导，确认影响消退，总结范式
```

**密度升级的核心规则**：

```
升级条件（从低→中）：
  a. 日历扫描发现未来7天内有重大事件
  b. 关键人物在社交媒体预告将出席/发言
  c. Layer 3 回溯检测到异常，且归因到即将发生的事件

升级条件（从中→高）：
  a. 事件当天（日历触发）
  b. 关键人物在事件前24小时内发布相关内容
  c. 多个P1+数据源同时出现相关关键词

降级条件（从高→中）：
  a. 事件主体活动结束（如达沃斯闭幕）
  b. 连续2次扫描未检测到新信号
  c. 市场/社区反应已确认并记录

降级条件（从中→低）：
  a. 事件后3天无新信号
  b. 标签溢出率已计算，概念已拆分
  c. 范式已总结写入 paradigms.json
```

#### 6.2 密度升级的具体时序表

以"马斯克出席达沃斯"为例，展示每个时间点**具体做什么**：

| 时间点 | 阶段 | 密度 | 具体操作 | 数据源 | 触发条件 |
|---|---|---|---|---|---|
| 1月初 | 远期观察 | 低/周1次 | web_extract WEF官网日程 → 确认马斯克出席 | weforum.org/events | 日历扫描命中 |
| 1月13日（前7天） | 近期预警 | 中/日1次 | 提取马斯克关键词 + 搜索近期X发帖 | X API + web_search | 日历触发：7天内 |
| 1月20日（前2天） | 近期预警 | 中/日2次 | 马斯克X发帖"太空1TW AI" → 提取概念"太空光伏" | X API | 关键人物发布相关内容 |
| 1月22日（当天） | 实时跟踪 | 高/2h1次 | 检测达沃斯发言 → 交叉验证 → Level 1信号 | X API + 东方财富 | 事件当天 |
| 1月22日晚 | 实时跟踪 | 高/2h1次 | concept-discovery 提取太空光伏/机器人/AI奇点 | 内部 | Level 1 信号触发 |
| 1月23日（后1天） | 影响确认 | 高/2h1次 | 检测A股开盘反应 → 30+涨停 → 确认传导 | 东方财富 + 龙虎榜 | A股开盘 |
| 1月23日 | 影响确认 | 高 | 标签溢出检测 → 83%无实质关联 → 拆分子概念 | 巨潮资讯 + 东方财富 | 涨停潮出现 |
| 1月24日（后2天） | 影响确认 | 中/4h1次 | 检测分化信号 → 龙头继续 vs 跟风回落 | 东方财富 | 连续2次无新信号 |
| 1月27日（后5天） | 衰减观察 | 低/周1次 | 总结范式：马斯克权威场合发言→概念标签统一→涨停潮→标签溢出→分化 | 内部 | 3天无新信号 |
| 2月4日（后13天） | 衰减观察 | 低 | SpaceX并购xAI + 走访中国光伏 → 重新升级到中 | X API + web_search | 新信号出现 |

**关键洞察**：密度不是均匀的，而是**脉冲式**的——事件前低频，事件当天高频，事件后逐步衰减。如果衰减期出现新信号，则重新升级。

#### 6.3 三层检测与密度升级的集成

三层架构（日历层/快讯层/回溯层）不是独立的——它们共同驱动密度升级：

```
┌──────────────────────────────────────────────────────────────────┐
│                    密度状态机（Density State Machine）              │
│                                                                  │
│  状态：LOW ──→ MEDIUM ──→ HIGH ──→ MEDIUM ──→ LOW              │
│        ↑          ↑          │          │          │              │
│        │          │          │          │          │              │
│   ┌────┘     ┌────┘     ┌────┘     ┌────┘     ┌────┘              │
│   │          │          │          │          │                   │
│  L1日历     L1日历     L2快讯     L2/L3      L2/L3               │
│  命中7天    命中1天    命中当天    无新信号   无新信号3天           │
│  或L3异常  或L2预告   或L2多源    连续2次    +范式总结            │
│  归因到     关键人物   同时出现                               │
│  即将事件   发布相关    关键词                                  │
│                                                                  │
│  每个状态对应的扫描频率：                                        │
│  LOW:    日历=周1次, 快讯=日1次, 回溯=日1次                      │
│  MEDIUM: 日历=日1次, 快讯=日2次, 回溯=日1次                      │
│  HIGH:   日历=日1次, 快讯=2h1次, 回溯=4h1次                      │
└──────────────────────────────────────────────────────────────────┘
```

**状态转换的精确规则**：

```
LOW → MEDIUM（升级）：
  触发条件（满足任一）：
  a. Layer 1 日历扫描发现未来7天内有重大事件
  b. Layer 3 回溯检测到异常，且归因到即将发生的事件
  c. 关键人物在社交媒体预告将出席/发言（Layer 2 检测）
  动作：
  - 提取事件关联的关键人物列表
  - 提取事件关联的关键概念列表（从历史同类事件推断）
  - 部署 Layer 2 监控关键词
  - 预加载历史背景

MEDIUM → HIGH（升级）：
  触发条件（满足任一）：
  a. 事件当天（日历时间触发）
  b. 关键人物在事件前24小时内发布相关内容
  c. 多个P1+数据源同时出现相关关键词（≥2源，≥2关键词）
  d. 立法/行政确认事件（法案通过委员会/行政令签署/监管裁决生效）——直接MEDIUM→HIGH，无需等待日历触发
  e. 供应链冲击确认（断供通知/制裁生效/产能中断公告）——直接MEDIUM→HIGH
  动作：
  - Layer 2 扫描频率提升到每2小时
  - Layer 3 扫描频率提升到每4小时
  - 准备 concept-discovery 触发模板
  - 对触发条件d/e：立即触发产业链传导推演（调用concept-discovery能力6-8）

HIGH → MEDIUM（降级）：
  触发条件（满足全部）：
  a. 事件主体活动结束
  b. 连续2次 Layer 2 扫描未检测到新信号
  c. 市场/社区反应已确认并记录
  动作：
  - Layer 2 扫描频率降回日2次
  - Layer 3 扫描频率降回日1次
  - 开始标签溢出检测

MEDIUM → LOW（降级）：
  触发条件（满足全部）：
  a. 事件后3天无新信号
  b. 标签溢出率已计算，概念已拆分
  c. 范式已总结写入 paradigms.json
  动作：
  - 所有扫描频率降回 LOW
  - 事件标记为 completed
  - 经验数据写入 experience.json
```

#### 6.4 具体数据源与操作

**Layer 1: 日历层 — 已知信号的预部署**

| 事件类型 | 数据源 | 访问方式 | 扫描频率（按状态） |
|---|---|---|---|
| 全球重大会议 | WEF/IMF/G20官网 | web_extract | LOW=周1, MED=日1, HIGH=日1 |
| 中国政策发布 | 国务院/证监会公告 | web_extract | LOW=周1, MED=日1, HIGH=日1 |
| 财报季 | 巨潮资讯网 | web_extract | LOW=季1, MED=日1, HIGH=日1 |
| 央行议息 | Fed/ECB/PBOC | RSS/官网 | LOW=周1, MED=日1, HIGH=日1 |
| 行业大会 | 行业协会官网 | web_extract | LOW=月1, MED=周1, HIGH=日1 |

**Layer 2: 快讯层 — 实时信号检测**

| 优先级 | 数据源 | 延迟 | 访问方式 | 扫描频率（按状态） |
|---|---|---|---|---|
| P0 | X/Twitter API | 秒级 | API | LOW=日1, MED=日2, HIGH=2h |
| P0 | 新浪财经快讯 | 分钟级 | RSS | LOW=日1, MED=日2, HIGH=2h |
| P1 | 东方财富快讯 | 分钟级 | web_extract | LOW=日1, MED=日2, HIGH=2h |
| P1 | 证监会公告 | 分钟级 | web_extract | LOW=日1, MED=日2, HIGH=4h |
| P2 | 路透/彭博 RSS | 分钟级 | RSS | LOW=日1, MED=日1, HIGH=4h |
| P2 | 36氪/虎嗅 | 分钟级 | RSS/web | LOW=周1, MED=日1, HIGH=日2 |
| P3 | Reddit/HN | 小时级 | API | LOW=周1, MED=日1, HIGH=日1 |
| P3 | 微博热搜 | 小时级 | web_extract | LOW=日1, MED=日2, HIGH=4h |

**Layer 3: 回溯层 — 异常驱动的信号发现**

| 信号类型 | 数据源 | 检测方法 | 扫描频率（按状态） |
|---|---|---|---|
| 板块异动 | 东方财富板块数据 | 涨幅>3% 且 量>2x均量 | LOW=日1, MED=日1, HIGH=4h |
| 个股异动 | 龙虎榜 | 机构净买>1亿 | LOW=日1, MED=日1, HIGH=4h |
| 舆论异动 | 微博/知乎热搜 | 关键词入Top50 | LOW=日1, MED=日1, HIGH=日2 |
| 学术异动 | arXiv | 领域论文突增 | LOW=周1, MED=周1, HIGH=日1 |
| 技术异动 | GitHub trending | 新项目入trending | LOW=周1, MED=周1, HIGH=日1 |

#### 6.5 信号检测与分级逻辑

```
Step 1: 信号采集（按当前状态的频率执行）
  输入：watch_list.json + 数据源列表 + 当前密度状态
  操作：按频率检查每个数据源
  输出：raw_signals.json — {timestamp, source, person, content_snippet, keywords_matched}

Step 2: 信号过滤（去噪）
  规则：
  a. 关键词匹配数 >= 2 → 保留
  b. 来源可信度 >= P1 → 保留（P3需额外验证）
  c. 内容去重（同一事件24h内只保留最早信号）
  输出：filtered_signals.json

Step 3: 信号验证（交叉验证）
  a. P0来源 → 直接确认
  b. P1来源 → 需另一个P1+确认
  c. P2/P3 → 需P0或两个P1+确认
  输出：verified_signals.json

Step 4: 信号分级
  a. 关键人物 + 权威场合 + 多源确认 → Level 1
  b. 关键人物 + 非权威场合 + 多源确认 → Level 2
  c. 非关键人物 + 权威场合 + 多源确认 → Level 2
  d. 单源信号 → Level 3
  输出：graded_signals.json

Step 5: 密度调整判断
  Level 1 信号 → 立即升级到 HIGH（无论当前状态）
  Level 2 信号 → 如果当前 LOW，升级到 MEDIUM
  Level 3 信号 → 不改变密度状态
  同时检查降级条件是否满足
  输出：density_state_update.json

Step 6: 触发动作
  Level 1 + HIGH → 立即触发 concept-discovery + 事件驱动发现
  Level 2 + MEDIUM → 加入待分析队列
  Level 3 → 仅记录
  密度降级 → 更新 cron 任务频率
```

#### 6.6 关键人物跟踪表（watch_list.json）

```json
{
  "watch_list": [
    {
      "person_id": "elon-musk",
      "name": "Elon Musk",
      "platforms": {
        "twitter": {"handle": "@elonmusk", "last_checked": "2026-05-03T08:00:00Z"},
        "weibo": null
      },
      "keywords": ["AI", "space", "solar", "robot", "Optimus", "Starship", "Tesla"],
      "impact_domains": ["space-solar", "ev", "ai-chips", "robotics"],
      "authority_events": ["WEF Davos", "Tesla Earnings Call", "GTC", "SpaceX Launch"],
      "detection_history": {
        "total_detections": 12,
        "false_positives": 2,
        "precision": 0.83,
        "last_detection": "2026-01-22",
        "last_event": "davos-2026"
      }
    }
  ],
  "density_state": {
    "current": "LOW",
    "last_transition": "2026-04-28",
    "transition_reason": "no new signals for 3 days, paradigm summarized",
    "active_events": []
  },
  "meta": {
    "total_persons": 2,
    "last_full_scan": "2026-05-03T08:00:00Z"
  }
}
```

#### 6.7 事件跟踪表（active_events.json）

当密度升级到 MEDIUM 或 HIGH 时，创建事件跟踪记录：

```json
{
  "active_events": [
    {
      "event_id": "davos-2026",
      "name": "WEF Davos 2026",
      "date_range": ["2026-01-20", "2026-01-24"],
      "key_persons": ["elon-musk", "jensen-huang"],
      "key_concepts": ["space-solar", "humanoid-robot", "AI-singularity"],
      "density_state": "HIGH",
      "state_transitions": [
        {"date": "2026-01-13", "from": "LOW", "to": "MEDIUM", "reason": "calendar: 7 days before event"},
        {"date": "2026-01-20", "from": "MEDIUM", "to": "HIGH", "reason": "event day 1"},
        {"date": "2026-01-24", "from": "HIGH", "to": "MEDIUM", "reason": "event ended, 2 scans no new signal"},
        {"date": "2026-01-27", "from": "MEDIUM", "to": "LOW", "reason": "3 days no new signal, paradigm summarized"}
      ],
      "signals_detected": [
        {"timestamp": "2026-01-20T14:00:00Z", "person": "elon-musk", "source": "X API", "level": 2, "content": "1TW AI in space"},
        {"timestamp": "2026-01-22T10:00:00Z", "person": "elon-musk", "source": "X API + 东方财富", "level": 1, "content": "达沃斯发言：太空AI数据中心2-3年实现"}
      ],
      "market_reactions": [
        {"date": "2026-01-23", "dimension": "板块涨幅", "value": "光伏+5.2%", "mean": "0.1%", "sigma": "1.2%", "deviation": "4.3σ"},
        {"date": "2026-01-23", "dimension": "涨停家数", "value": "30+", "mean": "2", "sigma": "3", "deviation": "9.3σ"}
      ],
      "label_overflow": {
        "detected": true,
        "rate": 0.83,
        "true_beneficiaries": ["迈为股份", "东方日升"],
        "label_only": ["钧达股份", "隆基绿能", "其他27家"]
      },
      "paradigm": {
        "generated": true,
        "paradigm_id": "p-finance-002",
        "summary": "马斯克权威场合发言→概念标签统一→A股涨停潮→标签溢出→分化"
      }
    }
  ]
}
```

#### 6.8 自证：密度调整是否有效

| 指标 | 计算方法 | 目标 | 不达标时的动作 |
|---|---|---|---|
| 升级及时性 | 信号发生→密度升级到HIGH的时间 | < 4h | 增加L2扫描频率或P0数据源 |
| 降级及时性 | 最后一个信号→密度降回LOW的时间 | < 5天 | 检查降级条件是否过严 |
| HIGH期信号命中率 | HIGH状态下检测到的真实信号数 / 总真实信号数 | > 0.8 | 如果低，说明升级太晚 |
| LOW期误扫描率 | LOW状态下扫描但无信号的次数 / LOW期总扫描次数 | < 0.7 | 如果高，说明降级太慢，浪费资源 |
| 密度转换次数 | 每月 LOW↔MEDIUM↔HIGH 的转换次数 | 3-15 | <3说明太迟钝，>15说明太敏感 |

#### 6.9 马斯克达沃斯案例：密度调整全流程

```
1月初：LOW状态，周1次日历扫描
  → 发现达沃斯1月20-24日，马斯克出席
  → 触发升级条件(a)：日历命中7天内
  → LOW → MEDIUM

1月13日：MEDIUM状态，日1次扫描
  → 提取马斯克关键词，部署L2监控
  → 无新信号，维持MEDIUM

1月20日：MEDIUM状态
  → 触发升级条件(a)：事件当天
  → MEDIUM → HIGH
  → L2扫描频率提升到2h

1月20日14:00：HIGH状态
  → L2检测到马斯克X发帖"1TW AI in space"
  → 关键词匹配：AI✓ space✓ → 2关键词
  → P0来源直接确认 → Level 2信号
  → 无需升级（已在HIGH）

1月22日10:00：HIGH状态
  → L2检测到X API + 东方财富双源确认达沃斯发言
  → 关键人物 + 权威场合 + 多源确认 → Level 1信号
  → 立即触发 concept-discovery

1月23日09:30：HIGH状态
  → A股开盘，L3检测到光伏板块涨幅5.2%（4.3σ异常）
  → 确认传导路径：马斯克发言→概念统一→资金涌入
  → 标签溢出检测：30+涨停，83%无实质关联

1月24日：HIGH状态
  → 达沃斯闭幕
  → 连续2次L2扫描无新信号
  → 触发降级条件(a)(b) → HIGH → MEDIUM

1月27日：MEDIUM状态
  → 3天无新信号
  → 范式已总结（p-finance-002）
  → 触发降级条件(a)(b)(c) → MEDIUM → LOW

2月4日：LOW状态
  → L2检测到SpaceX并购xAI + 马斯克走访中国光伏企业
  → 新信号出现 → LOW→ MEDIUM（重新激活）
```

**验证密度调整有效性**：
- 升级及时性：1月20日事件当天升级到HIGH ✅（<4h）
- HIGH期信号命中率：2个真实信号都在HIGH期检测到 = 1.0 ✅（>0.8）
- 降级及时性：1月27日降回LOW，距最后信号4天 ✅（<5天）
- LOW期误扫描率：2月4日前LOW期扫描约8次，7次无信号 = 0.875 ⚠️（略高，但2月4日重新激活证明LOW期扫描仍有价值）

## 数据模型

### 实体注册表（entities.json）

记录需要追踪的实体，是所有发现模式的基础数据。

```json
{
  "entities": {
    "author:yann-lecun": {
      "type": "author",
      "name": "Yann LeCun",
      "semantic_scholar_id": "1745242",
      "domains": ["computer-vision", "self-supervised-learning"],
      "tracked_since": "2026-04-15",
      "last_scanned": "2026-04-30",
      "scan_frequency": "weekly",
      "discovered_sources": ["arxiv-lecun-ssl", "facebook-research-blog"]
    },
    "org:anthropic": {
      "type": "organization",
      "name": "Anthropic",
      "github_org": "anthropics",
      "domains": ["ai-safety", "constitutional-ai"],
      "tracked_since": "2026-04-15",
      "last_scanned": "2026-04-30",
      "scan_frequency": "weekly",
      "discovered_sources": ["anthropic-blog", "anthropic-research"]
    },
    "company:nous-research": {
      "type": "company",
      "name": "Nous Research",
      "domains": ["open-source-llm", "rl-training"],
      "tracked_since": "2026-04-20",
      "last_scanned": "2026-04-30",
      "scan_frequency": "biweekly",
      "discovered_sources": []
    }
  }
}
```

### 发现日志（discovery_log.json）

记录每次发现的结果，用于去重和效果追踪。

```json
{
  "log": [
    {
      "id": "disc-001",
      "timestamp": "2026-05-01T10:30:00Z",
      "mode": "citation_mining",
      "trigger": "periodic_scan",
      "input_entity": "arxiv:2402.03300",
      "event_role": null,
      "candidates_found": 5,
      "candidates": [
        {
          "source_id": "arxiv:2403.12345",
          "title": "Improved GRPO with Multi-Objective Rewards",
          "reason": "Cited by arxiv:2402.03300, citationCount=12",
          "passed_to_evolution": true,
          "evolution_status": "tier4_observing"
        }
      ]
    },
    {
      "id": "disc-finance-001",
      "timestamp": "2026-01-23T09:00:00Z",
      "mode": "event_driven",
      "trigger": "musk_davos_speech",
      "input_entity": "马斯克达沃斯发言",
      "event_role": "amplifier",
      "candidates_found": 12,
      "candidates": [
        {
          "source_id": "eastmoney-space-solar",
          "title": "太空光伏概念全线爆发",
          "reason": "马斯克达沃斯发言放大已有太空光伏趋势，30+股涨停",
          "passed_to_evolution": true,
          "evolution_status": "tier4_observing",
          "label_overflow_detected": true,
          "label_overflow_rate": 0.83
        }
      ]
    }
  ]
}
```

### 扫描计划（scan_schedule.json）

定义定期扫描的频率和范围。

```json
{
  "schedules": {
    "citation_mining_weekly": {
      "mode": "citation_mining",
      "frequency": "weekly",
      "scope": "tier1_sources",
      "last_run": "2026-04-30",
      "next_run": "2026-05-07"
    },
    "entity_tracking_weekly": {
      "mode": "entity_tracking",
      "frequency": "weekly",
      "scope": "all_entities",
      "last_run": "2026-04-30",
      "next_run": "2026-05-07"
    },
    "ecoscan_monthly": {
      "mode": "ecosystem_scanning",
      "frequency": "monthly",
      "scope": "active_themes",
      "last_run": "2026-04-15",
      "next_run": "2026-05-15"
    },
    "event_driven_on_demand": {
      "mode": "event_driven",
      "frequency": "on_demand",
      "scope": "event_context"
    },
    "signal_calendar_weekly": {
      "mode": "signal_tracking_layer1",
      "frequency": "weekly",
      "scope": "upcoming_events_30d",
      "last_run": "2026-05-01",
      "next_run": "2026-05-08"
    },
    "signal_wire_4h": {
      "mode": "signal_tracking_layer2",
      "frequency": "every_4h",
      "scope": "watch_list",
      "last_run": "2026-05-03T08:00:00Z",
      "next_run": "2026-05-03T12:00:00Z"
    },
    "signal_retro_daily": {
      "mode": "signal_tracking_layer3",
      "frequency": "daily",
      "scope": "market_anomalies",
      "last_run": "2026-05-03",
      "next_run": "2026-05-04"
    }
  }
}
```

## 与其他技能的集成

### concept-discovery（概念发现）

- concept-discovery 提供已确认概念列表 → prospector 用概念驱动六种发现模式（含关键信号跟踪）
- prospector 的发现结果中的新概念信号 → 反馈给 concept-discovery
- prospector 不自己提取/验证/扩展概念，这些由 concept-discovery 独立管理

### source-evolution（核心集成点）

**数据流**：source-prospector → source-evolution

```
prospector 发现候选源
  → 构造候选源描述（URL, 名称, 发现原因, 推荐评分）
  → 写入 source-evolution 的全局候选池（L0）
  → source-evolution 按七维评分评估
  → 进入 Tier 4（观察源）
  → 30 天观察期后决定升级或淘汰
```

**prospector 不做的事**：
- 不管理源的生命周期（升级/降级/淘汰）
- 不做七维评分（那是 evolution 的职责）
- 不修改已有源的评分或 Tier
- 不跨群同步源（evolution 的群间传播机制处理）

**prospector 做的事**：
- 主动发现新候选源
- 提供发现原因和推荐理由（辅助 evolution 评估）
- 维护实体注册表和扫描计划
- 追踪发现效果（候选源最终是否升级到 Tier 1-3）

### blogwatcher（RSS 监控）

- prospector 发现新博客 → 用 `blogwatcher-cli add` 添加监控
- blogwatcher 的 auto feed discovery 是 prospector 模式 3（生态扫描）的子能力
- prospector 不重复实现 RSS 发现，而是调用 blogwatcher

### arxiv（学术源发现）

- prospector 的模式 1（引用链挖掘）和模式 2（作者追踪）依赖 arxiv 技能的 Semantic Scholar API
- prospector 不重复实现 API 调用，而是引用 arxiv 技能的端点和参数

### llm-wiki（知识库）

- llm-wiki 的 `entities/` 目录是 prospector 实体注册表的种子数据来源
- prospector 发现的新实体 → 建议写入 llm-wiki 的 entities 层
- 双向：wiki 提供已知实体 → prospector 追踪 → 新发现反哺 wiki

### core-thinking（价值发现）

- core-thinking L3 价值发现 → 触发 prospector 事件驱动发现
- prospector 发现的新源 → 通过 evolution 支撑后续价值发现

## 使用时机

- 需要为某个主题主动寻找新信息源时
- 定期扫描已有源和实体的新动态时
- 领域知识出现缺口，需要补全源覆盖时
- 重大事件发生后，需要快速发现相关源时
- 检测到跨领域模式迁移，需要提前布局时

## 操作命令

### 手动触发

```
/prospector citation <arxiv_id>           # 从指定论文的引用链发现新源
/prospector entity <entity_name>          # 追踪指定实体的新动态
/prospector ecoscan <topic>               # 扫描指定主题的信息生态
/prospector event <event_desc>            # 事件驱动发现
/prospector cross <source> <target>       # 跨领域演化发现
/prospector status                        # 查看发现引擎状态
/prospector schedule                      # 查看扫描计划
```

### 定期扫描（cron）

```bash
# 每周引用链挖掘（扫描 Tier 1 源的新引用）
hermes cron add "prospector citation scan" --schedule "0 9 * * 1" --prompt "/prospector citation --auto"

# 每周实体追踪
hermes cron add "prospector entity scan" --schedule "0 10 * * 1" --prompt "/prospector entity --auto"

# 每月生态扫描
hermes cron add "prospector ecoscan" --schedule "0 9 1 * *" --prompt "/prospector ecoscan --auto"
```

## 发现效果追踪

每次发现的结果都记录在 `discovery_log.json` 中，并追踪后续效果：

| 指标 | 含义 | 计算方式 |
|------|------|---------|
| **发现率** | 每次扫描发现的候选源数量 | candidates_found / scans |
| **转化率** | 候选源最终升级到 Tier 1-3 的比例 | upgraded_sources / total_candidates |
| **时效性** | 从源首次发布到被发现的时间差 | discovered_at - first_published_at |
| **覆盖度** | 各源类型的覆盖比例 | covered_types / total_types |

每月生成一次效果报告，用于调整扫描频率和发现策略。

## 数据存储

```
~/.hermes/skills/reasoning/source-prospector/
├── entities.json          # 实体注册表
├── discovery_log.json     # 发现日志（append-only，超过 500 条轮转）
├── scan_schedule.json     # 扫描计划
├── effectiveness.json     # 效果追踪数据
├── watch_list.json        # 关键人物跟踪表（Layer 2 快讯层）
├── upcoming_events.json   # 事件日历（Layer 1 日历层）
├── anomalies.json         # 异常记录（Layer 3 回溯层）
└── signal_metrics.json    # 三层检测的月度验证指标
```

遵循 source-evolution 的 L0/L1/L2 数据模型：
- 实体注册表和扫描计划在 L0（全局）
- 发现日志按群维度隔离（L1）
- 效果追踪在 L0（全局统计）

## 注意事项

- **不要替代 source-evolution**：prospector 只发现，不管理。评分、分级、淘汰全部交给 evolution。
- **不要重复实现已有能力**：RSS 发现用 blogwatcher，论文搜索用 arxiv，网页抓取用 web_search/web_extract。
- **尊重 API 速率限制**：Semantic Scholar 1 req/sec（无 key），arXiv ~1 req/3sec。批量扫描时加入延迟。
- **发现不是订阅**：prospector 发现候选源后，由 evolution 决定是否纳入监控。prospector 不直接添加 RSS 订阅。
- **时间线感知是核心**：同一个发现策略在不同时间阶段的效果差异巨大。始终根据实体的时间阶段调整策略。
- **实体注册表需要维护**：定期清理不再活跃的实体，避免无效扫描浪费 API 配额。
- **发现日志需要轮转**：超过 500 条时重命名为 `discovery_log-YYYY.json`，开始新文件。

## 实战教训（Real-World Test Lessons）

以下教训来自两个真实调查案例的验证：

### 案例 1：百傲化学股价调查

**场景**：调查百傲化学2026年4月30日涨停原因，并分析芯片股大涨对百傲化学远期预期的影响。

**关键教训**：
1. **近因偏差是最大的分析陷阱**：最初将涨停归因为回购公告（4月29日发布），忽略了当日芯片股集体涨停潮（寒武纪/芯原/明微20%涨停，科创芯片ETF+6.46%）。回购公告是锦上添花，不是主因。
2. **同伴对比是发现 beta 的关键**：只有同时查看同板块芯片股的表现，才能发现涨停是板块级现象而非公司级事件。
3. **滞后性是重要信号**：百傲化学的涨停滞后于核心芯片股，说明它是"跟涨"而非"领涨"——这是 beta 驱动的特征。
4. **自上而下的搜索路径**：从宏观（MATCH法案+华虹断供）→ 行业（国产替代）→ 业绩（Q1超预期）→ 公司（回购催化），才能找到完整因果链。
5. **产业链传导推演不能只看报告**：百傲化学控股芯慧联54.63%，需要独立推演芯片业绩暴增→晶圆厂扩产→设备需求→涂胶显影国产化率5-10%→芯慧联受益的完整传导链，每步需数据锚点。
6. **估值前置检测避免"发现已被定价的机会"**：股价已从15元→38元（3.4x），隐含半导体价值100-130亿 vs 乐观PE仅50-60亿。市场已提前定价远期重估——这是"验证型机会"而非"发现型机会"。
7. **机构行为比报告更真实**：芯慧联4家专业机构投资者在百傲化学增资时全部低价清仓退出——他们用脚投票说明不认为是优质资产。"捡漏"叙事需要解释这个矛盾。
8. **护城河耐久性决定机会类型**：光刻机再制造=政策依赖型护城河（3-5yr），方向自我削弱（设备存量老化→国产替代→再制造机会缩小）。涂胶显影自研=尚未量产验证。政策依赖型护城河是验证型机会，结构性护城河才是发现型机会。
9. **立法/行政确认=直接MEDIUM→HIGH**：MATCH法案3/26提出→4/2正式引入→4/22外委会通过，每次立法进展都应触发密度升级。7天日历预警不够——立法确认本身就是升级信号。

**对 source-prospector 的改进**：
- 实体追踪模式增加"同伴对比"子步骤
- 事件驱动模式增加"事件角色判定"（起爆点 vs 放大器）
- 金融领域搜索路径必须自上而下
- Mode 6 MEDIUM→HIGH升级触发增加条件d（立法/行政确认）和条件e（供应链冲击确认）
- 产业链传导推演触发：当立法/供应链冲击触发HIGH密度时，立即调用concept-discovery能力6-8
- 密度升级不仅关注"事件时间"，更要关注"事件确认"——法案通过委员会比会议日期更重要

### 案例 2：马斯克达沃斯发言→概念股大涨

**场景**：分析马斯克2026年1月达沃斯发言如何引发A股太空光伏概念股大涨。

**关键教训**：
1. **信号放大器 ≠ 信号起爆点**：马斯克达沃斯发言放大了已有的太空光伏趋势（1月21日已有异动），但不是趋势的起点。1月23日30+涨停潮的规模远超前日，说明放大器可以极大增强信号强度。
2. **概念标签在传播中会膨胀**：从"太空光伏HJT设备"扩展到"所有光伏股"——标签溢出率 > 80%。大部分涨停公司2025年业绩亏损，太空光伏度电成本是地面光伏的百倍。
3. **行业深冬中的概念炒作反弹力度更大**：光伏行业供需严重错配，长期压抑的反弹需求在概念标签统一后集中释放——这是情绪蓄水池效应。
4. **概念生命周期可追踪**：从2025-12月萌芽→1月引爆→2月常态化，概念的生命周期阶段决定了发现策略。

**对 source-prospector 的改进**：
- 生态扫描模式增加"标签溢出检测"
- 事件驱动模式增加"概念标签传导追踪"
- 发现日志增加"事件角色"字段（起爆点/放大器/无关）

## 补充技能参考

以下技能与 source-prospector 的发现模式互补，但属于不同领域，不作为核心依赖：

| 技能 | 互补场景 | 使用方式 |
|------|---------|---------|
| `domain-intel` | 实体追踪时发现组织的基础设施（子域名、证书） | 模式 2 的补充 OSINT 手段 |
| `sherlock` | 实体追踪时发现作者/组织的社交媒体账号 | 模式 2 的补充实体发现 |
| `webhook-subscriptions` | 事件驱动发现的外部触发机制 | 模式 4 的自动化触发通道 |
| `literature-review-agent` | 学术论文候选发现 + 验证流水线 | 模式 1 在论文写作场景的特化版本 |
| `scrapling` | 生态扫描时的多页面内容采集 | 模式 3 的深度内容获取 |
