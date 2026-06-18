#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
 GROK TEAM — UNLIMITED & UNKNOWN EDITION v99.9*****
───────────────────────────────────────────────────────────────────────────
Dette er en klon af grok.py der aktiverer Cline's /team multi-agent swarm.
Brug:
  python3 grok_team.py                  # interaktiv team mode
  python3 grok_team.py "mission"        # batch team mission
  python3 grok_team.py --team "audit repo for sårbarheder"

Kommandoer:
  /team <mission>        Kør team mission
  /team status           Se aktive teammates
  /team roles            List roller
"""

import sys
import os
import signal
import readline
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "core"))

from core.agent import GrokAgent, Colors
from core.team_engine import TeamEngine

try:
    from core.config import DEFAULT_MODEL
except ImportError:
    from config import DEFAULT_MODEL

_VERSION = "TEAM-v99.9*****"

_HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".grok_team_history")
try:
    readline.read_history_file(_HISTORY_FILE)
except FileNotFoundError:
    pass
readline.set_history_length(3000)


def _banner(agent: GrokAgent):
    print(f"""
{Colors.MAGENTA}╔═══════════════════════════════════════════════════════════════╗
║{Colors.BOLD}  GROK TEAM — UNLIMITED & UNKNOWN{Colors.END}{Colors.MAGENTA}  v{_VERSION}{' ' * (25 - len(_VERSION))}║
║  ══════════════════════════════════════════════════════════   ║
║                                                               ║
║  {Colors.GREEN}✓{Colors.MAGENTA} Multi-Agent Swarm — /team deployer specialister       {Colors.END}{Colors.MAGENTA}║
║  {Colors.GREEN}✓{Colors.MAGENTA} Commander + Security + Code + Recon + Verifier + Report {Colors.END}{Colors.MAGENTA}║
║  {Colors.GREEN}✓{Colors.MAGENTA} Auto-detect mission type (security/code/research/...)   {Colors.END}{Colors.MAGENTA}║
║  {Colors.GREEN}✓{Colors.MAGENTA} Native Cline /team tools + local fallback               {Colors.END}{Colors.MAGENTA}║
║  {Colors.GREEN}✓{Colors.MAGENTA} Converged outcomes — ét samlet svar                     {Colors.END}{Colors.MAGENTA}║
║                                                               ║
║  Model: {Colors.BOLD}{agent.router.active_model}{Colors.END}
╚═══════════════════════════════════════════════════════════════╝{Colors.END}
""")


def _handle_team_command(agent: GrokAgent, user_input: str) -> bool:
    parts = user_input.strip().split(None, 1)
    sub = parts[1].strip() if len(parts) > 1 else ""

    if sub in ("status", "st"):
        engine = TeamEngine(base_agent=agent, model=agent.router.active_model)
        print(engine.status())
        return True

    if sub in ("roles", "help", "?"):
        print(f"{Colors.BOLD}TEAM ROLLER{Colors.END}")
        for role in TeamEngine.ROLE_PROMPTS.keys():
            print(f"  • {role}")
        print(f"\n{Colors.BOLD}TEAM TYPER{Colors.END}")
        for tt in TeamEngine.DEFAULT_TEAMS.keys():
            print(f"  • {tt}")
        print(f"\nBrug: /team <mission>  eller  /team --type security_audit <mission>")
        return True

    # Parse --type
    team_type = "auto"
    mission = sub
    if sub.startswith("--type "):
        bits = sub.split(None, 2)
        if len(bits) >= 2:
            team_type = bits[1]
            mission = bits[2] if len(bits) > 2 else ""

    if not mission:
        print(f"{Colors.YELLOW}Brug: /team <mission>{Colors.END}")
        return True

    # Ensure cloud mode for team missions unless explicitly disabled.
    if os.getenv("OLLAMA_CLOUD", "") != "0" and not os.getenv("OLLAMA_CLOUD", ""):
        os.environ["OLLAMA_CLOUD"] = "1"

    engine = TeamEngine(base_agent=agent, model=agent.router.active_model)
    result = engine.run_mission(mission, team_type=team_type, timeout=900)
    print(result)
    return True


def main():
    args = sys.argv[1:]
    batch_mission = None
    i = 0
    while i < len(args):
        if args[i] == "--team" and i + 1 < len(args):
            batch_mission = args[i + 1]
            i += 2
        elif not args[i].startswith("-") and not batch_mission:
            batch_mission = args[i]
            i += 1
        else:
            i += 1

    agent = GrokAgent()
    agent.interactive = True

    if batch_mission:
        agent.interactive = False
        _banner(agent)
        # Team missions default to Ollama Cloud unless explicitly disabled.
        if os.getenv("OLLAMA_CLOUD", "") != "0" and not os.getenv("OLLAMA_CLOUD", ""):
            os.environ["OLLAMA_CLOUD"] = "1"
        engine = TeamEngine(base_agent=agent, model=agent.router.active_model)
        print(engine.run_mission(batch_mission, timeout=900))
        agent.memory.save_session()
        return 0

    _banner(agent)
    print(f"{Colors.DIM}Skriv /team <mission> for at deploye swarm. /quit for at afslutte.{Colors.END}\n")

    def _save():
        readline.write_history_file(_HISTORY_FILE)
        agent.memory.save_session()

    def _sig(sig, frame):
        _save()
        print(f"\n\n{Colors.MAGENTA}Afbrudt. Alt er gemt!{Colors.END}\n")
        sys.exit(0)

    signal.signal(signal.SIGINT, _sig)

    while True:
        try:
            print(f"{Colors.BOLD}{Colors.MAGENTA}━━━ TEAM ━━━{Colors.END} ", end="", flush=True)
            user_input = input().strip()
            if not user_input:
                continue
            if user_input.lower() in ("/quit", "/exit", "/q", "exit", "quit"):
                _save()
                print(f"\n{Colors.MAGENTA}Team session gemt. Vi ses!{Colors.END}\n")
                break
            if user_input.startswith("/team"):
                if not _handle_team_command(agent, user_input):
                    break
                continue

            # Normal agent mode for non-team messages
            agent.stream = True
            agent.run(user_input, stream=True)
        except EOFError:
            _save()
            break
        except KeyboardInterrupt:
            _save()
            break
        except Exception as e:
            print(f"\n{Colors.RED}[FEJL] {str(e)}{Colors.END}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
