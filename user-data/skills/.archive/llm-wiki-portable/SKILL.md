---
name: llm-wiki-portable
version: "4.1.0"
description: Portable version of llm-wiki skill for cross-agent transplantation. Zero external dependencies, zero API keys, pure Markdown+Python stdlib.
---

# llm-wiki v4.1.0 — 通用移植包

## 移植包关键改造（vs Hermes专属版）
1. **工具映射表**：9个抽象工具名 → Hermes/Claude Code/Codex/Generic 四列对照
2. **最低工具集**：只需4个工具（file_read/write/search + shell_exec）即可运行
3. **配置去耦合**：去掉Hermes config系统，改用环境变量 WIKI_PATH / WIKI_DOMAIN
4. **移植指南**：4个目标平台适配说明：Claude Code / Codex / 任意Python Agent / MCP兼容Agent
5. **Python适配器代码**：4函数最小实现（file_read/write/search/shell_exec），复制即用
6. **去Hermes特有引用**：sage-wiki互操作移除，Obsidian集成标为可选

## 核心架构（四层认知记忆模型）
- L1 Working Memory: 当前对话上下文，自动衰减
- L2 Short-term: 会话级笔记，Ebbinghaus衰减
- L3 Long-term: 持久化wiki页面，typed wikilink关系
- L4 Meta-cognitive: 知识置信度+来源追踪+演化历史

## 关键算法（Python stdlib）
- SHA256 diff增量编译：.manifest.json跟踪每个source的SHA256
- Wikilink解析：r'\[\[([^\]|]+?)(?:\s*\\?\|[^\]]+)?\]' 处理别名+转义+.md兼容
- Ebbinghaus衰减：R(t) = e^(-t/S) where S=strength, 间隔复习刷新

## 文件位置
- 通用移植包已通过飞书发送: llm-wiki-v4.1.0-portable.md (42.2KB)
- Hermes专属版: /root/.hermes/skills/research/llm-wiki/SKILL.md
