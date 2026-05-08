# NousResearch/hermes-agent Analysis

## Architecture Highlights

### Skills System
- Procedural memory via SKILL.md files
- Agent-curated memory with periodic nudges
- Autonomous skill creation after complex tasks
- Skills self-improve during use
- Compatible with agentskills.io open standard

### Closed Learning Loop
- Creates skills from experience
- Improves skills during use
- Nudges itself to persist knowledge
- FTS5 session search with LLM summarization
- Cross-session recall
- Honcho dialectic user modeling

### Gateway Pattern
- Single gateway process for multi-platform delivery
- Telegram, Discord, Slack, WhatsApp, Signal, Email
- Voice memo transcription
- Cross-platform conversation continuity

### Tool Orchestration
- 40+ built-in tools
- Toolset system for platform-specific toolsets
- MCP integration (connect any MCP server)
- Six terminal backends: local, Docker, SSH, Daytona, Singularity, Modal
- Daytona and Modal offer serverless persistence (hibernates when idle)

### Research-Ready
- Batch trajectory generation
- Atropos RL environments
- Trajectory compression for training next-gen tool-calling models
- OpenClaw migration support

## Key Differentiators (vs old frameworks)
1. Self-improving (skills auto-create/improve)
2. Provider-agnostic (any LLM - Nous Portal, OpenRouter, GLM, Kimi, MiniMax, OpenAI, Anthropic)
3. Multi-platform gateway (not just CLI)
4. Serverless persistence (Daytona/Modal - nearly zero idle cost)
5. Cross-session memory with FTS5 search
