# 受限频道权限系统 v2

## 概述

Hermes Gateway 支持对飞书群聊频道设置权限控制，限制不同用户在群中的操作范围。v2 在原有 whitelist/blacklist 二级权限基础上，新增 **trusted** 角色级别，支持更细粒度的权限分级。

## 权限级别

| 角色 | 问答 | 发送消息 | 推送日报 | 更新信息源 | 修改技能/记忆/配置 | 执行命令 |
|------|:----:|:--------:|:--------:|:----------:|:------------------:|:--------:|
| **admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **trusted** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **普通用户** (无角色) | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ (只读命令) |
| **blacklisted** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

### 角色说明

- **admin** — 完全放行，绕过所有限制。向后兼容旧 `whitelist` 配置。
- **trusted** — 可通过 source-evolution 技能更新信息源（添加/删除/进化 RSS、媒体、社交账号等），保留 skills 工具集。禁止修改记忆、配置、cron 任务、文件系统。
- **普通用户** — 只能问答、接收日报、通过 submit_approval 提交审批请求。
- **blacklisted** — 完全拒绝，连问答都不允许。

## 配置格式

在 `config.yaml` 的 `gateway.restricted_channels` 中配置：

```yaml
gateway:
  restricted_channels:
    oc_6ed1cc645057da3bbe93c6120219a61e:   # 飞书群 chat_id
      users:
        - id: ou_d366ba075912a3865430a7fe7020454b
          role: admin
        - id: ou_aaa111bbb222ccc333ddd444eee555f
          role: trusted
      blacklist:
        - ou_zzz999yyy888xxx777www666vvv555u
```

### 向后兼容

旧的 `whitelist` 格式仍然支持，自动映射为 `role: admin`：

```yaml
# 旧格式（仍然有效）
restricted_channels:
  oc_xxx:
    whitelist:
      - ou_aaa   # 等价于 role: admin
    blacklist: []

# 新格式（推荐）
restricted_channels:
  oc_xxx:
    users:
      - id: ou_aaa
        role: admin
    blacklist: []
```

如果 `users` 和 `whitelist` 同时存在，`users` 优先；`whitelist` 中的用户仅在其不在 `users` 列表时才生效（自动分配 admin 角色）。

## 三道防线

权限控制通过三层防御实现，每层独立检查：

### 防线1: 命令拦截 (`gateway/run.py`)

**位置**: `_handle_message()` 方法入口处

**逻辑**:
- admin 用户 → 放行所有命令
- blacklisted 用户 → 直接返回拒绝消息
- trusted 用户 → 放行所有命令
- 普通用户 → 只允许只读命令（`/help`, `/commands`, `/status`），其他命令被拦截

### 防线2: 工具集过滤 (`gateway/run.py`)

**位置**: `_build_agent_kwargs()` 方法，构建 AIAgent 参数时

**逻辑**:
- admin 用户 → 保留全部 toolsets
- blacklisted 用户 → 清空所有 toolsets
- trusted 用户 → 保留 `skills` toolset（用于 source-evolution），移除 `memory`/`cronjob`/`file`，添加 `approval`
- 普通用户 → 移除 `skills`/`memory`/`cronjob`/`file`，添加 `approval`

**trusted 用户保留的 skills 工具集**使得 agent 可以调用 source-evolution 技能来管理信息源。

### 防线3: 系统提示词 (`gateway/session.py`)

**位置**: `build_session_context_prompt()` 函数

**逻辑**:
- admin 用户 → 不注入额外限制提示
- blacklisted 用户 → 注入 "BLOCKED USER" 提示，要求 agent 拒绝所有请求
- trusted 用户 → 注入 "Trusted User Mode" 提示，明确允许/禁止的操作列表
- 普通用户 → 注入 "Read-Only Agent Mode" 提示，明确只能问答

**trusted 用户提示允许的操作**:
- 接收和处理数据
- 提供分析、摘要、评估和回答
- 执行只读计算代码
- 搜索网页、浏览页面、读取文件
- **更新信息源**（通过 source-evolution 技能添加/删除/进化信息源）
- 使用技能进行信息源管理
- 通过 submit_approval 提交变更请求

**trusted 用户提示禁止的操作**:
- 修改记忆 (memory: add/replace/remove)
- 修改配置 (config.yaml)
- 创建/修改/删除 cron 任务
- 写入/修补文件
- 安装包或修改环境
- 修改技能 (skill_manage) — 信息源更新除外

## 群消息中的用户识别

### 如何获取群 ID 和用户 ID

飞书群消息到达时，`FeishuAdapter._process_inbound_message()` 自动构建 `SessionSource` 对象，包含完整的群和用户信息：

```python
# gateway/platforms/feishu.py:2519-2527
source = self.build_source(
    chat_id=chat_id,                    # 群 ID (oc_ 开头)
    chat_name=chat_info.get("name"),     # 群名称
    chat_type="group",                   # 群聊类型标记
    user_id=sender_profile["user_id"],   # 发送者 open_id (ou_ 开头)
    user_name=sender_profile["user_name"], # 发送者显示名
)
```

### SessionSource 数据结构

```python
# gateway/session.py
@dataclass
class SessionSource:
    platform: Platform               # "feishu"
    chat_id: str                     # 群 ID: oc_6ed1cc...
    chat_name: Optional[str]         # 群名称: "AI日报群"
    chat_type: str                   # "dm" | "group" | "channel"
    user_id: Optional[str]           # 用户 ID: ou_d366ba...
    user_name: Optional[str]         # 用户显示名: "张三"
    thread_id: Optional[str]         # 话题/线索 ID
    chat_topic: Optional[str]        # 频道描述
    user_id_alt: Optional[str]       # 备用用户 ID (Signal UUID)
    chat_id_alt: Optional[str]       # 备用群 ID
    is_bot: bool                     # 是否为 bot 消息
```

### 回复中 @提问者

群消息回复时，`base.py` 自动在 metadata 中注入提问者信息：

```python
# gateway/platforms/base.py:1815-1822
if event.source.chat_type != "dm" and event.source.user_id:
    _thread_metadata["reply_to_user_id"] = event.source.user_id
    if event.source.user_name:
        _thread_metadata["reply_to_user_name"] = event.source.user_name
```

飞书适配器在发送回复时使用这些信息：

1. **引用回复**: 通过 `im.v1.message.reply` API 的 `reply_to` 参数，回复自动引用原消息
2. **@提问者**: 在富文本 post 中注入 `<at user_id="ou_xxx">` 标签

```python
# gateway/platforms/feishu.py:1439-1449
at_user_id = (metadata or {}).get("reply_to_user_id")
at_user_name = (metadata or {}).get("reply_to_user_name")

if at_user_id and msg_type == "post" and reply_to:
    payload = self._inject_at_mention(payload, at_user_id, at_user_name)
```

### 如何查找飞书用户 ID

要给 config.yaml 添加用户，需要知道其 `ou_` 开头的 open_id：

1. **从 gateway 日志获取**: 发送一条消息后查看日志
   ```bash
   journalctl -u hermes-gateway -n 50 | grep "Inbound.*message"
   ```
   日志会显示 `chat_id=oc_xxx` 和用户信息

2. **从飞书管理后台**: 组织管理 → 成员管理 → 查看成员详情中的 open_id

3. **从 SessionSource 的 to_dict()**: 如果启用了 session 存储，source 信息会持久化

## 信息源更新机制

### source-evolution 技能

trusted 用户可以通过 `source-evolution` 技能更新信息源：

**技能位置**: `~/.hermes/skills/research/source-evolution/`

**支持的信息源类型**:
- RSS/Atom feeds
- 新闻/媒体网站
- 微信公众号
- Twitter/X 账号
- 微博账号
- 知乎话题/用户
- GitHub 仓库/用户
- API 端点
- Substack/YouTube/Reddit 等

**核心功能**:
- 从用户分享的链接自动发现新信息源
- 评估信息源质量 (S/A/B/C/D Tier 评级)
- 持续监控和进化信息源
- 从文章内容和评论中提取新源

### 普通用户的替代路径

普通用户在受限频道中无法直接更新信息源，但可以通过 `submit_approval` 工具提交变更请求：

1. 用户在群中请求添加信息源
2. Agent 通过 submit_approval 提交到审批队列
3. 管理员在私聊中审批/拒绝
4. 审批通过后变更生效

## 变更历史

| 版本 | 日期 | 改动 |
|------|------|------|
| v1 | 2026-04-22 | 初始实现：受限频道三道防线 + whitelist/blacklist |
| v2 | 2026-04-24 | 新增 trusted 角色，users 列表格式，信息源更新权限 |

## 相关文件

| 文件 | 改动内容 |
|------|---------|
| `gateway/run.py` | 防线1 (命令拦截) + 防线2 (toolset 过滤) — 支持 admin/trusted/普通/blacklist 四级权限 |
| `gateway/session.py` | 防线3 (系统提示词) — 按角色注入不同的权限提示 |
| `gateway/platforms/base.py` | 群消息 metadata 注入 reply_to_user_id/user_name |
| `gateway/platforms/feishu.py` | @提问者 (_inject_at_mention) + reply_to_user_id 传递 + FEISHU_GROUP_REQUIRE_MENTION 环境变量 |
