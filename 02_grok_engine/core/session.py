"""Grok Session Store — Save and restore full conversation sessions.
Ported from claw-code session_store.
"""
import json
import time
from pathlib import Path
from typing import Optional

SESSION_DIR = Path.home() / ".grok" / "sessions"

def _ensure_dir():
    SESSION_DIR.mkdir(parents=True, exist_ok=True)

def session_save(session_id: str, messages: list, input_tokens: int = 0, output_tokens: int = 0) -> str:
    """Save a session to disk."""
    _ensure_dir()
    data = {
        "session_id": session_id,
        "messages": messages,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "saved_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "version": 3
    }
    path = SESSION_DIR / f"{session_id}.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return json.dumps({"action": "saved", "session_id": session_id, "message_count": len(messages), "path": str(path)}, ensure_ascii=False)

def session_load(session_id: str) -> str:
    """Load a session from disk."""
    path = SESSION_DIR / f"{session_id}.json"
    if not path.exists():
        # Try partial match
        matches = list(SESSION_DIR.glob(f"{session_id}*.json"))
        if matches:
            path = matches[0]
        else:
            return json.dumps({"error": f"Session {session_id} not found", "available": session_list_raw()})
    data = json.loads(path.read_text())
    return json.dumps(data, indent=2, ensure_ascii=False)

def session_list() -> str:
    """List all saved sessions."""
    _ensure_dir()
    sessions = []
    for path in sorted(SESSION_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(path.read_text())
            sessions.append({
                "session_id": data.get("session_id", path.stem),
                "saved_at": data.get("saved_at", "unknown"),
                "message_count": len(data.get("messages", [])),
                "input_tokens": data.get("input_tokens", 0),
                "output_tokens": data.get("output_tokens", 0)
            })
        except:
            sessions.append({"session_id": path.stem, "error": "corrupt"})
    return json.dumps({"count": len(sessions), "sessions": sessions}, indent=2, ensure_ascii=False)

def session_list_raw() -> list:
    """Return raw list of available session IDs."""
    _ensure_dir()
    return [path.stem for path in SESSION_DIR.glob("*.json")]

def session_delete(session_id: str) -> str:
    """Delete a saved session."""
    path = SESSION_DIR / f"{session_id}.json"
    if not path.exists():
        return json.dumps({"error": f"Session {session_id} not found"})
    path.unlink()
    return json.dumps({"action": "deleted", "session_id": session_id})
