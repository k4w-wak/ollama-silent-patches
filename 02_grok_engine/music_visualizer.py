#!/usr/bin/env python3
"""3. TERMINAL MUSIK VISUALIZER — Fake men flot!"""
import sys, time, random, os

bars = ['▁','▂','▃','▄','▅','▆','▇','█']
colors = ['\033[91m', '\033[93m', '\033[92m', '\033[96m', '\033[94m', '\033[95m']
reset = '\033[0m'

print("\033[2J\033[H", end='')
print(f"{' '*22}🐭 KIMI MUSIC VISUALIZER 🐭")
print(f"{' '*18}(fake music - real colors!)\n")
print(f"  {' '*8}https://www.youtube.com/watch?v=YGee7cXlNIg")
print(f"{' '*15}🎵 Playing: Massive Attack - Teardrop 🎵\n")

try:
    for _ in range(60):
        line = '  '
        for i in range(20):
            h = random.randint(0, 7)
            line += colors[i % len(colors)] + bars[h] + reset
        sys.stdout.write(f'\r{line}')
        sys.stdout.flush()
        time.sleep(0.12)
    print(f"\n\n  {colors[3]}🎶 Musikken sluttede... men Kimi musen danser videre! 🐭💕{reset}\n")
except KeyboardInterrupt:
    print(f"\n\n  {colors[2]}⏹ Stoppet. Nyd musikken! 🎵{reset}\n")
