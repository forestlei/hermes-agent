---
name: knowledge-base
description: Intelligent knowledge base system for multi-source information collection, content analysis, insight generation, and knowledge precipitation. Use when: (1) collecting data from RSS/API/web sources, (2) analyzing content quality and extracting knowledge, (3) generating insights from collected data, (4) managing knowledge sources and scoring reliability, (5) performing agent fission for parallel analysis, (6) validating predictions and precipitating knowledge, (7) packaging skills and automating workflows, (8) optimizing performance with caching/concurrency/rate-limiting. NOT for: simple file reads (use read tool), general web search (use web_fetch), or basic text processing.
---

# Knowledge Base System

A 6-stage intelligent knowledge base system built in TypeScript.

## Quick Start

```typescript
import { KnowledgeBase } from './src/index';

const kb = new KnowledgeBase('./data');

// Add source
const source = await kb.addSource({
  name: 'TechCrunch',
  type: 'rss',
  url: 'https://techcrunch.com/feed/',
  metadata: { description: 'Tech news', category: 'technology' }
});

// Collect & analyze
await kb.collect(source.id);
const result = await kb.analyze(item);

// Execute fission for parallel processing
const session = await kb.executeFission('parent-1', 'task', data);

// Validate & precipitate knowledge
kb.startAnalysis('content-1', 'swot');
```

## Architecture

### Stage 1: Source Management & Collection
- **SourceManager**: Register, update, delete, score sources (RSS/API/Web/Social/File/Manual)
- **ContentManager**: Collect from sources with auto-dedup and quality scoring
- **StorageManager**: JSON file storage with batch operations

### Stage 2: Content Analysis
- **QualityScorer**: 8-dimension scoring (completeness, accuracy, relevance, freshness, authority, clarity, depth, originality)
- **KnowledgeExtractor**: Entity, relation, fact, concept extraction
- **InsightGenerator**: 6 insight types (trend, causal, pattern, anomaly, opportunity, risk)
- **FrameworkLibrary**: SWOT, PESTLE, 5W2H, PDCA, Six Thinking Hats

### Stage 3: Agent Fission
- **FissionTrigger**: 6 trigger types (data volume, depth, tasks, time, memory, context)
- **FissionStrategy**: 8 strategies (by domain, function, task, data, depth, time, memory, context)
- **SubAgentManager**: Lifecycle, communication, timeout, retry
- **ResultAggregator**: Validation, conflict resolution, synthesis
- **FissionRollback**: Problem detection, stop, rollback, reevaluation

### Stage 4: Validation & Knowledge Precipitation
- **ValidationTracker**: Predictions, verification, accuracy scoring
- **KnowledgePrecipitator**: Success patterns, failure lessons, best practices
- **AnalysisRecorder**: Process steps, conclusions, reasoning chains

### Stage 5: Skillization & Integration
- **SkillPackager**: 9 pre-defined skills with parameter validation
- **AutomationIntegrator**: 7 default tasks, cron scheduling
- **DataManager**: Backup, restore, cleanup, migration

### Stage 7: Evolution Engine (NEW!)
- **EvolutionEngine**: Continuous self-evolution with 6-phase cycle
- **SkillTree**: Growing analysis skill tree with experience and levels
- **KnowledgeOrganizer**: Generate first, organize later (先生成，再组织)
- **MutationSystem**: Track all knowledge mutations and evolution chains
- **AutoDiscovery**: Automatically discover new sources from existing knowledge
- **CrossPollination**: Transfer patterns between different skill domains
- **PerformanceOptimizer**: LRU cache, concurrency control, rate limiting, retry
- **ExtensionManager**: Visualization, prediction, recommendation, UI, export, import

## Key APIs

| Method | Description |
|--------|-------------|
| `kb.addSource(source)` | Register information source |
| `kb.collect(sourceId?)` | Collect from source(s) |
| `kb.analyze(item)` | Analyze single content item |
| `kb.analyzeBatch(items)` | Batch analysis |
| `kb.executeFission(parentId, task, data, strategyId?)` | Parallel agent fission |
| `kb.startAnalysis(contentId, frameworkId?)` | Start validation process |
| `kb.completeAnalysis(processId)` | Complete validation |
| `kb.executeSkill(skillId, params)` | Execute packaged skill |
| `kb.executeAutomationTask(taskId)` | Run automation task |
| `kb.backup()` / `kb.restore(id)` | Data management |
| `kb.optimizer.set/get(key)` | Cache operations |
| `kb.optimizer.executeConcurrent(fn, priority)` | Concurrent execution |
| `kb.optimizer.retry(fn, attempts, delay)` | Retry with backoff |
| `kb.extensions.registerExtension(ext)` | Register extension |
| `kb.evolution.start()` | Start continuous evolution |
| `kb.evolution.stop()` | Stop evolution |
| `kb.evolve()` | Trigger one evolution cycle |
| `kb.evolution.getSkillTree()` | Get growing skill tree |
| `kb.evolution.getMutations()` | Get all knowledge mutations |
| `kb.evolution.getClusters()` | Get knowledge clusters |
| `kb.evolution.injectMutation(...)` | Inject external knowledge |

## Detailed References

- **Source types & configuration**: See [references/sources.md](references/sources.md)
- **Analysis frameworks**: See [references/frameworks.md](references/frameworks.md)
- **Fission strategies**: See [references/fission.md](references/fission.md)
- **Automation tasks**: See [references/automation.md](references/automation.md)

## Scripts

- `scripts/setup.sh` - Initialize project (install deps, build, test)
- `scripts/collect.sh` - Run collection from configured sources
- `scripts/analyze.sh` - Run analysis on collected data
