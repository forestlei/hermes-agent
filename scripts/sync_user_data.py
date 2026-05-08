#!/usr/bin/env python3
"""
sync_user_data.py — Sync Hermes user data between ~/.hermes/ and user-data/ directory.

Usage:
    python3 scripts/sync_user_data.py              # Backup: ~/.hermes/ → user-data/
    python3 scripts/sync_user_data.py --restore     # Restore: user-data/ → ~/.hermes/
    python3 scripts/sync_user_data.py --dry-run     # Preview what would be synced
    python3 scripts/sync_user_data.py --verify      # Verify sync status

This ensures user-defined content (top-level rules, skills, knowledge, automation)
is version-controlled in Git and survives version upgrades / instance migrations.
"""

import argparse
import filecmp
import json
import os
import re
import shutil
import sys
from pathlib import Path

# Resolve paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
USER_DATA_DIR = PROJECT_ROOT / "user-data"

# Try to find HERMES_HOME
def get_hermes_home() -> Path:
    """Resolve HERMES_HOME following the same logic as hermes_constants.py."""
    env = os.environ.get("HERMES_HOME")
    if env:
        return Path(env)
    return Path.home() / ".hermes"

HERMES_HOME = get_hermes_home()

# ── Sync definitions ──────────────────────────────────────────────────
# Each entry: (source_path, dest_path, category, priority, sanitize_fn)
# source_path: relative to HERMES_HOME (backup) or USER_DATA_DIR (restore)
# dest_path: relative to USER_DATA_DIR (backup) or HERMES_HOME (restore)
# category: directory name under user-data/
# priority: "critical" | "important" | "optional"
# sanitize_fn: optional function to sanitize content before writing

SYNC_ITEMS = []

def _add(src_rel: str, dst_rel: str, category: str, priority: str, is_dir: bool = False, sanitize: str = None):
    SYNC_ITEMS.append({
        "src_rel": src_rel,
        "dst_rel": dst_rel,
        "category": category,
        "priority": priority,
        "is_dir": is_dir,
        "sanitize": sanitize,
    })

# ── Constitution layer (critical) ──
_add("skills/software-development/persistent-solver/SKILL.md",
     "constitution/persistent-solver-SKILL.md", "constitution", "critical")
_add("memories/MEMORY.md", "constitution/MEMORY.md", "constitution", "critical")
_add("memories/USER.md", "constitution/USER.md", "constitution", "critical")

# ── Knowledge (critical) ──
_add("github-memory", "knowledge/github-memory", "knowledge", "critical", is_dir=True)
_add("data/knowledge-search.db", "knowledge/data/knowledge-search.db", "knowledge", "critical")

# ── Skills (important) ──
# Skills are handled specially: only SKILL.md files, not large reference dirs
# See _sync_skills() below

# ── Automation (important) ──
_add("scripts", "automation/scripts", "automation", "important", is_dir=True)
_add("cron/jobs.json", "automation/cron/jobs.json", "automation", "important")
_add("sources", "automation/sources", "automation", "important", is_dir=True)

# ── Config (important, sanitized) ──
_add("config.yaml", "config/config.yaml", "config", "important", sanitize="strip_secrets")
_add("SOUL.md", "config/SOUL.md", "config", "important")


def sanitize_config_yaml(content: str) -> str:
    """Remove API keys and secrets from config.yaml."""
    content = re.sub(r'(api_key:\s*).+', r'\1YOUR_API_KEY_HERE', content)
    content = re.sub(r'(api_base:\s*).+', r'\1YOUR_API_BASE_HERE', content)
    return content


def _sync_skills(direction: str, dry_run: bool = False) -> list:
    """Sync skills — only SKILL.md files, skip large reference directories."""
    actions = []

    if direction == "backup":
        src_base = HERMES_HOME / "skills"
        dst_base = USER_DATA_DIR / "skills"
    else:
        src_base = USER_DATA_DIR / "skills"
        dst_base = HERMES_HOME / "skills"

    if not src_base.exists():
        return actions

    # Find all SKILL.md files
    for skill_md in src_base.rglob("SKILL.md"):
        rel = skill_md.relative_to(src_base)
        dst = dst_base / rel

        if direction == "backup":
            if dry_run:
                actions.append(f"  WOULD COPY: {skill_md} → {dst}")
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(skill_md, dst)
                actions.append(f"  COPIED: {rel}")

        elif direction == "restore":
            if dry_run:
                actions.append(f"  WOULD COPY: {skill_md} → {dst}")
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(skill_md, dst)
                actions.append(f"  RESTORED: {rel}")

    # Also sync .usage.json if it exists
    usage_file = src_base / ".usage.json"
    if usage_file.exists():
        dst_usage = dst_base / ".usage.json"
        if direction == "backup":
            if dry_run:
                actions.append(f"  WOULD COPY: {usage_file} → {dst_usage}")
            else:
                shutil.copy2(usage_file, dst_usage)
                actions.append("  COPIED: .usage.json")
        elif direction == "restore":
            if dry_run:
                actions.append(f"  WOULD COPY: {usage_file} → {dst_usage}")
            else:
                shutil.copy2(usage_file, dst_usage)
                actions.append("  RESTORED: .usage.json")

    return actions


def do_backup(dry_run: bool = False) -> None:
    """Backup from ~/.hermes/ to user-data/."""
    print(f"{'[DRY RUN] ' if dry_run else ''}Backing up {HERMES_HOME} → {USER_DATA_DIR}")
    print()

    stats = {"copied": 0, "skipped": 0, "errors": 0}

    for item in SYNC_ITEMS:
        src = HERMES_HOME / item["src_rel"]
        dst = USER_DATA_DIR / item["dst_rel"]

        if not src.exists():
            print(f"  ⏭ SKIP (not found): {item['src_rel']}")
            stats["skipped"] += 1
            continue

        if item["is_dir"]:
            if dry_run:
                print(f"  WOULD SYNC DIR: {item['src_rel']} → {item['dst_rel']} [{item['priority']}]")
                stats["copied"] += 1
            else:
                try:
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                    print(f"  ✅ SYNCED DIR: {item['src_rel']} → {item['dst_rel']} [{item['priority']}]")
                    stats["copied"] += 1
                except Exception as e:
                    print(f"  ❌ ERROR: {item['src_rel']}: {e}")
                    stats["errors"] += 1
        else:
            if dry_run:
                print(f"  WOULD COPY: {item['src_rel']} → {item['dst_rel']} [{item['priority']}]")
                stats["copied"] += 1
            else:
                try:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    if item["sanitize"] == "strip_secrets":
                        content = src.read_text(encoding="utf-8")
                        content = sanitize_config_yaml(content)
                        dst.write_text(content, encoding="utf-8")
                    else:
                        shutil.copy2(src, dst)
                    print(f"  ✅ COPIED: {item['src_rel']} → {item['dst_rel']} [{item['priority']}]")
                    stats["copied"] += 1
                except Exception as e:
                    print(f"  ❌ ERROR: {item['src_rel']}: {e}")
                    stats["errors"] += 1

    # Skills (special handling)
    print()
    print("  Skills (SKILL.md only):")
    skill_actions = _sync_skills("backup", dry_run)
    for a in skill_actions:
        print(a)
        if "COPIED" in a or "WOULD COPY" in a:
            stats["copied"] += 1

    print()
    print(f"  Summary: {stats['copied']} synced, {stats['skipped']} skipped, {stats['errors']} errors")


def do_restore(dry_run: bool = False) -> None:
    """Restore from user-data/ to ~/.hermes/."""
    print(f"{'[DRY RUN] ' if dry_run else ''}Restoring {USER_DATA_DIR} → {HERMES_HOME}")
    print()

    if not HERMES_HOME.exists():
        if not dry_run:
            HERMES_HOME.mkdir(parents=True, exist_ok=True)
            print(f"  Created {HERMES_HOME}")

    stats = {"restored": 0, "skipped": 0, "errors": 0}

    for item in SYNC_ITEMS:
        src = USER_DATA_DIR / item["dst_rel"]  # Note: dst_rel is the user-data path
        dst = HERMES_HOME / item["src_rel"]     # And src_rel is the hermes path

        if not src.exists():
            print(f"  ⏭ SKIP (not found): {item['dst_rel']}")
            stats["skipped"] += 1
            continue

        # Constitution layer: never overwrite without confirmation
        if item["priority"] == "critical" and dst.exists():
            if filecmp.cmp(src, dst, shallow=False):
                print(f"  ⏭ SKIP (identical): {item['src_rel']}")
                stats["skipped"] += 1
                continue
            print(f"  ⚠️  CONFLICT: {item['src_rel']} exists and differs!")
            print(f"      user-data version: {src.stat().st_size} bytes")
            print(f"      live version: {dst.stat().st_size} bytes")
            if not dry_run:
                response = input("      Overwrite? [y/N]: ").strip().lower()
                if response != 'y':
                    print(f"      → Skipped")
                    stats["skipped"] += 1
                    continue

        if item["is_dir"]:
            if dry_run:
                print(f"  WOULD RESTORE DIR: {item['dst_rel']} → {item['src_rel']} [{item['priority']}]")
                stats["restored"] += 1
            else:
                try:
                    if dst.exists():
                        # Merge, don't delete existing
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copytree(src, dst)
                    print(f"  ✅ RESTORED DIR: {item['dst_rel']} → {item['src_rel']} [{item['priority']}]")
                    stats["restored"] += 1
                except Exception as e:
                    print(f"  ❌ ERROR: {item['dst_rel']}: {e}")
                    stats["errors"] += 1
        else:
            if dry_run:
                print(f"  WOULD RESTORE: {item['dst_rel']} → {item['src_rel']} [{item['priority']}]")
                stats["restored"] += 1
            else:
                try:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    print(f"  ✅ RESTORED: {item['dst_rel']} → {item['src_rel']} [{item['priority']}]")
                    stats["restored"] += 1
                except Exception as e:
                    print(f"  ❌ ERROR: {item['dst_rel']}: {e}")
                    stats["errors"] += 1

    # Skills (special handling)
    print()
    print("  Skills (SKILL.md only):")
    skill_actions = _sync_skills("restore", dry_run)
    for a in skill_actions:
        print(a)
        if "RESTORED" in a or "WOULD COPY" in a:
            stats["restored"] += 1

    print()
    print(f"  Summary: {stats['restored']} restored, {stats['skipped']} skipped, {stats['errors']} errors")


def do_verify() -> None:
    """Verify sync status between ~/.hermes/ and user-data/."""
    print(f"Verifying sync status: {HERMES_HOME} ↔ {USER_DATA_DIR}")
    print()

    issues = []

    for item in SYNC_ITEMS:
        hermes_path = HERMES_HOME / item["src_rel"]
        user_data_path = USER_DATA_DIR / item["dst_rel"]

        if not hermes_path.exists() and not user_data_path.exists():
            print(f"  ⚪ {item['src_rel']}: not found in either location")
        elif not hermes_path.exists():
            print(f"  🟡 {item['src_rel']}: only in user-data (needs restore)")
            issues.append(("restore_needed", item["src_rel"]))
        elif not user_data_path.exists():
            print(f"  🔴 {item['src_rel']}: only in ~/.hermes (NOT BACKED UP!)")
            issues.append(("backup_needed", item["src_rel"]))
        elif item["is_dir"]:
            # Compare directory file counts
            h_count = sum(1 for _ in hermes_path.rglob("*") if _.is_file())
            u_count = sum(1 for _ in user_data_path.rglob("*") if _.is_file())
            if h_count == u_count:
                print(f"  ✅ {item['src_rel']}: synced ({h_count} files)")
            else:
                print(f"  ⚠️  {item['src_rel']}: hermes={h_count} files, user-data={u_count} files (drift detected)")
                issues.append(("drift", item["src_rel"]))
        else:
            if filecmp.cmp(hermes_path, user_data_path, shallow=False):
                print(f"  ✅ {item['src_rel']}: synced")
            else:
                h_size = hermes_path.stat().st_size
                u_size = user_data_path.stat().st_size
                print(f"  ⚠️  {item['src_rel']}: differs (hermes={h_size}B, user-data={u_size}B)")
                issues.append(("drift", item["src_rel"]))

    # Skills verification
    print()
    print("  Skills verification:")
    hermes_skills = HERMES_HOME / "skills"
    user_data_skills = USER_DATA_DIR / "skills"
    if hermes_skills.exists():
        h_skills = set(p.relative_to(hermes_skills) for p in hermes_skills.rglob("SKILL.md"))
    else:
        h_skills = set()
    if user_data_skills.exists():
        u_skills = set(p.relative_to(user_data_skills) for p in user_data_skills.rglob("SKILL.md"))
    else:
        u_skills = set()

    only_hermes = h_skills - u_skills
    only_user_data = u_skills - h_skills
    common = h_skills & u_skills

    print(f"    Common: {len(common)} skills")
    if only_hermes:
        print(f"    🔴 Only in ~/.hermes (NOT BACKED UP!): {len(only_hermes)} skills")
        for s in sorted(only_hermes):
            print(f"       - {s}")
        issues.append(("skills_not_backed_up", str(len(only_hermes))))
    if only_user_data:
        print(f"    🟡 Only in user-data (needs restore): {len(only_user_data)} skills")

    print()
    if issues:
        print(f"  ⚠️  {len(issues)} issues found. Run backup or restore to fix.")
    else:
        print("  ✅ All synced!")


def main():
    parser = argparse.ArgumentParser(
        description="Sync Hermes user data between ~/.hermes/ and user-data/ directory"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--restore", action="store_true", help="Restore from user-data/ to ~/.hermes/")
    group.add_argument("--dry-run", action="store_true", help="Preview what would be synced (backup mode)")
    group.add_argument("--verify", action="store_true", help="Check sync status")
    args = parser.parse_args()

    if not HERMES_HOME.exists() and not args.restore:
        print(f"Error: {HERMES_HOME} does not exist. Is Hermes installed?")
        sys.exit(1)

    if args.verify:
        do_verify()
    elif args.restore:
        do_restore(dry_run=False)
    elif args.dry_run:
        do_backup(dry_run=True)
    else:
        do_backup(dry_run=False)


if __name__ == "__main__":
    main()
