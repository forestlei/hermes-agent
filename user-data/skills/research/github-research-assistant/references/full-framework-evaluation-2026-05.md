# AI Agent 框架完整选型评估（跨子专题合并）

> 日期: 2026-05-05 | 3个子专题合并 | 87个项目

## 评估模式

当用户要求"智能体框架"选型时，这不是单一维度的评估，而是多子专题的系统性评估。每个子专题有独立的需求规格和评估打分卡，但最终交付物必须是一份合并的完整文档。

### 子专题清单（agent-framework）

| 子专题 | 需求指标数 | 项目数 | 核心关注 |
|--------|-----------|--------|---------|
| 执行平台 | 7项硬性 | 38 | 安全沙箱/权限/隔离/自动执行 |
| 协作平台 | 6项核心 | 22 | 通信协议/经验共享/团队编排 |
| 桌面总入口 | 7项硬性 | 27 | 统一入口/个人模式/Agent路由 |

### 合并交付物结构

```
1. 框架全景架构图（所有层）
2. 执行平台 — 项目清单（按分类）
3. 协作平台 — 项目清单（按分类）
4. 桌面总入口 — 项目清单（按分类）
5. 全框架推荐短名单（按架构层级汇总 + 按优先级汇总）
6. 淘汰项目汇总（跨子专题）
7. 关键发现与缺口（跨子专题共性缺口分析）
8. 持续维护策略
```

### 跨子专题共性缺口（2026-05发现）

| 缺口 | 影响子专题 | 严重度 |
|------|-----------|--------|
| 经验共享 | 执行+协作+桌面 | 🔴最高 |
| 团队助理 | 协作+桌面 | 🟠高 |
| Agent路由 | 桌面 | 🟡中 |
| 个人助理闭环 | 桌面 | 🟡中 |

### 全框架核心推荐（11个P0/P1项目）

| 层级 | 组件 | 项目 | ⭐ |
|------|------|------|-----|
| 桌面 | Web内核 | MiniMax-AI/OpenRoom | 1,160 |
| 桌面 | 桌面App | ValueCell-ai/ClawX | 7,041 |
| 桌面 | 助理逻辑 | RedPlanetHQ/core | 1,509 |
| 协作 | 通信协议 | a2aproject/A2A | 23,586 |
| 协作 | 身份权限 | casdoor/casdoor | 13,548 |
| 协作 | 经验共享 | modelscope/ultron | 100 |
| 协作 | 编排调度 | builderz-labs/mission-control | 4,604 |
| 执行 | 主力平台 | nearai/ironclaw | 12,126 |
| 执行 | 通用OS | RightNow-AI/openfang | 17,139 |
| 执行 | 生产沙箱 | alibaba/OpenSandbox | 10,424 |
| 执行 | 边缘轻量 | nullclaw/nullclaw | 7,398 |

### 数据文件索引

| 文件 | 说明 |
|------|------|
| `data/agent-framework/agent-framework-full-catalog.md` | 完整合并文档（主交付物） |
| `data/agent-framework/execution-platform-spec.md` | 执行平台需求规格 |
| `data/agent-framework/collaboration-platform-spec.md` | 协作平台需求规格+选型 |
| `data/agent-framework/desktop-portal-spec.md` | 桌面总入口需求规格 |
| `data/agent-framework/desktop-portal-catalog.md` | 桌面总入口项目清单 |
| `data/agent-framework/awesome-claw-hermes-cn.md` | 执行平台生态全景（中文） |
| `skills/data/topics/agent-framework/metadata.json` | 框架元数据（含所有子专题注册） |
