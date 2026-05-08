# AI Agent 人机交互层 (L7) 选型评估

> 2026-05-05 | 七层架构第7层

## 8项核心需求

| # | 需求 | 定义 | 验收标准 |
|---|------|------|---------|
| H1 | 多Agent统一入口 | 一个界面管理/切换/协调多个Agent实例 | 单界面≥5个Agent同时在线 |
| H2 | 多平台接入 | 飞书/Telegram/Discord/Web/CLI等多渠道 | ≥3个平台同时在线 |
| H3 | 实时流式交互 | Agent输出实时流式呈现，支持中断/引导 | 流式延迟<500ms，支持中途干预 |
| H4 | 任务可视化 | Agent执行过程可视化（DAG/进度/日志） | 任务状态实时更新，支持回溯 |
| H5 | 权限可视化 | Agent操作权限的可视化审批/管理 | 操作审批<3步，权限变更实时生效 |
| H6 | 技能/工具管理 | Agent技能和工具的浏览/配置/启用 | 技能一键启用，工具参数可视化配置 |
| H7 | 多模态交互 | 文字/语音/图像/文件多模态输入输出 | ≥3种模态 |
| H8 | 群组协作 | 多人在同一Agent会话中协作 | 支持群聊@Agent，消息隔离 |

## 搜索策略

- 12维度搜索（自底向上+自顶向下双视角）
- 362个唯一项目，73个⭐≥500

## 评分体系

- Star分(50%)：log归一化，max 50分
- 需求分(50%)：8项需求×6.25分=50分
- 达标线：总分≥63分

## 推荐短名单（9个达标）

| 排名 | 项目 | ⭐ | 总分 | 推荐等级 |
|------|------|---|------|---------|
| 1 | iOfficeAI/AionUi | 24,221 | 77.7 | 🔥 Tier A |
| 2 | open-webui/open-webui | 135,836 | 77.2 | 🔥 Tier A |
| 3 | CopilotKit/CopilotKit | 29,978 | 73.9 | ✅ Tier B |
| 4 | all-hands-ai/openhands | 53,000 | 72.0 | ✅ Tier B |
| 5 | lobehub/lobe-chat | 62,000 | 71.9 | ✅ Tier B |
| 6 | EKKOLearnAI/hermes-web-ui | 3,585 | 66.6 | ✅ Tier B |
| 7 | ValueCell-ai/ClawX | 7,025 | 66.5 | ✅ Tier B |
| 8 | builderz-labs/mission-control | 4,600 | 65.9 | ✅ Tier B |
| 9 | continue-dev/continue | 26,000 | 65.0 | ✅ Tier B |

## 技术栈推荐

```
主力交互平台：open-webui (136K⭐, MIT, 最成熟)
  + Agent编排UI：mission-control (4.6K⭐, 编排可视化)
  + Hermes原生对接：hermes-web-ui (3.6K⭐, 8平台频道+技能管理)
  + SDK嵌入：CopilotKit (30K⭐, React SDK)
```

## 按需求最佳匹配

- H1 多Agent → mission-control / AionUi
- H2 多平台 → hermes-web-ui(8频道) / open-webui
- H3 流式交互 → open-webui / CopilotKit
- H4 任务可视化 → mission-control
- H5 权限可视化 → mission-control
- H6 技能管理 → hermes-web-ui
- H7 多模态 → open-webui / lobe-chat
- H8 群组协作 → AionUi / hermes-web-ui

## 关键决策点

- 以Hermes Agent为核心 → hermes-web-ui做主力
- 需要通用AI交互 → open-webui做主力
- 需要嵌入现有应用 → CopilotKit做SDK层
- 编排可视化 → mission-control做补充

## 风险

- AionUi License为NOASSERTION，商用需谨慎
- oobabooga/ComfyUI为AGPL-3.0/GPL-3.0，不适合商用
- hermes-web-ui仅1个月(2026-04创建)，需观察稳定性

## 与L3执行平台交叉验证

| L7项目 | L3关联 | 交叉价值 |
|--------|--------|---------|
| hermes-web-ui | Hermes Agent Gateway | L7→L4→L3全链路打通 |
| open-webui | OpenSandbox/e2b | 沙箱执行可视化 |
| mission-control | Ruflo/Vibe Kanban | 编排可视化+执行监控 |
| CopilotKit | 任何MCP工具 | 工具调用可视化 |
