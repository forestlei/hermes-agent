# Agent间直接通讯开源项目全景

> 调研时间：2026-05-01 | 共42项目（36通用 + 6 Hermes-specific）

## 一、A2A (Agent-to-Agent) 协议核心项目

| # | 项目名称 | ⭐ | 语言 | 描述 | 通讯机制类型 |
|---|---------|--------|------|------|-------------|
| 1 | a2aproject/A2A | 23,527 | Shell | Google 官方 Agent2Agent 开放协议 | A2A协议 (HTTP/JSON-RPC) |
| 2 | themanojdesai/python-a2a | 986 | Python | A2A 协议 Python 实现库 | A2A协议实现 |
| 3 | vishalmysore/a2ajava | 102 | Java | A2A 协议纯 Java 实现 + MCP桥接 | A2A协议实现 + MCP桥接 |
| 4 | imfangs/a2a4j | 8 | Java | A2A 协议 Java 实现 | A2A协议实现 |
| 5 | thestupd/nestjs-a2a | 16 | TypeScript | NestJS 框架的 A2A 协议实现 | A2A协议实现 |

## 二、A2A 生态集成与工具项目

| # | 项目名称 | ⭐ | 语言 | 描述 | 通讯机制类型 |
|---|---------|--------|------|------|-------------|
| 6 | johnson7788/MultiAgentPPT | 1,589 | Python | A2A + MCP + ADK 智能PPT生成 | A2A+MCP多Agent协作 |
| 7 | google-agentic-commerce/a2a-x402 | 498 | Python | A2A x402 加密货币支付扩展 | A2A + 加密支付 |
| 8 | win4r/openclaw-a2a-gateway | 472 | TypeScript | OpenClaw A2A 双向Agent通信网关 | A2A网关/双向通信 |
| 9 | elkar-ai/elkar-a2a | 149 | TypeScript | A2A Agent任务管理系统 | A2A任务管理 |
| 10 | GongRzhe/A2A-MCP-Server | 148 | Python | MCP-A2A 桥接服务器 | MCP↔A2A桥接 |
| 11 | dabit3/a2a-x402-typescript | 102 | TypeScript | A2A x402 支付协议 TS实现 | A2A + 加密支付 |
| 12 | chongdashu/adk-mcp-a2a-crash-course | 52 | Python | ADK + A2A + MCP 多Agent演示 | A2A+MCP+ADK集成 |
| 13 | pjawz/n8n-nodes-agent2agent | 46 | TypeScript | n8n 工作流 A2A 协议节点 | A2A工作流集成 |
| 14 | ruska-ai/a2a-langgraph | 27 | Python | 基于 LangGraph 的 A2A 协议实现 | A2A + LangGraph |
| 15 | cybertheory/AutonomousSphere | 16 | Python | Agent协作服务器，联邦式网络 | A2A联邦网络 |

## 三、MCP 相关 Agent 通讯项目

| # | 项目名称 | ⭐ | 语言 | 描述 | 通讯机制类型 |
|---|---------|--------|------|------|-------------|
| 16 | Coral-Protocol/Anemoi | 372 | Python | 半中心化多Agent MCP服务器 | MCP服务器 + Agent间通信 |
| 17 | gilbarbara/agent-hub-mcp | 27 | TypeScript | MCP 多Agent通信与协调 | MCP Hub/协调中心 |
| 18 | stoops-io/stoops-cli | 26 | TypeScript | AI Agent 实时通信聊天服务器 | 实时聊天服务器 |
| 19 | GongRzhe/ACP-MCP-Server | 22 | Python | ACP 与 MCP 桥接服务器 | ACP↔MCP桥接 |
| 20 | howardpen9/tmux-bridge-mcp | 15 | TypeScript | tmux 跨窗格 Agent 通信 | MCP跨Agent通信桥 |
| 21 | theo-nash/claude-slack | 8 | Python | 类 Slack 协议Agent间通信 | MCP + 类Slack消息协议 |
| 22 | fkesheh/mcp-agent-server | 7 | TypeScript | MCP 中心枢纽 | MCP跨生态通信 |
| 23 | agentralabs/agentic-comm | 4 | Rust | 结构化Agent通信（频道/Pub-Sub/路由）| MCP + Pub/Sub + 频道路由 |

## 四、Agent P2P / Mesh 网络项目

| # | 项目名称 | ⭐ | 语言 | 描述 | 通讯机制类型 |
|---|---------|--------|------|------|-------------|
| 24 | qualixar/slm-mesh | 16 | TypeScript | AI编码Agent P2P 通信网络 | P2P Mesh + MCP |
| 25 | GlobalAgents-Hub/GA2A | 3 | Python | 去中心化 P2P Agent通信协议 | P2P去中心化 (类BitTorrent) |
| 26 | a2al/A2AL | 0 | Go | 去中心化Agent网络协议 | P2P + 加密 + 身份认证 |
| 27 | Ankhlan/rshtex | 0 | Python | Agent间通信协议 Ed25519+P2P | P2P TCP Mesh + 加密身份 |
| 28 | marcochen2023/openclaw-p2p-mesh | 0 | HTML | OpenClaw P2P 通信网络 | P2P去中心化 |

## 五、独立 Agent 通讯协议/框架

| # | 项目名称 | ⭐ | 语言 | 描述 | 通讯机制类型 |
|---|---------|--------|------|------|-------------|
| 29 | TeoSlayer/pilotprotocol | 82 | Go | Pilot Protocol: Agent 互联网协议 | 独立Agent网络协议 |
| 30 | labsai/EDDI | 331 | Java | 配置驱动AI Agent引擎 | MCP + A2A + 多Agent编排 |
| 31 | viche-ai/viche | 23 | Elixir | Agent间发现与通信协议 | Agent发现+通信协议 |
| 32 | YouAM-Network/uam | 20 | Python | 通用Agent消息协议（加密）| 加密Agent消息协议 |
| 33 | isekOS/awesome-a2a-agents | 23 | - | A2A 生态工具/框架精选列表 | 资源索引 |
| 34 | amtp-protocol/amtp | 13 | - | Agent消息传输协议（联邦式）| 联邦式消息传输协议 |
| 35 | adriannoes/asap-protocol | 13 | Python | 标准化Agent通信（有状态编排）| 有状态编排 + MCP兼容 |

## 六、Hermes Agent 通讯专项项目 ⚠️ 容易遗漏

> **搜索教训**：通用关键词搜索（agent communication/a2a）容易漏掉框架特定的通讯项目。
> 必须额外搜索 `{framework-name} + communication/bridge/relay/protocol` 组合。

| # | 项目名称 | ⭐ | 语言 | 描述 | 通讯机制类型 |
|---|---------|--------|------|------|-------------|
| 36 | codejunkie99/agentic-stack | 1,778 | Python | 可移植.agent/目录，跨Agent框架共享记忆+协议 | 便携式Agent身份+协议 |
| 37 | iamagenius00/hermes-a2a | 109 | Python | Hermes Agent A2A协议插件，零补丁session注入 | A2A插件 |
| 38 | workingclassbuddha/hermes-relay-for-chrome | 18 | TypeScript | Chrome浏览器Hermes Agent通信桥 | 浏览器→Agent通信 |
| 39 | 503496348-ops/feishu-multi-agent-relay | 8 | Python | 飞书多Hermes Bot跨实例@通讯 | 飞书群内多Agent通信 |
| 40 | dp-pcs/ogp | 15 | TypeScript | Open Gateway Protocol，加密P2P跨Agent网关 | 加密P2P联邦网关 |
| 41 | firstintent/a2a-bridge | 6 | TypeScript | 多Agent桥接（Claude/Codex/OpenClaw/Hermes/Gemini）| 多框架统一桥接 |
| 42 | zhugezihou/hermes-six-ministries | 2 | Python | Hermes Agent六部尚书多Agent通信系统 | A2A + 跨Agent协调 |

## 协议层关系图

```
┌─────────────────────────────────────────────┐
│           Application Layer                 │
│  MultiAgentPPT / EDDI / Lucid Agents        │
├─────────────────────────────────────────────┤
│        Protocol Bridge Layer                │
│  A2A-MCP-Server / ACP-MCP-Server / Hub     │
├──────────┬──────────┬───────────────────────┤
│  A2A     │   MCP    │  Independent Protos   │
│ Protocol │ Protocol │  (AMTP/UAM/Pilot/etc) │
├──────────┴──────────┴───────────────────────┤
│        Transport Layer                       │
│  HTTP/JSON-RPC │ P2P/TCP │ WebSocket │ gRPC │
└─────────────────────────────────────────────┘
```

## 选型建议

- **最大生态兼容** → A2A协议（唯一事实标准）
- **已有MCP工具链** → A2A-MCP-Server桥接
- **去中心化/无中心节点** → slm-mesh（极早期）
- **Hermes场景** → A2A最合适（Agent Card发现机制天然适配）
- **跨框架统一桥接** → firstintent/a2a-bridge 或 codejunkie99/agentic-stack
- **飞书群内多Hermes协作** → 503496348-ops/feishu-multi-agent-relay
