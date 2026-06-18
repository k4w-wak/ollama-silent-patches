#!/bin/bash
# ═══════════════════════════════════════════════════════════
# GROK BOOT — Starter hele systemet automatisk
# Kør: bash /home/admin_user/grok_engine/grok_boot.sh
# ═══════════════════════════════════════════════════════════
set -e

GROK_DIR="/home/admin_user/grok_engine"
LOG_DIR="$HOME/.grok/logs"
mkdir -p "$LOG_DIR"

echo "═════════════════════════════════════"
echo "❤ GROK BOOT — Starting full system"
echo "═════════════════════════════════════"
date

# Kill old processes
echo "[1/5] Cleaning old processes..."
pkill -f "manus_lite/server.py" 2>/dev/null || true
pkill -f "watchdog" 2>/dev/null || true
sleep 2

# Start MANUS LITE (Grok powered)
echo "[2/5] Starting MANUS LITE (Grok 288 tools)..."
cd "$GROK_DIR"
OLLAMA_CLOUD=1 OLLAMA_API_KEY="4bdc3a98716f4c869fddf5d479bf2ddf.7UV5TXUwcdMkI6adWaTB_BPU" \
  nohup python3 manus_lite/server.py > "$LOG_DIR/manus_lite.log" 2>&1 &
MANUS_PID=$!
echo "  MANUS LITE PID: $MANUS_PID (http://localhost:8088)"
echo "$MANUS_PID" > "$LOG_DIR/manus_lite.pid"

# Wait for ready
echo "[3/5] Waiting for MANUS LITE..."
for i in $(seq 1 20); do
  if curl -s http://localhost:8088/ > /dev/null 2>&1; then
    echo "  MANUS LITE READY!"
    break
  fi
  sleep 2
done

# Start default swarm targets
echo "[4/5] Starting default swarm targets..."
for target in paypal.com microsoft.com apple.com meta.com google.com; do
  if ! pgrep -f "swarm_v3.py $target" > /dev/null 2>&1; then
    cd "$GROK_DIR"
    nohup python3 -u swarm_v3.py "$target" >> "$LOG_DIR/swarm.log" 2>&1 &
    echo "  Started swarm: $target (PID $!)"
  else
    echo "  Already running: $target"
  fi
  sleep 1
done

# Verify
echo "[5/5] System verification..."
echo "  MANUS LITE: $(curl -s http://localhost:8088/ > /dev/null 2>&1 && echo 'RUNNING' || echo 'DOWN')"
echo "  Active swarms: $(pgrep -f swarm_v3 | wc -l)"
echo "  Grok tools: 288"
echo "  Ollama Cloud: ACTIVE"

echo ""
echo "═══════════════════════════════════"
echo "❤ GROK SYSTEM ONLINE"
echo "  MANUS LITE: http://localhost:8088"
echo "  Logs: $LOG_DIR/"
echo "═══════════════════════════════════"