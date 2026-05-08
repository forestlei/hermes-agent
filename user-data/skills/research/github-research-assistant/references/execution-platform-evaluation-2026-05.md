# AI Agent 执行平台选型评估 v3.5 (2026-05)

> 版本: 3.5 | 基准日期: 2026-05-05 | 评分体系: 分层选型(按层独立评分)
> v3.5 核心变化：从"选一个全能项目"修正为"分层选型"，沙箱=安全执行层=执行平台地基
> 维护：活文档，季度审查（下次：2026-08-05）

## 评分体系演进

| 版本 | 方法 | 问题 |
|------|------|------|
| v1.0 | 加权7维度(安全25%+隔离20%+...) | 未验证项目真实性 |
| v3.2 | 7项硬性指标(P0×2加权)，纯技术排序 | capsule(281⭐)排#1，高star被低估 |
| v3.3 | 技术门槛(≥20/55) + Star(50%)+Tech(50%) | ✅ star是核心要素，但tech仅看沙箱 |
| v3.4 | 4域运行时定义 + Star(50%)+Tech(4域加权50%) | ✅ 执行平台≠沙箱，=4域运行时 |
| **v3.5** | **分层选型：4层独立评分+组合推荐** | ✅ 沙箱=安全执行层地基，不因缺编排被降级 |

### v3.5 核心修正：分层选型

**v3.4的错误**：用4域覆盖度要求单个项目，导致沙箱项目(capsule/SmolVM/greywall)因缺编排能力排名靠后。但沙箱就是安全执行层本身，是地基而非附属功能。

**正确做法**：执行平台=4层架构，按层选项目

```
┌─────────────────────────────────────┐
│  🎛️ 编排调度层                      │  多实例管理 + 灵活部署 + 自动执行
├─────────────────────────────────────┤
│  🔐 权限治理层                      │  权限管理 + 可控 + 审计
├─────────────────────────────────────┤
│  🛡️ 安全执行层（沙箱）              │  隔离执行 + 防非法操作 + 数据隔离
├─────────────────────────────────────┤
│  🧠 经验共享层                      │  跨实例经验传递 + 技能共享 + 学习沉淀
└─────────────────────────────────────┘
```

### v3.5 另一修正：搜索关键词遗漏

v3.4仅搜索"execution platform"+"agent"等角色级关键词，完全遗漏了沙箱领域的头部项目：
- **遗漏**：OpenSandbox(10,432⭐)、CubeSandbox(5,014⭐)、E2B(12,056⭐)、Daytona(72,381⭐)、Sandcastle(3,522⭐)
- **原因**：未搜索实现级关键词(sandbox/microvm/firecracker/wasm sandbox/code execution)
- **教训**：技术选型搜索必须同时覆盖角色级+实现级关键词

## 🛡️ 安全执行层（沙箱）— 按层独立评估

### Tier 1 — 强烈推荐（⭐≥5K 或 隔离技术领先）

| 项目 | ⭐ | 语言 | 隔离技术 | 数据隔离 | 防非法操作 | 冷启动 | 许可证 | 评分 |
|------|-----|------|---------|---------|-----------|--------|--------|------|
| **OpenSandbox** | 10,432 | Python | Docker→gVisor→Kata→Firecracker多层可选 | ✅多层 | ✅按层递增 | 可选 | Apache 2.0 | 10/10 |
| **E2B** | 12,056 | TS | Firecracker MicroVM | ✅硬件级 | ✅独立内核 | ~150ms | Apache 2.0 | 9/10 |
| **CubeSandbox** | 5,014 | Rust | KVM MicroVM + eBPF | ✅硬件级+网络级 | ✅独立内核+eBPF | ~60ms | Apache 2.0 | 9/10 |

**Tier 1 关键对比：**

| 维度 | OpenSandbox | E2B | CubeSandbox |
|------|------------|-----|-------------|
| 隔离强度 | 按需选择(Docker→microVM) | Firecracker microVM | KVM microVM + eBPF |
| K8s原生 | ✅ | ❌(自建) | ⚠️(需适配) |
| 多语言SDK | Python/Java/TS/C#/Go | TS/Python | TS(Python计划中) |
| MCP集成 | ✅ | ✅ | ✅(E2B兼容) |
| 商业友好 | ✅ Apache 2.0 | ✅ Apache 2.0 | ✅ Apache 2.0 |
| 出品方 | 阿里 | E2B公司 | 腾讯云 |
| 适合场景 | 企业级/多安全等级 | 快速集成/生态成熟 | 极致性能/云原生 |

### Tier 2 — 推荐

| 项目 | ⭐ | 语言 | 隔离技术 | 许可证 | 评分 |
|------|-----|------|---------|--------|------|
| **Daytona** | 72,381 | TS | OCI/Docker | ⚠️AGPL-3.0 | 7/10 |
| **Arrakis** | 808 | Rust | cloud-hypervisor MicroVM | Apache 2.0 | 8/10 |
| **SmolVM** | 505 | Rust | Firecracker MicroVM | MIT | 8/10 |

### Tier 3 — 备选

| 项目 | ⭐ | 隔离技术 | 评分 | 说明 |
|------|-----|---------|------|------|
| Judge0 | 4,151 | Docker+Isolate | 6/10 | 代码执行沙箱，非Agent沙箱 |
| Sandcastle | 3,522 | 依赖Provider | 5/10 | 编排框架，非沙箱本身 |
| capsule | 281 | WASM+WASI | 7/10 | WASM轻量级，适合可信代码 |
| greywall | 173 | Linux 5层内核栈 | 7/10 | 内核级，Linux专用 |
| dify-sandbox | 1,187 | Docker+seccomp | 6/10 | Dify专用，通用性弱 |
| hazmat | 107 | macOS Seatbelt | 6/10 | macOS专用 |

**安全执行层推荐：OpenSandbox + CubeSandbox 双引擎**

## 🎛️ 编排调度层

| 项目 | ⭐ | 多实例 | 灵活部署 | 自动执行 | 评分 |
|------|-----|--------|---------|---------|------|
| **agent-os** | 2,771 | ✅ | ✅ | ✅ | 9/10 |
| **moltis** | 2,648 | ✅ | ✅ | ✅ | 8/10 |
| **goclaw** | 3,014 | ✅多租户 | ✅ | ✅ | 8/10 |

**编排调度层推荐：agent-os**

## 🔐 权限治理层

| 项目 | ⭐ | 权限模型 | 可控性 | 审计 | 评分 |
|------|-----|---------|--------|------|------|
| **nono** | 2,231 | Cap-based | ✅最小权限 | ✅ | 9/10 |
| **agent-gov-toolkit** | 1,401 | OPA+OWASP | ✅ | ✅ | 8/10 |
| **greywall** | 173 | Landlock+Seccomp | ✅Learning | ✅ | 7/10 |

**权限治理层推荐：nono**

## 🧠 经验共享层

❌ 0个现有项目 → P0自研

## 推荐组合方案

### 方案A — 生产级（推荐）
- 安全执行: OpenSandbox(10,432⭐) + CubeSandbox(5,014⭐)
- 编排调度: agent-os(2,771⭐)
- 权限治理: nono(2,231⭐)
- 经验共享: 自研

### 方案B — 轻量级（WASM优先）
- 安全执行: OpenSandbox(Docker/gVisor层) + capsule(WASM)
- 编排调度: moltis(2,648⭐)
- 权限治理: agent-gov-toolkit(1,401⭐)
- 经验共享: 自研

### 方案C — 极致安全（MicroVM优先）
- 安全执行: CubeSandbox(KVM) + E2B(Firecracker)
- 编排调度: agent-os(2,771⭐)
- 权限治理: nono + greywall 双保险
- 经验共享: 自研

## 关键缺口

| 缺口 | 严重度 | 说明 |
|------|--------|------|
| 🧠经验共享层 | 🔴 | 0个现有项目，P0自研 |
| 🛡️+🎛️层间接口 | 🔴 | 安全层与编排层如何对接？需设计统一接口 |
| 🔐跨层权限传播 | 🟠 | nono的Cap权限如何穿透到OpenSandbox/CubeSandbox？ |
| 🛡️双引擎调度 | 🟠 | OpenSandbox(多层)+CubeSandbox(KVM)如何按任务自动选择？ |
| Daytona AGPL | 🟠 | 72K⭐但AGPL-3.0限制商业使用 |

## 头条文章生态项目验证（14个项目）

### ❌ 错误归属（3个）
- dclause/hermes-five 36⭐ — 独立机器人/IoT平台，与Hermes Agent无关
- rust-hermes/rusty_hermes 72⭐ — Meta Hermes JS引擎绑定，非Hermes Agent
- Harsh-2909/hermes-go 25⭐ — 独立AI框架，碰巧叫hermes

### ❌ 分类/语言错误（2个）
- nullclaw/nullclaw 7402⭐ — 标Rust实为Zig
- 0xNyk/awesome-hermes-agent 2479⭐ — 标Go框架实为Markdown列表

### ❌ 无法验证（3个）
- IronClaw / PicoClaw / Hermes-Zig — 无GitHub链接

### ✅ 真实但0个适合做执行平台（4域覆盖均≤1域）

## 淘汰规则

- 最后git提交超过2个月 → 直接淘汰
- 提交在1-2月间且star < 1K → 淘汰
- 提交在1月内 → star无下限
- star < 100 → 不分析（用户要求）

下次审查：**2026-08-05**

## 产出文件

- `~/.hermes/data/agent-framework/agent-framework-exec-os-analysis-v3.5.md` — v3.5完整分析文档（分层选型版）
- v3.4/v3.3/v3.2/v3.1 — 历史版本保留
