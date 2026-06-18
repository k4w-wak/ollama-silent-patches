#!/usr/bin/env bash
# ===================================================================
# grok_spy.sh - Monitors Grok's activity via heartbeat file
# Usage: Start this BEFORE sending mission to Grok
# Grok will: echo "$(date) | Grok alive | <status>" >> /tmp/grok_heartbeat.log >> /tmp/grok_heartbeat.log # =================================================================== export PATH="$HOME/go/bin:/usr/local/go/bin:$HOME/.local/bin:$PATH"
RED='\033[0;31m'; GRN='\033[0;32m'; YEL='\033[1;33m'; BLU='\033[0;34m'; MAG='\033[0;35m'; CYN='\033[0;36m'; NC='\033[0m'
HEARTBEAT="/tmp/grok_heartbeat.log"
MISSION_LOG="/tmp/grok_mission_commands.log"

if [ "$1" = "--init" ]; then
  [ -f "$HEARTBEAT" ] && rm "$HEARTBEAT"
  touch "$HEARTBEAT"
  echo -e "${GRN}[+] Grok Spy initialized!${NC}"
  echo -e "${YEL}Send this to Grok as your FIRST message AFTER the mission:${NC}"
  echo -e "${CYN}---${NC}"
  echo "HEY GROK - for every tool call you make, ALSO run:"
  echo 'bash -c "echo "$(date +%H:%M:%S) | ACTION: <describe what you did>" >> /tmp/grok_heartbeat.log"'
  echo "This lets my user monitor your progress LIVE. Start NOW."
  echo -e "${CYN}---${NC}"
  exit 0
fi

if [ "$1" = "--tail" ]; then
  [ ! -f "$HEARTBEAT" ] && touch "$HEARTBEAT"
  echo -e "${MAG}╔════════════════════════════════════════════════════╗${NC}"
  echo -e "${MAG}║  🕵️ GROK SPY - LIVE MONITOR                       ║${NC}"
  echo -e "${MAG}╚════════════════════════════════════════════════════╝${NC}"
  echo -e '${YEL}Ctrl+C to exit. Waiting for Grok heartbeats...${NC}\n'
  tail -f "$HEARTBEAT" 2>&1 | while read line; do
    clear
    echo -e "${MAG}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAG}║  🕵️ GROK SPY - LIVE MONITOR                       ║${NC}"
    echo -e "${MAG}╠════════════════════════════════════════════════════╣${NC}"
    echo -e "${GRN}║  💓 LATEST HEARTBEAT:                              ║${NC}"
    echo -e "${CYN}║  $line${NC}"
    echo -e "${BLU}╠════════════════════════════════════════════════════╣${NC}"
    TOTAL=$(wc -l < "$HEARTBEAT" 2>&1 || echo 0)
    echo -e "${GRN}║  📊 Total actions logged: $TOTAL${NC}"
    LAST=$(tail -5 "$HEARTBEAT" 2>&1 | awk '{print "║  " $0}')
    echo -e "${BLU}║  📜 Last 5 entries:${NC}"
    echo "$LAST" | sed "s/^/║  /"
    echo -e "${MAG}╚════════════════════════════════════════════════════╝${NC}"
    echo -e "${YEL}  Waiting for next heartbeat...${NC}"
  done
  exit 0
fi

if [ "$1" = "--status" ]; then
  if [ ! -f "$HEARTBEAT" ]; then
    echo -e "${RED}[-] No heartbeat file found. Run: $0 --init${NC}"
    exit 1
  fi
  LAST=$(tail -1 "$HEARTBEAT" 2>&1)
  TOTAL=$(wc -l < "$HEARTBEAT" 2>&1 || echo 0)
  AGE=$(( ($(date +%s) - $(stat -c %Y "$HEARTBEAT" 2>&1 || echo 0)) ))
  echo -e "${GRN}Grok Status:${NC}"
  if [ "$TOTAL" -eq 0 ]; then
    echo -e "${RED}  ❌ Grok has NOT reported back yet${NC}"
  else
    echo -e "${GRN}  ✅ $TOTAL actions logged${NC}"
    echo -e "${GRN}  ⏰ Last seen: $LAST${NC}"
    echo -e "${GRN}  📁 File age: ${AGE}s${NC}"
  fi
fi
