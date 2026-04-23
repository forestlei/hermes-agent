# 群ID + 用户ID 维度的技能分别进化体系 — 设计文档

## 1. 问题定义

### 现状

Hermes Agent 的技能和信息源是**全局共享**的：

| 资源 | 存储位置 | 隔离粒度 |
|------|---------|---------|
| 技能 (SKILL.md) | `~/.hermes/skills/` | 按 profile 隔离，profile 内全局共享 |
| 信息源数据 | `~/.hermes/skills/research/source-evolution/data/` | 全局共享 |
| 记忆 (MEMORY.md) | `~/.hermes/MEMORY.md` | 全局共享 |
| 用户画像 (USER.md) | `~/.hermes/USER.md` | 全局共享 |
| 会话 | SQLite `sessions/` | 按 session_key 隔离（已支持 chat_id:user_id） |

### 痛点

1. **信息源冲突** — A 群（AI 日报）需要 AI 信息源，B 群（财经日报）需要财经信息源，全局共享导致互相干扰
2. **评分失真** — AI 群用户觉得财经源低质（relevance 低），财经群用户觉得 AI 源低质，7 维评分被跨群噪音稀释
3. **技能冗余** — 每个群都需要同类的日报技能，但内容模板、信息源、分析框架完全不同
4. **用户偏好丢失** — 同一群内不同用户关注点不同（宏观经济 vs 个股），全局 USER.md 无法区分
5. **进化方向失控** — source-evolution 的自动发现机制会从一个群的讨论内容中发现对另一群无用的源

### 目标

```
每个群有独立的信息源宇宙，每个用户在群内有独立的偏好画像
技能按群维度进化，信息源按群+用户双维度评分
```

## 2. 核心设计

### 2.1 三维数据模型

```
                    ┌─────────────────────────────────────┐
                    │         Profile (HERMES_HOME)        │
                    │  ┌─────────────────────────────────┐ │
                    │  │     Global Skills & Sources      │ │
                    │  │  (共享基线，所有群继承)          │ │
                    │  └─────────────────────────────────┘ │
                    │                                      │
                    │  ┌──────────┐  ┌──────────┐         │
                    │  │ Group A  │  │ Group B  │  ...    │
                    │  │ AI日报群 │  │ 财经日报 │         │
                    │  │ ┌──────┐ │  │ ┌──────┐ │         │
                    │  │ │User X│ │  │ │User Y│ │         │
                    │  │ │AI偏好│ │  │ │宏观偏好│ │        │
                    │  │ └──────┘ │  │ └──────┘ │         │
                    │  │ ┌──────┐ │  │ ┌──────┐ │         │
                    │  │ │User Z│ │  │ │User W│ │         │
                    │  │ │通用偏好│ │ │ │个股偏好│ │       │
                    │  │ └──────┘ │  │ └──────┘ │         │
                    │  └──────────┘  └──────────┘         │
                    └─────────────────────────────────────┘
```

### 2.2 数据隔离层级

| 层级 | Key | 存储位置 | 内容 |
|------|-----|---------|------|
| **L0 全局** | profile | `~/.hermes/skills/` | 全局技能、共享基线信息源 |
| **L1 群维度** | `{chat_id}` | `~/.hermes/groups/{chat_id}/` | 群专属信息源、群日报模板、群角色设定 |
| **L2 群内用户** | `{chat_id}:{user_id}` | `~/.hermes/groups/{chat_id}/users/{user_id}/` | 用户偏好、个性化信息源权重、问答历史摘要 |

### 2.3 继承机制

```
查询顺序: L2(群内用户) → L1(群) → L0(全局)

信息源评分 = f(全局基线分, 群维度relevance, 用户偏好权重)
技能加载 = 全局技能 ∪ 群专属技能
日报生成 = 群模板 + 群信息源 + 汇总用户偏好
```

## 3. 存储结构

### 3.1 目录设计

```
~/.hermes/
├── skills/                                    # L0: 全局技能（现有结构不变）
│   ├── research/
│   │   ├── source-evolution/                  # 全局信息源进化引擎
│   │   └── deep-research/
│   └── ...
│
├── groups/                                    # L1+L2: 群维度数据
│   ├── oc_6ed1cc645057da3bbe93c6120219a61e/  # AI 日报群
│   │   ├── config.yaml                        # 群配置（角色、模板、cron）
│   │   ├── sources.json                       # 群专属信息源（继承+覆盖全局）
│   │   ├── sources_scores.json                # 群维度评分（relevance 群内重算）
│   │   ├── daily_template.md                  # 群日报模板
│   │   ├── SOUL.md                            # 群角色设定（可选，覆盖全局 SOUL）
│   │   ├── MEMORY.md                          # 群记忆（群级别的事实和规则）
│   │   └── users/                             # L2: 群内用户数据
│   │       ├── ou_d366ba075912a3865430a7fe7020454b/
│   │       │   ├── preferences.json           # 用户偏好画像
│   │       │   ├── source_weights.json        # 信息源个性化权重
│   │       │   └── qa_summary.jsonl           # 问答历史摘要
│   │       └── ou_aaa111bbb222ccc333ddd444eee555f/
│   │           ├── preferences.json
│   │           ├── source_weights.json
│   │           └── qa_summary.jsonl
│   │
│   └── oc_796d9f6d333a76820bc7dad59706e7cc/  # 财经日报群
│       ├── config.yaml
│       ├── sources.json
│       ├── sources_scores.json
│       ├── daily_template.md
│       ├── SOUL.md
│       ├── MEMORY.md
│       └── users/
│           └── ...
```

### 3.2 数据模型

#### 群配置 `groups/{chat_id}/config.yaml`

```yaml
# 群基本信息
name: "AI日报群"
description: "AI行业动态、论文速递、工具推荐"

# 信息源配置
sources:
  inherit_global: true                    # 继承全局信息源
  override_scores: true                   # 用群维度评分覆盖全局评分
  add:                                    # 群专属新增信息源
    - url: https://arxiv.org/list/cs.AI/recent
      name: arXiv CS.AI
      type: rss
      tier: S
    - url: https://huggingface.co/blog/feed.xml
      name: HuggingFace Blog
      type: rss
      tier: A
  remove:                                 # 屏蔽全局中的某些源（群内不需要）
    - url: https://wallstreetcn.com/feed  # AI群不需要财经源

# 日报配置
daily_report:
  template: daily_template.md
  schedule: "0 8 * * *"                   # cron 表达式
  sections:
    - name: "行业动态"
      source_types: [rss, web]
      max_items: 5
    - name: "论文速递"
      source_types: [rss, arxiv]
      max_items: 3
    - name: "工具推荐"
      source_types: [github, producthunt]
      max_items: 2

# 群角色
soul_override: SOUL.md                    # 可选，覆盖全局角色
memory_override: MEMORY.md                # 可选，群专属记忆

# 技能配置
skills:
  inherit_global: true
  add:
    - source-evolution                    # 群内信息源进化
    - ai-daily-monitor                    # AI 监控
  remove:
    - stock-analysis-akshare              # 不需要股票分析
```

#### 信息源数据 `groups/{chat_id}/sources.json`

```json
{
  "version": 2,
  "chat_id": "oc_6ed1cc645057da3bbe93c6120219a61e",
  "sources": [
    {
      "id": "rss-arxiv-cs-ai-1713500000",
      "url": "https://arxiv.org/list/cs.AI/recent",
      "name": "arXiv CS.AI",
      "type": "rss",
      "tier": "S",
      "global_score": null,
      "group_score": {
        "overall": 0.92,
        "reliability": 0.95,
        "freshness": 0.88,
        "relevance": 0.95,
        "influence": 0.90,
        "trend": "stable",
        "fetch_frequency": "daily",
        "last_scored": "2026-04-24T00:00:00Z"
      },
      "discovered_from": "admin_manual",
      "created_at": "2026-04-20T00:00:00Z",
      "updated_at": "2026-04-24T00:00:00Z"
    }
  ],
  "discovered": [],
  "shared_links": [],
  "stats": {
    "total": 25,
    "by_tier": {"S": 3, "A": 8, "B": 10, "C": 3, "D": 1},
    "avg_score": 0.72
  }
}
```

#### 用户偏好 `groups/{chat_id}/users/{user_id}/preferences.json`

```json
{
  "user_id": "ou_d366ba075912a3865430a7fe7020454b",
  "chat_id": "oc_6ed1cc645057da3bbe93c6120219a61e",
  "display_name": "张三",
  "role": "admin",
  "interests": {
    "primary": ["LLM", "Agent框架", "RLHF"],
    "secondary": ["开源工具", "论文复现"]
  },
  "source_preferences": {
    "boost": ["arxiv", "huggingface-blog", "anthropic-blog"],
    "suppress": ["producthunt"],
    "custom_sources": []
  },
  "interaction_stats": {
    "questions_asked": 42,
    "links_shared": 15,
    "daily_reports_received": 90,
    "last_active": "2026-04-24T06:30:00Z"
  },
  "qa_categories": {
    "技术原理": 15,
    "行业动态": 12,
    "工具使用": 10,
    "论文讨论": 5
  }
}
```

#### 信息源权重 `groups/{chat_id}/users/{user_id}/source_weights.json`

```json
{
  "user_id": "ou_d366ba075912a3865430a7fe7020454b",
  "chat_id": "oc_6ed1cc645057da3bbe93c6120219a61e",
  "weights": {
    "rss-arxiv-cs-ai-1713500000": 1.2,
    "rss-huggingface-blog-1713500001": 1.1,
    "rss-techcrunch-1713500002": 0.8
  },
  "auto_learned": {
    "rss-arxiv-cs-ai-1713500000": {
      "click_count": 15,
      "positive_feedback": 12,
      "negative_feedback": 1,
      "learned_weight": 1.2
    }
  },
  "updated_at": "2026-04-24T06:30:00Z"
}
```

## 4. 评分体系

### 4.1 三级评分模型

现有 source-evolution 的 7 维评分是全局的。新体系引入三级评分：

```
最终源评分 = global_score × 0.3 + group_score × 0.5 + user_score × 0.2
```

| 评分级别 | 计算方式 | 作用 |
|---------|---------|------|
| **global_score** | 现有 7 维评分（reliability/freshness/relevance/completeness/diversity/influence/qualityRatio） | 全局基线，所有群共享 |
| **group_score** | 群内重算 relevance + influence，其余继承 global | 群维度排序，决定日报内容选取 |
| **user_score** | 用户行为加权（点击/分享/正负反馈） | 个性化推荐，不影响群排序 |

### 4.2 群维度 relevance 重算

```
group_relevance = semantic_similarity(source_topics, group_topics) × 0.6
                + group_member_engagement(source) × 0.2
                + source_daily_usage_in_group × 0.2
```

- `source_topics` — 信息源的主题标签（自动从内容中提取）
- `group_topics` — 群配置中的主题定义 + 群内讨论热词
- `group_member_engagement` — 群成员对该源的互动率（点击/分享/引用）
- `source_daily_usage_in_group` — 该源在群日报中的历史使用频率

### 4.3 用户维度权重

```
user_weight = base_weight × feedback_modifier

feedback_modifier:
  - 用户分享该源的链接 → +0.2
  - 用户引用该源的内容 → +0.1
  - 用户点击日报中该源的文章 → +0.05
  - 用户跳过/忽略该源的文章 → -0.05
  - 用户明确表示不喜欢 → -0.2
```

用户权重**不**影响群的日报内容选取（避免个人偏好绑架群体），只在用户单独问问题时用于个性化排序。

## 5. 进化机制

### 5.1 群维度进化

```
群内消息 → 提取链接/话题 → 评估与群主题相关性 → 注册到群信息源 → 群维度评分 → 日报使用 → 反馈修正
```

**触发条件**:
- 群内用户分享链接（trusted 以上用户分享的链接置信度更高）
- 群内讨论中出现新的高频话题（通过关键词/实体提取检测）
- cron 定期扫描群内未跟踪的链接

**进化规则**:
1. 新源先以 Tier C 注册到群信息源，经 3 次评分后根据表现升降 Tier
2. 群维度评分 < 0.3 连续 5 次的源自动降频，< 0.3 连续 10 次移至 `discovered` 池（不删除，只是不采集）
3. 群信息源数量上限 50 个（可配置），超出时淘汰最低分源

### 5.2 用户维度进化

```
用户在群内问答 → 提取兴趣点 → 更新 preferences.json → 调整 source_weights.json → 下次问答结果更精准
```

**触发条件**:
- 用户在群中提问（自动提取问题类别和关键词）
- 用户分享链接（分享的源获得 weight boost）
- 用户对日报内容做出反应（点赞/引用/忽略）

**进化规则**:
1. 用户偏好每 10 次交互更新一次（避免单次噪音）
2. 兴趣标签最多 10 个 primary + 15 个 secondary，超出时淘汰最久未激活的
3. source_weights 衰减机制：30 天无交互的权重向 1.0 回归（避免历史偏好固化）

### 5.3 跨群进化隔离

```
Group A 进化的信息源 ≠ Group B 自动获得

跨群信息流:
  Group A 新源 → global discovered 池 → Group B 的 source-evolution 评估 → 决定是否引入
```

- 群内发现的新源**不**自动进入全局池，只在群内生效
- 管理员可手动将群内表现好的源（group_score ≥ 0.8）"晋升"到全局
- 全局源自动继承到所有开启了 `inherit_global: true` 的群

## 6. 日报系统适配

### 6.1 群日报生成流程

```
cron 触发
  → 读取群 config.yaml (模板、schedule)
  → 读取群 sources.json (信息源列表)
  → 读取群 sources_scores.json (排序)
  → 按 group_score 排序选取 Top-N 源
  → 采集内容 (并行 web_fetch)
  → 按模板分 section 汇总
  → 生成群日报
  → 发送到群频道
```

### 6.2 个性化日报（可选）

如果 `config.yaml` 开启 `personalized_daily: true`：

```
群日报基础上
  → 读取群内所有用户的 source_weights
  → 为每个用户生成个性化 Section（"为你推荐"）
  → 附加在群日报末尾
  → @对应用户
```

## 7. 技能注入机制

### 7.1 现有机制

技能通过 `agent/skill_commands.py` 扫描 `~/.hermes/skills/` 目录，将 SKILL.md 内容作为 **user message** 注入 agent 上下文。

### 7.2 新增群维度注入

在 `build_session_context_prompt()` 中，当 `chat_type == "group"` 时：

```python
# 伪代码
if source.chat_type == "group":
    group_dir = get_hermes_home() / "groups" / source.chat_id
    
    # 1. 群角色覆盖
    if (group_dir / "SOUL.md").exists():
        lines.append(read(group_dir / "SOUL.md"))
    
    # 2. 群记忆
    if (group_dir / "MEMORY.md").exists():
        lines.append(read(group_dir / "MEMORY.md"))
    
    # 3. 群信息源摘要（Top 10 + 评分）
    if (group_dir / "sources.json").exists():
        sources = load(group_dir / "sources.json")
        top_sources = sorted(sources, key=lambda s: s["group_score"]["overall"], reverse=True)[:10]
        lines.append(format_sources_brief(top_sources))
    
    # 4. 群内用户偏好摘要（当前提问用户）
    user_dir = group_dir / "users" / source.user_id
    if (user_dir / "preferences.json").exists():
        prefs = load(user_dir / "preferences.json")
        lines.append(format_user_prefs_brief(prefs))
```

### 7.3 source-evolution 适配

当 agent 在群聊中调用 source-evolution 技能时，需要传入 `chat_id` 上下文：

```
现有: evolution.ingestSharedLink({url, sharedBy, ...})
新增: evolution.ingestSharedLink({url, sharedBy, chatId, ...})
```

source-evolution 内部根据 `chatId` 决定信息源注册到哪个群的数据目录。

## 8. API 设计

### 8.1 GroupContext API

```python
class GroupContext:
    """群维度上下文管理器"""
    
    def __init__(self, hermes_home: Path, chat_id: str):
        self.group_dir = hermes_home / "groups" / chat_id
        self.chat_id = chat_id
    
    def get_sources(self, include_global: bool = True) -> list[Source]:
        """获取群信息源（合并全局+群专属）"""
        
    def add_source(self, source: Source, added_by: str, role: str) -> Source:
        """添加群专属信息源（需检查 role 权限）"""
    
    def remove_source(self, source_id: str, removed_by: str, role: str) -> bool:
        """移除群信息源"""
    
    def score_sources(self) -> list[SourceScore]:
        """对群信息源进行群维度评分"""
    
    def get_user_context(self, user_id: str) -> UserContext:
        """获取群内用户上下文"""
    
    def get_daily_sources(self, section: str, limit: int) -> list[Source]:
        """按 section 获取日报用的信息源（按 group_score 排序）"""
    
    def promote_to_global(self, source_id: str) -> bool:
        """将群信息源晋升到全局"""
    
    def get_stats(self) -> GroupStats:
        """获取群统计信息"""
```

### 8.2 UserContext API

```python
class UserContext:
    """群内用户上下文管理器"""
    
    def __init__(self, group_dir: Path, chat_id: str, user_id: str):
        self.user_dir = group_dir / "users" / user_id
    
    def get_preferences(self) -> UserPreferences:
        """获取用户偏好"""
    
    def update_preferences(self, interaction: Interaction) -> None:
        """从交互中更新用户偏好"""
    
    def get_source_weights(self) -> dict[str, float]:
        """获取用户对信息源的个性化权重"""
    
    def record_qa(self, question: str, categories: list[str]) -> None:
        """记录问答，提取兴趣点"""
    
    def record_feedback(self, source_id: str, feedback: str) -> None:
        """记录对信息源的反馈（positive/negative/neutral）"""
```

## 9. 权限控制集成

### 9.1 与受限频道权限系统的关系

| 角色 | 群信息源操作 | 群配置 | 用户偏好 | 全局操作 |
|------|-------------|--------|---------|---------|
| **admin** | 增删改查 + 晋升全局 | 读写 | 读写所有人的 | 完全放行 |
| **trusted** | 增改（添加新源、分享链接触发进化） | 只读 | 读写自己的 | 通过 approval |
| **普通用户** | 通过 approval 提交 | 只读 | 读写自己的 | 通过 approval |
| **blacklisted** | 无 | 无 | 无 | 无 |

### 9.2 信息源操作权限矩阵

| 操作 | admin | trusted | 普通用户 |
|------|-------|---------|---------|
| 查看群信息源 | ✅ | ✅ | ✅ |
| 添加信息源 | ✅ 直接入库 | ✅ 直接入库 | ⚠️ 需 approval |
| 删除信息源 | ✅ | ❌ 需 approval | ❌ 需 approval |
| 修改信息源 Tier | ✅ | ❌ 需 approval | ❌ 需 approval |
| 晋升信息源到全局 | ✅ | ❌ 需 approval | ❌ 需 approval |
| 屏蔽全局信息源 | ✅ | ❌ 需 approval | ❌ 需 approval |
| 更新自己的偏好 | ✅ | ✅ | ✅ |
| 查看他人偏好 | ✅ | ❌ | ❌ |

## 10. 实现路径

### Phase 1: 数据层 (1-2天)

1. 创建 `groups/` 目录结构
2. 实现 `GroupContext` + `UserContext` 类
3. 实现群的 `sources.json` 读写 + 全局继承逻辑
4. 实现用户的 `preferences.json` + `source_weights.json` 读写

### Phase 2: 注入层 (1天)

5. 修改 `build_session_context_prompt()` — 注入群角色/记忆/信息源摘要/用户偏好
6. 修改 `source-evolution` 技能 — 接收 `chatId` 参数，注册到对应群

### Phase 3: 评分层 (1-2天)

7. 实现群维度 relevance 重算
8. 实现用户维度权重学习（从交互中自动学习）
9. 实现三级评分合并公式

### Phase 4: 日报层 (1天)

10. 修改日报生成逻辑 — 从群 `sources.json` + `daily_template.md` 生成
11. 可选：个性化日报 Section

### Phase 5: 进化层 (1-2天)

12. 实现群内链接自动发现 → 群信息源注册
13. 实现群维度自动评分 + Tier 升降
14. 实现跨群晋升机制

### Phase 6: 权限集成 (1天)

15. 扩展受限频道权限系统 — 信息源操作权限矩阵
16. 扩展 approval 队列 — 支持信息源变更审批类型

## 11. 与现有系统的兼容性

| 现有组件 | 影响 | 兼容方案 |
|---------|------|---------|
| `source-evolution` 技能 | 需要适配 chatId | 新增 chatId 参数，未传时退化为全局模式 |
| `knowledge-base` 技能 | 无直接影响 | GroupContext 可复用其 SourceManager |
| `MEMORY.md` / `USER.md` | 保留全局 | 群维度 MEMORY.md 是附加层，不覆盖全局 |
| `build_session_key()` | 无需修改 | 群隔离通过数据目录实现，不依赖 session key |
| `restricted_channels` | 需扩展 | 新增信息源操作权限（见 §9） |
| 日报 cron | 需适配 | 从群 config.yaml 读取模板和 schedule |
| `skill_commands.py` | 需扩展 | 注入群维度上下文到 agent prompt |
| `channel_skill_bindings` (Discord) | 参考模式 | 扩展为跨平台，增加群维度状态 |
| `channel_prompts` | 参考模式 | 群 SOUL.md / MEMORY.md 复用此注入机制 |
| `llm-wiki` ($WIKI_PATH) | 设计缺陷 | 当前 `~/wiki` 不随 profile 隔离，需改为 `HERMES_HOME/groups/{chat_id}/wiki/` |
| Memory flush (会话过期保存) | 需扩展 | 群会话 flush 时写入群 MEMORY.md 而非全局 |

## 12. 现有集成点参考

### 12.1 channel_skill_bindings (Discord)

Discord 已支持频道级技能绑定，但**无状态**：

```python
# gateway/run.py — Discord channel_skill_bindings
# 配置方式: config.extra.channel_skill_bindings = [{id: "channel_xxx", skills: ["skill-a"]}]
# 限制: 仅 Discord, 仅频道级, 无进化状态
```

新体系扩展为跨平台 + 群维度 + 有状态：

```
旧: channel_skill_bindings → 无状态地注入 SKILL.md 内容
新: groups/{chat_id}/config.yaml → 注入 SKILL.md + 群信息源 + 用户偏好 + 进化状态
```

### 12.2 channel_prompts (跨平台)

所有平台支持频道级临时系统提示：

```python
# gateway/platforms/base.py: resolve_channel_prompt()
# 配置方式: config.channel_prompts.telegram = {chat_id: "你是AI助手"}
# 特点: 注入为 ephemeral_system_prompt, 不修改核心系统提示
```

群维度 SOUL.md / MEMORY.md 可复用此注入路径。

### 12.3 Memory Flush

会话过期时，gateway 运行 flush agent 将对话中的重要事实保存到 MEMORY.md：

```python
# gateway/run.py:878-997 — session expiry flush
# 当前: flush → 全局 MEMORY.md / USER.md
# 扩展: flush → 群 MEMORY.md (群维度事实) + 用户 preferences.json (兴趣更新)
```

### 12.4 Session Key 作为用户边界

`build_session_key()` 在群聊中已按 `chat_id:user_id` 隔离（`group_sessions_per_user=True`）：

```
agent:main:feishu:group:oc_6ed1cc:ou_d366ba  ← 用户A在AI日报群的会话
agent:main:feishu:group:oc_6ed1cc:ou_aaa111  ← 用户B在AI日报群的会话
```

新体系无需修改 session key 逻辑——群维度隔离通过数据目录（`groups/{chat_id}/`）实现，用户维度通过 `groups/{chat_id}/users/{user_id}/` 实现。session key 仅用于会话管理，与数据隔离解耦。
