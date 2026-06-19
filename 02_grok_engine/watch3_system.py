#!/usr/bin/env python3
"""TERMINAL 3 — SYSTEM HEALTH MONITOR"""
import os, time, subprocess, json

R='\033[91m'; G='\033[92m'; Y='\033[93m'; C='\033[96m'; B='\033[1m'; D='\033[2m'; E='\033[0m'

# === PERMANENT UTF-8 ENCODING FIX ===
_UTF8_ENV = {**__import__('os').environ, 'PYTHONIOENCODING': 'utf-8', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8'}

def ok(test): return f"{G}●{E}" if test else f"{R}●{E}"

print(f"{B}{Y}╔══════════════════════════════════════════════╗\n║        SYSTEM HEALTH — hvert sekund          ║\n╚══════════════════════════════════════════════╝{E}")

while True:
    os.system('clear')
    print(f"{B}  GROK MAX POWER — SYSTEM MONITOR{E}\n")
    
    # Ollama
    try:
        r = subprocess.run("curl -s http://127.0.0.1:11434/api/tags", shell=True, capture_output=True, text=True, timeout=2, encoding='utf-8', errors='replace', env=_UTF8_ENV)
        up = r.returncode == 0 and r.stdout.strip()
        if up:
            print(f"  {ok(True)} Ollama: {G}ONLINE{E}")
        else:
            print(f"  {ok(False)} Ollama: {R}DOWN{E}")
    except:
        print(f"  {ok(False)} Ollama: {R}UNREACHABLE{E}")
    
    # FCC Proxy
    try:
        r = subprocess.run("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8082/v1/models", shell=True, capture_output=True, text=True, timeout=2, encoding='utf-8', errors='replace', env=_UTF8_ENV)
        up = r.stdout.strip() == '200'
        print(f"  {ok(up)} FCC Proxy: {G+'ONLINE — Claude 4 via NVIDIA'+E if up else R+'DOWN'+E}")
    except:
        print(f"  {ok(False)} FCC Proxy: {R}DOWN{E}")
    
    # Grok sessions
    sdir = os.path.expanduser("~/.grok/sessions/")
    try:
        files = sorted([f for f in os.listdir(sdir) if f.endswith('.json')])
        count = len(files)
        latest = files[-1] if files else 'ingen'
        print(f"  {ok(True)} Grok sessions: {count} gemt | seneste: {C}{latest}{E}")
    except:
        print(f"  {ok(False)} Grok sessions: kan ikke læse")
    
    # Grok log
    logf = os.path.expanduser("~/.grok/logs/grok.log")
    try:
        size = os.path.getsize(logf)
        with open(logf) as f:
            lines = f.readlines()
            activity = sum(1 for l in lines[-50:] if '▶' in l)
        print(f"  {ok(True)} Grok log: {size//1024}KB | seneste 50 linjer: {activity} tool-kald")
    except:
        print(f"  {ok(False)} Grok log: kan ikke læse")
    
    # Hardware
    try:
        r = subprocess.run("df -h / | tail -1 | awk '{print $4\" fri af \"$2\" (WSL)\"}'", shell=True, capture_output=True, text=True, timeout=2, encoding='utf-8', errors='replace', env=_UTF8_ENV)
        disk = r.stdout.strip()
        r = subprocess.run("free -h | grep Mem | awk '{print $7\" ledig af \"$2\" (aktiv)\"}'", shell=True, capture_output=True, text=True, timeout=2, encoding='utf-8', errors='replace', env=_UTF8_ENV)
        mem = r.stdout.strip()
        print(f"  {ok(True)} HOST PC: 250GB SSD | 24GB DDR4 | Radeon GPU")
        print(f"  {D}  WSL disk: {disk}")
        print(f"  {' ' * 2}WSL RAM:  {mem}{E}")
    except: pass
    
    # Seneste Grok aktivitet (fra log)
    print(f"\n  {B}─── SENESTE AKTIVITET ───{E}")
    try:
        with open(logf) as f:
            lines = [l.strip() for l in f.readlines() if l.strip() and ('▶' in l or '◆' in l or 'FEJL' in l)]
            for l in lines[-8:]:
                if '▶' in l: print(f"  {G}{l[:140]}{E}")
                elif '◆' in l: print(f"  {D}  └─ {l[:140]}{E}")
                elif 'FEJL' in l: print(f"  {R}{l[:140]}{E}")
    except: pass
    
    print(f"\n  {D}Opdaterer hvert sekund — Ctrl+C for at stoppe{E}")
    time.sleep(1)
