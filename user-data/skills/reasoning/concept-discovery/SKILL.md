---
name: concept-discovery
description: "关键概念发现：从知识图谱中提取、验证、扩展关键概念，积累领域经验，持续进化发现范式"
version: 1.3.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [reasoning, concept, discovery, knowledge-graph, domain-adaptive, feedback-loop]
    related_skills: [source-prospector, source-evolution, llm-wiki, core-thinking, group-thinking]
    category: reasoning
---

# Concept Discovery — 关键概念发现引擎

## 概述

从知识图谱中**提取、验证、扩展**关键概念的独立技能。与"知识体系"同级别，是信息收集和信息源发现的上游认知能力。

**核心定位**：关键概念发现是信息收集的"眼睛"——在信息爆炸中，先知道"看什么"比"怎么看"更重要。

**与 source-prospector 的分工**：
- `concept-discovery`：发现和确认关键概念（发现什么）
- `source-prospector`：用确认的概念驱动信息源发现（从哪里发现）

**与 source-evolution 的分工**：
- `concept-discovery`：提供概念维度的信息源评估依据
- `source-evolution`：管理信息源的全生命周期

## 为什么独立

关键概念发现需要独立发展，原因有三：

### 1. 概念发现是跨技能的认知基础

关键概念不仅服务于信息源发现（source-prospector），还服务于：
- **价值发现**（core-thinking L3）— 价值信号的本质是关键概念的变化
- **群讨论**（group-thinking）— 共识/分歧围绕关键概念形成
- **知识库建设**（llm-wiki）— 概念页面是 wiki 的骨架
- **日报生成** — 日报的主题结构由关键概念决定

如果概念发现被锁在 source-prospector 内部，其他技能就无法直接使用。

### 2. 不同领域的概念发现范式不同

| 领域 | 关键概念定义 | 提取方法 | 验证标准 | 扩展策略 |
|------|-------------|---------|---------|---------|
| **AI 研究** | 技术术语 + 方法名 | 论文关键词提取 + 引用网络分析 | arXiv 引用数 + 社区讨论度 | 引用链 + 作者追踪 |
| **专利情报** | 技术特征 + 权利要求 | IPC 分类 + 权利要求解析 | 专利族规模 + 诉讼引用 | 技术演进路径 + 竞争对手 |
| **金融分析** | 市场信号 + 监管概念 | 财报关键词 + 政策文本解析 | 市场反应 + 机构引用 | 宏观-微观传导链 |
| **医疗研究** | 疾病机制 + 靶点 | MeSH 术语 + 临床试验关键词 | 临床证据等级 + 引用数 | 机制-靶点-药物链 |
| **开源生态** | 技术栈 + 架构模式 | README + 依赖图分析 | GitHub star 趋势 + 生态采用率 | 依赖链 + 组织追踪 |

这些范式需要**独立积累经验**，不能混在一起。

### 3. 概念发现需要持续进化的反馈闭环

概念发现的质量取决于反馈数据的积累：
- 用户确认/拒绝的概念 → 调整提取算法的权重
- 概念验证通过/失败 → 调整验证阈值
- 扩展搜索命中率 → 调整扩展策略
- 领域专家的反馈 → 调整领域特定范式

这些反馈数据是**长期资产**，需要独立存储和持续进化。

## 核心架构：领域自适应的概念发现

### 三层架构

```
┌─────────────────────────────────────────────────┐
│              通用概念发现层 (Generic)              │
│  概念类型定义 · 提取框架 · 验证流程 · 扩展策略     │
│  反馈闭环 · 效果追踪 · 概念注册表                  │
├─────────────────────────────────────────────────┤
│           领域适配层 (Domain Adapter)             │
│  领域特定参数 · 领域特定提取规则 · 领域特定验证标准  │
│  领域特定扩展策略 · 领域反馈数据                    │
├─────────────────────────────────────────────────┤
│           领域实例层 (Domain Instance)             │
│  AI研究 · 专利情报 · 金融分析 · 医疗研究 · ...     │
│  每个领域有独立的经验库和范式库                      │
└─────────────────────────────────────────────────┘
```

### 通用概念发现层

所有领域共享的概念发现框架。

#### 概念类型体系

| 概念类型 | 定义 | 通用提取信号 | 通用验证标准 |
|----------|------|-------------|-------------|
| **枢纽概念** | 连接多个实体的概念 | 入站引用数 > 阈值 | 被多个独立源引用 |
| **前沿概念** | 近期出现且增速快的概念 | 时间衰减 + 引用增速 | 近期搜索结果增长 |
| **桥接概念** | 连接不同领域的概念 | 跨领域引用 > 阈值 | 在多个领域的搜索结果中出现 |
| **缺口概念** | 覆盖不足的概念 | 页面长度 < 阈值 AND 引用数 > 阈值 | 搜索结果多但本地覆盖少 |
| **衰退概念** | 活跃度下降的概念 | 近期引用增速 < 0 | 搜索结果减少趋势 |
| **标签溢出** | 被归入概念但实质不匹配的实体群 | 标签内实体满足核心定义比例 < 50% | 溢出率 > 阈值时触发概念泡沫警告 |

#### 通用提取框架

```
输入: 知识图谱 (llm-wiki) + 信息源内容 (source-evolution) + 讨论记录 (group-thinking)
  │
  ├── 结构提取: 从 wiki 的 concepts/ 和 entities/ 中提取概念节点和关系
  ├── 内容提取: 从 Tier 1 源的最新内容中提取技术术语和方法名
  ├── 讨论提取: 从群聊记录中提取高频但未覆盖的术语
  │
  └── 合并去重 → 候选概念列表
```

#### 通用验证流程

```
对每个候选概念:
1. 构造搜索查询 (概念名 + 领域词)
2. 执行搜索 (web_search)
3. 评估核心相关性:
   - 可信度: 结果中来自高质量源的比例
   - 领域相关性: 结果与关注领域的匹配度
   - 时效性: 近期结果占比
   - 发现潜力: 结果中是否出现新实体/概念
4. 判定: 高相关 / 中相关 / 低相关 / 待观察
5. 更新概念注册表
```

#### 通用扩展策略

| 方向 | 方法 | 目的 |
|------|------|------|
| 深度 | 概念 + 技术细节词 | 发现深度技术源 |
| 广度 | 概念 + 关联概念 | 发现关联领域源 |
| 时间 | 概念 + 时间限定词 | 发现最新进展源 |
| 应用 | 概念 + 应用领域词 | 发现应用场景源 |
| 批判 | 概念 + 批判性词 | 发现对立视角源 |

#### 反馈闭环

```
概念提取 → 验证 → 扩展 → 使用(source-prospector) → 结果反馈
   │                                              │
   │         ┌────────────────────────────────────┘
   │         │
   │         ▼
   │    反馈数据积累:
   │    - 用户确认/拒绝的概念 → 调整提取权重
   │    - 验证通过/失败率 → 调整验证阈值
   │    - 扩展命中率 → 调整扩展策略参数
   │    - 概念使用效果 → 调整概念类型权重
   │
   └──→ 下次提取使用调整后的参数
```

### 通用调查能力层（Generic Investigation Abilities）

所有领域的概念发现和验证都必须使用的**通用分析能力**。这些能力不是领域特定的，而是任何严谨调查的基础——无论调查对象是 AI 论文、金融事件还是医疗研究。

> **关键区分**：通用调查能力 vs 领域特定方法。通用能力回答"如何严谨地分析任何问题"，领域方法回答"这个领域有什么特殊的分析维度"。混淆两者会导致：把行业常识当成通用方法论（不可迁移），或把通用逻辑当成行业特色（无法泛化）。

#### 能力 1：Beta/Alpha 分离（系统性 vs 个体性归因）

**定义**：区分系统性驱动因素（beta）和个体性驱动因素（alpha），避免将近因偏差（near-cause bias）误认为因果解释。

**问题模式**：当多个实体同时出现相似变化时，首先识别这是行业级/系统级现象（beta），再分析个体差异（alpha）。

**操作方法**：

```
1. 观察到目标实体变化（如：某公司股价涨停）
2. 检查同行业/同类实体是否同步变化
   - 同步变化 → beta 主导，需找行业级驱动
   - 独立变化 → alpha 主导，需找公司级驱动
3. 如果是 beta：
   a. 识别行业级驱动因素（政策、技术突破、宏观事件）
   b. 在 beta 框架下分析 alpha（为什么涨得多/少？是否滞后/领先？）
4. 如果是 alpha：
   a. 识别公司级驱动因素（公告、业绩、事件）
   b. 验证是否有隐藏的 beta（行业趋势是否也在起作用？）
```

**验证标准**：
- 如果归因为 alpha，必须解释为什么同类实体没有同步变化
- 如果归因为 beta，必须量化行业级驱动的覆盖面（多少同类实体同步变化）
- 混合归因时，必须区分 beta 和 alpha 的相对贡献

**反例（近因偏差）**：
- ❌ "百傲化学涨停因为公司发布回购公告" — 忽略了当日芯片股集体涨停潮（beta）
- ✅ "百傲化学涨停主因是芯片股集体暴涨（beta），回购公告是锦上添花（alpha），证据：涨停滞后核心芯片股，化学制品板块当日-0.48%"

#### 能力 2：反事实检验（Counterfactual Testing）

**定义**：对每个因果假说，构造反事实场景——"如果 X 没有发生，Y 还会发生吗？"——来检验因果关系的强度。

**问题模式**：当声称"A 导致了 B"时，必须验证"没有 A，B 是否还会发生"。

**操作方法**：

```
1. 陈述因果假说：A → B
2. 构造反事实：如果 A 没有发生，B 会怎样？
3. 寻找证据：
   - 时间证据：A 发生前，B 是否已有趋势？
   - 空间证据：没有 A 的同类实体，B 是否也发生了？
   - 量级证据：B 的规模是否远超 A 的解释力？
4. 判定：
   - 反事实下 B 仍发生 → A 不是主因，是放大器/催化剂
   - 反事实下 B 不发生 → A 是必要条件
   - 反事实下 B 减弱 → A 是部分原因
```

**验证标准**：
- 每个主因归因必须通过反事实检验
- "放大器"和"起爆点"是不同的角色——放大器强化已有趋势，起爆点创造新趋势
- 反事实检验不要求完美控制实验，但要求至少一个维度的对比证据

**反例**：
- ❌ "马斯克达沃斯发言引爆太空光伏行情" — 反事实：1月21日（达沃斯前）太空光伏已有异动
- ✅ "马斯克达沃斯发言是太空光伏行情的放大器而非起爆点——1月21日已有异动，但1月23日30+涨停潮的规模远超前日，达沃斯发言放大了已有趋势"

#### 能力 3：时间对比（Temporal Comparison）

**定义**：将事件放在时间线上，通过前后对比和阶段划分，识别趋势的起点、加速点和衰减点。

**问题模式**：孤立看一个时间点的事件容易误判其性质；放在时间线上才能看清它是趋势的起点、中继还是终点。

**操作方法**：

```
1. 建立时间线：按时间顺序列出所有相关事件
2. 识别阶段：
   - 萌芽期：概念/趋势首次出现，影响范围小
   - 加速期：多个信号汇聚，影响范围扩大
   - 高潮期：公众/媒体大规模关注
   - 分化期：共识开始分裂，分化出赢家和输家
   - 衰减期：关注度下降，核心信号减弱
3. 定位当前事件在时间线上的位置
4. 根据阶段调整分析框架：
   - 萌芽期→关注信号确认
   - 加速期→关注扩散路径
   - 高潮期→关注分化信号
   - 分化期→关注实质兑现
   - 衰减期→关注替代趋势
```

**验证标准**：
- 任何"引爆点"声明必须有"引爆前"的对比数据
- 任何"趋势"声明必须有时间线上的连续信号支撑
- 阶段划分必须有可观察的转折点证据

**示例**：
- 太空光伏概念时间线：2025-12月萌芽（Moonshots播客）→ 2026-01-20扩散（X发帖）→ 01-22加速（达沃斯）→ 01-23高潮（30+涨停）→ 01-26分化 → 02月常态化 → 02-04再起（SpaceX并购+走访中国光伏）

#### 能力 4：多层归因（Multi-Level Attribution）

**定义**：任何非平凡事件都有多层因果驱动，必须逐层分析，避免跳层归因（用宏观原因解释微观现象，或用微观原因解释宏观现象）。

**问题模式**：单一层级的归因总是不完整的——宏观政策、产业趋势、技术突破、个体事件、情绪博弈各自贡献不同比例的驱动力。

**操作方法**：

```
1. 识别可能的因果层级：
   - 宏观/政策层：制度、法规、国际关系
   - 产业/技术层：行业趋势、技术路线、竞争格局
   - 事件/信号层：具体事件、关键人物发言、公告
   - 情绪/博弈层：市场情绪、资金博弈、羊群效应
2. 对每一层，评估其对目标现象的解释力：
   - 宏观层：是否创造了必要条件？
   - 产业层：是否提供了趋势方向？
   - 事件层：是否是直接触发器？
   - 情绪层：是否放大了反应规模？
3. 构建完整因果链：宏观 → 产业 → 事件 → 情绪
4. 标注每层的贡献比例（定性：主导/重要/辅助/边际）
```

**验证标准**：
- 不能只归因到某一层而忽略其他层
- 每层的归因必须有该层的独立证据支撑
- 层间传导必须有可观察的传导机制

**示例**：
- 太空光伏行情四层归因：
  - 宏观：ITU"先占先得"规则 → 卫星星座竞赛 → 供电需求刚性
  - 产业：SpaceX确定HJT路线 → HJT设备商直接受益
  - 事件：马斯克达沃斯发言 → 全球媒体放大 → 概念标签统一
  - 情绪：光伏行业深冬 → 长期压抑的反弹需求 → 涨停潮规模放大

#### 能力 5：标签溢出检测（Label-Overflow Detection）

**定义**：当实体被归入某个概念标签，但实体的实质内容与标签的核心定义不匹配时，识别这种"标签溢出"——标签的覆盖范围超出了其有效边界。

**问题模式**：概念标签在传播过程中会膨胀——越来越多的实体被归入标签，但其中许多实体与标签核心定义的关联是弱的或虚假的。标签溢出是概念泡沫的早期信号。

**操作方法**：

```
1. 明确概念标签的核心定义（什么条件必须满足才能归入此标签？）
2. 列出被归入该标签的所有实体
3. 对每个实体，检验其是否满足核心定义：
   - 满足 → 真成员（strong alpha）
   - 部分满足 → 边缘成员（weak alpha）
   - 不满足 → 标签溢出（no alpha，纯标签效应）
4. 计算标签溢出率 = 不满足核心定义的实体数 / 总实体数
5. 溢出率 > 50% → 概念泡沫警告
6. 识别溢出机制：
   - 产业链延伸（"太空光伏"→ 光伏胶膜→ 光伏玻璃→ 纯光伏股）
   - 概念泛化（"AI"→ 任何有软件的公司）
   - 资金溢出（龙头涨停→ 资金溢出到同板块低质股）
```

**验证标准**：
- 每个概念标签必须有清晰的核心定义和入标签条件
- 标签溢出检测是概念验证的必要步骤
- 溢出率高的概念需要降级或拆分

**示例**：
- "太空光伏"标签溢出：1月23日30+涨停股中，大部分公司2025年业绩亏损，太空光伏度电成本2-3美元/kWh vs 地面0.03-0.05美元/kWh（百倍差距），真正有太空光伏技术储备的公司不到5家——标签溢出率 > 80%

#### 能力 6：估值前置检测（Valuation Pre-Pricing Detection）

**定义**：在推演远期预期之前，先检查市场是否已经定价了该预期。避免"发现"一个已被市场充分定价的机会。

**问题模式**：当分析产业链传导后推演出"远期重估空间X倍"时，必须先检查股价是否已经反映了这个预期——如果市场已经提前定价，则"机会"是验证型而非发现型。

**操作方法**：

```
1. 计算当前市值隐含的业务分部价值
2. 对比隐含价值与基本面支撑价值：
   - 隐含价值 ≈ 基本面价值 → 市场尚未定价，存在发现型机会
   - 隐含价值 > 基本面价值 2x+ → 市场已过度定价，机会是验证型（需兑现才能维持）
   - 隐含价值 < 基本面价值 → 市场低估，存在真正的重估机会
3. 检查定价驱动因素：
   - 有分析师覆盖 → 机构定价，相对有效
   - 零分析师覆盖 → 散户/概念驱动，可能过度定价
4. 检查股价历史：
   - 股价已3x+上涨 → 远期预期大概率已被定价
   - 股价未显著上涨 → 远期预期可能尚未被市场发现
```

**验证标准**：
- 任何"远期重估空间"声明必须先通过估值前置检测
- 如果市场已定价，必须明确标注"验证型机会"而非"发现型机会"
- 验证型机会需要列出验证节点清单和风险清单

**反例**：
- ❌ "百傲化学远期估值重估空间6-10倍" — 忽略了股价已从15元涨到38元（3.4x），隐含半导体价值100-130亿 vs 收购成本7亿
- ✅ "百傲化学的远期重估已被市场部分定价（隐含半导体价值100-130亿 vs 乐观估值50-60亿），当前是验证型机会——如果6个验证节点通过可维持估值，如果失败需回调40-50%"

#### 能力 7：机构行为解读（Smart Money Behavior Interpretation）

**定义**：专业投资者（机构投资者、产业资本、内部人）的进入/退出行为是比报告和声明更真实的价值信号。当机构用脚投票时，其行为比任何报告都更有信息量。

**问题模式**：当声称某资产是"稀缺资产"或"捡漏"时，必须检查专业投资者是否认同——如果他们在退出而非进入，"稀缺"可能是假象。

**操作方法**：

```
1. 检查机构投资者行为：
   - 机构在增资/增持 → 正面信号（用钱投票）
   - 机构在退出/清仓 → 强负面信号（用脚投票）
   - 机构无变化 → 中性
2. 检查产业资本行为：
   - 产业资本入股 → 技术验证+客户关系信号（最强正面信号）
   - 产业资本退出 → 技术质疑信号
3. 检查内部人行为：
   - 创始团队/管理层增持 → 信心信号
   - 创始团队/管理层减持/质押 → 风险信号
4. 对比机构行为与公开叙事：
   - 机构行为与公开叙事一致 → 叙事可信
   - 机构行为与公开叙事矛盾 → 叙事可疑，需追问原因
```

**验证标准**：
- 当声称"稀缺资产"或"低估值"时，必须检查机构投资者是否认同
- 机构集体退出是**强负面信号**，必须追问"他们看到了什么我们没看到的？"
- 产业资本入股是**强正面信号**，因为产业资本有客户关系验证能力

**反例**：
- ❌ "芯慧联是稀缺资产，PE仅4.79倍，百傲化学捡漏" — 忽略了4家专业机构投资者全部选择"低价"清仓退出
- ✅ "芯慧联估值虽低，但4家专业机构投资者（上海半导体装备材料基金等）全部清仓退出——他们用脚投票说明不认为是优质资产。'捡漏'叙事需要解释这个矛盾：如果真是稀缺资产，为什么专业投资者要跑？"

#### 能力 8：护城河耐久性分级（Moat Durability Classification）

**定义**：将竞争优势按耐久性分为三级——政策依赖型（3-5年）、结构性（10年+）、自我强化型（永久）——避免将临时优势误认为持久护城河。

**问题模式**：当声称某公司有"护城河"或"稀缺性"时，必须评估护城河的耐久性——政策依赖型护城河在外部条件变化时会消失，结构性护城河则不会。

**操作方法**：

```
1. 识别竞争优势的来源：
   - 政策/法规驱动 → 政策依赖型
   - 技术/规模/网络效应驱动 → 结构性
   - 用户增长→数据增长→体验改善→用户增长 → 自我强化型
2. 评估耐久性：
   - 政策依赖型：出口管制/补贴/准入限制 → 持续3-5年（政策可能转向）
   - 结构性：技术壁垒/规模效应/品牌 → 持续10年+（需要大量投入才能打破）
   - 自我强化型：网络效应/数据飞轮 → 持续永久（越强越难打破）
3. 评估护城河方向：
   - 自我强化 → 护城河随时间加宽（最安全）
   - 稳定 → 护城河宽度不变
   - 自我削弱 → 护城河随时间收窄（如：再制造业务随设备存量老化而萎缩）
4. 标注耐久性等级和方向：
   - 等级：政策依赖 / 结构性 / 自我强化
   - 方向：加宽 / 稳定 / 收窄
```

**验证标准**：
- 每个声称的"护城河"必须标注耐久性等级和方向
- 政策依赖型护城河必须标注"依赖什么政策"+"政策转向的条件"
- 自我削弱型护城河必须标注"收窄时间线"+"收窄后的替代方案"

**反例**：
- ❌ "芯慧联光刻机再制造是稀缺护城河" — 没有评估耐久性
- ✅ "芯慧联光刻机再制造是政策依赖型护城河（依赖出口管制维持），方向为自我削弱（随TEL设备存量老化替换为国产设备，再制造机会缩小），耐久性3-5年。护城河收窄后的替代方案：涂胶显影自研（结构性护城河，方向加宽）"

#### 通用调查能力的集成方式

这五种能力不是独立的检查清单，而是**相互强化的分析框架**：

```
Beta/Alpha分离 → 识别系统性 vs 个体性
        ↓
反事实检验 → 验证因果假说的强度
        ↓
时间对比 → 定位事件在趋势中的位置
        ↓
多层归因 → 构建完整因果链
        ↓
标签溢出检测 → 识别概念泡沫和虚假关联
        ↓
估值前置检测 → 检查市场是否已定价远期预期
        ↓
机构行为解读 → 从专业投资者的行为推断真实价值
        ↓
护城河耐久性分级 → 评估竞争优势的时间维度
```

**在概念发现中的应用**：
- 提取候选概念时：用 Beta/Alpha 分离判断概念是行业级还是实体级
- 验证概念时：用反事实检验确认概念的核心相关性
- 扩展概念时：用时间对比选择扩展方向（萌芽期→深度，成熟期→批判）
- 评估概念时：用多层归因理解概念的价值来源
- 注册概念时：用标签溢出检测确保概念边界清晰
- 推演远期预期时：用估值前置检测避免"发现已被定价的机会"
- 判断概念价值时：用机构行为解读获取比报告更真实的信号
- 评估概念持续性时：用护城河耐久性分级区分临时优势与结构性优势

### 领域适配层

每个领域有自己的适配器，覆盖通用层的参数和规则。

#### 适配器结构

```json
{
  "domain": "ai-research",
  "display_name": "AI 研究",
  "adapter_version": "1.0.0",
  "concept_types": {
    "hub": {
      "threshold": 3,
      "weight": 0.3,
      "extraction_rules": ["论文关键词", "方法名", "框架名"],
      "validation_sources": ["arxiv", "semantic-scholar", "papers-with-code"]
    },
    "frontier": {
      "time_window_months": 12,
      "growth_threshold": 2.0,
      "weight": 0.3,
      "extraction_rules": ["新 arXiv 分类", "新会议主题", "新 benchmark"],
      "validation_sources": ["arxiv", "twitter-ai", "huggingface"]
    },
    "bridge": {
      "cross_domain_threshold": 2,
      "weight": 0.2,
      "extraction_rules": ["跨分类论文", "跨领域引用"],
      "validation_sources": ["semantic-scholar", "google-scholar"]
    },
    "gap": {
      "page_length_threshold": 50,
      "mention_threshold": 3,
      "weight": 0.2,
      "extraction_rules": ["讨论中高频但wiki无页面", "Tier1源中提及但未追踪"],
      "validation_sources": ["web-search", "arxiv"]
    }
  },
  "validation_criteria": {
    "credibility_min": 0.4,
    "domain_relevance_min": 0.5,
    "timeliness_min": 0.3,
    "discovery_potential_min": 0.2
  },
  "expansion_strategies": {
    "depth": {"weight": 0.3, "suffixes": ["implementation", "details", "architecture"]},
    "breadth": {"weight": 0.25, "suffixes": ["comparison", "vs", "alternative"]},
    "temporal": {"weight": 0.2, "suffixes": ["2025", "latest", "new", "recent"]},
    "application": {"weight": 0.15, "suffixes": ["application", "use case", "real world"]},
    "critique": {"weight": 0.1, "suffixes": ["limitation", "problem", "critique", "failure"]}
  },
  "search_templates": [
    "{concept} {domain_keyword} {year}",
    "{concept} survey OR review",
    "{concept} {connected_concept}"
  ],
  "feedback_weights": {
    "user_confirm": 1.0,
    "user_reject": -0.5,
    "validation_pass": 0.3,
    "validation_fail": -0.2,
    "expansion_hit": 0.2,
    "expansion_miss": -0.1
  }
}
```

#### 领域适配器注册

```json
{
  "domains": {
    "ai-research": {
      "adapter_path": "domains/ai-research/adapter.json",
      "experience_path": "domains/ai-research/experience.json",
      "status": "active",
      "concepts_tracked": 47,
      "feedback_count": 128
    },
    "patent-intelligence": {
      "adapter_path": "domains/patent-intelligence/adapter.json",
      "experience_path": "domains/patent-intelligence/experience.json",
      "status": "active",
      "concepts_tracked": 23,
      "feedback_count": 56
    },
    "finance-analysis": {
      "adapter_path": "domains/finance-analysis/adapter.json",
      "experience_path": "domains/finance-analysis/experience.json",
      "status": "active",
      "concepts_tracked": 31,
      "feedback_count": 48
    }
  }
}
```

### 领域实例层

每个领域实例包含：

```
domains/{domain-name}/
├── adapter.json       # 领域适配器参数
├── experience.json    # 领域经验库（反馈数据积累）
├── concepts.json      # 领域概念注册表
└── paradigms.json     # 领域发现范式库
```

#### 金融分析领域（finance-analysis）

金融分析领域的概念发现与通用模式有本质差异：**搜索路径是自上而下的**（宏观→行业→业绩→公司），而非通用的自下而上（公司→概念→扩展）。这是因为金融市场的驱动因素是层级传导的——宏观政策决定行业趋势，行业趋势决定公司业绩，公司业绩是最终结果而非起点。

##### 金融分析适配器（adapter.json）

```json
{
  "domain": "finance-analysis",
  "display_name": "金融分析",
  "adapter_version": "1.1.0",
  "concept_types": {
    "hub": {
      "threshold": 5,
      "weight": 0.25,
      "extraction_rules": ["行业关键词", "政策术语", "监管概念"],
      "validation_sources": ["csdc", "csrc", "sse", "szse"],
      "finance_specific": true
    },
    "frontier": {
      "time_window_months": 6,
      "growth_threshold": 3.0,
      "weight": 0.25,
      "extraction_rules": ["新政策概念", "新行业术语", "新监管框架"],
      "validation_sources": ["eastmoney", "caixin", "yicai", "stcn"],
      "finance_specific": true
    },
    "bridge": {
      "cross_domain_threshold": 2,
      "weight": 0.15,
      "extraction_rules": ["跨行业传导概念", "政策-行业桥接", "技术-金融桥接"],
      "validation_sources": ["web-search", "caixin"],
      "finance_specific": true
    },
    "gap": {
      "page_length_threshold": 30,
      "mention_threshold": 5,
      "weight": 0.15,
      "extraction_rules": ["讨论中高频但wiki无页面", "龙虎榜/资金流中频繁出现但未追踪"],
      "validation_sources": ["eastmoney", "web-search"],
      "finance_specific": true
    },
    "label-overflow": {
      "overflow_threshold": 0.5,
      "weight": 0.20,
      "extraction_rules": ["概念标签内实体不满足核心定义", "涨停潮中大部分公司无实质关联"],
      "validation_sources": ["eastmoney", "cninfo", "sse", "szse"],
      "finance_specific": true,
      "description": "金融领域标签溢出高发——概念炒作时大量公司被归入标签但无实质关联"
    }
  },
  "search_path": {
    "direction": "top_down",
    "order": ["macro", "industry", "earnings", "company"],
    "description": "金融分析必须自上而下搜索：宏观政策→行业趋势→业绩周期→公司个体"
  },
  "validation_criteria": {
    "credibility_min": 0.5,
    "domain_relevance_min": 0.6,
    "timeliness_min": 0.5,
    "discovery_potential_min": 0.3
  },
  "expansion_strategies": {
    "depth": {"weight": 0.2, "suffixes": ["产业链", "供应链", "技术路线"]},
    "breadth": {"weight": 0.25, "suffixes": ["关联行业", "替代品", "上下游"]},
    "temporal": {"weight": 0.2, "suffixes": ["最新", "2026", "近期"]},
    "application": {"weight": 0.15, "suffixes": ["应用场景", "商业化", "量产"]},
    "critique": {"weight": 0.2, "suffixes": ["风险", "泡沫", "质疑", "不确定性"]}
  }
}
```

##### 金融分析六大领域特定模块

以下六个分析模块是金融分析领域**特有的**，不适用于其他领域。它们与通用调查能力（Beta/Alpha分离、反事实检验、时间对比、多层归因、标签溢出检测）互补——通用能力提供分析框架，领域模块提供金融特有的分析维度。

###### 模块 1：板块轮动与资金流（Sector Rotation & Capital Flow）

**领域特定性**：A股市场存在显著的板块轮动效应——资金在不同板块间流动，形成"跷跷板"现象。这是A股特有的市场结构决定的（散户占比高、涨跌停制度、T+1）。

**核心概念**：
- **板块轮动**：资金从高估值板块流向低估值板块，或从冷门板块流向热门板块
- **资金溢出**：龙头涨停后，资金溢出到同板块低质股（标签溢出的资金面机制）
- **跷跷板效应**：一个板块上涨时，另一个板块下跌（存量博弈特征）

**分析操作**：
```
1. 识别当日领涨板块和领跌板块
2. 检查资金流向：北向资金、融资融券、龙虎榜
3. 判断轮动类型：
   - 顺周期轮动（经济周期驱动）→ 持续性强
   - 事件驱动轮动（消息刺激）→ 持续性弱
   - 资金博弈轮动（存量博弈）→ 切换快
4. 评估目标公司在轮动中的位置：龙头/跟涨/溢出
```

**与通用能力的关系**：板块轮动是 Beta/Alpha 分离在金融领域的具体化——识别板块级 beta 后，再分析个股在板块中的 alpha 位置。

###### 模块 2：业绩周期与预期差（Earnings Cycle & Expectation Gap）

**领域特定性**：股价反映的不是业绩本身，而是业绩与市场预期的差异（预期差）。同样的业绩增长，超预期则涨，不及预期则跌。

**核心概念**：
- **预期差**：实际业绩 vs 市场一致预期的差异
- **业绩周期**：行业/公司的盈利周期（扩张→顶峰→收缩→谷底）
- **前瞻指引**：公司对未来业绩的指引比当期业绩更重要

**分析操作**：
```
1. 获取市场一致预期（券商研报、Wind一致预期）
2. 对比实际业绩与预期：
   - 超预期 → 正面预期差 → 利好
   - 符合预期 → 无预期差 → 中性
   - 不及预期 → 负面预期差 → 利空
3. 识别业绩周期位置：
   - 扩张期：增速加速 → 估值扩张
   - 顶峰期：增速见顶 → 估值压缩
   - 收缩期：增速下滑 → 估值收缩
   - 谷底期：增速触底 → 估值修复
4. 评估前瞻指引的方向和可信度
```

**与通用能力的关系**：预期差分析是反事实检验在金融领域的具体化——"如果业绩符合预期，股价会怎样？"

###### 模块 3：监管风险（Regulatory Risk）

**领域特定性**：中国金融市场的监管风险是独特且不可忽视的——证监会立案、行业政策变化、退市新规等可以瞬间改变公司基本面。

**核心概念**：
- **立案调查**：证监会立案 = 不确定性暴增，期间不得增发/重组
- **政策风险**：行业政策变化（如教培双减、游戏版号）
- **退市风险**：财务造假、连续亏损、面值退市

**分析操作**：
```
1. 检查公司是否处于监管调查中（巨潮资讯网、证监会公告）
2. 评估调查性质：
   - 信息披露违规 → 通常罚款了事
   - 财务造假 → 可能退市，严重
   - 内幕交易 → 高管风险，公司经营影响取决于涉案人级别
3. 检查行业政策环境：
   - 鼓励类 → 政策顺风
   - 限制类 → 政策逆风
   - 待定类 → 政策不确定性
4. 评估退市风险：
   - *ST / ST 标识
   - 连续亏损年数
   - 审计意见类型
```

**与通用能力的关系**：监管风险是多层归因中"宏观/政策层"在金融领域的特化——监管变化可以独立于产业趋势和公司基本面，创造全新的驱动因素。

###### 模块 4：大股东行为（Major Shareholder Behavior）

**领域特定性**：A股大股东的行为（减持、增持、质押、表决权委托）是公司治理和股价的重要信号，且信息不对称严重。

**核心概念**：
- **减持信号**：大股东减持 = 内部人看淡（但需区分被动减持和主动减持）
- **质押风险**：高质押率 = 强平风险 = 股价下跌螺旋
- **表决权委托**：实际控制权与持股比例不一致 = 治理风险
- **增持/回购**：大股东增持 = 内部人看好（但需区分真看好和护盘）

**分析操作**：
```
1. 检查大股东持股变化（季报、权益变动报告）
2. 检查质押比例（中国结算、巨潮资讯网）
3. 检查表决权安排（是否有表决权委托/差异安排）
4. 综合评估：
   - 大股东减持 + 业绩下滑 → 强负面信号
   - 大股东增持 + 业绩上升 → 强正面信号
   - 高质押 + 股价下跌 → 强制平仓风险
   - 表决权委托 + 持股分散 → 控制权不稳定
```

**与通用能力的关系**：大股东行为是 alpha 分析的重要维度——在 beta 主导的行情中，大股东行为决定了个股的 alpha 方向。

###### 模块 5：估值框架（Valuation Framework）

**领域特定性**：不同行业适用不同估值方法——PE/PB/PS/DCF/PEG——选择错误的估值框架会导致严重误判。

**核心概念**：
- **估值方法匹配**：行业特性决定估值方法
  - 成熟盈利 → PE
  - 重资产 → PB
  - 高增长未盈利 → PS/PEG
  - 现金流稳定 → DCF
- **估值分位数**：当前估值在历史分位数中的位置
- **估值切换**：市场风格切换时，估值框架本身会变化

**分析操作**：
```
1. 确定行业适用的估值方法
2. 计算当前估值水平
3. 对比历史分位数：
   - > 90% → 高估风险
   - 50-90% → 中性偏高
   - 10-50% → 中性偏低
   - < 10% → 低估机会（但需排除价值陷阱）
4. 检查估值框架是否需要切换：
   - 行业从成长期进入成熟期 → PE → PB
   - 公司从亏损进入盈利 → PS → PE
   - 市场风格从成长切换到价值 → PEG → PB
```

**与通用能力的关系**：估值框架是标签溢出检测的量化工具——当概念标签推高估值但业绩不支撑时，估值分位数会发出泡沫信号。

###### 模块 6：A股市场微观结构（A-Share Market Microstructure）

**领域特定性**：A股的交易制度（涨跌停、T+1、融资融券限制）创造了独特的市场微观结构，影响价格发现和流动性。

**核心概念**：
- **涨跌停制度**：10%/20%涨跌停 → 一字涨停/跌停 = 信息无法充分定价
- **T+1 制度**：当日买入次日才能卖出 → 日内风险无法对冲
- **融资融券**：两融余额变化 = 杠杆资金方向
- **北向资金**：外资流向 = 机构偏好信号
- **龙虎榜**：营业部买卖 = 游资/机构行为信号

**分析操作**：
```
1. 检查涨跌停状态：
   - 一字涨停 → 买盘远大于卖盘，信息未充分定价
   - 反复开板 → 多空分歧大
   - 尾盘涨停 → 资金博弈结果
2. 检查龙虎榜数据：
   - 机构买入 → 基本面驱动
   - 游资买入 → 情绪/题材驱动
   - 机构+游资共振 → 最强信号
3. 检查北向资金：
   - 连续净买入 → 外资看好
   - 连续净卖出 → 外资看淡
4. 检查融资融券：
   - 融资余额上升 → 杠杆做多
   - 融券余额上升 → 杠杆做空
```

**与通用能力的关系**：市场微观结构是时间对比分析在金融领域的具体化——涨跌停状态、龙虎榜数据等都是时间线上的关键节点信号。

##### 金融分析搜索路径

金融分析的概念发现必须遵循**自上而下**的搜索路径，与通用模式的**自下而上**相反：

```
通用模式：公司 → 概念 → 扩展
金融模式：宏观 → 行业 → 业绩 → 公司

原因：金融市场的驱动因素是层级传导的
- 宏观政策决定行业趋势（如：MATCH法案→国产替代）
- 行业趋势决定公司业绩（如：国产替代→芯片股Q1超预期）
- 公司业绩是最终结果而非起点（如：寒武纪+159%营收）
- 从公司层面出发容易犯近因偏差（如：把涨停归因为回购公告）
```

**搜索路径操作**：

```
1. 宏观层：
   - 搜索关键词：政策名称 + 法案 + 监管动态 + 国际关系
   - 验证：政策是否改变了行业基本面？
   - 产出：宏观驱动因素列表

2. 行业层：
   - 搜索关键词：行业指数 + 板块涨跌 + 产业链动态 + 技术路线
   - 验证：行业趋势是否与宏观驱动一致？
   - 产出：行业趋势和传导路径

3. 业绩层：
   - 搜索关键词：季报 + 业绩预告 + 一致预期 + 业绩超预期
   - 验证：业绩是否验证了行业趋势？
   - 产出：预期差和业绩周期位置

4. 公司层：
   - 搜索关键词：公司公告 + 大股东行为 + 龙虎榜 + 估值
   - 验证：公司个体因素是顺势还是逆势？
   - 产出：公司级 alpha 和风险因素
```

#### 经验库（experience.json）

记录领域特定的反馈数据，用于持续进化：

```json
{
  "extraction_feedback": [
    {
      "concept": "GRPO",
      "type": "frontier",
      "extracted_at": "2026-04-15",
      "user_feedback": "confirmed",
      "validation_result": "high_relevance",
      "expansion_hit_rate": 0.7,
      "source_quality_avg": 0.82,
      "notes": "用户确认 GRPO 是当前 RL 训练的关键概念"
    },
    {
      "concept": "speculative-decoding",
      "type": "frontier",
      "extracted_at": "2026-04-20",
      "user_feedback": "confirmed",
      "validation_result": "high_relevance",
      "expansion_hit_rate": 0.5,
      "source_quality_avg": 0.65,
      "notes": "推理加速方向，但扩展命中率中等，可能需要调整扩展策略"
    }
  ],
  "parameter_adjustments": [
    {
      "date": "2026-04-25",
      "parameter": "frontier.growth_threshold",
      "old_value": 2.0,
      "new_value": 1.5,
      "reason": "多个有效前沿概念因阈值过高被漏掉，降低阈值提高召回率"
    }
  ],
  "paradigm_evolution": [
    {
      "date": "2026-05-01",
      "paradigm": "paper_keyword_extraction",
      "change": "增加 Semantic Scholar 的 fieldsOfStudy 字段作为概念分类依据",
      "reason": "纯关键词提取无法区分概念所属子领域，fieldsOfStudy 提供了额外维度"
    }
  ],
  "finance_analysis_feedback": [
    {
      "concept": "太空光伏",
      "type": "frontier",
      "extracted_at": "2026-01-23",
      "user_feedback": "confirmed",
      "validation_result": "high_relevance",
      "expansion_hit_rate": 0.6,
      "source_quality_avg": 0.75,
      "label_overflow_rate": 0.83,
      "notes": "30+涨停股中大部分无实质关联，标签溢出严重。真正受益：迈为股份(HJT设备)、东方日升(超薄HJT交付)"
    },
    {
      "concept": "芯片国产替代",
      "type": "hub",
      "extracted_at": "2026-04-30",
      "user_feedback": "confirmed",
      "validation_result": "high_relevance",
      "expansion_hit_rate": 0.8,
      "source_quality_avg": 0.85,
      "label_overflow_rate": 0.3,
      "notes": "MATCH法案+华虹断供+Q1业绩超预期三层驱动，标签实质覆盖率高"
    },
    {
      "concept": "百傲化学-芯慧联产业链传导",
      "type": "bridge",
      "extracted_at": "2026-05-03",
      "user_feedback": "corrected",
      "validation_result": "critical_correction",
      "expansion_hit_rate": 0.5,
      "source_quality_avg": 0.6,
      "label_overflow_rate": 0.0,
      "valuation_pre_priced": true,
      "institutional_divergence": true,
      "moat_durability": "policy-dependent",
      "notes": "初始分析误判为'低估值等待重估'，实际为'高估值等待兑现'。股价已3.4x(15→38元)，隐含半导体价值100-130亿vs乐观PE仅50-60亿。4家专业机构投资者全部清仓退出=强负面信号。光刻机再制造护城河为政策依赖型(3-5yr)，方向自我削弱。关键教训：估值前置检测+机构行为解读+护城河耐久性分级缺一不可"
    }
  ]
}
```

#### 范式库（paradigms.json）

记录领域特定的发现范式——经过验证的有效模式：

```json
{
  "paradigms": [
    {
      "id": "p-001",
      "name": "论文关键词→引用验证→社区确认",
      "domain": "ai-research",
      "description": "从 arXiv 论文中提取关键词，通过引用增速验证前沿性，通过社区讨论确认实用性",
      "steps": [
        "扫描 arXiv cs.AI/cs.CL 最新论文",
        "提取标题和摘要中的技术术语",
        "查询 Semantic Scholar 引用增速",
        "搜索 Reddit/HN 社区讨论",
        "综合判定概念类型"
      ],
      "effectiveness": {
        "precision": 0.72,
        "recall": 0.65,
        "user_satisfaction": 0.80
      },
      "created_at": "2026-04-15",
      "last_used": "2026-05-01",
      "use_count": 8
    },
    {
      "id": "p-002",
      "name": "GitHub trending→依赖图→生态扩散",
      "domain": "ai-research",
      "description": "从 GitHub trending 项目中提取技术栈概念，通过依赖图分析生态扩散",
      "steps": [
        "扫描 GitHub trending repositories",
        "提取项目标签和依赖中的技术概念",
        "分析依赖图中的概念传播路径",
        "搜索相关博客和教程",
        "判定概念成熟度"
      ],
      "effectiveness": {
        "precision": 0.60,
        "recall": 0.78,
        "user_satisfaction": 0.70
      },
      "created_at": "2026-04-20",
      "last_used": "2026-05-01",
      "use_count": 5
    },
    {
      "id": "p-finance-001",
      "name": "宏观→行业→业绩→公司 自上而下传导链",
      "domain": "finance-analysis",
      "description": "金融分析的概念发现必须自上而下：先识别宏观/政策驱动，再追踪行业传导，再验证业绩兑现，最后分析公司个体因素。避免从公司层面出发导致近因偏差。",
      "steps": [
        "搜索宏观政策/法规/国际关系变化（如：MATCH法案、华虹断供）",
        "识别受影响的行业和板块（如：国产替代→芯片板块）",
        "验证行业趋势是否在业绩层面兑现（如：Q1芯片股营收超预期）",
        "在行业beta框架下分析公司个体alpha（如：回购公告是锦上添花非主因）",
        "用Beta/Alpha分离+反事实检验+标签溢出检测验证结论"
      ],
      "effectiveness": {
        "precision": 0.78,
        "recall": 0.70,
        "user_satisfaction": 0.85
      },
      "created_at": "2026-05-03",
      "last_used": "2026-05-03",
      "use_count": 2,
      "lessons_learned": [
        "从公司层面出发容易犯近因偏差——百傲化学涨停被误归因为回购公告",
        "行业级涨停潮是beta信号，必须先识别beta再分析alpha",
        "标签溢出在金融领域高发——太空光伏30+涨停股中大部分无实质关联"
      ]
    },
    {
      "id": "p-finance-002",
      "name": "关键人物发言→概念标签→市场传导",
      "domain": "finance-analysis",
      "description": "当高影响力人物（如马斯克）在权威场合发言时，其发言会被市场统一为一个可交易的'概念标签'，引发概念股行情。分析重点是：发言是起爆点还是放大器？概念标签的实质覆盖率是多少？",
      "steps": [
        "识别发言的核心概念（如：太空光伏、人形机器人、AI奇点）",
        "追踪概念标签的市场传导路径（发言→媒体放大→概念统一→资金涌入）",
        "用反事实检验判断发言角色（起爆点 vs 放大器 vs 无关）",
        "用标签溢出检测评估概念实质覆盖率（真受益 vs 纯标签）",
        "识别概念生命周期阶段（萌芽→加速→高潮→分化→衰减）"
      ],
      "effectiveness": {
        "precision": 0.72,
        "recall": 0.68,
        "user_satisfaction": 0.80
      },
      "created_at": "2026-05-03",
      "last_used": "2026-05-03",
      "use_count": 1,
      "lessons_learned": [
        "马斯克达沃斯发言是放大器非起爆点——1月21日太空光伏已有异动",
        "概念标签在传播中会膨胀——从'太空光伏HJT设备'扩展到'所有光伏股'",
        "行业深冬中的概念炒作反弹力度更大——情绪蓄水池效应"
      ]
    },
    {
      "id": "p-finance-003",
      "name": "产业链传导→竞争力定位→远期预期→估值验证",
      "domain": "finance-analysis",
      "description": "当行业级事件（如芯片股业绩暴增）发生后，不仅要分析'为什么涨'，更要追问'涨了对下游标的意味着什么'——需要产业链传导推演、竞争力定位、远期预期量化、估值前置检测四步闭环。避免只看报告不做独立判断。",
      "steps": [
        "构建产业链传导链：上游事件→中游需求→下游标的受益（每步需数据锚点）",
        "竞争力定位：标的在产业链中的真实位置 vs 竞争对手（第二梯队 vs 第一梯队）",
        "远期预期量化：从产能/订单/市场规模推演远期收入天花板和估值重估空间",
        "估值前置检测：检查市场是否已提前定价远期预期（股价历史+隐含分部价值+分析师覆盖）",
        "机构行为解读：检查专业投资者是否认同（机构退出=强负面信号）",
        "护城河耐久性分级：标注竞争优势的耐久性等级（政策依赖/结构性/自我强化）和方向（加宽/稳定/收窄）",
        "产出验证清单：6个验证节点+6个风险节点，明确'验证型机会'而非'发现型机会'"
      ],
      "effectiveness": {
        "precision": 0.82,
        "recall": 0.65,
        "user_satisfaction": 0.90
      },
      "created_at": "2026-05-03",
      "last_used": "2026-05-03",
      "use_count": 1,
      "lessons_learned": [
        "只看报告不做独立判断=无用——百傲化学'稀缺资产'叙事被机构清仓退出证伪",
        "远期预期推演前必须先做估值前置检测——股价已3.4x涨了，隐含半导体价值100-130亿",
        "护城河耐久性决定机会类型——政策依赖型(3-5年)是验证型机会，结构性(10年+)才是发现型机会",
        "产业链传导链每步需数据锚点——'然后奇迹发生'是逻辑断链",
        "竞争力定位必须对标第一梯队——芯慧联vs芯源微的对比揭示了'第二梯队'的真实位置"
      ]
    }
  ]
}
```

## 概念注册表

全局概念注册表，记录所有已发现和验证的关键概念：

```json
{
  "version": 1,
  "last_updated": "2026-05-01",
  "concepts": {
    "GRPO": {
      "type": "frontier",
      "key_score": 0.85,
      "domain": "ai-research",
      "sub_domain": "reinforcement-learning",
      "first_seen": "2024-02",
      "discovered_at": "2026-04-15",
      "discovered_by": "paradigm:p-001",
      "validation_status": "confirmed",
      "validation_score": {
        "credibility": 0.5,
        "domain_relevance": 0.7,
        "timeliness": 0.8,
        "discovery_potential": 0.6
      },
      "connected_entities": ["deepseek", "openrlhf"],
      "connected_concepts": ["RLHF", "PPO", "reward-model", "reinforcement-learning"],
      "cross_domain_links": [],
      "search_queries": [
        "GRPO reinforcement learning",
        "Group Relative Policy Optimization",
        "GRPO vs PPO RLHF"
      ],
      "expansion_results": {
        "depth": {"hit_rate": 0.7, "avg_quality": 0.82},
        "breadth": {"hit_rate": 0.5, "avg_quality": 0.70},
        "temporal": {"hit_rate": 0.8, "avg_quality": 0.75},
        "application": {"hit_rate": 0.6, "avg_quality": 0.68},
        "critique": {"hit_rate": 0.3, "avg_quality": 0.60}
      },
      "feedback": {
        "user_confirmations": 3,
        "user_rejections": 0,
        "source_upgrades": 2,
        "wiki_page_created": true
      },
      "lifecycle": "rising"
    },
    "constitutional-AI": {
      "type": "bridge",
      "key_score": 0.78,
      "domain": "ai-research",
      "sub_domain": "alignment",
      "first_seen": "2022-12",
      "discovered_at": "2026-04-10",
      "discovered_by": "paradigm:p-001",
      "validation_status": "confirmed",
      "validation_score": {
        "credibility": 0.6,
        "domain_relevance": 0.8,
        "timeliness": 0.5,
        "discovery_potential": 0.7
      },
      "connected_entities": ["anthropic"],
      "connected_concepts": ["RLHF", "AI-safety", "red-teaming"],
      "cross_domain_links": ["legal-compliance", "governance"],
      "search_queries": [
        "constitutional AI alignment",
        "constitutional AI legal compliance",
        "Anthropic constitutional AI"
      ],
      "expansion_results": {
        "depth": {"hit_rate": 0.6, "avg_quality": 0.78},
        "breadth": {"hit_rate": 0.7, "avg_quality": 0.80},
        "temporal": {"hit_rate": 0.4, "avg_quality": 0.65},
        "application": {"hit_rate": 0.5, "avg_quality": 0.72},
        "critique": {"hit_rate": 0.4, "avg_quality": 0.70}
      },
      "feedback": {
        "user_confirmations": 2,
        "user_rejections": 0,
        "source_upgrades": 1,
        "wiki_page_created": true
      },
      "lifecycle": "mature"
    }
  }
}
```

### 概念生命周期

```
候选概念 → 验证中 → 已确认 → 活跃使用 → 衰退观察 → 归档
              │           │          │            │
              │          │          │            └─ 讨论度下降，标记衰退
              │           │          └─ 被 source-prospector 等技能使用
              │           └─ 验证通过，进入概念注册表
              └─ 验证失败 → 待观察 / 丢弃
```

| 阶段 | 条件 | 行为 |
|------|------|------|
| 候选 | 刚提取，未验证 | 等待验证队列 |
| 验证中 | 正在执行搜索验证 | 不对外提供 |
| 已确认 | 验证通过（高/中相关） | 对外提供，可被其他技能使用 |
| 活跃使用 | 被其他技能引用 > 0 | 持续追踪扩展效果 |
| 衰退观察 | 近期引用增速 < 0 | 降低扩展频率，观察是否需要替代 |
| 归档 | 持续衰退 > 90 天 | 停止主动扩展，保留历史数据 |

## 与其他技能的集成

### source-prospector（信息源发现）

```
concept-discovery 提供: 已确认概念列表 + 概念扩展搜索结果
source-prospector 消费: 用概念驱动六种发现模式（含关键信号跟踪）
```

- source-prospector 不再自己提取概念，而是从 concept-discovery 获取
- source-prospector 的发现结果反馈给 concept-discovery（新概念、新实体）
- source-prospector 的模式6（关键信号跟踪）是 concept-discovery 的**信号输入源**——检测到关键人物发言/重大事件后，触发概念提取

**信号驱动的概念发现流程（逻辑闭环）**：

```
source-prospector 模式6 检测到信号
  │
  │  Level 1 信号（关键人物+权威场合+多源确认）
  │  → 立即触发 concept-discovery 概念提取
  │  → 提取发言中的新概念
  │  → 验证概念的核心相关性
  │  → 扩展概念到相关领域
  │  → 产出：已确认概念列表 → 回传给 source-prospector 驱动信息源发现
  │
  │  Level 2 信号（关键人物+非权威场合 / 非关键人物+权威场合）
  │  → 加入概念提取队列
  │  → 下次定期提取时处理
  │
  │  Level 3 信号（单源信号）
  │  → 仅记录，不触发概念提取
  │  → 如果后续有新信号确认 → 升级为 Level 2
  │
  └──→ 闭环验证：概念提取结果 → 反馈给 source-prospector → source-prospector 用概念驱动信息源发现 → 信息源内容 → 反哺 concept-discovery（新概念信号）
```

**自证**：概念提取的触发不是随意的——只有经过三层信号检测和交叉验证的 Level 1/2 信号才触发。这避免了"噪音驱动概念漂移"的问题。

### source-evolution（信息源管理）

```
concept-discovery 提供: 概念维度的信息源评估依据
source-evolution 消费: 在七维评分中增加概念相关性维度
```

- concept-discovery 不管理信息源生命周期
- source-evolution 可以使用概念信息来辅助 relevance 评分

### llm-wiki（知识库）

```
concept-discovery 消费: wiki 的概念页面和实体页面作为提取输入
concept-discovery 提供: 新概念和缺口概念建议 → 创建/补充 wiki 页面
```

- wiki 是概念发现的种子数据源
- 概念发现反哺 wiki 的内容建设

### core-thinking（价值发现）

```
concept-discovery 提供: 关键概念变化信号
core-thinking 消费: 概念变化 → 价值信号 → 价值发现
```

- 前沿概念的出现 = 价值信号
- 桥接概念的形成 = 跨域价值机会
- 衰退概念的替代 = 价值链调整

### group-thinking（群讨论）

```
concept-discovery 消费: 群讨论中的高频术语和分歧概念
concept-discovery 提供: 概念验证结果 → 辅助共识/分歧判断
```

## 操作命令

```
/concept list                              # 列出所有已确认概念
/concept list --domain <domain>            # 列出指定领域的概念
/concept extract [--domain <domain>]       # 从知识图谱提取候选概念
/concept validate [concept]                # 验证指定概念（不指定则验证所有候选）
/concept expand [concept]                  # 对已确认概念执行扩展搜索
/concept feedback <concept> <confirm|reject> # 用户反馈：确认或拒绝概念
/concept domains                           # 列出所有领域适配器
/concept domain add <domain>               # 添加新领域适配器
/concept paradigm list [--domain <domain>] # 列出领域发现范式
/concept stats                             # 查看概念发现统计
```

## 定期任务（cron）

```bash
# 每周概念提取
hermes cron add "concept extract" --schedule "0 8 * * 1" --prompt "/concept extract"

# 每周概念验证
hermes cron add "concept validate" --schedule "0 8 * * 2" --prompt "/concept validate"

# 每两周概念扩展
hermes cron add "concept expand" --schedule "0 9 1,15 * *" --prompt "/concept expand --auto"

# 每月范式评估
hermes cron add "concept paradigm review" --schedule "0 8 1 * *" --prompt "/concept paradigm review"
```

## 效果追踪

| 指标 | 含义 | 目标 |
|------|------|------|
| **概念提取率** | 每次提取发现的新概念数 | ≥3/次 |
| **验证通过率** | 验证通过的概念占比 | ≥60% |
| **扩展命中率** | 扩展搜索产出的高评分源占比 | ≥40% |
| **用户确认率** | 用户确认的概念占比 | ≥70% |
| **范式有效率** | 范式的 precision ≥ 0.5 的占比 | ≥60% |
| **领域分化度** | 活跃领域适配器数量 | 持续增长 |
| **反馈积累率** | 每月新增反馈数据量 | ≥20条/月 |

## 数据存储

```
~/.hermes/skills/reasoning/concept-discovery/
├── concepts.json              # 全局概念注册表
├── domain_registry.json      # 领域适配器注册表
├── domains/                   # 领域实例目录
│   ├── ai-research/
│   │   ├── adapter.json       # AI 研究领域适配器
│   │   ├── experience.json    # AI 研究经验库
│   │   ├── concepts.json      # AI 研究概念子集
│   │   └── paradigms.json     # AI 研究发现范式
│   ├── patent-intelligence/
│   │   ├── adapter.json
│   │   ├── experience.json
│   │   ├── concepts.json
│   │   └── paradigms.json
│   └── finance-analysis/
│       ├── adapter.json
│       ├── experience.json
│       ├── concepts.json
│       └── paradigms.json
├── discovery_log.json         # 发现日志（append-only，超过 500 条轮转）
└── effectiveness.json         # 效果追踪数据
```

## 领域分化指南

### 添加新领域

1. **创建领域目录**：`domains/{domain-name}/`
2. **编写适配器**：基于通用层参数，定义领域特定的提取规则、验证标准、扩展策略
3. **注册领域**：在 `domain_registry.json` 中添加条目，状态设为 `experimental`
4. **种子概念**：手动添加 5-10 个领域核心概念作为种子
5. **试运行**：运行 2-4 周收集反馈数据
6. **评估**：验证通过率 ≥ 40% 且用户确认率 ≥ 50% → 升级为 `active`
7. **范式沉淀**：从试运行中提取有效模式，写入 `paradigms.json`

### 领域间概念迁移

当一个领域的概念在另一个领域也出现时：

```
1. 检测：概念的 cross_domain_links 非空
2. 评估：在目标领域中验证该概念的核心相关性
3. 迁移：如果验证通过，在目标领域注册为"桥接概念"
4. 联动：两个领域的适配器共享该概念的反馈数据
```

### 领域范式进化

范式不是静态的——随着反馈数据积累，范式需要进化：

```
1. 每月评估范式的 effectiveness (precision, recall, user_satisfaction)
2. precision < 0.4 → 标记为"需改进"，分析失败案例
3. recall < 0.5 → 考虑增加新步骤或降低阈值
4. user_satisfaction < 0.5 → 重新设计范式的输出格式
5. 连续 3 个月 effectiveness 下降 → 标记为"过时"，设计替代范式
6. 新范式的 effectiveness 优于旧范式 → 替换旧范式
```

## 注意事项

- **概念发现 ≠ 关键词提取**：关键概念是知识图谱中的结构化节点，不是简单的文本关键词
- **验证是必须的**：未经验证的概念不应对外提供，避免概念漂移
- **领域分化是渐进的**：新领域从 experimental 开始，积累足够反馈后才升级为 active
- **反馈数据是核心资产**：经验库和范式库是概念发现持续进化的基础，需要持久化存储
- **不要替代 source-prospector**：concept-discovery 只发现概念，不发现信息源
- **不要替代 llm-wiki**：concept-discovery 只提取和验证概念，不构建知识页面
- **尊重领域差异**：不同领域的概念类型权重、验证标准、扩展策略可能完全不同
- **范式需要验证**：新范式必须经过至少 4 周试运行才能标记为"已验证"

## 设计参考

本技能的架构参考了以下学术和工业实践：

### 领域自适应概念发现

- **DySECT**（Dynamic Scientific Concept Tracking）：闭环反馈的概念追踪系统，从科学文献中提取概念并通过用户反馈持续进化。本技能的反馈闭环设计参考了 DySECT 的"提取→验证→反馈→调整"循环。
- **CDC**（Cross-Domain Concept Discovery）：领域限定的概念关系模型 `Concept → Relation@Domain → Concept`。同一对概念在不同领域中的关系不同（如"transformer → enables@NLP → 长文本理解" vs "transformer → enables@CV → 全局特征提取"）。本技能的领域适配层参考了 CDC 的领域限定三元组。
- **ODKE+**（Ontology-Driven Knowledge Extraction）：多阶段概念验证流水线（候选→初筛→领域专家验证→确认）。本技能的概念生命周期参考了 ODKE+ 的渐进式验证。

### 概念质量评估

- **CQAS**（Concept Quality Assessment System）：概念质量的四维评估框架（完整性、一致性、时效性、区分度）。本技能的概念验证标准参考了 CQAS 的多维度评估思路。
- **Active Learning for Concept Extraction**：基于信息增益的概念验证优先级排序——优先验证那些"如果确认了，能带来最多新发现"的概念。本技能的验证队列排序参考了这一思路。

### 领域分化

- **BioPortal**（生物医学本体库）：同一概念在不同生物医学子领域中的定义差异管理。展示了领域分化的必要性——"expression"在基因组学和蛋白质组学中的含义完全不同。
- **MeSH**（Medical Subject Headings）：层级化的领域概念分类，每个概念有领域限定的定义和关系。参考了 MeSH 的"概念-限定词"组合模式。