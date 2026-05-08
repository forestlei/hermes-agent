---
name: ai-daily-report-session-data
description: Persistent session data for AI Daily Report — article records, source registry, and scoring history across sessions
version: 1.0
---

# AI Daily Report — Session Data Store

## Purpose
This skill stores article data and source registry that would otherwise be lost between sessions (since execute_code state is ephemeral and memory tool may be unavailable).

## Source Registry (20 sources, updated 2026-04-13)

| # | 信息源 | 平台 | 类别 | 首次收录 | 代表文章 |
|---|--------|------|------|----------|----------|
| 1 | 量子位 | 头条号 | AI产业新闻 | 2026-04-12 | HTML-in-Canvas引爆前端(85) |
| 2 | 不秃头程序员 | 头条号 | AI工具/开源 | 2026-04-12 | Claude Code成本爆降89%(72) |
| 3 | 李飞飞的飞-vtxf | 头条号 | 前端开发 | 2026-04-12 | frontend-slides网页PPT(58) |
| 4 | Yietion | 头条号 | 开源项目 | 2026-04-12 | Onyx企业知识库(70) |
| 5 | 自由海浪 | 头条号 | AI Agent | 2026-04-12 | Goose AI Agent(68) |
| 6 | 一行人 | 头条号 | AI Agent | 2026-04-12 | Hermes Agent WebUI(55) |
| 7 | AI科技评论 | 头条号 | 学术深度 | 2026-04-12 | A₁ VLA模型(88) |
| 8 | 人工智能科普站 | 头条号 | 论文解读 | 2026-04-12 | SeLaR选择性潜在推理(82) |
| 9 | 娱圈玩家 | 头条号 | 知识图谱 | 2026-04-12 | 本体论与知识图谱(75) |
| 10 | VibeCoder | 头条号 | AI工程化 | 2026-04-12 | GSD Harness Engineering(80) |
| 11 | 网文成神笔记 | 头条号 | AI工具 | 2026-04-12 | 5个Claude Code开源项目(74) |
| 12 | 黎明破晓 | 头条号 | 开源工具 | 2026-04-12 | cmux终端管理(70) |
| 13 | 逛逛GitHub | 头条号 | 开源项目 | 2026-04-13 | awesome-design-md(82) |
| 14 | InfoQ | 头条号 | 技术架构 | 2026-04-13 | 谷歌开源Colab MCP Server(78) |
| 15 | 机器之心Pro | 头条号 | AI深度媒体 | 2026-04-13 | LatentUM统一模型(87), WildClawBench(88) |
| 16 | AIGC小玩童 | 头条号 | AI工具推荐 | 2026-04-13 | Task Master(76) |
| 17 | Phodal | 头条号 | AI架构师 | 2026-04-13 | Harness Monitor(83) |
| 18 | 36氪 | 头条号 | AI创业投资 | 2026-04-13 | StarVLA(86) |
| 19 | 极市平台 | 头条号 | CV/深度学习 | 2026-04-13 | 北大CPL++(79) |
| 20 | arXiv论文解读 | 头条号 | 论文速递 | 2026-04-13 | MegaTrain(81) |

## Article Records (2026-04-13 batch, 11 articles)

| # | 标题 | 作者 | 评分 | group_id |
|---|------|------|------|----------|
| 1 | awesome-design-md 58个设计规范 | 逛逛GitHub | 82 | 7628126598918586923 |
| 2 | AutoResearchClaw/OMNIMEM | 人工智能科普站 | 85 | 7628064625661870638 |
| 3 | 谷歌开源Colab MCP Server | InfoQ | 78 | 7628205878998467126 |
| 4 | LatentUM视觉推理统一模型 | 机器之心Pro | 87 | 7628184670307467819 |
| 5 | Agents外部化综述 | 人工智能科普站 | 84 | 7628045362015601203 |
| 6 | Task Master AI项目管理 | AIGC小玩童 | 76 | 7620322228969816602 |
| 7 | Harness Monitor多Agent质量 | Phodal | 83 | 7628105987064431113 |
| 8 | StarVLA乐高式VLA统一架构 | 36氪 | 86 | 7628177686300525098 |
| 9 | 北大CPL++弱监督视觉定位 | 极市平台 | 79 | 7628056718534099466 |
| 10 | WildClawBench Agent评测 | 机器之心Pro | 88 | 7628140444370813494 |
| 11 | MegaTrain单GPU训120B | arXiv论文解读 | 81 | 7628055894235955750 |

## Article Records (2026-04-12 batch, 13 articles)

| # | 标题 | 作者 | 评分 | group_id |
|---|------|------|------|----------|
| 1 | HTML-in-Canvas引爆前端 | 量子位 | 85 | 7627867768385290771 |
| 2 | Claude Code成本爆降89% | 不秃头程序员 | 72 | 7627748926438801958 |
| 3 | frontend-slides网页PPT | 李飞飞的飞-vtxf | 58 | 1862234147764299 |
| 4 | Onyx企业知识库(26k⭐) | Yietion | 70 | 7626929365934998050 |
| 5 | Goose AI Agent(35k⭐) | 自由海浪 | 68 | 7627088236296307252 |
| 6 | Hermes Agent WebUI | 一行人 | 55 | 7627871286772957705 |
| 7 | A₁ VLA模型(CVPR2026) | AI科技评论 | 88 | 7626335099042251306 |
| 8 | SeLaR选择性潜在推理 | 人工智能科普站 | 82 | 7627676609713062406 |
| 9 | 本体论与知识图谱 | 娱圈玩家 | 75 | 7627745546656039466 |
| 10 | GSD Harness Engineering | VibeCoder | 80 | 7627862613792014890 |
| 11 | 5个Claude Code开源项目 | 网文成神笔记 | 74 | 7627680456355463743 |
| 12 | Multica多Agent协作(4k⭐) | 不秃头程序员 | 72 | 7627002472908800566 |
| 13 | cmux终端管理(1.2k⭐) | 黎明破晓 | 70 | 7624771468869567011 |

## Duplicate Sources
- 不秃头程序员: appears twice (articles 2 and 12 from 04-12 batch)
- 人工智能科普站: appears twice (articles 2 from 04-13, article 8 from 04-12, article 5 from 04-13)
- 机器之心Pro: appears twice in 04-13 batch (articles 4 and 10)
