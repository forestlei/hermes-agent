# AI Agent Framework Complete Architecture Evaluation v2.0 (2026-05)

## What Changed from v1.0 → v2.0

v1.0 only covered 3 layers: Execution Platform + Collaboration Platform + Desktop Portal (87 projects).
User correction: "架构里缺乏网关层，还需要服务层，只有主题没有服务形同虚设，操作系统层里面的进化机制，oracle思维机制，规划机制，记忆机制都没有提及"

v2.0 adds 3 critical layers: Gateway + Services + OS Mechanisms (130+ projects total).

## 7-Layer Architecture

| Layer | Name | Solves | Key Projects |
|-------|------|--------|-------------|
| L7 | Desktop Portal | Human-Agent interaction | OpenRoom, ClawX, Core |
| L6 | Collaboration | Multi-agent coordination | A2A, Casdoor, Ultron |
| L5 | Services | Agent intelligence capabilities | Evolver, DeepResearch, Deer-Flow, Mem0 |
| L4 | Gateway | LLM API management | LiteLLM, TensorZero, ClawRouter |
| L3 | Execution | Safe agent execution | IronClaw, OpenFang, OpenSandbox |
| L2 | OS | Runtime mechanism primitives | Self-develop (16 primitives) |
| L1 | Infrastructure | Physical resource scheduling | Docker, K8s, vLLM |

## Service Layer — Four Core Mechanisms

### Evolution Engine
- **Projects**: EvoMap/evolver (7.2K⭐), lsdefine/GenericAgent (9.1K⭐), EvoAgentX/EvoAgentX (2.9K⭐)
- **Primitives**: mutate() / evaluate() / select() / inherit()
- **Gap**: inherit() cross-generation heredity — no project implements this

### Oracle/Thinking Engine
- **Projects**: SkyworkAI/DeepResearchAgent (3.4K⭐), griptape-ai/griptape (2.5K⭐), octotools/octotools (1.4K⭐)
- **Primitives**: perspective() / critique() / debate() / arbitrate()
- **Gap**: debate() + arbitrate() — no project implements full multi-perspective→debate→arbitration loop

### Planning Engine
- **Projects**: bytedance/deer-flow (64.9K⭐), microsoft/TaskWeaver (6.2K⭐), darrenhinde/OpenAgentsControl (3.9K⭐)
- **Primitives**: decompose() / schedule() / checkpoint() / rollback()
- **Gap**: rollback() checkpoint recovery — no project implements this

### Memory System
- **Projects**: mem0ai/mem0 (54.8K⭐), topoteretes/cognee (17K⭐), MemTensor/MemOS (8.9K⭐), MemoriLabs/Memori (14K⭐)
- **Primitives**: encode() / store() / retrieve() / decay()
- **Gap**: decay() automatic forgetting — no project implements this

## Gateway Layer — 19 Projects

### Tier 1 (Must-adopt)
- BerriAI/litellm (45.7K⭐, Python) — Full-featured LLM gateway, de facto standard
- tensorzero/tensorzero (11.3K⭐, Rust) — High-performance LLMOps platform
- BlockRunAI/ClawRouter (6.5K⭐, TypeScript) — Agent-native LLM router

### Tier 2 (Recommended)
- QuantumNous/new-api (30.6K⭐, Go) — Unified model hub
- maximhq/bifrost (4.6K⭐, Go) — 50x faster than LiteLLM
- higress-group/higress (8.3K⭐, Go) — Cloud-native AI gateway

### Tier 3 (Specialized)
- IBM/mcp-context-forge (3.7K⭐) — MCP/A2A protocol gateway
- katanemo/plano (6.4K⭐) — Agent data plane
- mnfst/manifest (6.1K⭐) — Cost-optimized routing

## Key Gaps (Self-Development Priorities)

| Priority | Gap | Rationale |
|----------|-----|-----------|
| P0 | OS layer mechanism primitives | Without primitives, upper services cannot be built |
| P0 | Oracle thinking loop | Core guarantee of agent decision quality |
| P1 | Memory decay mechanism | No decay = memory inflation = system crash |
| P1 | Experience sharing bus | Only channel for cross-instance knowledge transfer |
| P2 | Planning rollback mechanism | Necessary for long-task failure recovery |
| P2 | Evolution heredity mechanism | Efficiency guarantee for cross-generation experience transfer |

## Data Files
- `/root/.hermes/data/agent-framework/agent-framework-architecture-v2.md` — Full v2.0 architecture doc (28.8KB)
- `/root/.hermes/data/agent-framework/execution-platform-spec.md` — Execution platform spec
- `/root/.hermes/data/agent-framework/collaboration-platform-spec.md` — Collaboration platform spec
- `/root/.hermes/data/agent-framework/desktop-portal-spec.md` — Desktop portal spec
