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

---

## 13. 模块化设计：最小改动 + 可插拔

### 13.1 设计原则

群进化体系必须是一个**独立模块**，可以：
- 通过 config 开关启用/禁用（`group_evolution.enabled: true`）
- 不启用时零侵入——不创建目录、不注入 prompt、不拦截工具调用
- 启用后通过现有 Hook 系统接入，不修改核心代码路径

### 13.2 模块结构

```
hermes-agent/
├── gateway/
│   ├── group_evolution/                    # 新模块：完整自包含
│   │   ├── __init__.py                     # 模块入口 + 开关检测
│   │   ├── context.py                      # GroupContext + UserContext
│   │   ├── sources.py                      # 群信息源管理（继承、覆盖、评分）
│   │   ├── scoring.py                      # 三级评分引擎
│   │   ├── versioning.py                   # 版本管理系统
│   │   ├── evolution.py                    # 进化引擎（发现、评分、升降级）
│   │   ├── prompt_injector.py              # 群维度 prompt 注入
│   │   ├── daily_report.py                 # 群日报生成
│   │   ├── config_loader.py                # 热重载配置加载器
│   │   ├── engine_router.py                # 分层推理引擎路由
│   │   ├── capability_test.py              # 引擎能力测试例
│   │   └── merge_policy.py                 # 个人→群 技能合并策略
│   └── hooks/                              # 现有 Hook 系统（不改）
│       └── group_evolution/                # 新 Hook：模块接入点
│           ├── HOOK.yaml
│           └── handler.py                  # 监听 agent:start/end/step
```

### 13.3 核心代码改动点（仅3处，每处≤5行）

**改动1: `gateway/run.py` — agent 启动时注入群上下文**（~line 9200）

```python
if source.chat_type == "group":
    try:
        from gateway.group_evolution import inject_group_context
        inject_group_context(source, enabled_toolsets, user_config)
    except ImportError:
        pass  # 模块未安装，跳过
```

**改动2: `gateway/session.py` — 构建系统提示词时追加群信息**

```python
if context.source.chat_type == "group":
    try:
        from gateway.group_evolution.prompt_injector import build_group_prompt
        group_lines = build_group_prompt(context.source)
        lines.extend(group_lines)
    except ImportError:
        pass
```

**改动3: `gateway/run.py` — agent 结束时触发进化**

```python
if source.chat_type == "group":
    try:
        from gateway.group_evolution import record_interaction
        record_interaction(source, final_response)
    except ImportError:
        pass
```

### 13.4 Hook 接入

```yaml
# ~/.hermes/hooks/group_evolution/HOOK.yaml
name: group-evolution
description: Per-group skill evolution system
events:
  - agent:start     # 注入群上下文到 agent
  - agent:end       # 记录交互，触发进化
  - agent:step      # 拦截信息源操作，检查权限
  - session:end     # flush 群记忆
  - gateway:startup # 加载群配置，注册 cron
```

```python
# ~/.hermes/hooks/group_evolution/handler.py
async def handle(event_type, context):
    from gateway.group_evolution import handle_hook
    await handle_hook(event_type, context)
```

### 13.5 启用/禁用

```yaml
# config.yaml
group_evolution:
  enabled: true                   # 总开关
  data_dir: "groups"              # 相对于 HERMES_HOME
  max_groups: 50
  max_sources_per_group: 50
  max_users_per_group: 200
  evolution_interval: 3600        # 进化周期（秒）
  daily_report_default: true
```

禁用时：`ImportError` 被捕获，三处改动点全部 no-op，零开销。

---

## 14. 配置热重载

### 14.1 设计原则

- 修改群配置后**不需要重启 gateway** 即可生效
- 热重载粒度：群级别（改一个群的配置只重载该群）
- 热重载期间不影响正在进行的对话

### 14.2 实现机制

```python
# gateway/group_evolution/config_loader.py

class GroupConfigLoader:
    """带热重载的群配置加载器 — 基于 mtime 检测"""
    
    def __init__(self, hermes_home: Path):
        self._cache: Dict[str, GroupConfig] = {}         # chat_id → GroupConfig
        self._mtimes: Dict[str, float] = {}               # chat_id → 文件修改时间
        self._lock = asyncio.Lock()
    
    async def get(self, chat_id: str) -> Optional[GroupConfig]:
        config_path = self._hermes_home / "groups" / chat_id / "config.yaml"
        if not config_path.exists():
            return None
        
        current_mtime = config_path.stat().st_mtime
        if chat_id in self._cache and self._mtimes.get(chat_id) == current_mtime:
            return self._cache[chat_id]  # 缓存命中
        
        async with self._lock:
            config = GroupConfig.from_yaml(config_path)
            self._cache[chat_id] = config
            self._mtimes[chat_id] = current_mtime
            return config
    
    def invalidate(self, chat_id: str) -> None:
        self._cache.pop(chat_id, None)
        self._mtimes.pop(chat_id, None)
```

**热重载触发方式**:

| 触发方式 | 实现路径 | 延迟 |
|---------|---------|------|
| **自动检测** | 每次读取时检查 mtime | 实时 |
| **SIGHUP 信号** | gateway 收到 SIGHUP → `invalidate_all()` | 秒级 |
| **slash 命令** | `/group reload [chat_id]` | 立即 |
| **API 调用** | `GroupContext.reload()` | 立即 |

**热重载范围**:

| 配置项 | 支持热重载 | 说明 |
|-------|-----------|------|
| 群信息源 (sources.json) | ✅ | 下次 agent 调用时生效 |
| 群角色 (SOUL.md) | ✅ | 下次会话的 system prompt |
| 群记忆 (MEMORY.md) | ✅ | 同上 |
| 日报模板 (daily_template.md) | ✅ | 下次 cron 触发生效 |
| 日报 schedule | ✅ | 重置 cron timer |
| 用户角色 (users 列表) | ✅ | 下次消息到达时检查 |
| 全局开关 (enabled) | ❌ | 需重启 gateway |

### 14.3 运行中状态保护

- Agent 的 system prompt 在会话开始时构建，中途不变更
- 信息源评分变更在**下一个进化周期**生效，不中断当前评分
- 正在执行的 cron 日报任务**不中断**，下次执行时用新配置

---

## 15. 分层推理引擎

### 15.1 三层推理架构

```
┌───────────────────────────────────────────────────┐
│                    应用层                          │
│   群日报 / 问答 / 深度研究 / 价值发现              │
└────────────────────┬──────────────────────────────┘
                     │ engine_router.route(task)
┌────────────────────▼──────────────────────────────┐
│               引擎路由层                           │
│   根据任务类型 + 群配置 + 能力测试结果选择引擎      │
└──┬─────────────┬──────────────┬───────────────────┘
   │             │              │
┌──▼──┐     ┌───▼───┐    ┌────▼────┐
│ L1  │     │  L2   │    │   L3    │
│数据层│     │能力层  │    │价值层   │
│轻量 │     │标准   │    │高端    │
│模型 │     │模型   │    │模型    │
└─────┘     └───────┘    └────────┘
```

### 15.2 引擎配置

```yaml
group_evolution:
  engines:
    l1_data:                          # 数据获取层
      model: "xunfei/astron-code"
      max_tokens: 4096
      timeout: 30
      cost_per_1k: 0.002
      
    l2_capability:                    # 能力获取层
      model: "anthropic/claude-sonnet-4-20250514"
      max_tokens: 8192
      timeout: 60
      cost_per_1k: 0.01
      
    l3_value:                         # 价值层
      model: "anthropic/claude-opus-4-20250514"
      max_tokens: 16384
      timeout: 120
      cost_per_1k: 0.05
      requires_approval: true
```

### 15.3 任务路由

| 任务类型 | 引擎层级 | 说明 |
|---------|---------|------|
| source_fetch, source_score, daily_summary, fact_lookup, data_clean | L1 | 事实查询、格式化 |
| source_assess, trend_analysis, cross_reference, logic_compose, daily_deep_analysis | L2 | 分析、推理、逻辑组合 |
| value_discovery, strategic_decision, causal_inference, value_chain_validation, paradigm_shift_detection | L3 | 战略决策、价值发现 |

### 15.4 能力测试系统

系统启动时和每天定期运行能力测试，验证配置的引擎是否满足最低要求：

```python
CAPABILITY_TESTS = {
    "l1_data": [
        {"name": "basic_extraction", "min_pass_rate": 0.95,
         "assert": "从文本中提取所有URL和作者名，结果非空"},
        {"name": "data_formatting", "min_pass_rate": 0.99,
         "assert": "将原始数据格式化为JSON，结构正确"},
    ],
    "l2_capability": [
        {"name": "trend_identification", "min_pass_rate": 0.80,
         "assert": "分析3条新闻的共同趋势，输出>100字"},
        {"name": "causal_chain", "min_pass_rate": 0.75,
         "assert": "推理因果关系，含因果关键词"},
        {"name": "logic_composition", "min_pass_rate": 0.70,
         "assert": "组合3个原子逻辑完成综合分析，输出>300字"},
    ],
    "l3_value": [
        {"name": "value_pattern_discovery", "min_pass_rate": 0.60,
         "assert": "从10个事件中识别价值模式"},
        {"name": "paradigm_detection", "min_pass_rate": 0.50,
         "assert": "论证是否构成范式转移，输出>500字"},
    ],
}
```

**降级策略**: L3 测试不通过 → L3 任务降级到 L2（质量降低但不中断）。测试结果持久化到 `groups/.engine_test_results.json`。

---

## 16. 版本体系：群策群力共同进化

### 16.1 核心理念

> 个人的改进可以合并进入群的技能。一旦合并，个人技能隐藏但不删除，以便回滚。新的演进基于新群技能版本继续。

### 16.2 三级版本号

```
版本格式: {major}.{group}.{personal}

major     = 管理者牵引的主动版本合并升级（大版本）
group     = 群技能独立进化（群版本，继承大版本号）
personal  = 个人技能独立进化（个人版本，可选用大版本或群版本）

示例:
  2.3.7  = 第2大版本 → 群第3次进化 → 个人第7次演进
  1.0.0  = 初始大版本，尚未独立进化
  2.1.0  = 个人基于群版本尚未演进
```

### 16.3 版本继承关系

```
大版本 2.0.0 (管理员发布)
  └── 群版本 2.1.0 (群内进化)
       ├── 个人A: 2.1.3 (演进3次)
       ├── 个人B: 2.1.1 (演进1次)
       └── 个人C: 2.0.0 (未演进，直接用大版本)
  └── 群版本 2.2.0 (群内第2次进化)
       └── 个人A: 2.2.0 (重置到新群版本)

大版本 3.0.0 (管理员发布，合并群2.2.0精华)
```

### 16.4 版本存储

```json
// groups/{chat_id}/versions.json
{
  "current_major": 2,
  "group_versions": {
    "2.0": {"released_at": "...", "changes": "初始大版本2.0", "merged_from_personal": []},
    "2.1": {"released_at": "...", "changes": "新增3个信息源", "merged_from_personal": ["ou_aaa:2.0.2"]}
  },
  "personal_versions": {
    "ou_aaa": {
      "base_group_version": "2.1",
      "current": "2.1.2",
      "hidden_since_merge": null,
      "versions": {
        "2.1.0": {"changes": "继承群版本"},
        "2.1.1": {"changes": "偏好调整：增加宏观权重"},
        "2.1.2": {"changes": "新增2个个人定制信息源"}
      }
    }
  }
}
```

### 16.5 个人→群合并流程

```
1. 管理员审查: /group review-personal {chat_id}
2. 选择合并:  /group merge-personal {chat_id} --from ou_aaa:2.1.2
3. 合并执行:
   → 个人 diff 应用到群技能
   → 群版本 +1 (2.1 → 2.2)
   → 被合并个人版本标记 hidden_since_merge = "2.2"
   → 个人技能存入 users/{user_id}/archived/{version}/ (不删除!)
4. 回滚:     /group rollback {chat_id} --to 2.1
```

### 16.6 大版本升级

```
1. 管理员触发: /group major-upgrade {chat_id} --version 3
2. 合并策略:
   → 所有群的 S/A 级信息源 → 大版本 3.0 全局基线
   → 高频使用逻辑 → 大版本 3.0 默认模板
3. 发布: 所有群继承新大版本，群版本重置为 3.0.0
4. 回滚: /group rollback {chat_id} --major 2
```

---

## 17. 进化能力分级

### 17.1 L1: 数据获取层 — "数据可得 + 数据质量"

```
L1.1 数据可得
  ├── 信息源发现 (用户分享、文章引用、RSS)
  ├── 信息源注册 (自动评估Tier、初始评分)
  ├── 信息源可达性 (URL有效性、RSS可用性)
  └── 数据采集 (web_fetch、RSS解析、API)

L1.2 数据质量
  ├── 数据清洗 (去重、格式统一、编码修正)
  ├── 数据解释 (实体提取、语义标注、分类打标)
  ├── 数据对齐 (时间线对齐、跨源实体归一、单位统一)
  └── 质量评分 (完整性、准确性、时效性、权威性)

L1.3 数据验证
  ├── 交叉验证 (多源比对、矛盾检测)
  ├── 信源可信度 (历史准确率、撤稿记录、偏见指数)
  ├── 事件追溯 (溯源链、一手/二手/N手标记)
  └── 时间线验证 (时序一致性、因果链合理性)
```

**L1 进化指标**:

| 指标 | 衡量 | 目标 |
|------|------|------|
| 信息源覆盖率 | 主题关键词被现有源覆盖的比例 | ≥80% |
| 数据新鲜度 | 最后成功采集距今时间 | ≤24h |
| 数据可信度 | 交叉验证通过率 | ≥90% |
| 采集成功率 | 采集请求成功率 | ≥95% |

### 17.2 L2: 能力获取层 — "分析逻辑 + 逻辑组合"

```
L2.1 原子逻辑
  ├── 趋势识别 (上升/下降/拐点/周期)
  ├── 异常检测 (突发、偏离、结构性变化)
  ├── 关联分析 (A变化与B变化的相关性)
  ├── 归因分析 (直接/间接原因)
  ├── 预测外推 (基于历史趋势的短期预测)
  └── 对比分析 (横向跨源、纵向跨期)

L2.2 逻辑组合
  ├── 任务模板 (日报=趋势+异常+关联)
  ├── 条件触发 (IF 异常 THEN 深入归因)
  ├── 串行流水 (采集→清洗→分析→摘要)
  ├── 并行聚合 (多源并行→交叉验证→合并)
  └── 迭代深化 (初步分析→发现疑问→深入→修正)

L2.3 逻辑进化
  ├── 模板优化 (用户反馈调整分析步骤)
  ├── 新逻辑发现 (从成功分析提取可复用模式)
  ├── 逻辑参数调优 (阈值、权重、窗口期)
  └── 失败逻辑淘汰 (低效/误导模式降权)
```

**L2 进化指标**:

| 指标 | 衡量 | 目标 |
|------|------|------|
| 分析覆盖率 | 问题能用原子逻辑回答的比例 | ≥70% |
| 逻辑复用率 | 新任务复用已有模板的比例 | ≥50% |
| 用户满意度 | 分析结果被正面反馈的比例 | ≥80% |
| 预测准确率 | 预测与实际一致 | ≥60% |

### 17.3 L3: 价值层 — "目标→模式→发现→验证→推荐"

```
L3.1 目标定义
  ├── 显性目标 (用户明确提出)
  ├── 隐性目标 (从行为推断)
  └── 目标分解 (大目标→可验证子目标)

L3.2 价值模式
  ├── 价值信号 (数据中的机会/风险信号)
  ├── 价值模式 (反复出现的信号组合)
  ├── 模式匹配 (新数据匹配已知模式)
  └── 模式进化 (模式随环境变化调整)

L3.3 价值自动发现
  ├── 主动扫描 (非问答场景下寻找价值信号)
  ├── 跨域关联 (不同领域交叉产生新价值)
  ├── 长尾发现 (低频信号中的隐藏价值)
  └── 反共识识别 (与主流相反的信号)

L3.4 价值链验证
  ├── 价值链构建 (信号→推断→行动→收益)
  ├── 链条验证 (每步置信度评估)
  ├── 风险评估 (链条断裂可能性和后果)
  └── 链条分级 (高/中/低置信度分级)

L3.5 价值推荐
  ├── 推荐排序 (期望价值×置信度×用户偏好 综合排序)
  ├── 个性化适配 (按用户角色/兴趣/风险偏好筛选)
  ├── 推荐呈现 (紧急告警/日报嵌入/定期推送/被动响应)
  ├── 推荐追踪 (推荐→查看→行动→结果 闭环反馈)
  └── 推荐进化 (高转化推荐强化，低转化降权或调呈现)
```

**推荐呈现的四种通道**:

| 通道 | 触发条件 | 典型场景 | 侵入性 |
|------|---------|---------|--------|
| **紧急告警** | 高置信度 + 高时效性（链条可能很快失效） | 突发政策变化影响持仓 | 高（主动推送+@用户） |
| **日报嵌入** | 中置信度 + 时效性适中 | 趋势信号写入次日日报的"重点关注" | 中（随日报一起） |
| **定期推送** | 低时效性 + 需要长期观察 | 月度价值模式汇总 | 低（周期性推送） |
| **被动响应** | 用户主动查询时附加相关推荐 | 用户问某行业时推荐关联价值链 | 最低（不主动打扰） |

**推荐追踪闭环**:

```
推荐发出 → 用户是否查看(打开/点击) → 是否行动(采纳建议) → 结果如何(正/负反馈)
    │                                    │                       │
    ▼                                    ▼                       ▼
 未查看→调整通道/呈现                未行动→降低置信度/调整话术   正反馈→强化该推荐模式
 或降低推送优先级                   或补充论据                  负反馈→降权/暂停该类推荐
```

**L3 进化指标**:

| 指标 | 衡量 | 目标 |
|------|------|------|
| 价值发现率 | 主动发现的有效信号数/周期 | ≥1/天 |
| 模式命中率 | 匹配的模式后续被证实的比率 | ≥40% |
| 价值链完整度 | 推荐的价值链可完整追踪的比率 | ≥60% |
| 推荐到达率 | 验证通过的价值链成功推荐给用户的比率 | ≥90% |
| 推荐查看率 | 用户实际查看推荐内容的比率 | ≥50% |
| 行动转化率 | 价值推荐导致用户行动的比率 | ≥20% |
| 推荐进化率 | 推荐策略因反馈调整的频率 | ≥1次/周 |

### 17.4 层级关系与进化阶段

```
L3 价值层 ←──需求反哺──→ L1 数据层
▲     │                   │
│     └─反馈反哺─→ L2 能力层
│                         │
│                         ▼
└──────── L2 能力层 ────────┘

L1 是 L2 基础: 没有可信数据，分析逻辑无意义
L2 是 L3 基础: 没有分析能力，价值发现是空中楼阁
L3 是输出层: 发现并验证的价值必须推荐给用户才能形成闭环
L3 反哺 L1: 价值发现揭示新信息源需求 → L1 扩展采集
L3 反哺 L2: 推荐追踪反馈 → L2 逻辑参数调优
```

**群的进化阶段判定**:

| 阶段 | 条件 | 可执行任务 |
|------|------|-----------|
| 种子期 | L1 指标 <50% | 仅数据采集和基础问答 |
| 成长期 | L1 ≥80%, L2 <50% | 分析 + 问答，无主动价值发现 |
| 成熟期 | L2 ≥70%, L3 <30% | 主动价值发现 + 推荐 |
| 自主期 | L3 ≥40% | 完整价值链自动发现、验证和推荐，闭环反馈驱动进化 |

---

## 18. 应用场景

### 18.1 场景A: 服务场景 (多对1)

```
多个用户 ──提问──→ Agent ──回答──→ 各用户
特点: 并发独立问答，用户之间无交互
典型: AI日报群中用户各自问股票/技术/行业问题
```

**设计支撑**: group_sessions_per_user=True → 每用户独立会话；L2 用户偏好 → 个性化排序；L1 信息源 → 群信息源检索；L2 原子逻辑 → 按问题类型选择分析逻辑。

**进化路径**: 用户频繁问某类问题 → L2 自动注册该类分析逻辑 → 用户反馈质量 → L2 参数调优 → 新问题类型 → L1 扩展信息源。

### 18.2 场景B: 群策群力场景 (多对多)

```
用户A ──分享链接──→ 群 ──Agent处理──→ 群知识库
用户B ──补充观点──→ 群 ──Agent关联──→ 知识图谱更新
用户C ──提出质疑──→ 群 ──Agent验证──→ 交叉验证结果
                     ──群记忆更新──→ 所有人受益
```

**特点**: 用户之间有交互，知识共建
**典型**: 财经群中多人讨论某个行业趋势，各贡献不同视角

**设计支撑**: 共享会话模式 + L1 交叉验证 + L2 逻辑组合 + L3 价值发现 + 版本合并。

**进化路径**: 多人分享同类源 → L1 提升该源 Tier → 讨论中产生新观点 → L2 新增原子逻辑 → 观点被验证 → L3 形成价值模式 → 个人洞察被群采纳 → 版本合并。

### 18.3 场景C: 管理场景 (1对多)

```
管理员 ──指令──→ Agent ──执行──→ 群配置/内容
                              ──通知──→ 所有用户
```

**特点**: 单向管理，管理员驱动
**典型**: 管理员添加新信息源、调整日报模板、升级大版本

**设计支撑**: admin 角色权限 + 大版本升级 + 个人→群合并 + 配置热重载。

### 18.4 场景D: 驾驶舱场景 (混合)

```
管理员 ──监控面板──→ 群进化指标
       ──实时调整──→ 引擎路由/权限/信息源
用户   ──正常交互──→ 问答/分享/讨论
Agent  ──持续进化──→ L1/L2/L3 自动进化
       ──异常告警──→ 管理员介入
```

**特点**: 管理与运营并行，实时监控 + 主动干预

**告警规则**:

| 告警 | 触发条件 | 动作 |
|------|---------|------|
| 信息源失效 | >30% 信息源连续3次采集失败 | 通知管理员 + 自动降频 |
| 评分骤降 | 群平均评分一周内下降>20% | 触发 L1 全面验证 |
| 成本异常 | 单日 L3 调用超过上限 | 降级到 L2 + 通知 |
| 价值链断裂 | L3 推荐验证失败率>50% | 暂停 L3 自动推荐 |

### 18.5 场景→功能→设计映射

| 场景 | 核心功能 | 设计支撑 | 进化层级 |
|------|---------|---------|---------|
| **A: 服务** | 个性化问答 | 用户偏好 + 信息源权重 + L1/L2 | L1→L2 |
| **A: 服务** | 日报推送 | 群模板 + 群信息源排序 | L1 |
| **B: 群策群力** | 知识共建 | 共享会话 + 交叉验证 + 版本合并 | L1→L2→L3 |
| **B: 群策群力** | 观点碰撞 | 多视角分析 + 共识/分歧识别 | L2→L3 |
| **B: 群策群力** | 贡献追踪 | 版本体系 + 个人→群合并 | 版本系统 |
| **C: 管理** | 信息源管理 | admin权限 + 热重载 + 能力测试 | L1 |
| **C: 管理** | 版本升级 | 三级版本号 + 大版本发布 | 版本系统 |
| **C: 管理** | 权限控制 | admin/trusted/普通 + 操作矩阵 | 权限系统 |
| **D: 驾驶舱** | 健康监控 | 进化指标 + 告警规则 | 全层级 |
| **D: 驾驶舱** | 引擎切换 | 分层推理 + 降级策略 | L1/L2/L3 |
| **D: 驾驶舱** | 成本控制 | 引擎路由 + 调用上限 + 降级 | 全层级 |
| **D: 驾驶舱** | 异常干预 | Hook告警 + 热重载 + 回滚 | 全层级 |

### 18.6 场景组合示例

```
财经日报群的一天:
  08:00  → 场景C (管理员触发cron日报推送)
  09-12  → 场景A (用户各自问个股/宏观问题)
  午休   → 场景B (群内讨论热点，群策群力)
  全天   → 场景D (管理员监控，异常告警)
  月末   → 场景C (合并个人贡献，发布新群版本)
```

---

## 19. 实现路径（更新）

### Phase 0: 模块骨架 (1天)
1. 创建 `gateway/group_evolution/` 模块结构
2. 创建 Hook 接入点
3. 实现 `config_loader.py`（热重载基础）
4. 实现 `__init__.py`（开关检测 + 条件导入）
5. 修改 `run.py` + `session.py` 的3处改动点

### Phase 1: 数据层 (1-2天)
6. 实现 `context.py` (GroupContext + UserContext)
7. 实现 `sources.py` (群信息源管理)
8. 实现 `versioning.py` (三级版本号)
9. 群目录结构自动创建

### Phase 2: 注入层 (1天)
10. 实现 `prompt_injector.py`
11. 群 SOUL.md / MEMORY.md / 信息源摘要注入

### Phase 3: 评分层 (1-2天)
12. 实现 `scoring.py` (三级评分)
13. 用户偏好学习

### Phase 4: 引擎层 (1-2天)
14. 实现 `engine_router.py`
15. 实现 `capability_test.py`
16. 降级策略

### Phase 5: 进化层 (1-2天)
17. 实现 `evolution.py`
18. L1/L2/L3 进化逻辑
19. 实现 `merge_policy.py` (个人→群合并)

### Phase 6: 日报+场景 (1天)
20. 实现 `daily_report.py`
21. 四种场景的配置预设

### Phase 7: 运维 (1天)
22. 进化指标仪表盘
23. 告警规则
24. 回滚机制

**总估时: 8-12天**
