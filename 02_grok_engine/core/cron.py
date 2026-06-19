"""Grok Cron — Schedule tasks to run at intervals or specific times.
Ported from claw-code cron concept.
"""
import json
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime

CRON_DIR = Path.home() / ".grok" / "cron"
CRON_DIR.mkdir(parents=True, exist_ok=True)

CRON_FILE = CRON_DIR / "jobs.json"

# Active threads
_active_jobs = {}


# === PERMANENT UTF-8 ENCODING FIX ===
_UTF8_ENV = {**__import__('os').environ, 'PYTHONIOENCODING': 'utf-8', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8'}

def _load_jobs() -> dict:
    """Load cron jobs from file."""
    if CRON_FILE.exists():
        try:
            return json.loads(CRON_FILE.read_text())
        except:
            pass
    return {"jobs": []}


def _save_jobs(data: dict):
    """Save cron jobs to file."""
    CRON_FILE.write_text(json.dumps(data, indent=2))


def cron_list() -> str:
    """List all scheduled cron jobs."""
    data = _load_jobs()
    jobs = data.get("jobs", [])
    
    lines = ["╔══════════════════════════════════════╗",
             "║  GROK CRON JOBS                     ║",
             "╚══════════════════════════════════════╝"]
    
    if not jobs:
        lines.append("\nIngen cron jobs.")
        lines.append("\nTilføj med: cron_add 'interval' 'kommando'")
        lines.append("Interval: 30s, 5m, 1h, 1d")
        return "\n".join(lines)
    
    for job in jobs:
        status = "🟢 Aktiv" if job.get("enabled", True) else "🔴 Inaktiv"
        lines.append(f"\n  [{job.get('id','?')}] {status}")
        lines.append(f"    Kommando: {job.get('command','?')[:60]}")
        lines.append(f"    Interval: {job.get('interval','?')}")
        lines.append(f"    Sidst kørt: {job.get('last_run','aldrig')}")
        lines.append(f"    Antal kørsler: {job.get('run_count', 0)}")
    
    return "\n".join(lines)


def cron_add(interval: str, command: str) -> str:
    """
    Add a cron job. Input: '30s nmap_scan 192.168.1.1' or '1h osint_ip 8.8.8.8'
    Intervals: 30s, 1m, 5m, 15m, 30m, 1h, 6h, 12h, 1d
    """
    import hashlib
    
    # Parse interval to seconds
    interval_map = {
        "10s": 10, "30s": 30, "1m": 60, "5m": 300,
        "15m": 900, "30m": 1800, "1h": 3600,
        "6h": 21600, "12h": 43200, "1d": 86400,
    }
    
    seconds = interval_map.get(interval, 300)  # Default 5 min
    
    job_id = hashlib.md5(f"{interval}:{command}".encode()).hexdigest()[:8]
    
    job = {
        "id": job_id,
        "interval": interval,
        "interval_seconds": seconds,
        "command": command,
        "enabled": True,
        "created": datetime.now().isoformat(),
        "last_run": None,
        "run_count": 0,
    }
    
    data = _load_jobs()
    # Check for duplicate
    for existing in data["jobs"]:
        if existing.get("id") == job_id:
            return f"[FEJL] Job {job_id} eksisterer allerede."
    
    data["jobs"].append(job)
    _save_jobs(data)
    
    # Start background thread
    _start_job(job)
    
    return json.dumps({"action": "added", "id": job_id, "interval": interval, 
                       "command": command, "seconds": seconds}, indent=2)


def cron_remove(job_id: str) -> str:
    """Remove a cron job by ID."""
    data = _load_jobs()
    data["jobs"] = [j for j in data["jobs"] if j.get("id") != job_id]
    _save_jobs(data)
    
    # Stop thread if running
    if job_id in _active_jobs:
        _active_jobs[job_id]["running"] = False
        del _active_jobs[job_id]
    
    return json.dumps({"action": "removed", "id": job_id})


def cron_run_once(job_id: str) -> str:
    """Run a cron job once immediately."""
    data = _load_jobs()
    job = None
    for j in data["jobs"]:
        if j.get("id") == job_id:
            job = j
            break
    
    if not job:
        return f"[FEJL] Job {job_id} ikke fundet."
    
    try:
        r = subprocess.run(job["command"], shell=True, capture_output=True, text=True, timeout=120, encoding='utf-8', errors='replace', env=_UTF8_ENV)
        output = r.stdout[:2000] if r.stdout else r.stderr[:500]
        
        # Update last run
        for j in data["jobs"]:
            if j.get("id") == job_id:
                j["last_run"] = datetime.now().isoformat()
                j["run_count"] = j.get("run_count", 0) + 1
        _save_jobs(data)
        
        return output if output else f"[Job {job_id} kørte uden output]"
    except subprocess.TimeoutExpired:
        return f"[TIMEOUT] Job {job_id} tog for lang tid"
    except Exception as e:
        return f"[FEJL] Job {job_id} fejlede: {str(e)[:200]}"


def _start_job(job: dict):
    """Start a cron job in a background thread."""
    job_id = job["id"]
    seconds = job.get("interval_seconds", 300)
    
    def _run_loop():
        state = {"running": True}
        _active_jobs[job_id] = state
        
        while state["running"]:
            time.sleep(seconds)
            if not state["running"]:
                break
            
            # Run the command
            try:
                r = subprocess.run(job["command"], shell=True, capture_output=True, text=True, timeout=120, encoding='utf-8', errors='replace', env=_UTF8_ENV)
                
                # Save result
                result_file = CRON_DIR / f"{job_id}_result.txt"
                result_file.write_text(f"[{datetime.now().isoformat()}]\n{r.stdout[:2000]}\n{r.stderr[:500]}")
                
                # Update job data
                data = _load_jobs()
                for j in data["jobs"]:
                    if j.get("id") == job_id:
                        j["last_run"] = datetime.now().isoformat()
                        j["run_count"] = j.get("run_count", 0) + 1
                _save_jobs(data)
                
            except:
                pass
    
    t = threading.Thread(target=_run_loop, daemon=True, name=f"cron-{job_id}")
    t.start()


def cron_start_all():
    """Start all enabled cron jobs."""
    data = _load_jobs()
    for job in data["jobs"]:
        if job.get("enabled", True):
            _start_job(job)
    return f"Startede {len([j for j in data['jobs'] if j.get('enabled', True)])} cron jobs."


def cron_stop_all():
    """Stop all cron jobs."""
    for job_id in list(_active_jobs.keys()):
        _active_jobs[job_id]["running"] = False
    _active_jobs.clear()
    return "Stoppede alle cron jobs."