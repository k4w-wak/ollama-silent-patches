#!/usr/bin/env python3
"""
GROK LIVE FEED v2 — Smarter, færre beskeder, mere info pr. besked
Sender hvert 5. minut: systemstatus + nye fund + recon highlights
"""
import subprocess, json, time
from datetime import datetime, timedelta

TOKEN = "<REDACTED_TELEGRAM_TOKEN>"
CHAT_ID = 8711492906
start_time = datetime.now()

def tg(text):
    text = text[:4096]
    try:
        subprocess.run([
            "curl", "-s", "-X", "POST",
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})
        ], capture_output=True, timeout=5)
    except: pass

def api(endpoint):
    try:
        r = subprocess.run(["curl", "-s", f"https://api.github.com{endpoint}",
            "-H", "Accept: application/vnd.github+json", "-H", "User-Agent: grok-recon"],
            capture_output=True, text=True, timeout=15)
        return r.stdout
    except: return None

previous_highlights = set()

tg("⚡ <b>GROK LIVE FEED v2 — AKTIV</b>\n\nOpdatering hvert <b>5. minut</b>.\nKun vigtige ting — ingen spam.\n\n💀 = Critical fund | 🔥 = Høj interesse\n⚙️ = System | 📡 = Scanning\n\n<i>48 timer recon → github.com</i>")
time.sleep(2)

scan_count = 0

while True:
    scan_count += 1
    elapsed = datetime.now() - start_time
    h, m = divmod(int(elapsed.total_seconds()), 3600)
    m //= 60
    
    lines = [f"<b>📊 UPDATE #{scan_count}</b> | ⏱ {h:02d}:{m:02d} elapsed\n"]
    
    # ── SYSTEM HEALTH ──
    try:
        r = subprocess.run("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8082/v1/models",
                          shell=True, capture_output=True, text=True, timeout=3)
        fcc = "✅" if r.stdout.strip() == "200" else "❌"
    except: fcc = "❌"
    
    try:
        r = subprocess.run("curl -s http://127.0.0.1:11434/api/tags",
                          shell=True, capture_output=True, text=True, timeout=3)
    except: ollama = "❌"
    
    gw_file = "/home/admin_user/.hermes/gateway_state.json"
    try:
        with open(gw_file) as f:
            gs = json.load(f)
        gw = "✅" if gs.get("gateway_state") == "running" else "❌"
        tg_conn = "✅" if gs.get("platforms",{}).get("telegram",{}).get("state") == "connected" else "❌"
    except: gw, tg_conn = "❌", "❌"
    
    lines.append(f"⚙️ FCC {fcc} | Ollama {ollama} | GW {gw} | TG {tg_conn}")
    
    # ── GITHUB API STATUS ──
    rl_raw = api("/rate_limit")
    if rl_raw:
        try:
            rl = json.loads(rl_raw)
            core = rl.get("resources",{}).get("core",{})
            search = rl.get("resources",{}).get("search",{})
            lines.append(f"📡 API: Core {core.get('remaining',0)}/{core.get('limit',0)} | Search {search.get('remaining',0)}/{search.get('limit',0)}")
        except: pass
    
    # ── HIGH VALUE REPOS ──
    repos_raw = api("/orgs/github/repos?per_page=30&sort=updated")
    highlights = []
    if repos_raw:
        try:
            repos = json.loads(repos_raw)
            for r in repos:
                name = r.get("full_name","")
                stars = r.get("stargazers_count", 0)
                topics = r.get("topics", [])
                desc = (r.get("description") or "")[:80]
                actions = r.get("has_actions", False)
                pages = r.get("has_pages", False)
                lang = r.get("language", "")
                
                score = 0
                tags = []
                if stars > 50000: score += 5; tags.append(f"⭐{stars//1000}k")
                elif stars > 10000: score += 3; tags.append(f"⭐{stars//1000}k")
                elif stars > 5000: score += 2
                
                if "ai" in str(topics).lower() or "copilot" in name.lower(): score += 4; tags.append("🤖AI")
                if "mcp" in str(topics).lower() or "mcp" in name.lower(): score += 3; tags.append("🔌MCP")
                if "security" in str(topics).lower() or "codeql" in name.lower(): score += 3; tags.append("🛡SEC")
                if actions: score += 2; tags.append("🔧WF")
                if pages: score += 1
                
                if score >= 3:
                    tag_str = " ".join(tags)
                    highlights.append((score, f"🔥 <b>{name}</b> [{lang}] {tag_str}\n  <i>{desc}</i>"))
        except: pass
    
    if highlights:
        highlights.sort(reverse=True)
        lines.append(f"\n<b>🎯 TOP TARGETS:</b>")
        seen = 0
        for score, line in highlights[:8]:
            if line not in previous_highlights:
                previous_highlights.add(line)
                if seen < 5:
                    lines.append(line)
                    seen += 1
        # Prune old highlights
        if len(previous_highlights) > 100:
            previous_highlights.clear()
    
    # ── ACTIVE ENDPOINT CHECKS ──
    endpoint_checks = [
        ("/repos/github/spec-kit/contents/.github/workflows", "spec-kit → workflow files"),
        ("/repos/github/github-mcp-server", "mcp-server → repo accessible"),
        ("/repos/github/copilot-cli", "copilot-cli → repo accessible"),
        ("/repos/github/gh-aw", "gh-aw → agentic workflows"),
    ]
    
    new_access = []
    for ep, label in endpoint_checks:
        try:
            r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                f"https://api.github.com{ep}", "-H", "Accept: application/vnd.github+json",
                "-H", "User-Agent: grok-recon"], capture_output=True, text=True, timeout=8)
            code = r.stdout.strip()
            if code == "200":
                new_access.append(f"✓ {label}")
            elif code != "404":
                new_access.append(f"· {label} [{code}]")
        except: pass
    
    if new_access:
        lines.append(f"\n<b>🔓 TILGÆNGELIGE:</b>")
        lines.extend(new_access[:5])
    
    lines.append(f"\n<i>Næste: {datetime.now() + timedelta(minutes=5):%H:%M}</i>")
    
    tg("\n".join(lines))
    
    time.sleep(300)  # 5 minutter
