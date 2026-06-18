#!/bin/bash
# ================================================================
# 🔥 GROK SAFETY GUARD — REAL-TID KONTINUERLIG OVERVÅGNING 🔥
# Kører hvert X sekund og alarmerer ved TRUSLER
# Brug: ./realtime_guard.sh [sekunder_mellem_scans]
# ================================================================

GUARD_DIR="$HOME/02_grok_engine/safety_guard"
ALERT_LOG="$GUARD_DIR/logs/realtime_$(date +%Y%m%d).log"
PREV_IP=""
PREV_PORTS=""

mkdir -p "$GUARD_DIR/logs"

RED='\033[91m'; GREEN='\033[92m'; YELLOW='\033[93m'; BOLD='\033[1m'; RESET='\033[0m'

INTERVAL=${1:-30}  # Default 30 sekunder

# Gem baseline
save_baseline() {
    ss -tlnp 2>/dev/null | grep LISTEN > "$GUARD_DIR/snapshots/ports_baseline.txt" 2>/dev/null
    ps aux > "$GUARD_DIR/snapshots/processes_baseline.txt" 2>/dev/null
    echo "$(date +%s)" > "$GUARD_DIR/snapshots/last_scan.txt"
}

alert_realtime() {
    local level="$1" category="$2" msg="$3"
    local ts=$(date '+%H:%M:%S')
    echo "[$ts] [$level] [$category] $msg" >> "$ALERT_LOG"
    
    case $level in
        CRITICAL) echo -e "${RED}${BOLD}🚨[$ts] $category: $msg${RESET}" ;;
        HIGH)     echo -e "${YELLOW}${BOLD}⚠️[$ts] $category: $msg${RESET}" ;;
        MEDIUM)   echo -e "${YELLOW}⚡[$ts] $category: $msg${RESET}" ;;
        *)        echo -e "📋[$ts] $category: $msg" ;;
    esac
}

# Hurtig realtids-check
quick_check() {
    # 1. IP-ændring
    CURRENT_IP=$(curl -s --max-time 3 ifconfig.me 2>/dev/null)
    if [ -n "$CURRENT_IP" ]; then
        if [ -n "$PREV_IP" ] && [ "$CURRENT_IP" != "$PREV_IP" ]; then
            alert_realtime CRITICAL IP_CHANGE "IP ÆNDRET fra $PREV_IP til $CURRENT_IP"
        fi
        PREV_IP="$CURRENT_IP"
    fi
    
    # 2. Nye porte åbnet
    CURRENT_PORTS=$(ss -tlnp 2>/dev/null | grep LISTEN | awk '{print $4}' | sort)
    if [ -n "$PREV_PORTS" ] && [ "$CURRENT_PORTS" != "$PREV_PORTS" ]; then
        NEW_PORTS=$(diff <(echo "$PREV_PORTS") <(echo "$CURRENT_PORTS") 2>/dev/null | grep ">" | awk '{print $2}')
        if [ -n "$NEW_PORTS" ]; then
            alert_realtime HIGH NEW_PORT "NYE PORTE ÅBNET: $NEW_PORTS"
        fi
    fi
    PREV_PORTS="$CURRENT_PORTS"
    
    # 3. Reverse shell check (hurtig)
    REVERSE=$(ps aux 2>/dev/null | grep -iE '/dev/tcp|nc.*-e|python.*socket.*connect' | grep -v grep | head -3)
    if [ -n "$REVERSE" ]; then
        alert_realtime CRITICAL REVERSE_SHELL "REVERSE SHELL: $REVERSE"
    fi
    
    # 4. Cryptominer check
    MINER=$(ps aux 2>/dev/null | grep -iE 'xmrig|minerd|cpuminer|stratum' | grep -v grep | head -1)
    if [ -n "$MINER" ]; then
        alert_realtime CRITICAL CRYPTOMINER "CRYPTOMINER: $MINER"
    fi
    
    # 5. Mistænkelige forbindelser til farlige porte
    for port in 4444 5555 6666 31337; do
        CONN=$(ss -tnp 2>/dev/null | grep ":$port" | head -1)
        if [ -n "$CONN" ]; then
            alert_realtime CRITICAL SUSPICIOUS_CONN "Forbindelse på port $port: $CONN"
        fi
    done
    
    # 6. Fil-ændringer i kritiske filer (hurtig check)
    for file in /etc/passwd /etc/shadow /etc/sudoers; do
        if [ -f "$file" ]; then
            MTIME=$(stat -c %Y "$file" 2>/dev/null)
            NOW=$(date +%s)
            AGE=$((NOW - MTIME))
            if [ "$AGE" -lt 60 ]; then
                alert_realtime HIGH FILE_CHANGE "NETOP ÆNDRET: $file (for $AGE sekunder siden)"
            fi
        fi
    done
    
    # 7. SSH login check
    RECENT_SSH=$(journalctl -u sshd --since "1 min ago" 2>/dev/null | grep -iE "failed|accepted" | head -3)
    if [ -n "$RECENT_SSH" ]; then
        alert_realtime MEDIUM SSH "SSH-aktivitet: $RECENT_SSH"
    fi
}

# ================================================================
# MAIN LOOP
# ================================================================

echo -e "${BOLD}${RED}══════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${RED}  🔥 GROK SAFETY GUARD — REAL-TID OVERVÅGNING 🔥${RESET}"
echo -e "${BOLD}${RED}══════════════════════════════════════════════════════${RESET}"
echo -e "  Scan-interval: ${INTERVAL}s"
echo -e "  Log: $ALERT_LOG"
echo -e "  Tryk Ctrl+C for at stoppe\n"

save_baseline

CYCLE=0
while true; do
    CYCLE=$((CYCLE + 1))
    echo -e "\n${GREEN}━━━ Scan #$CYCLE ┃ $(date '+%H:%M:%S') ━━━${RESET}"
    quick_check
    sleep "$INTERVAL"
done