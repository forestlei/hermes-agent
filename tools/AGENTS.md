# tools/ — Tool Implementations

## Overview
69 tool files auto-discovered via `registry.register()`. Each file self-registers at import time. The registry handles schema collection, dispatch, availability checking, and error wrapping.

## Structure
```
tools/
├── registry.py           # ToolRegistry singleton — ZERO deps (circular-import safe)
├── file_tools.py         # file toolset: read_file, write_file, patch, search_files
├── terminal_tool.py      # terminal toolset: terminal (6 backends)
├── web_tools.py          # web toolset: web_search, web_extract
├── browser_tool.py       # browser toolset: 10 browser_* tools
├── code_execution_tool.py# code_execution toolset
├── delegate_tool.py      # delegation toolset: delegate (subagents)
├── memory_tool.py        # memory toolset: memory (MemoryStore, 2200/1375 char limits)
├── todo_tool.py          # todo toolset: todo
├── skills_tool.py        # skills toolset: skill_install, skill_create
├── skill_manager_tool.py # skills toolset: skill_manage
├── session_search_tool.py# session_search toolset
├── cronjob_tools.py      # cronjob toolset
├── send_message_tool.py  # messaging toolset
├── vision_tools.py       # vision toolset: vision_analyze
├── tts_tool.py           # tts toolset (Piper support added v0.12.0)
├── mcp_tool.py           # dynamic mcp-* toolsets (per MCP server)
├── approval_tool.py      # approval toolset: submit_approval
├── clarify_tool.py       # clarify toolset
├── (20+ more tool files)
│
├── environments/         # Terminal backends
│   ├── base.py           # BaseEnvironment ABC
│   ├── local.py          # Local subprocess
│   ├── docker.py         # Docker (cap-drop ALL, no-new-privileges)
│   ├── ssh.py            # SSH with ControlMaster persistence
│   ├── modal.py          # Modal SDK Sandbox
│   ├── daytona.py        # Daytona SDK
│   ├── singularity.py    # Singularity/Apptainer
│   └── vercel_sandbox.py # Vercel SDK
│
├── browser_providers/    # Cloud browser backends
│   ├── base.py           # CloudBrowserProvider ABC
│   ├── browserbase.py    # Browserbase
│   └── firecrawl.py      # Firecrawl
│
└── (20+ support files)   # Security, URL safety, patch parsing, etc.
```

## Registration Pattern (required in every tool file)

```python
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

## Registry API (tools/registry.py)

| Method | Purpose |
|--------|---------|
| `register(name, toolset, schema, handler, ...)` | Self-register a tool |
| `get_definitions(tool_names, quiet)` | Get OpenAI-format schemas (filtered by check_fn) |
| `dispatch(name, args, **kwargs)` | Execute handler, return JSON string |
| `deregister(name)` | Remove tool + cleanup toolset if last |
| `get_toolset_for_tool(name)` | Map tool name → toolset |
| `is_toolset_available(toolset)` | Check if all env deps met |

## Discovery
`discover_builtin_tools()` AST-scans `tools/*.py` for `registry.register()` calls, imports matching modules. Excludes `__init__.py`, `registry.py`, `mcp_tool.py`.

## BaseEnvironment ABC (environments/base.py)

```python
class BaseEnvironment(ABC):
    def execute(self, command, cwd="", *, timeout=None, stdin_data=None) -> dict
    # Returns: {"output": str, "returncode": int}
    def init_session(self)    # capture login shell env snapshot
    def cleanup(self)         # abstract — release backend resources
```

8 backends: Local, Docker, SSH, Modal, ManagedModal, Daytona, Singularity, VercelSandbox

## Security Layers (in dispatch order)
1. **Path security** (`path_security.py`) — traversal prevention
2. **URL safety** (`url_safety.py`) — SSRF, metadata IP blocking
3. **Website policy** (`website_policy.py`) — robots.txt compliance
4. **Approval gates** (`approval.py`) — hardline blocklist + user approval
5. **Tirith scanner** (`tirith_security.py`) — security policy enforcement
6. **Write deny list** (`file_operations.py`) — sensitive file protection
7. **Env sanitization** (`environments/local.py`) — secret stripping for subprocesses

## Anti-Patterns
- DO NOT import from `model_tools.py` in tool files (circular import)
- All handlers MUST return a JSON string
- Tool schema descriptions must NOT mention tools from other toolsets by name
- Use `get_hermes_home()` for all persistent state paths (profile safety)
- Use `display_hermes_home()` for user-facing path strings
