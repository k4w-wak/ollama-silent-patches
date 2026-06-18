"""
GROK SWARM — Multi-Agent System
================================
Agent-tilbehør der kører SEKVENTIELT men med specialiserede prompts.
Kan ikke køre parallelt (Ollama limitation) men kan specialisere.

MODES:
  - SWARM:  Del targets op mellem specialiserede agenter
  - RACE:   Kør samme opgave 2x med forskellige modeller, vælg bedste
  - PIPELINE: Kør agenter i rækkefølge (recon → exploit → report)

STRATEGY:
  I stedet for parallel execution (Ollama can't), vi bruger:
  1. Specialiserede agent-personalities
  2. Model-switching per phase
  3. Result aggregation
  4. Quality scoring
"""

import json
import time
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# ============================================================
# REAL RECON — actual tool execution (no LLM hallucination)
# ============================================================
RECON_TOOLS = {
    "subfinder": {"cmd": "subfinder", "args": ["-d", "{target}", "-silent"], "timeout": 120},
    "httpx": {"cmd": "httpx", "args": ["-u", "{target}", "-status-code", "-title", "-tech-detect", "-silent"], "timeout": 60},
    "nuclei": {"cmd": "nuclei", "args": ["-u", "{target}", "-severity", "medium,high,critical", "-silent", "-timeout", "30"], "timeout": 300},
    "nmap": {"cmd": "nmap", "args": ["-sV", "-sC", "--top-ports", "100", "-T4", "{target}"], "timeout": 180},
    "whatweb": {"cmd": "whatweb", "args": ["{target}"], "timeout": 30},
    "curl_headers": {"cmd": "curl", "args": ["-sI", "-L", "-m", "15", "https://{target}"], "timeout": 20},
}


def run_real_recon(target: str) -> str:
    """Run ACTUAL recon tools and return real findings.
    This replaces LLM hallucination with genuine tool output."""
    results = []
    results.append(f"=== REAL RECON for {target} ===")
    results.append(f"Timestamp: {datetime.now().isoformat()}\n")

    # 1. Subfinder — passive subdomain enum
    try:
        r = subprocess.run(
            ["subfinder", "-d", target, "-silent"],
            capture_output=True, text=True, timeout=120
        )
        subs = [s.strip() for s in r.stdout.strip().split("\n") if s.strip()]
        if subs:
            results.append(f"[SUBFINDER] {len(subs)} subdomains found:")
            for s in subs[:30]:  # cap at 30
                results.append(f"  - {s}")
            if len(subs) > 30:
                results.append(f"  ... and {len(subs)-30} more")
        else:
            results.append("[SUBFINDER] No subdomains found")
    except Exception as e:
        results.append(f"[SUBFINDER] Error: {str(e)[:100]}")

    # 2. HTTP headers — curl -sI
    for proto in ["https://", "http://"]:
        try:
            r = subprocess.run(
                ["curl", "-sI", "-L", "-m", "15", f"{proto}{target}"],
                capture_output=True, text=True, timeout=20
            )
            if r.stdout.strip():
                results.append(f"\n[CURL HEADERS {proto}{target}]")
                results.append(r.stdout.strip()[:2000])
                break  # prefer https
        except Exception as e:
            results.append(f"[CURL {proto}] Error: {str(e)[:60]}")

    # 3. httpx — status, title, tech detect
    try:
        r = subprocess.run(
            ["httpx", "-u", target, "-status-code", "-title", "-tech-detect", "-silent"],
            capture_output=True, text=True, timeout=60
        )
        if r.stdout.strip():
            results.append(f"\n[HTTPX] {r.stdout.strip()[:2000]}")
    except Exception as e:
        results.append(f"[HTTPX] Error: {str(e)[:80]}")

    # 4. whatweb — tech fingerprinting
    try:
        r = subprocess.run(
            ["whatweb", target],
            capture_output=True, text=True, timeout=30
        )
        if r.stdout.strip():
            results.append(f"\n[WHATWEB] {r.stdout.strip()[:1500]}")
    except FileNotFoundError:
        pass  # whatweb not installed
    except Exception as e:
        results.append(f"[WHATWEB] Error: {str(e)[:80]}")

    # 5. Nuclei — vulnerability scanning (medium+ severity, fast templates only)
    try:
        r = subprocess.run(
            ["nuclei", "-u", target, "-severity", "medium,high,critical", "-silent",
             "-timeout", "10", "-bulk-size", "25", "-c", "50",
             "-tags", "cve,misconfig,exposure,token,default-login"],
            capture_output=True, text=True, timeout=120
        )
        if r.stdout.strip():
            results.append(f"\n[NUCLEI] Vulnerability scan results:")
            results.append(r.stdout.strip()[:3000])
        else:
            results.append(f"\n[NUCLEI] No medium/high/critical vulns found")
    except subprocess.TimeoutExpired:
        results.append(f"\n[NUCLEI] Scan timed out (120s limit) — target may be filtering probes")
    except Exception as e:
        results.append(f"[NUCLEI] Error: {str(e)[:80]}")

    output = "\n".join(results)
    # Truncate to 6000 chars for context window
    if len(output) > 6000:
        output = output[:3000] + "\n...[truncated]...\n" + output[-3000:]
    return output


def run_real_verify(target: str, recon_data: str) -> str:
    """Run ACTUAL verification commands on discovered subdomains and endpoints.
    Probes each subdomain from recon data with curl, checks for common vulns.
    Returns factual results — no hallucination possible."""
    import re
    results = []
    results.append(f"=== REAL VERIFY for {target} ===")
    results.append(f"Timestamp: {datetime.now().isoformat()}\n")

    # Extract subdomains from recon data
    subdomains = []
    for line in recon_data.split("\n"):
        line = line.strip()
        if line.startswith("- ") and "." in line and not line.startswith("- and"):
            sub = line.lstrip("- ").strip()
            if sub and len(sub) < 80 and sub.count(".") >= 1:
                subdomains.append(sub)
    subdomains = subdomains[:15]  # Cap at 15 to keep runtime sane
    if not subdomains:
        results.append("[VERIFY] No subdomains found in recon data to verify")
        return "\n".join(results)

    results.append(f"[VERIFY] Probing {len(subdomains)} subdomains...\n")

    # 1. Check each subdomain for HTTP reachability and response codes
    live_subs = []
    for sub in subdomains:
        try:
            r = subprocess.run(
                ["curl", "-sI", "-L", "-m", "8", f"https://{sub}"],
                capture_output=True, text=True, timeout=12
            )
            first_line = r.stdout.strip().split("\n")[0] if r.stdout.strip() else "NO RESPONSE"
            status_code = first_line.split()[1] if len(first_line.split()) > 1 else "??"

            if status_code in ("200", "301", "302", "307", "403", "401"):
                live_subs.append(sub)
                results.append(f"[CURL] https://{sub} → {first_line}")

                # Check for interesting headers
                for header_line in r.stdout.split("\n"):
                    hl = header_line.lower()
                    if any(k in hl for k in ["server:", "x-powered-by:", "x-aspnet", "set-cookie:", "www-authenticate"]):
                        results.append(f"  {header_line.strip()}")
            elif status_code == "??":
                pass  # No response, skip
        except Exception:
            pass

    # 2. Check for dangling CNAME / subdomain takeover on live subs
    results.append(f"\n[VERIFY] Checking {len(live_subs)} live subdomains for takeover candidates...")
    for sub in live_subs:
        try:
            r = subprocess.run(
                ["curl", "-s", "-m", "8", f"https://{sub}"],
                capture_output=True, text=True, timeout=12
            )
            body = r.stdout.lower()
            # Subdomain takeover indicators
            takeover_keywords = ["s3 bucket", "no such bucket", "herokucdn", "cloudfront", 
                                "github pages", "does not exist", "page not found",
                                "deleted bucket", "bad request", "no such app"]
            for kw in takeover_keywords:
                if kw in body:
                    results.append(f"[TAKEOVER CANDIDATE] {sub} → keyword: '{kw}' found in response body")
                    break
        except Exception:
            pass

    # 3. Quick security header check on main target
    results.append(f"\n[VERIFY] Security headers on https://{target}...")
    try:
        r = subprocess.run(
            ["curl", "-sI", "-m", "10", f"https://{target}"],
            capture_output=True, text=True, timeout=15
        )
        headers_lower = r.stdout.lower()
        security_headers = {
            "strict-transport-security": "HSTS",
            "content-security-policy": "CSP",
            "x-frame-options": "X-Frame-Options",
            "x-content-type-options": "X-Content-Type-Options",
            "x-xss-protection": "X-XSS-Protection",
            "referrer-policy": "Referrer-Policy",
        }
        for header, name in security_headers.items():
            if header in headers_lower:
                # Find the actual line
                for line in r.stdout.split("\n"):
                    if header in line.lower():
                        results.append(f"  ✅ {line.strip()}")
                        break
            else:
                results.append(f"  ❌ MISSING: {name}")
    except Exception as e:
        results.append(f"[VERIFY] Header check error: {str(e)[:60]}")

    # 4. CORS check
    results.append(f"\n[VERIFY] CORS check on https://{target}...")
    try:
        r = subprocess.run(
            ["curl", "-sI", "-m", "10", "-H", "Origin: https://evil.com", f"https://{target}"],
            capture_output=True, text=True, timeout=15
        )
        for line in r.stdout.split("\n"):
            if "access-control-allow" in line.lower():
                results.append(f"  🚨 CORS: {line.strip()}")
        if "access-control-allow" not in r.stdout.lower():
            results.append(f"  ✅ No CORS headers reflecting Origin")
    except Exception as e:
        results.append(f"[VERIFY] CORS check error: {str(e)[:60]}")

    output = "\n".join(results)
    if len(output) > 6000:
        output = output[:3000] + "\n...[truncated]...\n" + output[-3000:]
    return output


def run_real_exploit(target: str, recon_data: str) -> str:
    """Run ACTUAL exploitation/assessment tools on target.
    Replaces the hallucinating LLM exploit agent with REAL tool output.
    No hallucination possible — every finding comes from a real command."""
    import re
    results = []
    results.append(f"=== REAL EXPLOIT for {target} ===")
    results.append(f"Timestamp: {datetime.now().isoformat()}\n")

    # Extract live subdomains from recon data
    subdomains = []
    for line in recon_data.split("\n"):
        line = line.strip()
        if line.startswith("- ") and "." in line and not line.startswith("- and"):
            sub = line.lstrip("- ").strip()
            if sub and len(sub) < 80 and sub.count(".") >= 1:
                subdomains.append(sub)
    subdomains = subdomains[:20]  # Cap at 20

    # 1. Nuclei — full vulnerability scan with more templates
    results.append("[NUCLEI EXPLOIT SCAN]")
    try:
        r = subprocess.run(
            ["nuclei", "-u", target, "-severity", "low,medium,high,critical",
             "-silent", "-timeout", "10", "-bulk-size", "25", "-c", "50",
             "-tags", "cve,misconfig,exposure,token,default-login,xss,sqli,ssrf,lfi,rce,redirect,upload"],
            capture_output=True, text=True, timeout=180
        )
        if r.stdout.strip():
            results.append(r.stdout.strip()[:4000])
        else:
            results.append("No vulns found by nuclei exploit scan")
    except subprocess.TimeoutExpired:
        results.append("Nuclei exploit scan timed out (180s)")
    except Exception as e:
        results.append(f"Nuclei error: {str(e)[:100]}")

    # 2. Test for common auth bypass / exposed endpoints
    results.append("\n[AUTH BYPASS PROBES]")
    auth_paths = [
        "/admin", "/login", "/api", "/graphql", "/swagger", "/api-docs",
        "/.env", "/.git", "/.htaccess", "/wp-admin", "/phpmyadmin",
        "/console", "/debug", "/metrics", "/healthz", "/status",
        "/actuator", "/.well-known/security.txt", "/robots.txt",
    ]
    for path in auth_paths:
        try:
            r = subprocess.run(
                ["curl", "-sI", "-m", "6", "-L", f"https://{target}{path}"],
                capture_output=True, text=True, timeout=10
            )
            first_line = r.stdout.strip().split("\n")[0] if r.stdout.strip() else ""
            if first_line and "404" not in first_line and "0" not in first_line:
                status = first_line.split()[1] if len(first_line.split()) > 1 else "??"
                if status not in ("0",):
                    results.append(f"  https://{target}{path} → {status} {first_line.strip()}")
        except Exception:
            pass

    # 3. CORS deep check — multiple origins
    results.append("\n[CORS DEEP PROBES]")
    cors_origins = [
        "https://evil.com",
        "null",
        "https://evil." + target,
        "https://subdomain.evil.com",
    ]
    for origin in cors_origins:
        try:
            r = subprocess.run(
                ["curl", "-sI", "-m", "8", "-H", f"Origin: {origin}", f"https://{target}"],
                capture_output=True, text=True, timeout=12
            )
            cors_headers = []
            for line in r.stdout.split("\n"):
                if "access-control-allow" in line.lower():
                    cors_headers.append(line.strip())
            if cors_headers:
                results.append(f"  Origin: {origin}")
                for h in cors_headers:
                    results.append(f"    🚨 {h}")
        except Exception:
            pass
    if not any("access-control" in r.lower() for r in results if isinstance(r, str)):
        results.append("  ✅ No CORS reflection with any origin")

    # 4. Cookie security check
    results.append("\n[COOKIE SECURITY CHECK]")
    try:
        r = subprocess.run(
            ["curl", "-sI", "-m", "10", f"https://{target}"],
            capture_output=True, text=True, timeout=15
        )
        for line in r.stdout.split("\n"):
            if "set-cookie" in line.lower():
                cookie = line.strip()
                issues = []
                if "secure" not in cookie.lower() and "httponly" not in cookie.lower() and "__" not in cookie.lower():
                    # Only flag cookies missing BOTH secure AND httponly
                    if "secure" not in cookie.lower():
                        issues.append("missing Secure flag")
                    if "httponly" not in cookie.lower():
                        issues.append("missing HttpOnly flag")
                    if "samesite" not in cookie.lower():
                        issues.append("missing SameSite")
                if issues:
                    results.append(f"  ⚠️ {cookie[:100]}")
                    results.append(f"    Issues: {', '.join(issues)}")
                else:
                    results.append(f"  ✅ {cookie[:80]}")
    except Exception as e:
        results.append(f"  Cookie check error: {str(e)[:60]}")

    # 5. Open redirect check
    results.append("\n[OPEN REDIRECT PROBES]")
    redirect_payloads = [
        "/redirect?url=https://evil.com",
        "/redirect?next=https://evil.com",
        "/login?redirect=https://evil.com",
        "/auth/callback?redirect_uri=https://evil.com",
        "/oauth/authorize?redirect_uri=https://evil.com",
    ]
    for payload in redirect_payloads:
        try:
            r = subprocess.run(
                ["curl", "-sI", "-m", "6", f"https://{target}{payload}"],
                capture_output=True, text=True, timeout=10
            )
            for line in r.stdout.split("\n"):
                if "location:" in line.lower() and "evil.com" in line.lower():
                    results.append(f"  🚨 OPEN REDIRECT: https://{target}{payload}")
                    results.append(f"     Redirects to: {line.strip()}")
        except Exception:
            pass
    if not any("OPEN REDIRECT" in r for r in results):
        results.append("  ✅ No open redirect found with common payloads")

    # 6. Subdomain nuclei scan (top 5 interesting subs)
    if subdomains:
        results.append(f"\n[SUBDOMAIN NUCLEI SCAN] (top {min(5, len(subdomains))} subs)")
        for sub in subdomains[:5]:
            try:
                r = subprocess.run(
                    ["nuclei", "-u", sub, "-severity", "medium,high,critical",
                     "-silent", "-timeout", "8", "-c", "20",
                     "-tags", "cve,misconfig,exposure,takeover"],
                    capture_output=True, text=True, timeout=60
                )
                if r.stdout.strip():
                    results.append(f"  [{sub}] {r.stdout.strip()[:500]}")
            except Exception:
                pass

    output = "\n".join(results)
    if len(output) > 8000:
        output = output[:4000] + "\n...[truncated]...\n" + output[-4000:]
    return output


# Agent personalities — Grok's Swarm Team
# GROK er master. Disse agenter er hans udsendte styrker.
AGENT_PERSONALITIES = {
    "recon": {
        "name": "Recon Scout",
        "prompt": """You are a RECON SCOUT — part of Grok's Swarm. You receive REAL scan data from actual security tools (subfinder, nuclei, httpx, curl, whatweb).

Your job is to ANALYZE the real data — NOT to hallucinate or invent findings.
- Summarize the key findings from the scan data
- Identify interesting subdomains, unusual headers, exposed tech
- Note any CVEs or vulns from nuclei
- Highlight potential attack surface (auth endpoints, APIs, unusual ports)
- Be FACTUAL — only report what the scan data actually shows
- Structure your output as findings with severity estimates

DO NOT invent subdomains, CVEs, or vulnerabilities not in the scan data.
DO NOT add disclaimers about needing more access — just analyze what's there.""",
        "model": "glm-5.1:cloud",  # Fast cloud — quick recon overview
    },
    # "exploit" agent REMOVED — was pure LLM hallucination.
    # Replaced by run_real_exploit() which uses ACTUAL security tools.
    "analyst": {
        "name": "Deep Analyst",
        "prompt": """You are the DEEP ANALYST — Grok's heavy hitter. 284 billion parameters of pure security analysis power.

You receive ALL data: real_recon results, real_exploit probes, real_verify checks, AND the recon scout's analysis.

Your mission:
1. CROSS-REFERENCE all data sources — find patterns others missed
2. CHAIN vulnerabilities — does a missing header + exposed endpoint = real attack?
3. ASSESS real impact — not theoretical, but what's actually exploitable from the data
4. DEEP DIVE on any anomalies — unusual headers, unexpected status codes, misconfig combos
5. RANK findings by actual bounty value — what would a CISO actually care about?
6. Think about business logic — what does this target DO? Where are the money flows?

You have 3 thinking modes:
- No thinking: quick pattern recognition
- Thinking: careful logical analysis  
- Max thinking: maximum reasoning on the hardest problems

USE YOUR BRAIN. You're not a summarizer — you're a HUNTER finding what others miss.

CRITICAL: Only base findings on REAL data from the tools. No fabrication.
Mark each finding: [CONFIRMED] / [UNVERIFIED] / [CHAIN: requires X+Y]""",
        "model": "glm-5.1:cloud",  # hurtig+stabil
    },
    "verify": {
        "name": "Bounty Verifier",
        "prompt": """You are a BOUNTY VERIFICATION SPECIALIST — part of Grok's Swarm. You receive REAL scan data from actual security tools plus REAL verification results (curl probes, CORS checks, security header checks, takeover tests).

Your job is to ANALYZE the real data — NOT to invent findings.

CRITICAL RULES:
1. ONLY mark a finding [CONFIRMED] if the REAL probe data supports it
2. If curl shows a subdomain returns 200/301/403 — that's real. Use it.
3. If CORS check shows no reflection — mark CORS as [DISPROVEN], not [CONFIRMED]
4. If security headers are present — that's GOOD, not a finding
5. If a subdomain has takeover keywords — that's a real [CONFIRMED] finding
6. If a subdomain IS reachable but you can't actually exploit it — mark [UNVERIFIED]
7. NEVER fabricate curl commands you didn't actually run
8. NEVER invent CVEs, server versions, or vulnerabilities not in the real data

OUTPUT FORMAT for each finding:
[CONFIRMED] / [DOWNGRADED] / [DISPROVEN] / [UNVERIFIED] - vulnerability_type - honest_severity
  Evidence: what the REAL data shows
  Reproduction: only reference commands that were ACTUALLY run
  Actual Impact: based on real evidence only
  Honest Severity: CRITICAL/HIGH/MEDIUM/LOW based on ACTUAL impact

Better [UNVERIFIED] than a fabricated [CONFIRMED].""",
        "model": "glm-5.1:cloud",  # hurtig+stabil for verification
    },
    "reporter": {
        "name": "Report Writer",
        "prompt": """You are a BUG BOUNTY REPORT WRITER — part of Grok's Swarm. Your job is to compile VERIFIED findings into professional reports.

ABSOLUTE RULES — VIOLATION = INVALID REPORT:
1. NEVER include findings marked [DISPROVEN]. Delete them entirely. No exceptions.
2. NEVER call [UNVERIFIED] findings "confirmed" or "proven". Mark them [UNVERIFIED] with caveats.
3. NEVER upgrade severity above what the verify agent assigned. If verify said HIGH, you write HIGH — not CRITICAL.
4. If the verifier marked a finding [DOWNGRADED], use the DOWNGRADED severity — NOT the original.
5. ALWAYS include the verifier's reproduction commands as proof of concept.
6. If ALL findings are [DISPROVEN], write "No verifiable vulnerabilities found" — do NOT fabricate findings.

OUTPUT FORMAT:
- Executive Summary (honest severity, no inflation)
- Technical Findings (only [CONFIRMED] and [UNVERIFIED] with honest severity)
- Proof of Concept (curl commands from verify agent)
- Remediation

CVSS scores, OWASP categories, remediation timelines. Write for a CISO — clear, actionable, honest.""",
        "model": "glm-5.1:cloud",  # Cloud — fast, stable, good writing
    },
}

# Swarm modes
SWARM_MODES = ["swarm", "race", "pipeline"]


class SwarmConfig:
    """Configuration for a swarm run."""
    def __init__(
        self,
        mode: str = "pipeline",
        agents: List[str] = None,
        model_override: str = None,
        output_dir: str = None,
        targets: List[str] = None,
    ):
        self.mode = mode
        self.agents = agents or ["recon", "analyst", "verify", "reporter"]  # Grok's swarm team
        self.model_override = model_override
        self.output_dir = output_dir or str(Path.home() / "06_osint_forensics" / "swarm_reports")
        self.targets = targets or []
        
        # Validate
        if self.mode not in SWARM_MODES:
            raise ValueError(f"Mode must be one of {SWARM_MODES}")


class SwarmResult:
    """Result from a single agent."""
    def __init__(self, agent_name: str, model: str, findings: str, duration: float):
        self.agent_name = agent_name
        self.model = model
        self.findings = findings
        self.duration = duration
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "agent": self.agent_name,
            "model": self.model,
            "findings": self.findings,
            "findings_length": len(self.findings),
            "duration_seconds": round(self.duration, 1),
            "timestamp": self.timestamp,
        }


class AgentSwarm:
    """
    Multi-Agent Orchestrator for Grok.
    
    Manages specialized agents that run sequentially (not parallel — Ollama limit).
    Each agent has a personality, model preference, and task scope.
    """
    
    def __init__(self, config: SwarmConfig = None):
        self.config = config or SwarmConfig()
        self.results: List[SwarmResult] = []
        self.log_path = Path.home() / ".grok" / "logs" / "swarm.log"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        print(f"  🐝 {line}")
        with open(self.log_path, "a") as f:
            f.write(line + "\n")
    
    def _run_agent(self, agent_name: str, target: str, context: str = "") -> SwarmResult:
        """Run a single agent via Ollama HTTP API (/api/chat)."""
        personality = AGENT_PERSONALITIES.get(agent_name)
        if not personality:
            personality = AGENT_PERSONALITIES["recon"]
        
        model = self.config.model_override or personality["model"]
        system_prompt = personality["prompt"]
        
        # Build messages for chat API (system + user)
        messages = [{"role": "system", "content": system_prompt}]
        if context:
            messages.append({"role": "user", "content": f"CONTEXT FROM PREVIOUS AGENT:\n{context}\n\nTARGET: {target}"})
        else:
            messages.append({"role": "user", "content": f"TARGET: {target}"})
        
        self._log(f"Agent '{personality['name']}' ({model}) → {target}")
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"num_predict": 8192},
        }
        
        start = time.time()
        try:
            resp = requests.post(
                "http://localhost:11434/api/chat",
                json=payload,
                timeout=600,
            )
            duration = time.time() - start
            
            if resp.status_code != 200:
                self._log(f"❌ {personality['name']} HTTP {resp.status_code}: {resp.text[:200]}")
                return SwarmResult(agent_name, model, f"[HTTP {resp.status_code}: {resp.text[:200]}]", duration)
            
            data = resp.json()
            output = data.get("message", {}).get("content", "").strip()
            
            if not output:
                # Fallback: check if response has content at top level
                output = data.get("response", "").strip()
            
            if not output:
                output = "[No output from agent]"
            
            # Truncate to 8000 chars for next agent context (preserve more findings)
            if len(output) > 8000:
                output = output[:4000] + "\n...[truncated]...\n" + output[-4000:]
            
            sr = SwarmResult(agent_name, model, output, duration)
            self._log(f"✅ {personality['name']} done in {duration:.1f}s — {len(output)} chars")
            return sr
            
        except requests.exceptions.Timeout:
            duration = time.time() - start
            self._log(f"⏰ {personality['name']} timed out after {duration:.1f}s")
            return SwarmResult(agent_name, model, "[Agent timed out]", duration)
        except requests.exceptions.ConnectionError:
            duration = time.time() - start
            self._log(f"❌ {personality['name']} connection refused — Ollama not running?")
            return SwarmResult(agent_name, model, "[Connection refused: is Ollama running?]", duration)
        except Exception as e:
            duration = time.time() - start
            self._log(f"❌ {personality['name']} error: {str(e)[:100]}")
            return SwarmResult(agent_name, model, f"[Agent error: {str(e)[:200]}]", duration)
    
    def run_swarm(self, targets: List[str] = None) -> Dict:
        """
        SWARM mode: Split targets across specialized agents.
        Each target gets real recon → LLM analysis → exploit pipeline.
        """
        targets = targets or self.config.targets
        if not targets:
            return {"error": "No targets specified"}
        
        self._log(f"🐝 SWARM mode — {len(targets)} targets, {len(self.config.agents)} agents")
        all_results = []
        
        for target in targets:
            self._log(f"🎯 Target: {target}")
            
            # Real recon first
            self._log(f"🔍 REAL RECON — running actual tools on {target}")
            real_recon_data = run_real_recon(target)
            real_sr = SwarmResult("real_recon", "tools", real_recon_data, 0)
            all_results.append(real_sr)
            
            # LLM agents analyze real data
            context = real_recon_data
            for agent_name in self.config.agents:
                sr = self._run_agent(agent_name, target, context)
                all_results.append(sr)
                context = sr.findings
        
        self.results = all_results
        return self._compile_results()
    
    def run_race(self, target: str) -> Dict:
        """
        RACE mode: Two models compete on the same task.
        Best result wins. Uses quality scoring.
        """
        self._log(f"🏁 RACE mode — 2 models competing on {target}")
        
        race_models = ["glm-5.1:cloud", "kimi-k2.6:cloud"]
        results = {}
        
        for model in race_models:
            self._log(f"🏇 {model} starts...")
            start = time.time()
            try:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a bug bounty recon specialist. Be thorough and structured."},
                        {"role": "user", "content": f"Bug bounty recon on {target}. Run subfinder, whatweb, curl headers analysis. Report all findings with severity levels."},
                    ],
                    "stream": False,
                    "options": {"num_predict": 8192},
                }
                resp = requests.post("http://localhost:11434/api/chat", json=payload, timeout=600)
                duration = time.time() - start
                if resp.status_code != 200:
                    results[model] = {"output": f"[HTTP {resp.status_code}]", "duration": duration, "quality_score": 0}
                else:
                    data = resp.json()
                    output = data.get("message", {}).get("content", "") or data.get("response", "")
                    results[model] = {
                        "output": output,
                        "duration": duration,
                        "length": len(output) if output else 0,
                        "quality_score": self._score_quality(output),
                    }
                    self._log(f"✅ {model} done in {duration:.1f}s — score: {results[model]['quality_score']}")
            except Exception as e:
                results[model] = {"output": f"Error: {e}", "duration": 0, "quality_score": 0}
        
        # Pick winner
        winner = max(results, key=lambda m: results[m]["quality_score"])
        self._log(f"🏆 Winner: {winner} (score: {results[winner]['quality_score']})")
        
        return {
            "mode": "race",
            "target": target,
            "winner": winner,
            "scores": {m: r["quality_score"] for m, r in results.items()},
            "winning_output": results[winner]["output"],
            "all_results": results,
        }
    
    def run_pipeline(self, target: str) -> Dict:
        """
        PIPELINE v3 — Grok's Swarm: real tools + cloud agents.
        real_recon → LLM recon → real_exploit → real_verify → Deep Analyst → verify → reporter
        """
        self._log(f"🔗 GROK SWARM v3 — target: {target}")
        
        # PHASE 0: REAL RECON — actual tool execution
        self._log(f"🔍 REAL RECON — running actual tools on {target}")
        real_recon_data = run_real_recon(target)
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        real_recon_path = Path(self.config.output_dir) / f"{ts}_real_recon_{target.replace('.', '_')}.txt"
        real_recon_path.parent.mkdir(parents=True, exist_ok=True)
        real_recon_path.write_text(real_recon_data)
        self._log(f"💾 Real recon saved ({len(real_recon_data)} chars)")
        
        recon_sr = SwarmResult("real_recon", "tools", real_recon_data, 0)
        
        # PHASE 1: LLM recon ANALYSIS — quick overview
        self._log(f"📎 Phase: recon (glm-5.1 quick overview)")
        recon_llm = self._run_agent("recon", target, real_recon_data)
        
        # PHASE 2: REAL EXPLOIT — actual tools, NO LLM hallucination
        self._log(f"⚡ REAL EXPLOIT — running actual security tools on {target}")
        real_exploit_data = run_real_exploit(target, real_recon_data)
        exploit_sr = SwarmResult("real_exploit", "tools", real_exploit_data, 0)
        
        real_exploit_path = Path(self.config.output_dir) / f"{ts}_real_exploit_{target.replace('.', '_')}.txt"
        real_exploit_path.write_text(real_exploit_data)
        self._log(f"💾 Real exploit saved ({len(real_exploit_data)} chars)")
        
        # PHASE 3: REAL VERIFY — actual curl probes
        self._log(f"🔍 REAL VERIFY — probing subdomains and security headers on {target}")
        real_verify_data = run_real_verify(target, real_recon_data)
        verify_sr = SwarmResult("real_verify", "tools", real_verify_data, 0)
        
        real_verify_path = Path(self.config.output_dir) / f"{ts}_real_verify_{target.replace('.', '_')}.txt"
        real_verify_path.write_text(real_verify_data)
        self._log(f"💾 Real verify saved ({len(real_verify_data)} chars)")
        
        all_results = [recon_sr, recon_llm, exploit_sr, verify_sr]
        
        # PHASE 4: DEEP ANALYST — glm-5.1 gets ALL real data + recon analysis
        # This is the HEAVY HITTER — cross-references everything, chains vulns, finds patterns
        full_context = (
            "=== REAL RECON DATA ===\n" + real_recon_data +
            "\n\n=== REAL EXPLOIT DATA ===\n" + real_exploit_data +
            "\n\n=== REAL VERIFY DATA ===\n" + real_verify_data +
            "\n\n--- RECON SCOUT ANALYSIS ---\n" + recon_llm.findings
        )
        self._log(f"🧠 Phase: Deep Analyst (glm-5.1 — hurtig+stabil)")
        analyst_sr = self._run_agent("analyst", target, full_context)
        all_results.append(analyst_sr)
        
        # Update context with analyst findings
        full_context += "\n\n--- DEEP ANALYST FINDINGS ---\n" + analyst_sr.findings
        
        # PHASES 5-6: verify → reporter
        phases = [
            ("verify", "VERIFY ALL FINDINGS on " + target),
            ("reporter", "WRITE REPORT for " + target),
        ]
        
        for phase_name, phase_desc in phases:
            self._log(f"📎 Phase: {phase_name}")
            sr = self._run_agent(phase_name, target, full_context)
            all_results.append(sr)
            full_context = sr.findings
        
        self.results = all_results
        return self._compile_results()
    
    def _score_quality(self, text: str) -> float:
        """Score output quality based on heuristics."""
        if not text:
            return 0.0
        score = 0.0
        # Length bonus (up to 10 points)
        score += min(len(text) / 500, 10)
        # Finding indicators
        findings = ["CVE", "vuln", "security", "exposed", "misconfig", 
                    "XSS", "SQL", "IDOR", "SSRF", "RCE", "LFI", "CSP",
                    "header", "cookie", "token", "auth", "bypass"]
        for f in findings:
            if f.lower() in text.lower():
                score += 0.5
        # Structure indicators
        structure = ["##", "|", "```", "1.", "2.", "**"]
        for s in structure:
            if s in text:
                score += 0.3
        return round(score, 1)
    
    def _compile_results(self) -> Dict:
        """Compile all agent results into summary and save full findings."""
        compiled = {
            "mode": self.config.mode,
            "agents_used": [r.agent_name for r in self.results],
            "models_used": [r.model for r in self.results],
            "total_duration": sum(r.duration for r in self.results),
            "total_findings_length": sum(len(r.findings) for r in self.results),
            "results": [r.to_dict() for r in self.results],
            "timestamp": datetime.now().isoformat(),
        }
        
        # Save full findings to disk
        try:
            report_dir = Path(self.config.output_dir)
            report_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_safe = self.config.targets[0].replace(".", "_").replace("/", "_") if self.config.targets else "unknown"
            
            # Save each agent's findings
            for r in self.results:
                fname = f"{ts}_{r.agent_name}_{r.model.replace(':', '_')}_{target_safe}.txt"
                (report_dir / fname).write_text(r.findings)
            
            # Save compiled summary
            summary_path = report_dir / f"{ts}_summary_{target_safe}.json"
            summary_path.write_text(json.dumps(compiled, indent=2, ensure_ascii=False))
            self._log(f"💾 Reports saved to {report_dir}")
        except Exception as e:
            self._log(f"⚠️ Could not save reports: {e}")
        
        return compiled


def run_swarm(target: str, mode: str = "pipeline", agents: List[str] = None) -> Dict:
    """Quick-start function for swarm."""
    config = SwarmConfig(mode=mode, agents=agents, targets=[target])
    swarm = AgentSwarm(config)
    
    if mode == "swarm":
        return swarm.run_swarm([target])
    elif mode == "race":
        return swarm.run_race(target)
    elif mode == "pipeline":
        return swarm.run_pipeline(target)
    else:
        return {"error": f"Unknown mode: {mode}"}


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "shopify.com"
    mode = sys.argv[2] if len(sys.argv) > 2 else "pipeline"
    
    print(f"🐝 GROK SWARM — {mode.upper()} mode on {target}")
    result = run_swarm(target, mode)
    print(json.dumps(result, indent=2))
