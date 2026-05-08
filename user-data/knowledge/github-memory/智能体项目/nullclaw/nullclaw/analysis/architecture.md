# nullclaw/nullclaw Architecture

## Key Statistics
- **7.1k stars**, 837 forks, 2,066 commits
- **678 KB static binary** (vs ~150 MB for Claude Code)
- **<2 ms startup time**
- **~1 MB peak RAM**
- **100% Zig** — no runtime, no garbage collector, no dependencies
- 5,300+ tests, 50+ providers, 19 channels, 35+ tools, 10 memory engines

## Architecture Philosophy
"Null overhead. Null compromise."

Written entirely in Zig — eliminates allocator overhead, garbage collector pauses, and runtime dependencies. The binary is statically compiled and runs on anything with a CPU (including $5 boards).

## Comparison with OpenClaw

| Metric | OpenClaw | NullClaw |
|--------|----------|----------|
| Binary Size | ~100 MB (Node.js) | 678 KB |
| Startup | ~seconds | <2 ms |
| Language | TypeScript/Node.js | Zig |
| Dependencies | Node runtime | None (static) |
| Config | JSON | JSON (OpenClaw-compatible) |

## Key Features
- **50+ LLM providers** via OpenRouter, OpenAI-compatible APIs
- **19 messaging channels** (same multi-channel as OpenClaw)
- **35+ built-in tools** (file, shell, search, git)
- **10 memory engines**: SQLite (FTS5 + vector cosine similarity), Markdown, ClickHouse, PostgreSQL, and more
- **Multi-layer sandbox** for tool execution
- **Heartbeat schedulers** and **cron job engines**
- **OpenClaw compatible** — uses same config structure

## Ecosystem
- **nullhub** — UI layer for Null ecosystem (beta)
- **nullboiler** — orchestration
- **nullwatch** — observability
- **nulltickets** — task tracking

## Why It Matters
NullClaw is the **minimalist rewrite** of OpenClaw in Zig — proving that the gateway + skills paradigm can be implemented as a tiny, zero-dependency binary. It's the antithesis of framework-bloated AI tools.
