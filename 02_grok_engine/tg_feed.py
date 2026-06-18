#!/usr/bin/env python3
"""
GROK LIVE FEED → TELEGRAM
Sender hver scan-opdatering direkte til @supergrokv4bot
"""
import subprocess, json, time, sys
from datetime import datetime

TOKEN = "<REDACTED_TELEGRAM_TOKEN>"
CHAT_ID = 8711492906

def tg(text):
    """Send besked til Telegram"""
    text = text[:4000]  # TG message limit
    try:
        subprocess.run([
            "curl", "-s", "-X", "POST",
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"})
        ], capture_output=True, timeout=5)
    except:
        pass

def api(endpoint):
    """Kald GitHub API"""
    try:
        r = subprocess.run([
            "curl", "-s", f"https://api.github.com{endpoint}",
            "-H", "Accept: application/vnd.github+json",
            "-H", "User-Agent: grok-recon"
        ], capture_output=True, text=True, timeout=15)
        return r.stdout
    except:
        return None

def api_head(endpoint):
    """HEAD request for status codes"""
    try:
        r = subprocess.run([
            "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
            f"https://api.github.com{endpoint}",
            "-H", "Accept: application/vnd.github+json",
            "-H", "User-Agent: grok-recon"
        ], capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except:
        return "ERR"

# ═══════════════════════════════════════════
tg("⚡ <b>GROK LIVE FEED — START</b>\n\nAlle scanninger rapporteres her hvert 60. sekund.\nFund marketes: 💀 CRITICAL | 🔥 HIGH | ⚠️ MEDIUM | ✓ INFO\n\n<i>48 timer recon mod github.com</i>")
time.sleep(2)

scan_count = 0

while True:
    scan_count += 1
    ts = datetime.now().strftime("%H:%M:%S")
    lines = [f"<b>📍 SCAN #{scan_count}</b> — <code>{ts}</code>\n"]
    
    # 1. Rate limit check
    rl = api("/rate_limit")
    if rl:
        try:
            rl_data = json.loads(rl)
            core = rl_data.get("resources",{}).get("core",{})
            lines.append(f"⚙️ API: {core.get('remaining',0)}/{core.get('limit',0)} remaining\n")
        except: pass
    
    # 2. Scan GitHub org repos
    repos = api("/orgs/github/repos?per_page=10&sort=updated")
    found = []
    if repos:
        try:
            data = json.loads(repos)
            if not isinstance(data, list):
                pass
            else:
                for r in data[:10]:
                    name = r.get("full_name","")
                    stars = r.get("stargazers_count", 0)
                    lang = r.get("language", "")
                    actions = r.get("has_actions", False)
                    topics = r.get("topics", [])[:2]
                    has_pages = r.get("has_pages", False)
                    
                    flags = []
                    if actions: flags.append("🔧WF")
                    if has_pages: flags.append("📄Pages")
                    if stars > 20000: flags.append(f"⭐{stars}")
                    
                    # Check for high-value targets
                    high_value = any(t in str(topics).lower() for t in ["ai","copilot","actions","security","api","mcp","codeql"])
                    prefix = "🔥" if high_value else "  "
                    
                    topic_str = ", ".join(topics) if topics else ""
                    flag_str = " ".join(flags)
                    
                    found.append(f"{prefix}{name:<40} {lang:<12} {flag_str:<20} {topic_str[:30]}")
                    
                    if high_value:
                        found.append(f"  └─ HIGH INTEREST: {r.get('description','')[:100]}")
        except: pass
    
    if found:
        lines.append("<b>🎯 REPOS SCANNET:</b>")
        lines.append("<pre>" + "\n".join(found[:12]) + "</pre>")
    else:
        lines.append("⏳ Ingen repo-data...")
    
    # 3. Check specific endpoints for vulnerability surface
    checks = [
        ("/repos/github/spec-kit/contents/.github/workflows", "spec-kit workflows"),
        ("/repos/github/github-mcp-server/contents/.github", "mcp-server CI"),
        ("/repos/github/docs", "github/docs exist"),
    ]
    
    for endpoint, label in checks:
        code = api_head(endpoint)
        if code == "200":
            lines.append(f"✓ {label}: <b>ACCESSIBLE (HTTP 200)</b>")
        elif code == "404":
            lines.append(f"· {label}: 404")
        else:
            lines.append(f"· {label}: {code}")
    
    lines.append(f"\n<i>Næste scan om 60s...</i>")
    
    tg("\n".join(lines))
    
    time.sleep(60)
