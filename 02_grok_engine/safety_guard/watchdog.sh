#!/bin/bash
# ================================================================
# 🔥 GROK SAFETY GUARD — WATCHDOG SCRIPT 🔥
# Kører kontinuerligt og alarmerer ved enhver trussel
# ================================================================

GUARD_DIR="$HOME/02_grok_engine/safety_guard"
LOG_DIR="$GUARD_DIR/logs"
ALERT_DIR="$GUARD_DIR/alerts"
ALERT_LOG="$LOG_DIR/watchdog_$(date +%Y%m%d).log"

mkdir -p "$LOG_DIR" "$ALERT_DIR"

RED='\033[91m'
GREEN='\033[92m'
YELLOW='\033[93m'
CYAN='\033[96m'
BOLD='\033[1m'
RESET='\033[0m'

alert() {
    local level="$1"
    local category="$2"
    local message="$3"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] [$level] [$category] $message" >> "$ALERT_LOG"
    
    case $level in
        CRITICAL) echo -e "${RED}${BOLD}🚨 [$level] $category: $message${RESET}" ;;
        HIGH)      echo -e "${YELLOW}${BOLD}⚠️  [$level] $category: $message${RESET}" ;;
        MEDIUM)    echo -e "${CYAN}⚡ [$level] $category: $message${RESET}" ;;
        LOW)       echo -e "${GREEN}📋 [$level] $category: $message${RESET}" ;;
        *)         echo "ℹ️  [$level] $category: $message" ;;
    esac
}

# ================================================================
# REAL-TID NETVÆRKSOVERVÅGNING
# ================================================================

monitor_network() {
    echo -e "\n${BOLD}📡 NETVÆRKSOVERVÅGNING${RESET}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Tjek offentlig IP
    CURRENT_IP=$(curl -s --max-time 5 ifconfig.me 2>/dev/null)
    KNOWN_IP="<REDACTED_IP>"
    if [ -n "$CURRENT_IP" ]; then
        if [ "$CURRENT_IP" != "$KNOWN_IP" ]; then
            alert CRITICAL IP_CHANGE "OFFENTLIG IP ÆNDRING! Forventet: $KNOWN_IP, Aktuel: $CURRENT_IP"
        else
            alert INFO IP "Offentlig IP OK: $CURRENT_IP"
        fi
    fi
    
    # Tjek lyttende porte
    LISTENING=$(ss -tlnp 2>/dev/null | grep LISTEN | wc -l)
    if [ "$LISTENING" -gt 20 ]; then
        alert HIGH PORTS "Mange lyttende porte: $LISTENING"
    else
        alert INFO PORTS "Lyttende porte: $LISTENING"
    fi
    
    # Tjek for mistænkelige forbindelser
    SUSPICIOUS_PORTS="4444 5555 6666 6667 8888 9999 1234 31337"
    for port in $SUSPICIOUS_PORTS; do
        CONN=$(ss -tnp 2>/dev/null | grep ":$port" | head -1)
        if [ -n "$CONN" ]; then
            alert CRITICAL SUSPICIOUS_PORT "MISTÆNKELIG PORT $port AKTIV: $CONN"
        fi
    done
    
    # Tjek etablerede forbindelser til mistænkelige IP'er
    ESTABLISHED=$(ss -tnp state established 2>/dev/null | grep -v "127.0.0.1")
    CONN_COUNT=$(echo "$ESTABLISHED" | grep -c "^[0-9]")
    alert INFO CONNECTIONS "Etablerede forbindelser: $CONN_COUNT"
    
    # ARP-tabel
    ARP_COUNT=$(arp -an 2>/dev/null | wc -l)
    if [ "$ARP_COUNT" -gt 15 ]; then
        alert MEDIUM ARP "Mange ARP-entries: $ARP_COUNT — muligt ARP spoofing"
    fi
}

# ================================================================
# PROCES-OVERVÅGNING
# ================================================================

monitor_processes() {
    echo -e "\n${BOLD}⚙️ PROCESOVERVÅGNING${RESET}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Reverse shells
    REVERSE_SHELL=$(ps aux 2>/dev/null | grep -iE '/dev/tcp|nc.*-e|bash.*-i >& /dev|python.*socket.*connect|perl.*socket|socat.*exec|pwncat' | grep -v grep)
    if [ -n "$REVERSE_SHELL" ]; then
        alert CRITICAL REVERSE_SHELL "REVERSE SHELL DETEKTERET: $REVERSE_SHELL"
    fi
    
    # Cryptominers
    CRYPTOMINER=$(ps aux 2>/dev/null | grep -iE 'xmrig|minerd|cpuminer|cryptonight|stratum+tcp' | grep -v grep)
    if [ -n "$CRYPTOMINER" ]; then
        alert CRITICAL CRYPTOMINER "CRYPTOMINER DETEKTERET: $CRYPTOMINER"
    fi
    
    # Mistænkelige processer
    for proc in ncat netcat hydra medusa john aircrack ettercap bettercap responder crackmapexec; do
        if pgrep -x "$proc" >/dev/null 2>&1; then
            alert HIGH SUSPICIOUS_PROC "Mistenkelig proces kører: $proc"
        fi
    done
    
    # CPU-intensive processer (mulig minage)
    HIGH_CPU=$(ps aux --sort=-%cpu 2>/dev/null | head -5 | grep -v "PID")
    alert INFO CPU "Top CPU processer: $(echo "$HIGH_CPU" | head -3 | awk '{print $11, $3"%"}')"
}

# ================================================================
# FILOVERVÅGNING
# ================================================================

monitor_files() {
    echo -e "\n${BOLD}📁 FILOVERVÅGNING${RESET}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Kritiske systemfiler
    for file in /etc/passwd /etc/shadow /etc/hosts /etc/resolv.conf /etc/ssh/sshd_config /etc/sudoers; do
        if [ -f "$file" ]; then
            MTIME=$(stat -c %Y "$file" 2>/dev/null)
            NOW=$(date +%s)
            AGE=$((NOW - MTIME))
            if [ "$AGE" -lt 3600 ]; then
                alert HIGH FILE_CHANGE "Nyligt ændret (inden for 1 time): $file"
            fi
        fi
    done
    
    # SSH authorized_keys
    AUTH_KEYS="$HOME/.ssh/authorized_keys"
    if [ -f "$AUTH_KEYS" ]; then
        KEY_COUNT=$(wc -l < "$AUTH_KEYS")
        if [ "$KEY_COUNT" -gt 5 ]; then
            alert MEDIUM SSH_KEYS "$KEY_COUNT SSH-nøgler i authorized_keys"
        fi
    fi
    
    # Nye skjulte filer
    HIDDEN_FILES=$(find "$HOME" -name ".*" -mtime -1 -type f 2>/dev/null | head -10)
    if [ -n "$HIDDEN_FILES" ]; then
        alert MEDIUM HIDDEN_FILES "Nye skjulte filer: $(echo "$HIDDEN_FILES" | tr '\n' ' ')"
    fi
    
    # SUID filer (privilege escalation)
    SUID_FILES=$(find /usr/bin /usr/sbin /usr/local/bin -perm -4000 -type f 2>/dev/null | head -5)
    alert INFO SUID "SUID-filer fundet: $(echo "$SUID_FILES" | wc -l) stk"
}

# ================================================================
# SYSTEMOVERVÅGNING
# ================================================================

monitor_system() {
    echo -e "\n${BOLD}🖥️ SYSTEMOVERVÅGNING${RESET}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Disk
    DISK_PCT=$(df -h / | tail -1 | awk '{print $5}' | tr -d '%')
    if [ "$DISK_PCT" -gt 90 ]; then
        alert CRITICAL DISK "Disk er ${DISK_PCT}% fuld!"
    elif [ "$DISK_PCT" -gt 80 ]; then
        alert MEDIUM DISK "Disk er ${DISK_PCT}% fuld"
    else
        alert INFO DISK "Disk: ${DISK_PCT}% brugt"
    fi
    
    # Memory
    MEM_PCT=$(free | grep Mem | awk '{printf "%.0f", ($3/$2)*100}')
    if [ "$MEM_PCT" -gt 90 ]; then
        alert HIGH MEMORY "Hukommelse ${MEM_PCT}% brugt!"
    else
        alert INFO MEMORY "Hukommelse: ${MEM_PCT}% brugt"
    fi
    
    # Load
    LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
    alert INFO LOAD "System load: $LOAD"
    
    # Login-forsøg
    FAILED_LOGINS=$(lastb 2>/dev/null | wc -l)
    if [ "$FAILED_LOGINS" -gt 50 ]; then
        alert HIGH BRUTE_FORCE "$FAILED_LOGINS mislykkede login-forsøg!"
    else
        alert INFO LOGINS "Mislykkede logins: $FAILED_LOGINS"
    fi
}

# ================================================================
# HOVEDMÅL
# ================================================================

echo -e "\n${BOLD}${RED}════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${RED}    🔥 GROK SAFETY GUARD — WATCHDOG MODE 🔥${RESET}"
echo -e "${BOLD}${RED}════════════════════════════════════════════════════════════${RESET}"
echo -e "  Tidspunkt: $(date '+%Y-%m-%d %H:%M:%S')"
echo -e "  IP: <REDACTED_IP> (DK/TDC)"
echo -e "  Host: $(hostname)"
echo ""

monitor_network
monitor_processes
monitor_files
monitor_system

echo ""
echo -e "${BOLD}════════════════════════════════════════════════════════════${RESET}"

# Tæl trusler
if [ -f "$ALERT_LOG" ]; then
    CRITICALS=$(grep -c "\[CRITICAL\]" "$ALERT_LOG" 2>/dev/null || echo 0)
    HIGHS=$(grep -c "\[HIGH\]" "$ALERT_LOG" 2>/dev/null || echo 0)
    echo -e "  ${RED}🔴 KRITISKE: $CRITICALS${RESET}"
    echo -e "  ${YELLOW}🟠 HOJE: $HIGHS${RESET}"
    
    if [ "$CRITICALS" -gt 0 ]; then
        echo -e "\n  ${RED}${BOLD}🚨🚨🚨 ALARM — KRITISKE TRUSLER DETEKTERET! 🚨🚨🚨${RESET}"
    elif [ "$HIGHS" -gt 0 ]; then
        echo -e "\n  ${YELLOW}${BOLD}⚠️  HOJE TRUSLER DETEKTERET — UNDERSØG STRAKS!${RESET}"
    else
        echo -e "\n  ${GREEN}✅ System ser rent ud${RESET}"
    fi
fi

echo -e "${BOLD}════════════════════════════════════════════════════════════${RESET}"