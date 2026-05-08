# Cross-Topic Sub-Topic Research Methodology

> Established 2026-05-07 from "knowledge compilation" sub-topic investigation session.
> When user identifies a concept that spans multiple github-memory topics, use this methodology.

## When to Use

User says something like:
- "X is both a technology for Y and Z, needs a sub-topic under multiple topics"
- "X is the underlying technology for both [topic A] and [topic B]"
- "X should be categorized under multiple existing topics"

## Methodology (5 Steps)

### Step 1: Decompose the Concept into Layers
Break the concept into 2-4 layers by abstraction level or application domain.
- Example: "Knowledge Compilation" → L1 (classic/academic), L2 (LLM-era application), L3 (skill/agent compilation)
- Each layer should have a clear boundary and distinct project ecosystem

### Step 2: Systematic GitHub Search per Layer
For each layer, run targeted searches:
1. **Core concept search**: `q="knowledge compilation"` → sort by stars
2. **Key algorithm/tool search**: `q="SDD OR d-DNNF OR OBDD"` → find classic implementations
3. **Modern application search**: `q="knowledge compilation LLM"` → find LLM-era projects
4. **Cross-domain search**: `q="skill compilation agent"` → find agent-related projects
5. **Ecosystem search**: Check org repos (e.g., meelgroup, neuppl, Tractables) for related tools
6. **Awesome list search**: `q="awesome knowledge compilation"` → curated lists (often none exist for niche domains)

**Pitfall**: GitHub search for niche academic topics returns lots of noise (e.g., "knowledge compilation" returns Makefile tutorials). Filter by checking description for domain-specific terms (SDD, d-DNNF, circuit, tractable).

**Pitfall**: GitHub API rate limits (10 req/min unauthenticated). Use 12-15s delays between queries, or batch queries.

### Step 3: Verify and Enrich Each Project
For each candidate project:
1. Check `stargazers_count`, `language`, `license`, `description`, `topics`
2. Read README (first 500 chars) to verify project actually does what the search suggests
3. Check if project is already in github-memory (dedup)
4. Note license issues (GPL-3.0, AGPL-3.0, NOASSERTION)

### Step 4: Assign Cross-Topic Mapping
Map each layer to existing github-memory topics:

| Layer | Primary Topic | Secondary Topic | Rationale |
|-------|--------------|-----------------|-----------|
| L1 classic | 本体与语义 | AI基础设施 | Core reasoning compilation for ontology/logic |
| L2 LLM-era | 本体与语义 | 工具与资源 | Knowledge base construction + knowledge management tools |
| L3 skill/agent | 智能体项目 | - | Skill compilation for agent capability |

### Step 5: Present Proposal with Project Tables
For each layer, present a table with: project, stars, language, positioning, license.
Include cross-topic assignment table and rationale.

## Knowledge Compilation Domain Knowledge (2026-05-07)

### 3-Layer Framework

**L1 Classic Knowledge Compilation** — Compile logical formulas into tractable circuits (SDD/d-DNNF/OBDD) for polynomial-time inference.
- Core insight: NP-hard logical reasoning → compile once, query many times in P-time
- Relation to ontology: OWL → CNF → SDD/d-DNNF is the reasoning acceleration path
- Key projects: PySDD(73⭐), rsdd(31⭐), KCBox(27⭐), cirkit(138⭐), pyjuice(99⭐), d-dnnf-reasoner(10⭐)

**L2 LLM Knowledge Compilation** — Compile unstructured documents into structured knowledge bases (wikis, knowledge graphs).
- Core insight: Raw docs → structured, queryable knowledge → RAG alternative
- Relation to ontology: Automatic ontology population from documents
- Key projects: WeKnora(14K⭐), karpathy-llm-wiki(754⭐), llm-wiki(367⭐), synthadoc(236⭐), athenaeum(9⭐)

**L3 Skill Compilation** — Compile knowledge into executable agent skills/programs.
- Core insight: Knowledge → executable capability, conversation → searchable skill
- Relation to ontology: Ontology concepts → agent-callable operations
- Key projects: claude-memory-compiler(996⭐), tensorlogic(39⭐), Pluck.jl(15⭐)

### Key Insight: Progressive Disclosure = Knowledge Compilation Information Loss
SkillRouter (arXiv:2603.22455, Alibaba, 74⭐) proved that progressive disclosure (exposing only name+desc, hiding body) causes 31-44pp accuracy drop in skill routing. This is isomorphic to knowledge compilation's core problem: compiling away information (body → metadata) loses critical distinguishing signal. The 91.7% attention on body proves the "full circuit" is needed, not just its "label".

### Probabilistic Circuits Ecosystem (Julia)
- ProbabilisticCircuits.jl (106⭐, Apache-2.0) — Julia PC from Juice library
- Juice.jl (12⭐, Apache-2.0) — Logic + probabilistic circuits unified
- pyjuice (99⭐, Apache-2.0) — Python scalable PC training/inference
- cirkit (138⭐, GPL-3.0) — Python PC + tensor network framework

### Classic KC Tools (mostly academic, low stars)
- PySDD (73⭐) — Python SDD package, Cython wrapper
- rsdd (31⭐) — Rust SDD, performant and safe
- KCBox (27⭐) — C++ KC toolbox (model counting + uniform sampling)
- d-dnnf-reasoner (10⭐) — Rust d-DNNF reasoner for feature models
- BellaCompiler (6⭐) — Knowledge compiler for wDNNF/pwDNNF/nwDNNF/sd-DNNF

### Cross-Topic Assignment Decision
- L1 projects → 本体与语义 (primary), AI基础设施 (secondary)
- L2 projects → 本体与语义 (primary), 工具与资源 (secondary)
- L3 projects → 智能体项目 (primary)
- SkillRouter → 智能体项目 (skill routing is agent infrastructure)
