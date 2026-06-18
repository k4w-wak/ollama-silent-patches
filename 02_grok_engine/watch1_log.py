#!/usr/bin/env python3
"""TERMINAL 1 — GROK LIVE LOG"""
import os, time

LOG = os.path.expanduser("~/.grok/logs/grok.log")
R='\033[91m'; G='\033[92m'; Y='\033[93m'; C='\033[96m'; B='\033[1m'; D='\033[2m'; E='\033[0m'

last = 0
print(f"{B}{Y}╔══════════════════════════════════════════════╗\n║        GROK LIVE LOG — hvert sekund          ║\n╚══════════════════════════════════════════════╝{E}")
while True:
    if os.path.exists(LOG):
        s = os.path.getsize(LOG)
        if s > last:
            with open(LOG) as f:
                f.seek(last)
                new = f.read()
            for line in new.strip().split('\n'):
                line = line.strip()
                if not line: continue
                if '▶' in line: print(f"  {G}{line}{E}")
                elif '◆' in line: print(f"  {D}  └─ {line[:120]}{E}")
                elif 'GROK SVAR' in line: print(f"  {C}{line[:140]}{E}")
                elif 'FEJL' in line: print(f"  {R}{line}{E}")
                else: print(f"  {line[:140]}")
            last = s
    time.sleep(1)
