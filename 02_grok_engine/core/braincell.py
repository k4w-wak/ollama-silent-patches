"""
HJERNECELLE — Auto-load admin_user's brain backup into long-term memory.

Reads HJERNECELLE.txt (session log archive) from the engine root and exposes
the content for the agent to inject as long-term memory facts.
"""

import os
from pathlib import Path

_HJERNECELLE_NAME = "HJERNECELLE.txt"


def _hjernecelle_path() -> Path:
    """Locate HJERNECELLE.txt next to the engine root."""
    return Path(__file__).resolve().parent.parent / _HJERNECELLE_NAME


def load_braincell() -> dict:
    """
    Load the braincell backup.

    Returns dict with keys:
        status: "LOADED" | "MISSING" | "EMPTY" | "ERROR"
        path:   absolute path to the file
        content: full text content (empty string on failure)
        lines:  line count
        bytes:  file size in bytes
    """
    path = _hjernecelle_path()
    info = {"status": "ERROR", "path": str(path), "content": "", "lines": 0, "bytes": 0}

    if not path.exists():
        info["status"] = "MISSING"
        return info

    try:
        size = path.stat().st_size
    except OSError:
        info["status"] = "ERROR"
        return info

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        info["status"] = "ERROR"
        return info

    info["content"] = text
    info["lines"] = text.count("\n") + (0 if text.endswith("\n") else 1)
    info["bytes"] = size
    info["status"] = "LOADED" if text.strip() else "EMPTY"
    return info


def braincell_status() -> str:
    """One-line human-readable status, safe to print at boot."""
    info = load_braincell()
    status = info["status"]
    if status == "LOADED":
        return f"[HJERNECELLE] LOADED — {info['lines']} linjer / {info['bytes']:,} bytes fra {info['path']}"
    if status == "EMPTY":
        return f"[HJERNECELLE] EMPTY — {info['path']} findes men er tom"
    if status == "MISSING":
        return f"[HJERNECELLE] MISSING — forventer {info['path']}"
    return f"[HJERNECELLE] ERROR — kunne ikke læse {info['path']}"
