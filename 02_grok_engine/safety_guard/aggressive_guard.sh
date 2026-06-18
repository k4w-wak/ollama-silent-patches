#!/bin/bash
# ================================================================
# 🔥 GROK SAFETY GUARD — AGGRESSIVE NETWORK GUARD 🔥
# Blokerer trusler automatisk med iptables
# ================================================================

GUARD_DIR="$HOME/02_grok_engine/safety_guard"
BLOCK_LOG="$GUARD_DIR/logs/blocked_ips.log"
BLOCK_LIST="$GUARD_DIR/blocked_ips.txt"

mkdir -p "$GUARD_DIR/logs"
touch "$BLOCK_LIST"

RED='\033[91m'; GREEN='\033[92m'; YELLOW='\033[93m'; BOLD='\033[1m'; RESET='\033[0m'

log_block() {
    local ip="$1" reason="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] BLOCKED $ip — $reason" >> "$BLOCK_LOG"
    echo -e "${RED}${BOLD}🚫 BLOKERET: $ip — $reason${RESET}"
}

# Bloker en IP
block_ip() {
    local ip="$1"
    local reason="$2"
    
    # Tjek om allerede blokeret
    if grep -q "^$ip$" "$BLOCK_LIST" 2>/dev/null; then
        return
    fi
    
    # Bloker med iptables (kræver sudo)
    sudo iptables -A INPUT -s "$ip" -j DROP 2>/dev/null
    sudo iptables -A OUTPUT -d "$ip" -j DROP 2>/dev/null
    
    # Gem til liste
    echo "$ip" >> "$BLOCK_LIST"
    log_block "$ip" "$reason"
}

# Scan for port scan-angreb
detect_port_scan() {
    echo -e "\n${BOLD}🔍 Scanner for port scan-angreb...${RESET}"
    
    # Tjek for mange forbindelser fra samme IP (SYN flood / port scan)
    SUSPECT_IPS=$(ss -tnp state established 2>/dev/null | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn | head -10)
    
    echo "$SUSPECT_IPS" | while read count ip; do
        if [ -n "$count" ] && [ "$count" -gt 20 ] 2>/dev/null; then
            alert HIGH PORT_SCAN "IP $ip har $count forbindelser — muligt port scan!"
            block_ip "$ip" "Port scan detected ($count connections)"
        fi
    done
}

# Bloker kendte farlige IP'er
block_known_malicious() {
    echo -e "\n${BOLD}🧱 Blokerer kendte farlige IP-ranges...${RESET}"
    
    # Bloker kendte botnet/scanner ranges (eksempler)
    # Disse er velkendte scanners
    for range in "45.33.32.0/24" "45.33.34.0/24" "185.220.101.0/24"; do
        sudo iptables -A INPUT -s "$range" -j DROP 2>/dev/null
        echo "  🚫 Blokeret range: $range"
    done
}

# Tjek og bloker brute force
detect_bruteforce() {
    echo -e "\n${BOLD}🔐 Tjekker for brute force-angreb...${RESET}"
    
    # SSH brute force
    if [ -f /var/log/auth.log ]; then
        ATTACKERS=$(grep "Failed password" /var/log/auth.log 2>/dev/null | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -5)
        echo "$ATTACKERS" | while read count ip; do
            if [ -n "$count" ] && [ "$count" -gt 10 ] 2>/dev/null; then
                alert CRITICAL BRUTE_FORCE "SSH brute force fra $ip ($count forsøg)"
                block_ip "$ip" "SSH brute force ($count attempts)"
            fi
        done
    fi
}

# Vis blokerings-status
show_status() {
    echo -e "\n${BOLD}📊 SAFETY GUARD STATUS${RESET}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    BLOCKED=$(wc -l < "$BLOCK_LIST" 2>/dev/null || echo 0)
    echo -e "  🚫 Blokerede IP'er: ${RED}$BLOCKED${RESET}"
    
    if [ -f "$BLOCK_LOG" ]; then
        BLOCK_TODAY=$(grep "$(date +%Y-%m-%d)" "$BLOCK_LOG" | wc -l)
        echo -e "  📋 Blokeret i dag: ${YELLOW}$BLOCK_TODAY${RESET}"
    fi
    
    # Vis iptables DROP regler
    DROP_COUNT=$(sudo iptables -L INPUT 2>/dev/null | grep -c DROP || echo 0)
    echo -e "  🧱 Firewall DROP regler: ${CYAN}$DROP_COUNT${RESET}"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ================================================================
# MAIN
# ================================================================

case "${1:-run}" in
    run)
        echo -e "${BOLD}${RED}══════════════════════════════════════════════════════${RESET}"
        echo -e "${BOLD}${RED}  🔥 GROK SAFETY GUARD — AGGRESSIVE MODE 🔥${RESET}"
        echo -e "${BOLD}${RED}══════════════════════════════════════════════════════${RESET}"
        
        detect_port_scan
        detect_bruteforce
        show_status
        ;;
    
    block)
        # Bloker specifik IP
        if [ -n "$2" ]; then
            block_ip "$2" "${3:-Manual block}"
        fi
        ;;
    
    unblock)
        # Fjern blokering
        if [ -n "$2" ]; then
            sudo iptables -D INPUT -s "$2" -j DROP 2>/dev/null
            sudo iptables -D OUTPUT -d "$2" -j DROP 2>/dev/null
            sed -i "/^$2$/d" "$BLOCK_LIST" 2>/dev/null
            echo -e "${GREEN}✅ Afblokeret: $2${RESET}"
        fi
        ;;
    
    status)
        show_status
        ;;
    
    list)
        echo -e "\n${BOLD}🚫 Blokerede IP'er:${RESET}"
        cat "$BLOCK_LIST" 2>/dev/null | while read ip; do
            echo -e "  ${RED}$ip${RESET}"
        done
        ;;
    
    *)
        echo "Brug: $0 {run|block IP|unblock IP|status|list}"
        ;;
esac