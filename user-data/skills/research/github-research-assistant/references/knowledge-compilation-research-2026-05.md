# Knowledge Compilation (知识编译) — Cross-Topic Research

**Date**: 2026-05-07
**Status**: Research complete, implementation pending user approval
**Cross-topic**: 本体与语义 (L1+L2) + 智能体项目 (L3) + 工具与资源 (L2)

## Three-Layer Framework

Knowledge Compilation has three distinct meanings that must be distinguished:

| Layer | Meaning | Ontology Relation | Skill Relation |
|-------|---------|-------------------|----------------|
| **L1 Classical** | Compile logic formulas → tractable circuits (SDD/d-DNNF/OBDD) for poly-time inference | Ontology reasoning accelerator: OWL→CNF→SDD/d-DNNF | Skill's "executable kernel": rules/constraints → fast-inference circuit |
| **L2 LLM** | Compile unstructured knowledge → structured knowledge base (wiki/KG) | Ontology auto-construction: docs → ontology instances → OWL KB | Skill's "knowledge substrate": extract reusable structured knowledge from conversations/docs |
| **L3 Skill** | Compile knowledge → executable skill programs (Skill/Agent capability) | Ontology "operationalization": concepts/relations → Agent-callable operations | Skill's "generator": knowledge → executable skill compilation pipeline |

## Candidate Projects (14 total)

### L1 Classical Knowledge Compilation (6 projects)

| Project | ⭐ | Language | Role | License |
|---------|-----|----------|------|---------|
| ML-KULeuven/PySDD | 73 | C/Python | SDD Python package, core KC tool | NOASSERTION |
| neuppl/rsdd | 31 | Rust | High-performance Rust SDD compiler | MIT |
| meelgroup/KCBox | 27 | C++ | KC toolbox (model counting+sampling) | MIT |
| april-tools/cirkit | 138 | Python | Probabilistic circuits + tensor networks | GPL-3.0 |
| Tractables/pyjuice | 99 | Python | Scalable probabilistic circuit training & inference | Apache-2.0 |
| SoftVarE-Group/d-dnnf-reasoner | 10 | Rust | d-DNNF reasoner | LGPL-3.0 |

### L2 LLM Knowledge Compilation (5 projects)

| Project | ⭐ | Language | Role | License |
|---------|-----|----------|------|---------|
| Tencent/WeKnora | 14,288 | Go | LLM knowledge platform: docs→RAG+reasoning Agent+self-maintaining Wiki | NOASSERTION |
| Astro-Han/karpathy-llm-wiki | 754 | - | Agent Skills-compatible LLM Wiki builder | MIT |
| nvk/llm-wiki | 367 | Shell | Karpathy-pattern LLM knowledge compilation: multi-Agent→Wiki | MIT |
| axoviq-ai/synthadoc | 236 | Python | LLM KC engine: docs→structured local Wiki | AGPL-3.0 |
| Kromatic-Innovation/athenaeum | 9 | Python | Knowledge management pipeline: passive recall+tiered compilation | Apache-2.0 |

### L3 Skill Compilation (3 projects)

| Project | ⭐ | Language | Role | License |
|---------|-----|----------|------|---------|
| coleam00/claude-memory-compiler | 996 | Python | Conversations→searchable KB, Claude Code memory compilation | - |
| cool-japan/tensorlogic | 39 | Rust | Logic rules→tensor equations, neural/symbolic/probabilistic unified | Apache-2.0 |
| pluck-lang/Pluck.jl | 15 | Julia | Discrete probabilistic programming + lazy KC (PLDI 2025) | Apache-2.0 |

### Probabilistic Circuits Ecosystem (Julia, supplementary)

| Project | ⭐ | Language | Role | License |
|---------|-----|----------|------|---------|
| Tractables/ProbabilisticCircuits.jl | 106 | Julia | Julia probabilistic circuits (Juice library) | Apache-2.0 |
| Tractables/Juice.jl | 12 | Julia | Julia logic+probabilistic circuits unified | Apache-2.0 |

## Cross-Topic Assignment

| Sub-topic | Parent Topics | Rationale |
|-----------|--------------|-----------|
| L1 Classical KC | **本体与语义** | SDD/d-DNNF is core tech for ontology reasoning compilation; OWL→CNF→SDD is the acceleration path |
| L2 LLM KC | **本体与语义** + **工具与资源** | Doc→structured KB is both ontology construction (semantic layer) and tool (knowledge management) |
| L3 Skill KC | **智能体项目** | Knowledge→executable skill is the core compilation pipeline for Agent capability |

## Key Insight: SkillRouter Connection

SkillRouter (arXiv:2603.22455, 74⭐) is directly related to L3 skill compilation:
- **Progressive Disclosure = KC information loss problem**: Compiling by discarding body semantics causes routing failure
- **Skill body = KC's "complete circuit"**: SDD/d-DNNF preserves full inference structure; name+desc is just "circuit labels"
- **False negative filtering = KC's "equivalence detection"**: trigram Jaccard>0.6 and embedding similarity>0.92 filter functionally equivalent skills — same problem as detecting logically equivalent circuits in KC

## Search Strategy Used

1. GitHub Search API: `knowledge compilation`, `SDD`, `d-DNNF`, `probabilistic circuits`, `LLM knowledge compilation`, `skill compilation`
2. Organization repos: `neuppl`, `meelgroup`, `Tractables`
3. HuggingFace models: `pipizhao/SkillRouter-Embedding-0.6B`, `pipizhao/SkillRouter-Reranker-0.6B`
4. Awesome lists: `awesome-mcp-servers` (checked for financial KC connectors — none found)
5. Cross-reference: llm-wiki ecosystem, Claude Code skill ecosystem

## Implementation Status

- [ ] Create 知识编译 sub-topic in github-memory under 本体与语义
- [ ] Register L1+L2 projects under 本体与语义
- [ ] Register L3 projects under 智能体项目
- [ ] Register L2 projects under 工具与资源
- [ ] Update _index.yaml with cross-topic entries
- [ ] Run auto-sync-data.sh
