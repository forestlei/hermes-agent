---
name: mcporter
description: Use the mcporter CLI to list, configure, auth, and call MCP servers/tools directly (HTTP or stdio), including ad-hoc servers, config edits, and CLI/type generation.
version: 1.0.0
author: community
license: MIT
metadata:
  hermes:
    tags: [MCP, Tools, API, Integrations, Interop]
    homepage: https://mcporter.dev
prerequisites:
  commands: [npx]
---

# mcporter

Use `mcporter` to discover, call, and manage [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) servers and tools directly from the terminal.

## Prerequisites

Requires Node.js:
```bash
# No install needed (runs via npx)
npx mcporter list

# Or install globally
npm install -g mcporter
```

## Quick Start

```bash
# List MCP servers already configured on this machine
mcporter list

# List tools for a specific server with schema details
mcporter list <server> --schema

# Call a tool
mcporter call <server.tool> key=value
```

## Discovering MCP Servers

mcporter auto-discovers servers configured by other MCP clients (Claude Desktop, Cursor, etc.) on the machine. To find new servers to use, browse registries like [mcpfinder.dev](https://mcpfinder.dev) or [mcp.so](https://mcp.so), then connect ad-hoc:

```bash
# Connect to any MCP server by URL (no config needed)
mcporter list --http-url https://some-mcp-server.com --name my_server

# Or run a stdio server on the fly
mcporter list --stdio "npx -y @modelcontextprotocol/server-filesystem" --name fs
```

## Calling Tools

```bash
# Key=value syntax
mcporter call linear.list_issues team=ENG limit:5

# Function syntax
mcporter call "linear.create_issue(title: \"Bug fix needed\")"

# Ad-hoc HTTP server (no config needed)
mcporter call https://api.example.com/mcp.fetch url=https://example.com

# Ad-hoc stdio server
mcporter call --stdio "bun run ./server.ts" scrape url=https://example.com

# JSON payload
mcporter call <server.tool> --args '{"limit": 5}'

# Machine-readable output (recommended for Hermes)
mcporter call <server.tool> key=value --output json
```

## Auth and Config

```bash
# OAuth login for a server
mcporter auth <server | url> [--reset]

# Manage config
mcporter config list
mcporter config get <key>
mcporter config add <server>
mcporter config remove <server>
mcporter config import <path>
```

Config file location: `./config/mcporter.json` (override with `--config`).

## Daemon

For persistent server connections:
```bash
mcporter daemon start
mcporter daemon status
mcporter daemon stop
mcporter daemon restart
```

## Code Generation

```bash
# Generate a CLI wrapper for an MCP server
mcporter generate-cli --server <name>
mcporter generate-cli --command <url>

# Inspect a generated CLI
mcporter inspect-cli <path> [--json]

# Generate TypeScript types/client
mcporter emit-ts <server> --mode client
mcporter emit-ts <server> --mode types
```

## Notes

- Use `--output json` for structured output that's easier to parse
- Ad-hoc servers (HTTP URL or `--stdio` command) work without any config — useful for one-off calls
- OAuth auth may require interactive browser flow — use `terminal(command="mcporter auth <server>", pty=true)` if needed

## Sub-Tool: Skill Discovery (from find-skills)

Use `npx skills` to discover and install skills from the open agent skills ecosystem when the user asks "how do I do X" or wants to extend capabilities.

**Key commands:**
- `npx skills find [query]` — Search for skills interactively or by keyword
- `npx skills add <owner/repo@skill>` — Install a skill (e.g., `npx skills add vercel-labs/agent-skills@vercel-react-best-practices -g -y`)
- `npx skills check` / `npx skills update` — Check for and apply updates
- Browse skills at: https://skills.sh/

**Search strategy:** Use specific keywords for best results. Try alternative terms if first search misses. Check popular sources like `vercel-labs/agent-skills` and `ComposioHQ/awesome-claude-skills`.

## Sub-Tool: Headless Browser Automation (from Agent Browser)

For headless browser automation beyond MCP, use `agent-browser` CLI (Rust-based, fast):

```bash
# Quick start
npm install -g agent-browser && agent-browser install
agent-browser open <url>          # Navigate
agent-browser snapshot -i         # Get interactive elements with refs
agent-browser click @e1           # Click by ref
agent-browser fill @e2 "text"     # Fill input
agent-browser screenshot out.png  # Screenshot
agent-browser close               # Close

# Advanced: sessions, video recording, network interception, state management
agent-browser --session test1 open site-a.com   # Parallel sessions
agent-browser record start ./demo.webm           # Video recording
agent-browser state save auth.json               # Persist auth state
```

Use `--json` for machine-readable output. Always re-snapshot after navigation (refs change).
