# AI Agent 协作平台选型评估 (2026-05)

> 来源：用户指出执行平台分析遗漏了"协作平台"维度，补充定义6项需求后评估
> 关键洞察：协作平台 ≠ 执行平台，两者互补不可替代
> 维护：活文档，季度审查（下次：2026-08-05）

## 定位

协作平台是智能体框架的**多实例协调层**，位于执行平台之上：
- 执行平台解决"单个Agent如何安全执行"（沙箱、权限、隔离）
- 协作平台解决"多个Agent如何协同工作"（通信、共享、编排）

```
┌─────────────────────────────────────────┐
│          协作平台 (Collaboration)         │
│  通信协议 / 经验共享 / 团队管理 / 控制台    │
├─────────────────────────────────────────┤
│          执行平台 (Execution)             │
│  安全沙箱 / 权限管理 / 数据隔离 / 自动执行  │
├─────────────────────────────────────────┤
│          操作系统 (OS)                    │
└─────────────────────────────────────────┘
```

## 需求规格（6项指标）

### 2.1 通信协议（Communication Protocol）
| 需求项 | 验收标准 |
|--------|----------|
| Agent间通信 | 消息延迟 < 100ms |
| 协议标准化 | 至少支持1种标准协议（A2A/ANP/MCP） |
| 异步通信 | 消息不丢失 |
| 广播/组播 | 广播延迟 < 200ms |

### 2.2 经验共享（Experience Sharing）
| 需求项 | 验收标准 |
|--------|----------|
| 经验序列化 | 格式可跨实例解析 |
| 共享存储 | 读写延迟 < 50ms |
| 技能共享 | 技能加载 < 5s |
| 经验检索 | Top-5召回率 > 80% |

### 2.3 团队编排（Team Orchestration）
| 需求项 | 验收标准 |
|--------|----------|
| 角色分配 | 角色定义可配置 |
| 任务分解 | DAG依赖管理 |
| 结果聚合 | 聚合策略可配置 |
| 冲突解决 | 冲突检测率 > 95% |

### 2.4 身份与权限（Identity & Access）
| 需求项 | 验收标准 |
|--------|----------|
| Agent身份 | 身份不可伪造 |
| 访问控制 | 未授权访问 100% 拦截 |
| 审计追踪 | 日志完整可回溯 |
| 凭证管理 | 凭证不暴露给Agent |

### 2.5 管理控制台（Management Console）
| 需求项 | 验收标准 |
|--------|----------|
| 实例管理 | 操作响应 < 1s |
| 状态可视化 | 刷新延迟 < 2s |
| 成本追踪 | 成本统计准确率 > 99% |
| 配置管理 | 配置变更 < 5s生效 |

### 2.6 灵活部署（Flexible Deployment）
| 需求项 | 验收标准 |
|--------|----------|
| 自托管 | Docker/K8s一键部署 |
| 弹性伸缩 | 扩容响应 < 30s |
| 混合部署 | 跨网络通信稳定 |
| 多租户 | 租户间数据零泄露 |

## 候选项目评估

### 通信协议层
| 项目 | ⭐ | 语言 | 定位 | 协作适配度 |
|------|-----|------|------|-----------|
| a2aproject/A2A | 23,586 | Shell | Google主导的Agent间通信开放协议 | ⭐⭐⭐⭐⭐ |
| agent-network-protocol/AgentNetworkProtocol | 1,285 | HTML | Agent网络开放协议（去中心化身份） | ⭐⭐⭐⭐ |
| SolaceLabs/solace-agent-mesh | 3,409 | Python | 事件驱动的Agent网格框架 | ⭐⭐⭐⭐ |
| win4r/openclaw-a2a-gateway | 481 | TypeScript | OpenClaw的A2A协议网关 | ⭐⭐⭐ |

### 编排协作平台
| 项目 | ⭐ | 语言 | 定位 | 协作适配度 |
|------|-----|------|------|-----------|
| ruvnet/ruflo | 41,498 | TypeScript | Claude Agent编排平台 | ⭐⭐⭐⭐ |
| Yeachan-Heo/oh-my-claudecode | 32,514 | TypeScript | Teams-first多Agent编排 | ⭐⭐⭐⭐ |
| agno-agi/agno | 39,908 | Python | 生产级Agent运行平台 | ⭐⭐⭐⭐ |
| langchain-ai/langgraph | 31,186 | Python | 图结构Agent编排框架 | ⭐⭐⭐⭐ |
| VRSEN/agency-swarm | 4,253 | Python | 可靠的多Agent编排框架 | ⭐⭐⭐⭐ |
| builderz-labs/mission-control | 4,603 | TypeScript | 自托管Agent编排仪表盘 | ⭐⭐⭐⭐ |
| AgentsMesh/AgentsMesh | 1,923 | Go | AI Agent劳动力平台 | ⭐⭐⭐⭐ |
| openonion/connectonion | 990 | Python | Agent协作框架 | ⭐⭐⭐ |
| uluckyXH/OpenMOSS | 1,250 | Python | 多Agent自主运行的AI公司OS | ⭐⭐⭐ |

### 管理控制台
| 项目 | ⭐ | 语言 | 定位 | 协作适配度 |
|------|-----|------|------|-----------|
| CherryHQ/cherry-studio | 45,007 | TypeScript | AI生产力工作室 | ⭐⭐⭐ |
| abhi1693/openclaw-mission-control | 3,902 | TypeScript | OpenClaw编排仪表盘 | ⭐⭐⭐⭐ |
| EKKOLearnAI/hermes-web-ui | 3,523 | TypeScript | Hermes Web管理界面 | ⭐⭐⭐⭐ |
| grp06/openclaw-studio | 2,007 | TypeScript | OpenClaw Web仪表盘 | ⭐⭐⭐ |
| xaspx/hermes-control-interface | 574 | JavaScript | Hermes自托管控制台 | ⭐⭐⭐ |

### 身份权限
| 项目 | ⭐ | 语言 | 定位 | 协作适配度 |
|------|-----|------|------|-----------|
| casdoor/casdoor | 13,548 | Go | Agent-first IAM/MCP网关 | ⭐⭐⭐⭐⭐ |

### 经验共享
| 项目 | ⭐ | 语言 | 定位 | 协作适配度 |
|------|-----|------|------|-----------|
| letta-ai/agent-file | 1,144 | TypeScript | Agent状态序列化标准格式 | ⭐⭐⭐⭐ |
| modelscope/ultron | 100 | Python | 集体智能-共享记忆/技能 | ⭐⭐⭐⭐⭐ |

### Agent OS（全栈平台）
| 项目 | ⭐ | 语言 | 定位 | 协作适配度 |
|------|-----|------|------|-----------|
| Coral-Protocol/coral-server | 218 | Kotlin | AI Agent的Kubernetes | ⭐⭐⭐⭐ |

## 推荐短名单

### Tier 1 — 核心协作组件（必须）
| 组件 | 推荐项目 | ⭐ | 理由 |
|------|----------|-----|------|
| 通信协议 | A2A (a2aproject/A2A) | 23,586 | Google主导开放标准，生态最广 |
| 身份权限 | Casdoor (casdoor/casdoor) | 13,548 | Agent-first IAM，MCP/A2A/OAuth2/OIDC全支持 |
| 经验共享 | Ultron (modelscope/ultron) | 100 | 唯一专注"集体智能+共享记忆+技能进化"的项目 |

### Tier 2 — 编排协作平台（推荐）
| 项目 | ⭐ | 语言 | 理由 |
|------|-----|------|------|
| Mission Control (builderz-labs) | 4,603 | TS | 自托管、舰队管理、任务调度、成本追踪 |
| AgentsMesh | 1,923 | Go | Agent劳动力平台、团队协作、Docker部署 |
| Solace Agent Mesh | 3,409 | Python | 事件驱动、Agent网格、异步通信 |

### Tier 3 — 管理控制台（可选）
| 项目 | ⭐ | 语言 | 理由 |
|------|-----|------|------|
| Hermes Web UI | 3,523 | TS | Hermes原生管理界面 |
| OpenClaw Mission Control | 3,902 | TS | OpenClaw编排仪表盘 |

### Tier 4 — 潜力项目（关注）
| 项目 | ⭐ | 语言 | 理由 |
|------|-----|------|------|
| CoralOS | 218 | Kotlin | "AI Agent的K8s"概念，早期 |
| OpenMOSS | 1,250 | Python | "AI公司OS"概念，自组织多Agent |
| Agent File | 1,144 | TS | Agent序列化标准，经验共享基础 |
| ANP | 1,285 | HTML | 去中心化Agent身份协议 |

## 推荐架构

```
┌──────────────────────────────────────────────────────┐
│                    协作平台架构                        │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Mission  │  │ Agents   │  │ Solace   │           │
│  │ Control  │  │ Mesh     │  │ Agent    │           │
│  │ (编排)    │  │ (劳动力)  │  │ Mesh     │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │              │              │                 │
│  ┌────┴──────────────┴──────────────┴─────┐          │
│  │           A2A Protocol (通信)           │          │
│  └────┬──────────────┬──────────────┬─────┘          │
│       │              │              │                 │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐          │
│  │ Casdoor  │  │ Ultron   │  │ Agent    │           │
│  │ (IAM)    │  │ (经验共享) │  │ File     │           │
│  └──────────┘  └──────────┘  └──────────┘          │
│                                                      │
│  ┌──────────────────────────────────────────┐        │
│  │        执行平台 (IronClaw/NullClaw)       │        │
│  └──────────────────────────────────────────┘        │
└──────────────────────────────────────────────────────┘
```

## 关键发现

### 经验共享是最大缺口
- 当前开源生态中，几乎没有项目专门解决Agent经验共享问题
- Ultron（modelscope/ultron）是唯一专注"集体智能+共享记忆"的项目，但仅100⭐
- Agent File（letta-ai/agent-file）解决了Agent序列化，但未解决跨实例经验传递
- **这是自研的重点方向**

### 通信协议已标准化
- A2A（Google）已成为事实标准，23K+⭐
- ANP提供去中心化身份方案，1.2K⭐
- OpenClaw已有A2A网关（win4r/openclaw-a2a-gateway）

### 管理控制台生态丰富
- Hermes和OpenClaw各有多个Web UI项目
- Mission Control是功能最全的自托管方案

## 产出文件

- `~/.hermes/data/agent-framework/collaboration-platform-spec.md` — 协作平台需求规格（6项指标+评估+架构图+维护策略）

## 知识库注册状态

已注册到以下持久化系统：
- `agent-framework/metadata.json` → `collaboration-platform` 子项目（含tier1-4项目列表、数据文件引用、更新策略）
- `github-memory/智能体项目/_topic.yaml` → 15个协作平台项目（从26→41个）
- `github-memory/_index.yaml` → 15个新repo（从63→78个）
- `github-memory/_index.md` → 15行新增（从160→175总项目）
- 每个新项目的 `metadata.json` 已创建（含tier、feature_tags、来源标注、category分类）
