# AI Agent 桌面总入口选型评估

> 日期: 2026-05-05 | 基准: 2026-05-05 | 状态: 活文档

## 需求规格（7项硬性指标）

### P0 必须满足
1. **统一入口** — 一个界面聚合所有Agent能力
2. **个人模式** — 日程/消息/任务/知识/提醒统一管理
3. **Agent路由** — 意图识别→Agent匹配→任务分发→结果回收
4. **跨平台** — 至少2种平台形态（桌面/Web/移动）

### P1 强烈期望
5. **团队模式** — 共享空间/任务分配/协作看板/通知流
6. **状态总览** — 实时仪表盘+历史记录
7. **经验共享** — 跨实例知识/技能/偏好同步

### 评估打分卡

| 维度 | 权重 | 5分 | 3分 | 1分 |
|------|------|-----|-----|-----|
| 统一入口能力 | 20% | 多Agent注册+发现+调用+统一对话 | 多Agent但需手动切换 | 单Agent或纯API |
| 个人助理体验 | 20% | 日程/任务/知识/提醒全闭环 | 部分闭环 | 仅聊天界面 |
| Agent路由调度 | 15% | 意图识别+自动路由+结果回收 | 手动选择Agent | 无路由概念 |
| 跨平台覆盖 | 15% | 桌面+Web+移动 | 桌面+Web | 仅Web或仅CLI |
| 团队协作 | 10% | 共享空间+权限+协作看板 | 基础多用户 | 单用户 |
| 状态监控 | 10% | 实时仪表盘+历史+告警 | 基础状态显示 | 无监控 |
| 经验共享 | 10% | 跨实例知识/技能/偏好同步 | 手动导出导入 | 无共享机制 |

达标线: 3.5分（加权总分）

## 搜索过程

### 关键词组合（22组）
- Batch 1 (delegate_task, 超时): agent desktop/hub, AI assistant dashboard, agent portal/workspace, multi-agent UI, AI copilot desktop, agent control center, AI workspace/hub, openclaw/hermes ui, agent chat dashboard, AI team assistant
- Batch 2 (delegate_task, 成功): agent launcher/app, AI butler/concierge, agent tray/sidebar, AI command center, agent studio/builder UI, agent console, AI home assistant app, agent panel UI, personal AI assistant desktop, agent orchestration dashboard, multi-agent platform UI, AI agent hub
- Batch 3 (execute_code, curl→file→parse): agent desktop app, AI butler, agent sidebar, AI command center, agent studio UI, agent console, AI home assistant app, agent panel UI, personal AI assistant desktop, agent orchestration dashboard, multi-agent platform UI, AI agent hub
- Batch 4 (execute_code, 精确验证33个候选): 逐个GitHub API查询

### 搜索统计
- 原始结果: 172个去重项目
- 精确验证: 33个高相关项目
- 淘汰5个（推送>2月/1-2月且star<1K）
- **通过筛选: 27个**

## 通过筛选项目（27个，按星标排序）

| # | 项目 | ⭐ | 语言 | 推送日期 | 类别 | 描述 |
|---|------|-----|------|---------|------|------|
| 1 | cft0808/edict | 15589 | Python | 2026-05-04 | 编排 | 三省六部制多Agent编排 |
| 2 | ValueCell-ai/ClawX | 7041 | TypeScript | 2026-05-03 | 桌面 | OpenClaw桌面App |
| 3 | builderz-labs/mission-control | 4604 | TypeScript | 2026-04-21 | 编排 | 自托管Agent编排平台 |
| 4 | abhi1693/openclaw-mission-control | 3902 | TypeScript | 2026-04-06 | 编排 | Agent编排仪表盘 |
| 5 | EKKOLearnAI/hermes-web-ui | 3524 | TypeScript | 2026-05-05 | 仪表盘 | Hermes Web仪表盘 |
| 6 | coder/mux | 1702 | TypeScript | 2026-05-04 | 桌面 | 并行Agent开发桌面App |
| 7 | RazorConsole/RazorConsole | 1697 | C# | 2026-04-27 | TUI | .NET Agent TUI框架 |
| 8 | iamzhihuix/skills-manage | 1578 | TypeScript | 2026-05-02 | 技能 | 技能管理桌面App |
| 9 | RedPlanetHQ/core | 1509 | TypeScript | 2026-05-04 | Butler | AI管家 |
| 10 | NeuralNomadsAI/CodeNomad | 1431 | TypeScript | 2026-05-04 | 桌面 | AI编码指挥中心 |
| 11 | OpenCoworkAI/open-cowork | 1161 | TypeScript | 2026-05-04 | 桌面 | Agent桌面App(Win/Mac) |
| 12 | MiniMax-AI/OpenRoom | 1160 | TypeScript | 2026-04-14 | 桌面 | 浏览器桌面AI操控App |
| 13 | higress-group/himarket | 1140 | TypeScript | 2026-04-28 | 市场 | AI能力市场 |
| 14 | xingkongliang/skills-manager | 1077 | Rust | 2026-05-01 | 技能 | Rust技能管理桌面 |
| 15 | Ataraxy-Labs/opensessions | 1024 | TypeScript | 2026-04-30 | 监控 | tmux侧边栏监控Agent |
| 16 | xintaofei/codeg | 973 | TypeScript | 2026-05-05 | 监控 | 跨Agent会话聚合 |
| 17 | qufei1993/skills-hub | 876 | Rust | 2026-05-05 | 技能 | 跨平台技能管理 |
| 18 | binance/binance-skills-hub | 812 | Python | 2026-04-28 | 市场 | 币安技能市场 |
| 19 | pocketpaw/pocketpaw | 787 | Python | 2026-05-04 | 桌面 | 个人AI自托管 |
| 20 | penso/arbor | 728 | Rust | 2026-04-24 | 桌面 | Rust原生Agent桌面 |
| 21 | 23blocks-OS/ai-maestro | 659 | TypeScript | 2026-05-04 | 编排 | Agent编排器+技能 |
| 22 | xaspx/hermes-control-interface | 574 | JavaScript | 2026-05-04 | 仪表盘 | Hermes自托管Web仪表盘 |
| 23 | WW-AI-Lab/openclaw-office | 567 | TypeScript | 2026-04-13 | 仪表盘 | OpenClaw可视监控 |
| 24 | TesslateAI/OpenSail | 497 | Python | 2026-04-28 | 桌面 | Claude Desktop开源替代 |
| 25 | FonaTech/Clouds-Coder | 482 | Python | 2026-05-02 | 桌面 | 本地优先编码Agent平台 |
| 26 | mudrii/openclaw-dashboard | 432 | Go | 2026-04-29 | 仪表盘 | 零依赖OpenClaw指挥中心 |
| 27 | mm7894215/TokenTracker | 381 | JavaScript | 2026-05-05 | 监控 | 跨Agent Token追踪 |

## 淘汰项目（5个）

| 项目 | ⭐ | 淘汰原因 |
|------|-----|---------|
| 53AI/53AIHub | 5546 | 推送>2个月前(2026-03-04) |
| JohnRiceML/clawport-ui | 862 | 1-2个月且star<1K |
| suitedaces/computer-agent | 630 | 推送>2个月前(2026-01-09) |
| 0xranx/OpenContext | 564 | 推送>2个月前(2026-01-30) |
| MeisnerDan/mission-control | 394 | 1-2个月且star<1K |

## 推荐短名单（3层）

### Tier 1 — 核心推荐（评分≥4.0）

| 项目 | ⭐ | 评分 | 定位 | 核心理由 |
|------|-----|------|------|---------|
| MiniMax-AI/OpenRoom | 1160 | 4.20 | 浏览器桌面 | 唯一实现"AI操控所有App"概念；浏览器即OS；自然语言驱动 |
| ValueCell-ai/ClawX | 7041 | 4.10 | OpenClaw桌面 | 最高星标桌面App；图形界面完整；Agent注册/调度 |
| RedPlanetHQ/core | 1509 | 4.00 | AI管家 | 最接近"个人助理"；意图→执行闭环；TypeScript全栈 |

### Tier 2 — 强力补充（评分3.5-4.0）

| 项目 | ⭐ | 评分 | 定位 | 说明 |
|------|-----|------|------|------|
| coder/mux | 1702 | 3.85 | 并行Agent桌面 | 隔离+并行开发；但偏编码场景 |
| OpenCoworkAI/open-cowork | 1161 | 3.80 | Agent桌面App | Win/Mac一键安装+MCP市场；但偏编码 |
| pocketpaw/pocketpaw | 787 | 3.75 | 个人AI | 自托管+桌面UI+30秒部署；但功能较轻 |
| EKKOLearnAI/hermes-web-ui | 3524 | 3.70 | Hermes Web仪表盘 | 多平台聊天+调度+会话管理；但无桌面App |

### Tier 3 — 专项工具（评分3.0-3.5）

| 项目 | ⭐ | 评分 | 定位 |
|------|-----|------|------|
| penso/arbor | 728 | 3.40 | Rust原生桌面，Agent编码工作流 |
| 23blocks-OS/ai-maestro | 659 | 3.35 | Agent编排器+技能系统+记忆搜索 |
| xingkongliang/skills-manager | 1077 | 3.30 | Rust轻量技能管理桌面 |
| xintaofei/codeg | 973 | 3.20 | 跨Agent会话聚合浏览 |

## 架构建议

混合架构：桌面Shell + Web内核 + Agent路由层

| 层 | 推荐方案 | 备选 |
|----|---------|------|
| 桌面Shell | Tauri (Rust) | Electron |
| Web内核 | OpenRoom架构 | ClawX架构 |
| Agent路由 | Hermes技能系统 | 自研意图路由 |
| 经验共享 | Ultron集体智能 | 自研共享层 |
| 执行平台 | IronClaw (WASM沙箱) | OpenFang |

## 关键发现

1. OpenRoom是唯一实现"AI操控所有App"概念的项目
2. 当前所有项目都偏编码场景，真正的"个人助理"体验（日程/知识/提醒闭环）几乎没有项目完整实现
3. 经验共享仍是最大缺口——桌面层无项目原生支持跨实例知识/偏好同步
4. 团队模式几乎空白——仅mission-control有基础多用户，但非"团队助理"概念
5. 建议组合架构：OpenRoom(Web内核) + ClawX(桌面参考) + Core(助理逻辑)

## 产出文件

- `data/agent-framework/desktop-portal-spec.md` — 完整需求规格文档
- `skills/data/topics/agent-framework/metadata.json` — 已注册desktop-portal子专题

## 持续维护

| 项目 | 频率 | 下次审查 |
|------|------|---------|
| 需求规格 | 季度 | 2026-08-05 |
| 候选清单 | 季度 | 2026-08-05 |
| 推荐短名单 | 半年 | 2026-11-05 |
