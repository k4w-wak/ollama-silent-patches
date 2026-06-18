"""Grok Cost Tracker — Token usage tracking.
Ported from claw-code cost_tracker/costHook.
"""
import json
import time
from pathlib import Path

COST_FILE = Path.home() / ".grok" / "costs.json"

def _ensure_file():
    COST_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not COST_FILE.exists():
        COST_FILE.write_text(json.dumps({"total_input": 0, "total_output": 0, "sessions": [], "models": {}}, indent=2))

def cost_track(model: str, input_tokens: int, output_tokens: int) -> str:
    """Track token usage for a model call."""
    _ensure_file()
    data = json.loads(COST_FILE.read_text())
    data["total_input"] = data.get("total_input", 0) + input_tokens
    data["total_output"] = data.get("total_output", 0) + output_tokens
    
    models = data.get("models", {})
    if model not in models:
        models[model] = {"input": 0, "output": 0, "calls": 0}
    models[model]["input"] = models[model].get("input", 0) + input_tokens
    models[model]["output"] = models[model].get("output", 0) + output_tokens
    models[model]["calls"] = models[model].get("calls", 0) + 1
    data["models"] = models
    
    # Session log
    sessions = data.get("sessions", [])
    sessions.append({
        "model": model,
        "input": input_tokens,
        "output": output_tokens,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
    })
    # Keep last 100 entries
    data["sessions"] = sessions[-100:]
    
    COST_FILE.write_text(json.dumps(data, indent=2))
    total = data["total_input"] + data["total_output"]
    return json.dumps({"tracked": True, "model": model, "input": input_tokens, "output": output_tokens, "session_total": total})

def cost_report() -> str:
    """Get cost/usage report."""
    _ensure_file()
    data = json.loads(COST_FILE.read_text())
    total = data.get("total_input", 0) + data.get("total_output", 0)
    models = data.get("models", {})
    
    lines = ["═ KOST / TOKEN RAPPORT ═", ""]
    lines.append(f"Total tokens brugt: {total:,}")
    lines.append(f"  Input:  {data.get('total_input', 0):,}")
    lines.append(f"  Output: {data.get('total_output', 0):,}")
    lines.append("")
    lines.append("Pr. model:")
    for model, stats in sorted(models.items()):
        m_total = stats.get("input", 0) + stats.get("output", 0)
        lines.append(f"  {model}: {m_total:,} tokens ({stats.get('calls',0)} calls)")
    
    return "\n".join(lines)

def cost_reset() -> str:
    """Reset cost tracking."""
    COST_FILE.write_text(json.dumps({"total_input": 0, "total_output": 0, "sessions": [], "models": {}}, indent=2))
    return "✅ Cost tracker nulstillet"
