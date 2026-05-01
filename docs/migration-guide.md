# Hermes Agent Migration Guide

Complete guide for migrating a Hermes Agent installation — between servers, between profiles, or both.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Data Inventory](#2-data-inventory)
3. [Server-to-Server Migration](#3-server-to-server-migration)
4. [Profile-to-Profile Migration](#4-profile-to-profile-migration)
5. [SQLite Database Migration](#5-sqlite-database-migration)
6. [Security Considerations](#6-security-considerations)
7. [Post-Migration Validation](#7-post-migration-validation)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Overview

### What is HERMES_HOME?

All Hermes runtime data lives under a single root directory called `HERMES_HOME`, resolved by `get_hermes_home()` in `hermes_constants.py`:

```python
def get_hermes_home() -> Path:
    val = os.environ.get("HERMES_HOME", "").strip()
    return Path(val) if val else Path.home() / ".hermes"
```

Default: `~/.hermes`. Profiles use `~/.hermes/profiles/<name>/`.

### Migration Scenarios

| Scenario | Description |
|----------|-------------|
| Server-to-server | Move entire installation to a new machine |
| Profile creation | Create a new isolated profile from existing data |
| Profile merge | Combine two profiles into one |
| Profile split | Separate one profile into domain-specific profiles |
| Backup & restore | Create portable archives for disaster recovery |

### Key Principles

1. **All paths use `get_hermes_home()`** — never hardcode `~/.hermes`
2. **SQLite must be backed up via `sqlite3.backup()`** — not file copy (WAL mode)
3. **Runtime state must not be migrated** — PIDs, locks, gateway state are machine-specific
4. **Secrets require encrypted transport** — `.env` and `auth.json` contain API keys

---

## 2. Data Inventory

### 2.1 Must Migrate (not regeneratable)

| Path | Description | Notes |
|------|-------------|-------|
| `config.yaml` | Main settings | All config: model, providers, toolsets, terminal, display, memory, etc. |
| `.env` | API keys and secrets | **Most sensitive file** — provider keys, messaging tokens |
| `SOUL.md` | Agent persona/identity | Agent's personality definition |
| `auth.json` | Provider credential store | Active provider, credential pools, OAuth tokens |
| `.anthropic_oauth.json` | Anthropic PKCE OAuth tokens | If using Anthropic OAuth |
| `auth/google_oauth.json` | Google OAuth tokens | If using Google Workspace |
| `memories/MEMORY.md` | Agent's curated notes | Env facts, project conventions, learned things |
| `memories/USER.md` | Agent's knowledge about user | Preferences, communication style |
| `skills/` | User-created and installed skills | Including SKILL.md, scripts/, references/ |
| `cron/jobs.json` | Cron job definitions | Schedule, prompt, delivery target |
| `cron/output/` | Cron job execution history | Per-job output files |
| `sessions/sessions.json` | Gateway session store | session_key → session_id mapping |
| `sessions/saved/` | Saved conversation snapshots | |
| `state.db` | Session metadata + messages | **SQLite — use `sqlite3.backup()`** |
| `shell-hooks-allowlist.json` | Approved shell hook commands | |
| `plugins/` | User-installed plugins | Plugin code + manifests |
| `hooks/` | Shell-script hooks | |
| `skins/` | Custom skin YAML files | |
| `home/` | Per-profile HOME for subprocesses | git, ssh, gh configs |
| `scripts/` | User scripts | Referenced by cron jobs |

### 2.2 Migrate Selectively (large or conditional)

| Path | Description | When to Include |
|------|-------------|-----------------|
| `whatsapp/session/` | WhatsApp credentials | Only if using WhatsApp |
| `slack_tokens.json` | Slack token store | Only if using Slack |
| `slack-manifest.json` | Slack app manifest | Only if using Slack |
| `feishu_seen_message_ids.json` | Feishu dedup state | Only if using Feishu |
| `feishu_comment_rules.json` | Feishu comment rules | Only if using Feishu |
| `feishu_comment_pairing.json` | Feishu comment pairing | Only if using Feishu |
| `{platform}_threads.json` | Per-platform thread maps | Only for active platforms |
| `pairing/` | DM pairing data | If using DM pairing |
| `channel_directory.json` | Channel directory | If using channel-based routing |
| `sticker_cache.json` | Sticker cache | Optional — regeneratable |
| `honcho.json` | Honcho memory provider | Only if using Honcho |
| `mem0.json` | Mem0 memory provider | Only if using Mem0 |
| `hindsight/config.json` | Hindsight memory provider | Only if using Hindsight |
| `memory_store.db` | Holographic memory store | Only if using Holographic |
| `byterover/` | Byterover memory data | Only if using Byterover |
| `workspace/` | Workspace data | If using Google Meet bot etc. |
| `plans/` | Plan files | If using plan mode |
| `logs/` | Log files | Recent only if needed for debugging |
| `cron/output/` | Job output history | Optional — historical only |
| `dashboard-themes/` | Dashboard themes | If customized |
| `mcp/` | MCP server state | If using MCP servers |
| `google_token.json` | Google Workspace token | If using Google integration |

### 2.3 Do NOT Migrate (transient, machine-specific, or regeneratable)

| Path | Reason |
|------|--------|
| `gateway.pid` | Process ID — transient |
| `gateway_state.json` | Runtime state — transient |
| `gateway_voice_mode.json` | Voice mode toggle — transient |
| `processes.json` | Running process registry — transient |
| `.clean_shutdown` | Shutdown marker — transient |
| `.update_pending.json` | Update state — transient |
| `.update_pending.claimed.json` | Update claim — transient |
| `.update_output.txt` | Update output — transient |
| `.update_exit_code` | Update exit code — transient |
| `.update_check` | Update timestamp — transient |
| `.restart_notify.json` | Restart notification — transient |
| `.restart_last_processed.json` | Restart tracking — transient |
| `.sync.lock` | File sync lock — transient |
| `cron.pid` | Cron PID — transient |
| `state.db-wal` | SQLite WAL journal — regenerated on open |
| `state.db-shm` | SQLite shared memory — regenerated on open |
| `state.db-journal` | SQLite rollback journal — transient |
| `cache/` | All caches — regenerated on use |
| `cache/images/` | Generated images — regeneratable |
| `cache/model_catalog.json` | Model catalog cache — regeneratable |
| `image_cache/` | Legacy image cache — regeneratable |
| `audio_cache/` | TTS audio cache — regeneratable |
| `document_cache/` | Document cache — regeneratable |
| `context_length_cache.yaml` | Model context length cache — regeneratable |
| `ollama_cloud_models_cache.json` | Ollama cloud models cache — regeneratable |
| `models_dev_cache.json` | xAI models dev cache — regeneratable |
| `.skills_prompt_snapshot.json` | Skills prompt cache — transient |
| `browser_screenshots/` | Browser screenshots — regeneratable |
| `camofox-state/` | Camofox browser state — regeneratable |
| `chrome-debug/` | Chrome debug profile — regeneratable |
| `sandboxes/` | Sandbox environments — machine-specific |
| `modal_snapshots.json` | Modal snapshots — machine-specific |
| `singularity_snapshots.json` | Singularity snapshots — machine-specific |
| `vercel_snapshots.json` | Vercel snapshots — machine-specific |
| `checkpoints/` | Filesystem checkpoint shadow repos — session-hash-keyed, non-portable |
| `bin/` | Installed binaries (tirith, etc.) — reinstalled on target |
| `.tirith-install-failed` | Tirith marker — transient |
| `response_store.db` | API server response store — transient |
| `spawn-trees/` | Subagent spawn records — transient |
| `pastes/pending.json` | Debug paste state — transient |
| `approval-queue/` | Pending approvals — transient |
| `skills/.hub/` | Skills hub metadata — regeneratable |
| `skills/.bundled_manifest` | Bundled skills manifest — regeneratable |
| `skills/.curator_state` | Curator state — regeneratable |
| `skills/.archive/` | Archived skills — optional, usually stale |
| `profiles/` | Other profiles — handled separately (never recursive-export) |
| `hermes-agent/` | Repo checkout — re-clone on target |
| `.worktrees/` | Git worktrees — re-clone on target |
| `node_modules/` | npm packages — reinstalled on target |

---

## 3. Server-to-Server Migration

### 3.1 Preparation

```bash
# === SOURCE SERVER ===

# 1. Stop all Hermes services
pkill -f "python -m gateway" 2>/dev/null
pkill -f "hermes" 2>/dev/null

# Wait for clean shutdown
sleep 5

# Verify no processes remain
ps aux | grep -E "hermes|gateway" | grep -v grep
```

### 3.2 Create Migration Archive

```bash
# === SOURCE SERVER ===

# Create a consistent SQLite backup (handles WAL mode)
python3 << 'PYEOF'
import sqlite3, os

db_path = os.path.expanduser("~/.hermes/state.db")
backup_path = os.path.expanduser("~/.hermes/state.db.backup")

if os.path.exists(db_path):
    src = sqlite3.connect(db_path)
    dst = sqlite3.connect(backup_path)
    src.backup(dst)
    dst.close()
    src.close()
    print(f"SQLite backup created: {backup_path}")
else:
    print("No state.db found, skipping")
PYEOF
```

```bash
# Create tar archive
# Includes: config, secrets, memory, skills, sessions, cron, platform state
# Excludes: runtime state, caches, logs, binaries, repo checkout

tar czf /tmp/hermes-migration.tar.gz \
  -C /root \
  --exclude='.hermes/gateway.pid' \
  --exclude='.hermes/gateway_state.json' \
  --exclude='.hermes/processes.json' \
  --exclude='.hermes/cron.pid' \
  --exclude='.hermes/.clean_shutdown' \
  --exclude='.hermes/.update_*' \
  --exclude='.hermes/.restart_*' \
  --exclude='.hermes/.sync.lock' \
  --exclude='.hermes/state.db-wal' \
  --exclude='.hermes/state.db-shm' \
  --exclude='.hermes/state.db-journal' \
  --exclude='.hermes/cache' \
  --exclude='.hermes/image_cache' \
  --exclude='.hermes/audio_cache' \
  --exclude='.hermes/document_cache' \
  --exclude='.hermes/checkpoints' \
  --exclude='.hermes/sandboxes' \
  --exclude='.hermes/browser_screenshots' \
  --exclude='.hermes/camofox-state' \
  --exclude='.hermes/chrome-debug' \
  --exclude='.hermes/bin' \
  --exclude='.hermes/node_modules' \
  --exclude='.hermes/hermes-agent' \
  --exclude='.hermes/.worktrees' \
  --exclude='.hermes/profiles' \
  --exclude='.hermes/response_store.db*' \
  --exclude='.hermes/spawn-trees' \
  --exclude='.hermes/approval-queue' \
  --exclude='.hermes/pastes' \
  --exclude='.hermes/.skills_prompt_snapshot.json' \
  .hermes/
```

**Optional: Include profiles separately**

```bash
# If you have named profiles, migrate them individually
tar czf /tmp/hermes-profile-wangxia.tar.gz \
  -C /root/.hermes/profiles \
  wangxia/
```

**Optional: Include logs (recent only)**

```bash
# If you want recent logs for debugging
tar czf /tmp/hermes-logs.tar.gz \
  -C /root/.hermes \
  logs/agent.log logs/errors.log logs/gateway.log
```

### 3.3 Transfer

```bash
# === SOURCE → TARGET ===

# Option A: scp (encrypted, simple)
scp /tmp/hermes-migration.tar.gz root@TARGET:/tmp/
scp /tmp/hermes-profile-wangxia.tar.gz root@TARGET:/tmp/  # if applicable

# Option B: rsync (resumable, bandwidth-efficient)
rsync -avz --progress /tmp/hermes-migration.tar.gz root@TARGET:/tmp/

# Option C: Direct rsync (no tar, preserves incremental changes)
rsync -avz --delete \
  --exclude='gateway.pid' \
  --exclude='gateway_state.json' \
  --exclude='processes.json' \
  --exclude='cache/' \
  --exclude='checkpoints/' \
  --exclude='sandboxes/' \
  --exclude='logs/' \
  --exclude='bin/' \
  --exclude='node_modules/' \
  --exclude='hermes-agent/' \
  --exclude='.worktrees/' \
  /root/.hermes/ root@TARGET:/root/.hermes/
```

### 3.4 Restore on Target

```bash
# === TARGET SERVER ===

# 1. Install Hermes Agent
cd /root
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"

# 2. Restore data
cd /root
tar xzf /tmp/hermes-migration.tar.gz

# 3. Restore SQLite backup (the tar includes state.db.backup)
if [ -f /root/.hermes/state.db.backup ]; then
    mv /root/.hermes/state.db.backup /root/.hermes/state.db
    echo "SQLite database restored from consistent backup"
fi

# 4. Restore profiles (if applicable)
if [ -f /tmp/hermes-profile-wangxia.tar.gz ]; then
    mkdir -p /root/.hermes/profiles
    tar xzf /tmp/hermes-profile-wangxia.tar.gz -C /root/.hermes/profiles/
fi

# 5. Set proper permissions
chmod 600 /root/.hermes/.env       # secrets
chmod 600 /root/.hermes/auth.json  # credentials
chmod 700 /root/.hermes/           # directory

# 6. Verify
hermes doctor

# 7. Start gateway
nohup python -m gateway &> /dev/null &

# 8. Start profile gateway (if applicable)
HERMES_HOME=/root/.hermes/profiles/wangxia nohup python -m gateway &> /dev/null &
```

---

## 4. Profile-to-Profile Migration

### 4.1 Profile Architecture

Profiles are fully isolated HERMES_HOME directories under `~/.hermes/profiles/<name>/`. Each contains the same structure as the default `~/.hermes/`.

**Profile directories** (created automatically by `hermes profile create`):
```python
_PROFILE_DIRS = [
    "memories", "sessions", "skills", "skins",
    "logs", "plans", "workspace", "cron", "home",
]
```

**Clone defaults** (what `hermes profile create <name> --clone` copies):
```python
_CLONE_CONFIG_FILES = ["config.yaml", ".env", "SOUL.md"]
_CLONE_SUBDIR_FILES = ["memories/MEMORY.md", "memories/USER.md"]
```

**Clone all** (`--clone-all`) copies everything except runtime state:
```python
_CLONE_ALL_STRIP = ["gateway.pid", "gateway_state.json", "processes.json"]
```

### 4.2 Create New Profile from Default

```bash
# Using built-in command (recommended)
hermes profile create newprofile --clone-all

# Or manual:
mkdir -p ~/.hermes/profiles/newprofile/{memories,sessions,skills,skins,logs,plans,workspace,cron,home}

# Copy core config
cp ~/.hermes/config.yaml ~/.hermes/profiles/newprofile/
cp ~/.hermes/.env ~/.hermes/profiles/newprofile/
cp ~/.hermes/SOUL.md ~/.hermes/profiles/newprofile/
cp ~/.hermes/auth.json ~/.hermes/profiles/newprofile/

# Copy memory
cp ~/.hermes/memories/MEMORY.md ~/.hermes/profiles/newprofile/memories/
cp ~/.hermes/memories/USER.md ~/.hermes/profiles/newprofile/memories/

# Copy skills (options)
# Option A: Shared skills via symlink (all profiles see same skills)
ln -s ~/.hermes/skills ~/.hermes/profiles/newprofile/skills

# Option B: Independent copy (each profile has its own)
cp -r ~/.hermes/skills ~/.hermes/profiles/newprofile/skills

# Copy cron
cp ~/.hermes/cron/jobs.json ~/.hermes/profiles/newprofile/cron/

# Copy SQLite sessions
python3 << 'PYEOF'
import sqlite3, os
src = sqlite3.connect(os.path.expanduser("~/.hermes/state.db"))
dst = sqlite3.connect(os.path.expanduser("~/.hermes/profiles/newprofile/state.db"))
src.backup(dst)
dst.close()
src.close()
PYEOF

# Start
HERMES_HOME=~/.hermes/profiles/newprofile nohup python -m gateway &
```

### 4.3 Merge Two Profiles

**Warning: Merging is manual and lossy. Config conflicts must be resolved by hand.**

```bash
# SOURCE: ~/.hermes/profiles/wangxia
# TARGET: ~/.hermes (default)

# 1. Merge config.yaml — MUST be manual (YAML merge of conflicting keys)
# Open both files and reconcile by hand. Key areas that may conflict:
#   - model, providers (different default models)
#   - messaging platform configs (different tokens)
#   - terminal.cwd (different working directories)
#   - memory limits (different char limits)

# 2. Merge memory — append, don't overwrite
cat ~/.hermes/profiles/wangxia/memories/MEMORY.md >> ~/.hermes/memories/MEMORY.md
cat ~/.hermes/profiles/wangxia/memories/USER.md >> ~/.hermes/memories/USER.md

# Then edit MEMORY.md to deduplicate and reorganize

# 3. Merge skills — copy new ones, don't overwrite existing
cp -rn ~/.hermes/profiles/wangxia/skills/* ~/.hermes/skills/ 2>/dev/null

# 4. Merge cron — manually add wangxia's jobs to default's jobs.json
# Edit ~/.hermes/cron/jobs.json and add entries from wangxia's cron/jobs.json
# Ensure job IDs don't collide

# 5. Merge sessions — import session files
cp ~/.hermes/profiles/wangxia/sessions/*.jsonl ~/.hermes/sessions/ 2>/dev/null

# 6. Merge SQLite — NOT directly mergeable
# Sessions are stored in SQLite with auto-increment IDs.
# The only way to merge is via session_search and re-import,
# or by keeping the larger state.db and accepting data loss.
# RECOMMENDATION: Keep both profiles running and use /search across them.
```

### 4.4 Split Profile into Domain-Specific Profiles

```bash
# Create separate profiles for different domains
hermes profile create research --clone
hermes profile create operations --clone
hermes profile create personal --clone

# For each profile, customize:
# 1. Edit config.yaml — set domain-specific model, toolsets, cwd
# 2. Edit SOUL.md — set domain-specific persona
# 3. Edit memories/MEMORY.md — keep only domain-relevant entries
# 4. Edit memories/USER.md — keep only domain-relevant preferences
# 5. Clean skills/ — remove skills not needed for this domain
# 6. Clean cron/jobs.json — keep only domain-relevant jobs

# Start each
HERMES_HOME=~/.hermes/profiles/research nohup python -m gateway &
HERMES_HOME=~/.hermes/profiles/operations nohup python -m gateway &
HERMES_HOME=~/.hermes/profiles/personal nohup python -m gateway &
```

---

## 5. SQLite Database Migration

### 5.1 Why Not File Copy?

`state.db` operates in **WAL (Write-Ahead Logging) mode**. A raw file copy can produce a torn or inconsistent database because:

1. The WAL file (`state.db-wal`) may contain uncommitted transactions
2. The shared-memory file (`state.db-shm`) tracks WAL read pointers
3. Copying `.db` + `.wal` + `.shm` separately can produce mismatched snapshots

### 5.2 Correct Method: `sqlite3.backup()`

```python
import sqlite3

def backup_hermes_db(source_path, target_path):
    """Create a consistent backup of a WAL-mode SQLite database."""
    source = sqlite3.connect(source_path)
    target = sqlite3.connect(target_path)
    source.backup(target)  # ACID-consistent copy
    target.close()
    source.close()

# Usage
backup_hermes_db(
    os.path.expanduser("~/.hermes/state.db"),
    "/tmp/hermes-state.db.backup"
)
```

This is the same method used by `hermes backup` internally (see `hermes_cli/backup.py:_safe_copy_db()`).

### 5.3 Database Contents

| Table | Contents | Migration Notes |
|-------|----------|-----------------|
| `sessions` | Session metadata (model, tokens, cost, timestamps) | Portable across machines |
| `messages` | Full message history (role, content, tool calls, reasoning) | Portable — but session IDs must match |
| `messages_fts` | FTS5 search index on content + tool_name + tool_calls | Auto-rebuilt on target if missing |
| `messages_fts_trigram` | Trigram FTS5 for CJK substring search | Auto-rebuilt on target if missing |
| `state_meta` | Key-value store | Portable |
| `schema_version` | Schema version tracking | Portable — currently version 11 |

### 5.4 Large Database Handling

If `state.db` is very large (months of conversations):

```bash
# Check size
du -sh ~/.hermes/state.db

# Option A: Migrate as-is (simplest)
python3 -c "
import sqlite3
src = sqlite3.connect('$HOME/.hermes/state.db')
dst = sqlite3.connect('/tmp/state.db')
src.backup(dst)
dst.close()
src.close()
"
rsync -avz /tmp/state.db root@TARGET:/root/.hermes/state.db

# Option B: Prune old sessions before migration
python3 << 'PYEOF'
import sqlite3

db = sqlite3.connect(os.path.expanduser("~/.hermes/state.db"))
cursor = db.cursor()

# Delete sessions older than 90 days
cutoff = "2025-01-01"  # adjust date
cursor.execute("SELECT id FROM sessions WHERE ended_at < ?", (cutoff,))
old_ids = [row[0] for row in cursor.fetchall()]

for sid in old_ids:
    cursor.execute("DELETE FROM messages WHERE session_id = ?", (sid,))
    cursor.execute("DELETE FROM sessions WHERE id = ?", (sid,))

db.commit()
db.execute("INSERT INTO state_meta (key, value) VALUES ('rebuild_fts', '1')")
db.commit()

# Rebuild FTS indexes
db.execute("INSERT INTO messages_fts(messages_fts) VALUES('rebuild')")
db.execute("INSERT INTO messages_fts_trigram(messages_fts_trigram) VALUES('rebuild')")
db.commit()

# Vacuum to reclaim space
db.execute("VACUUM")
db.close()
PYEOF
```

---

## 6. Security Considerations

### 6.1 Sensitive Files

| File | Contents | Risk Level | Required Protection |
|------|----------|------------|---------------------|
| `.env` | All API keys (OpenAI, Anthropic, Telegram, etc.) | **CRITICAL** | Encrypted transport only, chmod 600 |
| `auth.json` | Provider credentials, OAuth tokens, credential pools | **CRITICAL** | Encrypted transport only, chmod 600 |
| `.anthropic_oauth.json` | Anthropic PKCE tokens | **HIGH** | Encrypted transport only |
| `auth/google_oauth.json` | Google OAuth tokens | **HIGH** | Encrypted transport only |
| `google_token.json` | Google Workspace API token | **HIGH** | Encrypted transport only |
| `whatsapp/session/creds.json` | WhatsApp session credentials | **HIGH** | Encrypted transport only |
| `slack_tokens.json` | Slack bot/workspace tokens | **HIGH** | Encrypted transport only |
| `config.yaml` | May contain tokens in platform sections | **MEDIUM** | Encrypted transport recommended |
| `state.db` | Full conversation history | **MEDIUM** | Encrypted transport recommended |
| `SOUL.md` | Agent persona | **LOW** | No special handling needed |
| `memories/` | Agent notes about user/environment | **MEDIUM** | Encrypted transport recommended |

### 6.2 Transport Security

```bash
# CORRECT: scp/rsync (encrypted by default)
scp hermes-migration.tar.gz root@TARGET:/tmp/
rsync -avz .hermes/ root@TARGET:/root/.hermes/

# CORRECT: Encrypted archive (for storage or unencrypted transport)
gpg --symmetric --cipher-algo AES256 hermes-migration.tar.gz
# Output: hermes-migration.tar.gz.gpg (password-protected)

# WRONG: HTTP/FTP (unencrypted)
curl -T hermes-migration.tar.gz http://TARGET/upload  # NEVER DO THIS
```

### 6.3 Post-Migration Cleanup

```bash
# On source server: securely wipe migration archive
shred -u /tmp/hermes-migration.tar.gz

# On target server: set restrictive permissions
chmod 700 ~/.hermes/
chmod 600 ~/.hermes/.env
chmod 600 ~/.hermes/auth.json
chmod 600 ~/.hermes/state.db

# Verify no secrets in world-readable files
find ~/.hermes -perm /o+r -name "*.json" -o -name "*.env" -o -name "*.yaml" | head -20
```

### 6.4 Secret Rotation (Recommended)

After migration to a new server, consider rotating high-value secrets:

1. **Telegram bot token** — @BotFather → Revoke token → Update `.env`
2. **Discord bot token** — Discord Developer Portal → Reset token → Update `.env`
3. **API keys** — Provider dashboards → Regenerate key → Update `.env`
4. **Slack tokens** — Slack App Admin → Rotate → Update `.env`

This is especially important if the source server is being decommissioned or shared.

---

## 7. Post-Migration Validation

### 7.1 Automated Checks

```bash
# Run built-in diagnostics
hermes doctor

# Expected output:
# ✓ config.yaml: Found and valid
# ✓ .env: Found
# ✓ Model provider: Connected
# ✓ Tools: N tools available
# ✓ Memory: Loaded
# ✓ Skills: N skills loaded
```

### 7.2 Manual Verification Checklist

```bash
# 1. Config loaded correctly
hermes config get model
hermes config get terminal.cwd

# 2. Memory intact
cat ~/.hermes/memories/MEMORY.md | head -5
cat ~/.hermes/memories/USER.md | head -5

# 3. Skills available
hermes skills list

# 4. Sessions searchable
hermes session search "recent topic"

# 5. Cron jobs present
cat ~/.hermes/cron/jobs.json | python3 -m json.tool | head -20

# 6. API key works (quick test)
hermes chat "Hello, are you working?"

# 7. Gateway starts and connects
hermes gateway status
```

### 7.3 Profile-Specific Validation

```bash
# For each profile, validate independently
HERMES_HOME=~/.hermes/profiles/wangxia hermes doctor
HERMES_HOME=~/.hermes/profiles/wangxia hermes config get model
```

---

## 8. Troubleshooting

### 8.1 "state.db is locked"

**Cause**: Source server still has a running Hermes process.

```bash
# Find and stop the process
lsof ~/.hermes/state.db
pkill -f "python -m gateway"
```

### 8.2 "database disk image is malformed"

**Cause**: Database was copied while in WAL mode without `sqlite3.backup()`.

```bash
# Attempt recovery
python3 << 'PYEOF'
import sqlite3
db = sqlite3.connect(os.path.expanduser("~/.hermes/state.db"))
db.execute("PRAGMA integrity_check")
# If corrupted, try:
db.execute("REINDEX")
db.execute("VACUUM")
db.close()
PYEOF

# If still broken, restore from backup
cp ~/.hermes/state.db.backup ~/.hermes/state.db
```

### 8.3 "Permission denied" on .env

**Cause**: File permissions from source server don't match target user.

```bash
chown $(whoami) ~/.hermes/.env
chmod 600 ~/.hermes/.env
```

### 8.4 Gateway fails to start — "Address already in use"

**Cause**: Old gateway process still running, or port conflict.

```bash
# Find the process
lsof -i :8080  # or whatever port

# Kill it
kill -9 <PID>

# Or change the port
hermes config set gateway.port 8081
```

### 8.5 Platform adapter fails to connect

**Cause**: Platform tokens in `.env` are invalid or the platform webhook URL still points to the old server.

```bash
# Verify token
hermes gateway status

# Update webhook URL (platform-specific)
# Telegram: Use @BotFather to set new webhook
# Discord: Bot connects outbound — no webhook needed
# Slack: Update Event Subscriptions URL in app settings
# Feishu: Update event subscription URL in app console
```

### 8.6 Skills not loading

**Cause**: Symlinked skills directory points to wrong location after migration.

```bash
# Check if skills is a symlink
ls -la ~/.hermes/skills

# If broken symlink, recreate or copy
rm ~/.hermes/skills
cp -r /correct/path/skills ~/.hermes/skills
# OR fix symlink:
ln -sf /correct/path/skills ~/.hermes/skills
```

### 8.7 Cron jobs not running

**Cause**: `scripts/` directory paths in cron jobs reference old server paths.

```bash
# Check cron jobs for hardcoded paths
cat ~/.hermes/cron/jobs.json | grep "/old/server/path"

# Update paths to new server
# Edit cron/jobs.json manually or via:
hermes cron list
hermes cron edit <job_id>
```

### 8.8 Memory char limit exceeded after merge

**Cause**: Merging two MEMORY.md files exceeded the character limit.

```bash
# Check size
wc -c ~/.hermes/memories/MEMORY.md

# Current limits (check your config)
hermes config get memory.char_limit       # default: 2200
hermes config get memory.user_char_limit  # default: 1375

# Options:
# 1. Increase limit (doubles token usage)
hermes config set memory.char_limit 4400

# 2. Manually trim MEMORY.md
# Edit the file and remove low-value entries

# 3. Ask the agent to consolidate
hermes chat "Please consolidate my MEMORY.md — keep the most important entries within the character limit"
```

---

## Appendix A: Quick Reference — Single Command Migration

For experienced users who just need to move everything quickly:

```bash
# === SOURCE (stop services first) ===
pkill -f "python -m gateway"; sleep 5
python3 -c "import sqlite3,os; s=sqlite3.connect(os.path.expanduser('~/.hermes/state.db')); t=sqlite3.connect(os.path.expanduser('~/.hermes/state.db.migrate')); s.backup(t); t.close(); s.close()"
tar czf /tmp/hermes-migration.tar.gz \
  --exclude='*.pid' --exclude='*_state.json' --exclude='processes.json' \
  --exclude='cache' --exclude='checkpoints' --exclude='sandboxes' \
  --exclude='browser_screenshots' --exclude='camofox-state' \
  --exclude='chrome-debug' --exclude='bin' --exclude='node_modules' \
  --exclude='hermes-agent' --exclude='.worktrees' \
  --exclude='profiles' --exclude='logs' \
  --exclude='*.db-wal' --exclude='*.db-shm' --exclude='*.db-journal' \
  --exclude='.update_*' --exclude='.restart_*' --exclude='.sync.lock' \
  --exclude='.clean_shutdown' --exclude='approval-queue' \
  --exclude='spawn-trees' --exclude='pastes' \
  -C /root .hermes/
scp /tmp/hermes-migration.tar.gz root@TARGET:/tmp/

# === TARGET ===
cd /root && git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent && python3.11 -m venv .venv && source .venv/bin/activate && pip install -e ".[all]"
cd /root && tar xzf /tmp/hermes-migration.tar.gz
[ -f .hermes/state.db.migrate ] && mv .hermes/state.db.migrate .hermes/state.db
chmod 600 .hermes/.env .hermes/auth.json
hermes doctor && nohup python -m gateway &
```

## Appendix B: Migration with Profiles

```bash
# Migrate default profile + all named profiles

# === SOURCE ===
pkill -f "python -m gateway"; sleep 5

# Backup SQLite for default
python3 -c "import sqlite3,os; s=sqlite3.connect(os.path.expanduser('~/.hermes/state.db')); t=sqlite3.connect(os.path.expanduser('~/.hermes/state.db.migrate')); s.backup(t); t.close(); s.close()"

# Backup SQLite for each profile
for profile_dir in ~/.hermes/profiles/*/; do
    profile_name=$(basename "$profile_dir")
    if [ -f "$profile_dir/state.db" ]; then
        python3 -c "import sqlite3; s=sqlite3.connect('$profile_dir/state.db'); t=sqlite3.connect('${profile_dir}state.db.migrate'); s.backup(t); t.close(); s.close()"
        echo "Backed up state.db for profile: $profile_name"
    fi
done

# Create archives
tar czf /tmp/hermes-default.tar.gz --exclude='*.pid' --exclude='*_state.json' \
  --exclude='processes.json' --exclude='cache' --exclude='checkpoints' \
  --exclude='sandboxes' --exclude='browser_screenshots' --exclude='camofox-state' \
  --exclude='chrome-debug' --exclude='bin' --exclude='node_modules' \
  --exclude='hermes-agent' --exclude='.worktrees' --exclude='profiles' \
  --exclude='logs' --exclude='*.db-wal' --exclude='*.db-shm' \
  --exclude='*.db-journal' --exclude='.update_*' --exclude='.restart_*' \
  --exclude='.sync.lock' --exclude='.clean_shutdown' --exclude='approval-queue' \
  --exclude='spawn-trees' --exclude='pastes' \
  -C /root .hermes/

tar czf /tmp/hermes-profiles.tar.gz -C /root/.hermes profiles/

scp /tmp/hermes-default.tar.gz /tmp/hermes-profiles.tar.gz root@TARGET:/tmp/

# === TARGET ===
cd /root && git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent && python3.11 -m venv .venv && source .venv/bin/activate && pip install -e ".[all]"
cd /root && tar xzf /tmp/hermes-default.tar.gz
mkdir -p .hermes/profiles && tar xzf /tmp/hermes-profiles.tar.gz -C .hermes/

# Restore SQLite backups
[ -f .hermes/state.db.migrate ] && mv .hermes/state.db.migrate .hermes/state.db
for profile_dir in .hermes/profiles/*/; do
    [ -f "${profile_dir}state.db.migrate" ] && mv "${profile_dir}state.db.migrate" "${profile_dir}state.db"
done

chmod 600 .hermes/.env .hermes/auth.json
hermes doctor

# Start gateways
nohup python -m gateway &
for profile_dir in .hermes/profiles/*/; do
    profile_name=$(basename "$profile_dir")
    HERMES_HOME="$profile_dir" nohup python -m gateway &
    echo "Started gateway for profile: $profile_name"
done
```
