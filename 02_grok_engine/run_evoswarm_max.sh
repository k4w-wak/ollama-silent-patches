#!/usr/bin/env bash
# EvoSwarm v2.2 MAX++ — MEGA MENU launcher
# Nu behøver du IKKE huske argumenter. Bare kør scriptet.
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -f .env ]; then
    echo "[FEJL] .env fil mangler. Kopier .env.example til .env og indsæt din OLLAMA_API_KEY."
    exit 1
fi

# Load all env vars from .env, but do NOT print them
set -a
source .env
set +a

if [ -z "${OLLAMA_API_KEY:-}" ]; then
    echo "[FEJL] OLLAMA_API_KEY ikke fundet i .env"
    exit 1
fi

# DING! 🔔
printf '\a'

# Farverig intro
printf '\033[?25h'
clear
echo -e "\033[1;36m"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     🤖 EvoSwarm v2.2 MAX++ — MEGA MENU                        ║"
echo "║     🌩️ Cloud · ⚡ Parallel · 🧠 Stateful · 🔧 Self-improving  ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "\033[0m"

# Hvis brugeren angiver argumenter, kør batch/CLI-mode stadig
if [ $# -gt 0 ]; then
    echo "▶ CLI mode: python3 evoswarm_v2_max.py $@"
    exec python3 evoswarm_v2_max.py "$@"
else
    echo "▶ MEGA MENU mode: Bare vælg et tal!"
    echo ""
    exec python3 evoswarm_v2_max.py
fi
