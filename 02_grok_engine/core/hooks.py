"""Grok Hooks — Pre/post tool execution hooks.
Ported from claw-code hooks.rs.
"""
import json
import subprocess
from pathlib import Path
from datetime import datetime

HOOKS_DIR = Path.home() / ".grok" / "hooks"

# Ensure dir exists
HOOKS_DIR.mkdir(parents=True, exist_ok=True)


# === PERMANENT UTF-8 ENCODING FIX ===
_UTF8_ENV = {**__import__('os').environ, 'PYTHONIOENCODING': 'utf-8', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8'}

def _load_hooks() -> dict:
    """Load hooks config from ~/.grok/hooks/hooks.json"""
    hooks_file = HOOKS_DIR / "hooks.json"
    if hooks_file.exists():
        try:
            return json.loads(hooks_file.read_text())
        except:
            pass
    return {"pre_tool": [], "post_tool": []}


def _save_hooks(hooks: dict):
    """Save hooks config."""
    hooks_file = HOOKS_DIR / "hooks.json"
    hooks_file.write_text(json.dumps(hooks, indent=2))


def hooks_list() -> str:
    """List all registered hooks."""
    hooks = _load_hooks()
    lines = ["╔══════════════════════════════════════╗",
             "║  GROK HOOKS                         ║",
             "╚══════════════════════════════════════╝"]
    
    if not hooks.get("pre_tool") and not hooks.get("post_tool"):
        lines.append("\nIngen hooks registeret.")
        lines.append("\nTilføj med: hooks_add pre|post tool_name command")
        return "\n".join(lines)
    
    if hooks.get("pre_tool"):
        lines.append("\n▸ PRE-TOOL HOOKS:")
        for h in hooks["pre_tool"]:
            lines.append(f"  [{h.get('id','?')}] {h.get('tool','*')} → {h.get('command','?')}")
            if h.get('enabled', True):
                lines.append(f"      Aktiv: ja | Beskrivelse: {h.get('description','')}")
            else:
                lines.append(f"      Aktiv: nej | Beskrivelse: {h.get('description','')}")
    
    if hooks.get("post_tool"):
        lines.append("\n▸ POST-TOOL HOOKS:")
        for h in hooks["post_tool"]:
            lines.append(f"  [{h.get('id','?')}] {h.get('tool','*')} → {h.get('command','?')}")
            lines.append(f"      Aktiv: {'ja' if h.get('enabled', True) else 'nej'} | {h.get('description','')}")
    
    return "\n".join(lines)


def hooks_add(event: str, tool: str, command: str, description: str = "") -> str:
    """
    Add a hook. event=pre_tool|post_tool, tool=*|tool_name, command=shell command.
    Input: 'pre_tool nmap_scan echo "Starting scan"' or 'post_tool * notify-send "Done"'
    """
    hooks = _load_hooks()
    
    # Parse input
    parts = event.split(maxsplit=3) if not tool else [event, tool, command]
    if len(parts) < 3:
        # Direct call with separate args
        evt = event
        tl = tool
        cmd = command
    else:
        evt, tl, cmd = parts[0], parts[1], parts[2]
        if len(parts) > 3:
            cmd = cmd + " " + parts[3]
    
    if evt not in ("pre_tool", "post_tool"):
        return f"[FEJL] Event skal være 'pre_tool' eller 'post_tool', got: {evt}"
    
    # Generate ID
    import hashlib
    hook_id = hashlib.md5(f"{evt}:{tl}:{cmd}".encode()).hexdigest()[:8]
    
    hook = {
        "id": hook_id,
        "event": evt,
        "tool": tl,
        "command": cmd,
        "description": description or f"{evt} hook for {tl}",
        "enabled": True,
        "created": datetime.now().isoformat(),
    }
    
    hooks.setdefault(evt, []).append(hook)
    _save_hooks(hooks)
    
    return json.dumps({"action": "added", "id": hook_id, "event": evt, "tool": tl, "command": cmd}, indent=2)


def hooks_remove(hook_id: str) -> str:
    """Remove a hook by ID."""
    hooks = _load_hooks()
    removed = False
    
    for evt in ("pre_tool", "post_tool"):
        hooks[evt] = [h for h in hooks.get(evt, []) if h.get("id") != hook_id]
    
    _save_hooks(hooks)
    return json.dumps({"action": "removed", "id": hook_id})


def hooks_run(event: str, tool_name: str, tool_input: str = "", tool_output: str = "") -> dict:
    """
    Run hooks for a given event and tool.
    Returns dict with 'denied' (bool) and 'messages' (list).
    """
    hooks = _load_hooks()
    result = {"denied": False, "messages": []}
    
    for hook in hooks.get(event, []):
        if not hook.get("enabled", True):
            continue
        
        # Check if hook matches this tool (* = all tools)
        if hook["tool"] != "*" and hook["tool"] != tool_name:
            continue
        
        # Run the command
        try:
            cmd = hook["command"]
            # Replace placeholders
            cmd = cmd.replace("{tool}", tool_name)
            cmd = cmd.replace("{input}", tool_input[:200])
            cmd = cmd.replace("{output}", tool_output[:200])
            cmd = cmd.replace("{timestamp}", datetime.now().isoformat())
            
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10, encoding='utf-8', errors='replace', env=_UTF8_ENV)
            
            if r.returncode != 0:
                # Non-zero exit = deny (for pre_tool hooks)
                if event == "pre_tool":
                    result["denied"] = True
                    result["messages"].append(f"Hook {hook['id']} denied: {r.stderr[:200]}")
                else:
                    result["messages"].append(f"Hook {hook['id']} error: {r.stderr[:200]}")
            else:
                result["messages"].append(f"Hook {hook['id']}: {r.stdout[:200]}")
                
        except subprocess.TimeoutExpired:
            result["messages"].append(f"Hook {hook['id']} timeout")
        except Exception as e:
            result["messages"].append(f"Hook {hook['id']} error: {str(e)[:100]}")
    
    return result