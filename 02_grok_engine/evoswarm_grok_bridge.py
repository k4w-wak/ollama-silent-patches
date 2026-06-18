#!/usr/bin/env python3
"""
EvoSwarm → Grok Bridge

Tager en EvoSwarm debat-rapport (.md) og sender den som en batch mission
til grok.py for dybere analyse, follow-up eller handling.

Brug:
  python3 evoswarm_grok_bridge.py <rapport.md> [--model <ollama:model>]
"""

import os
import sys
import glob
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

_GROK_DIR = Path(__file__).parent.resolve()
_GROK_PY = _GROK_DIR / "grok.py"
_LOG_DIR = _GROK_DIR / "evoswarm_logs"

from dotenv import load_dotenv
load_dotenv()
DEFAULT_ROUNDS = int(os.getenv("DEFAULT_ROUNDS", "5"))


def find_latest_report(log_dir: Path = _LOG_DIR) -> str:
    reports = sorted(glob.glob(str(log_dir / "evoswarm_*.md")))
    if not reports:
        print(f"[FEJL] Ingen evoswarm rapporter fundet i {log_dir}")
        sys.exit(1)
    return reports[-1]


def load_report(report_path: str) -> str:
    try:
        with open(report_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f"[FEJL] Kunne ikke læse rapport: {e}")
        sys.exit(1)


def truncate_report(text: str, max_len: int = 12000) -> str:
    if len(text) > max_len:
        return text[:max_len] + "\n\n[TRUNCATED — resten af rapporten udeladt af token-budget]"
    return text


def build_mission(report_path: str, mode: str = "deep_analysis", extra_context: str = "") -> str:
    report_text = truncate_report(load_report(report_path))

    prompts = {
        "deep_analysis": (
            "Du er en senior AI-sikkerhedsanalytiker. Du har modtaget en rapport fra EvoSwarm "
            "(en parallel multi-agent debat om et sikkerhedsemne). \n\n"
            "OPGAVE:\n"
            "1. Identificér de 3 vigtigste indsigter fra panelets diskussion.\n"
            "2. Find 2 svagheder eller blind spots i argumentationen.\n"
            "3. Angiv 1 konkret follow-up research-opgave med metode og kilde-forslag.\n"
            "4. Konkluder med en 'syntetisk vurdering' på max 3 sætninger.\n\n"
            "FORMAT: Markdown med overskrifter. Vær kritisk, balanceret og præcis."
        ),
        "action_items": (
            "Du er en CISO der skal omdanne en EvoSwarm debatrapport til handling. \n\n"
            "OPGAVE:\n"
            "For hvert centralt problem i rapporten, skriv et handlingspunkt med:\n"
            "- Handling (hvad skal gøres, max 1 sætning)\n"
            "- Ansvarlig rolle (f.eks. CISO, DevOps, Threat Intel, Vendor)\n"
            "- Prioritet (Høj / Medium / Lav)\n"
            "- Næste skridt (konkret, målbart)\n"
            "- Afhængigheder (hvis relevant)\n\n"
            "Afslut med en 'top 3 hurtig gevinster' liste."
        ),
        "security_advisory": (
            "Du er ansvarlig for at udarbejde et security advisory baseret på en EvoSwarm debat. "
            "Rapporten behandler typisk CVE'er, exposed infrastructure, supply chain eller silent patching. \n\n"
            "OPGAVE: Skriv et advisory draft med følgende sektioner:\n"
            "- Executive Summary (max 5 sætninger)\n"
            "- Affected Systems / Versions\n"
            "- Risk Assessment (CVSS-lignende score med begrundelse)\n"
            "- Technical Details (kort)\n"
            "- Mitigations & Workarounds\n"
            "- Detection & Hunting Tips\n"
            "- Timeline forhandlinger / Vendor Response (hvis kendt)\n"
            "- References\n\n"
            "Skriv i professionel sikkerhedstekststil."
        ),
        "osint_followup": (
            "Du er en OSINT-analytiker. Du har fået en debatrapport om en sårbarhed eller et produkt. "
            "Din opgave er at finde huller i research og foreslå næste skridt. \n\n"
            "OPGAVE:\n"
            "1. Liste: Hvilke fakta i rapporten har svageste kildegrundlag?\n"
            "2. For hver indsigt: vurder reliability (A = bekræftet, B = sandsynlig, C = spekulativ).\n"
            "3. Foreslå konkrete yderligere kilder: Shodan queries, Censys, GitHub commits, DNS records, vendor advisories, researcher blogs.\n"
            "4. Foreslå 3 specifikke søgestrenge / dork-forespørgsler.\n"
            "5. Angiv hvad der ville ændre din vurdering markant."
        ),
        "threat_model": (
            "Du er en threat modeler. Givet en EvoSwarm debat om en teknologi/sårbarhed, "
            "opbyg et simpelt threat model. \n\n"
            "OPGAVE:\n"
            "1. Asset: Hvad beskytter vi?\n"
            "2. Threat Actors: Hvem angriber, og hvad er deres motivation/capability?\n"
            "3. Attack Vectors: mindst 5 veje ind i systemet.\n"
            "4. Kill Chain: beskriv trin-for-trin angreb.\n"
            "5. Controls: eksisterende og foreslåede mitigations.\n"
            "6. Risk Table: Threat | Likelihood | Impact | Risk | Priority."
        ),
        "ioc_extract": (
            "Du er en DFIR-analytiker. Gennemgå EvoSwarm rapporten og identificér alle potentielle IoC'er "
            "og observables — direkte eller implicitte. \n\n"
            "OPGAVE:\n"
            "1. IP-adresser, domæner, URLs, filnavne, hashes, CVE-ID'er, porte, processer.\n"
            "2. For hver IoC: angiv type, kontekst, og confidence (Høj/Medium/Lav).\n"
            "3. Output som markdown liste og som JSON blok.\n"
            "4. Bemærkninger om false positives."
        ),
        "patch_diff_review": (
            "Du er en reverse engineer / patch analyst. Du skal vurdere hvad der kan udledes "
            "om en sårbarhed ud fra en hypotetisk patch diff (beskrevet i debatten). \n\n"
            "OPGAVE:\n"
            "1. Hvilke funktioner / filer er sandsynligvis ændret?\n"
            "2. Hvad er root cause?\n"
            "3. Er patchen tilstrækkelig? Find bypass-muligheder.\n"
            "4. Angiv diff-forespørgsler / commits / PR'er der er værd at undersøge.\n"
            "5. Konkluder med 'patched adequately / insufficient / needs monitoring'."
        ),
        "media_response": (
            "Du er en kommunikationsrådgiver for et security research team. "
            "Du skal forberede svar på potentielle medie-/Twitter-spørgsmål om emnet. \n\n"
            "OPGAVE:\n"
            "1. 5 hårde spørgsmål journalister kunne stille.\n"
            "2. Et kort, balanceret svar til hvert spørgsmål.\n"
            "3. 3 nøglebudskaber vi vil have frem.\n"
            "4. 1 sætning der ALDRIG må siges offentligt.\n"
            "5. LinkedIn/Twitter tråd udkast (max 5 posts)."
        ),
    }

    chosen = prompts.get(mode, prompts["deep_analysis"])

    extra = ""
    if extra_context:
        extra = f"\n\nEKSTRA KONTEKST FRA BRUGER:\n{extra_context}\n"

    mission = f"""{chosen}{extra}

=== EVOSWARM RAPPORT ===
{report_text}
=== SLUT RAPPORT ===

Husk: præcist, handlingsorienteret, professionelt."""

    return mission


def run_grok(mission: str, model: str = None) -> int:
    if not _GROK_PY.exists():
        print(f"[FEJL] grok.py ikke fundet på {_GROK_PY}")
        return 1

    env = os.environ.copy()
    env["EVOSWARM_BRIDGE_MODE"] = "1"

    cmd = [sys.executable, str(_GROK_PY), "--batch", mission]
    if model:
        cmd.extend(["--model", model])

    print(f"\n▶ Sender mission til grok.py...")
    print(f"   Model: {model or 'default'}")
    print(f"   Rapport: {args.report}")
    print(f"   Mode: {args.mode}\n")

    result = subprocess.run(cmd, cwd=str(_GROK_DIR), env=env, check=False)
    return result.returncode


def run_pipeline(topic: str, rounds: int, mode: str, model: str = None, auto_send: bool = True, extra_context: str = "") -> int:
    """Auto-pipeline: debat -> analyse -> grok follow-up."""
    print("\n" + "═" * 70)
    print("🚀 EVOSWARM AUTO-PIPELINE")
    print("   Trin 1: Kør debat")
    print("   Trin 2: Analysér rapport")
    print("   Trin 3: Send til grok.py")
    print("═" * 70 + "\n")

    # 1. Kør debat
    debat_cmd = [sys.executable, str(_GROK_DIR / "evoswarm_v2_max.py"), topic, str(rounds)]
    print(f"▶ Trin 1: Kører debat '{topic}' ({rounds} runder)...")
    rc = subprocess.run(debat_cmd, cwd=str(_GROK_DIR), env=os.environ.copy(), check=False).returncode
    if rc != 0:
        print(f"[FEJL] Debatafslutning med kode {rc}")
        return rc

    # 2. Find nyeste rapport
    report_path = find_latest_report()
    print(f"\n✅ Trin 2: Rapport klar: {report_path}")

    # 3. Send til grok
    if auto_send:
        print(f"▶ Trin 3: Sender rapport til grok.py mode={mode}...")
        mission = build_mission(report_path, mode, extra_context)
        rc = run_grok(mission, model)
    else:
        print(f"\n💡 Pipeline stoppede før grok. Brug:")
        print(f"   python3 evoswarm_grok_bridge.py {report_path} --mode {mode}")

    return rc


def main():
    all_modes = [
        "deep_analysis", "action_items", "security_advisory", "osint_followup",
        "threat_model", "ioc_extract", "patch_diff_review", "media_response",
    ]

    parser = argparse.ArgumentParser(description="EvoSwarm → Grok Bridge")
    parser.add_argument("report", nargs="?", help="Sti til EvoSwarm .md rapport")
    parser.add_argument("--mode", choices=all_modes, default="deep_analysis",
                        help="Hvilken type opfølgning")
    parser.add_argument("--model", help="Model at bruge i grok.py, f.eks. ollama:kimi-k2.7-code")
    parser.add_argument("--extra", help="Ekstra kontekst der tilføjes missionen")
    parser.add_argument("--pipeline", action="store_true",
                        help="Kør auto-pipeline: debat -> analyse -> grok")
    parser.add_argument("--topic", help="Emne til auto-pipeline")
    parser.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS,
                        help="Antal runder i auto-pipeline")
    global args
    args = parser.parse_args()

    if args.pipeline or args.topic:
        topic = args.topic or input("📝 Emne til auto-pipeline: ").strip()
        if not topic:
            print("[FEJL] Intet emne — afbryder.")
            sys.exit(1)
        rc = run_pipeline(topic, args.rounds, args.mode, args.model,
                          extra_context=args.extra or "")
        if rc == 0:
            print("\n✅ Auto-pipeline færdig.")
        else:
            print(f"\n⚠️ Pipeline afsluttede med kode {rc}")
        return rc

    report_path = args.report or find_latest_report()
    if not os.path.isfile(report_path):
        print(f"[FEJL] Fil ikke fundet: {report_path}")
        sys.exit(1)

    mission = build_mission(report_path, args.mode, extra_context=args.extra or "")
    rc = run_grok(mission, args.model)
    if rc == 0:
        print("\n✅ EvoSwarm → Grok bridge færdig.")
    else:
        print(f"\n⚠️ grok.py afsluttede med kode {rc}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
