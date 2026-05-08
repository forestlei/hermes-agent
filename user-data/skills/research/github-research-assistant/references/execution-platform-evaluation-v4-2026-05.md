# AI Agent执行平台选型评估 v4.0

> 日期：2026-05-05 | 数据源：GitHub搜索(284项目) + awesome-agent-sandboxes(26项目) + 交叉验证

## 关键修正（v3.5→v4.0）

1. **搜索策略根本性重构**：从单一GitHub API关键词搜索 → 三源交叉验证（GitHub API + awesome列表 + 已有数据）
2. **awesome列表是权威起点**：awesome-agent-sandboxes(26项目)有14个项目GitHub搜索未覆盖，双源互补必要
3. **头条"高性能生态矩阵"验证**：全部不适合做执行平台——用Rust/Zig/Go重写Agent框架 ≠ 执行平台

## 执行平台4层架构

```
L4 经验共享层 — 跨实例知识沉淀与复用（P0自研，无开源方案）
L3 权限治理层 — 细粒度权限控制与审计
L2 编排调度层 — 多实例编排与任务调度
L1 安全执行层 — 沙箱隔离与资源控制（地基）
```

## 9大需求维度

| # | 需求 | 对应层 |
|---|------|--------|
| 1 | 安全隔离 | L1 |
| 2 | 可控性 | L1+L3 |
| 3 | 权限管理 | L3 |
| 4 | 防非法操作 | L1+L3 |
| 5 | 无审核自动执行 | L2+L3 |
| 6 | 多实例 | L2 |
| 7 | 数据隔离 | L1 |
| 8 | 经验共享 | L4 |
| 9 | 灵活部署 | L2 |

## 交叉验证方法论

### 三源合并流程
1. **GitHub API搜索**：12组关键词（sandbox/microvm/code execution/agent sandbox等），284个去重项目
2. **awesome列表**：awesome-agent-sandboxes(26项目) + awesome-sandbox，按Cloud/Self-hosted/Local分类
3. **已有数据**：v1.0-v3.5迭代积累的163个项目
4. **合并去重**：`full_name`为key，标注来源（github_search/awesome_only/github_search+awesome）

### 关键发现
- awesome-agent-sandboxes有14个项目GitHub搜索未覆盖（E2B/sandboxer/bouvet/microsandbox/sandboxai/daytona/fence/landrun/yolo-cage/volant/capsule/enclave/pctx/agentfence）
- **单一搜索策略必然遗漏**，双源互补必要
- GitHub API限流(60 req/hr)时，用web读取GitHub页面补充验证

## 安全执行层综合评分（Top 14）

评分：Star(55% log归一化) + 技术适配(45% 6维评分)

| # | 综合 | ⭐ | 项目 | 隔离级别 | 语言 | 定位 |
|---|------|-----|------|---------|------|------|
| 1 | 95.0 | 72,381 | daytonaio/daytona | 容器级 | Go | 开发环境平台(AGPL-3.0) |
| 2 | 86.3 | 34,128 | firecracker-microvm/firecracker | VM级 | Rust | AWS MicroVM最底层原语 |
| 3 | 83.7 | 12,056 | e2b-dev/e2b | VM级 | TS | 云端沙箱即服务 |
| 4 | 83.0 | 10,432 | alibaba/OpenSandbox | 多层 | Python | AI Agent专用多层隔离 |
| 5 | 80.5 | 10,576 | WasmEdge/WasmEdge | WASM级 | C++ | 轻量WASM运行时 |
| 6 | 80.2 | 5,950 | superradcompany/microsandbox | VM级 | Rust | Rust MicroVM<200ms启动 |
| 7 | 79.4 | 5,015 | TencentCloud/CubeSandbox | KVM+eBPF | Rust | 腾讯云双层隔离 |
| 8 | 77.8 | 28,062 | ComposioHQ/composio | 应用级 | TS | 工具集成平台 |
| 9 | 76.6 | 7,909 | wasm3/wasm3 | WASM级 | C | 极快WASM解释器 |
| 10 | 75.0 | 15,646 | trycua/cua | 容器级 | HTML | Computer Use Agent |
| 11 | 74.9 | 2,035 | kubernetes-sigs/agent-sandbox | 可插拔 | Go | K8s原生Agent沙箱 |
| 12 | 74.1 | 7,863 | kata-containers/kata-containers | VM级 | Rust | CNCF容器+VM融合 |
| 13 | 73.5 | 4,235 | hyperlight-dev/hyperlight | VM级 | Rust | 微软极轻VMM |
| 14 | 71.5 | 2,774 | rivet-dev/agent-os | 进程级 | Rust | Agent OS概念 |

## 隔离级别对比

```
隔离强度 ←—————————————————————————————→ 轻量灵活
VM级 → 容器级 → WASM级 → 进程级
Firecracker/E2B/MicroSandbox/CubeSandbox/Kata/Hyperlight
Daytona/CUA/K8s-Agent-Sandbox/Composio
WasmEdge/wasm3
agent-os
```

## 推荐短名单

### 安全执行层 Top 5
| 优先级 | 项目 | ⭐ | 理由 | 注意 |
|--------|------|-----|------|------|
| 🥇 P0 | OpenSandbox | 10,432 | AI Agent专用多层隔离 | 社区活跃度需观察 |
| 🥈 P0 | MicroSandbox | 5,950 | Rust VM级<200ms | 生态待成熟 |
| 🥉 P1 | Firecracker | 34,128 | 最成熟VM隔离 | 需上层编排 |
| P1 | K8s Agent-Sandbox | 2,035 | CNCF可插拔gVisor/Kata | 依赖K8s |
| P2 | WasmEdge | 10,576 | WASM轻量嵌入 | 隔离弱于VM |

### 编排调度层 Top 2
| 优先级 | 项目 | ⭐ | 理由 |
|--------|------|-----|------|
| P0 | agent-os | 2,774 | Rust Agent OS |
| P1 | K8s Agent-Sandbox | 2,035 | K8s原生编排 |

### 权限治理层 Top 2
| 优先级 | 项目 | ⭐ | 理由 |
|--------|------|-----|------|
| P1 | KubeArmor | 2,090 | K8s运行时安全策略 |
| P2 | OPA/Gatekeeper | — | 通用策略引擎 |

### 经验共享层
**P0自研**，无开源替代。需实现：inherit遗传/debate辩论/arbitrate裁决/rollback回滚/decay遗忘

## 头条"高性能生态矩阵"验证

| 项目 | 声称归属 | 实际 | 结论 |
|------|---------|------|------|
| nullclaw/nullclaw | OpenClaw(Zig) | 独立项目 | ⚠️ 生态归属造假 |
| eikarna/hermes-rs | Hermes(Rust) | 与Hermes Agent无关 | ⚠️ 生态归属造假 |
| dclause/hermes-five | Hermes(Rust) | IoT项目 | ⚠️ 生态归属造假 |
| rust-hermes/rusty_hermes | Hermes(Rust) | Meta JS引擎封装 | ⚠️ 生态归属造假 |
| Harsh-2909/hermes-go | Hermes(Go) | 独立AI框架 | ⚠️ 生态归属造假 |

**核心逻辑错误**：用底层语言重写Agent框架 ≠ 执行平台，不增加沙箱/隔离/权限能力

## Daytona不推荐原因
72K⭐排名第一但：AGPL-3.0限制商业 + 定位是开发环境非Agent执行平台 + 重量级

## 推荐技术栈
```
L4 经验共享层    【P0自研】
L3 权限治理层    KubeArmor + OPA + 自研预授权机制
L2 编排调度层    agent-os (rivet-dev)
L1 安全执行层    OpenSandbox(主力) + Firecracker(高安全) + WasmEdge(轻量嵌入)
```

## 选型决策树
```
需要最强隔离？ → Firecracker/MicroSandbox (VM级)
否 → K8s环境？ → K8s Agent-Sandbox (gVisor/Kata可插拔)
    否 → 需要极轻量？ → WasmEdge/wasm3 (WASM级)
        否 → OpenSandbox (默认推荐)
```
