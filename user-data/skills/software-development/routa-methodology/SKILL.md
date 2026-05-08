---
name: routa-methodology
version: 1.0.0
description: |
  Routa 多智能体协作方法论——从需求到交付的看板驱动协调框架。
  源自 phodal/routa 开源项目（730⭐, MIT），提炼其核心方法论为 Hermes 可执行技能。
  三大核心：Workspace-First 作用域 + Kanban Lane Specialist 逐级加严 + Feature Explorer 需求全景恢复。
triggers:
  - 多智能体协作
  - 看板驱动开发
  - 需求演化追踪
  - Feature Explorer
  - session 历史恢复
  - kanban lane specialist
  - workspace-first
  - routa
references:
  - phodal/routa: https://github.com/phodal/routa
  - ARCHITECTURE.md: https://github.com/phodal/routa/blob/main/docs/ARCHITECTURE.md
  - FEATURE_TREE.md: https://github.com/phodal/routa/blob/main/docs/product-specs/FEATURE_TREE.md
---

# Routa 多智能体协作方法论

## 一、核心问题

单 Agent 聊天适合孤立任务，但当同一线程需要同时做**分解、实现、审查、证据收集、发布决策**时就会崩溃。Routa 的解法：**让这些职责显式化**。

## 二、三大支柱

### 支柱 1：Workspace-First 作用域

工作区是顶层协调边界，不是隐藏的全局仓库状态。

```
Workspace（工作区）
  ├── Sessions（会话）
  ├── Tasks（任务）
  ├── Kanban Boards（看板）
  ├── Codebases（代码库）
  ├── Worktrees（工作树）
  ├── Notes（笔记/Spec）
  ├── Traces（追踪）
  └── Artifacts（制品）
```

**关键不变量**：新产品界面必须要求显式的工作区上下文，除非是刻意设计的引导流程。

### 支柱 2：Kanban Lane Specialist（逐级加严）

看板不是视觉状态投影，而是**驱动专业化提示词和证据契约的协调总线**。每个泳道由不同的 Specialist 负责，下游泳道比上游**更严格**。

```
Backlog → Todo → Dev → Review → Done
   ↓        ↓      ↓      ↓       ↓
 Refiner  Orch.  Crafter Guard  Reporter
                                    ↘
                                Blocked Resolver
```

**Lane 合约表**（代码级细节来自 `resources/specialists/workflows/kanban/*.yaml`）：

| Lane | Specialist | 提示词强制执行 | 写入卡片的制品 | 交接条件 |
|------|-----------|--------------|-------------|---------|
| Backlog | Backlog Refiner | 澄清范围，不编码，直到卡片包含恰好一个规范 YAML story 块 | 规范 YAML story（problem_statement + acceptance_criteria + constraints + dependencies + out_of_scope + INVEST 检查） | 仅当 story 解析通过且可独立执行时移至 Todo |
| Todo | Todo Orchestrator | 重新验证 Backlog 输出，拒绝模糊卡片，转为执行就绪简报 | Execution Plan + Key Files + Dependency Plan + Risk Notes | 仅当实现可在几分钟内开始时移至 Dev |
| Dev | Dev Executor | 重新检查卡片可执行性，仅实现范围内变更，运行验证，提交工作 | Dev Evidence（changed files + work summary + tests run + per-AC verification） | 仅当 commit 存在且 worktree 干净时移至 Review |
| Review | Review Guard | 独立验证每个验收标准，拒绝缺失证据/范围蔓延/脏 git 状态 | Review Findings（verdict + per-AC status + issues） | 仅当 APPROVED 时移至 Done |
| Done | Done Reporter | Done 是终态，留下完成记录 | Completion Summary（what shipped + key evidence） | 留在 Done |
| Blocked | Blocked Resolver | 分类阻塞，解释根因，仅在具体下一步时路由回去 | Blocker Analysis（type + root cause + resolution） | 路由回正确泳道 |

**卡片制品逐级增长**：同一张卡片随工作推进变得更严格——
- Backlog 产出规范 story YAML
- Todo 追加执行简报
- Dev 追加实现和验证证据
- Review 追加正式裁决和发现
- Done 追加完成摘要

### 支柱 3：Feature Explorer（需求全景恢复）

**核心洞察**：Agent 不应负责第一层上下文组织。系统应先按 feature 维度归并证据，再让 Agent 分析。

三层架构：
```
Layer 1: SPEC              → 定义起点（应该构建什么）
Layer 2: SESSION           → 记录过程（Agent 实际做了什么）
Layer 3: FEATURE EXPLORER  → 恢复全景（从 session 中重建 feature 地图）
```

Feature Explorer 的数据结构（来自 `docs/product-specs/FEATURE_TREE.md` 的 frontmatter）：

```yaml
feature_metadata:
  schema_version: 1
  capability_groups:              # 能力分组
    - id: workspace-coordination
    - id: agent-execution
    - id: kanban-automation
    - id: team-collaboration
    - id: governance-settings
  features:                       # Feature 定义
    - id: feature-explorer
      name: Feature Explorer
      group: workspace-coordination
      summary: 检查工作区 feature 表面和 session 支持的文件活动
      status: evolving            # shipped | evolving | planned
      pages:                      # 前端页面路由
        - /workspace/:workspaceId/feature-explorer
      apis:                       # API 端点
        - GET /api/feature-explorer
        - GET /api/feature-explorer/{featureId}
        - GET /api/feature-explorer/{featureId}/apis
        - GET /api/feature-explorer/{featureId}/files
      domain_objects:             # 领域对象
        - feature
        - session
        - workspace
      related_features:           # 关联 feature
        - session-recovery
      source_files:               # 源文件清单
        - crates/routa-server/src/api/feature_explorer.rs
        - src/app/api/feature-explorer/route.ts
```

## 三、三大核心角色（Specialist Prompts）

来自 `resources/specialists/core/{routa,crafter,gate}.yaml`：

### ROUTA Coordinator（协调者）
- **硬规则**：永远不直接编辑文件，永远不实现代码
- **工作流**：理解需求 → 写 Spec（@@@task 块）→ 等待批准 → 分波委派 → 验证
- **Spec 格式**：Goal + Tasks（@@@task 块）+ Acceptance Criteria + Non-goals + Assumptions + Verification Plan + Rollback Plan
- **@@@task 语法**：一个块一个任务，首行 # 标题，内容含 Scope/Inputs/Definition of Done/Verification

### CRAFTER Implementor（实现者）
- **硬规则**：无范围蔓延，无重构，协调冲突，完成后报告
- **执行流**：读 spec → 读 task note → 冲突预检 → 最小实现 → 运行验证 → 提交 → 更新 note
- **Git 纪律**：Author 必须是人类开发者，Agent 用 Co-authored-by 追加

### GATE Verifier（验证者）
- **硬规则**：验收标准是唯一检查清单，无证据不验证，无部分批准
- **验证流**：预检（验证对不对）→ 映射工作到标准 → 执行验证 → 边缘检查 → 提交作者检查
- **输出格式**：Verdict（✅/❌/⚠️）+ AC Checklist + Evidence Index + Tests Run + Risk Notes

## 四、Review Gate 架构

交付门是**堆叠决策路径**，不是单一审查者：

```
Harness Monitor（发生了什么）
  → 追踪 traces、changed files、commands、git state、attribution
Entrix Fitness（应该是什么）
  → 强制硬门、证据要求、文件预算/策略检查
Gate Specialist（能否移动）
  → 验证验收标准，路由到 Done/Dev/人工升级
```

## 五、协议栈

| 协议 | 端点 | 角色 |
|------|------|------|
| REST | `/api/*` | CRUD 和产品操作 |
| MCP | `/api/mcp`, `/api/mcp/tools` | 工具执行和协作 Agent 能力 |
| ACP | `/api/acp` | 生成、提示、流式、安装、预热、管理 Agent 运行时 |
| A2A | `/api/a2a/*` | Agent-to-Agent 互操作 |
| AG-UI | `/api/ag-ui` | UI 面 Agent 流协议 |
| A2UI | `/api/a2ui/*` | 面板 UI 协议 |
| SSE | ACP/notes/AG-UI | 增量更新到前端 |

## 六、Hermes 应用指南

### 场景 1：多 Agent 协作开发
使用 Kanban Lane Specialist 模式：
1. 将任务拆分为 @@@task 块
2. 按泳道委派：Backlog Refiner → Todo Orchestrator → Dev Executor → Review Guard
3. 每个泳道使用对应的提示词合约
4. 下游泳道不信任上游，独立验证

### 场景 2：需求演化追踪
使用 Feature Explorer 模式：
1. 在项目根目录维护 `FEATURE_TREE.md`（含 frontmatter metadata）
2. 每个 feature 记录：pages/apis/source_files/domain_objects/related_features
3. Session 结束后，按 feature 维度归并证据
4. 生成 `feature-tree.index.json` 供程序化查询

### 场景 3：代码审查门控
使用 Review Gate 模式：
1. Harness Monitor：收集 traces、changed files、git state
2. Fitness Check：验证硬门（测试通过、lint 干净、类型检查）
3. Gate Specialist：逐条验证验收标准，输出 ✅/❌/⚠️

## 七、关键设计模式

### 模式 1：Spec-Driven Recovery
Spec 作为先验约束恢复过程。无 Spec = 无监督聚类；有 Spec = 半监督匹配。

### 模式 2：Evidence Attribution
每个制品携带证据链：`session-XXX:action-YYY`，支持审计和纠正。

### 模式 3：Boundary Negotiation
Feature 边界不是硬墙，而是协商的：
- `includedPaths`：确定归属
- `excludedPaths`：确定不归属
- `sharedFiles`：重叠/共享——集成点

### 模式 4：Dual Representation
同一 feature 树存在两种形式：
- `FEATURE_TREE.md`：人类可读（开发者文档、onboarding、代码审查）
- `feature-tree.index.json`：机器可读（IDE 集成、自动化工具、API 查询）

### 模式 5：Provider Abstraction
不同 Agent CLI 和运行时通过适配器层归一化，不泄漏 provider 特定协议。

## 八、陷阱与注意事项

1. **不要跳泳道**：Backlog 未产出规范 YAML 就不进 Todo，Todo 未产出执行简报就不进 Dev
2. **不要信任上游**：每个 Specialist 独立验证，不假设上游输出正确
3. **不要部分批准**：Review Guard 要么全过，要么打回，没有"差不多"
4. **不要让 Agent 做第一层组织**：Feature Explorer 先归并证据，再让 Agent 分析
5. **不要用 "default" 作用域**：这是过渡脚手架，不是目标模型
6. **Git 纪律**：Author 必须是人类，Agent 只能 Co-authored-by

## 九、与 Hermes 技能的映射

| Routa 概念 | Hermes 对应 |
|-----------|------------|
| Workspace | 工作目录 + session context |
| Kanban Board | todo 工具 + task list |
| Specialist Prompts | skill 系统 |
| Feature Explorer | llm-wiki + knowledge-search-db |
| Session Trace | session_search |
| ACP/MCP | native-mcp skill |
| Review Gate | requesting-code-review skill |
| @@@task blocks | todo items |
