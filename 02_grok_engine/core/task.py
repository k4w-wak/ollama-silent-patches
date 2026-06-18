"""Grok Task System — Create, track, stop, and update tasks.
Ported from claw-code Rust TaskCreateTool/TaskGetTool/TaskListTool/TaskStopTool/TaskUpdateTool.
"""
import json
import os
import time
import uuid
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional

TASK_DIR = Path.home() / ".grok" / "tasks"

@dataclass
class GrokTask:
    id: str
    title: str
    description: str = ""
    status: str = "pending"  # pending, in_progress, completed, failed, stopped
    priority: str = "normal"  # low, normal, high, critical
    created_at: str = ""
    updated_at: str = ""
    completed_at: Optional[str] = None
    result: Optional[str] = None
    subtasks: list = field(default_factory=list)
    tags: list = field(default_factory=list)

def _ensure_dir():
    TASK_DIR.mkdir(parents=True, exist_ok=True)

def _task_path(task_id: str) -> Path:
    return TASK_DIR / f"{task_id}.json"

def task_create(title: str, description: str = "", priority: str = "normal", tags: list = None) -> str:
    """Create a new task. Returns task ID and details."""
    _ensure_dir()
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    task = GrokTask(
        id=str(uuid.uuid4())[:8],
        title=title,
        description=description,
        status="pending",
        priority=priority,
        created_at=now,
        updated_at=now,
        tags=tags or []
    )
    _task_path(task.id).write_text(json.dumps(asdict(task), indent=2, ensure_ascii=False))
    return json.dumps({"action": "created", "task_id": task.id, "title": title, "priority": priority, "status": "pending", "created_at": now}, ensure_ascii=False)

def task_get(task_id: str) -> str:
    """Get details of a task by ID."""
    path = _task_path(task_id)
    if not path.exists():
        return json.dumps({"error": f"Task {task_id} not found"})
    data = json.loads(path.read_text())
    return json.dumps(data, indent=2, ensure_ascii=False)

def task_list(status_filter: str = None, priority_filter: str = None) -> str:
    """List all tasks, optionally filtered by status or priority."""
    _ensure_dir()
    tasks = []
    for path in sorted(TASK_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        if status_filter and data.get("status") != status_filter:
            continue
        if priority_filter and data.get("priority") != priority_filter:
            continue
        tasks.append(data)
    if not tasks:
        return json.dumps({"count": 0, "tasks": []})
    return json.dumps({"count": len(tasks), "tasks": tasks}, indent=2, ensure_ascii=False)

def task_update(task_id: str, status: str = None, result: str = None, description: str = None, priority: str = None) -> str:
    """Update a task's status, result, description, or priority."""
    path = _task_path(task_id)
    if not path.exists():
        return json.dumps({"error": f"Task {task_id} not found"})
    data = json.loads(path.read_text())
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    if status:
        data["status"] = status
        if status in ("completed", "failed", "stopped"):
            data["completed_at"] = now
    if result is not None:
        data["result"] = result
    if description is not None:
        data["description"] = description
    if priority is not None:
        data["priority"] = priority
    data["updated_at"] = now
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return json.dumps({"action": "updated", "task_id": task_id, "status": data["status"], "updated_at": now}, ensure_ascii=False)

def task_stop(task_id: str, reason: str = "") -> str:
    """Stop a running task. Sets status to 'stopped'."""
    path = _task_path(task_id)
    if not path.exists():
        return json.dumps({"error": f"Task {task_id} not found"})
    data = json.loads(path.read_text())
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    data["status"] = "stopped"
    data["completed_at"] = now
    data["updated_at"] = now
    if reason:
        data["result"] = f"Stopped: {reason}"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    return json.dumps({"action": "stopped", "task_id": task_id, "reason": reason, "stopped_at": now}, ensure_ascii=False)
