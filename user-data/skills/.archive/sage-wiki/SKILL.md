---
name: sage-wiki
description: "sage-wiki — LLM-compiled personal knowledge base engine. Compile sources into structured, interlinked wiki with hybrid search, ontology graph, and MCP integration."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [wiki, knowledge-base, compiler, mcp, ontology, hybrid-search, sage]
    category: research
    related_skills: [llm-wiki, obsidian, arxiv]
    config:
      - key: sage-wiki.path
        description: Path to the sage-wiki project directory
        default: "~/sage-wiki"
        prompt: sage-wiki project directory
      - key: sage-wiki.api_provider
        description: LLM provider (anthropic, openai, gemini, ollama, openai-compatible, qwen)
        default: "gemini"
        prompt: LLM provider for compilation
---

# sage-wiki — LLM-Compiled Knowledge Base Engine

An implementation of [Karpathy's LLM Wiki idea](https://x.com/karpathy/status/2039805659525644595) as a **Go binary compiler**. Drop in your papers, articles, and notes — sage-wiki compiles them into a structured, interlinked wiki with concepts extracted, cross-references discovered, and everything searchable.

**Key differentiator from llm-wiki**: sage-wiki is a **compiled engine** with SQLite+FTS5+vector storage, tiered compilation pipeline, hybrid BM25+vector search, typed ontology graph, and MCP server. llm-wiki is a pure Markdown skill spec executed by LLM agents.

## When This Skill Activates

Use this skill when the user:
- Asks to compile, build, or process a knowledge base with sage-wiki
- Wants to search or query an existing sage-wiki project
- Wants to start an MCP server for their sage-wiki
- Mentions sage-wiki specifically
- Wants a production-grade, scalable knowledge base (1000+ documents)
- Needs MCP integration for agent memory

## Prerequisites

### Installation

```bash
# Requires Go 1.24+
go install github.com/xoai/sage-wiki/cmd/sage-wiki@latest

# Binary installed at ~/go/bin/sage-wiki
# Add to PATH: export PATH=$PATH:$HOME/go/bin
```

### Verify

```bash
sage-wiki --help
sage-wiki doctor  # Validate config and connectivity
```

### API Key

sage-wiki requires an LLM API key. Supported providers:
- **Gemini** (recommended, cheapest): `GEMINI_API_KEY`
- **Anthropic**: `ANTHROPIC_API_KEY`
- **OpenAI**: `OPENAI_API_KEY`
- **Ollama** (free, local): No key needed
- **OpenAI-compatible** (OpenRouter, etc.): Set `base_url` in config
- **Qwen** (DashScope): `DASHSCOPE_API_KEY`

## Project Location

Set the project path in your Hermes config under `skills.config.sage-wiki.path` (default: `~/sage-wiki`).

## Core Workflow

### 1. Initialize

```bash
# New project (greenfield)
mkdir my-wiki && cd my-wiki
sage-wiki init

# Or overlay on existing Obsidian vault
cd ~/Documents/MyVault
sage-wiki init --vault
```

This creates:
- `config.yaml` — LLM provider, models, compiler settings
- `raw/` — Source material directory
- `wiki/` — Compiled output directory

**Edit `config.yaml`** to add your API key and pick models:

```yaml
api:
  provider: gemini
  api_key: ${GEMINI_API_KEY}

models:
  summarize: gemini-3-flash-preview
  extract: gemini-3-flash-preview
  write: gemini-3-flash-preview
  lint: gemini-3-flash-preview
  query: gemini-3-flash-preview
```

### 2. Add Sources

```bash
# Copy files into raw/
cp ~/papers/*.pdf raw/papers/
cp ~/articles/*.md raw/articles/

# Or use the ingest command
sage-wiki ingest https://example.com/article
sage-wiki ingest /path/to/file.pdf

# Or from AI conversations (MCP)
sage-wiki learn "Key insight: flash attention reduces memory from O(n²) to O(n)"
sage-wiki capture "Discussion concluded that RAG is insufficient for cumulative knowledge"
```

**Supported formats**: Markdown, PDF, Word, Excel, PowerPoint, CSV, EPUB, Email (.eml), Plain text, Transcripts (.vtt/.srt), Images (via vision LLM), Code (.go/.py/.js/.ts/.rs etc.)

### 3. Compile

```bash
# Full compile
sage-wiki compile

# Watch mode (auto-recompile on file changes)
sage-wiki compile --watch

# Estimate cost before compiling
sage-wiki compile --estimate

# Batch API (50% cost reduction for 10+ sources)
sage-wiki compile --batch

# Dry run (show what would be compiled)
sage-wiki compile --dry-run

# Prune deleted sources
sage-wiki compile --prune
```

**Tiered compilation** (key scaling feature):

| Tier | What happens | Cost | Time/doc |
|------|-------------|------|----------|
| 0 — Index only | FTS5 full-text search | Free | ~5ms |
| 1 — Index + embed | FTS5 + vector embedding | ~$0.00002 | ~200ms |
| 2 — Code parse | Structural summary (no LLM) | Free | ~10ms |
| 3 — Full compile | Summarize + extract + write | ~$0.05-0.15 | ~5-8 min |

For large vaults (10K+), set `default_tier: 1` in config to index everything fast, then compile on demand.

### 4. Search and Query

```bash
# Hybrid search (BM25 + vector)
sage-wiki search "attention mechanism"

# Filter by tags
sage-wiki search "transformer" --tags architecture,model

# Natural language Q&A with citations
sage-wiki query "How does flash attention optimize memory?"

# Check source coverage
sage-wiki provenance "flash-attention"
```

**Search pipeline** (automatic, zero config):
1. **Chunk-level indexing** — ~800 token chunks with FTS5 + vector
2. **LLM query expansion** — keyword/semantic/HyDE rewrites
3. **BM25 + vector RRF fusion** — dual-channel retrieval
4. **LLM re-ranking** — position-aware blending
5. **Graph expansion** — 4-signal ontology traversal

### 5. Lint and Maintain

```bash
# Run all lint passes
sage-wiki lint

# Auto-fix issues
sage-wiki lint --fix

# Run specific pass
sage-wiki lint --pass crossrefs

# Check wiki health
sage-wiki status

# Show pending changes
sage-wiki diff
```

### 6. MCP Server (Agent Integration)

```bash
# Start MCP server (stdio mode, for Claude Code etc.)
sage-wiki serve

# SSE mode (network clients)
sage-wiki serve --transport sse --port 3333
```

**Claude Code** — add to `.mcp.json`:
```json
{
  "mcpServers": {
    "sage-wiki": {
      "command": "sage-wiki",
      "args": ["serve", "--project", "/path/to/wiki"]
    }
  }
}
```

**MCP tools available**:
- `wiki_search` — Hybrid search
- `wiki_query` — Q&A with citations
- `wiki_compile` — Trigger compilation
- `wiki_compile_topic` — Compile specific topic cluster
- `wiki_learn` — Store a knowledge nugget
- `wiki_capture` — Extract knowledge from conversation
- `wiki_add_source` — Ingest a file
- `wiki_list` — List entities/concepts/sources
- `wiki_ontology` — Query ontology graph

### 7. TUI (Terminal Dashboard)

```bash
sage-wiki tui
```

4 tabs:
- **[F1] Browse** — Navigate articles by section
- **[F2] Search** — Fuzzy search with preview
- **[F3] Q&A** — Conversational streaming Q&A
- **[F4] Compile** — Live compile dashboard

### 8. Web UI (Optional)

Build from source with `go build -tags webui` tag. Features: Article browser, hybrid search, knowledge graph visualization, streaming Q&A, dark/light mode.

### 9. Ontology Management

```bash
# List ontology entities and relations
sage-wiki ontology list

# Query specific concept
sage-wiki ontology query "attention"
```

8 built-in relation types: `implements`, `extends`, `optimizes`, `contradicts`, `cites`, `prerequisite_of`, `trades_off`, `derived_from`

Custom relations in `config.yaml`:
```yaml
ontology:
  relation_types:
    - name: regulates
      synonyms: ["regulates", "regulated by"]
  entity_types:
    - name: decision
      description: "A recorded decision with rationale"
```

### 10. Multi-Project Hub

```bash
# Add a project to hub
sage-wiki hub add /path/to/project --name "AI Research"

# Search across all projects
sage-wiki hub search "transformer"

# Check hub status
sage-wiki hub status
```

## Cost Optimization

1. **Prompt caching** (default: on) — Saves 50-90% on input tokens
2. **Batch API** — 50% cost reduction for 10+ sources
3. **Tiered compilation** — Index fast, compile what matters
4. **Code AST parsing** — 10 languages parsed without LLM (Tier 2)
5. **Cost estimation** — `sage-wiki compile --estimate` before committing
6. **Auto mode** — `compiler.mode: auto` uses batch when 10+ sources

## Scaling Guide

| Vault Size | Recommended Config |
|------------|-------------------|
| < 1K docs | `default_tier: 3` (full compile everything) |
| 1K-10K | `default_tier: 1` + compile on demand |
| 10K-100K | `default_tier: 1` + auto-promote + auto-demote |
| 100K+ | `default_tier: 0` + selective Tier 3 for core topics |

## Performance Benchmarks

From 1,107 source wiki (49.4 MB DB, 2,832 wiki files):

| Operation | p50 | Throughput |
|-----------|-----|-----------|
| FTS5 keyword search | 411µs | 1,775 qps |
| Vector cosine search | 81ms | 15 qps |
| Hybrid RRF | 80ms | 16 qps |
| Graph traversal (BFS ≤5) | 1µs | 738K qps |

Quality: Search recall@10 = **100%**, Source citation rate = 94.6%, Overall quality = 73.0%

## Integration with Hermes Agent

### As MCP Tool

When sage-wiki MCP server is running, Hermes can use it as a persistent knowledge layer:

1. Start server: `sage-wiki serve --project ~/sage-wiki`
2. Hermes connects via MCP client
3. Use `wiki_search` / `wiki_query` for knowledge retrieval
4. Use `wiki_learn` / `wiki_capture` to save insights from conversations
5. Use `wiki_compile_topic` for on-demand compilation

### As CLI Command

Hermes can also invoke sage-wiki directly via terminal:

```bash
sage-wiki search "topic" --project ~/sage-wiki
sage-wiki query "question" --project ~/sage-wiki
sage-wiki compile --project ~/sage-wiki
sage-wiki learn "insight text" --project ~/sage-wiki
```

## Comparison with llm-wiki Skill

| Dimension | sage-wiki | llm-wiki |
|-----------|-----------|----------|
| Type | Go binary compiler | Markdown skill spec |
| Storage | SQLite + FTS5 + vectors | Pure Markdown files |
| Search | Hybrid BM25 + vector + graph | ripgrep (search_files) |
| Scale | 100K+ documents | No optimization for scale |
| Lifecycle | Tier auto-promote/demote | Confidence + forgetting curve |
| MCP | Built-in server | No |
| Ontology | 8 typed relations + custom | Free [[wikilinks]] |
| Visualization | Force-directed graph + TUI + Web UI | Canvas/Excalidraw/Mermaid |
| Cost control | Estimate + Batch + Tiered | None |
| Agent support | MCP + skill file | Claude Code/Codex/Gemini specs |

**Use sage-wiki when**: Large vaults, MCP integration, cost control, production deployment
**Use llm-wiki when**: Personal notes, Obsidian-native, knowledge lifecycle management, visual diagrams

## Pitfalls

- **Go version**: Requires Go 1.24+. Old Go versions will fail silently or produce broken binaries.
- **API key required**: Compilation won't work without a valid LLM API key. Use `sage-wiki doctor` to verify.
- **First compile is slow**: Full Tier 3 compilation takes ~5-8 min per document. Use `--estimate` first.
- **Watch mode debounce**: Default 2 seconds. Adjust `compiler.debounce_seconds` for your workflow.
- **Vector search requires embedding**: If embedding provider is misconfigured, search falls back to BM25 only.
- **Large vaults need tiered config**: Don't use `default_tier: 3` for 10K+ docs — it will be expensive and slow.
- **Batch API checkpoint**: After `--batch`, you must run `sage-wiki compile` again to poll and retrieve results.
- **Code parsing is Tier 2**: Only 10 languages supported. Other code files go to Tier 3 (LLM).
- **Image processing needs vision LLM**: Gemini/Claude/GPT-4o required for image source extraction.
