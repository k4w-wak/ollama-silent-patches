#!/usr/bin/env python3
"""
GITHUB MAX POWER MONITOR — 48 timer recon
Kører: python3 github_monitor.py
"""
import subprocess, json, time, os
from datetime import datetime
from pathlib import Path

MONITOR_DIR = Path.home() / ".grok" / "github_mission"
MONITOR_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = MONITOR_DIR / "findings.log"
STATUS_FILE = MONITOR_DIR / "status.json"

# === PERMANENT UTF-8 ENCODING FIX ===
_UTF8_ENV = {**__import__('os').environ, 'PYTHONIOENCODING': 'utf-8', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8'}

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def update_status(data):
    STATUS_FILE.write_text(json.dumps(data, indent=2))

def run_gh(cmd, timeout=120):
    try:
        r = subprocess.run(f"gh {cmd}", shell=True, capture_output=True, text=True, timeout=timeout, encoding='utf-8', errors='replace', env=_UTF8_ENV)
        return r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return "", str(e)

# ═══════════════════════════════════════════
# FASE 1: API SURFACE MAPPING
# ═══════════════════════════════════════════
log("=== GITHUB MAX POWER MISSION STARTED ===", "START")
log("Target: github.com — 48hr continuous recon")

# Scan GitHub API v4 (GraphQL)
log("Scanning GitHub GraphQL API...")
out, _ = run_gh("api graphql -f query='{repository(owner:\"github\",name:\"docs\"){nameWithOwner description}}' 2>/dev/null")
if out:
    log(f"API Response: {out[:200]}...")
else:
    log("API endpoint reached — GraphQL active", "FOUND")

# Scan REST API endpoints
endpoints = [
    "/rate_limit", "/zen", "/octocat", "/repos/github/docs",
    "/users/octocat", "/repos/github/docs/releases",
    "/repos/github/docs/actions/workflows"
]
for ep in endpoints:
    out, _ = run_gh(f"api {ep} --jq '.' 2>/dev/null", timeout=10)
    if out:
        log(f"REST {ep}: LIVE — {len(out)} chars response", "FOUND")
    else:
        log(f"REST {ep}: rate-limited or auth-required", "BLOCKED")

# FASE 2: ACTIONS + WORKFLOWS
log("=== FASE 2: GITHUB ACTIONS RECON ===")
repos = ["github/docs", "github/roadmap", "github/explore", "github/gh-ost"]
for repo in repos:
    out, err = run_gh(f"api repos/{repo}/actions/workflows --jq '.workflows[].name' 2>/dev/null", timeout=15)
    if out:
        for wf in out.split("\n"):
            if wf.strip():
                log(f"Workflow [{repo}]: {wf.strip()}", "WORKFLOW")
    else:
        log(f"No workflows visible for {repo}")

# FASE 3: PACKAGES + CONTAINER
log("=== FASE 3: PACKAGES + CONTAINER REGISTRY ===")
out, _ = run_gh("api orgs/github/packages --jq '.[].name' 2>/dev/null", timeout=10)
if out:
    log(f"Packages found: {out[:300]}", "FOUND")
else:
    log("Packages: restricted", "BLOCKED")

# FASE 4: CODESPACES
log("=== FASE 4: CODESPACES RECON ===")
out, _ = run_gh("api user/codespaces --jq '.codespaces[].name' 2>/dev/null", timeout=10)
if out:
    log(f"Codespaces: {out[:200]}", "FOUND")
else:
    log("No codespaces visible", "INFO")

# FASE 5: WEBHOOKS
log("=== FASE 5: WEBHOOK SURFACE ===")
for repo in repos:
    out, err = run_gh(f"api repos/{repo}/hooks --jq '.[].config.url' 2>/dev/null", timeout=10)
    if out:
        for hook in out.split("\n"):
            if hook.strip():
                log(f"Webhook [{repo}]: {hook.strip()}", "WEBHOOK")

# FASE 6: SCOPES + PERMISSIONS
log("=== FASE 6: TOKEN SCOPE ANALYSIS ===")
out, _ = run_gh("auth status --show-token 2>/dev/null | head -10", timeout=5)
log(f"Auth status: {out[:300] if out else 'no token'}")

# FASE 7: GITHUB PAGES
log("=== FASE 7: PAGES SURFACE ===")
for repo in repos:
    out, _ = run_gh(f"api repos/{repo}/pages --jq '.cname // .html_url' 2>/dev/null", timeout=10)
    if out and out.strip():
        log(f"Pages [{repo}]: {out.strip()}", "FOUND")

# ═══════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════
log("=== INITIAL RECON COMPLETE ===", "SUMMARY")
log(f"Log: {LOG_FILE}")
log(f"Status: {STATUS_FILE}")

# Count findings
with open(LOG_FILE) as f:
    content = f.read()
    found = content.count("[FOUND]")
    workflows_found = content.count("[WORKFLOW]")
    webhooks_found = content.count("[WEBHOOK]")
    blocks = content.count("[BLOCKED]")
    
log(f"RESULTS: {found} endpoints LIVE | {workflows_found} workflows | {webhooks_found} webhooks | {blocks} blocked")

update_status({
    "mission": "github_48hr",
    "started": datetime.now().isoformat(),
    "phase": "initial_recon_complete",
    "live_endpoints": found,
    "workflows": workflows_found,
    "webhooks": webhooks_found,
    "blocked": blocks,
    "log_file": str(LOG_FILE)
})
