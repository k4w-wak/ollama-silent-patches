#!/usr/bin/env python3 -u
"""
GROK CHAT — Interaktiv chat med menu
Kør: python3 grok_chat.py
     python3 grok_chat.py --model kimi-k2.6:cloud
"""

import sys, os, time
sys.stdout.reconfigure(line_buffering=True)
from datetime import datetime

GROK_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, GROK_DIR)
sys.path.insert(0, os.path.join(GROK_DIR, 'core'))
os.chdir(GROK_DIR)

from core.agent import GrokAgent, Colors

# ── Farver ──────────────────────────────────────────────
C = Colors
BOLD = '\033[1m'
DIM = '\033[2m'
END = '\033[0m'

LOGO = f"""
{C.RED}╔══════════════════════════════════════╗
║    {C.YELLOW}GROK MAX POWER{C.RED}                   ║
║    {C.CYAN}336 tools • ubegraenset{C.RED}             ║
╚══════════════════════════════════════╝{END}
"""

def show_menu():
    """Vis model-menu"""
    print(f"""
{C.BOLD}{C.YELLOW}Vaelg model:{END}
  {C.GREEN}[1]{END}  kimi-k2.6:cloud        {C.DIM}(STANDARD — hurtig & klog){END}
  {C.GREEN}[a]{END}  auto-select            {C.DIM}(lader Grok vaelge){END}
  {C.GREEN}[q]{END}  quit
    """)

def select_model(choice):
    models = {
        "1": ("ollama", "kimi-k2.6:cloud"),
    }
    if choice == "a" or choice == "":
        return None, None
    return models.get(choice, (None, None))

def print_help():
    print(f"""
{C.CYAN}Kommandoer:{END}
  /model      — Skift model
  /config     — Læs/skriv settings
  /whoami     — Vis hvem der kører grok
  /challenge <target> — Kør parallel scan challenge
  /help       — Denne hjaelp
  /tools      — Antal tools
  /status     — Agent status
  /history    — Vis chat historik
  /save       — Gem session
  /clear      — Ryd skaerm
  /exit, /quit — Afslut
  /mission <prompt> — Mission mode (ReAct med tools)
    """)

def main():
    # Parse --model argument
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

    # Model menu
    os.system('clear')
    print(LOGO)
    
    if force_model:
        provider = force_provider or "ollama"
        print(f"  {C.DIM}Model: {provider}/{force_model}{END}")
    else:
        show_menu()
        choice = input(f"  {C.YELLOW}> {END}").strip().lower()
        if choice == "q":
            print(f"\n  {C.RED}Farvel!{END}")
            return
        provider, force_model = select_model(choice)
        if not provider:
            print(f"\n  {C.GREEN}Auto-select...{END}")
    
    # Init agent
    print(f"\n  {C.DIM}Starter Grok...{END}")
    agent = GrokAgent(model=force_model, provider=force_provider or provider)
    agent.interactive = True
    
    os.system('clear')
    print(LOGO)
    model_display = f"{agent.router.active_provider}/{agent.router.active_model}"
    print(f"  {C.GREEN}Aktiv model:{END} {C.BOLD}{model_display}{END}")
    print(f"  {C.GREEN}Tools:{END} {C.BOLD}{len(agent.router.get_tool_schemas() if hasattr(agent.router, 'get_tool_schemas') else [])}{END}")
    print(f"  {C.DIM}Skriv /help for kommandoer, eller bare chat{END}\n")
    
    # Chat loop
    try:
        while True:
            try:
                user_input = input(f"\n{C.BOLD}{C.RED}du{END} > ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            
            if not user_input:
                continue
            
            # Slash commands
            if user_input.startswith("/"):
                cmd = user_input.lower().split()
                
                if cmd[0] in ("/exit", "/quit", "/q"):
                    print(f"\n  {C.RED}Farvel!{END}")
                    break
                    
                elif cmd[0] == "/help":
                    print_help()
                    continue
                    
                elif cmd[0] == "/clear":
                    os.system('clear')
                    print(LOGO)
                    print(f"  {C.GREEN}Aktiv model:{END} {C.BOLD}{model_display}{END}\n")
                    continue
                    
                elif cmd[0] == "/status":
                    status = agent.get_status()
                    print(f"\n  {C.CYAN}Status:{END}")
                    print(f"    Provider: {status['provider']}")
                    print(f"    Model:    {status['model']}")
                    print(f"    Turns:    {status['turns']}")
                    print(f"    Tools:    {status['tools_used']}")
                    print(f"    Uptime:   {status['uptime_seconds']}s")
                    continue
                    
                elif cmd[0] == "/whoami":
                    import getpass
                    user = getpass.getuser()
                    hostname = os.uname().nodename
                    print(f"\n  {C.CYAN}User:{END} {C.BOLD}{user}{END} @ {hostname}")
                    continue
                    
                elif cmd[0] == "/model":
                    show_menu()
                    choice = input(f"  {C.YELLOW}> {END}").strip().lower()
                    if choice == "q":
                        continue
                    new_provider, new_model = select_model(choice)
                    if new_provider:
                        agent.switch_model(new_provider, new_model)
                        model_display = f"{new_provider}/{new_model}"
                        print(f"  {C.GREEN}Skiftet til: {model_display}{END}")
                    continue
                    
                elif cmd[0] == "/config":
                    try:
                        from core.tools import execute_tool
                        if len(cmd) == 1:
                            from core.config import list_settings
                            print(f"\n  {C.CYAN}Settings:{END}")
                            print(list_settings())
                        elif len(cmd) == 2:
                            result = execute_tool('config_read', cmd[1])
                            print(f"\n  {C.CYAN}{cmd[1]}:{END} {result}")
                        elif len(cmd) >= 3:
                            key = cmd[1]
                            val = " ".join(cmd[2:])
                            result = execute_tool('config_write', f"{key} {val}")
                            print(f"\n  {C.GREEN}{result}{END}")
                    except Exception as e:
                        print(f"\n  {C.RED}Config fejl: {e}{END}")
                    continue
                    
                elif cmd[0] == "/challenge":
                    try:
                        import subprocess, json
                        target = cmd[1] if len(cmd) > 1 else "scanme.nmap.org"
                        print(f"\n  {C.YELLOW}🏴‍☠️ CHALLENGE MODE — Target: {target}{END}")
                        print(f"  {C.DIM}Kører nmap + dirscan + osint parallelt...{END}\n")
                        
                        # Run tools directly via subprocess for live output
                        import threading
                        results = {}
                        
                        def run_tool(name, target):
                            from core.tools import execute_tool
                            print(f"\n  {C.CYAN}[{name}]{END} starter...")
                            t1 = time.time()
                            result = execute_tool(name, target)
                            t2 = time.time()
                            results[name] = {"result": result, "time": t2-t1}
                            print(f"  {C.GREEN}[{name}]{END} færdig ({t2-t1:.1f}s)")
                        
                        threads = []
                        for tool in ['nmap_scan', 'dns_enum', 'osint_domain']:
                            t = threading.Thread(target=run_tool, args=(tool, target))
                            t.start()
                            threads.append(t)
                        
                        for t in threads:
                            t.join()
                        
                        print(f"\n  {C.YELLOW}=== RESULTATER ==={END}")
                        for name, data in results.items():
                            print(f"\n  {C.BOLD}{name}{END} ({data['time']:.1f}s):")
                            print(f"  {data['result'][:400]}...")
                        
                        print(f"\n  {C.GREEN}Challenge færdig! Total tid: {sum(d['time'] for d in results.values()):.1f}s{END}")
                    except Exception as e:
                        print(f"  {C.RED}Fejl: {e}{END}")
                    continue
                    
                elif cmd[0] == "/mission":
                    if len(cmd) < 2:
                        print(f"  {C.RED}Brug: /mission <prompt>{END}")
                        continue
                    prompt = " ".join(cmd[1:])
                    print(f"\n  {C.YELLOW}Mission mode: {prompt}{END}\n")
                    print(f"  {C.DIM}Kører i baggrunden — se live log med: tail -f /tmp/grok_mission.log{END}\n")
                    
                    # Run mission in background with file logging
                    import subprocess
                    mission_script = '''import sys
sys.path.insert(0, '/home/admin_user/grok_engine')
sys.path.insert(0, '/home/admin_user/grok_engine/core')
from core.agent import GrokAgent
import time

t1 = time.time()
agent = GrokAgent(model='kimi-k2.6:cloud', provider='ollama')
agent.interactive = True
result = agent.run("""{p}""")
t2 = time.time()

with open('/tmp/grok_mission.log', 'w') as f:
    f.write("\\n=== MISSION FÆRDIG (" + str(round(t2-t1, 1)) + "s) ===\\n")
    f.write(result)
    f.write("\\n")
'''
                    script = mission_script.replace('{p}', prompt.replace('"', '\\"'))
                    with open('/tmp/mission_bg.py', 'w') as f:
                        f.write(script)
                    
                    subprocess.Popen(['venv/bin/python', '/tmp/mission_bg.py'],
                                   stdout=open('/tmp/grok_mission.log', 'w'),
                                   stderr=subprocess.STDOUT,
                                   cwd='/home/admin_user/grok_engine')
                    print(f"  {C.GREEN}Mission started!{END} Kør: tail -f /tmp/grok_mission.log")
                    continue
                    
                elif cmd[0] == "/history":
                    msgs = agent.memory.get_chat_messages()[-10:]
                    print(f"\n  {C.CYAN}Seneste beskeder:{END}")
                    for m in msgs:
                        role = m["role"]
                        content = str(m.get("content", ""))[:150]
                        if role == "user":
                            print(f"  {C.RED}du{END}: {content}")
                        elif role == "assistant":
                            print(f"  {C.GREEN}grok{END}: {content}")
                    continue
                    
                elif cmd[0] == "/save":
                    agent.memory.save_session()
                    print(f"  {C.GREEN}Session gemt!{END}")
                    continue
                
                elif cmd[0] == "/tools":
                    try:
                        from core.tools import tool_count
                        print(f"  {C.CYAN}Tools tilgaengelige: {tool_count()} (ReAct format){END}")
                    except:
                        print(f"  {C.DIM}Tool count ikke tilgaengelig{END}")
                    continue
                
                else:
                    print(f"  {C.RED}Ukendt kommando: {cmd[0]}{END}")
                    continue
            
            # Normal chat
            print(f"\n  {C.DIM}Grok taenker...{END}")
            try:
                response = agent.chat(user_input)
                print(f"\n{C.BOLD}{C.GREEN}grok{END} > {response}")
            except Exception as e:
                print(f"\n  {C.RED}FEJL: {e}{END}")
                
    except KeyboardInterrupt:
        print(f"\n\n  {C.RED}Farvel!{END}")
    
    # Auto-save on exit
    try:
        agent.memory.save_session()
    except:
        pass
    
    print()

if __name__ == "__main__":
    main()
