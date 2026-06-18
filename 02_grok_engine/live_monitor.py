#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║        GROK MAX POWER — LIVE MISSION MONITOR            ║
║        Target: GITHUB.COM — 48hr Recon                  ║
╚══════════════════════════════════════════════════════════╝
"""
import subprocess, json, time, os, signal, sys
from datetime import datetime
from pathlib import Path

MONITOR_DIR = Path.home() / ".grok" / "github_mission"
MONITOR_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = MONITOR_DIR / "mission.log"
STATUS_FILE = MONITOR_DIR / "status.json"
FINDINGS_FILE = MONITOR_DIR / "findings.json"

# ═══════════════════════════════════════════
# FINDINGS DATABASE
# ═══════════════════════════════════════════
def load_findings():
    if FINDINGS_FILE.exists():
        return json.loads(FINDINGS_FILE.read_text())
    return []

def save_finding(level, title, detail, score=""):
    findings = load_findings()
    findings.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "level": level,
        "title": title,
        "detail": detail[:300],
        "score": score
    })
    FINDINGS_FILE.write_text(json.dumps(findings, indent=2))
    # Also append to log
    with open(LOG_FILE, "a") as f:
        f.write(f"[{findings[-1]['time']}] [{level}] {title} | {detail[:200]}\n")
    return findings

def log_system(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] [SYS] {msg}\n")

# ═══════════════════════════════════════════
# RECON SCANNERS
# ═══════════════════════════════════════════
def scan_github_api():
    """Scan GitHub public API for active attack surface"""
    results = {}
    try:
        r = subprocess.run(
            'curl -s "https://api.github.com/rate_limit" -H "Accept: application/vnd.github+json" -H "User-Agent: recon"',
            shell=True, capture_output=True, text=True, timeout=10
        )
        if r.stdout:
            data = json.loads(r.stdout)
            core = data.get("resources",{}).get("core",{})
            results["api_remaining"] = core.get("remaining", 0)
            results["api_limit"] = core.get("limit", 0)
    except: pass
    return results

def scan_github_org(org="github"):
    """Scan organization repos"""
    repos = []
    try:
        r = subprocess.run(
            f'curl -s "https://api.github.com/orgs/{org}/repos?per_page=30&sort=updated" -H "Accept: application/vnd.github+json" -H "User-Agent: recon"',
            shell=True, capture_output=True, text=True, timeout=15
        )
        if r.stdout:
            data = json.loads(r.stdout)
            for repo in data:
                repos.append({
                    "name": repo["full_name"],
                    "stars": repo.get("stargazers_count", 0),
                    "lang": repo.get("language", ""),
                    "topics": repo.get("topics", [])[:5],
                    "has_actions": repo.get("has_actions", False),
                    "has_pages": repo.get("has_pages", False),
                    "open_issues": repo.get("open_issues_count", 0),
                    "description": (repo.get("description") or "")[:100]
                })
    except: pass
    return repos

def scan_repo_details(repo_full):
    """Deep scan a single repo"""
    findings = []
    try:
        r = subprocess.run(
            f'curl -s "https://api.github.com/repos/{repo_full}" -H "Accept: application/vnd.github+json" -H "User-Agent: recon"',
            shell=True, capture_output=True, text=True, timeout=10
        )
        if r.stdout:
            repo = json.loads(r.stdout)
            
            # Check for sensitive files
            checks = [
                ".github/workflows", "Dockerfile", "package.json",
                "requirements.txt", "pyproject.toml", "go.mod",
                "terraform", "kubernetes", ".yaml", ".yml"
            ]
            
            # Check workflows
            try:
                wr = subprocess.run(
                    f'curl -s "https://api.github.com/repos/{repo_full}/contents/.github/workflows" -H "Accept: application/vnd.github+json" -H "User-Agent: recon"',
                    shell=True, capture_output=True, text=True, timeout=10
                )
                if wr.stdout and "name" in wr.stdout:
                    wf_data = json.loads(wr.stdout)
                    if isinstance(wf_data, list) and len(wf_data) > 0:
                        findings.append(f"Workflows: {len(wf_data)} files")
            except: pass
            
            # Check webhooks
            try:
                hr = subprocess.run(
                    f'curl -s "https://api.github.com/repos/{repo_full}/hooks" -H "Accept: application/vnd.github+json" -H "User-Agent: recon"',
                    shell=True, capture_output=True, text=True, timeout=10
                )
                if hr.stdout and '"url"' in hr.stdout:
                    hooks = json.loads(hr.stdout)
                    if isinstance(hooks, list) and len(hooks) > 0:
                        findings.append(f"Webhooks: {len(hooks)} active")
            except: pass
            
    except: pass
    return findings

# ═══════════════════════════════════════════
# DISPLAY
# ═══════════════════════════════════════════
RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
CYAN = '\033[96m'; MAGENTA = '\033[95m'; WHITE = '\033[97m'
BOLD = '\033[1m'; DIM = '\033[2m'; END = '\033[0m'

def clear():
    os.system('clear')

def header():
    elapsed = datetime.now() - start_time
    hours = int(elapsed.total_seconds() // 3600)
    mins = int((elapsed.total_seconds() % 3600) // 60)
    secs = int(elapsed.total_seconds() % 60)
    
    print(f"""
{RED}{BOLD}╔══════════════════════════════════════════════════════════════╗
║     GROK MAX POWER — LIVE MISSION MONITOR                  ║
║     Target: GITHUB.COM  |  {hours:02d}:{mins:02d}:{secs:02d} elapsed  |  Phase: {current_phase:<26} ║
╚══════════════════════════════════════════════════════════════╝{END}
""")

def show_system_status():
    print(f"  {BOLD}SYSTEM STATUS{END}")
    
    # Hermes gateway
    gw = Path.home() / ".hermes" / "gateway_state.json"
    if gw.exists():
        gs = json.loads(gw.read_text())
        gw_state = gs.get("gateway_state", "?")
        discord = gs.get("platforms",{}).get("discord",{}).get("state","?")
        print(f"  {GREEN}●{END} Hermes: {gw_state:<10} Discord: {discord:<12}")
    else:
        print(f"  {RED}●{END} Hermes: OFFLINE")
    
    # FCC proxy
    try:
        r = subprocess.run("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8082/v1/models",
                          shell=True, capture_output=True, text=True, timeout=3)
        fcc = "ONLINE" if r.stdout.strip() == "200" else "DOWN"
        color = GREEN if fcc == "ONLINE" else RED
        print(f"  {color}●{END} FCC Proxy: {fcc:<10} (Claude 4 via NVIDIA NIM)")
    except:
        print(f"  {RED}●{END} FCC Proxy: DOWN")
    
    # Ollama
    try:
        r = subprocess.run("curl -s http://127.0.0.1:11434/api/tags",
                          shell=True, capture_output=True, text=True, timeout=3)
        if r.stdout:
            data = json.loads(r.stdout)
            models = [m["name"] for m in data.get("models", [])]
        else:
            print(f"  {RED}●{END} Ollama: OFFLINE")
    except:
        print(f"  {RED}●{END} Ollama: OFFLINE")
    
    # GitHub API
    api = scan_github_api()
    remaining = api.get("api_remaining", "?")
    color = GREEN if isinstance(remaining, int) and remaining > 30 else YELLOW
    print(f"  {color}●{END} GitHub API: {remaining}/{api.get('api_limit','?')} requests remaining")
    print()

def show_targets(repos):
    print(f"  {BOLD}TARGET REPOS (sorted by stars){END}")
    print(f"  {'─'*90}")
    print(f"  {'REPO':<45} {'⭐':>6} {'ACTIONS':>8} {'LANG':<12} {'SURFACE'}")
    print(f"  {'─'*90}")
    
    for r in repos[:20]:
        name = r["name"][:44]
        stars = r["stars"]
        actions = "✓" if r.get("has_actions") else "-"
        lang = (r.get("lang") or "")[:11]
        surface = []
        if r.get("has_actions"): surface.append("WF")
        if r.get("has_pages"): surface.append("PAGES")
        topics = r.get("topics", [])[:2]
        surface.extend(topics)
        surf_str = ", ".join(surface)[:30]
        
        color = YELLOW if stars > 20000 else (CYAN if stars > 5000 else WHITE)
        print(f"  {color}{name:<45}{END} {stars:>5}  {actions:>6}   {lang:<12} {DIM}{surf_str}{END}")
    print()

def show_findings():
    findings = load_findings()
    if not findings:
        print(f"  {DIM}  Ingen fund endnu — scannere kører...{END}")
        return
    
    print(f"  {BOLD}FINDINGS ({len(findings)} total){END}")
    print(f"  {'─'*90}")
    
    for f in findings[-15:]:
        icon = {"CRITICAL": "💀", "HIGH": "🔥", "MEDIUM": "⚠️", "INFO": "📡", "FOUND": "✓", "SYSTEM": "⚙️"}
        emoji = icon.get(f["level"], "•")
        color = {"CRITICAL": RED, "HIGH": YELLOW, "MEDIUM": CYAN}.get(f["level"], DIM)
        print(f"  {color}[{f['time']}] {emoji} {f['level']:<8} {f['title'][:60]}{END}")
        if f.get("detail"):
            print(f"  {DIM}         └─ {f['detail'][:80]}{END}")
    print()

def show_activity():
    """Show recent log activity"""
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            lines = f.readlines()[-5:]
            if lines:
                print(f"  {BOLD}LIVE ACTIVITY{END}")
                for line in lines:
                    line = line.strip()[:95]
                    print(f"  {DIM}┊ {line}{END}")
                print()

# ═══════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════
start_time = datetime.now()
current_phase = "INITIAL RECON"
scan_count = 1
repos_cache = []

def signal_handler(sig, frame):
    clear()
    print(f"\n{RED}MISSION PAUSED — {datetime.now().strftime('%H:%M:%S')}{END}")
    print(f"Findings saved to: {FINDINGS_FILE}")
    print(f"Full log: {LOG_FILE}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Initial scan
log_system("MISSION STARTED — GitHub 48hr recon")
save_finding("SYSTEM", "Mission started", "48-timers GitHub recon aktiveret", "")
repos_cache = scan_github_org("github")
log_system(f"Scanned {len(repos_cache)} repos from github org")

while True:
    try:
        clear()
        header()
        show_system_status()
        
        # Every 5th cycle, refresh repo list
        if scan_count % 5 == 0 or not repos_cache:
            repos_cache = scan_github_org("github")
        
        show_targets(repos_cache)
        show_findings()
        show_activity()
        
        # Deep scan top targets every 3 cycles
        if scan_count % 3 == 0 and repos_cache:
            top = sorted(repos_cache, key=lambda r: r["stars"], reverse=True)[:5]
            for repo in top:
                name = repo["name"]
                details = scan_repo_details(name)
                if details:
                    for d in details:
                        save_finding("FOUND", f"[{name}] {d}", "", "")
            
            current_phase = f"DEEP SCAN #{scan_count//3}"
        
        scan_count += 1
        time.sleep(8)  # Refresh every 8 seconds
        
    except KeyboardInterrupt:
        signal_handler(None, None)
    except Exception as e:
        time.sleep(5)
