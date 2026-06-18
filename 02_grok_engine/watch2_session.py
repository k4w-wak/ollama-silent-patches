#!/usr/bin/env python3
"""TERMINAL 2 — GROK SESSION MONITOR"""
import os, time, json

SDIR = os.path.expanduser("~/.grok/sessions/")
R='\033[91m'; G='\033[92m'; Y='\033[93m'; C='\033[96m'; B='\033[1m'; D='\033[2m'; E='\033[0m'

print(f"{B}{C}╔══════════════════════════════════════════════╗\n║      GROK SESSION MONITOR — live chat        ║\n╚══════════════════════════════════════════════╝{E}")

shown = set()
while True:
    try:
        files = sorted([f for f in os.listdir(SDIR) if f.endswith('.json')])
        if files:
            latest = os.path.join(SDIR, files[-1])
            with open(latest) as f:
                data = json.load(f)
            msgs = data.get('messages', data if isinstance(data, list) else [])
            for i, m in enumerate(msgs):
                if i in shown: continue
                shown.add(i)
                role = m.get('role','?')
                content = str(m.get('content',''))[:300]
                icon = {'user': f'{Y}▸ DU{E}', 'assistant': f'{G}◉ GROK{E}', 'system': f'{C}⚙ SYS{E}', 'tool': f'{D}◆ TOOL{E}'}
                tag = icon.get(role, f'[{role}]')
                content = content.replace('\n', ' ')[:200]
                print(f"  {tag}: {content}{E}")
    except: pass
    time.sleep(1)
