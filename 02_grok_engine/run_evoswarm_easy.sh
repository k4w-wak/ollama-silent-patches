#!/usr/bin/env bash
# EvoSwarm EASY — start den brugervenlige menu
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -f .env ]; then
    echo "[FEJL] .env fil mangler. Kopier .env.example til .env og indsæt din OLLAMA_API_KEY."
    echo "Tip: cp .env.example .env"
    exit 1
fi

# Load env vars quietly
set -a
source .env
set +a

if [ -z "${OLLAMA_API_KEY:-}" ]; then
    echo "[FEJL] OLLAMA_API_KEY ikke fundet i .env"
    exit 1
fi

# Terminal bell + blink før start
printf '\a'
for i in 1 2 3; do
    tput blink || true
    printf '\e[5m🚀 EvoSwarm EASY starter...\e[0m\r'
    sleep 0.2
    printf '                     \r'
    sleep 0.2
done

python3 evoswarm_easy.py
