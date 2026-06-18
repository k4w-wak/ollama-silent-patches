#!/usr/bin/env python3
import sys, os
sys.path.insert(0, '/home/admin_user/grok_engine')
sys.path.insert(0, '/home/admin_user/grok_engine/core')

from core.agent import GrokAgent

agent = GrokAgent(model='kimi-k2.6:cloud', provider='ollama')
agent.interactive = True

mission = '''Du er lead pentester på et autoriseret bug bounty. 
Target: scanme.nmap.org
Din mission:
1. nmap_scan - find ALLE porte og services
2. dir_scan på http://scanme.nmap.org - find skjulte stier
3. sslscan - check TLS og certifikater
4. nuclei_scan - find kendte CVEs
5. osint_domain - samle threat intel

Analyser ALT og lav en komplet sikkerhedsrapport med:
- CVSS severity scores
- Attack vector beskrivelser
- Konkrete exploit anbefalinger
- Risk ratings (Critical/High/Medium/Low/Info)

Du har carte blanche.'''

result = agent.run(mission)
print("\n" + "="*60)
print("MISSION COMPLETE")
print("="*60)
print(result)
