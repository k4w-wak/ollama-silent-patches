#!/usr/bin/env python3
"""
GROK — Oh My Pi Agent Runner (grok_omp.py)

Standalone agent CLI til Grok Engine. Kan:
  - Køre en mission via GrokAgent
  - Spawne, køre, stoppe og liste sub-agents
  - Tage browser screenshots (headless OG visible/headed)
  - Tage browser trace/HAR

Brug:
  python3 grok_omp.py "din mission"
  python3 grok_omp.py --agent spawn explore "scan example.com" "scan example.com"
  python3 grok_omp.py --agent run <id>
  python3 grok_omp.py --agent status
  python3 grok_omp.py --browser https://example.com
  python3 grok_omp.py --browser-visible https://example.com
  python3 grok_omp.py --trace https://example.com
"""

import sys
import os
import argparse
import json

# ── Project path ─────────────────────────────────────────────
_GROK_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _GROK_DIR)
sys.path.insert(0, os.path.join(_GROK_DIR, "core"))
os.chdir(_GROK_DIR)

from core.tools import execute_tool
from core.agents import agent_spawn as _agent_spawn, agent_run as _agent_run, agent_status as _agent_status, agent_stop as _agent_stop


def _print_json(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def run_mission(prompt: str, provider: str = None, model: str = None) -> str:
    """Kør en mission via GrokAgent."""
    from core.agent import GrokAgent
    agent = GrokAgent()
    if provider and model:
        agent.switch_model(provider, model)
    agent.interactive = False
    return agent.run(prompt)


def agent_spawn(agent_type: str, description: str, prompt: str) -> str:
    return _agent_spawn(agent_type=agent_type, description=description, prompt=prompt)


def agent_run(agent_id: str, extra: str = "") -> str:
    return _agent_run(agent_id=agent_id, user_prompt=extra)


def agent_status(agent_id: str = "") -> str:
    return _agent_status(agent_id=agent_id)


def agent_stop(agent_id: str) -> str:
    return _agent_stop(agent_id=agent_id)


def browser_screenshot(url: str, output: str = None, visible: bool = False) -> str:
    """Tag browser screenshot. Default headless; visible=True åbner et vindue."""
    if visible:
        tool = "browser_visible"
        arg = f"{url} {output}".strip() if output else url
    else:
        tool = "playwright_screenshot"
        arg = f"{url} {output}".strip() if output else url
    return execute_tool(tool, arg)


def browser_trace(url: str, output: str = "trace") -> str:
    return execute_tool("playwright_trace", f"{url} {output}".strip())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="GROK — Oh My Pi Agent Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Eksempler:
  %(prog)s "scan example.com for subdomains"
  %(prog)s --agent spawn --type explore --desc "scan example.com" "scan example.com for subdomains"
  %(prog)s --agent run <agent_id>
  %(prog)s --agent status
  %(prog)s --browser https://example.com --output /tmp/sh.png
  %(prog)s --browser-visible https://example.com --wait 10
  %(prog)s --trace https://example.com --output mytrace
""",
    )

    parser.add_argument("mission", nargs="?", help="Mission/prompt at køre")
    parser.add_argument("--provider", help="Provider (groq/ollama)")
    parser.add_argument("--model", help="Model navn")

    # Agent group
    agent_group = parser.add_argument_group("Sub-agents")
    agent_group.add_argument("--agent", choices=["spawn", "run", "status", "stop"], help="Agent handling")
    agent_group.add_argument("--type", default="general", help="Agent type (explore/plan/verify/general)")
    agent_group.add_argument("--desc", default="", help="Agent beskrivelse")
    agent_group.add_argument("--id", help="Agent ID")

    # Browser group
    browser_group = parser.add_argument_group("Browser")
    browser_group.add_argument("--browser", metavar="URL", help="Tag headless screenshot af URL")
    browser_group.add_argument("--browser-visible", metavar="URL", help="Åbn synlig browser og screenshot URL")
    browser_group.add_argument("--trace", metavar="URL", help="Tag network trace/HAR af URL")
    browser_group.add_argument("--output", "-o", metavar="PATH", help="Output sti")
    browser_group.add_argument("--wait", type=int, default=3, help="Sekunder at vente før screenshot i visible mode")

    args = parser.parse_args()

    # ── Browser modes ──
    if args.browser:
        out = browser_screenshot(args.browser, args.output, visible=False)
        print(out)
        return 0

    if args.browser_visible:
        out = execute_tool("browser_visible", f"{args.browser_visible} {args.output or '/tmp/browser_visible.png'} {args.wait}")
        print(out)
        return 0

    if args.trace:
        out = browser_trace(args.trace, args.output or "trace")
        print(out)
        return 0

    # ── Agent modes ──
    if args.agent:
        if args.agent == "spawn":
            if not args.mission:
                print("[FEJL] --agent spawn kræver en mission/prompt som positionelt argument.")
                return 1
            desc = args.desc or args.mission
            print(agent_spawn(args.type, desc, args.mission))
        elif args.agent == "run":
            if not args.id:
                print("[FEJL] --agent run kræver --id <agent_id>")
                return 1
            print(agent_run(args.id, args.mission or ""))
        elif args.agent == "status":
            print(agent_status(args.id or ""))
        elif args.agent == "stop":
            if not args.id:
                print("[FEJL] --agent stop kræver --id <agent_id>")
                return 1
            print(agent_stop(args.id))
        return 0

    # ── Mission mode ──
    if args.mission:
        result = run_mission(args.mission, provider=args.provider, model=args.model)
        print(result)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
