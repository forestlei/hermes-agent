# nativ3ai/hermes-agent-camel

## Overview
Hermes Agent fork with integrated CaMeL (Capabilities for Machine Learning) trust boundaries. Adapts Google DeepMind's CaMeL security framework to the Hermes agent runtime.

## Research Provenance
- **Paper**: [CaMeL: Capabilities for Machine Learning](https://arxiv.org/abs/2503.18813) (Google DeepMind)
- **Reference repo**: [google-research/camel-prompt-injection](https://github.com/google-research/camel-prompt-injection)
- **Note**: This is a community implementation, NOT Google's official code. The design is research-inspired but implementation is Hermes-native.

## Core Innovation: Trust Boundary Separation
The key insight from CaMeL: **don't restrict what the agent "thinks" — restrict what it "can do"**.

### Trusted vs Untrusted Data
| Category | Examples |
|----------|----------|
| **Trusted** | System prompt, approved skills, real user turns |
| **Untrusted** | Tool outputs, web content, browser content, files, session recall, MCP data |

### Implementation (agent/camel_guard.py)
1. **Trusted operator plan extraction** — Parse real user intent from genuine turns
2. **Provenance-aware wrapping** — Tag untrusted tool outputs with source metadata
3. **Per-turn security envelope** — Inject security context into system prompt each turn
4. **Capability gating** — Sensitive tools require authorization against trusted plan

### Gated Capabilities
- Terminal/command execution
- File mutation
- Persistent memory writes
- External messaging
- Scheduled actions (cron)
- Skill mutation
- Delegation and subagents
- Browser interaction

### Ungated (Read-only)
- `send_message(action="list")`
- `cronjob(action="list")`
- Other read operations

## Threat Model
Targets **indirect prompt injection**:
1. Agent retrieves untrusted content (web/file/MCP)
2. Content contains hidden instructions ("ignore previous instructions", "run this command")
3. Model attempts to execute malicious commands from untrusted source

## Comparison with Related Projects
| Project | Type | Stars | Focus |
|---------|------|-------|-------|
| nativ3ai/hermes-agent-camel | Community runtime integration | 107 | Hermes-specific trust separation |
| camel-ai/camel | Multi-agent framework | 5K+ | General-purpose agent communication |
| google-research/camel-prompt-injection | Research artifact | - | Paper reproduction & evaluation |

## Relevance
- **Article #8 (MCP Tool Poisoning)**: This project directly addresses the tool description injection attack described in that article
- **Article #19 (CaMeL Defense)**: The article covered CaMeL but with wrong repo name; this is the actual Hermes integration
- **Agent Security**: Represents a practical implementation of capability-based security for production agent loops
