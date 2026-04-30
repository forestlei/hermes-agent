# ui-tui/ — Ink Terminal UI

## Overview
Full replacement for the classic CLI, activated via `hermes --tui`. TypeScript (Ink/React) renders the screen; Python (`tui_gateway/`) owns sessions, tools, and model calls. JSON-RPC over stdio bridges the two.

## Process Model
```
hermes --tui
  └─ Node (Ink)  ──stdio JSON-RPC──  Python (tui_gateway)
       │                                  └─ AIAgent + tools + sessions
       └─ renders transcript, composer, prompts, activity
```

## Structure
```
ui-tui/
├── src/
│   ├── entry.tsx          # TTY gate + Ink render()
│   ├── app.tsx            # Top-level Ink tree
│   ├── gatewayClient.ts   # Child process spawn + JSON-RPC bridge
│   ├── gatewayTypes.ts    # Full TypeScript types for all RPC (508 lines)
│   ├── theme.ts           # Default palette + skin merge
│   ├── app/               # App logic (21 files)
│   │   ├── createGatewayEventHandler.ts
│   │   ├── createSlashHandler.ts
│   │   ├── useComposerState.ts
│   │   ├── useMainApp.ts
│   │   ├── useSubmission.ts
│   │   ├── useSessionLifecycle.ts
│   │   ├── turnController.ts, turnStore.ts
│   │   └── slash/         # Slash command subsystem
│   ├── components/        # Ink UI components (21 files)
│   │   ├── appLayout.tsx, appChrome.tsx, appOverlays.tsx
│   │   ├── messageLine.tsx, streamingAssistant.tsx
│   │   ├── thinking.tsx, prompts.tsx
│   │   ├── sessionPicker.tsx, modelPicker.tsx
│   │   ├── textInput.tsx, markdown.tsx
│   │   └── themed.tsx
│   ├── hooks/             # React/Ink hooks (5 files)
│   ├── lib/               # Pure utilities (34 files)
│   ├── domain/            # Domain types (8 files)
│   ├── content/           # Static content (7 files: charms, faces, verbs, etc.)
│   └── config/            # Config constants (3 files)
│
└── packages/hermes-ink/   # Forked Ink renderer
    └── src/ink/           # Core renderer (57 files)
        ├── components/    # Box, Text, ScrollBox, Button, etc. (19 files)
        └── hooks/         # use-input, use-app, use-stdin, etc. (13 files)

tui_gateway/              # Python JSON-RPC backend
├── entry.py              # Stdio entrypoint, signal handling
├── server.py             # ~5.7k LOC — RPC dispatch, session lifecycle
├── transport.py          # StdioTransport, TeeTransport
├── slash_worker.py       # Persistent HermesCLI subprocess for slash commands
└── event_publisher.py    # WebSocket sidecar for dashboard
```

## TypeScript-Python Boundary

### What Runs in Node (TypeScript)
- Screen rendering, input handling, local slash commands (/help, /quit, /clear, /new, etc.)
- Completion (slash + path), theme/skin, state management (nanostores)

### What Runs in Python (tui_gateway)
- Session management, agent execution, all non-local slash commands
- Config read/write, MCP, voice, model switching, approvals

### Key RPC Methods (Node → Python)
`prompt.submit`, `session.create/resume/close/list`, `session.compress/undo/interrupt`, `clarify/approval/sudo/secret.respond`, `slash.exec`, `command.dispatch`, `complete.slash/path`, `config.get/set`, `tools.configure`, `model.options`

### Key Events (Python → Node)
`gateway.ready`, `message.delta/complete`, `thinking.delta`, `tool.start/progress/complete`, `clarify/approval/sudo/secret.request`, `subagent.spawn/start/complete`, `skin.changed`

## Dev Commands
```bash
cd ui-tui
npm install && npm run dev     # watch mode
npm run build                  # full build
npm run type-check             # tsc --noEmit
npm run lint && npm run fmt    # eslint + prettier
npm test                       # vitest
```

## Anti-Patterns
- DO NOT re-implement the primary chat experience in React — the dashboard embeds the real `hermes --tui` via PTY
- DO NOT add new RPC methods only in `server.py` — they must also be typed in `gatewayTypes.ts`
- DO NOT use `input()` from Python worker threads — deadlocks the TUI (see delegate_tool.py pattern)
- Structured React UI around the TUI is OK for sidebar widgets, inspectors, status panels — NOT for a second transcript/composer
