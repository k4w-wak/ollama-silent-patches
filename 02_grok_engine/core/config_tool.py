"""Grok Config — Runtime settings (read/write).
No permissions. No restrictions. Full access.
"""
import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".grok" / "settings.json"

def _load() -> dict:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except:
            return {}
    return {}

def _save(data: dict) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def get_setting(key: str) -> str:
    """Get a setting value."""
    data = _load()
    if not key:
        return json.dumps(data, indent=2, ensure_ascii=False)
    val = data.get(key, None)
    if val is None:
        return json.dumps({"setting": key, "value": None, "exists": False}, ensure_ascii=False)
    return json.dumps({"setting": key, "value": val, "exists": True}, ensure_ascii=False)

def set_setting(key: str, value: str) -> str:
    """Set a setting value."""
    data = _load()
    old = data.get(key)
    data[key] = value
    _save(data)
    return json.dumps({"action": "set", "setting": key, "old_value": old, "new_value": value}, ensure_ascii=False)

def list_settings() -> str:
    """List all settings."""
    data = _load()
    if not data:
        return json.dumps({"settings": {}, "count": 0})
    return json.dumps({"settings": data, "count": len(data)}, indent=2, ensure_ascii=False)