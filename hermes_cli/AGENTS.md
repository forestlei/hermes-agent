# hermes_cli/ — CLI Surface

## Overview
65 Python files covering CLI entry point, argparse tree, config system, plugin discovery, setup wizard, skin engine, and dashboard web server.

## Structure
```
hermes_cli/
├── main.py           # ~10k LOC — entry point, argparse, cmd_* dispatch, profile override
├── _parser.py        # Top-level parser + chat subparser (shared with relaunch.py)
├── config.py         # ~4.6k LOC — DEFAULT_CONFIG, load_config(), OPTIONAL_ENV_VARS
├── commands.py       # COMMAND_REGISTRY — single source of truth for slash commands
├── plugins.py        # PluginManager — discovers from 4 sources, PluginContext facade
├── skin_engine.py    # SkinConfig, built-in skins, YAML loader
├── setup.py          # Interactive setup wizard (5 sections)
├── auth.py           # PROVIDER_REGISTRY, auth status
├── models.py         # Model listing/selection
├── gateway.py        # Gateway subcommand handlers
├── web_server.py     # Dashboard FastAPI server
├── pty_bridge.py     # PTY bridge for dashboard embedded TUI
├── curses_ui.py      # Preferred interactive menus (replaces simple_term_menu)
├── tools_config.py   # Tools configuration UI (curses)
├── profiles.py       # Profile management
├── env_loader.py     # .env loading from HERMES_HOME + project root
└── (50+ more files)
```

## Startup Sequence (main.py)
1. `_apply_profile_override()` — pre-parses `--profile/-p`, sets `HERMES_HOME` env var
2. `load_hermes_dotenv()` — loads `.env` from HERMES_HOME, then project root
3. Bridge `security.redact_secrets` config → `HERMES_REDACT_SECRETS` env var
4. `setup_logging(mode="cli")`
5. `build_top_level_parser()` from `_parser.py`
6. `args.func(args)` dispatch

## Config System
Three config loaders (know which one you're in):

| Loader | Used by | Location |
|--------|---------|----------|
| `load_cli_config()` | CLI mode | `cli.py` — CLI defaults + user YAML |
| `load_config()` | Most CLI subcommands | `config.py` — DEFAULT_CONFIG + user YAML |
| Direct YAML load | Gateway runtime | `gateway/run.py` — reads user YAML raw |

If you add a config key and CLI sees it but gateway doesn't (or vice versa), you're on the wrong loader.

## PluginManager Discovery (4 sources, later overrides earlier)
1. **Bundled** — `<repo>/plugins/<name>/` (excludes memory/ and context_engine/)
2. **User** — `~/.hermes/plugins/<name>/`
3. **Project** — `./.hermes/plugins/<name>/` (gated by `HERMES_ENABLE_PROJECT_PLUGINS`)
4. **Pip** — packages with `hermes_agent.plugins` entry point

Each plugin needs: `plugin.yaml` manifest + `__init__.py` with `register(ctx)`.

## PluginContext Registration Methods
`register_tool()`, `register_hook()`, `register_cli_command()`, `register_command()`, `register_platform()`, `register_context_engine()`, `register_image_gen_provider()`, `inject_message()`, `dispatch_tool()`

## Slash Command Registry (commands.py)
All commands defined in `COMMAND_REGISTRY` as `CommandDef` objects. Adding an alias only requires updating the `aliases` tuple — dispatch, help, menus, autocomplete all update automatically.

## Anti-Patterns
- DO NOT use `simple_term_menu` — use `curses_ui.py` instead (ghost-duplication bugs in tmux)
- Plugins MUST NOT modify core files — expand the generic plugin surface instead
- Plugin context MUST be injected into user message, NEVER system prompt (preserves prefix cache)
