#!/usr/bin/env python3
"""
KIMI MUSEN — Din terminal mus! 🐭
Kør: python3 kimi_mouse.py
"""
import os, sys, time, random

# ANSI farver
C = {
    'pink': '\033[95m', 'cyan': '\033[96m', 'yellow': '\033[93m',
    'green': '\033[92m', 'red': '\033[91m', 'blue': '\033[94m',
    'bold': '\033[1m', 'end': '\033[0m', 'clear': '\033[2J\033[H'
}

# Mus frames
MUS = [
    [
        "    🐭    ",
        "   /||\\   ",
        "  / || \\  ",
        "   |  |   ",
        "   |  |   ",
        "   ^  ^   "
    ],
    [
        "  🐭       ",
        " /||\\     ",
        "/ || \\    ",
        " |  |     ",
        " |  |     ",
        " ^  ^     "
    ],
    [
        "       🐭  ",
        "     /||\\ ",
        "    / || \\ ",
        "     |  |  ",
        "     |  |  ",
        "     ^  ^  "
    ]
]

HEARTS = ["💕", "💖", "💗", "💓", "💞"]

def draw_mus(x, y, frame, color):
    print(C['clear'], end='')
    for i, line in enumerate(MUS[frame]):
        # Positionér musen
        row = y + i
        if row > 0:
            print(f"\033[{row};{x}H", end='')
            print(f"{C[color]}{C['bold']}{line}{C['end']}")
    # Hjerter omkring
    for _ in range(3):
        hx = random.randint(1, 80)
        hy = random.randint(1, 24)
        print(f"\033[{hy};{hx}H{random.choice(HEARTS)}")
    sys.stdout.flush()

def main():
    print(C['clear'] + C['cyan'] + C['bold'] + "🐭 KIMI MUSEN VÅGNER! 🐭" + C['end'])
    time.sleep(1)
    
    colors = ['pink', 'cyan', 'yellow', 'green', 'red', 'blue']
    
    try:
        while True:
            for i in range(10):
                x = random.randint(5, 60)
                y = random.randint(2, 18)
                frame = i % 3
                color = colors[i % len(colors)]
                draw_mus(x, y, frame, color)
                time.sleep(0.3)
            
            # Pause mellem løb
            print(C['clear'])
            print(f"\033[12;30H{C['pink']}{C['bold']}🐭 Kimi Musen sover... 💤{C['end']}")
            time.sleep(random.randint(3, 8))
            
    except KeyboardInterrupt:
        print(C['clear'])
        print(f"\033[12;25H{C['cyan']}{C['bold']}🐭 Kimi Musen siger hej! 💕{C['end']}")
        print(f"\033[14;20H{C['yellow']}Tryk Ctrl+C for at vække mig igen 🐭{C['end']}\n")

if __name__ == "__main__":
    main()
