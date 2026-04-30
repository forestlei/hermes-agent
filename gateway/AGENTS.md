# gateway/ — Messaging Gateway

## Overview
The gateway connects Hermes to 20+ messaging platforms (Telegram, Discord, Slack, Feishu, WhatsApp, Signal, Matrix, etc.) and orchestrates the agent loop for each inbound message.

## Structure
```
gateway/
├── run.py           # GatewayRunner — 12.8k LOC, the gateway core
│                    #   Adapter factory, message dispatch, agent lifecycle,
│                    #   slash command routing, cron delivery, session management
├── session.py       # build_session_context_prompt() — system prompt assembly
├── config.py        # Platform enum (20 members), PlatformConfig dataclass
├── status.py        # Gateway status tracking, scoped locks, takeover markers
├── platform_registry.py  # Plugin adapter registry (PlatformEntry, factory)
├── channel_directory.py  # Session-based channel discovery
├── platforms/       # 20+ platform adapters — see platforms/AGENTS.md
└── builtin_hooks/   # Extension point for always-registered hooks (none shipped)
```

## Where To Look

| Task | Location | Notes |
|------|----------|-------|
| Add a new platform adapter | `platforms/<platform>.py` + see `platforms/ADDING_A_PLATFORM.md` | 16-file checklist for built-in; 1-file for plugin |
| Route/dispatch an inbound message | `run.py` `_process_message_background()` ~L4000 | Message → command check → agent spawn |
| Modify system prompt for gateway | `session.py` `build_session_context_prompt()` | Layer 5 in prompt assembly |
| Change how agents are created | `run.py` `_run_agent_for_event()` ~L9000 | AIAgent init with platform context |
| Add a slash command to gateway | `run.py` command dispatch ~L3800 | Also needs `hermes_cli/commands.py` |
| Fix session lifecycle issues | `run.py` `_active_sessions` dict + `run_agent.py` | Sessions keyed by `session_key` |
| Modify typing indicators | `platforms/base.py` `_keep_typing()` | Per-adapter override |
| Add restricted channel logic | `run.py` ~L4273 (command filter) + ~L10574 (toolset filter) | + `session.py` ~L377 (prompt filter) |

## Conventions
- Gateway config is loaded via **direct YAML read** (not `DEFAULT_CONFIG` merge) — new keys must be in user's config.yaml
- All platform adapters extend `BasePlatformAdapter` from `platforms/base.py`
- Adapter factory: plugin registry checked FIRST, then built-in if/elif chain
- `_active_sessions` dict prevents duplicate agents for same session_key
- `_pending_messages` queue in base adapter gates messages when agent is running — control commands (/stop, /new, /approve, /deny) MUST bypass both guards

## Anti-Patterns
- DO NOT send messages from gateway runner directly — use `adapter.send()` for platform-specific formatting
- DO NOT modify system prompt mid-conversation — breaks prefix caching (see `session.py` frozen snapshot pattern)
- DO NOT add new command dispatch in `_process_message_background()` — control commands must reach runner inline, not via background queue

## Key Numbers
- `run.py`: 12,827 lines (largest file in the repo)
- 20 platform adapters, largest: yuanbao.py (4,754), feishu.py (4,666), discord.py (4,080)
- ~16 files must change for a new built-in adapter (vs 1 file for plugin path)
