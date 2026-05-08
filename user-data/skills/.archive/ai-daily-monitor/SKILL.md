---
name: ai-daily-monitor
description: AI信息监控系统 — 自动采集GitHub热门项目/高评价论文/AI动态，3个月去重缓存，llm-wiki知识库整理，高价值项目触发深度分析
version: 0.1
status: architecture-designed
---

# AI信息监控系统

## 架构设计

### 1. 采集层
- **GitHub热门项目**: 使用 `github-tracker` 技能采集trending repos，按AI/ML分类
- **高评价论文**: arxiv API + HuggingFace Daily Papers，按引用/讨论热度筛选
- **AI产业动态**: 使用 `blogwatcher` 技能采集RSS/博客（厂商博客、AI日报、Newsletter）
- **信息源管理**: 自动积累信息源，定期探索新源

### 2. 去重层（3个月缓存）
- **存储**: SQLite数据库，路径 `~/ai-monitor/cache.db`
- **表结构**: items(id, source, title, content_hash, embedding, url, collected_at, merged_into)
- **去重策略**:
  - 精确匹配: URL + content_hash 直接过滤
  - 相似度检测: TF-IDF + cosine similarity，阈值 >0.85 视为重复
  - 合并: 相似信息合并到最早记录，后续引用指向它
- **滚动清理**: 每次运行自动清理3个月前的缓存条目

### 3. 知识库层（llm-wiki）
- 采集去重后的新信息 → ingest 到 llm-wiki
- 自动创建/更新 entities（项目/论文/概念）
- 信息源作为独立 entity 积累，定期评估质量
- 路径: `~/wiki`

### 4. 深度分析层
- 高价值项目（stars>1000 或 讨论热度高）→ 触发 `github-research-assistant` 深度分析
- 分析结果写回 wiki，关联到对应 entity
- 分类标签: framework / model / tool / research / infrastructure

## 数据流

```
采集脚本 → 去重缓存DB → 新信息? → YES → llm-wiki ingest → 高价值? → YES → github深度分析 → 写回wiki
                                  → NO  → 跳过（已存在）
```

## 定时任务
- 每日 06:00 采集 + 去重 + wiki写入
- 每周日 信息源质量评估 + 新源探索
- 每月1日 3个月缓存清理

## 已知AI信息源（见memory中的完整列表）
- 微信公众号: 机器之心、量子位、新智元、AI科技评论、夕小瑶科技说
- 厂商博客: OpenAI/Anthropic/DeepMind/Meta/Microsoft/Mistral/HuggingFace/NVIDIA/百度/阿里/字节/智谱/DeepSeek
- 论文追踪: HF Daily Papers, AK's Papers, Papers With Code, Arxiv Sanity
- 英文Newsletter: The Batch, Import AI, TLDR AI, Ben's Bites, The Rundown AI
- 社区: Reddit r/ML, r/LocalLLaMA, Hacker News, AI Discord

## 实现状态
- [x] 架构设计
- [ ] SQLite去重缓存数据库 + 相似度检测脚本
- [ ] GitHub热门项目采集脚本
- [ ] 论文采集脚本 (arxiv + HF Daily Papers)
- [ ] RSS/博客采集脚本
- [ ] 信息源管理与自动发现脚本
- [ ] 日报生成 + wiki写入主脚本
- [ ] 高价值项目自动深度分析触发脚本
- [ ] Cron定时任务设置
