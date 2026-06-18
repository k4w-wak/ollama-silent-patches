#!/usr/bin/env python3
"""
GROK CHALLENGE — Live scanning med real-time output
Brug: python3 grok_challenge.py <target>
"""
import sys, os, time, threading
sys.path.insert(0, '/home/admin_user/grok_engine')
sys.path.insert(0, '/home/admin_user/grok_engine/core')
from core.tools import execute_tool

C = {
    'RED': '\033[91m', 'GREEN': '\033[92m', 'YELLOW': '\033[93m',
    'BLUE': '\033[94m', 'CYAN': '\033[96m', 'MAGENTA': '\033[95m',
    'BOLD': '\033[1m', 'DIM': '\033[2m', 'END': '\033[0m'
}

def print_colored(color, text):
    print(f"{C[color]}{text}{C['END']}", flush=True)

def run_tool_live(name, target):
    """Kør et tool og vis output i realtid"""
    t1 = time.time()
    print_colored('CYAN', f"\n▶ [{name}] starter...")
    
    result = execute_tool(name, target)
    
    t2 = time.time()
    elapsed = t2 - t1
    print_colored('GREEN', f"✓ [{name}] færdig ({elapsed:.1f}s)")
    
    # Vis første 600 tegn af resultatet
    lines = result.split('\n')[:15]
    for line in lines:
        print(f"  {C['DIM']}{line[:110]}{C['END']}")
    if len(result) > 600:
        print_colored('DIM', f"  ... ({len(result)} tegn total)")
    
    return {"result": result, "time": elapsed}

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "scanme.nmap.org"
    
    print_colored('YELLOW', "="*70)
    print_colored('YELLOW', f"🏴‍☠️  GROK CHALLENGE — Target: {target}")
    print_colored('YELLOW', "="*70)
    print(f"Start: {time.strftime('%H:%M:%S')}\n")
    
    total_start = time.time()
    results = {}
    
    tools = ['nmap_scan', 'dns_enum', 'osint_domain']
    
    # Sekventiel for bedre readability
    for tool in tools:
        results[tool] = run_tool_live(tool, target)
    
    total_time = time.time() - total_start
    
    print_colored('YELLOW', f"\n{'='*70}")
    print_colored('YELLOW', "📊 RESULTATOVERSIGT")
    print_colored('YELLOW', f"{'='*70}")
    
    for name, data in results.items():
        print(f"  {C['BOLD']}{name}{C['END']} : {data['time']:.1f}s")
    
    print_colored('GREEN', f"\n⏱ Total tid: {total_time:.1f}s")
    print(f"Færdig: {time.strftime('%H:%M:%S')}")
    
    # Gem til fil
    log_file = f"/tmp/challenge_{target.replace('/', '_')}.log"
    with open(log_file, 'w') as f:
        f.write(f"GROK CHALLENGE — {target}\n")
        f.write(f"Tid: {time.strftime('%H:%M:%S')}\n")
        f.write(f"Total: {total_time:.1f}s\n\n")
        for name, data in results.items():
            f.write(f"\n{'='*60}\n")
            f.write(f"[{name}] ({data['time']:.1f}s)\n")
            f.write(f"{'='*60}\n")
            f.write(data['result'])
            f.write("\n")
    
    print_colored('CYAN', f"\n💾 Gemt til: {log_file}")

if __name__ == "__main__":
    main()
