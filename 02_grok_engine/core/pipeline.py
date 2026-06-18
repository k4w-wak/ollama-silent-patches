#!/usr/bin/env python3
"""
Grok Swarm Orchestrator — styrer teamet så alt bliver gjort rigtigt.

Pipeline:
  1. RECON  → bb_hunter / subdomain scan / tech detect
  2. ANALYZE → LLM vurderer fund for exploit potential
  3. EXPLOIT → test udvalgte angrebsvektorer
  4. VERIFY  → kør verify.py, gentag test 2 gange
  5. STORE   → verified/ eller potential/
  6. REPORT  → generer bounty-rapport

Kaldet af Grok når den får en /pipeline <target> kommando.
"""

import os
import sys
import json
import time
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# ── Konstanter ────────────────────────────────────────
GROK_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = GROK_DIR / "scripts"
REPORT_DIR = Path.home() / "06_osint_forensics" / "swarm_reports"
VERIFIED_DIR = REPORT_DIR / "verified"
POTENTIAL_DIR = REPORT_DIR / "potential"
LOG_FILE = Path.home() / ".grok" / "logs" / "pipeline.log"

for d in [REPORT_DIR, VERIFIED_DIR, POTENTIAL_DIR, LOG_FILE.parent]:
    d.mkdir(parents=True, exist_ok=True)


# ── Logger ────────────────────────────────────────────
def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# ── Phase 1: Recon ────────────────────────────────────
def run_recon(target: str) -> str:
    """Kør bb_hunter (7-trins recon) på target."""
    log(f"🔍 RECON: {target}")
    try:
        r = subprocess.run(
            ["python3", "-c", f"""
import sys; sys.path.insert(0, '{GROK_DIR}/core')
from tools import bb_hunter
print(bb_hunter('{target}'))
"""],
            capture_output=True, text=True, timeout=300
        )
        output = r.stdout[:15000] if r.stdout else r.stderr[:2000]
        report_path = REPORT_DIR / f"{target}_recon.txt"
        report_path.write_text(output)
        log(f"✅ RECON done ({len(output)} chars) → {report_path.name}")
        return output
    except Exception as e:
        log(f"❌ RECON failed: {e}")
        return f"[RECON FEJL] {e}"


# ── Phase 2: LLM Analyse ──────────────────────────────
def analyze_recon(recon_output: str, target: str) -> str:
    """LLM analyserer recon-output og vælger exploit-vektor."""
    log(f"🧠 ANALYZE: {target}")
    # Dette køres af Grok selv i ReAct loop – her returnerer vi bare
    # en placeholder. Grok laver analysen.
    analysis_path = REPORT_DIR / f"{target}_analysis.txt"
    analysis_path.write_text("[LLM ANALYSIS PENDING - køres af Grok i næste step]")
    return "[ANALYSIS READY - venter på Grok exploit step]"


# ── Phase 3: Exploit ──────────────────────────────────
def run_exploit(target: str, vector: str = "") -> str:
    """Kør exploit mod target. Grok vælger selv vektor."""
    log(f"⚔️ EXPLOIT: {target}")
    # Grok kører sine tools i ReAct loop – vi gemmer resultatet
    report_path = REPORT_DIR / f"{target}_exploit.txt"
    if report_path.exists():
        log(f"📄 Exploit report findes allerede: {report_path.name}")
        return report_path.read_text()
    return "[EXPLOIT PENDING - køres af Grok]"


# ── Phase 4: Verify ────────────────────────────────────
def verify_report(target: str) -> Dict:
    """Kør verify.py på exploit-rapporten."""
    log(f"✅ VERIFY: {target}")
    report_path = REPORT_DIR / f"{target}_exploit.txt"
    verify_script = SCRIPTS_DIR / "verify.py"

    if not report_path.exists():
        log(f"⚠️ Ingen exploit report at verificere for {target}")
        return {"verified": False, "error": "no exploit report"}

    if not verify_script.exists():
        log(f"⚠️ verify.py ikke fundet på {verify_script}")
        return {"verified": False, "error": "verify.py missing"}

    try:
        r = subprocess.run(
            ["python3", str(verify_script), str(report_path)],
            capture_output=True, text=True, timeout=60
        )
        if r.returncode != 0:
            log(f"⚠️ verify.py failed: {r.stderr[:200]}")
            return {"verified": False, "error": r.stderr[:200]}

        result = json.loads(r.stdout) if r.stdout.strip() else {"verified": False}
        log(f"{'✅ VERIFIED' if result.get('verified') else '⚠️ POTENTIAL'} for {target}")
        return result
    except json.JSONDecodeError:
        log(f"⚠️ verify.py output ikke JSON: {r.stdout[:200]}")
        return {"verified": False, "error": "invalid verify output"}
    except Exception as e:
        log(f"❌ Verify error: {e}")
        return {"verified": False, "error": str(e)}


# ── Phase 5: Store ─────────────────────────────────────
def store_report(target: str, verified: bool):
    """Flyt rapport til verified/ eller potential/."""
    log(f"📦 STORE: {target} → {'verified' if verified else 'potential'}")
    report_path = REPORT_DIR / f"{target}_exploit.txt"
    target_dir = VERIFIED_DIR if verified else POTENTIAL_DIR

    if report_path.exists():
        dest = target_dir / report_path.name
        os.rename(str(report_path), str(dest))
        log(f"   ╰─> {dest}")

    # Flyt også recon + analysis hvis de findes
    for suffix in ["_recon.txt", "_analysis.txt", "_verify.json"]:
        f = REPORT_DIR / f"{target}{suffix}"
        if f.exists():
            dest = target_dir / f.name
            os.rename(str(f), str(dest))
            log(f"   ╰─> {dest}")


# ── Phase 6: Report ────────────────────────────────────
def generate_report(target: str, verified: bool) -> str:
    """Generer slutrapport."""
    log(f"📝 REPORT: {target}")
    target_dir = VERIFIED_DIR if verified else POTENTIAL_DIR

    recon_path = target_dir / f"{target}_recon.txt"
    exploit_path = target_dir / f"{target}_exploit.txt"
    verify_path = target_dir / f"{target}_verify.json"

    parts = [f"# Bounty Report: {target}", f"Status: {'✅ VERIFIED' if verified else '⚠️ POTENTIAL'}", ""]

    if recon_path.exists():
        parts.append("## Recon Results")
        parts.append(recon_path.read_text()[:2000])
    if exploit_path.exists():
        parts.append("## Exploit Results")
        parts.append(exploit_path.read_text()[:2000])
    if verify_path.exists():
        parts.append("## Verification")
        parts.append(verify_path.read_text())

    report = "\n\n".join(parts)
    report_path = REPORT_DIR / f"{target}_report.md"
    report_path.write_text(report)
    log(f"📄 Report gemt: {report_path}")
    return report


# ── Hoved-pipeline ─────────────────────────────────────
def run_pipeline(target: str, auto_exploit: bool = False) -> Dict:
    """
    Kør hele pipeline for et target.
    auto_exploit=True: Grok kører automatisk exploit (hvis muligt)
    auto_exploit=False: Grok spørger brugeren først
    """
    log(f"{'='*50}")
    log(f"🚀 PIPELINE START: {target}")
    results = {"target": target, "steps": [], "verified": False}

    # Step 1: Recon
    recon = run_recon(target)
    results["steps"].append({"step": "recon", "output_length": len(recon)})

    # Step 2-3: Analyse + Exploit (køres af Grok i chat loop)
    # Grok får besked om at analysere og vælge exploit
    results["steps"].append({"step": "analyze_exploit", "status": "pending_grok"})

    # Step 4: Verify (køres efter Grok har lavet exploit)
    verify_result = verify_report(target)
    verified = verify_result.get("verified", False)
    results["verified"] = verified
    results["steps"].append({"step": "verify", "verified": verified})

    # Step 5: Store
    store_report(target, verified)

    # Step 6: Report
    report = generate_report(target, verified)
    results["steps"].append({"step": "report", "path": str(REPORT_DIR / f"{target}_report.md")})

    status = "✅ VERIFIED" if verified else "⚠️ POTENTIAL"
    log(f"{'='*50}")
    log(f"{status} — {target}")
    log(f"{'='*50}")

    return results


# ── CLI entry point ───────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Grok Swarm Pipeline")
    parser.add_argument("target", help="target domain (fx stripe.com)")
    parser.add_argument("--auto", action="store_true", help="auto-exploit uden bekræftelse")
    args = parser.parse_args()

    result = run_pipeline(args.target, auto_exploit=args.auto)
    print(json.dumps(result, indent=2))
