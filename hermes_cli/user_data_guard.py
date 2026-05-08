"""
user_data_guard.py — Protect user-defined data during Hermes version upgrades.

This module provides a pre-launch hook that:
1. Detects when a version upgrade has occurred
2. Verifies that critical user data (constitution layer) still exists
3. Auto-restores from user-data/ backup if critical data is missing
4. Logs warnings when user data drift is detected

Integration point: hermes_cli/main.py calls _guard_user_data() after
_apply_profile_override() and before the main argparse dispatch.
"""

import json
import logging
import os
import shutil
from pathlib import Path
from typing import Optional

logger = logging.getLogger("hermes.user_data_guard")

_VERSION_MARKER = ".hermes_version"
_CRITICAL_FILES = [
    "skills/software-development/persistent-solver/SKILL.md",
    "memories/MEMORY.md",
    "memories/USER.md",
]


def _get_hermes_home() -> Path:
    env = os.environ.get("HERMES_HOME")
    if env:
        return Path(env)
    return Path.home() / ".hermes"


def _get_project_root() -> Optional[Path]:
    candidates = [
        Path(__file__).resolve().parent.parent,
        Path.cwd(),
    ]
    for c in candidates:
        if (c / "run_agent.py").exists() and (c / "user-data").is_dir():
            return c
    return None


def _read_version_marker(home: Path) -> Optional[str]:
    marker = home / _VERSION_MARKER
    if marker.exists():
        return marker.read_text().strip()
    return None


def _write_version_marker(home: Path, version: str) -> None:
    marker = home / _VERSION_MARKER
    marker.write_text(version)


def _get_current_package_version() -> str:
    try:
        from importlib.metadata import version
        return version("hermes-agent")
    except Exception:
        return "unknown"


def _critical_file_exists(home: Path, rel_path: str) -> bool:
    return (home / rel_path).exists()


def _restore_from_backup(project_root: Path, home: Path, rel_path: str) -> bool:
    backup_map = {
        "skills/software-development/persistent-solver/SKILL.md":
            "user-data/constitution/persistent-solver-SKILL.md",
        "memories/MEMORY.md":
            "user-data/constitution/MEMORY.md",
        "memories/USER.md":
            "user-data/constitution/USER.md",
    }

    backup_rel = backup_map.get(rel_path)
    if not backup_rel:
        return False

    backup_path = project_root / backup_rel
    target_path = home / rel_path

    if not backup_path.exists():
        logger.warning("Backup not found for %s: %s", rel_path, backup_path)
        return False

    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup_path, target_path)
        logger.info("Restored %s from backup", rel_path)
        return True
    except Exception as e:
        logger.error("Failed to restore %s: %s", rel_path, e)
        return False


def _guard_user_data() -> None:
    home = _get_hermes_home()
    project_root = _get_project_root()
    current_version = _get_current_package_version()
    previous_version = _read_version_marker(home)

    if not home.exists():
        return

    version_changed = (
        previous_version is not None
        and current_version != "unknown"
        and previous_version != current_version
    )

    if version_changed:
        logger.info(
            "Version upgrade detected: %s → %s. Checking user data integrity.",
            previous_version, current_version,
        )

    missing_critical = []
    for rel_path in _CRITICAL_FILES:
        if not _critical_file_exists(home, rel_path):
            missing_critical.append(rel_path)

    if missing_critical and project_root:
        logger.warning(
            "Missing critical user data files: %s. Attempting auto-restore from backup.",
            missing_critical,
        )
        restored = []
        failed = []
        for rel_path in missing_critical:
            if _restore_from_backup(project_root, home, rel_path):
                restored.append(rel_path)
            else:
                failed.append(rel_path)

        if restored:
            logger.info("Auto-restored: %s", restored)
        if failed:
            logger.error(
                "FAILED to restore: %s. These files are LOST. "
                "Manual restoration required from user-data/ backup.",
                failed,
            )

    elif missing_critical and not project_root:
        logger.error(
            "Missing critical user data files: %s. No project root found for auto-restore. "
            "Run 'python scripts/sync_user_data.py --restore' manually.",
            missing_critical,
        )

    if current_version != "unknown":
        _write_version_marker(home, current_version)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _guard_user_data()