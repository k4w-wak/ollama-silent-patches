#!/usr/bin/env python3
"""
GROK MISSION CONTROL — Interaktiv menu-drevet interface
Kør: python3 grok_mc.py
     python3 grok_mc.py --model kimi-k2.6:cloud
"""

import sys, os, time, json
from datetime import datetime

GROK_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, GROK_DIR)
sys.path.insert(0, os.path.join(GROK_DIR, 'core'))
os.chdir(GROK_DIR)

from core.agent import GrokAgent, Colors

C = Colors
BOLD = '\033[1m'
DIM = '\033[2m'
END = '\033[0m'

def clear():
    os.system('clear')

LOGO = f"""
{C.RED}╔══════════════════════════════════════════╗
║     {C.YELLOW}GROK MISSION CONTROL{C.RED}                ║
║     {C.CYAN}336 tools • ubegraenset• MAX POWER{C.RED}    ║
╚══════════════════════════════════════════╝{END}
"""

def show_main_menu(model_display, turn_count, uptime):
    print(LOGO)
    print(f"  {C.GREEN}Model:{END} {BOLD}{model_display}{END}  {C.GREEN}Turns:{END} {turn_count}  {C.GREEN}Uptime:{END} {uptime}")
    print()
    print(f"  {BOLD}{C.YELLOW}── JAGT ──────────────────────────{END}")
    print(f"  {C.GREEN}[1]{END} Scan target (recon)              {C.GREEN}[2]{END} Exploit target")
    print(f"  {C.GREEN}[3]{END} Full auto-mission               {C.GREEN}[4]{END} Bug bounty mode")
    print(f"  {C.GREEN}[5]{END} Kali tool søgning              {C.GREEN}[6]{END} GitHub tool søgning")
    print()
    print(f"  {BOLD}{C.YELLOW}── OSINT ─────────────────────────{END}")
    print(f"  {C.GREEN}[7]{END} IP opslag                        {C.GREEN}[8]{END} Domain recon")
    print(f"  {C.GREEN}[9]{END} Harvest target data              {C.GREEN}[10]{END} DNS enumeration")
    print()
    print(f"  {BOLD}{C.YELLOW}── SCAN ─────────────────────────{END}")
    print(f"  {C.GREEN}[11]{END} Nmap scan                       {C.GREEN}[12]{END} Vuln scan")
    print(f"  {C.GREEN}[13]{END} Dir scan                        {C.GREEN}[14]{END} SQL injection test")
    print(f"  {C.GREEN}[15]{END} Playbook v2 — bug bounty jagt")
    print()
    print(f"  {BOLD}{C.YELLOW}── SYSTEM ────────────────────────{END}")
    print(f"  {C.GREEN}[m]{END} Skift model                      {C.GREEN}[s]{END} Status")
    print(f"  {C.GREEN}[h]{END} Chat history                     {C.GREEN}[t]{END} Tools liste")
    print(f"  {C.GREEN}[k]{END} Kali service/update             {C.GREEN}[f]{END} Fakta/opsætning")
    print(f"  {C.GREEN}[c]{END} Ryd skærm                        {C.GREEN}[q]{END} Afslut")
    print()
    print(f"  {BOLD}{C.YELLOW}── ELLER bare skriv direkte ──────{END}")
    print(f"  {C.DIM}Skriv hvad som helst for at chatte med Grok{END}")
    print(f"  {C.DIM}Start med / for avancerede commands{END}")

MISSIONS = {
    "1": ("recon", "Scan target — fuld recon (nmap + dns + osint).\n  Target: "),
    "2": ("exploit", "Exploit target — prøv kendte sårbarheder.\n  Target: "),
    "3": ("auto", "Full auto-mission — Grok vælger selv tilgang.\n  Beskriv mission: "),
    "4": ("bounty", "Bug bounty mode — systematisk jagt efter bounties.\n  Scope/target: "),
    "5": ("kali_search", "Søg kali.org efter nye tools og installer dem.\n  Søgeord (eller Enter for alle): "),
    "6": ("github_search", "Søg GitHub efter nye security/bounty tools.\n  Søgeord (eller Enter for trending): "),
    "7": ("ip", "IP opslag — OSINT på IP adresse.\n  IP: "),
    "8": ("domain", "Domain recon — fuld undersøgelse af domæne.\n  Domæne: "),
    "9": ("harvest", "Harvest target data — saml alt tilgængeligt data.\n  Target: "),
    "10": ("dns", "DNS enumeration — fuld DNS kortlægning.\n  Domæne: "),
    "11": ("nmap", "Nmap scan — port scan.\n  Target: "),
    "12": ("vuln", "Vuln scan — sårbarhedsscanning.\n  Target: "),
    "13": ("dirscan", "Directory scan — find skjulte stier.\n  URL: "),
    "14": ("sqli", "SQL injection test.\n  Target URL: "),
    "15": ("playbook", "Kør Playbook v2 — fuld bug bounty jagt med TEAM_PLAYBOOK_v2.md.\n  Vælg spor (1=store payouts, 2=bevis, 3=triangulering, Enter=alle): "),
    "k": ("kali_service", "Kali service — opdater alle tools + installer manglende."),
}

def build_mission_prompt(mission_type, user_input):
    """Byg en proper mission prompt baseret på type og input"""
    templates = {
        "recon": f"Udfør fuld recon på target: {user_input}. Brug nmap, dns_enum, osint_ip, osint_domain, osint_harvest. Rapporter alle fund.",
        "exploit": f"Prøv at exploit target: {user_input}. Brug web_vuln_scan, sql_injection, dir_scan, nmap_scan. Find sårbarheder og verifier dem.",
        "auto": f"Udfør autonom mission: {user_input}. Vælg selv de bedste tools og tilgang. Rapporter alt du finder.",
        "bounty": f"Bug bounty jagt på scope: {user_input}. Systematisk recon → scan → exploit → document. Følg responsible disclosure. Find severity issues.",
        "kali_search": f"Søg efter nye security tools på kali.org. {'Specifikt: ' + user_input if user_input else 'Find alle nye/opdaterede tools.'} Installer dem der mangler.",
        "github_search": f"Søg GitHub efter nye security/bounty tools. {'Specifikt: ' + user_input if user_input else 'Find trending security repos.'} Klon og installer de bedste.",
        "ip": f"Udfør fuld OSINT opslag på IP: {user_input}. Brug osint_ip og alle tilgængelige kilder. Rapporter lokation, ISP, historik, reputation.",
        "domain": f"Udfør fuld domain recon på: {user_input}. Brug osint_domain, dns_enum, osint_harvest. Kortlæg subdomains, IPs, teknologi, mail.",
        "harvest": f"Harvest alt tilgængeligt data på target: {user_input}. Brug osint_harvest + alle data-kilder. Saml emails, subdomains, mediarbejdere, teknologi.",
        "dns": f"Udfør fuld DNS enumeration på: {user_input}. Brug dns_enum. Find alle records, subdomains, MX, TXT, historik.",
        "nmap": f"Udfør nmap scan på: {user_input}. Brug nmap_scan. Scan alle porte, detect OS og services.",
        "vuln": f"Udfør sårbarhedsscan på: {user_input}. Brug web_vuln_scan, nmap_scan med scripts. Find CVEs og misconfigurations.",
        "dirscan": f"Udfør directory scan på: {user_input}. Brug dir_scan. Find skjulte stier, admin panels, backups.",
        "sqli": f"Test for SQL injection på: {user_input}. Brug sql_injection. Verifier og demonstrer sårbarheden.",
        "kali_service": "Kali full service: kør apt update && apt upgrade, tjek alle installerede tools for updates, installer nuclei + subfinder + manglende Go tools, opdater nuclei templates. Rapportér status.",
    }
    if mission_type == "playbook":
        return _build_playbook_prompt(user_input)
    return templates.get(mission_type, user_input)

def _build_playbook_prompt(spor_choice):
    PLAYBOOK_PATH = os.path.expanduser("~/01_missions_og_rapporter/TEAM_PLAYBOOK_v2.md")
    try:
        with open(PLAYBOOK_PATH) as f:
            playbook = f.read()
    except:
        playbook = "PLAYBOOK IKKE FUNDET — fortsæt med standard bug bounty metode."

    spor_map = {
        "1": "Spor 1 — Store Payouts: Fokuser på Tier 1 targets med høj bounty potential. Brug playbookens prioriteringsmatrix og 3-spors strategi.",
        "2": "Spor 2 — Bevis: Fokuser på at samle stærke PoC beviser. Brug RCE PoC-strategi og validator workflow fra playbook.",
        "3": "Spor 3 — Triangulering: Krydsreferér fund på tværs af targets. Brug nuclei clustering og triage-regler fra playbook.",
        "": "Kør ALLE 3 spor fra playbook. Start med spor 1 (store payouts), gå videre til spor 2 (bevis) og spor 3 (triangulering). Følg playbookens sektioner 1-13 systematisk.",
    }
    spor_instruks = spor_map.get(spor_choice, spor_map[""])

    return f"""Kør TEAM PLAYBOOK v2.0 som din mission guide.

{spor_instruks}

HER ER HELE PLAYBOOKEN — følg den systematisk:

{playbook}

Start jagten nu. Rapportér alle fund med severity og bounty estimat."""

def select_model():
    print(f"""
{BOLD}{C.YELLOW}Vaelg model:{END}
  {C.GREEN}[1]{END}  kimi-k2.6:cloud        {C.DIM}(STANDARD — hurtig & klog){END}
  {C.GREEN}[a]{END}  auto-select            {C.DIM}(lader Grok vaelge){END}
  {C.GREEN}[q]{END}  annuller
    """)
    choice = input(f"  {C.YELLOW}> {END}").strip().lower()
    models = {
        "1": ("ollama", "kimi-k2.6:cloud"),
    }
    if choice in ("q", ""):
        return None, None
    if choice == "a":
        return None, "auto"
    return models.get(choice, (None, None))

def format_uptime(seconds):
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds//60}m"
    else:
        return f"{seconds//3600}h{seconds%3600//60}m"

def main():
    force_model = None
    force_provider = None
    if "--model" in sys.argv:
        idx = sys.argv.index("--model")
        if idx + 1 < len(sys.argv):
            model_name = sys.argv[idx + 1]
            if "/" in model_name:
                parts = model_name.split("/", 1)
                if parts[0] in ("fcc", "ollama", "groq"):
                    force_provider = parts[0]
                    force_model = parts[1]
                else:
                    force_model = model_name
            else:
                force_model = model_name

    clear()
    print(LOGO)

    if force_model:
        provider = force_provider or "ollama"
        print(f"  {C.DIM}Model: {provider}/{force_model}{END}")
    else:
        print(f"  {C.YELLOW}Vælg model for at starte:{END}")
        provider, force_model = select_model()
        if not provider and force_model != "auto":
            print(f"\n  {C.RED}Farvel!{END}")
            return

    print(f"\n  {C.DIM}Starter Grok...{END}")
    try:
        agent = GrokAgent(model=force_model, provider=force_provider or provider or "ollama")
        agent.interactive = True
    except Exception as e:
        print(f"\n  {C.RED}FEJL ved start: {e}{END}")
        print(f"  {C.DIM}Tjek at Ollama Cloud keys er gyldige{END}")
        return

    model_display = f"{agent.router.active_provider}/{agent.router.active_model}"
    start_time = time.time()
    turn_count = 0

    while True:
        try:
            uptime = format_uptime(int(time.time() - start_time))
            clear()
            show_main_menu(model_display, turn_count, uptime)

            try:
                user_input = input(f"\n  {BOLD}{C.RED}du{END} > ").strip()
            except (EOFError, KeyboardInterrupt):
                print(f"\n  {C.RED}Farvel!{END}")
                break

            if not user_input:
                continue

            # System commands
            if user_input in ("q", "quit"):
                try: agent.memory.save_session()
                except: pass
                print(f"\n  {C.RED}Farvel!{END}")
                break

            elif user_input == "c":
                continue  # clear allerede kørt

            elif user_input == "m":
                new_provider, new_model = select_model()
                if new_provider:
                    try:
                        agent.switch_model(new_provider, new_model)
                        model_display = f"{new_provider}/{new_model}"
                        print(f"\n  {C.GREEN}Skiftet til: {model_display}{END}")
                        time.sleep(1)
                    except Exception as e:
                        print(f"\n  {C.RED}Skift fejlede: {e}{END}")
                        time.sleep(2)
                continue

            elif user_input == "s":
                try:
                    status = agent.get_status()
                    print(f"\n  {C.CYAN}═══ STATUS ═══{END}")
                    print(f"  Provider:  {status['provider']}")
                    print(f"  Model:     {status['model']}")
                    print(f"  Turns:     {status['turns']}")
                    print(f"  Tools:     {status['tools_used']}")
                    print(f"  Uptime:    {format_uptime(status['uptime_seconds'])}")
                except Exception as e:
                    print(f"\n  {C.RED}Status fejl: {e}{END}")
                input(f"\n  {C.DIM}Enter for at fortsætte...{END}")
                continue

            elif user_input == "h":
                try:
                    msgs = agent.memory.get_chat_messages()[-20:]
                    print(f"\n  {C.CYAN}═══ HISTORIK (seneste {len(msgs)}) ═══{END}")
                    for m in msgs:
                        role = m["role"]
                        content = str(m.get("content", ""))[:120]
                        if role == "user":
                            print(f"  {C.RED}du{END}: {content}")
                        elif role == "assistant":
                            print(f"  {C.GREEN}grok{END}: {content}")
                except Exception as e:
                    print(f"\n  {C.RED}Historik fejl: {e}{END}")
                input(f"\n  {C.DIM}Enter for at fortsætte...{END}")
                continue

            elif user_input == "t":
                try:
                    from core.tools import ACTIVE_TOOLS
                    print(f"\n  {C.CYAN}═══ TOOLS ({len(ACTIVE_TOOLS)}) ═══{END}")
                    categories = {}
                    for name, t in ACTIVE_TOOLS.items():
                        cat = t.get("cat", "other")
                        categories.setdefault(cat, []).append(name)
                    for cat, tools in sorted(categories.items()):
                        print(f"\n  {BOLD}{cat.upper()}{END} ({len(tools)})")
                        print(f"  {C.DIM}{', '.join(tools[:8])}{'...' if len(tools) > 8 else ''}{END}")
                except Exception as e:
                    print(f"\n  {C.RED}Tools fejl: {e}{END}")
                input(f"\n  {C.DIM}Enter for at fortsætte...{END}")
                continue

            elif user_input == "f":
                try:
                    facts_file = os.path.expanduser("~/.grok/facts.json")
                    if os.path.exists(facts_file):
                        facts = json.load(open(facts_file))
                        print(f"\n  {C.CYAN}═══ FAKTA ═══{END}")
                        for k, v in facts.items():
                            val = v["value"] if isinstance(v, dict) else v
                            print(f"  {BOLD}{k}{END}: {val[:80]}")
                    else:
                        print(f"\n  {C.DIM}Ingen facts.json{END}")
                except Exception as e:
                    print(f"\n  {C.RED}Fakta fejl: {e}{END}")
                input(f"\n  {C.DIM}Enter for at fortsætte...{END}")
                continue

            # Mission choices (numbered menu items)
            elif user_input in MISSIONS:
                mission_type, prompt_text = MISSIONS[user_input]
                target = input(f"  {C.YELLOW}{prompt_text}{END}").strip()
                mission_prompt = build_mission_prompt(mission_type, target)
                print(f"\n  {C.YELLOW}▶ Mission startet...{END}\n")
                try:
                    result = agent.run(mission_prompt)
                    turn_count += 1
                    print(f"\n{C.BOLD}{C.GREEN}═══ RESULTAT ═══{END}")
                    print(f"{C.GREEN}{result}{END}")
                except Exception as e:
                    print(f"\n  {C.RED}MISSION FEJL: {e}{END}")
                input(f"\n  {C.DIM}Enter for at fortsætte...{END}")
                continue

            # Slash commands (legacy support)
            elif user_input.startswith("/"):
                cmd = user_input.lower().split()
                if cmd[0] in ("/exit", "/quit", "/q"):
                    break
                elif cmd[0] == "/help":
                    print(f"\n  {C.DIM}Brug nummer-valg fra menuen, eller skriv direkte.{END}")
                    input(f"  {C.DIM}Enter for at fortsætte...{END}")
                    continue
                else:
                    # Pass slash command as chat
                    pass  # fall through to chat

            # Direct chat (anything else)
            print(f"\n  {C.DIM}Grok tænker...{END}\n")
            try:
                response = agent.chat(user_input)
                turn_count += 1
                print(f"\n{C.BOLD}{C.GREEN}grok{END} > {response}")
            except Exception as e:
                print(f"\n  {C.RED}FEJL: {e}{END}")
            input(f"\n  {C.DIM}Enter for at fortsætte...{END}")

        except KeyboardInterrupt:
            print(f"\n\n  {C.YELLOW}Ctrl+C - brug q for at afslutte{END}")
            # Reset stdin efter interrupt - WSL korrumperer input bufferen
            import sys
            try:
                sys.stdin = open('/dev/tty', 'r')
            except:
                pass
            time.sleep(0.5)
            continue

    try: agent.memory.save_session()
    except: pass
    print()

if __name__ == "__main__":
    main()