---
name: deep-research
description: Use when the user needs multi-source research with citation tracking, evidence persistence, and structured report generation. Triggers on "deep research", "comprehensive analysis", "research report", "compare X vs Y", "analyze trends", or "state of the art". Not for simple lookups, debugging, or questions answerable with 1-2 searches.
---

# Deep Research

## Core Purpose

Deliver citation-tracked research reports through a structured pipeline with evidence persistence, source identity management, claim-level verification, and progressive context management.

**Autonomy Principle:** Operate independently. Infer assumptions from context. Only stop for critical errors or incomprehensible queries. Surface high-materiality assumptions explicitly in the Introduction and Methodology rather than silently defaulting.

---

## Decision Tree

```
Request Analysis
+-- Simple lookup? --> STOP: Use WebSearch
+-- Debugging? --> STOP: Use standard tools
+-- Complex analysis needed? --> CONTINUE

Mode Selection
+-- Initial exploration --> quick (3 phases, 2-5 min)
+-- Standard research --> standard (6 phases, 5-10 min) [DEFAULT]
+-- Critical decision --> deep (8 phases, 10-20 min)
+-- Comprehensive review --> ultradeep (8+ phases, 20-45 min)
```

**Default assumptions:** Technical query = technical audience. Comparison = balanced perspective. Trend = recent 1-2 years.

---

## Workflow Overview

| Phase | Name | Quick | Std | Deep | Ultra |
|-------|------|-------|-----|------|-------|
| 1 | SCOPE | Y | Y | Y | Y |
| 2 | PLAN | - | Y | Y | Y |
| 3 | RETRIEVE | Y | Y | Y | Y |
| 4 | TRIANGULATE | - | Y | Y | Y |
| 4.5 | OUTLINE REFINEMENT | - | Y | Y | Y |
| 5 | SYNTHESIZE | - | Y | Y | Y |
| 6 | CRITIQUE | - | - | Y | Y |
| 7 | REFINE | - | - | Y | Y |
| 8 | PACKAGE | Y | Y | Y | Y |

**Note:** Phases 3-5 operate as an evidence loop per section (retrieve → evidence store → refine outline → draft → verify claims → delta-retrieve if needed), not as strict sequential gates.

---

## Execution

**On invocation, load relevant reference files:**

1. **Phase 1-7:** Load [methodology.md](./reference/methodology.md) for detailed phase instructions
2. **Phase 8 (Report):** Load [report-assembly.md](./reference/report-assembly.md) for progressive generation
3. **HTML/PDF output:** Load [html-generation.md](./reference/html-generation.md)
4. **Quality checks:** Load [quality-gates.md](./reference/quality-gates.md)
5. **Long reports (>18K words):** Load [continuation.md](./reference/continuation.md)

**Templates:**
- Report structure: [report_template.md](./templates/report_template.md)
- HTML styling: [mckinsey_report_template.html](./templates/mckinsey_report_template.html)

**Scripts:**
- `python scripts/validate_report.py --report [path]`
- `python scripts/verify_citations.py --report [path]`
- `python scripts/md_to_html.py [markdown_path]`

---

## Output Contract

**Required sections:**
- Executive Summary (200-400 words)
- Introduction (scope, methodology, assumptions)
- Main Analysis (4-8 findings, 600-2,000 words each, cited)
- Synthesis & Insights (patterns, implications)
- Limitations & Caveats
- Recommendations
- Bibliography (COMPLETE - every citation, no placeholders)
- Methodology Appendix

**Output files (all to `~/Documents/[Topic]_Research_[YYYYMMDD]/`):**
- Markdown (primary source of truth)
- `sources.jsonl` — stable source registry with canonical IDs
- `evidence.jsonl` — append-only evidence store with quotes and locators
- `claims.jsonl` — atomic claim ledger with support status
- `run_manifest.json` — query, mode, assumptions, provider config
- HTML (McKinsey style, auto-opened)
- PDF (professional print, auto-opened)

**Quality standards:**
- 10+ sources, 3+ per major claim (cluster-independent, not just count)
- All factual claims cited immediately [N] with evidence backing in `evidence.jsonl`
- Claim-support verification mandatory: no unsupported factual claims pass delivery
- No placeholders, no fabricated citations
- Prose-first (>=80%), bullets sparingly

---

## When to Use / NOT Use

**Use:** Comprehensive analysis, technology comparisons, state-of-the-art reviews, multi-perspective investigation, market analysis.

**Do NOT use:** Simple lookups, debugging, 1-2 search answers, quick time-sensitive queries.

## Sub-Workflows (Consolidated)

### Fact-Checking & Provenance (from fact-check)

Verify information legitimacy and trace provenance chains. Cross-reference claims against multiple sources, assess credibility, detect bias, and auto-register high-value sources.

**Provenance tracing**: Record original_url, author, platform, discovered_via, share_chain. Score provenance quality (1.0=official channel → 0.2=anonymous).

**Cross-reference verification levels**: ✅ Verified (2+ independent sources), ⚠️ Plausible (1 source, no contradiction), ❌ Disputed (sources contradict), 🚫 Unverifiable, 🔴 Retracted.

**Credibility formula**: provenance_quality×0.3 + source_reliability×0.25 + cross_ref_count×0.2 + author_authority×0.15 + recency×0.1

**Bias detection**: Check for single-source dependency, same-platform bias, echo chamber risk. ≥3 diverse sources = healthy coverage.

**Auto-source discovery**: During provenance tracing, auto-register sources with credibility ≥ 0.8 that provide new domain coverage or unique perspective.

**SIFT method**: Stop → Investigate the source → Find better coverage → Trace claims to origin.

### Source Evolution (from source-evolution)

Continuously discover, register, score, and evolve information sources (RSS, media, social accounts, WeChat, API endpoints).

**Core loop**: User shares link → extract URL/author → assess Tier (S/A/B/C/D) → register new source → score and rank → monitor → evolve.

**7-dimension scoring** (0-1): Reliability×0.2, Freshness×0.2, Relevance×0.1, Completeness×0.05, Diversity×0.05, Influence×0.15, QualityRatio×0.15, plus Tier bonus (S+0.2, A+0.1).

**Sink-and-slow mechanism**: Low-scoring sources get progressively less frequent fetches. Consecutive low scores → tier demotion → dormant → dead.

### Survey Knowledge Reconstruction (from survey-knowledge-reconstruction)

Deep knowledge reconstruction from survey papers — extract complete domain knowledge skeleton, build concept maps and evolution trajectories. NOT shallow paper summaries.

**Output format: Dual-track system**:
- **Upper track (Theory)**: Core metaphor → Evolution stages → Dimensional system → Unifying framework → Tradeoff boundaries
- **Lower track (Engineering)**: For each dimension: "Core is not X but Y" positioning → Work goals → Core techniques → Pitfalls (≥2, precisely named) → Best practices (≥3, actionable)

**Key principle**: Every dimension must have a "the core is not X, but Y" representational transformation. Pitfalls with vivid names ("memory poisoning", "retrieval noise", "planning hallucination") are the key differentiator from shallow analysis.

### Paper Analysis (from caveman-analysis)

Session-specific deep analysis of a single paper (CAVEMAN, arXiv 2604.00025). Demonstrates the pattern for paper knowledge reconstruction: basic info → core insights → layered architecture → key results → critical review → research opportunities → capability evolution trajectory.

This analysis was for a specific paper but the METHODOLOGY is reusable: extract layered architecture, identify core insight ("verification is not traversing more neurons but finding causally relevant features and propagating under manifold constraints"), map capability evolution trajectory with transition drivers.

### Tavily CLI Research (from tavily-research)

Quick-start research via the Tavily CLI (`tvly`). Use when you need a fast, citation-backed research report without the full deep-research pipeline.

**Prerequisites**: Install `tvly` CLI: `curl -fsSL https://cli.tavily.com/install.sh | bash && tvly login`

**Quick start**:
```bash
tvly research "competitive landscape of AI code assistants"           # basic (30s)
tvly research "electric vehicle market analysis" --model pro          # comprehensive (60-120s)
tvly research "AI agent frameworks comparison" --stream               # real-time streaming
tvly research "fintech trends 2025" --model pro -o report.md         # save to file
```

**Model selection**: `mini` for single-topic (~30s), `pro` for multi-angle analysis (~60-120s), `auto` for API-chosen.

**Async workflow**: `tvly research "topic" --no-watch --json` → `tvly research status <id>` → `tvly research poll <id>`

**When to use vs full deep-research**: Tavily CLI is for fast, single-query research with built-in citation tracking. Use the full deep-research pipeline when you need multi-phase investigation, evidence persistence, claim verification, and progressive context management across 6-8 phases.

### Knowledge Base System (from knowledge-base)

A 6-stage intelligent knowledge base for multi-source information collection, content analysis, insight generation, and knowledge precipitation. Built in TypeScript with stages: Source Management → Content Analysis → Agent Fission → Validation & Precipitation → Skillization → Evolution Engine.

**Key APIs**: `kb.addSource()`, `kb.collect()`, `kb.analyze()`, `kb.executeFission()`, `kb.startAnalysis()`, `kb.evolve()`

**Use alongside deep-research when**: You need persistent knowledge storage across sessions, multi-source collection with quality scoring, or agent fission for parallel analysis. The knowledge base provides the storage layer that deep-research's evidence store builds on.

**Full architecture and API reference → `references/knowledge-base-system.md`**
