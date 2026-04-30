# gateway/platforms/ — Platform Adapters

## Overview
20+ messaging platform adapters, each extending `BasePlatformAdapter`. Two integration paths: built-in (16-file checklist) or plugin (1 file, zero core changes).

## Structure
```
platforms/
├── base.py              # BasePlatformAdapter ABC (3,024 lines)
├── ADDING_A_PLATFORM.md # 16-step integration checklist (334 lines)
├── helpers.py           # MessageDeduplicator, TextBatchAggregator, strip_markdown, etc.
├── __init__.py          # Exports BasePlatformAdapter, MessageEvent, SendResult
│
├── telegram.py          # 3,341 lines — python-telegram-bot, MarkdownV2, UTF-16 chunking
├── yuanbao.py           # 4,754 lines — protobuf protocol, stickers, media
├── feishu.py            # 4,666 lines — Feishu/Lark API, rich cards, <at> tags
├── discord.py           # 4,080 lines — discord.py, threads, reaction indicators
├── slack.py             # 2,598 lines — slack-bolt, Assistant API, thread sessions
├── matrix.py            # 2,676 lines — mautrix client, e2ee
├── api_server.py        # 2,901 lines — HTTP REST + WebSocket
├── weixin.py            # 2,101 lines — WeChat Official Account, XML messaging
├── wecom.py             # 1,602 lines — WeCom/WeChat Work
├── dingtalk.py          # 1,362 lines — DingTalk AI Cards, REQUIRES_EDIT_FINALIZE=True
├── signal.py            # 1,272 lines — signal-cli SSE + JSON-RPC
├── whatsapp.py          # 1,074 lines — Node.js bridge
├── bluebubbles.py       #   935 lines — iMessage via BlueBubbles
├── webhook.py           #   771 lines — generic HTTP, HMAC validation
├── mattermost.py        #   738 lines — Mattermost REST
├── email.py             #   629 lines — IMAP + SMTP
├── homeassistant.py     #   449 lines — HA WebSocket API
├── sms.py               #   373 lines — Twilio
├── qqbot/               # 2,863 lines — QQBot package (5 files)
└── yuanbao_*.py         # supporting modules (proto, media, sticker)
```

## BasePlatformAdapter Required Interface

| Method | Purpose |
|--------|---------|
| `__init__(config)` | Parse config, call `super().__init__(config, Platform.YOURS)` |
| `connect() -> bool` | Connect to platform, start listeners |
| `disconnect()` | Stop listeners, close connections |
| `send(chat_id, content, ...) -> SendResult` | Send text message |
| `get_chat_info(chat_id) -> dict` | Return `{name, type, chat_id}` |

Required module-level function (not a method):
```python
def check_<platform>_requirements() -> bool
```

## Key Class Attributes

| Attribute | Purpose | Examples |
|-----------|---------|---------|
| `MAX_MESSAGE_LENGTH` | Platform char limit | 2000 (Discord), 4096 (Telegram), 39000 (Slack) |
| `REQUIRES_EDIT_FINALIZE` | Needs explicit finalize on streaming edits | `True` (DingTalk only) |

## Patterns All Adapters Must Follow

1. `self.build_source(...)` — construct SessionSource for every inbound message
2. `self.handle_message(event)` — dispatch to gateway (NOT `_message_handler` directly)
3. `cache_image_from_bytes` / `cache_audio_from_bytes` / `cache_document_from_bytes` — cache attachments
4. Filter self-messages — prevent reply loops
5. `_acquire_platform_lock()` / `_release_platform_lock()` — prevent duplicate gateway on same credential
6. Redact sensitive identifiers (phone numbers, tokens) in all log output
7. Reconnection with exponential backoff + jitter for SSE/WebSocket connections

## Shared Helpers (helpers.py)

| Helper | Used By |
|--------|---------|
| `MessageDeduplicator` | Discord, Slack, DingTalk, WeCom, Weixin, Mattermost, Feishu |
| `TextBatchAggregator` | Telegram, Discord, Matrix, WeCom, Feishu |
| `ThreadParticipationTracker` | Discord, Matrix |
| `strip_markdown()` | SMS, BlueBubbles, Feishu (plain-text platforms) |
| `redact_phone()` | Signal, WhatsApp, SMS |

## Registration Paths

**Built-in**: if/elif chain in `GatewayRunner._create_adapter()` (run.py L3262-3440)
**Plugin**: `PlatformEntry` in `platform_registry.py` — gateway checks registry FIRST

## Platform Quirks

- **Telegram**: Message length in UTF-16 code units (not Unicode codepoints); MarkdownV2 escaping; file URLs expire ~1 hour
- **Discord**: 2000-char strict limit; reaction-based processing indicators (👀→✅/❌)
- **DingTalk**: Only adapter with `REQUIRES_EDIT_FINALIZE = True`
- **Signal**: Phone number as user ID (requires redaction); 8s typing interval
- **WhatsApp**: Requires Node.js bridge (not Python SDK)
- **Yuanbao**: Protobuf-based protocol; largest adapter at 4,754 lines
