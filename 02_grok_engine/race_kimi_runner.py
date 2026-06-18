#!/usr/bin/env python3
"""KIMI RACE — Background mission runner"""
import sys, os, time
sys.path.insert(0, '/home/admin_user/grok_engine')
sys.path.insert(0, '/home/admin_user/grok_engine/core')
from core.agent import GrokAgent

log_path = '/tmp/race_kimi.log'

with open(log_path, 'w') as log:
    log.write("🏁 CHALLENGE 2: TRUE OSINT RACE\n")
    log.write(f"Start: {time.strftime('%H:%M:%S')}\n")
    log.write("="*60 + "\n\n")

agent = GrokAgent(model='kimi-k2.6:cloud', provider='ollama')
agent.interactive = True

mission = '''CHALLENGE 2: TRUE OSINT RACE
Target: rapid7.com
Du har 10 minutter.
Maal: Find 5 subdomains + 1 easter egg.
INGEN port scanning. Kun OSINT tools: dns_enum (passiv), wayback_urls, cert_transparency, web_search, osint_domain.
Rapportér ALLE fund med timestamps.'''

t1 = time.time()
result = agent.run(mission)
t2 = time.time()

with open(log_path, 'a') as log:
    log.write(result + "\n")
    log.write("="*60 + "\n")
    log.write(f"Tid: {t2-t1:.1f}s\n")
    log.write("🏁 FÆRDIG!\n")

print("🏁 RACE KIMI DONE!")
