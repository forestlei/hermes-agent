# Hermes Agent Migration Guide

Three complementary tools for protecting and migrating user data:

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `scripts/sync_user_data.py` | Sync `~/.hermes/` ↔ `user-data/` (Git) | After config changes, before/after upgrades |
| `scripts/migrate_hermes.py` | Cross-instance migration (different machines) | Moving to a new server/profile |
| `hermes_cli/user_data_guard.py` | Auto-restore on version upgrade | Automatic — runs at every startup |

## Priority Classification

| Priority | Category | Examples | Loss Impact |
|----------|----------|----------|-------------|
| 🔴 Critical | Constitution | persistent-solver, MEMORY.md, USER.md | Agent loses all personality/rules |
| 🔴 Critical | Core Config | config.yaml, .env, SOUL.md, rule files | Agent cannot function correctly |
| 🟡 Important | Capabilities | skills/, plugins/, skins/, hooks/ | Agent loses learned abilities |
| 🟡 Important | Knowledge | github-memory/, sources/, data/ | Irreplaceable accumulated knowledge |
| 🟡 Important | Automation | scripts/, cron/jobs.json | Scheduled tasks stop running |
| 🟢 Optional | Sessions | state.db, logs/, cache/ | Regenerable, low impact |

## Quick Start

### Sync to Git (backup)
```bash
python3 scripts/sync_user_data.py              # Backup ~/.hermes/ → user-data/
python3 scripts/sync_user_data.py --verify      # Check sync status
python3 scripts/sync_user_data.py --dry-run     # Preview without writing
```

### Restore from Git
```bash
python3 scripts/sync_user_data.py --restore     # Restore user-data/ → ~/.hermes/
```

### Cross-instance Migration
```bash
# Local migration (same machine, different profile)
python3 scripts/migrate_hermes.py --source ~/.hermes --target /path/to/new/hermes

# Remote migration via SSH
python3 scripts/migrate_hermes.py --source ~/.hermes --target user@host:~/.hermes

# Export to archive
python3 scripts/migrate_hermes.py --source ~/.hermes --export hermes-backup.tar.gz

# Import from archive
python3 scripts/migrate_hermes.py --import hermes-backup.tar.gz --target ~/.hermes
```

### Presets
```bash
python3 scripts/migrate_hermes.py --preset config-only ...   # Config + constitution only
python3 scripts/migrate_hermes.py --preset user-data ...     # + sessions, memories, cron
python3 scripts/migrate_hermes.py --preset full ...          # Everything
```

## Constitution Layer

The constitution layer is the **highest priority** and is ALWAYS migrated regardless of preset:

| File | Description | Backup Location |
|------|-------------|-----------------|
| `skills/software-development/persistent-solver/SKILL.md` | 8-rule top-level logic (v3.2) | `user-data/constitution/persistent-solver-SKILL.md` |
| `memories/MEMORY.md` | System index + rule summaries | `user-data/constitution/MEMORY.md` |
| `memories/USER.md` | User preferences + hallucination zero-tolerance | `user-data/constitution/USER.md` |

### Version Upgrade Protection

`hermes_cli/user_data_guard.py` runs automatically at every Hermes startup:
1. Detects version changes via `.hermes_version` marker
2. Checks if constitution files exist
3. Auto-restores from `user-data/` backup if files are missing
4. Logs errors if restoration fails

## Secrets Handling

| File | Git Backup | Migration | Notes |
|------|-----------|-----------|-------|
| `.env` | ❌ Never | ✅ With `--include-secrets` | API keys |
| `auth.json` | ❌ Never | ✅ With `--include-secrets` | OAuth tokens |
| `config.yaml` | ✅ Sanitized | ✅ | API keys replaced with placeholders |

## Workflow

```
Regular use:
  ~/.hermes/ ←→ user-data/ (sync_user_data.py)
                    ↕
                 Git repo (version controlled)

Version upgrade:
  Hermes starts → user_data_guard.py checks constitution
  → if missing: auto-restore from user-data/
  → if user-data/ missing: log ERROR, prompt manual restore

New machine:
  1. git clone repo (includes user-data/)
  2. python3 scripts/sync_user_data.py --restore
  3. Manually set .env and auth.json
  4. Done
```
