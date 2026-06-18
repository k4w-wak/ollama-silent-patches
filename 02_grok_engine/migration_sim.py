#!/usr/bin/env python3
"""5. MIGRERING SIMULATOR — WSL → Pop!_OS"""
import sys, time, random

colors = ['\033[91m', '\033[93m', '\033[92m', '\033[96m', '\033[94m', '\033[95m']
reset = '\033[0m'

files = [
    ".bashrc", ".zshrc", ".ssh/id_rsa", ".ssh/config",
    "projects/grok_engine", "projects/bugbounty",
    ".config/nvim/init.vim", ".config/kitty/kitty.conf",
    "Downloads/tools", "Documents/rapport",
    ".local/share/fish", ".gnupg", ".aws/credentials"
]

print("\033[2J\033[H", end='')
print(f"{' '*22}🐭 WSL → Pop!_OS MIGRERING 🐭\n")
print(f"  {colors[3]}Fra:{reset}    /mnt/c/Windows/... (WSL2)")
print(f"  {colors[2]}Til:{reset}     ~/ (Pop!_OS)\n")

for i, f in enumerate(files):
    pct = int((i+1) / len(files) * 100)
    speed = random.uniform(0.2, 0.8)
    color = colors[i % len(colors)]
    sys.stdout.write(f"\r  {color}[{pct:3d}%]{reset} 📁 Kopierer: {f} ... ")
    sys.stdout.flush()
    time.sleep(speed)
    sys.stdout.write(f"{colors[2]}✅{reset}\n")

print(f"\n  {colors[4]}{'='*50}{reset}")
print(f"  {colors[2]}🎉 MIGRERING FÆRDIG! {colors[4]}100%{reset}")
print(f"  {colors[3]}🐭 WSL kan nu tage en lang velfortjent pause... 💤{reset}")
print(f"  {colors[5]}🚀 Pop!_OS er din nye hjem! 💕{reset}\n")
