#!/usr/bin/env python3
"""
Approval Queue Tool — restricted-channel safe change submission.

In restricted channels (e.g. AI daily report group), the agent cannot
directly modify skills, memory, config, or data files.  Instead, it can
submit change requests to an approval queue.  An admin reviews and
approves/rejects them from a private chat.

Queue location: ~/.hermes/approval-queue/
Each request is a JSON file: <timestamp>_<type>_<hash>.json

This tool ONLY writes to the approval queue directory — it cannot touch
any other filesystem location.  This makes it safe for restricted channels.
"""

import json
import logging
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from hermes_constants import get_hermes_home

logger = logging.getLogger(__name__)

APPROVAL_QUEUE_DIR = Path(get_hermes_home()) / "approval-queue"

STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"

# ── Tool Schema ──────────────────────────────────────────────────────

SUBMIT_APPROVAL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "submit_approval",
        "description": (
            "Submit a change request to the approval queue. "
            "Use this in restricted channels when you want to update "
            "information sources, modify skills, add memory, or make any "
            "persistent change that requires admin approval. "
            "The request will be reviewed by an admin in a private chat. "
            "You will receive a confirmation with the request ID."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "request_type": {
                    "type": "string",
                    "enum": [
                        "source_update",
                        "skill_patch",
                        "memory_add",
                        "memory_replace",
                        "config_change",
                        "other",
                    ],
                    "description": (
                        "Category of the change request. "
                        "source_update: add/remove/update an information source. "
                        "skill_patch: patch a skill document (fix errors, add pitfalls). "
                        "memory_add: add a new memory entry. "
                        "memory_replace: replace an existing memory entry. "
                        "config_change: modify config.yaml. "
                        "other: any other change requiring approval."
                    ),
                },
                "target": {
                    "type": "string",
                    "description": (
                        "What is being changed. "
                        "For source_update: the sources JSON file path. "
                        "For skill_patch: the skill name. "
                        "For memory_add/replace: 'memory' or 'user'. "
                        "For config_change: the config key. "
                        "For other: a descriptive identifier."
                    ),
                },
                "change_description": {
                    "type": "string",
                    "description": (
                        "Human-readable summary of the change. "
                        "Be specific: what is being added/removed/modified and why."
                    ),
                },
                "change_data": {
                    "type": "object",
                    "description": (
                        "The actual change payload as a JSON object. "
                        "For source_update: {action: 'add'|'remove'|'update', "
                        "source_entry: {...}, source_id: '...'} "
                        "For skill_patch: {old_string: '...', new_string: '...'} "
                        "For memory_add: {content: '...', target: 'memory'|'user'} "
                        "For other: any structured data describing the change."
                    ),
                },
                "reason": {
                    "type": "string",
                    "description": (
                        "Why this change is needed. "
                        "Reference the user message or context that triggered it."
                    ),
                },
                "rollback": {
                    "type": "string",
                    "description": (
                        "How to reverse this change if needed. "
                        "E.g. 'git revert HEAD~1' or 'remove source entry by id'. "
                        "Optional but recommended."
                    ),
                },
            },
            "required": ["request_type", "target", "change_description", "change_data", "reason"],
        },
    },
}


# ── Handler ──────────────────────────────────────────────────────────

def submit_approval_handler(args: Dict[str, Any], **kwargs) -> str:
    """Handle submit_approval tool calls.

    Only writes to ~/.hermes/approval-queue/ — cannot touch any other path.
    """
    request_type = args.get("request_type", "other")
    target = args.get("target", "")
    change_description = args.get("change_description", "")
    change_data = args.get("change_data", {})
    reason = args.get("reason", "")
    rollback = args.get("rollback", "")

    # Get context info from kwargs (source, session, etc.)
    source = kwargs.get("source")
    submitted_by = ""
    channel = ""
    if source:
        submitted_by = getattr(source, "user_id", "") or ""
        channel = getattr(source, "chat_id", "") or ""

    # Ensure queue directory exists
    APPROVAL_QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    timestamp = now.isoformat()

    # Generate unique ID
    hash_input = f"{timestamp}:{request_type}:{target}:{json.dumps(change_data, sort_keys=True, ensure_ascii=False)}"
    short_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
    request_id = f"{now.strftime('%Y%m%d_%H%M%S')}_{request_type}_{short_hash}"

    request = {
        "id": request_id,
        "status": STATUS_PENDING,
        "request_type": request_type,
        "target": target,
        "change_description": change_description,
        "change_data": change_data,
        "reason": reason,
        "rollback": rollback,
        "submitted_by": submitted_by,
        "channel": channel,
        "created_at": timestamp,
        "resolved_at": None,
        "resolved_by": None,
    }

    # Write to approval queue (ONLY this directory is writable)
    file_path = APPROVAL_QUEUE_DIR / f"{request_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(request, f, ensure_ascii=False, indent=2)

    logger.info(
        "Approval request submitted: %s (type=%s, target=%s, by=%s in channel=%s)",
        request_id, request_type, target, submitted_by, channel,
    )

    return (
        f"✅ 审批请求已提交！\n"
        f"请求ID: {request_id}\n"
        f"类型: {request_type}\n"
        f"目标: {target}\n"
        f"变更描述: {change_description}\n"
        f"原因: {reason}\n\n"
        f"管理员将在私聊中审批此请求。审批通过后变更将自动生效。\n"
        f"你可以继续在此频道提问和查看日报。"
    )


# ── Registry ─────────────────────────────────────────────────────────

from tools.registry import registry

registry.register(
    name="submit_approval",
    toolset="approval",
    schema=SUBMIT_APPROVAL_SCHEMA,
    handler=submit_approval_handler,
    check_fn=lambda: True,  # Always available — no special requirements
    emoji="📋",
)