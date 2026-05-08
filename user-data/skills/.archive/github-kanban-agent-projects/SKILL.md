---
name: github-kanban-agent-projects
description: 兼具看板功能+智能体任务管理的GitHub开源项目调研结果，stars>1000筛选
version: 0.1
---

# 看板 + Agent 任务管理项目调研

## 用户要求
- 兼具看板功能和智能体任务管理
- stars > 1000 才值得关注

## 千星以上项目

### 1. Vibe Kanban ⭐24,816
- **GitHub**: BloopAI/vibe-kanban
- **定位**: 看板规划 + Agent执行工作区，专为编码Agent设计
- **技术栈**: Rust, Apache-2.0
- **看板功能**: Issue创建/优先级/分配、拖拽状态流转、Workspace(独立git branch+terminal+dev server)、Diff审查+行内评论、应用预览、PR流程
- **核心**: 人规划→Agent执行→人审查，看板是规划层，workspace是执行层
- **Agent支持**: Claude Code/Codex/Gemini CLI/Copilot/Amp/Cursor等10+

### 2. Taskmaster ⭐26,493
- **GitHub**: eyaltoledano/claude-task-master
- **定位**: AI驱动任务管理系统
- **技术栈**: JavaScript, MIT+Commons
- **注意**: 没有看板UI，是任务列表模式，AI自动拆解PRD为任务

### 3. Edict 三省六部 ⭐14,891
- **GitHub**: cft0808/edict
- **定位**: 12个专业Agent + 实时看板，三省六部制分权架构
- **技术栈**: Python/React, MIT
- **10个面板**: 旨意看板(状态列+省部过滤+心跳徽章)、省部调度(可视化)、奏折阁(归档)、旨库(模板)、官员总览(Token消耗)、天下要闻(自动采集)、模型配置、技能配置、小任务会话、朝堂议政(多角色辩论)
- **核心**: 制度性审核(门下省封驳) + 完全可观测 + 实时可干预
- **缺点**: 依赖OpenClaw生态

### 4. Plane ⭐47,611
- **GitHub**: makeplane/plane
- **定位**: 开源Jira/Linear替代
- **技术栈**: TypeScript/Django, AGPL-3.0
- **功能**: Work Items/Cycles(Sprint+燃尽图)/Modules/Views/Pages(AI驱动)/Analytics
- **注意**: Agent能力是后加的，不是原生设计，AI深度较浅

### 5. ClawTeam ⭐4,686 (增长极快)
- **GitHub**: HKUDS/ClawTeam
- **定位**: Agent Swarm Intelligence — Agent自组织成群
- **技术栈**: Python, MIT, 香港大学HKUDS
- **核心**: 人给目标→Leader Agent自动拆解→Spawn Worker→Worker自主执行+汇报
- **看板**: CLI看板(`oh board show`)、实时看板(`oh board live`)、tmux分屏(`oh board attach`)、Web UI(`oh board serve`)
- **关键设计**: 无数据库(纯JSON文件)、Git Worktree隔离、Inbox+广播通信、任务依赖链、计划审批、生命周期管理
- **风险**: 太新(2026-03-17发布)、v0.3、依赖tmux、JSON文件方案大规模瓶颈

## 对比总结

| 维度 | Vibe Kanban | Edict | Plane | ClawTeam |
|------|:-----------:|:-----:|:-----:|:--------:|
| 模式 | 人规划Agent执行 | 制度审核Agent自治 | 人管理AI辅助 | Agent自组织Swarm |
| 看板 | Web UI | 10面板Dashboard | 完整项目管理 | CLI+Web+tmux |
| 审核 | Diff审查 | 门下省封驳 | 无 | 计划审批 |
| AI深度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 成熟度 | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

## 推荐
- **Agent写代码** → Vibe Kanban
- **Agent全流程自治+审核** → Edict 三省六部
- **传统项目管理+轻AI** → Plane
- **Agent自组织Swarm** → ClawTeam
