---
name: llm-wiki
description: "Karpathy's LLM Wiki — build and maintain a persistent, interlinked markdown knowledge base with four-layer memory model, knowledge lifecycle management, and multi-agent skill specs."
version: 4.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [wiki, knowledge-base, research, notes, markdown, rag-alternative, lifecycle, memory-model]
    category: research
    related_skills: [obsidian, arxiv, sage-wiki]
    config:
      - key: wiki.path
        description: Path to the LLM Wiki knowledge base directory
        default: "~/wiki"
        prompt: Wiki directory path
---

# Karpathy's LLM Wiki v4

Build and maintain a persistent, compounding knowledge base as interlinked markdown files.
Based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Unlike traditional RAG (which rediscovers knowledge from scratch per query), the wiki
compiles knowledge once and keeps it current. Cross-references are already there.
Contradictions have already been flagged. Synthesis reflects everything ingested.

**v4 upgrades**: Four-layer memory model, knowledge lifecycle with confidence scoring
and Ebbinghaus forgetting curve, typed wikilink relations, incremental compilation
guidance, cost-aware bulk ingest, and sage-wiki interop.

**Division of labor:** The human curates sources and directs analysis. The agent
summarizes, cross-references, files, and maintains consistency.

## When This Skill Activates

Use this skill when the user:
- Asks to create, build, or start a wiki or knowledge base
- Asks to ingest, add, or process a source into their wiki
- Asks a question and an existing wiki is present at the configured path
- Asks to lint, audit, or health-check their wiki
- Asks to build, rebuild, or visualize the knowledge graph
- Asks to manage knowledge lifecycle (refresh, decay, archive stale knowledge)
- References their wiki, knowledge base, or "notes" in a research context

## Wiki Location

Set the wiki path in your Hermes config under the wiki path key (default: `~/wiki`).

The wiki is just a directory of markdown files — open it in Obsidian, VS Code, or
any editor. No database, no special tooling required.

## Architecture: Four Layers + Four Memory Tiers

### Directory Structure

```
wiki/
├── SCHEMA.md           # Layer 3: Conventions, structure rules, domain config
├── .manifest.json      # Incremental compilation state (sha256 per source, output_pages, status)
├── overview.md         # Layer 2: Living synthesis across all sources (updated on every ingest)
├── index.md            # Layer 2: Sectioned content catalog with one-line summaries
├── log.md              # Layer 2: Chronological action log (append-only, rotated yearly)
├── raw/                # Layer 1: Immutable source material
│   ├── articles/       # Web articles, clippings
│   ├── papers/         # PDFs, arxiv papers
│   ├── transcripts/    # Meeting notes, interviews
│   └── assets/         # Images, diagrams referenced by sources
├── sources/            # Layer 2: One summary page per source document
├── entities/           # Layer 2: Entity pages (people, orgs, products, models)
├── concepts/           # Layer 2: Concept/topic pages
├── comparisons/        # Layer 2: Side-by-side analyses
├── queries/            # Layer 2: Filed query results and syntheses worth keeping
├── output/             # Layer 2: Publishable deliverables (blog posts, reports, slides)
└── _archive/           # Layer 2: Superseded pages (not deleted, preserved for provenance)
graph/
├── graph.json          # Layer 4: Node/edge data (SHA256-cached for incremental rebuilds)
└── graph.html          # Layer 4: Interactive vis.js visualization — open in any browser
```

### Structural Layers

**Layer 1 — Raw Sources:** Immutable. The agent reads but never modifies these.
**Layer 2 — The Wiki:** Agent-owned markdown files. Created, updated, and
cross-referenced by the agent. Includes `overview.md`, `index.md`, `log.md`,
and all content directories.
**Layer 3 — The Schema:** `SCHEMA.md` defines structure, conventions, and tag taxonomy.
**Layer 4 — The Graph:** `graph/` contains derived knowledge graph data and visualization.

### Four-Layer Memory Model (v4 NEW)

The wiki organizes knowledge into four cognitive tiers, mirroring human memory:

```
┌─────────────────────────────────────────────────────────┐
│  Procedural    output/*                                  │  Deliverables
│                "How to produce results"                   │  Blog posts, reports, slides
├─────────────────────────────────────────────────────────┤
│  Semantic      wiki/comparisons/ + synthesis sections    │  Cross-source insights
│                "What it means in the bigger picture"      │  Patterns, principles, trade-offs
├─────────────────────────────────────────────────────────┤
│  Episodic      wiki/entities/ + concepts/                │  Structured knowledge
│                "What we know about X"                     │  Facts, relationships, definitions
├─────────────────────────────────────────────────────────┤
│  Working       wiki/sources/ + wiki/summaries/           │  Per-source summaries
│                "What this source says"                    │  Key claims, quotes, connections
└─────────────────────────────────────────────────────────┘
```

**Promotion rules** (knowledge moves up when it meets thresholds):
- **Working → Episodic**: Entity/concept mentioned in **2+ sources** → create dedicated page
- **Episodic → Semantic**: **3+ entities/concepts** interrelate → create comparison/synthesis
- **Semantic → Procedural**: Confidence ≥ 0.85 AND user confirms → suggest publishing to `output/`

**Demotion rules** (knowledge moves down when contradicted):
- Semantic synthesis contradicted by new evidence → demote to Episodic (mark `status: contested`)
- Episodic page superseded → add `superseded_by` frontmatter, move to `_archive/`

## Knowledge Lifecycle (v4 NEW)

Every wiki page has a lifecycle governed by confidence scoring and temporal decay.

### Confidence Scoring

Each page carries a `confidence` field in frontmatter (0.0–1.0):

```yaml
---
title: Flash Attention
confidence: 0.92
confidence_updated: 2026-04-20
---
```

**Confidence rules:**
- New page from single source: `confidence: 0.5`
- Corroborated by 2+ sources: `confidence: 0.7`
- Cross-referenced by 3+ pages: `confidence: 0.85`
- Contradicted by newer source: reduce by 0.2, mark `status: contested`
- User-verified: `confidence: 1.0`

### Ebbinghaus Forgetting Curve

Knowledge decays without reinforcement. The wiki models this:

```
effective_confidence = confidence × e^(-λ × days_since_access)
```

Where λ ≈ 0.003 (half-life ~230 days). Pages accessed recently retain full confidence.

**Reinforcement actions** (reset the decay clock):
- Page is read during a query → reset `last_accessed`
- Page is updated with new information → bump confidence +0.1 (max 1.0)
- Page is cross-referenced from a new source → bump confidence +0.05

### Lifecycle States

```
active → stale → archived
  ↑         │
  └─────────┘  (refreshed)
```

| State | Condition | Action |
|-------|-----------|--------|
| `active` | `effective_confidence ≥ 0.5` | Normal — appears in search and overview |
| `stale` | `effective_confidence < 0.5` | Flagged in lint, excluded from overview synthesis |
| `archived` | Moved to `_archive/` | Removed from index, wikilinks marked "(archived)" |

### Supersession Chain

When knowledge is replaced, track the chain:

```yaml
# Old page
superseded_by: concepts/flash-attention-v2
superseded_date: 2026-04-15

# New page
supersedes: concepts/flash-attention
```

This preserves provenance — you can always trace why knowledge changed.

### Refresh Operation (v4 NEW)

When the user asks to refresh or validate stale knowledge:

1. Identify pages with `effective_confidence < 0.5` (stale threshold)
2. For each stale page, search the web for updates using `web_search`
3. If new information found:
   - Update the page, bump confidence, reset `last_accessed`
   - If contradicted, follow the Update Policy
4. If no new information:
   - Mark `status: stale` in frontmatter
   - If stale for >180 days, suggest archiving
5. Log all refresh actions

## Typed Wikilink Relations (v4 NEW)

Beyond free `[[wikilinks]]`, llm-wiki v4 supports typed relations in frontmatter:

```yaml
relations:
  - target: concepts/transformer-architecture
    type: implements
  - target: concepts/attention-mechanism
    type: extends
  - target: concepts/rnn
    type: supersedes
```

**Standard relation types** (inspired by sage-wiki's ontology):
| Type | Meaning | Example |
|------|---------|---------|
| `implements` | Concrete realization of | GPT implements Transformer |
| `extends` | Builds upon | Flash Attention extends Attention |
| `optimizes` | Improves efficiency of | Flash Attention optimizes Attention |
| `contradicts` | Conflicts with | Paper B contradicts Paper A |
| `cites` | References | GPT-4 cites Scaling Laws |
| `prerequisite_of` | Required before | Python is prerequisite_of PyTorch |
| `trades_off` | Alternative with different trade-offs | RAG trades_off Fine-tuning |
| `derived_from` | Originates from | LoRA derived_from Adapter |
| `supersedes` | Replaces (newer/better) | Flash-2 supersedes Flash-1 |

Typed relations are optional — free `[[wikilinks]]` still work for casual links.
When typed relations exist, the Graph operation uses them for richer visualization.

## Resuming an Existing Wiki (CRITICAL — do this every session)

When the user has an existing wiki, **always orient yourself before doing anything**:

① **Read `SCHEMA.md`** — understand the domain, conventions, and tag taxonomy.
② **Read `overview.md`** — get the living synthesis of all knowledge so far.
③ **Read `index.md`** — learn what pages exist and their summaries.
④ **Scan recent `log.md`** — read the last 20-30 entries to understand recent activity.

```bash
WIKI="${wiki_path:-$HOME/wiki}"
read_file "$WIKI/SCHEMA.md"
read_file "$WIKI/overview.md"
read_file "$WIKI/index.md"
read_file "$WIKI/log.md" offset=<last 30 lines>
```

Only after orientation should you ingest, query, or lint. This prevents:
- Creating duplicate pages for entities that already exist
- Missing cross-references to existing content
- Contradicting the schema's conventions
- Repeating work already logged

For large wikis (100+ pages), also run a quick `search_files` for the topic
at hand before creating anything new.

## Initializing a New Wiki

When the user asks to create or start a wiki:

1. Determine the wiki path (from config, env var, or ask the user; default `~/wiki`)
2. Create the directory structure above
3. Ask the user what domain the wiki covers — be specific
4. Write `SCHEMA.md` customized to the domain (see template below)
5. Write initial `overview.md` with domain description
6. Write initial `index.md` with sectioned header
7. Write initial `log.md` with creation entry
8. Confirm the wiki is ready and suggest first sources to ingest

### SCHEMA.md Template

Adapt to the user's domain. The schema constrains agent behavior and ensures consistency:

```markdown
# Wiki Schema

## Domain
[What this wiki covers — e.g., "AI/ML research", "personal health", "startup intelligence"]

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `transformer-architecture.md`)
- Every wiki page starts with YAML frontmatter (see below)
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be appended to `log.md`

## Frontmatter
  ```yaml
  ---
  title: Page Title
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  type: source | entity | concept | comparison | query
  tags: [from taxonomy below]
  sources: [raw/articles/source-name.md]
  confidence: 0.0-1.0
  confidence_updated: YYYY-MM-DD
  last_accessed: YYYY-MM-DD
  status: active | stale | archived
  superseded_by: [page-path] (optional)
  supersedes: [page-path] (optional)
  relations: (optional)
    - target: [page-path]
      type: implements | extends | optimizes | contradicts | cites | prerequisite_of | trades_off | derived_from | supersedes
  ---
  ```

## Tag Taxonomy
[Define 10-20 top-level tags for the domain. Add new tags here BEFORE using them.]

Example for AI/ML:
- Models: model, architecture, benchmark, training
- People/Orgs: person, company, lab, open-source
- Techniques: optimization, fine-tuning, inference, alignment, data
- Meta: comparison, timeline, controversy, prediction

Rule: every tag on a page must appear in this taxonomy. If a new tag is needed,
add it here first, then use it. This prevents tag sprawl.

## Page Thresholds
- **Create a page** when an entity/concept appears in 2+ sources OR is central to one source
- **Add to existing page** when a source mentions something already covered
- **DON'T create a page** for passing mentions, minor details, or things outside the domain
- **Split a page** when it exceeds ~200 lines — break into sub-topics with cross-links
- **Archive a page** when its content is fully superseded — move to `_archive/`, remove from index

## Source Pages
One page per source document in `sources/`. Include:
- Summary (2-4 sentences)
- Key claims (bullet list)
- Key quotes (blockquotes with context)
- Connections to entities and concepts ([[wikilinks]])
- Contradictions with other sources (if any)

## Entity Pages
One page per notable entity. Include:
- Overview / what it is
- Key facts and dates
- Relationships to other entities ([[wikilinks]])
- Source references

## Concept Pages
One page per concept or topic. Include:
- Definition / explanation
- Current state of knowledge
- Open questions or debates
- Related concepts ([[wikilinks]])

## Comparison Pages
Side-by-side analyses. Include:
- What is being compared and why
- Dimensions of comparison (table format preferred)
- Verdict or synthesis
- Sources

## Update Policy
When new information conflicts with existing content:
1. Check the dates — newer sources generally supersede older ones
2. If genuinely contradictory, note both positions with dates and sources
3. Mark the contradiction in frontmatter: `contradictions: [page-name]`
4. Reduce confidence by 0.2 on the contradicted page
5. Flag for user review in the lint report
```

### index.md Template

The index is sectioned by type. Each entry is one line: wikilink + summary.

```markdown
# Wiki Index

> Content catalog. Every wiki page listed under its type with a one-line summary.
> Read this first to find relevant pages for any query.
> Last updated: YYYY-MM-DD | Total pages: N

## Overview
- [Overview](overview.md) — living synthesis

## Sources
- [Source Title](sources/slug.md) — one-line summary

## Entities
<!-- Alphabetical within section -->

## Concepts

## Comparisons

## Queries
- [Analysis Title](queries/slug.md) — what question it answers
```

**Scaling rule:** When any section exceeds 50 entries, split it into sub-sections
by first letter or sub-domain. When the index exceeds 200 entries total, create
a `_meta/topic-map.md` that groups pages by theme for faster navigation.

### log.md Template

```markdown
# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete, graph, refresh
> When this file exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.

## [YYYY-MM-DD] create | Wiki initialized
- Domain: [domain]
- Structure created with SCHEMA.md, overview.md, index.md, log.md
```

### overview.md Template

The overview is a **living synthesis** — a single page that summarizes the current state of
knowledge across all sources. It is revised on every ingest to reflect new information,
contradictions, and evolving understanding. Think of it as the wiki's "executive summary."

```markdown
# Wiki Overview

> Living synthesis of all knowledge in this wiki.
> Updated on every ingest. Read this for a quick picture of what the wiki knows.
> Last updated: YYYY-MM-DD | Sources ingested: N | Total pages: N

## Domain
[What this wiki covers — one sentence]

## Current State of Knowledge
[2-4 paragraphs synthesizing the most important findings across all sources.
This is NOT a list — it's a narrative that connects the dots between entities,
concepts, and comparisons. Revise on every ingest to keep it current.]

## Key Themes
- [Theme 1]: [one-line summary with [[wikilinks]] to relevant pages]
- [Theme 2]: [one-line summary with [[wikilinks]] to relevant pages]

## Open Questions
- [Question the wiki cannot yet answer — suggests sources to ingest]

## Contradictions
- [Conflicting claims across sources — link to pages with [[wikilinks]]]
```

**Scaling rule:** When the overview exceeds 200 lines, split into sub-sections by
topic area. Keep it scannable — this is the first thing read in every session.

## Core Operations

### 1. Ingest

When the user provides a source (URL, file, paste), integrate it into the wiki:

① **Capture the raw source:**
   - URL → use `web_extract` to get markdown, save to `raw/articles/`
   - PDF → use `web_extract` (handles PDFs), save to `raw/papers/`
   - Pasted text → save to appropriate `raw/` subdirectory
   - Name the file descriptively: `raw/articles/karpathy-llm-wiki-2026.md`

② **Discuss takeaways** with the user — what's interesting, what matters for
   the domain. (Skip this in automated/cron contexts — proceed directly.)

③ **Check what already exists** — search index.md and use `search_files` to find
   existing pages for mentioned entities/concepts. This is the difference between
   a growing wiki and a pile of duplicates.

④ **Write or update wiki pages** (following the Four-Layer Memory Model):
    - **Working Memory →** Write `sources/<slug>.md` — a structured summary of the source
      with key claims, quotes, connections, and contradictions. Set `confidence: 0.5`.
    - **Episodic Memory →** New entities/concepts: Create pages only if they meet the
      Page Thresholds (2+ source mentions, or central to one source). Set `confidence: 0.7`.
    - **Existing pages →** Add new information, update facts, bump `updated` date.
      When new info contradicts existing content, follow the Update Policy.
    - **Cross-reference →** Every new or updated page must link to at least 2 other
      pages via `[[wikilinks]]`. Check that existing pages link back.
    - **Tags →** Only use tags from the taxonomy in SCHEMA.md
    - **Relations →** Add typed relations where the connection is semantically clear
      (e.g., `type: implements`, `type: extends`)

⑤ **Update navigation:**
    - Add new pages to `index.md` under the correct section, alphabetically
    - Update the "Total pages" count and "Last updated" date in index header
    - **Revise `overview.md`** — update the living synthesis to reflect new information,
      themes, contradictions, and open questions. This is critical — the overview is the
      first thing read in every session.
    - Append to `log.md`: `## [YYYY-MM-DD] ingest | Source Title`
    - List every file created or updated in the log entry

⑥ **Report what changed** — list every file created or updated to the user.

A single source can trigger updates across 5-15 wiki pages. This is normal
and desired — it's the compounding effect.

### 2. Query

When the user asks a question about the wiki's domain:

① **Read `index.md`** to identify relevant pages.
② **For wikis with 100+ pages**, also `search_files` across all `.md` files
   for key terms — the index alone may miss relevant content.
③ **Read the relevant pages** using `read_file`.
④ **Check confidence** — prefer pages with `confidence ≥ 0.7`. Flag low-confidence
   answers: "Note: this is based on low-confidence knowledge (0.4)."
⑤ **Synthesize an answer** from the compiled knowledge. Cite the wiki pages
   you drew from: "Based on [[page-a]] and [[page-b]]..."
⑥ **File valuable answers back** — if the answer is a substantial comparison,
    deep dive, or novel synthesis, create a page in `queries/` or `comparisons/`.
    Don't file trivial lookups — only answers that would be painful to re-derive.
    Ask the user if they want the answer saved before filing.
⑦ **Update log.md** with the query and whether it was filed.
⑧ **Reset `last_accessed`** on all pages read during the query (reinforces confidence).

### 3. Lint

When the user asks to lint, health-check, or audit the wiki:

① **Orphan pages:** Find pages with no inbound `[[wikilinks]]` from other pages.
```python
# Use execute_code for this — programmatic scan across all wiki pages
import os, re
from collections import defaultdict
wiki = "<WIKI_PATH>"

# CRITICAL: Use the same wikilink regex as broken-link check
# Handles both [[path]] and [[path|display alias]], plus escaped pipes [[path\|display]]
WIKILINK_RE = re.compile(r'\[\[([^\]|]+?)(?:\s*\\?\|[^\]]+)?\]\]')

inbound = defaultdict(list)  # target_page -> [source_pages]
all_pages = set()

# Build page lookup (supports both with/without .md extension)
page_lookup = {}

# Scan all .md files (exclude raw/ and _archive/)
for root, dirs, files in os.walk(wiki):
    if '/raw/' in root or '/_archive/' in root: continue
    for f in files:
        if not f.endswith('.md'): continue
        filepath = os.path.join(root, f)
        rel = os.path.relpath(filepath, wiki)
        all_pages.add(rel)
        page_lookup[rel] = rel
        if rel.endswith('.md'):
            page_lookup[rel[:-3]] = rel
        content = open(filepath).read()
        for m in WIKILINK_RE.finditer(content):
            target = m.group(1).strip().rstrip('\\')
            inbound[target].append(rel)

# Pages with zero inbound links are orphans
# Resolve: a page is orphaned if NO wikilink target resolves to it
resolved_inbound = set()
for target in inbound:
    if target in page_lookup:
        resolved_inbound.add(page_lookup[target])

orphans = [p for p in all_pages if p not in resolved_inbound and p not in ('SCHEMA.md', 'index.md', 'log.md')]
```

② **Broken wikilinks:** Find `[[links]]` that point to pages that don't exist.
Use a proper wikilink parser — **never use simple grep** which mishandles alias syntax:
```python
# Use execute_code for this — correct wikilink extraction
import os, re
from collections import defaultdict
wiki = "<WIKI_PATH>"

# CRITICAL: This regex correctly handles BOTH [[path]] and [[path|display alias]]
# The simple grep approach splits on | and treats the alias as a separate link → false positives
# Also handles escaped pipes in markdown tables: [[path\|display]] → path (strip trailing backslash)
WIKILINK_RE = re.compile(r'\[\[([^\]|]+?)(?:\s*\\?\|[^\]]+)?\]\]')

all_links = defaultdict(list)  # target -> [source_files]
all_pages = set()

# 1. Collect all existing wiki pages (exclude raw/)
for root, dirs, files in os.walk(wiki):
    if '/raw/' in root or '/_archive/' in root: continue
    for f in files:
        if f.endswith('.md'):
            rel = os.path.relpath(os.path.join(root, f), wiki)
            all_pages.add(rel)

# 2. Build a lookup that supports both with/without .md extension
#    [[concepts/foo]] should match concepts/foo.md
page_lookup = {}
for p in all_pages:
    page_lookup[p] = p
    if p.endswith('.md'):
        page_lookup[p[:-3]] = p  # concepts/foo → concepts/foo.md

# 3. Extract wikilinks from all pages
for root, dirs, files in os.walk(wiki):
    if '/raw/' in root: continue
    for f in files:
        if not f.endswith('.md'): continue
        filepath = os.path.join(root, f)
        content = open(filepath).read()
        for m in WIKILINK_RE.finditer(content):
            target = m.group(1).strip().rstrip('\\')  # Strip trailing backslash from escaped pipes
            source = os.path.relpath(filepath, wiki)
            all_links[target].append(source)

# 4. Find broken links (target not in page_lookup)
broken = {t: srcs for t, srcs in all_links.items() if t not in page_lookup}
# Report broken links with source file locations
```

③ **Index completeness:** Every wiki page should appear in `index.md`. Compare
   the filesystem against index entries.

④ **Frontmatter validation:** Every wiki page must have all required fields
   (title, created, updated, type, tags, sources, confidence, status). Tags must be in the taxonomy.

⑤ **Stale content:** Pages whose `effective_confidence < 0.5` (considering
   Ebbinghaus decay). Flag for refresh.

⑥ **Contradictions:** Pages on the same topic with conflicting claims. Look for
   pages that share tags/entities but state different facts.

⑦ **Page size:** Flag pages over 200 lines — candidates for splitting.

⑧ **Tag audit:** List all tags in use, flag any not in the SCHEMA.md taxonomy.

⑨ **Log rotation:** If log.md exceeds 500 entries, rotate it.

⑩ **Overview staleness:** Check if `overview.md` reflects the most recent ingest.
    If sources were ingested but overview wasn't updated, flag it.

⑪ **Missing source pages:** If a raw document in `raw/` has no corresponding
    summary page in `sources/`, flag it.

⑫ **Supersession chains:** Verify `superseded_by`/`supersedes` are bidirectional.
    If page A says `superseded_by: B`, then B should say `supersedes: A`.

⑬ **Confidence drift:** Pages with `confidence < 0.3` that are still `status: active`.
    These should be marked `stale` or archived.

⑭ **Report findings** with specific file paths and suggested actions, grouped by
    severity (broken links > orphans > stale content > style issues).

⑮ **Append to log.md:** `## [YYYY-MM-DD] lint | N issues found`

### 4. Graph

When the user asks to build, rebuild, or visualize the knowledge graph:

① **Extract wikilinks** — scan all `.md` files in the wiki for `[[wikilinks]]`.
    Build a nodes list (one per page) and an edges list (one per wikilink), tagged `EXTRACTED`.

② **Extract typed relations** — read `relations` from frontmatter. These get
    their own edge type matching the relation type (implements, extends, etc.).

③ **Infer implicit relationships** — identify semantic connections between pages not
    captured by explicit wikilinks or typed relations. Tag these `INFERRED` with a
    confidence score (0.0–1.0). Low-confidence relationships (< 0.7) get tagged
    `AMBIGUOUS` instead.

④ **Build `graph/graph.json`:**
    ```json
    {
      "nodes": [{"id": "entities/OpenAI", "label": "OpenAI", "type": "entity", "color": "#2196F3", "confidence": 0.92}],
      "edges": [{"from": "entities/OpenAI", "to": "concepts/RLHF", "type": "EXTRACTED", "confidence": 1.0}],
      "built": "YYYY-MM-DD"
    }
    ```

⑤ **Build `graph/graph.html`** — a self-contained vis.js visualization:
     - Nodes colored by type (entity=blue, concept=orange, source=green, query=purple)
     - Node size reflects confidence (higher confidence = larger node)
     - Edges colored by type (EXTRACTED=gray, INFERRED=red, typed relations=blue, AMBIGUOUS=light gray)
    - Interactive: click nodes for details, search to filter, drag to rearrange
    - Community detection (Louvain algorithm) clusters related topics
    - Stale nodes (`effective_confidence < 0.5`) shown with dashed borders

⑥ **Incremental rebuilds** — cache SHA256 hashes of each page. Only reprocess pages
    that changed since the last graph build. This makes rebuilds fast for large wikis.

⑦ **Report** — node count, edge count, breakdown by type, and the most connected
    nodes (hubs). These hubs reveal the wiki's central topics.

⑧ **Append to log.md:** `## [YYYY-MM-DD] graph | Knowledge graph rebuilt`

**Node type colors** (consistent with SCHEMA.md frontmatter types):
| Type | Color | Hex |
|------|-------|-----|
| source | green | `#4CAF50` |
| entity | blue | `#2196F3` |
| concept | orange | `#FF9800` |
| comparison | teal | `#009688` |
| query | purple | `#9C27B0` |

### 5. Refresh (v4 NEW)

When the user asks to refresh, validate, or update stale knowledge:

① **Identify stale pages** — scan frontmatter for `effective_confidence < 0.5`:
```python
# Use execute_code for this
import os, yaml, math, datetime
wiki = "<WIKI_PATH>"
stale_pages = []
for root, dirs, files in os.walk(wiki):
    for f in files:
        if not f.endswith('.md'): continue
        # Parse frontmatter, compute effective_confidence
        # = confidence * exp(-0.003 * days_since_last_accessed)
        # If < 0.5, add to stale_pages
```

② **For each stale page**, search the web for updates:
   - Use `web_search` with key terms from the page
   - If new information found, update the page and bump confidence
   - If contradicted, follow the Update Policy

③ **Auto-archive** pages stale for >180 days with no new information

④ **Report** which pages were refreshed, archived, or still stale

⑤ **Append to log.md:** `## [YYYY-MM-DD] refresh | N refreshed, N archived`

## Working with the Wiki

### Searching

```bash
# Find pages by content
search_files "transformer" path="$WIKI" file_glob="*.md"

# Find pages by filename
search_files "*.md" target="files" path="$WIKI"

# Find pages by tag
search_files "tags:.*alignment" path="$WIKI" file_glob="*.md"

# Find stale pages (low confidence)
search_files "confidence: 0\\.[0-3]" path="$WIKI" file_glob="*.md"

# Recent activity
read_file "$WIKI/log.md" offset=<last 20 lines>
```

### Bulk Ingest (Cost-Aware)

When ingesting multiple sources at once, batch the updates:

1. **Estimate cost first** — each source requires ~2-3 LLM calls (summarize + extract + cross-ref).
   For 10+ sources, warn the user about token cost before proceeding.
2. Read all sources first
3. Write source summary pages for each one
4. Identify all entities and concepts across all sources
5. Check existing pages for all of them (one search pass, not N)
6. Create/update pages in one pass (avoids redundant updates)
7. Update overview.md once at the end
8. Update index.md once at the end
9. Write a single log entry covering the batch

**Cost control tips:**
- For 20+ sources, consider splitting into batches of 10
- Skip "discuss takeaways" step in bulk mode
- Use `search_files` once for all entities rather than per-source
- Defer graph rebuild until after the full batch is ingested

### Incremental Compilation (v4 — Manifest-Based Diff)

**Problem:** Re-processing all sources on every ingest is wasteful. For wikis with 100+ pages,
a single new source shouldn't trigger re-reading and re-summarizing everything.

**Solution:** A `.manifest.json` file tracks which sources have been compiled, enabling true
incremental processing — only new or changed sources get processed.

#### Manifest File: `.manifest.json`

Located at the wiki root. Tracks compilation state per source file:

```json
{
  "version": 1,
  "last_compiled": "2026-04-20T22:30:00Z",
  "entries": {
    "raw/articles/karpathy-llm-wiki-2026.md": {
      "sha256": "a1b2c3d4...",
      "compiled_at": "2026-04-20T22:30:00Z",
      "output_pages": ["sources/karpathy-llm-wiki.md", "entities/llm-wiki.md"],
      "status": "compiled"
    },
    "raw/articles/new-paper-2026.md": {
      "sha256": "e5f6g7h8...",
      "compiled_at": null,
      "output_pages": [],
      "status": "pending"
    }
  }
}
```

#### Incremental Ingest Flow

When ingesting, follow this diff-based flow instead of reprocessing everything:

① **Load manifest** — read `.manifest.json` from wiki root. If missing, create empty manifest
(first-time ingest = full compilation, which is correct).

② **Scan raw/ directory** — list all source files in `raw/` subdirectories.

③ **Compute diff** — for each source file:
```python
import hashlib, json, os

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def diff_sources(wiki_path, manifest):
    """Returns (new_files, changed_files, removed_files, unchanged_files)"""
    current = {}
    for root, dirs, files in os.walk(os.path.join(wiki_path, 'raw')):
        for f in files:
            if f.startswith('.'): continue
            filepath = os.path.join(root, f)
            rel = os.path.relpath(filepath, wiki_path)
            current[rel] = compute_sha256(filepath)

    entries = manifest.get('entries', {})
    new_files = [f for f in current if f not in entries]
    changed_files = [f for f in current if f in entries and entries[f]['sha256'] != current[f]]
    removed_files = [f for f in entries if f not in current]
    unchanged_files = [f for f in current if f in entries and entries[f]['sha256'] == current[f]]

    return new_files, changed_files, removed_files, unchanged_files
```

④ **Process only new + changed files** — skip `unchanged_files` entirely:
   - **New files**: Full ingest flow (summarize → create/update pages → cross-reference)
   - **Changed files**: Re-process the source, update existing output pages, bump `updated` dates
   - **Removed files**: Flag their output pages as potentially stale (reduce confidence by 0.1)
   - **Unchanged files**: Skip completely — no reads, no LLM calls

⑤ **Update manifest** after processing each file:
```python
def update_manifest(manifest, rel_path, sha256, output_pages):
    manifest['entries'][rel_path] = {
        'sha256': sha256,
        'compiled_at': datetime.utcnow().isoformat() + 'Z',
        'output_pages': output_pages,
        'status': 'compiled'
    }
    manifest['last_compiled'] = datetime.utcnow().isoformat() + 'Z'
```

⑥ **Update navigation once** — after the entire batch is processed (not per-file):
   - Update `overview.md` once
   - Update `index.md` once
   - Write single `log.md` entry

#### When to Use Full vs Incremental

| Condition | Mode | Reason |
|-----------|------|--------|
| First ingest (no manifest) | Full | No baseline to diff against |
| Manifest exists, 1-5 new sources | Incremental | Only process the new ones |
| Manifest exists, 10+ new sources | Incremental + batch | Process in batches, update nav once |
| Schema changed (SCHEMA.md updated) | Full | Conventions may affect all pages |
| User explicitly requests `--full` | Full | User override |

#### Integration with Existing Ingest Flow

The incremental manifest wraps around the existing ingest steps — it doesn't replace them.
Steps ①-⑥ from the Ingest section still apply, but only for the files identified by the diff.
The key change is: **before step ① of Ingest, run the diff to determine scope**.

```
Ingest (with incremental):
  → Load manifest
  → Diff sources
  → For each new/changed source:
      → Capture raw (skip if already in raw/)
      → Discuss takeaways (skip in bulk/cron mode)
      → Check existing pages
      → Write/update wiki pages
      → Update manifest entry
  → Update navigation (once)
  → Report changes
```

### Archiving

When content is fully superseded or the domain scope changes:
1. Create `_archive/` directory if it doesn't exist
2. Move the page to `_archive/` with its original path (e.g., `_archive/entities/old-page.md`)
3. Remove from `index.md`
4. Update any pages that linked to it — replace wikilink with plain text + "(archived)"
5. Set `superseded_by` on the archived page pointing to the replacement
6. Set `supersedes` on the replacement page pointing to the archived page
7. Log the archive action

### Obsidian Integration

The wiki directory works as an Obsidian vault out of the box:
- `[[wikilinks]]` render as clickable links
- Graph View visualizes the knowledge network
- YAML frontmatter powers Dataview queries
- The `raw/assets/` folder holds images referenced via `![[image.png]]`

For best results:
- Set Obsidian's attachment folder to `raw/assets/`
- Enable "Wikilinks" in Obsidian settings (usually on by default)
- Install Dataview plugin for queries like `TABLE tags FROM "entities" WHERE contains(tags, "company")`

If using the Obsidian skill alongside this one, set `OBSIDIAN_VAULT_PATH` to the
same directory as the wiki path.

For headless/server sync, use Obsidian Sync or any file sync tool (rsync, Syncthing, etc.)
to keep the wiki directory synchronized across devices.

## Interop with sage-wiki (v4 NEW)

llm-wiki and sage-wiki can coexist and complement each other:

| Scenario | Use llm-wiki | Use sage-wiki |
|----------|-------------|---------------|
| Personal research notes | ✅ Obsidian-native | ❌ Overkill |
| Large-scale knowledge base (10K+ docs) | ❌ No search optimization | ✅ Hybrid BM25+vector |
| MCP agent memory | ❌ No MCP server | ✅ Built-in MCP |
| Knowledge lifecycle management | ✅ Confidence + decay | ❌ Tier-based only |
| Visual diagrams | ✅ Canvas/Excalidraw/Mermaid | ❌ Force-directed only |
| Cost control | ❌ None | ✅ Estimate + Batch + Tiered |

**Bridge pattern**: Use sage-wiki for compilation and search, llm-wiki for lifecycle
management and visualization. Point both at the same `raw/` directory.

**Export to sage-wiki**: When a wiki grows beyond 1K pages, consider running
`sage-wiki init --vault` on the same directory to add hybrid search and MCP
capabilities while keeping the Obsidian-compatible structure.

## Pitfalls

- **Never modify files in `raw/`** — sources are immutable. Corrections go in wiki pages.
- **Always orient first** — read SCHEMA + overview + index + recent log before any operation in a new session.
  Skipping this causes duplicates and missed cross-references.
- **Always update overview.md, index.md and log.md** — skipping this makes the wiki degrade. These are the
  navigational backbone.
- **Don't create pages for passing mentions** — follow the Page Thresholds in SCHEMA.md. A name
  appearing once in a footnote doesn't warrant an entity page.
- **Don't create pages without cross-references** — isolated pages are invisible. Every page must
  link to at least 2 other pages.
- **Frontmatter is required** — it enables search, filtering, staleness detection, and lifecycle management.
- **Tags must come from the taxonomy** — freeform tags decay into noise. Add new tags to SCHEMA.md
  first, then use them.
- **Keep pages scannable** — a wiki page should be readable in 30 seconds. Split pages over
  200 lines. Move detailed analysis to dedicated deep-dive pages.
- **Ask before mass-updating** — if an ingest would touch 10+ existing pages, confirm
  the scope with the user first.
- **Rotate the log** — when log.md exceeds 500 entries, rename it `log-YYYY.md` and start fresh.
  The agent should check log size during lint.
- **Handle contradictions explicitly** — don't silently overwrite. Note both claims with dates,
  mark in frontmatter, reduce confidence, flag for user review.
- **Always update overview.md on ingest** — the overview is the wiki's executive summary.
  If it falls behind, every new session starts with an incomplete picture.
- **Graph rebuilds are incremental** — use SHA256 caching to avoid reprocessing unchanged pages.
  Full rebuilds on large wikis are expensive.
- **Confidence decays** — without reinforcement (reads, updates, cross-references), knowledge
  confidence drops over time. Run `refresh` periodically to validate stale knowledge.
- **Supersession chains must be bidirectional** — always set both `superseded_by` and `supersedes`.
- **Cost awareness for bulk ingest** — each source costs ~2-3 LLM calls. Warn users before
  ingesting 20+ sources at once.
