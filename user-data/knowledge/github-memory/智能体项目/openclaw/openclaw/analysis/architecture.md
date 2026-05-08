# openclaw/openclaw Architecture

## Key Statistics
- **354k stars**, 71.5k forks, 29,827 commits
- TypeScript/Node.js (Node 24 recommended)
- Sponsors: OpenAI, GitHub, NVIDIA, Vercel, Blacksmith, Convex

## Gateway Architecture (The Paradigm)
```
WhatsApp / Telegram / Slack / Discord / Signal / iMessage / IRC / Teams / Matrix / Feishu / LINE / ... (20+ channels)
               │
               ▼
┌───────────────────────────────┐
│            Gateway            │
│       (control plane)         │
│     ws://127.0.0.1:18789     │
└──────────────┬────────────────┘
               │
               ├─ Pi agent (RPC)
               ├─ CLI
               ├─ WebChat UI
               ├─ macOS app
               └─ iOS / Android nodes
```

## Core Features

### Multi-Channel Inbox
20+ messaging platforms: WhatsApp, Telegram, Slack, Discord, Google Chat, Signal, iMessage, BlueBubbles, IRC, Microsoft Teams, Matrix, Feishu, LINE, Mattermost, Nextcloud Talk, Nostr, Synology Chat, Tlon, Twitch, Zalo, WeChat, WebChat

### Skills System
- Bundled, managed, and workspace skills
- Install gating + UI
- SKILL.md files
- agentskills.io compatible

### Multi-Agent Routing
- Route inbound channels/accounts/peers to isolated agents
- Workspaces + per-agent sessions
- Group isolation

### Voice + Canvas
- Voice Wake (macOS/iOS wake words)
- Talk Mode (continuous voice on Android)
- Live Canvas with A2UI

### Tools
- Browser control (openclaw Chrome/Chromium)
- Canvas control
- Nodes (camera, screen, location, notifications)
- Cron + webhooks
- Gmail Pub/Sub integration

### Security
- DM pairing with approval codes
- Per-channel allowlists
- Untrusted input handling

## Why It Matters
OpenClaw is the **original gateway + skills paradigm** that inspired hermes-agent, poco-claw, and the broader "claw" ecosystem. Its core insight: the agent is a runtime, not an app — it should connect to ALL the channels you already use.
