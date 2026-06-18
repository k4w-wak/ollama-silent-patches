#!/usr/bin/env python3
"""
EvoSwarm EASY — Brugervenlig menu til EvoSwarm v2.2 MAX++

Tryk 1, 2, 3... intet behov for at huske kommandoer.
API-nøgle læses fra .env (sikker).
"""

import os
import sys
import glob
import json
import time
import subprocess
import requests
from typing import List

from dotenv import load_dotenv

load_dotenv()

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "").strip()
if not OLLAMA_API_KEY:
    print("[FEJL] OLLAMA_API_KEY ikke sat. Læg den i .env først.")
    print("Tip: cp .env.example .env")
    sys.exit(1)

SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "evoswarm_v2_max.py")
LOG_DIR = os.path.abspath(os.getenv("LOG_DIR", os.path.join(os.path.dirname(__file__), "evoswarm_logs")))
REPORTS_DIR = os.path.abspath(os.getenv("REPORTS_DIR", os.path.join(os.path.dirname(__file__), "..", "reports")))
os.makedirs(REPORTS_DIR, exist_ok=True)
DEFAULT_ROUNDS = int(os.getenv("DEFAULT_ROUNDS", "5"))


def clear():
    os.system("clear" if os.name != "nt" else "cls")


def header():
    print("\n" + "═" * 60)
    print("     🚀 EvoSwarm v2.2 MAX++ — EASY MENU")
    print("     Cloud-only · Parallel · Self-improving")
    print("═" * 60)


def run_debate():
    topic = input("\n📝 Emne: ").strip()
    if not topic:
        print("[INFO] Ingen emne skrevet — bruger default.")
        topic = "Hvordan bør vi forholde os til sikkerhed i AI-systemer?"

    rounds_input = input(f"🔁 Antal runder (default {DEFAULT_ROUNDS}): ").strip()
    rounds = DEFAULT_ROUNDS
    if rounds_input:
        try:
            rounds = int(rounds_input)
        except ValueError:
            print("[ADVARSEL] Ugyldigt tal — bruger default.")

    print(f"\n▶ Starter debat: '{topic}' med {rounds} runder...")
    subprocess.run([sys.executable, SCRIPT_PATH, topic, str(rounds)], check=False)
    print("\n✅ Debat færdig! Se rapporten ovenfor.")

    webhook_url = os.getenv("WEBHOOK_URL", "").strip()
    if webhook_url:
        print("▶ Sender webhook notifikation...")
        ok = send_webhook(webhook_url, {"event": "debate_finished", "topic": topic, "rounds": rounds})
        print("✅ Webhook sendt" if ok else "⚠️ Webhook fejlede")

    input("\nTryk Enter for at gå tilbage...")


def run_batch():
    print("\nSkriv emner adskilt med Enter. Skriv 'q' når du er færdig.")
    topics = []
    while True:
        t = input(f"  Emne {len(topics) + 1}: ").strip()
        if t.lower() in ("q", "quit", "done"):
            break
        if t:
            topics.append(t)

    if not topics:
        print("[INFO] Ingen emner — afbryder.")
        return

    rounds_input = input(f"🔁 Antal runder per emne (default {DEFAULT_ROUNDS}): ").strip()
    rounds = DEFAULT_ROUNDS
    if rounds_input:
        try:
            rounds = int(rounds_input)
        except ValueError:
            print("[ADVARSEL] Ugyldigt tal — bruger default.")

    topics_str = " | ".join(topics)
    print(f"\n▶ Starter batch med {len(topics)} emner...")
    env = os.environ.copy()
    env["DEBATE_TOPICS"] = topics_str
    subprocess.run([sys.executable, SCRIPT_PATH, "", str(rounds)], env=env, check=False)
    print("\n✅ Batch færdig!")
    input("\nTryk Enter for at gå tilbage...")


def show_agents():
    print("\n🤖 Default agenter:")
    print("  1. Freja Luna — Visionær · glm-5.1:cloud")
    print("  2. Mads Skov — Skeptiker · glm-5.1:cloud")
    print("  3. Viktor Lang — Filosof · kimi-k2.7-code:cloud")
    print("  4. Aisha Khan — Aktivist · minimax-m3:cloud")
    print("  5. Karl Bitter — Cyniker · deepseek-v4-flash:cloud")
    print("\n💡 Brug EVOSWARM_AGENTS i .env for custom agenter.")
    input("\nTryk Enter for at gå tilbage...")


def reset_memory():
    memory_file = os.path.join(LOG_DIR, "evoswarm_memory.json")
    print(f"\n⚠️ Dette sletter al persistent hukommelse.")
    confirm = input("Er du sikker? skriv 'ja' for at bekræfte: ").strip().lower()
    if confirm == "ja":
        try:
            if os.path.exists(memory_file):
                os.remove(memory_file)
                print("✅ Hukommelse slettet.")
            else:
                print("[INFO] Der var ingen hukommelse at slette.")
        except Exception as e:
            print(f"[FEJL] Kunne ikke slette: {e}")
    else:
        print("[INFO] Annulleret.")
    input("\nTryk Enter for at gå tilbage...")


def show_logs():
    logs = sorted(glob.glob(os.path.join(LOG_DIR, "evoswarm_*.md")))
    print(f"\n📄 Rapporter i {LOG_DIR}:")
    if not logs:
        print("  Ingen rapporter endnu.")
    else:
        for i, log in enumerate(logs[-10:], start=1):
            print(f"  {i}. {os.path.basename(log)}")

        print("\n💡 Send en rapport til grok.py for dybere analyse:")
        print(f"  python3 evoswarm_grok_bridge.py {logs[-1]}")
    input("\nTryk Enter for at gå tilbage...")


def send_to_grok():
    logs = sorted(glob.glob(os.path.join(LOG_DIR, "evoswarm_*.md")))
    if not logs:
        print(f"\n[FEJL] Ingen evoswarm rapporter at sende.")
        input("\nTryk Enter for at gå tilbage...")
        return

    print("\n📤 Send rapport til grok.py:")
    for i, log in enumerate(logs[-5:], start=1):
        print(f"  {i}. {os.path.basename(log)}")
    print("  0. Tilbage")

    valg = input("\n  Vælg rapport (0-5): ").strip()
    if valg == "0":
        return
    try:
        idx = int(valg) - 1
        if idx < 0 or idx >= len(logs[-5:]):
            raise ValueError
        report = logs[-5:][idx]
    except ValueError:
        print("[ADVARSEL] Ugyldigt valg.")
        input("\nTryk Enter for at gå tilbage...")
        return

    print("\n🎯 Analyse-type:")
    modes = [
        ("1", "deep_analysis", "Dyb analyse"),
        ("2", "action_items", "Handlingspunkter"),
        ("3", "security_advisory", "Security advisory draft"),
        ("4", "osint_followup", "OSINT follow-up"),
        ("5", "threat_model", "Threat model"),
        ("6", "ioc_extract", "IoC extract"),
        ("7", "patch_diff_review", "Patch diff review"),
        ("8", "media_response", "Medie-svar"),
    ]
    for num, key, label in modes:
        print(f"  {num}. {label}")

    mode_map = {num: key for num, key, _ in modes}
    mode_valg = input("\n  Vælg (1-8): ").strip()
    mode = mode_map.get(mode_valg, "deep_analysis")

    model = input("\n🤖 Model til grok.py (tryk Enter for default): ").strip()
    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "evoswarm_grok_bridge.py"), report, "--mode", mode]
    if model:
        cmd.extend(["--model", model])

    print(f"\n▶ Sender {os.path.basename(report)} til grok.py ({mode})...")
    subprocess.run(cmd, check=False)
    input("\nTryk Enter for at gå tilbage...")


def run_auto_pipeline():
    print("\n🚀 Auto-pipeline: debat → analyse → grok.py")
    topic = input("\n📝 Emne: ").strip()
    if not topic:
        print("[FEJL] Intet emne — afbryder.")
        input("\nTryk Enter for at gå tilbage...")
        return

    rounds_input = input(f"🔁 Antal runder (default {DEFAULT_ROUNDS}): ").strip()
    rounds = DEFAULT_ROUNDS
    if rounds_input:
        try:
            rounds = int(rounds_input)
        except ValueError:
            print("[ADVARSEL] Ugyldigt tal — bruger default.")

    print("\n🎯 Analyse-type:")
    modes = [
        ("1", "deep_analysis", "Dyb analyse"),
        ("2", "action_items", "Handlingspunkter"),
        ("3", "security_advisory", "Security advisory draft"),
        ("4", "osint_followup", "OSINT follow-up"),
        ("5", "threat_model", "Threat model"),
        ("6", "ioc_extract", "IoC extract"),
        ("7", "patch_diff_review", "Patch diff review"),
        ("8", "media_response", "Medie-svar"),
    ]
    for num, key, label in modes:
        print(f"  {num}. {label}")
    mode_valg = input("\n  Vælg (1-8): ").strip()
    mode_map = {num: key for num, key, _ in modes}
    mode = mode_map.get(mode_valg, "deep_analysis")

    model = input("\n🤖 Model til grok.py (tryk Enter for default): ").strip()
    extra = input("\n💬 Ekstra kontekst (tryk Enter for ingen): ").strip()

    cmd = [
        sys.executable,
        os.path.join(os.path.dirname(__file__), "evoswarm_grok_bridge.py"),
        "--pipeline",
        "--topic", topic,
        "--rounds", str(rounds),
        "--mode", mode,
    ]
    if model:
        cmd.extend(["--model", model])
    if extra:
        cmd.extend(["--extra", extra])

    print(f"\n▶ Starter auto-pipeline...")
    subprocess.run(cmd, check=False)
    input("\nTryk Enter for at gå tilbage...")


def send_to_grok():
    logs = sorted(glob.glob(os.path.join(LOG_DIR, "evoswarm_*.md")))
    if not logs:
        print(f"\n[FEJL] Ingen evoswarm rapporter at sende.")
        input("\nTryk Enter for at gå tilbage...")
        return

    print("\n📤 Send rapport til grok.py:")
    for i, log in enumerate(logs[-5:], start=1):
        print(f"  {i}. {os.path.basename(log)}")
    print("  0. Tilbage")

    valg = input("\n  Vælg rapport (0-5): ").strip()
    if valg == "0":
        return
    try:
        idx = int(valg) - 1
        if idx < 0 or idx >= len(logs[-5:]):
            raise ValueError
        report = logs[-5:][idx]
    except ValueError:
        print("[ADVARSEL] Ugyldigt valg.")
        input("\nTryk Enter for at gå tilbage...")
        return

    print("\n🎯 Analyse-type:")
    print("  1. Dyb analyse")
    print("  2. Handlingspunkter")
    print("  3. Security advisory draft")
    print("  4. OSINT follow-up")
    mode_map = {"1": "deep_analysis", "2": "action_items", "3": "security_advisory", "4": "osint_followup"}
    mode_valg = input("\n  Vælg (1-4): ").strip()
    mode = mode_map.get(mode_valg, "deep_analysis")

    model = input("\n🤖 Model til grok.py (tryk Enter for default): ").strip()
    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "evoswarm_grok_bridge.py"), report, "--mode", mode]
    if model:
        cmd.extend(["--model", model])

    print(f"\n▶ Sender {os.path.basename(report)} til grok.py ({mode})...")
    subprocess.run(cmd, check=False)
    input("\nTryk Enter for at gå tilbage...")


def show_env_status():
    print("\n🔧 Miljøvariabler (nøgle skjult):")
    print(f"  MAX_WORKERS: {os.getenv('MAX_WORKERS', '8')}")
    print(f"  RATE_LIMIT_QPS: {os.getenv('RATE_LIMIT_QPS', '5.0')}")
    print(f"  DEFAULT_ROUNDS: {os.getenv('DEFAULT_ROUNDS', str(DEFAULT_ROUNDS))}")
    print(f"  STREAMING: {os.getenv('STREAMING', 'false')}")
    print(f"  FALLBACK_MODEL: {os.getenv('FALLBACK_MODEL', 'glm-5.1:cloud')}")
    print(f"  CIRCUIT_THRESHOLD: {os.getenv('CIRCUIT_THRESHOLD', '3')}")
    print(f"  WEBHOOK_URL: {os.getenv('WEBHOOK_URL', '(ikke sat)')}")
    key_status = "sat" if OLLAMA_API_KEY else "mangler"
    print(f"  OLLAMA_API_KEY: {key_status}")
    input("\nTryk Enter for at gå tilbage...")


def send_webhook(url: str, payload: dict):
    """Send webhook notification."""
    try:
        import requests
        r = requests.post(url, json=payload, timeout=15)
        return r.status_code < 400
    except Exception as e:
        print(f"[Webhook fejl] {e}")
        return False


def test_webhook():
    webhook_url = os.getenv("WEBHOOK_URL", "").strip()
    if not webhook_url:
        print("\n[FEJL] WEBHOOK_URL ikke sat i .env")
        print("Sæt den først, f.eks. WEBHOOK_URL=https://dinside.dk/evoswarm")
        input("\nTryk Enter for at gå tilbage...")
        return

    print(f"\n▶ Sender test-webhook til {webhook_url}...")
    try:
        r = requests.post(
            webhook_url,
            json={"event": "test", "message": "EvoSwarm webhook test", "timestamp": time.time()},
            timeout=15,
        )
        if r.status_code < 400:
            print(f"✅ Webhook OK — status {r.status_code}")
        else:
            print(f"⚠️ Webhook fejlede — status {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"[FEJL] Kunne ikke sende webhook: {e}")
    input("\nTryk Enter for at gå tilbage...")


def model_compare():
    print("\n🏁 Auto-model sammenligning")
    print("Kører det samme spørgsmål på flere modeller og sammenligner hastighed/cost.")
    topic = input("\n📝 Spørgsmål: ").strip()
    if not topic:
        topic = "Hvad er den største risiko ved AI?"

    models = ["glm-5.1:cloud", "kimi-k2.7-code:cloud", "minimax-m3:cloud", "deepseek-v4-flash:cloud"]
    results = []

    for model in models:
        print(f"\n▶ Tester {model}...")
        start = time.time()
        try:
            # brug samme API-logik som hoved-scriptet via subprocess call
            env = os.environ.copy()
            env["DEBATE_TOPIC"] = topic
            env["EVOSWARM_AGENTS"] = json.dumps([
                {"name": "Tester", "role": "Ekspert", "belief": "Jeg svarer præcist.", "model": model}
            ])
            subprocess.run(
                [sys.executable, SCRIPT_PATH, topic, "1"],
                env=env,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            elapsed = time.time() - start
            results.append({"model": model, "elapsed": elapsed, "status": "OK"})
            print(f"   ✅ {model}: {elapsed:.2f}s")
        except Exception as e:
            results.append({"model": model, "elapsed": 0, "status": f"FEJL: {e}"})
            print(f"   ❌ {model}: {e}")

    if results:
        fastest = min(results, key=lambda x: x["elapsed"] if x["status"] == "OK" else float("inf"))
        print("\n📊 Resultater:")
        for r in results:
            print(f"  {r['model']}: {r['elapsed']:.2f}s — {r['status']}")
        print(f"\n🏆 Hurtigste model: {fastest['model']} ({fastest['elapsed']:.2f}s)")
        print("💡 Bemærk: Svar-kvalitet ikke vurderet her — kun hastighed.")
    input("\nTryk Enter for at gå tilbage...")


def security_debate():
    """Kør en sikkerheds-panel debat med security-fokuserede agenter."""
    print("\n🛡️ Sikkerhedspanel — vælg et emne:")
    topics = [
        "CVE-2024-37032 (Probllama): Hvor alvorlig er path traversal i Ollama?",
        "Ollama's silent patching problem: 9+ CVE'er uden advisories — er det acceptabelt?",
        "300.000+ exposed Ollama instances: Hvem har ansvaret?",
        "AI model supply chain attacks: Hvordan beskytter vi mod malicious GGUF/models?",
        "Windows auto-update RCE i Ollama: Hvad skal brugere gøre NU?",
        "MCP Server Command Injection i AI-systemer: Et nyt RCE-landskab?",
        "Bør Ollama have mandatory authentication og TLS by default?",
    ]
    for i, t in enumerate(topics, start=1):
        print(f"  {i}. {t}")
    print("  0. Tilbage")
    print("\n  99. Skriv dit eget CVE/emne")

    valg = input("\n  Vælg (0-7 eller 99): ").strip()
    if valg == "0":
        return

    if valg == "99":
        topic = input("\n📝 Skriv CVE/emne: ").strip()
        if not topic:
            print("[ADVARSEL] Intet emne — afbryder.")
            input("\nTryk Enter for at gå tilbage...")
            return
    else:
        try:
            idx = int(valg) - 1
            if idx < 0 or idx >= len(topics):
                raise ValueError
            topic = topics[idx]
        except ValueError:
            print("[ADVARSEL] Ugyldigt valg.")
            input("\nTryk Enter for at gå tilbage...")
            return

    rounds_input = input(f"🔁 Antal runder (default {DEFAULT_ROUNDS}): ").strip()
    rounds = DEFAULT_ROUNDS
    if rounds_input:
        try:
            rounds = int(rounds_input)
        except ValueError:
            print("[ADVARSEL] Ugyldigt tal — bruger default.")

    # Security panel: specialicerede agenter
    env = os.environ.copy()
    env["EVOSWARM_AGENTS"] = json.dumps([
        {"name": "CVE-Hunter", "role": "Sårbarhedsanalytiker", "belief": "Alle patches uden advisories er en potentiel supply-chain risiko.", "model": "glm-5.1:cloud"},
        {"name": "NetSec-Ops", "role": "Network defender", "belief": "Exposed services er en konfigurationsfejl, ikke kun en produktsårbarhed.", "model": "glm-5.1:cloud"},
        {"name": "Threat-Intel", "role": "Trusselsovervåger", "belief": "300.000 exposed instances betyder at angribere allerede scanner dem.", "model": "kimi-k2.7-code:cloud"},
        {"name": "Responsible-Disclosure", "role": "Etisk hacker", "belief": "Vendor uresponsiveness tvinger forskere til at gå public — det skader økosystemet.", "model": "minimax-m3:cloud"},
        {"name": "CISO-Pragmatiker", "role": "Sikkerhedschef", "belief": "Mitigations først: bind til localhost, reverse proxy, auth, verify models.", "model": "deepseek-v4-flash:cloud"},
    ])

    print(f"\n▶ Starter sikkerheds-debat: '{topic}'...")
    subprocess.run([sys.executable, SCRIPT_PATH, topic, str(rounds)], env=env, check=False)
    input("\nTryk Enter for at gå tilbage...")


def quick_debate():
    """Kør med foruddefinerede hot topics — vælg med tal."""
    topics = [
        "Hvordan bør vi regulere AI i 2026?",
        "Er cloud-baserede AI-modeller sikre nok til følsomme data?",
        "Hvilken rolle skal hackere og bug bounty-spillere have i AI-sikkerhed?",
        "Bør offentlige myndigheder bruge open-source eller proprietary AI?",
        "Hvordan undgår vi at AI bliver et våben i cyberkrig?",
    ]
    print("\n🔥 Hurtige emner:")
    for i, t in enumerate(topics, start=1):
        print(f"  {i}. {t}")
    print("  0. Tilbage")

    valg = input("\n  Vælg emne (0-5): ").strip()
    if valg == "0":
        return
    try:
        idx = int(valg) - 1
        if idx < 0 or idx >= len(topics):
            print("[ADVARSEL] Ugyldigt valg.")
            input("\nTryk Enter for at gå tilbage...")
            return
    except ValueError:
        print("[ADVARSEL] Skriv et tal.")
        input("\nTryk Enter for at gå tilbage...")
        return

    topic = topics[idx]
    rounds_input = input(f"🔁 Antal runder (default {DEFAULT_ROUNDS}): ").strip()
    rounds = DEFAULT_ROUNDS
    if rounds_input:
        try:
            rounds = int(rounds_input)
        except ValueError:
            print("[ADVARSEL] Ugyldigt tal — bruger default.")

    print(f"\n▶ Starter hurtig-debat: '{topic}'...")
    subprocess.run([sys.executable, SCRIPT_PATH, topic, str(rounds)], check=False)
    input("\nTryk Enter for at gå tilbage...")


def analyze_osint_report():
    """Læs en OSINT-rapport og få agenterne til at analysere + generere advisory draft."""
    print("\n📄 OSINT Rapport Analyse")
    print("Skriv stien til en .md/.txt rapport, eller klistre tekst ind direkte.")
    print("Eksempel: /home/admin_user/workspace_codex/reports/OLLAMA_VULNERABILITY_LANDSCAPE_OSINT_2026-01-13.md")

    raw = input("\nSti eller tekst (max ~8000 tegn): ").strip()
    if not raw:
        print("[INFO] Intet input — afbryder.")
        input("\nTryk Enter for at gå tilbage...")
        return

    content = ""
    if os.path.isfile(raw):
        try:
            with open(raw, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            print(f"✅ Læste {len(content)} tegn fra fil.")
        except Exception as e:
            print(f"[FEJL] Kunne ikke læse fil: {e}")
            input("\nTryk Enter for at gå tilbage...")
            return
    else:
        content = raw
        print(f"✅ Bruger indklistret tekst ({len(content)} tegn).")

    # Truncate hvis for lang
    if len(content) > 12000:
        content = content[:12000] + "\n\n[TRUNCATED]"
        print("[ADVARSEL] Tekst trunkeret til 12000 tegn.")

    task = input("\n🎯 Opgaver: [1] Risikoanalyse  [2] Mitigations  [3] Advisory draft  [4] Alt: ").strip()
    if task not in ("1", "2", "3", "4"):
        task = "4"

    task_prompts = {
        "1": "Udfør en risikoanalyse. Identificér de 5 vigtigste trusler og scorer dem CVSS-lignende (1-10).",
        "2": "Udarbejd konkrete mitigations for systemadministratorer, udviklere og sikkerhedsteams.",
        "3": "Skriv et professionelt security advisory draft med summary, affected versions, impact og remediation.",
        "4": "Udfør risikoanalyse, mitigations OG et advisory draft. Strukturér output tydeligt.",
    }

    prompt = f"""Du er en ekspert i AI-sikkerhed og OSINT-analyse.

ANALYSÉR FØLGENDE RAPPORT:

---
{content}
---

{task_prompts[task]}

Skriv på dansk eller engelsk efter behov. Vær præcis og handlingsorienteret."""

    print("\n▶ Sender rapport til cloud-model for analyse...")
    models = ["kimi-k2.7-code:cloud", "glm-5.1:cloud", "deepseek-v4-flash:cloud"]
    analyses = {}
    for model in models:
        try:
            r = requests.post(
                os.getenv("OLLAMA_URL", "https://ollama.com/v1/chat/completions"),
                headers={
                    "Authorization": f"Bearer {OLLAMA_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "Du er en senior sikkerhedsanalytiker."},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 2000,
                    "temperature": 0.7,
                },
                timeout=120,
            )
            if r.status_code == 200:
                analyses[model] = r.json()["choices"][0]["message"]["content"].strip()
                print(f"  ✅ {model}: OK")
            else:
                analyses[model] = f"[FEJL {r.status_code}]"
                print(f"  ❌ {model}: HTTP {r.status_code}")
        except Exception as e:
            analyses[model] = f"[FEJL: {e}]"
            print(f"  ❌ {model}: {e}")

    # Gem rapport
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_file = os.path.join(REPORTS_DIR, f"evoswarm_osint_analysis_{ts}.md")
    lines = [f"# EvoSwarm OSINT Analyse — {ts}", f"\n**Input:** `{raw[:80]}`", f"\n**Opgave:** {task_prompts[task]}\n"]
    for model, analysis in analyses.items():
        lines.extend([f"## {model}", "", analysis, ""])

    try:
        with open(out_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n💾 Gemt analyse i: {out_file}")
    except Exception as e:
        print(f"[FEJL] Kunne ikke gemme: {e}")

    webhook_url = os.getenv("WEBHOOK_URL", "").strip()
    if webhook_url:
        send_webhook(webhook_url, {"event": "osint_analysis_complete", "file": out_file, "models": list(analyses.keys())})

    input("\nTryk Enter for at gå tilbage...")


def main():
    while True:
        clear()
        header()
        print("\n  Hvad vil du gøre?")
        print("  ─────────────────────────")
        print("  1️⃣  Kør én debat")
        print("  2️⃣  Kør hurtig debat (hot topics)")
        print("  3️⃣  🛡️ Sikkerhedspanel (CVE/OSINT)")
        print("  4️⃣  Kør flere debatter (batch mode)")
        print("  5️⃣  Vis agenter")
        print("  6️⃣  Nulstil hukommelse")
        print("  7️⃣  Vis seneste rapporter")
        print("  8️⃣  Vis indstillinger")
        print("  9️⃣  Test webhook")
        print("  🔟  Auto-model sammenligning")
        print("  📝  OSINT rapport analyse")
        print("  🤖  Send rapport til grok.py")
        print("  ⚡  Auto-pipeline (debat → grok)")
        print("  0️⃣  Afslut")
        print("  ─────────────────────────")

        valg = input("\n  Vælg (0-13): ").strip()

        if valg == "1":
            run_debate()
        elif valg == "2":
            quick_debate()
        elif valg == "3":
            security_debate()
        elif valg == "4":
            run_batch()
        elif valg == "5":
            show_agents()
        elif valg == "6":
            reset_memory()
        elif valg == "7":
            show_logs()
        elif valg == "8":
            show_env_status()
        elif valg == "9":
            test_webhook()
        elif valg == "10":
            model_compare()
        elif valg == "11":
            analyze_osint_report()
        elif valg == "12":
            send_to_grok()
        elif valg == "13":
            run_auto_pipeline()
        elif valg == "0":
            print("\n👋 Farvel!")
            break
        else:
            print("\n[ADVARSEL] Vælg et tal mellem 0 og 13.")
            time.sleep(1)


if __name__ == "__main__":
    main()
