"""Grok REPL — Persistent Python session.
Variables survive between commands. Full Python power.
"""
import sys
import io
import traceback
from datetime import datetime
from pathlib import Path

# Shared persistent namespace
_REPL_NAMESPACE = {
    "__builtins__": __builtins__,
    "np": None,
    "pd": None,
}

_REPL_HISTORY = []
_REPL_SESSION_START = None


def _ensure_imports():
    """Try importing common libraries into the REPL namespace."""
    if _REPL_NAMESPACE["np"] is None:
        try:
            import numpy as np
            _REPL_NAMESPACE["np"] = np
        except ImportError:
            pass
    if _REPL_NAMESPACE["pd"] is None:
        try:
            import pandas as pd
            _REPL_NAMESPACE["pd"] = pd
        except ImportError:
            pass


def repl_exec(code: str) -> str:
    """Execute Python code in a persistent REPL session.
    Variables survive between calls. Input: Python code as string.
    """
    global _REPL_SESSION_START
    
    if not _REPL_SESSION_START:
        _REPL_SESSION_START = datetime.now()
    
    _ensure_imports()
    
    code = code.strip()
    if not code:
        return "[REPL] Tom kommando. Skriv Python kode."
    
    # Track history
    _REPL_HISTORY.append({
        "time": datetime.now().isoformat(),
        "code": code[:500]
    })
    
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    result = None
    is_expr = False
    
    try:
        # Try as expression first (returns value)
        try:
            compiled = compile(code, "<repl>", "eval")
            is_expr = True
        except SyntaxError:
            compiled = compile(code, "<repl>", "exec")
            is_expr = False
        
        result = eval(compiled, _REPL_NAMESPACE)
        
        output = sys.stdout.getvalue()
        
        if is_expr and result is not None:
            # Store last expression result
            _REPL_NAMESPACE["_"] = result
            _REPL_NAMESPACE["_last"] = result
            if output:
                return f"{output}\n→ {repr(result)}"
            return f"→ {repr(result)}"
        elif output:
            return output.rstrip()
        elif not is_expr:
            return "✅ OK"
        else:
            return "→ None"
            
    except Exception:
        output = sys.stdout.getvalue()
        err = traceback.format_exc().rstrip()
        # Clean up the traceback
        lines = err.split("\n")
        # Remove internal repl frames
        clean = [l for l in lines if "repl" not in l.lower() or "Error" in l or "Traceback" in l]
        if not clean:
            clean = lines[-3:]
        return f"{output}\n{'  '.join(clean)}" if output else "\n".join(clean)
    
    finally:
        sys.stdout = old_stdout


def repl_vars(dummy: str = "") -> str:
    """List all variables in the REPL session."""
    vars_dict = {k: v for k, v in _REPL_NAMESPACE.items() 
                 if not k.startswith("__") and v is not None}
    
    if not vars_dict:
        return "[REPL] Ingen variabler endnu."
    
    lines = ["[REPL] Variabler i session:", ""]
    for k, v in vars_dict.items():
        vrepr = repr(v)[:100]
        vtype = type(v).__name__
        lines.append(f"  {k} ({vtype}) = {vrepr}")
    
    # Count
    lines.append(f"\n  Total: {len(vars_dict)} variabler")
    return "\n".join(lines)


def repl_history(dummy: str = "") -> str:
    """Show REPL command history."""
    if not _REPL_HISTORY:
        return "[REPL] Ingen historik endnu."
    
    lines = [f"[REPL] Historik ({len(_REPL_HISTORY)} kommandoer):", ""]
    for i, entry in enumerate(_REPL_HISTORY[-20:], 1):
        t = entry["time"].split("T")[1][:8] if "T" in entry["time"] else "?"
        code = entry["code"][:80]
        lines.append(f"  {i:3d}. [{t}] {code}")
    
    return "\n".join(lines)


def repl_reset(dummy: str = "") -> str:
    """Reset the REPL session — clear all variables."""
    global _REPL_SESSION_START, _REPL_HISTORY
    count = len([k for k, v in _REPL_NAMESPACE.items() 
                 if not k.startswith("__") and v is not None])
    
    # Clear but keep builtins
    _REPL_NAMESPACE.clear()
    _REPL_NAMESPACE["__builtins__"] = __builtins__
    _REPL_NAMESPACE["np"] = None
    _REPL_NAMESPACE["pd"] = None
    _REPL_HISTORY = []
    _REPL_SESSION_START = None
    
    return f"✅ REPL nulstillet! {count} variabler fjernet."


def repl_save(path: str) -> str:
    """Save REPL variables to a Python file. Input: filepath"""
    import json
    
    path = path.strip() or "~/repl_session.json"
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Collect saveable variables (skip modules and non-serializable)
    saveable = {}
    skipped = []
    for k, v in _REPL_NAMESPACE.items():
        if k.startswith("__"):
            continue
        if k in ("np", "pd"):
            continue  # Modules re-imported on load
        try:
            json.dumps(v)  # Test if serializable
            saveable[k] = v
        except (TypeError, ValueError):
            try:
                # Try pickle for non-JSON types
                import pickle
                pickle.dumps(v)
                saveable[f"_pickle_{k}"] = v
                skipped.append(k)
            except:
                skipped.append(k)
    
    try:
        # Save as JSON + pickle hybrid
        json_data = {k: v for k, v in saveable.items() if not k.startswith("_pickle_")}
        pickle_data = {k.replace("_pickle_", ""): v for k, v in saveable.items() if k.startswith("_pickle_")}
        
        if json_data:
            with open(str(path) + ".json", "w") as f:
                json.dump(json_data, f, indent=2, default=str)
        if pickle_data:
            import pickle
            with open(str(path) + ".pkl", "wb") as f:
                pickle.dump(pickle_data, f)
        
        return f"✅ REPL session gemt: {path} ({len(json_data)} JSON + {len(pickle_data)} pickle variabler)"
    except Exception as e:
        return f"[FEJL] Kan ikke gemme: {str(e)[:200]}"


def repl_load(path: str) -> str:
    """Load REPL variables from a saved file. Input: filepath"""
    import json
    
    path = path.strip() or "~/repl_session"
    path = Path(path).expanduser()
    _ensure_imports()
    
    count = 0
    
    # Load JSON
    json_path = str(path) + ".json" if not str(path).endswith(".json") else str(path)
    json_path = Path(json_path)
    if json_path.exists():
        try:
            with open(json_path) as f:
                data = json.load(f)
            for k, v in data.items():
                _REPL_NAMESPACE[k] = v
                count += 1
        except Exception as e:
            pass  # Continue to pickle
    
    # Load pickle
    pkl_path = Path(str(path).replace(".json", "") + ".pkl")
    if pkl_path.exists():
        try:
            import pickle
            with open(pkl_path, "rb") as f:
                data = pickle.load(f)
            for k, v in data.items():
                _REPL_NAMESPACE[k] = v
                count += 1
        except:
            pass
    
    if count == 0:
        return f"[FEJL] Ingen data fundet ved: {path}"
    return f"✅ REPL session indlæst: {count} variabler"