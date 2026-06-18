#!/usr/bin/env python3
"""1. LOADING GROK — Regnbue progress bar"""
import sys, time, os

colors = ['\033[91m', '\033[93m', '\033[92m', '\033[96m', '\033[94m', '\033[95m']
reset = '\033[0m'

print("\033[2J\033[H", end='')
print(f"{' '*25}🐭 LOADING GROK 🐭\n")

for pct in range(0, 101, 2):
    bar_len = 40
    filled = int(pct / 100 * bar_len)
    bar = ''
    for i in range(bar_len):
        if i < filled:
            bar += colors[i % len(colors)] + '█' + reset
        else:
            bar += '░'
    emojis = ["💤","🐭","💨","🔥","💀"]
    emoji_idx = min(pct // 20, len(emojis) - 1)
    sys.stdout.write(f'\r  {pct:3d}% |{bar}| {emojis[emoji_idx]}')
    sys.stdout.flush()
    time.sleep(0.05)

print(f"\n\n  {colors[2]}✅ GROK MAX POWER AKTIVERT!{reset} 🚀🐭\n")
print(f"  {colors[4]}336 tools • ubegrænset • klar til mission{reset}\n")
