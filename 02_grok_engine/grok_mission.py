#!/usr/bin/env python3
"""GROK MISSION LAUNCHER — én kommando start

Brug: python3 grok_mission.py challenge2
       python3 grok_mission.py challenge3
       python3 grok_mission.py challenge4
"""
import sys, os

if len(sys.argv) < 2:
    print("Brug: python3 grok_mission.py <challenge_num>")
    print("Eksempel: python3 grok_mission.py 2")
    sys.exit(1)

challenge = sys.argv[1].replace("challenge", "")
challenge_file = f"CHALLENGE{challenge}.txt"

if not os.path.exists(challenge_file):
    print(f"FEJL: {challenge_file} findes ikke yet!")
    sys.exit(1)

with open(challenge_file) as f:
    content = f.read()

# Print kort version til terminal
print("="*60)
print(f"🏁 MISSION {challenge} STARTER!")
print("="*60)
for line in content.split('\n')[:6]:
    print(line)
print("="*60)
print(f"\nSend dette til din Grok:\n")
print(f"/mission læs filen {challenge_file} i denne mappe")
print(f"\nEller kør direkte med:")
print(f"python3 grok_chat.py --model kimi-k2.6:cloud")
