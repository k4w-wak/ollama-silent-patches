"""Grok Compact — Conversation compression when context gets too long.
Ported from claw-code compact.py.
"""
import json
from pathlib import Path

MEMORY_DIR = Path.home() / ".grok"

def compact_conversation(messages: list, max_messages: int = 30) -> list:
    """Compact a conversation by summarizing old messages.
    Keeps the last max_messages, summarizes the rest into one system msg.
    """
    if len(messages) <= max_messages:
        return messages
    
    # Split into old (to summarize) and recent (to keep)
    old = messages[:-max_messages]
    recent = messages[-max_messages:]
    
    # Build summary from old messages
    summary_parts = []
    for msg in old:
        role = msg.get("role", "?")
        content = msg.get("content", "")
        if isinstance(content, str) and content.strip():
            # Truncate long content
            preview = content[:200] + "..." if len(content) > 200 else content
            summary_parts.append(f"[{role}]: {preview}")
    
    summary = "\n".join(summary_parts[-20:])  # Keep last 20 old messages
    
    compact_msg = {
        "role": "system",
        "content": f"[COMPACTED CONTEXT — {len(old)} messages compressed]\n\nEarlier conversation summary:\n{summary}"
    }
    
    return [compact_msg] + recent

def get_message_count() -> int:
    """Get current message count from memory."""
    mem_file = MEMORY_DIR / "memory.json"
    if mem_file.exists():
        try:
            data = json.loads(mem_file.read_text())
            return len(data.get("short_term", {}).get("messages", []))
        except:
            pass
    return 0
