---
name: source-evolution
description: Multi-source information evolution system. Continuously discover, register, and evolve information sources including RSS feeds, media outlets, social accounts, WeChat public accounts, and API endpoints. Auto-discover new sources from article content, comments, and cross-references. Use when: (1) adding new RSS/media/social sources, (2) discovering sources from existing content, (3) managing source quality and reliability, (4) setting up continuous source evolution cycles, (5) extracting source URLs from articles or comments, (6) scoring and ranking sources by reliability. NOT for: one-time web fetch (use web_fetch), simple content reading (use read tool).
---

# Source Evolution Skill

Continuously discover, register, score, and evolve information sources.

## Core Loop

```
用户分享链接 → 提取URL/作者 → 评估Tier → 注册新源 → 评分排序 → 持续监控 → 再次进化
```

## Quick Start

```typescript
import { SourceEvolution } from './scripts/source-evolution';

const evolution = new SourceEvolution(kb);

// 用户分享链接（最重要）
await evolution.ingestSharedLink({
  url: 'https://mp.weixin.qq.com/s/xxx',
  sharedBy: 'user',
  sharedAt: new Date().toISOString(),
  source: 'wechat',
  context: '这篇文章讲得很清楚'
});

// 评估社交账号（只追踪作者/版主级别）
evolution.assessSocialProfile('https://twitter.com/sama', {
  followers: 150000,
  verified: true,
  isAuthor: true,
  bio: 'CEO of OpenAI'
});

// 注册源
evolution.addRssSource('https://techcrunch.com/feed/', 'TechCrunch', SourceTier.TIER_A);
evolution.addWeChatSource('https://mp.weixin.qq.com/s/xxx', '文章标题', SourceTier.TIER_B);

// 启动持续进化
evolution.start({ interval: 3600000 }); // 每小时

// 查看统计
console.log(evolution.getStats());
```

## Source Types

| Type | Description | Auto-Discovery |
|------|-------------|----------------|
| `rss` | RSS/Atom feeds | ✅ From link tags |
| `web` | News/media sites | ✅ From article links |
| `wechat` | WeChat public accounts | ✅ From shared URLs |
| `twitter` | Twitter/X accounts | ✅ From links (author-level only) |
| `weibo` | Weibo accounts | ✅ From links (author-level only) |
| `zhihu` | Zhihu topics/users | ✅ From links (author-level only) |
| `github` | GitHub repos/users | ✅ From references |
| `api` | API endpoints | ✅ From docs |
| `substack` | Newsletter feeds | ✅ From links |
| `discord` | Discord channels | Manual only |
| `youtube` | YouTube channels | ✅ From links (author-level only) |
| `reddit` | Reddit communities | ✅ From links |
| `hackernews` | Hacker News | ✅ From RSS |
| `producthunt` | Product Hunt | ✅ From RSS |

## Auto-Discovery Rules

### 1. 用户分享注入（最高优先级）
- 从用户分享的文章/链接中发现新源
- 用户分享的链接置信度最高（微信分享0.85，手动0.75）
- 自动提取文章作者信息
- 从分享的上下文评论中发现更多源

### 2. 内容发现
- **Article content** — URLs, links, references
- **Comments** — Shared links, recommended sources
- **Cross-references** — "According to X", "Source: Y"
- **RSS feed links** — `<link>` tags in feeds
- **Author profiles** — Bio links, other publications

### 3. 社交账号分级（只追踪作者/版主级别）
- **S级**：官方媒体、知名作者、行业领袖（影响力≥80）
- **A级**：专业博主、领域专家、活跃版主（影响力≥60）
- **B级**：有质量产出的创作者（影响力≥40）
- **C级**：普通账号，需验证（影响力≥20）
- **D级**：低质，自动过滤（影响力<20）

## Scoring

### 7维评分系统（0-1）
- **Reliability**: 历史准确性 (×0.2)
- **Freshness**: 更新频率，90天衰减到0 (×0.2)
- **Relevance**: 主题相关性 (×0.1)
- **Completeness**: 内容覆盖度 (×0.05)
- **Diversity**: 独特视角 (×0.05)
- **Influence**: 影响力 (×0.15)
- **QualityRatio**: 高质量文章占比 (×0.15)
- **Tier加成**: S级+0.2，A级+0.1

### 持续评分机制（v3）

每次cron采集后自动评分，追踪：
- `totalArticles` — 总采集文章数
- `highQualityArticles` — 高质量文章数
- `qualityRatio` — 高质量率 = highQuality / total
- `lastActiveAt` — 最后产出高质量内容的时间
- `consecutiveLowScore` — 连续低分次数（<0.3算低分）

### 沉没降频机制

| 评分 | 活跃度 | 采集频次 |
|------|--------|----------|
| ≥0.8 且活跃 | freshness≥0.7 | 每小时 |
| ≥0.8 | — | 每天 |
| ≥0.6 | — | 每天 |
| ≥0.4 | — | 每周 |
| ≥0.3 | — | 每两周 |
| <0.3 | — | 每月 |
| 连续低分≥5 | — | 每季度 |
| 连续低分≥10 | — | 休眠（不采集） |

### Tier降级机制

| 条件 | 动作 |
|------|------|
| 连续3次低分(overall<0.3) | 降1级 (A→B→C→D) |
| 连续5次低分 | 降2级 |
| 连续10次低分 | 标记dead，建议移除 |
| 连续5次低分 | 标记dormant，建议移除 |

### 趋势追踪
- **rising**: 评分上升（+5%以上）
- **stable**: 评分稳定（±5%以内）
- **declining**: 评分下降（-5%以上）
- **dormant**: 连续5次低分，休眠中
- **dead**: 连续10次低分，建议移除

### 历史记录
- 保留最近100次评分
- 支持评分趋势分析
- 每次cron采集后调用 `recordArticle(url, quality)` 更新
- cron任务只采集 `getSourcesToFetchNow()` 返回的源

## Scripts

- `scripts/source-evolution.ts` — Core evolution engine

## References

- **Source categories & presets**: See [references/preset-sources.md](references/preset-sources.md)
- **Discovery patterns**: See [references/discovery-patterns.md](references/discovery-patterns.md)

## API

### Source Registration

```typescript
// Add RSS source
evolution.addRssSource(url, name, tier);

// Add WeChat source
evolution.addWeChatSource(url, name, tier);

// Add social source (author/moderator level only)
evolution.addSocialSource(url, name, tier, { platform: 'twitter' });

// Generic registration
evolution.registerSource({
  url, name, type, tier, reliability, metadata
});
```

### User Shared Links

```typescript
// Single link
await evolution.ingestSharedLink({
  url: 'https://example.com/article',
  sharedBy: 'user-id',
  sharedAt: new Date().toISOString(),
  source: 'wechat',  // or 'manual', 'bookmark', 'chat'
  context: '这篇文章讲得很清楚'
});

// Batch
await evolution.ingestSharedLinks([
  { url: '...', sharedBy: 'user1', sharedAt: '...', source: 'wechat' },
  { url: '...', sharedBy: 'user2', sharedAt: '...', source: 'manual' }
]);
```

### Social Profile Assessment

```typescript
// Assess social account (only author/moderator level)
const profile = evolution.assessSocialProfile('https://twitter.com/sama', {
  followers: 150000,
  verified: true,
  isAuthor: true,
  bio: 'CEO of OpenAI'
});

// Influence score calculation:
// - Followers: 40 points (S-tier: 100k+, A-tier: 10k+, B-tier: 1k+, C-tier: 100+)
// - Verification: 10 points
// - Author/Official: 10-15 points
// - Bio keywords: 10 points
// - Total: 0-100
```

### Source Scoring

```typescript
// Score single source
const score = evolution.scoreSource(url);
console.log(score.overall, score.tier, score.trend, score.fetchFrequency);

// Score all sources
const scores = evolution.scoreAllSources();
scores.sort((a, b) => b.overall - a.overall);

// Record article quality (call after each cron fetch)
evolution.recordArticle(url, 'high');  // or 'medium', 'low'

// Get sources to fetch now (filtered by frequency)
const toFetch = evolution.getSourcesToFetchNow();

// Get health report
const health = evolution.getSourceHealthReport();
console.log(health.active, health.dormant, health.dead);
console.log(health.recommendations);  // action items
```

### Evolution Control

```typescript
// Start continuous evolution
evolution.start({
  interval: 3600000,           // 1 hour
  maxSourcesPerCycle: 10,
  minConfidence: 0.5,
  minScoreToKeep: 0.3,
  minInfluenceToTrack: 20,     // Only track author-level accounts
  autoRegister: true,
  autoRemove: false
});

// Stop evolution
evolution.stop();

// Manual evolution cycle
const result = await evolution.evolve();
console.log(result); // { discovered, registered, removed, scored }
```

### Query & Stats

```typescript
// Get all sources
const sources = evolution.getAllSources();

// Get by type
const rssSources = evolution.getSourcesByType(SourceCategory.RSS);

// Get by tier
const topSources = evolution.getSourcesByTier(SourceTier.TIER_S);

// Get scores
const scores = evolution.getAllScores();

// Get discovered sources
const discovered = evolution.getDiscovered();

// Get user shared links
const shared = evolution.getSharedLinks();

// Get social profiles
const profiles = evolution.getProfiles();

// Get statistics
const stats = evolution.getStats();
console.log(stats);
// {
//   total: 50,
//   byType: { rss: 20, wechat: 15, twitter: 10, ... },
//   byTier: { S: 5, A: 15, B: 20, C: 8, D: 2 },
//   discovered: 120,
//   sharedLinks: 45,
//   profiles: 30,
//   avgScore: 0.72
// }
```

## Events

```typescript
evolution.on('link-shared', (link: SharedLink) => {
  console.log('User shared:', link.url);
});

evolution.on('sources-discovered', (sources: DiscoveredSource[]) => {
  console.log('Discovered:', sources.length);
});

evolution.on('profile-assessed', (profile: SocialProfile) => {
  console.log('Profile:', profile.handle, profile.tier);
});

evolution.on('source-registered', (source: SourceInfo) => {
  console.log('Registered:', source.name);
});

evolution.on('evolution-started', () => {
  console.log('Evolution started');
});

evolution.on('evolution-stopped', () => {
  console.log('Evolution stopped');
});

evolution.on('evolution-cycle', (result) => {
  console.log('Cycle result:', result);
});
```

## Preset Sources

### S-Tier (Top Quality)
- Anthropic, OpenAI Blog, Reuters, Bloomberg, FT

### A-Tier (Excellent)
- TechCrunch, The Verge, Ars Technica, Ben's Bites, One Useful Thing, 36氪, 财联社, 机器之心

### B-Tier (Good)
- Hacker News, Product Hunt, 少数派, 爱范儿, r/artificial, r/MachineLearning

See [references/preset-sources.md](references/preset-sources.md) for full list.

## Best Practices

1. **用户分享优先**：用户分享的链接质量最高，优先处理
2. **只追踪作者级别**：社交媒体只追踪作者/版主/大V，忽略普通用户
3. **Tier管理**：S/A级源优先，D级自动过滤
4. **定期评分**：每次cron采集后自动评分，追踪趋势变化
5. **多样性优先**：避免信息茧房，优先差异化源
6. **沉没降频**：低质源自动降频，休眠源不消耗资源
7. **动态Tier**：Tier随表现升降，不是静态标签
8. **健康检查**：定期调用 `getSourceHealthReport()` 获取建议
