---
name: github-memory-status
version: 0.1
description: 本地GitHub项目知识库当前状态 - 74个项目7个主题168个功能标签
trigger: github-memory, 项目库, project library, 项目分析
---

# GitHub本地项目知识库

## 当前状态（2026-04-20）
- **总项目数**: 74个
- **功能标签**: 168个唯一标签
- **位置**: ~/.hermes/github-memory/

## 主题分布
| 主题 | 项目数 | 目录 |
|------|--------|------|
| 智能体项目 | 27 | github-memory/智能体项目/ |
| AI基础设施 | 13 | github-memory/AI基础设施/ |
| pptx生成 | 12 | github-memory/pptx生成/ |
| 数据工程AI项目 | 10 | github-memory/数据工程AI项目/ |
| AI应用平台 | 5 | github-memory/AI应用平台/ |
| AI研究 | 5 | github-memory/AI研究/ |
| 工具与资源 | 7 | github-memory/工具与资源/ |

## 目录结构
```
~/.hermes/github-memory/
├── _index.md              # 全项目总索引（按stars排序）
├── _features/
│   ├── tag-index.md       # 人类可读的功能标签索引
│   └── tag-index.json     # 程序化查询接口
├── {topic}/
│   └── {owner}/
│       └── {repo}/
│           ├── metadata.json    # 项目元数据+feature_tags
│           ├── notes.md         # 项目简介
│           └── analysis/
│               └── latest.md   # 深度分析
```

## 已知问题
- 26个热门项目(langchain, autogen等)的README只有278字符stub，需认证API重新获取
- HKUDS/Paper2Slides metadata.json截断，crewAIInc/crewAI字段为空
- execute_code沙箱write_file批量写入可能静默失败，需用terminal验证
- GitHub API需认证访问，token在环境变量中
