# Multi-Mechanism Independent Analysis — AI Agent Framework

> Session: 2026-05-05 | 69 keyword groups → 342 candidates → 163 passed activity filter → 31 sub-categories

## Methodology: Multi-Mechanism Independent Analysis

When evaluating a complex system with multiple independent subsystems (e.g., an Agent OS with 4 mechanisms), each mechanism must be analyzed independently with its own:

1. **5-dimension scoring matrix** (Completeness, Maturity, Integrability, Performance, Community Vitality)
2. **Sub-category classification** (e.g., Memory → working/episodic/semantic/procedural/decay/shared/OS/consolidation)
3. **Gap analysis** (which primitives are missing across ALL projects?)
4. **Cross-mechanism heatmap** (compare coverage across mechanisms)

This is distinct from the Technology Selection sub-workflow which evaluates a single role. Multi-mechanism analysis evaluates N roles simultaneously and identifies cross-cutting gaps.

### Pipeline Steps

```
1. Define mechanisms (e.g., Evolution/Oracle/Planning/Memory)
2. Define sub-categories per mechanism (5-8 per mechanism)
3. Define 5 scoring dimensions per mechanism
4. Batch GitHub Search API (10-17 keyword groups per mechanism)
5. Deduplicate (full_name as key, merge categories)
6. Activity filter (2-month cutoff + star floor for 1-2 month)
7. Manual sub-category classification (description + README analysis)
8. 5-dimension scoring per project
9. Per-mechanism gap analysis (which primitives have 0 projects?)
10. Cross-mechanism heatmap (coverage comparison)
11. Self-development priority (P0/P1/P2 based on gap severity)
```

### Key Finding: Primitive Coverage Pattern

Across all 4 OS-layer mechanisms, a consistent pattern emerged:
- **Generation/Mutation** → ✅ Well-covered (8-17 projects per mechanism)
- **Evaluation/Critique** → ✅ Partially covered (1-7 projects)
- **Selection/Debate** → ❌ Sparse (0-4 projects)
- **Inheritance/Arbitration** → ❌❌ Zero coverage (0 projects in ALL mechanisms)

This suggests a universal gap: the "closing" step of any iterative loop (converge, decide, inherit) is systematically underdeveloped in open source.

## Results Summary

### Execution Platform (47 projects, 7 sub-categories)

| Tier | Project | ⭐ | Score | Role |
|------|---------|-----|-------|------|
| T1 | rivet-dev/agent-os | 2,771 | 4.25 | Agent OS (Rust, ~6ms cold start, capability model) |
| T1 | always-further/nono | 2,231 | 4.15 | Capability-based sandbox (Rust, deny-by-default) |
| T1 | moltis-org/moltis | 2,648 | 4.05 | Secure persistent agent server (Rust, single binary) |
| T2 | microsoft/agent-governance-toolkit | 1,401 | 3.90 | Governance/audit |
| T2 | langgenius/dify-sandbox | 1,187 | 3.85 | Lightweight code sandbox (Go, gVisor) |
| T2 | nextlevelbuilder/goclaw | 3,014 | 3.80 | Go multi-tenant OpenClaw |
| T2 | CelestoAI/SmolVM | 505 | 3.75 | MicroVM sandbox |
| T2 | capsulerun/capsule | 281 | 3.70 | WASM sandbox |

**Gaps**: WASM+Capability fusion (0 projects), Experience sharing execution layer (1 project, 3⭐), Firecracker-level hardware isolation (2 low-star projects)

### Evolution Mechanism (25 projects, 5 sub-categories)

| Tier | Project | ⭐ | Score | Role |
|------|---------|-----|-------|------|
| T1 | MemTensor/MemOS | 8,889 | 4.2 | Memory-driven self-improvement |
| T1 | NousResearch/hermes-agent-self-evolution | 2,764 | 3.6 | Hermes native self-evolution |
| T2 | metaevo-ai/meta-context-engineering | 104 | 2.8 | ICML 2026, skill evolution |
| T2 | vibeeval/vibecosystem | 478 | 2.6 | 295 skills ecosystem |

**Gaps**: Inheritance mechanism (0 projects), Fitness evaluation standards, Evolution auditability, Convergence guarantees

### Oracle Mechanism (11 projects, 5 sub-categories)

| Tier | Project | ⭐ | Score | Role |
|------|---------|-----|-------|------|
| T1 | ariffazil/arifos | 42 | 2.8 | Constitutional MCP kernel |
| T2 | dreadnode/ares | 33 | 2.6 | Red-blue adversarial reasoning |
| T2 | dislovelhl/Acgs-Swarm | 3 | 2.4 | Constitutional swarm governance |

**⚠️ CRITICAL**: Highest score only 2.8! Entire Oracle field is nascent.
**Gaps**: Debate mechanism (0 projects), Arbitration mechanism (0 projects), Multi-perspective generation, Bias detection

### Planning Mechanism (32 projects, 6 sub-categories)

| Tier | Project | ⭐ | Score | Role |
|------|---------|-----|-------|------|
| T1 | langgenius/dify | 140,098 | 4.2 | Production DAG workflow |
| T1 | ruvnet/ruflo | 41,956 | 4.2 | Claude agent orchestration |
| T1 | microsoft/agent-framework | 10,114 | 4.2 | Microsoft agent framework |
| T2 | hatchet-dev/hatchet | 7,068 | 3.6 | Background task orchestration |
| T2 | SkyworkAI/DeepResearchAgent | 3,370 | 3.2 | Hierarchical deep research |
| T2 | fim-ai/fim-one | 753 | 3.0 | Dynamic DAG + code execution |

**Gaps**: Rollback mechanism (only 2 projects with 1⭐ each), Dynamic replanning (3 low-star projects), Resource-aware scheduling, Plan verification

### Memory Mechanism (48 projects, 8 sub-categories)

| Tier | Project | ⭐ | Score | Role |
|------|---------|-----|-------|------|
| T1 | mem0ai/mem0 | 54,784 | 4.6 | Universal memory layer (de facto standard) |
| T1 | topoteretes/cognee | 17,033 | 4.4 | Memory control plane |
| T1 | MemTensor/MemOS | 8,889 | 4.2 | Memory OS with decay + self-evolution |
| T2 | MemoriLabs/Memori | 14,061 | 4.4 | Agent-native memory infra |
| T2 | kitfunso/hippo-memory | 621 | 4.0 | Biologically-inspired decay (only complete decay impl) |
| T2 | volcengine/OpenViking | 23,449 | 4.0 | Semantic memory / context DB |
| T3 | sachitrafa/YourMemory | 210 | 3.6 | Ebbinghaus forgetting curve |
| T3 | Mirix-AI/MIRIX | 3,531 | 3.6 | Multi-agent shared memory |

**Gaps**: Decay+Shared fusion (projects with decay don't have shared, vice versa), Procedural memory (only 4 projects), Memory consolidation (no production-grade), Cross-instance consistency

## Self-Development Priority (Revised)

| Priority | Direction | Reason | Impact |
|----------|-----------|--------|--------|
| P0 | Oracle debate + arbitration | Highest score 2.8, 0 production projects | Decision quality |
| P0 | Evolution inheritance | 0 projects implement cross-generation transfer | Evolution loop closure |
| P0 | Planning rollback | Only 2 projects with 1⭐ each | Long-task reliability |
| P1 | Memory decay+shared fusion | Decay and shared exist in different projects | Memory system |
| P1 | Execution WASM+Cap fusion | No project combines WASM isolation + Cap permissions | Execution security |
| P2 | Procedural memory (skill muscle memory) | Only 4 projects | Skill reuse |
| P2 | Memory consolidation | No production-grade project | Long-term memory quality |

## Data Files

- `/root/.hermes/data/agent-framework/agent-framework-exec-os-analysis-v3.md` — Full v3.0 analysis document (36KB)
- `/tmp/gh3_all_repos.json` — Raw 342-repo dataset with categories
- `/tmp/gh3_classified.json` — 163 passed repos with sub-category classification
