# User Data Backup

This directory contains a backup of user-defined Hermes Agent data that is NOT
stored in the Git repository by default. It exists under `~/.hermes/` at runtime
and is at risk of being lost during version upgrades or instance migrations.

## Directory Structure

```
user-data/
├── constitution/        # 🔴 宪法层 — 最高优先级，不可丢失
│   ├── persistent-solver-SKILL.md   # 8条顶层规则 (v3.2.0)
│   ├── MEMORY.md                    # 顶层体系索引+规则摘要
│   ├── USER.md                      # 用户偏好+幻觉零容忍+消息规则
│   ├── top-level-rules.md           # 顶层规则定义 (v3.0.0)
│   └── coding-rules-README.md       # 编码规则说明
│
├── knowledge/           # 🔴 知识资产 — 长期积累，不可再生
│   ├── github-memory/               # GitHub知识库 (11主题154条目)
│   ├── ai-daily-report/             # AI日报索引 (完整内容51MB，仅存索引)
│   └── data/knowledge-search.db     # 知识搜索数据库
│
├── skills/              # 🟡 核心技能 — SKILL.md定义文件
│   ├── software-development/        # persistent-solver, routa-methodology 等
│   ├── reasoning/                   # concept-discovery, source-prospector 等
│   ├── research/                    # ai-daily-report, github-research-assistant 等
│   └── .usage.json                  # 技能使用统计
│
├── automation/          # 🟡 自动化配置
│   ├── scripts/                     # 用户脚本 (auto-sync等)
│   ├── cron/jobs.json               # 定时任务定义
│   └── sources/                     # 数据源注册表
│
└── config/              # 🟡 配置 (已脱敏)
    ├── config.yaml                  # 主配置 (API keys已替换为占位符)
    └── SOUL.md                      # 默认SOUL模板
```

## Sync Instructions

To sync latest user data from a running Hermes instance:

```bash
# From project root
./scripts/sync_user_data.sh
```

To restore user data to a new Hermes instance:

```bash
# From project root
./scripts/sync_user_data.sh --restore
```

## What's NOT Here

- `~/.hermes/.env` — API keys and secrets (NEVER commit to Git)
- `~/.hermes/auth.json` — Auth tokens (NEVER commit to Git)
- `~/.hermes/state.db` — Session database (regenerable)
- `~/.hermes/ai-daily-report/` full content — 51MB, only index stored here
- `~/.hermes/skills/*/routa-src/` — Large reference docs (regenerable from source)
- `~/.hermes/cron/output/` — Cron output logs (regenerable)

## Priority Classification

| Priority | Meaning | Loss Impact |
|----------|---------|-------------|
| 🔴 宪法层 | Agent的核心行为规则 | 完全丧失个性，退化为默认行为 |
| 🔴 知识资产 | 长期积累的知识库 | 不可再生，需要重新构建 |
| 🟡 核心技能 | 自定义技能定义 | 需要重新创建和训练 |
| 🟡 自动化 | 脚本和定时任务 | 需要重新配置 |
| 🟡 配置 | 运行时配置 | 需要重新设置 |
