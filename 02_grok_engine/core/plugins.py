"""Grok Plugins — Dynamic tool loading from ~/.grok/plugins/
Ported from claw-code plugins.rs.
"""
import json
import importlib
import subprocess
from pathlib import Path
from datetime import datetime

PLUGINS_DIR = Path.home() / ".grok" / "plugins"

# Ensure dir exists
PLUGINS_DIR.mkdir(parents=True, exist_ok=True)

# Create example plugin if none exist
_example_plugin = PLUGINS_DIR / "example_notify.json"
if not _example_plugin.exists():
    _example_plugin.write_text(json.dumps({
        "name": "notify",
        "version": "1.0",
        "description": "Send desktop notification",
        "type": "shell",
        "command": "notify-send 'GROK' '{input}'",
        "input_type": "text",
        "output_type": "text",
        "category": "utility",
        "enabled": True
    }, indent=2))


_installed_file = PLUGINS_DIR / "installed.json"
if not _installed_file.exists():
    _installed_file.write_text(json.dumps({}, indent=2))


# === PERMANENT UTF-8 ENCODING FIX ===
_UTF8_ENV = {**__import__('os').environ, 'PYTHONIOENCODING': 'utf-8', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8'}

def _load_plugins() -> dict:
    """Load all plugins from ~/.grok/plugins/*.json"""
    plugins = {}
    for f in PLUGINS_DIR.glob("*.json"):
        if f.name == "installed.json":
            continue
        try:
            data = json.loads(f.read_text())
            name = data.get("name", f.stem)
            plugins[name] = data
        except:
            pass
    return plugins


def plugin_list() -> str:
    """List all installed plugins."""
    plugins = _load_plugins()
    
    lines = ["╔══════════════════════════════════════╗",
             "║  GROK PLUGINS                       ║",
             "╚══════════════════════════════════════╝"]
    
    if not plugins:
        lines.append("\nIngen plugins installeret.")
        lines.append(f"\nTilføj plugins i: {PLUGINS_DIR}/")
        lines.append("Format: JSON med name, command, type")
        return "\n".join(lines)
    
    for name, data in plugins.items():
        enabled = "✅" if data.get("enabled", True) else "❌"
        ptype = data.get("type", "shell")
        cmd = data.get("command", "?")[:50]
        lines.append(f"\n  {enabled} {name} v{data.get('version', '?')} [{ptype}]")
        lines.append(f"    {data.get('description', '')}")
        lines.append(f"    Kommando: {cmd}")
        lines.append(f"    Kategori: {data.get('category', 'utility')}")
    
    return "\n".join(lines)


def plugin_add(name: str, command: str, description: str = "", 
              ptype: str = "shell", category: str = "utility") -> str:
    """
    Add a plugin. Input: 'name command' or separate args.
    """
    plugin = {
        "name": name,
        "version": "1.0",
        "description": description or f"Custom plugin: {name}",
        "type": ptype,
        "command": command,
        "input_type": "text",
        "output_type": "text",
        "category": category,
        "enabled": True,
        "created": datetime.now().isoformat(),
    }
    
    # Save to file
    plugin_file = PLUGINS_DIR / f"{name}.json"
    plugin_file.write_text(json.dumps(plugin, indent=2))
    
    return json.dumps({"action": "added", "name": name, "command": command, "file": str(plugin_file)}, indent=2)


def plugin_run(name: str, input_data: str = "") -> str:
    """
    Run a plugin by name. Executes the plugin's command with input.
    """
    plugins = _load_plugins()
    
    if name not in plugins:
        # Try partial match
        matches = [n for n in plugins if name in n]
        if matches:
            name = matches[0]
        else:
            return f"[FEJL] Plugin '{name}' ikke fundet. Tilgængelige: {', '.join(plugins.keys())}"
    
    plugin = plugins[name]
    
    if not plugin.get("enabled", True):
        return f"[FEJL] Plugin '{name}' er deaktiveret."
    
    cmd = plugin["command"].replace("{input}", input_data)
    
    try:
        if plugin.get("type") == "shell":
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60, encoding='utf-8', errors='replace', env=_UTF8_ENV)
            output = r.stdout[:3000] if r.stdout else r.stderr[:500]
            return output if output else f"[Plugin {name} kørte uden output]"
        elif plugin.get("type") == "python":
            # Run as Python module
            mod = importlib.import_module(plugin.get("module", name))
            func = getattr(mod, plugin.get("function", "run"))
            return str(func(input_data))
        else:
            return f"[FEJL] Ukendt plugin type: {plugin.get('type')}"
    except subprocess.TimeoutExpired:
        return f"[TIMEOUT] Plugin {name} tog for lang tid"
    except Exception as e:
        return f"[FEJL] Plugin {name} fejlede: {str(e)[:200]}"


def plugin_remove(name: str) -> str:
    """Remove a plugin by name."""
    plugin_file = PLUGINS_DIR / f"{name}.json"
    if plugin_file.exists():
        plugin_file.unlink()
        return json.dumps({"action": "removed", "name": name})
    else:
        plugins = _load_plugins()
        matches = [n for n in plugins if name in n]
        if matches:
            f = PLUGINS_DIR / f"{matches[0]}.json"
            f.unlink()
            return json.dumps({"action": "removed", "name": matches[0]})
        return f"[FEJL] Plugin '{name}' ikke fundet."