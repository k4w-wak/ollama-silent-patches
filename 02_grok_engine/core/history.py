"""Grok History Log — Conversation history system.
Ported from claw-code history.
"""
import json
import time
from pathlib import Path

HISTORY_FILE = Path.home() / ".grok" / "history.jsonl"

def history_add(role: str, content: str, tool_name: str = None, tool_result: str = None) -> None:
    """Add an entry to the history log."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "role": role,
        "content": content[:5000],  # Truncate very long content
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    if tool_name:
        entry["tool"] = tool_name
    if tool_result:
        entry["tool_result"] = tool_result[:2000]
    
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def history_read(limit: int = 50, role_filter: str = None) -> str:
    """Read history log entries."""
    if not HISTORY_FILE.exists():
        return "Ingen historik fundet"
    
    entries = []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entries.append(json.loads(line.strip()))
            except:
                continue
    
    if role_filter:
        entries = [e for e in entries if e.get("role") == role_filter]
    
    # Take last N entries
    entries = entries[-limit:]
    
    output = []
    for e in entries:
        ts = e.get("timestamp", "?")
        role = e.get("role", "?")
        content = e.get("content", "")[:200]
        tool = e.get("tool", "")
        if tool:
            output.append(f"[{ts}] {role}: ({tool}) {content}")
        else:
            output.append(f"[{ts}] {role}: {content}")
    
    return "\n".join(output) if output else "Ingen historik fundet"

def history_clear() -> str:
    """Clear history log."""
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
    return "✅ Historik slettet"

def history_count() -> dict:
    """Count history entries by role."""
    if not HISTORY_FILE.exists():
        return {"total": 0}
    
    counts = {}
    total = 0
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line.strip())
                role = e.get("role", "unknown")
                counts[role] = counts.get(role, 0) + 1
                total += 1
            except:
                continue
    
    counts["total"] = total
    return counts
