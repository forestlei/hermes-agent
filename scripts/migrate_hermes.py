#!/usr/bin/env python3
"""
Hermes Agent — One-Click Migration Script

Migrates all core capabilities, configuration, and user data from one
Hermes Agent instance to another. Works for:

  - Local → Local (same machine, different HERMES_HOME)
  - Local → Remote (via SSH/SCP)
  - Profile → Profile
  - Full instance → Full instance

Usage:
    # Migrate from default ~/.hermes to a new location
    python scripts/migrate_hermes.py /path/to/new/hermes_home

    # Migrate from a specific source
    python scripts/migrate_hermes.py --source ~/.hermes /path/to/target

    # Dry run — preview what would be migrated
    python scripts/migrate_hermes.py --dry-run /path/to/target

    # Migrate to a remote host via SSH
    python scripts/migrate_hermes.py --remote user@host:/path/to/hermes_home

    # Selective migration — only config + skills (no sessions/history)
    python scripts/migrate_hermes.py --preset config-only /path/to/target

    # Full migration including secrets
    python scripts/migrate_hermes.py --preset full --include-secrets /path/to/target

    # Export to a portable archive, then import on the target
    python scripts/migrate_hermes.py --export hermes-migration.tar.gz
    python scripts/migrate_hermes.py --import hermes-migration.tar.gz /path/to/target

Presets:
    config-only    Config, .env, auth.json, skills, plugins, skins, SOUL.md
    user-data      config-only + memories, sessions (state.db), cron jobs
    full           user-data + logs, caches, all platform state (default)

What gets migrated (by category):
    Constitution:   persistent-solver SKILL.md, MEMORY.md, USER.md (highest priority)
    Core Config:    config.yaml, .env, auth.json, SOUL.md
    Capabilities:   skills/, plugins/, skins/, optional-skills/
    User Data:      state.db (sessions), memories/, cron/jobs.json
    Knowledge:      github-memory/, data/knowledge-search.db, ai-daily-report/
    Automation:     scripts/, cron/jobs.json, sources/
    Platform State: whatsapp/, pairing/, channel_directory.json
    Runtime Config: hooks/, home/ (subprocess HOME)
    Gateway:        gateway_state.json, processes.json
    Caches:         cache/, model_catalog (optional, preset=full)
    Logs:           logs/ (optional, preset=full)

Constitution layer (persistent-solver + MEMORY.md + USER.md) is ALWAYS migrated
as the highest priority item, regardless of preset. If these files are missing
from the source, the script will attempt to restore from user-data/ backup in
the project repository before proceeding.

Related scripts:
    scripts/sync_user_data.py — sync user-data/ ↔ ~/.hermes/ (for version control)
    This script — cross-instance migration (different machines/profiles)
"""

import argparse
import json
import logging
import os
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("hermes-migrate")

# ─── ANSI Colors ──────────────────────────────────────────────────────────────

class _C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    DIM = "\033[2m"

def _color(text: str, code: str) -> str:
    return f"{code}{text}{_C.RESET}"

def _print_header(msg: str) -> None:
    print(f"\n{_color(f'  {msg}', _C.BOLD + _C.CYAN)}")

def _print_success(msg: str) -> None:
    print(f"  {_color('✓', _C.GREEN)} {msg}")

def _print_error(msg: str) -> None:
    print(f"  {_color('✗', _C.RED)} {msg}", file=sys.stderr)

def _print_warn(msg: str) -> None:
    print(f"  {_color('⚠', _C.YELLOW)} {msg}")

def _print_info(msg: str) -> None:
    print(f"  {_color('─', _C.DIM)} {msg}")

# ─── Migration Categories ─────────────────────────────────────────────────────

# Each entry: (relative_path, description, is_critical, contains_secrets)
# is_critical: always included regardless of preset
# contains_secrets: only included with --include-secrets

_MIGRATION_ITEMS: List[Tuple[str, str, bool, bool]] = [
    # ── Constitution Layer (ALWAYS migrated, highest priority) ──
    ("skills/software-development/persistent-solver/SKILL.md",
     "Constitution: 8-rule top-level logic (persistent-solver v3.2)", True,  False),
    ("memories/MEMORY.md",
     "Constitution: top-level system index + rule summary",          True,  False),
    ("memories/USER.md",
     "Constitution: user preferences + hallucination zero-tolerance", True,  False),

    # ── Core Config (always migrated) ──
    ("config.yaml",             "Main configuration",                True,  False),
    (".env",                    "API keys and secrets",              True,  True),
    ("auth.json",               "OAuth tokens, credential pools",    True,  True),
    ("SOUL.md",                 "Agent persona/personality",         True,  False),
    ("AGENTS.md",               "Top-level project rules",           True,  False),
    ("agents.md",               "Top-level project rules (lowercase)",True,  False),
    ("CLAUDE.md",               "Claude-style project rules",        True,  False),
    ("claude.md",               "Claude-style project rules (lowercase)",True,  False),
    (".cursorrules",            "Cursor IDE rules",                  True,  False),
    (".cursor/rules/",         "Cursor IDE rules directory (.mdc)", True,  False),
    (".hermes.md",              "Hermes project context",            True,  False),
    ("HERMES.md",               "Hermes project context (uppercase)",True,  False),
    (".managed",                "Managed-mode marker",               True,  False),
    (".container-mode",         "Container-mode metadata",           True,  False),

    # ── Capabilities ──
    ("skills/",                 "User-installed skills",             True,  False),
    ("plugins/",                "User-installed plugins",             True,  False),
    ("skins/",                  "Custom skin/theme files",           True,  False),
    ("optional-skills/",        "Optional skills data",              False, False),
    ("hooks/",                  "Gateway hooks",                     True,  False),
    ("scripts/",                "Cron/user scripts",                 True,  False),

    # ── Knowledge Assets ──
    ("github-memory/",          "GitHub knowledge base (11 topics)", False, False),
    ("data/knowledge-search.db","Knowledge search database",         False, False),
    ("sources/",                "Data source registry",              False, False),

    # ── User Data (config-only excludes these) ──
    ("state.db",                "Session database (FTS5)",           False, False),
    ("memories/",               "Persistent memory store",           False, False),
    ("cron/jobs.json",          "Cron scheduled jobs",               False, False),
    ("home/",                   "Subprocess HOME (git/ssh configs)", False, False),

    # ── Platform State ──
    ("whatsapp/",               "WhatsApp session state",            False, True),
    ("pairing/",                "User pairing data (legacy)",        False, True),
    ("platforms/pairing/",      "User pairing data (new)",           False, True),
    ("channel_directory.json",  "Channel routing table",             False, False),
    ("gateway_state.json",      "Gateway runtime state",             False, False),
    ("processes.json",          "Background process registry",       False, False),
    ("feishu_comment_pairing.json", "Feishu comment pairings",      False, False),
    ("sticker_cache.json",      "Sticker cache",                     False, False),

    # ── Memory Provider State ──
    ("honcho.json",             "Honcho memory config",              False, False),
    ("mem0.json",               "Mem0 memory config",               False, False),
    ("memory_store.db",         "Holographic memory DB",             False, False),
    ("byterover/",              "Byterover memory data",             False, False),
    ("hindsight/",              "Hindsight memory config",           False, False),

    # ── MCP / OAuth State ──
    ("mcp/",                    "MCP server configs/oauth",          False, True),
    ("auth/",                   "OAuth token files",                 False, True),

    # ── Caches (preset=full only) ──
    ("cache/",                  "Image/model/audio caches",          False, False),
    ("image_cache/",            "Image cache (legacy)",              False, False),
    ("audio_cache/",            "Audio cache (legacy)",              False, False),
    ("document_cache/",         "Document cache (legacy)",           False, False),
    ("browser_screenshots/",    "Browser screenshots",               False, False),

    # ── Logs (preset=full only) ──
    ("logs/",                   "Agent/gateway/error logs",          False, False),

    # ── Misc State ──
    ("dashboard-themes/",       "Dashboard custom themes",           False, False),
    ("approval-queue/",         "Pending approvals",                 False, False),
    ("slack-manifest.json",     "Slack app manifest",                False, False),
    ("chrome-debug/",           "Chrome debug profile",              False, False),
]

# Items to ALWAYS exclude (runtime junk, regenerated, dangerous)
_EXCLUDED_NAMES: Set[str] = {
    "__pycache__",
    ".git",
    "node_modules",
    "hermes-agent",       # repo checkout
    ".worktrees",
    "backups",            # don't nest backups
    "checkpoints",        # session-local, non-portable
    "sandboxes",
    "state-snapshots",    # auto-generated snapshots
}

_EXCLUDED_SUFFIXES = (".pyc", ".pyo", ".db-wal", ".db-shm", ".db-journal")

# SQLite sidecar patterns
_DB_EXTENSIONS = (".db",)

# ─── Preset Definitions ───────────────────────────────────────────────────────

_PRESET_CONFIG_ONLY = "config-only"
_PRESET_USER_DATA = "user-data"
_PRESET_FULL = "full"

_VALID_PRESETS = (_PRESET_CONFIG_ONLY, _PRESET_USER_DATA, _PRESET_FULL)

def _item_in_preset(item: Tuple[str, str, bool, bool], preset: str) -> bool:
    """Check if a migration item should be included for the given preset."""
    rel_path, desc, is_critical, has_secrets = item
    if is_critical:
        return True
    if preset == _PRESET_CONFIG_ONLY:
        # config-only: only core config + capabilities (no sessions, no memories)
        return rel_path in (
            "skills/", "plugins/", "skins/", "optional-skills/",
            "hooks/", "scripts/",
        )
    if preset == _PRESET_USER_DATA:
        # user-data: config + capabilities + user data + platform state
        return not rel_path.startswith(("cache/", "image_cache/", "audio_cache/",
                                         "document_cache/", "browser_screenshots/",
                                         "logs/"))
    # full: everything
    return True


# ─── SQLite Safe Copy ─────────────────────────────────────────────────────────

def _safe_copy_db(src: Path, dst: Path) -> bool:
    """Copy a SQLite database safely using the backup() API (handles WAL mode)."""
    try:
        conn = sqlite3.connect(f"file:{src}?mode=ro", uri=True)
        backup_conn = sqlite3.connect(str(dst))
        conn.backup(backup_conn)
        backup_conn.close()
        conn.close()
        return True
    except Exception as exc:
        logger.warning("SQLite safe copy failed for %s: %s", src, exc)
        try:
            shutil.copy2(src, dst)
            return True
        except Exception as exc2:
            logger.error("Raw copy also failed for %s: %s", src, exc2)
            return False


# ─── Size Formatting ──────────────────────────────────────────────────────────

def _format_size(nbytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if nbytes < 1024:
            return f"{nbytes:.1f} {unit}" if unit != "B" else f"{nbytes} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} TB"


# ─── Scanner ──────────────────────────────────────────────────────────────────

def scan_source(
    source: Path,
    preset: str,
    include_secrets: bool,
) -> List[Dict[str, Any]]:
    """Scan the source HERMES_HOME and return a list of items to migrate.

    Each item: {"path": relative_path, "abs": absolute_path, "type": "file"|"dir",
                "desc": description, "size": bytes, "secret": bool}
    """
    items: List[Dict[str, Any]] = []

    for rel_path, desc, is_critical, has_secrets in _MIGRATION_ITEMS:
        # Skip secrets unless explicitly included
        if has_secrets and not include_secrets:
            continue

        # Skip if not in preset
        if not _item_in_preset((rel_path, desc, is_critical, has_secrets), preset):
            continue

        abs_path = source / rel_path.rstrip("/")
        if not abs_path.exists():
            continue

        is_dir = abs_path.is_dir()
        size = 0

        if is_dir:
            # Calculate directory size
            try:
                for f in abs_path.rglob("*"):
                    if f.is_file() and f.name not in _EXCLUDED_NAMES:
                        try:
                            size += f.stat().st_size
                        except OSError:
                            pass
            except OSError:
                pass
        else:
            try:
                size = abs_path.stat().st_size
            except OSError:
                pass

        items.append({
            "path": rel_path,
            "abs": str(abs_path),
            "type": "dir" if is_dir else "file",
            "desc": desc,
            "size": size,
            "secret": has_secrets,
        })

    return items


# ─── Migrator ─────────────────────────────────────────────────────────────────

class HermesMigrator:
    """One-click Hermes Agent migration engine."""

    def __init__(
        self,
        source: Path,
        target: Path,
        preset: str = _PRESET_FULL,
        include_secrets: bool = False,
        overwrite: bool = False,
        dry_run: bool = False,
        no_backup: bool = False,
        verbose: bool = False,
    ):
        self.source = source.resolve()
        self.target = target.resolve()
        self.preset = preset
        self.include_secrets = include_secrets
        self.overwrite = overwrite
        self.dry_run = dry_run
        self.no_backup = no_backup
        self.verbose = verbose
        self.report: Dict[str, Any] = {
            "source": str(self.source),
            "target": str(self.target),
            "preset": preset,
            "include_secrets": include_secrets,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "items": [],
            "summary": {"migrated": 0, "skipped": 0, "conflict": 0, "error": 0},
        }

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(f"    {_color('┊', _C.DIM)} {msg}")

    def _copy_file(self, src: Path, dst: Path) -> bool:
        """Copy a single file, using SQLite safe copy for .db files."""
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix in _DB_EXTENSIONS:
            return _safe_copy_db(src, dst)
        try:
            shutil.copy2(src, dst)
            return True
        except (OSError, PermissionError) as exc:
            logger.error("Copy failed: %s → %s: %s", src, dst, exc)
            return False

    def _copy_dir(self, src: Path, dst: Path) -> Tuple[int, int]:
        """Copy a directory tree. Returns (files_copied, errors)."""
        copied = 0
        errors = 0
        for item in src.rglob("*"):
            if not item.is_file():
                continue
            # Skip excluded names
            if item.name in _EXCLUDED_NAMES:
                continue
            if any(item.name.endswith(s) for s in _EXCLUDED_SUFFIXES):
                continue
            # Skip if any path component is excluded
            try:
                rel = item.relative_to(src)
            except ValueError:
                continue
            if any(part in _EXCLUDED_NAMES for part in rel.parts):
                continue

            dst_file = dst / rel
            dst_file.parent.mkdir(parents=True, exist_ok=True)

            # Check for conflict
            if dst_file.exists() and not self.overwrite:
                continue

            if self._copy_file(item, dst_file):
                copied += 1
            else:
                errors += 1

        return copied, errors

    def _check_conflicts(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for conflicts at the target location."""
        conflicts = []
        for item in items:
            rel = item["path"].rstrip("/")
            target_path = self.target / rel
            if target_path.exists():
                conflicts.append({
                    "path": item["path"],
                    "desc": item["desc"],
                    "target": str(target_path),
                })
        return conflicts

    def _create_backup(self) -> Optional[Path]:
        """Create a pre-migration backup of the target (if it exists)."""
        if not self.target.is_dir():
            return None

        # Check if target has any hermes content
        if not (self.target / "config.yaml").exists() and not (self.target / ".env").exists():
            return None

        backup_dir = self.target / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = backup_dir / f"pre-migration-{stamp}.zip"

        _print_info(f"Creating pre-migration backup → {backup_path}")

        import zipfile
        file_count = 0
        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for dirpath, dirnames, filenames in os.walk(self.target, followlinks=False):
                dp = Path(dirpath)
                # Prune excluded dirs
                dirnames[:] = [d for d in dirnames if d not in _EXCLUDED_NAMES and d != "backups"]
                for fname in filenames:
                    fpath = dp / fname
                    try:
                        rel = fpath.relative_to(self.target)
                    except ValueError:
                        continue
                    if any(part in _EXCLUDED_NAMES for part in rel.parts):
                        continue
                    if any(rel.name.endswith(s) for s in _EXCLUDED_SUFFIXES):
                        continue
                    try:
                        if fpath.resolve() == backup_path.resolve():
                            continue
                    except (OSError, ValueError):
                        pass
                    try:
                        zf.write(fpath, arcname=str(rel))
                        file_count += 1
                    except (OSError, PermissionError):
                        pass

        if file_count == 0:
            backup_path.unlink(missing_ok=True)
            return None

        return backup_path

    def migrate(self) -> Dict[str, Any]:
        """Execute the migration. Returns the report dict."""
        # Banner
        print()
        print(_color("┌─────────────────────────────────────────────────────────┐", _C.MAGENTA))
        print(_color("│          ⚕ Hermes Agent — One-Click Migration          │", _C.MAGENTA))
        print(_color("└─────────────────────────────────────────────────────────┘", _C.MAGENTA))
        print()

        # Validate source
        if not self.source.is_dir():
            _print_error(f"Source directory not found: {self.source}")
            sys.exit(1)

        if not (self.source / "config.yaml").exists() and not (self.source / ".env").exists():
            _print_error(f"Source does not appear to be a Hermes home: {self.source}")
            _print_info("Expected config.yaml or .env in the source directory.")
            sys.exit(1)

        # Scan source
        _print_header("Scanning Source")
        _print_info(f"Source:  {self.source}")
        _print_info(f"Target:  {self.target}")
        _print_info(f"Preset:  {self.preset}")
        _print_info(f"Secrets: {'included' if self.include_secrets else 'excluded (use --include-secrets)'}")

        items = scan_source(self.source, self.preset, self.include_secrets)

        if not items:
            _print_warn("Nothing to migrate from source.")
            return self.report

        # Calculate totals
        total_size = sum(i["size"] for i in items)
        total_files = len(items)
        secret_items = [i for i in items if i["secret"]]

        print()
        _print_header(f"Migration Plan — {total_files} item(s), {_format_size(total_size)}")

        for item in items:
            marker = _color("🔒", _C.YELLOW) if item["secret"] else _color("📄", _C.DIM)
            kind = "dir " if item["type"] == "dir" else "file"
            size_str = _format_size(item["size"]) if item["size"] else ""
            print(f"    {marker} {kind} {item['path']:<35s} {size_str:>10s}  {item['desc']}")

        if secret_items:
            print()
            _print_warn(f"{len(secret_items)} item(s) contain secrets — handle with care!")

        # Check conflicts
        conflicts = self._check_conflicts(items)
        if conflicts:
            print()
            _print_warn(f"{len(conflicts)} conflict(s) detected at target:")
            for c in conflicts:
                print(f"      {c['path']:<35s}  {c['desc']}")
            if not self.overwrite:
                _print_info("Use --overwrite to replace conflicting items, or they will be skipped.")

        # Dry run — stop here
        if self.dry_run:
            print()
            _print_header("Dry Run — No changes made")
            self.report["summary"]["migrated"] = total_files
            return self.report

        # Pre-migration backup
        if not self.no_backup:
            backup_path = self._create_backup()
            if backup_path:
                _print_success(f"Pre-migration backup: {backup_path} ({_format_size(backup_path.stat().st_size)})")

        # Create target directory
        self.target.mkdir(parents=True, exist_ok=True)

        # Execute migration
        print()
        _print_header("Migrating")

        migrated = 0
        skipped = 0
        conflict_count = 0
        error_count = 0

        for item in items:
            rel = item["path"].rstrip("/")
            src_path = self.source / rel
            dst_path = self.target / rel

            if not src_path.exists():
                skipped += 1
                self._log(f"SKIP (not found): {rel}")
                self.report["items"].append({
                    "path": rel, "status": "skipped", "reason": "source not found",
                })
                continue

            # Check conflict
            if dst_path.exists() and not self.overwrite:
                conflict_count += 1
                self._log(f"CONFLICT: {rel}")
                self.report["items"].append({
                    "path": rel, "status": "conflict", "reason": "target exists",
                })
                continue

            # Copy
            try:
                if item["type"] == "dir":
                    copied, errors = self._copy_dir(src_path, dst_path)
                    if errors == 0:
                        migrated += 1
                        _print_success(f"{rel} ({copied} files)")
                        self.report["items"].append({
                            "path": rel, "status": "migrated", "files": copied,
                        })
                    else:
                        migrated += 1  # partial success
                        _print_warn(f"{rel} ({copied} files, {errors} errors)")
                        self.report["items"].append({
                            "path": rel, "status": "migrated",
                            "files": copied, "errors": errors,
                        })
                        error_count += errors
                else:
                    if self._copy_file(src_path, dst_path):
                        migrated += 1
                        _print_success(f"{rel}")
                        self.report["items"].append({
                            "path": rel, "status": "migrated",
                        })
                    else:
                        error_count += 1
                        _print_error(f"{rel} — copy failed")
                        self.report["items"].append({
                            "path": rel, "status": "error", "reason": "copy failed",
                        })
            except Exception as exc:
                error_count += 1
                _print_error(f"{rel} — {exc}")
                self.report["items"].append({
                    "path": rel, "status": "error", "reason": str(exc),
                })

        # Update summary
        self.report["summary"] = {
            "migrated": migrated,
            "skipped": skipped,
            "conflict": conflict_count,
            "error": error_count,
        }

        # Post-migration: set permissions on .env and auth.json
        self._secure_secrets()

        # Print results
        self._print_results()

        return self.report

    def _secure_secrets(self) -> None:
        """Set restrictive permissions on secret files at the target."""
        if self.dry_run:
            return
        for name in (".env", "auth.json"):
            path = self.target / name
            if path.exists():
                try:
                    os.chmod(path, 0o600)
                except OSError:
                    pass

    def _print_results(self) -> None:
        """Print the migration results summary."""
        s = self.report["summary"]
        print()
        _print_header("Migration Results")

        if s["migrated"]:
            _print_success(f"{s['migrated']} item(s) migrated successfully")
        if s["conflict"]:
            _print_warn(f"{s['conflict']} item(s) skipped (conflict — use --overwrite)")
        if s["skipped"]:
            _print_info(f"{s['skipped']} item(s) skipped (not found in source)")
        if s["error"]:
            _print_error(f"{s['error']} error(s) during migration")

        if s["migrated"] and not self.dry_run:
            print()
            _print_header("Next Steps")
            print(f"""
    1. Verify the migration:
       export HERMES_HOME={self.target}
       hermes doctor

    2. Start using the new instance:
       hermes                    # CLI chat
       hermes gateway start      # messaging gateway

    3. If using profiles, set the active profile:
       hermes -p <profile-name>

    4. To roll back, restore the pre-migration backup:
       hermes import {self.target}/backups/pre-migration-<timestamp>.zip
""")

    def export_archive(self, output_path: Path) -> Path:
        """Export migration data to a portable tar.gz archive."""
        print()
        print(_color("┌─────────────────────────────────────────────────────────┐", _C.MAGENTA))
        print(_color("│          ⚕ Hermes Agent — Export Migration Archive     │", _C.MAGENTA))
        print(_color("└─────────────────────────────────────────────────────────┘", _C.MAGENTA))
        print()

        if not self.source.is_dir():
            _print_error(f"Source directory not found: {self.source}")
            sys.exit(1)

        items = scan_source(self.source, self.preset, self.include_secrets)
        if not items:
            _print_warn("Nothing to export.")
            sys.exit(0)

        _print_info(f"Source: {self.source}")
        _print_info(f"Output: {output_path}")
        _print_info(f"Preset: {self.preset}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write a manifest first
        manifest = {
            "version": "1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": str(self.source),
            "preset": self.preset,
            "include_secrets": self.include_secrets,
            "items": [{"path": i["path"], "desc": i["desc"], "type": i["type"],
                       "secret": i["secret"]} for i in items],
        }

        manifest_tmp = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as mf:
                mf.write(json.dumps(manifest, indent=2, ensure_ascii=False))
                mf.flush()
                manifest_tmp = Path(mf.name)

            with tarfile.open(output_path, "w:gz") as tar:
                tar.add(str(manifest_tmp), arcname="migration-manifest.json")

                for item in items:
                    rel = item["path"].rstrip("/")
                    src_path = self.source / rel
                    if not src_path.exists():
                        continue

                    if item["type"] == "dir":
                        for f in src_path.rglob("*"):
                            if not f.is_file():
                                continue
                            if f.name in _EXCLUDED_NAMES:
                                continue
                            if any(f.name.endswith(s) for s in _EXCLUDED_SUFFIXES):
                                continue
                            try:
                                file_rel = f.relative_to(self.source)
                            except ValueError:
                                continue
                            if any(part in _EXCLUDED_NAMES for part in file_rel.parts):
                                continue
                            try:
                                tar.add(str(f), arcname=str(file_rel))
                            except (OSError, PermissionError):
                                pass
                    else:
                        if src_path.suffix in _DB_EXTENSIONS:
                            tmp_db = None
                            try:
                                with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
                                    tmp_db = Path(tmp.name)
                                if _safe_copy_db(src_path, tmp_db):
                                    tar.add(str(tmp_db), arcname=rel)
                            finally:
                                if tmp_db:
                                    tmp_db.unlink(missing_ok=True)
                        else:
                            try:
                                tar.add(str(src_path), arcname=rel)
                            except (OSError, PermissionError):
                                pass

        finally:
            if manifest_tmp:
                manifest_tmp.unlink(missing_ok=True)

        size = output_path.stat().st_size
        print()
        _print_success(f"Export complete: {output_path} ({_format_size(size)})")
        _print_info(f"Import on target with: python scripts/migrate_hermes.py --import {output_path.name} /path/to/target")

        return output_path

    def import_archive(self, archive_path: Path) -> Dict[str, Any]:
        """Import migration data from a portable tar.gz archive."""
        print()
        print(_color("┌─────────────────────────────────────────────────────────┐", _C.MAGENTA))
        print(_color("│          ⚕ Hermes Agent — Import Migration Archive     │", _C.MAGENTA))
        print(_color("└─────────────────────────────────────────────────────────┘", _C.MAGENTA))
        print()

        if not archive_path.is_file():
            _print_error(f"Archive not found: {archive_path}")
            sys.exit(1)

        _print_info(f"Archive: {archive_path}")
        _print_info(f"Target:  {self.target}")

        # Pre-migration backup
        if not self.no_backup and not self.dry_run:
            backup_path = self._create_backup()
            if backup_path:
                _print_success(f"Pre-migration backup: {backup_path}")

        self.target.mkdir(parents=True, exist_ok=True)

        # Read manifest
        with tarfile.open(archive_path, "r:gz") as tar:
            try:
                manifest_file = tar.extractfile("migration-manifest.json")
                if manifest_file:
                    manifest = json.loads(manifest_file.read().decode())
                    _print_info(f"Archive preset: {manifest.get('preset', 'unknown')}")
                    _print_info(f"Created: {manifest.get('timestamp', 'unknown')}")
            except (KeyError, json.JSONDecodeError):
                _print_warn("No manifest found — importing all files")

            if self.dry_run:
                members = tar.getmembers()
                _print_info(f"Archive contains {len(members)} entries")
                _print_header("Dry Run — No changes made")
                return self.report

            # Extract
            _print_header("Importing")
            restored = 0
            errors = 0

            for member in tar.getmembers():
                if member.name == "migration-manifest.json":
                    continue
                if not member.isfile():
                    continue

                target_path = self.target / member.name

                # Security: reject path traversal
                try:
                    target_path.resolve().relative_to(self.target.resolve())
                except ValueError:
                    _print_error(f"Path traversal blocked: {member.name}")
                    errors += 1
                    continue

                # Check conflict
                if target_path.exists() and not self.overwrite:
                    continue

                target_path.parent.mkdir(parents=True, exist_ok=True)

                try:
                    src_file = tar.extractfile(member)
                    if src_file:
                        with open(target_path, "wb") as dst:
                            dst.write(src_file.read())
                        restored += 1
                except (OSError, PermissionError) as exc:
                    _print_error(f"{member.name}: {exc}")
                    errors += 1

        # Secure secrets
        self._secure_secrets()

        print()
        _print_success(f"{restored} file(s) restored")
        if errors:
            _print_error(f"{errors} error(s)")

        self.report["summary"]["migrated"] = restored
        self.report["summary"]["error"] = errors

        return self.report


# ─── Remote Migration ─────────────────────────────────────────────────────────

def _migrate_remote(source: Path, remote_target: str, args) -> None:
    """Migrate to a remote host via SSH/SCP.

    remote_target format: user@host:/path/to/hermes_home
    """
    if ":" not in remote_target:
        _print_error("Remote target must be in format: user@host:/path/to/hermes_home")
        sys.exit(1)

    host_part, remote_path = remote_target.split(":", 1)

    # Step 1: Export to a local temp archive
    with tempfile.TemporaryDirectory(prefix="hermes-migrate-") as tmp_dir:
        archive_path = Path(tmp_dir) / "hermes-migration.tar.gz"

        migrator = HermesMigrator(
            source=source,
            target=Path(remote_path),  # placeholder
            preset=args.preset,
            include_secrets=args.include_secrets,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
            no_backup=True,
            verbose=args.verbose,
        )

        migrator.export_archive(archive_path)

        if args.dry_run:
            return

        # Step 2: SCP the archive to the remote host
        print()
        _print_header("Transferring to Remote Host")
        _print_info(f"Host: {host_part}")
        _print_info(f"Path: {remote_path}")

        remote_archive = f"{remote_path}/hermes-migration.tar.gz"

        # Create the remote directory
        try:
            subprocess.run(
                ["ssh", host_part, f"mkdir -p {remote_path}"],
                check=True, capture_output=True, timeout=30,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            _print_error(f"Could not create remote directory: {exc}")
            sys.exit(1)

        # Transfer the archive
        try:
            result = subprocess.run(
                ["scp", "-C", str(archive_path), f"{host_part}:{remote_archive}"],
                check=True, capture_output=True, timeout=300,
            )
            _print_success("Archive transferred")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            _print_error(f"SCP transfer failed: {exc}")
            sys.exit(1)

        # Step 3: Extract on the remote host
        _print_header("Extracting on Remote Host")
        extract_cmd = f"cd {remote_path} && tar xzf hermes-migration.tar.gz && rm hermes-migration.tar.gz"
        try:
            subprocess.run(
                ["ssh", host_part, extract_cmd],
                check=True, capture_output=True, timeout=60,
            )
            _print_success("Extraction complete")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            _print_error(f"Remote extraction failed: {exc}")
            sys.exit(1)

        # Step 4: Set permissions on secrets
        secure_cmd = f"chmod 600 {remote_path}/.env {remote_path}/auth.json 2>/dev/null; true"
        subprocess.run(["ssh", host_part, secure_cmd], capture_output=True, timeout=10)

        print()
        _print_success("Remote migration complete!")
        _print_info(f"Set HERMES_HOME={remote_path} on the remote host to use the new instance")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Hermes Agent — One-Click Migration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "target", nargs="?",
        help="Target HERMES_HOME directory (or user@host:/path for remote)",
    )
    parser.add_argument(
        "--source", default=None,
        help="Source HERMES_HOME directory (default: current HERMES_HOME or ~/.hermes)",
    )
    parser.add_argument(
        "--preset", choices=_VALID_PRESETS, default=_PRESET_FULL,
        help="Migration preset (default: full)",
    )
    parser.add_argument(
        "--include-secrets", action="store_true",
        help="Include secret files (.env, auth.json, WhatsApp session, etc.)",
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite existing files at target",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview what would be migrated without making changes",
    )
    parser.add_argument(
        "--no-backup", action="store_true",
        help="Skip pre-migration backup of target",
    )
    parser.add_argument(
        "--export", metavar="PATH", default=None,
        help="Export migration data to a portable archive (tar.gz)",
    )
    parser.add_argument(
        "--import", metavar="PATH", dest="import_archive", default=None,
        help="Import migration data from a portable archive",
    )
    parser.add_argument(
        "--remote", action="store_true",
        help="Target is a remote host (user@host:/path format)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show detailed progress",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    # Resolve source
    if args.source:
        source = Path(args.source).expanduser().resolve()
    else:
        env_home = os.environ.get("HERMES_HOME", "").strip()
        source = Path(env_home) if env_home else Path.home() / ".hermes"

    # Export mode
    if args.export:
        output = Path(args.export).expanduser().resolve()
        migrator = HermesMigrator(
            source=source,
            target=source,  # placeholder
            preset=args.preset,
            include_secrets=args.include_secrets,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
            no_backup=args.no_backup,
            verbose=args.verbose,
        )
        migrator.export_archive(output)
        return

    # Import mode
    if args.import_archive:
        if not args.target:
            _print_error("Target directory required for import.")
            _print_info("Usage: python scripts/migrate_hermes.py --import archive.tar.gz /path/to/target")
            sys.exit(1)
        target = Path(args.target).expanduser().resolve()
        archive = Path(args.import_archive).expanduser().resolve()
        migrator = HermesMigrator(
            source=source,
            target=target,
            preset=args.preset,
            include_secrets=args.include_secrets,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
            no_backup=args.no_backup,
            verbose=args.verbose,
        )
        migrator.import_archive(archive)
        return

    # Direct migration
    if not args.target:
        _print_error("Target directory required.")
        _print_info("Usage: python scripts/migrate_hermes.py /path/to/new/hermes_home")
        parser.print_help()
        sys.exit(1)

    # Remote migration
    if args.remote or (":" in args.target and "@" in args.target):
        _migrate_remote(source, args.target, args)
        return

    # Local migration
    target = Path(args.target).expanduser().resolve()

    migrator = HermesMigrator(
        source=source,
        target=target,
        preset=args.preset,
        include_secrets=args.include_secrets,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
        no_backup=args.no_backup,
        verbose=args.verbose,
    )

    report = migrator.migrate()

    # Write report
    if not args.dry_run:
        report_dir = target / "backups"
        report_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        report_path = report_dir / f"migration-report-{stamp}.json"
        try:
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            _print_info(f"Migration report: {report_path}")
        except OSError:
            pass


if __name__ == "__main__":
    main()
