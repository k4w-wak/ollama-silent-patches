"""Grok TodoWrite — Persistent todo list with status tracking.
Ported from claw-code TodoWriteTool.
"""
import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional, List

TODO_FILE = Path.home() / ".grok" / "todos.json"

@dataclass
class TodoItem:
    content: str
    active_form: str = ""
    status: str = "pending"  # pending, in_progress, completed
    priority: str = "normal"

def load_todos() -> list:
    """Load current todos from disk."""
    if not TODO_FILE.exists():
        return []
    try:
        data = json.loads(TODO_FILE.read_text())
        return data if isinstance(data, list) else []
    except:
        return []

def save_todos(todos: list) -> None:
    """Save todos to disk."""
    TODO_FILE.parent.mkdir(parents=True, exist_ok=True)
    TODO_FILE.write_text(json.dumps(todos, indent=2, ensure_ascii=False))

def todo_write(todos_input: str) -> str:
    """Write todos. Input: JSON array of {content, status, priority} or plain text list.
    Returns old and new state."""
    old_todos = load_todos()
    old_count = len(old_todos)
    
    # Parse input
    try:
        if isinstance(todos_input, str):
            try:
                items = json.loads(todos_input)
            except json.JSONDecodeError:
                # Plain text, split by lines
                items = [{"content": line.strip(), "status": "pending"} 
                         for line in todos_input.strip().split("\n") if line.strip()]
        else:
            items = todos_input
    except:
        items = [{"content": str(todos_input), "status": "pending"}]
    
    if not items:
        return json.dumps({"error": "todos must not be empty"}, ensure_ascii=False)
    
    new_todos = []
    for item in items:
        content = item.get("content", item.get("text", "")) if isinstance(item, dict) else str(item)
        if not content or not content.strip():
            continue
        new_todos.append({
            "content": content.strip(),
            "active_form": item.get("active_form", f"Working on: {content.strip()}") if isinstance(item, dict) else f"Working on: {content.strip()}",
            "status": item.get("status", "pending") if isinstance(item, dict) else "pending",
            "priority": item.get("priority", "normal") if isinstance(item, dict) else "normal"
        })
    
    # Check if all completed → verification nudge
    all_completed = all(t.get("status") == "completed" for t in new_todos) if new_todos else False
    
    save_todos(new_todos)
    
    return json.dumps({
        "action": "written",
        "old_count": old_count,
        "new_count": len(new_todos),
        "old_todos": old_todos[:5],  # Show up to 5 old items
        "new_todos": new_todos,
        "verification_nudge_needed": all_completed if all_completed else None
    }, indent=2, ensure_ascii=False)

def todo_read() -> str:
    """Read current todos."""
    todos = load_todos()
    return json.dumps({
        "count": len(todos),
        "todos": todos
    }, indent=2, ensure_ascii=False)
