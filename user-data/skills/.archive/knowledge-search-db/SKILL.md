---
name: knowledge-search-db
description: 统一知识搜索库 — SQLite FTS5全文检索，四类数据源（GitHub项目/技能/论文/专利）统一schema，评分过滤，跨源联合查询
version: 1.0.0
author: Hermes Agent
tags: [search, sqlite, fts5, knowledge-base, github, papers, skills, patents]
---

# 统一知识搜索库

SQLite FTS5全文检索系统，整合GitHub项目、技能库、论文、专利四类数据源。

## 数据库位置

`~/.hermes/data/knowledge-search.db`

## 统一Schema

四类数据源共享核心字段：**quality_score + tags + authors**

| 字段 | GitHub项目 | 技能库 | 论文 | 专利 |
|------|-----------|--------|------|------|
| ID | full_name | dir_name | arxiv_id | patent_id |
| 标题 | name | name | title | title |
| 描述 | description | description | abstract | abstract |
| 标签 | topics+language | category+tags | categories+kw | IPC/CPC+kw |
| 作者 | owner/org | author | authors[] | inventors |
| 评分 | quality_score | quality_score | quality_score | quality_score |
| 时间 | pushed_at | updated_at | published | filed_date |
| 特有 | stars/forks | content_len | link | assignee |

## 评分体系

### GitHub项目评分 (0-100)
- Stars (0-40): ≥50k→40 | ≥10k→35 | ≥5k→30 | ≥1k→25 | ≥500→20 | ≥100→15
- 活跃度 (0-20): 7天内→20 | 30天内→15 | 90天内→10
- Topics丰富度 (0-15): min(15, topics数×2)
- 摘要 (0-10): 有summary且>50字→10
- 描述质量 (0-15): >100字→15 | >50字→10 | >10字→5

### 论文评分 (0-100)
- depth×0.35 + originality×0.30 + accuracy×0.20 + readability×0.15

### 技能评分 (0-100)
- 描述质量(0-30) + 标签丰富度(0-20) + 分类(0-10) + 内容深度(0-40)

### 门槛
- **≥65分** → 入搜索库
- **≥80分** → 写入信息源注册表

## FTS5全文检索

```sql
-- 跨源搜索示例
SELECT 'github' as type, g.full_name, g.quality_score
FROM github_projects_fts f JOIN github_projects g ON f.rowid = g.id
WHERE github_projects_fts MATCH 'memory'
UNION ALL
SELECT 'paper' as type, p.title, p.quality_score
FROM papers_fts f JOIN papers p ON f.rowid = p.id
WHERE papers_fts MATCH 'memory'
ORDER BY quality_score DESC;
```

## 数据源

| 数据源 | 采集路径 | 数量 |
|--------|---------|------|
| GitHub项目 | `~/.hermes/ai-daily-report/shared/collections/{date}/github.json` | 220 |
| 项目摘要 | `~/.hermes/ai-daily-report/shared/projects/{org}--{repo}/` | 有摘要 |
| 技能库 | `~/.hermes/skills/{name}/SKILL.md` | 94 |
| 论文 | `~/.hermes/ai-daily-report/shared/collections/{date}/papers.json` | 621 |
| 专利 | 待建 | 0 |

## 构建脚本

```bash
# 重建搜索库（从数据源重新导入）
python3 ~/.hermes/scripts/build-knowledge-search-db.py
```

## 演进路线

1. ✅ FTS5全文检索（当前）
2. 🔜 向量语义搜索（sentence-transformers嵌入）
3. 📋 混合检索（BM25+向量RRF融合）
4. 🔄 增量更新（Cron定时采集→自动评分→增量入库）
5. 🌐 API服务化（REST API封装）

## Pitfalls

- FTS5虚拟表不含非索引列（如quality_score），需JOIN主表
- 标签和作者以JSON数组存储，FTS5可检索但需注意分词
- 论文quality_score来自采集时评分，GitHub项目评分由compute_gh_score()动态计算
- 专利表已建schema但暂无数据
- 数据同步到hermes-data仓库Git
