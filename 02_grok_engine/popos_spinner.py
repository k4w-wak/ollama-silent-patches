#!/usr/bin/env python3
"""2. ER POP!_OS FÆRDIG? — Spinner med random svar"""
import sys, time, random

svare = [
    "næsten...",
    "snart!",
    "kopierer configs...",
    "hade den anden Kimi spurgt?",
    "apt update kører...",
    "overfører SSH keys...",
    "dotfiles på vej!",
    "WSL siger farvel...",
    "næsten færdig!",
    "POP! 🎉"
]

frames = ['◐', '◓', '◑', '◒']

print("\033[2J\033[H", end='')
print(f"{' '*20}🐭 Er Pop!_OS færdig? 🐭\n")

for i, svar in enumerate(svare):
    for _ in range(8):
        frame = frames[random.randint(0, 3)]
        sys.stdout.write(f'\r  {frame} {svar}')
        sys.stdout.flush()
        time.sleep(0.15)
    print()

print(f"\n  ✅ {' '*10}JA! Pop!_OS er klar! 🎉🐭\n")
print(f"  🚀 WSL → Pop!_OS migration: SUCCES!\n")
