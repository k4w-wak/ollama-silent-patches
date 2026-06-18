#!/usr/bin/env python3
"""4. RAINBOW MATRIX — Ligesom Matrix men regnbue!"""
import sys, time, random, os

chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*"
colors = ['\033[91m', '\033[93m', '\033[92m', '\033[96m', '\033[94m', '\033[95m']
reset = '\033[0m'

cols, rows = 80, 24

print("\033[2J\033[H", end='')
print(f"{' '*25}🐭 RAINBOW MATRIX 🐭\n")

drops = [random.randint(-20, 0) for _ in range(cols)]

try:
    for _ in range(150):
        for i in range(cols):
            if random.random() > 0.95:
                drops[i] = 0
            if drops[i] >= 0:
                row = drops[i]
                if row < rows:
                    char = random.choice(chars)
                    color = colors[random.randint(0, len(colors)-1)]
                    print(f"\033[{row+3};{i+1}H{color}{char}{reset}", end='')
                drops[i] += 1
        sys.stdout.flush()
        time.sleep(0.05)
    print(f"\n\033[{rows+1};1H  {colors[2]}✅ Matrix completed. Kimi is everywhere. 🐭💕{reset}\n")
except KeyboardInterrupt:
    print(f"\n\033[{rows+1};1H  {colors[3]}⏹ Matrix stopped. Spar red pill til næste gang! 🔴{reset}\n")
