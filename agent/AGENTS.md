# agent/ — Agent Internals

## Overview
Core agent logic extracted from `run_agent.py`: provider adapters, memory, context management, prompt assembly, error handling. All modules are pure utilities — no circular deps back to AIAgent.

## Structure
```
agent/
├── auxiliary_client.py     # Shared LLM client router (compression, vision, search)
├── prompt_builder.py       # System prompt assembly (identity, skills, context files, threat scan)
├── context_compressor.py   # Built-in LLM summarization with head/tail protection
├── context_engine.py       # ContextEngine ABC (compress, should_compress, tools)
├── memory_provider.py      # MemoryProvider ABC (lifecycle, tools, hooks)
├── memory_manager.py       # Orchestrator: builtin + 1 external provider
├── image_gen_provider.py   # ImageGenProvider ABC
├── image_gen_registry.py   # Provider registry (config-driven selection)
├── credential_pool.py      # Multi-credential pool for same-provider failover
├── error_classifier.py     # API error taxonomy (FailoverReason enum)
├── model_metadata.py       # Context lengths, token estimation, model catalog
├── display.py              # KawaiiSpinner, tool preview, diff display
├── curator.py              # Background skill maintenance (auto-archive, lifecycle, classification — enhanced v0.12.0)
├── redact.py               # Regex-based secret redaction for logs/output
├── file_safety.py          # Write-deny paths and read-block rules
│
├── transports/             # Provider transport layer (format conversion only)
│   ├── base.py             # ProviderTransport ABC
│   ├── types.py            # NormalizedResponse, ToolCall, Usage
│   ├── chat_completions.py # OpenAI chat_completions transport
│   ├── anthropic.py        # Anthropic Messages transport
│   ├── codex.py            # Codex Responses transport
│   └── bedrock.py          # Bedrock Converse transport
│
└── (30+ more files)        # Provider adapters, auth, skills, usage, etc.
```

## Key ABC Interfaces

### MemoryProvider (`memory_provider.py`)
Core lifecycle: `initialize()` → `get_tool_schemas()` → `prefetch()` / `sync_turn()` → `shutdown()`
Optional hooks: `on_session_switch`, `on_pre_compress`, `on_memory_write`, `get_config_schema`
Constraint: exactly 1 builtin + at most 1 external provider (enforced by MemoryManager)

### ContextEngine (`context_engine.py`)
Core: `should_compress()` → `compress()` → return compacted messages
State: `threshold_percent` (0.75), `protect_first_n` (3), `protect_last_n` (6)
Built-in: `ContextCompressor` — LLM summarization, head/tail protection

### ProviderTransport (`transports/base.py`)
Format conversion only: `convert_messages()`, `convert_tools()`, `build_kwargs()`, `normalize_response()`
4 transports: chat_completions, anthropic, codex, bedrock

### ImageGenProvider (`image_gen_provider.py`)
Config-driven selection via `image_gen_registry.py`

## Where To Look

| Task | Location | Notes |
|------|----------|-------|
| Add a new LLM provider | `agent/<provider>_adapter.py` + `transports/<mode>.py` | Follow existing adapter pattern |
| Change system prompt assembly | `prompt_builder.py` | 7-layer structure, see root AGENTS.md |
| Add memory provider plugin | `plugins/memory/<name>/` implementing MemoryProvider ABC | Register via `memory.provider` config |
| Modify context compression | `context_compressor.py` | Head/tail protection, tool output pruning |
| Fix credential failover | `credential_pool.py` + `error_classifier.py` | FailoverReason enum drives retry logic |
| Add new transport mode | `transports/<mode>.py` implementing ProviderTransport | Register via `register_transport()` |

## Module Boundaries
- `tools/registry.py` has ZERO imports from model_tools or tool files (circular-import safe)
- `agent/` modules never import from `run_agent.py` (AIAgent) directly
- `agent/transports/` are format-conversion only — no client construction or retry logic
- `MemoryProvider` implementations live in `plugins/memory/`, not in `agent/`
