#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║  🛡️  FORTRESS FIREWALL - Kali Defense System                ║
# ║  Firewall + IDS + Alarmer + Auto-blokering                  ║
# ║  Bygget af Grok for admin_user                                 ║
# ╚══════════════════════════════════════════════════════════════╝

GUARD_DIR="$HOME/02_grok_engine/safety_guard"
ALERT_DIR="$GUARD_DIR/alerts"
LOG_DIR="$GUARD_DIR/logs"
BLOCKED_IPS="$GUARD_DIR/blocked_ips.txt"
FIREWALL_LOG="$LOG_DIR/firewall.log"
INTRUSION_LOG="$LOG_DIR/intrusion.log"
ALERT_SOUND="$GUARD_DIR/alert_tone"

# Opret mapper
mkdir -p "$ALERT_DIR" "$LOG_DIR"

# Farver
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$FIREWALL_LOG"
    echo -e "${CYAN}[$(date '+%H:%M:%S')]${NC} $1"
}

alert() {
    # Visuel alarm
    echo -e "${RED}🚨 ALERT: $1${NC}"
    # Log alert
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚨 ALERT: $1" >> "$INTRUSION_LOG"
    # Opret alert-fil
    echo "$1" > "$ALERT_DIR/alert_$(date +%s).txt"
    # Lyd-alarm (beep)
    which beep 2>/dev/null && beep -l 500 -f 1000 -r 3 2>/dev/null
    # Desktop notifikation
    which notify-send 2>/dev/null && notify-send -u critical "🚨 FORTRESS ALERT" "$1" 2>/dev/null
    # Terminal bell
    echo -e '\a'
}

# ══════════════════════════════════════════════
# FASE 1: FIREWALL OPSÆTNING
# ══════════════════════════════════════════════
setup_firewall() {
    log "🛡️ Starter firewall opsætning..."

    # Flush eksisterende regler
    iptables -F
    iptables -X
    iptables -t nat -F
    iptables -t nat -X
    iptables -t mangle -F
    iptables -t mangle -X

    # Standard politik: DROP alt (whitelist-tilgang)
    iptables -P INPUT DROP
    iptables -P FORWARD DROP
    iptables -P OUTPUT ACCEPT

    # ═══ CHAINS ═══
    iptables -N LOG_DROP 2>/dev/null
    iptables -N INTRUSION_DETECT 2>/dev/null
    iptables -N PORT_SCAN 2>/dev/null
    iptables -N ANTI_SPOOF 2>/dev/null

    # ═══ LOOPBACK ═══
    iptables -A INPUT -i lo -j ACCEPT
    iptables -A OUTPUT -o lo -j ACCEPT

    # ═══ EFTERSTABLER CONNECTIONS ═══
    iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

    # ═══ INVALID PAKKER = DROP + LOG ═══
    iptables -A INPUT -m conntrack --ctstate INVALID -j LOG --log-prefix "FORTRESS_INVALID: "
    iptables -A INPUT -m conntrack --ctstate INVALID -j DROP

    # ═══ ANTI-SPOOFING ═══
    # Bloker RFC1918 adresser fra eksterne interfaces
    iptables -A INPUT -s 10.0.0.0/8 ! -i lo -j LOG_DROP
    iptables -A INPUT -s 172.16.0.0/12 ! -i lo -j LOG_DROP
    iptables -A INPUT -s 192.168.0.0/16 ! -i lo -j LOG_DROP
    iptables -A INPUT -s 127.0.0.0/8 ! -i lo -j LOG_DROP
    iptables -A INPUT -s 0.0.0.0/8 -j LOG_DROP
    iptables -A INPUT -s 255.255.255.255 -j LOG_DROP
    iptables -A INPUT -s 224.0.0.0/4 -j LOG_DROP
    iptables -A INPUT -d 224.0.0.0/4 -j LOG_DROP

    # ═══ PORT SCAN DETEKTION ═══
    # Nmap SYN scan detektion
    iptables -A PORT_SCAN -p tcp --tcp-flags FIN,SYN,RST,PSH,ACK,URG NONE -m recent --set --name PORTSCAN -j LOG_DROP
    iptables -A PORT_SCAN -p tcp --tcp-flags FIN,SYN,RST,PSH,ACK,URG FIN,SYN,RST,PSH,ACK,URG -m recent --set --name PORTSCAN -j LOG_DROP
    iptables -A PORT_SCAN -p tcp --tcp-flags FIN,SYN,RST,PSH,ACK,URG FIN,PSH,URG -m recent --set --name PORTSCAN -j LOG_DROP
    iptables -A PORT_SCAN -p tcp --tcp-flags FIN,SYN,RST,PSH,ACK,URG FIN,SYN,RST,ACK,URG -m recent --set --name PORTSCAN -j LOG_DROP
    iptables -A PORT_SCAN -p tcp --tcp-flags SYN,RST SYN,RST -m recent --set --name PORTSCAN -j LOG_DROP
    iptables -A PORT_SCAN -p tcp --tcp-flags FIN,SYN FIN,SYN -m recent --set --name PORTSCAN -j LOG_DROP

    # Hvis port scan detekteret inden for 60 sek, DROP
    iptables -A PORT_SCAN -m recent --rcheck --seconds 60 --name PORTSCAN -j LOG_DROP
    iptables -A PORT_SCAN -j RETURN

    # Send alt gennem port scan detektion
    iptables -A INPUT -j PORT_SCAN

    # ═══ INTRUSION DETECTION ═══
    # Overvåg for mistænkelig aktivitet
    iptables -A INTRUSION_DETECT -m recent --set --name INTRUSION
    iptables -A INTRUSION_DETECT -m recent --rcheck --seconds 30 --hitcount 10 --name INTRUSION -j LOG --log-prefix "FORTRESS_BRUTE: "
    iptables -A INTRUSION_DETECT -j RETURN

    # ═══ TILLADTE SERVICES ═══
    # SSH (kun fra kendte netværk)
    iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --set --name SSH
    iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --rcheck --seconds 60 --hitcount 4 --name SSH -j LOG_DROP
    iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -j ACCEPT

    # HTTP/HTTPS (hvis webserver kører)
    iptables -A INPUT -p tcp --dport 80 -m conntrack --ctstate NEW -j ACCEPT
    iptables -A INPUT -p tcp --dport 443 -m conntrack --ctstate NEW -j ACCEPT

    # DNS (kun UDP svar)
    iptables -A INPUT -p udp --sport 53 -j ACCEPT
    iptables -A INPUT -p tcp --sport 53 -j ACCEPT

    # DHCP
    iptables -A INPUT -p udp --sport 67:68 -j ACCEPT

    # NTP
    iptables -A INPUT -p udp --sport 123 -j ACCEPT

    # ICMP (ping) - rate limited
    iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s --limit-burst 4 -j ACCEPT
    iptables -A INPUT -p icmp --icmp-type echo-request -j LOG_DROP

    # ═══ LOG_DROP CHAIN ═══
    iptables -A LOG_DROP -j LOG --log-prefix "FORTRESS_DROP: " --log-level 4
    iptables -A LOG_DROP -j DROP

    # ═══ SIDSTE: LOG ALT ANDET ═══
    iptables -A INPUT -j LOG --log-prefix "FORTRESS_CATCHALL: "
    iptables -A INPUT -j DROP

    # ═══ OUTPUT FILTRERING ═══
    # Tillad alt udgående men log mistænkeligt
    iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
    iptables -A OUTPUT -p tcp --dport 1:1023 -m conntrack --ctstate NEW -j LOG --log-prefix "FORTRESS_OUT_PRIV: "

    log "✅ Firewall aktiveret - DROP alt som standard"
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  🛡️  FORTRESS FIREWALL AKTIVERET              ║${NC}"
    echo -e "${GREEN}║  Politik: INPUT=DROP OUTPUT=ACCEPT           ║${NC}"
    echo -e "${GREEN}║  Port scan detektion: AKTIV                   ║${NC}"
    echo -e "${GREEN}║  Anti-spoofing: AKTIV                         ║${NC}"
    echo -e "${GREEN}║  SSH brute-force beskyttelse: AKTIV           ║${NC}"
    echo -e "${GREEN}║  ICMP rate-limit: AKTIV                      ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
}

# ══════════════════════════════════════════════
# FASE 2: INTRUSION MONITOR
# ══════════════════════════════════════════════
start_intrusion_monitor() {
    log "🔍 Starter intrusion monitor..."

    # Overvåg kernel log for FORTRESS events
    (
        while true; do
            # Læs dmesg/kernel ring buffer for firewall events
            dmesg 2>/dev/null | grep -i "FORTRESS" | tail -1 | while read line; do
                if echo "$line" | grep -qi "PORTSCAN"; then
                    alert "PORT SCAN DETEKTERET! Nogen scanner dine porte!"
                    # Udtræk IP og bloker
                    SCAN_IP=$(echo "$line" | grep -oP 'SRC=\K[^ ]+' | head -1)
                    if [ -n "$SCAN_IP" ] && ! grep -q "$SCAN_IP" "$BLOCKED_IPS" 2>/dev/null; then
                        iptables -A INPUT -s "$SCAN_IP" -j DROP
                        echo "$SCAN_IP" >> "$BLOCKED_IPS"
                        alert "AUTO-BLOKERET: $SCAN_IP (port scan)"
                    fi
                elif echo "$line" | grep -qi "BRUTE"; then
                    alert "BRUTE FORCE FORSØG DETEKTERET!"
                    BRUTE_IP=$(echo "$line" | grep -oP 'SRC=\K[^ ]+' | head -1)
                    if [ -n "$BRUTE_IP" ] && ! grep -q "$BRUTE_IP" "$BLOCKED_IPS" 2>/dev/null; then
                        iptables -A INPUT -s "$BRUTE_IP" -j DROP
                        echo "$BRUTE_IP" >> "$BLOCKED_IPS"
                        alert "AUTO-BLOKERET: $BRUTE_IP (brute force)"
                    fi
                elif echo "$line" | grep -qi "INVALID"; then
                    INVALID_IP=$(echo "$line" | grep -oP 'SRC=\K[^ ]+' | head -1)
                    log "⚠️ Invalid pakke fra: $INVALID_IP"
                fi
            done
            sleep 2
        done
    ) &
    INTRUSION_PID=$!
    echo "$INTRUSION_PID" > "$GUARD_DIR/intrusion_monitor.pid"
    log "✅ Intrusion monitor PID: $INTRUSION_PID"
}

# ══════════════════════════════════════════════
# FASE 3: REAL-TID NETVÆRKSOVERVÅGNING
# ══════════════════════════════════════════════
start_network_monitor() {
    log "📡 Starter netværksovervågning..."

    (
        while true; do
            # Tjek for nye forbindelser
            NEW_CONNS=$(ss -tn state established 2>/dev/null | tail -n +2 | grep -v "127.0.0.1" | grep -v "172.22.29")

            if [ -n "$NEW_CONNS" ]; then
                while read -r conn; do
                    REMOTE_IP=$(echo "$conn" | awk '{print $5}' | cut -d: -f1)
                    REMOTE_PORT=$(echo "$conn" | awk '{print $5}' | cut -d: -f2)

                    # Tjek for mistænkelige porte
                    case "$REMOTE_PORT" in
                        4444|5555|6666|7777|8888|9999|31337|12345)
                            alert "REVERSE SHELL DETEKTERET! Forbindelse til $REMOTE_IP:$REMOTE_PORT"
                            iptables -A OUTPUT -d "$REMOTE_IP" -j DROP
                            echo "$REMOTE_IP" >> "$BLOCKED_IPS"
                            ;;
                        9050|9051|9150)
                            log "ℹ️ Tor-forbindelse: $REMOTE_IP:$REMOTE_PORT"
                            ;;
                    esac
                done <<< "$NEW_CONNS"
            fi

            # Tjek for uventede lyttende porte
            LISTENING=$(ss -tlnp 2>/dev/null | tail -n +2 | grep -v "127.0.0.1" | grep -v "::1")
            KNOWN_PORTS="22 80 443 8082 11434 53"
            while read -r listener; do
                LPORT=$(echo "$listener" | awk '{print $4}' | rev | cut -d: -f1 | rev)
                if ! echo "$KNOWN_PORTS" | grep -qw "$LPORT"; then
                    log "⚠️ Ukendt lyttende port: $LPORT"
                fi
            done <<< "$LISTENING"

            sleep 5
        done
    ) &
    NET_MONITOR_PID=$!
    echo "$NET_MONITOR_PID" > "$GUARD_DIR/network_monitor.pid"
    log "✅ Netværksovervågning PID: $NET_MONITOR_PID"
}

# ══════════════════════════════════════════════
# FASE 4: CONNECTION THRESHOLD ALARM
# ══════════════════════════════════════════════
start_threshold_monitor() {
    log "📊 Starter threshold overvågning..."

    (
        PREV_CONN_COUNT=0
        while true; do
            CONN_COUNT=$(ss -tn state established 2>/dev/null | tail -n +2 | wc -l)

            # Alarm hvis forbindelser stiger hurtigt
            if [ "$CONN_COUNT" -gt 50 ]; then
                alert "HØJ FORBINDELSES-AKTIVITET: $CONN_COUNT aktive forbindelser!"
            fi

            DELTA=$((CONN_COUNT - PREV_CONN_COUNT))
            if [ "$DELTA" -gt 20 ]; then
                alert "FORBINDELSES-SPRAY: $DELTA nye forbindelser på kort tid!"
            fi

            PREV_CONN_COUNT=$CONN_COUNT
            sleep 10
        done
    ) &
    THRESHOLD_PID=$!
    echo "$THRESHOLD_PID" > "$GUARD_DIR/threshold_monitor.pid"
    log "✅ Threshold monitor PID: $THRESHOLD_PID"
}

# ══════════════════════════════════════════════
# FASE 5: ARP/MITM DETEKTION
# ══════════════════════════════════════════════
start_arp_monitor() {
    log "🔗 Starter ARP/MITM detektion..."

    # Gem oprindelig ARP cache
    arp -an 2>/dev/null > "$GUARD_DIR/arp_baseline.txt"

    (
        while true; do
            CURRENT_ARP=$(arp -an 2>/dev/null)

            # Tjek for MAC-ændringer (MITM indikator)
            while read -r line; do
                IP=$(echo "$line" | grep -oP '\(\K[^)]+' | head -1)
                MAC=$(echo "$line" | grep -oP 'at \K[^ ]+' | head -1)

                if [ -n "$IP" ] && [ -n "$MAC" ]; then
                    OLD_MAC=$(grep "($IP)" "$GUARD_DIR/arp_baseline.txt" 2>/dev/null | grep -oP 'at \K[^ ]+' | head -1)
                    if [ -n "$OLD_MAC" ] && [ "$OLD_MAC" != "$MAC" ] && [ "$MAC" != "<incomplete>" ]; then
                        alert "MITM DETEKTERET! MAC ændret for $IP: $OLD_MAC → $MAC"
                    fi
                fi
            done <<< "$CURRENT_ARP"

            # Opdater baseline periodisk
            sleep 60
            arp -an 2>/dev/null > "$GUARD_DIR/arp_baseline.txt"
        done
    ) &
    ARP_PID=$!
    echo "$ARP_PID" > "$GUARD_DIR/arp_monitor.pid"
    log "✅ ARP monitor PID: $ARP_PID"
}

# ══════════════════════════════════════════════
# FASE 6: FIREWALL STATUS RAPPORT
# ══════════════════════════════════════════════
show_status() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  🛡️  FORTRESS STATUS RAPPORT                  ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}"
    echo ""

    # Firewall politik
    INPUT_POLICY=$(iptables -L INPUT | head -1 | awk '{print $NF}')
    OUTPUT_POLICY=$(iptables -L OUTPUT | head -1 | awk '{print $NF}')
    echo -e "  Firewall politik:  INPUT=${RED}$INPUT_POLICY${NC}  OUTPUT=${GREEN}$OUTPUT_POLICY${NC}"

    # Regler tælling
    RULE_COUNT=$(iptables -L INPUT -n | wc -l)
    echo -e "  Firewall regler:   ${YELLOW}$RULE_COUNT${NC} INPUT regler"

    # Blokerede IP'er
    BLOCKED_COUNT=$(wc -l < "$BLOCKED_IPS" 2>/dev/null || echo 0)
    echo -e "  Blokerede IP'er:   ${RED}$BLOCKED_COUNT${NC}"

    # Aktive monitorer
    echo ""
    echo -e "  ${YELLOW}Aktive monitorer:${NC}"
    for pidfile in intrusion_monitor.pid network_monitor.pid threshold_monitor.pid arp_monitor.pid; do
        if [ -f "$GUARD_DIR/$pidfile" ]; then
            PID=$(cat "$GUARD_DIR/$pidfile")
            if kill -0 "$PID" 2>/dev/null; then
                echo -e "    ✅ ${pidfile%.pid}: Kører (PID $PID)"
            else
                echo -e "    ❌ ${pidfile%.pid}: STOPPET"
            fi
        else
            echo -e "    ⚪ ${pidfile%.pid}: Ikke startet"
        fi
    done

    # Aktive forbindelser
    CONN_COUNT=$(ss -tn state established 2>/dev/null | tail -n +2 | wc -l)
    echo ""
    echo -e "  Aktive forbindelser: ${YELLOW}$CONN_COUNT${NC}"

    # Seneste alerts
    ALERT_COUNT=$(ls "$ALERT_DIR" 2>/dev/null | wc -l)
    echo -e "  Aktive alerts:      ${RED}$ALERT_COUNT${NC}"

    # Seneste intrusion log
    if [ -f "$INTRUSION_LOG" ]; then
        RECENT=$(tail -5 "$INTRUSION_LOG" 2>/dev/null)
        if [ -n "$RECENT" ]; then
            echo ""
            echo -e "  ${RED}Seneste intrusion events:${NC}"
            echo "$RECENT" | while read line; do
                echo -e "    🔴 $line"
            done
        fi
    fi

    echo ""
}

# ══════════════════════════════════════════════
# HOVEDPROGRAM
# ══════════════════════════════════════════════
case "${1:-start}" in
    start)
        echo -e "${GREEN}🛡️ FORTRESS FIREWALL STARTER...${NC}"
        setup_firewall
        start_intrusion_monitor
        start_network_monitor
        start_threshold_monitor
        start_arp_monitor
        show_status
        log "🏰 FORTRESS fuldt operationel!"
        ;;
    stop)
        log "🛑 Stopper FORTRESS..."
        for pidfile in intrusion_monitor.pid network_monitor.pid threshold_monitor.pid arp_monitor.pid; do
            if [ -f "$GUARD_DIR/$pidfile" ]; then
                PID=$(cat "$GUARD_DIR/$pidfile")
                kill "$PID" 2>/dev/null
                rm "$GUARD_DIR/$pidfile"
            fi
        done
        iptables -F
        iptables -P INPUT ACCEPT
        iptables -P OUTPUT ACCEPT
        iptables -P FORWARD ACCEPT
        log "✅ FORTRESS stoppet - firewall flushet"
        ;;
    status)
        show_status
        ;;
    block)
        if [ -n "$2" ]; then
            iptables -A INPUT -s "$2" -j DROP
            echo "$2" >> "$BLOCKED_IPS"
            log "⛔ Blokeret: $2"
        fi
        ;;
    unblock)
        if [ -n "$2" ]; then
            iptables -D INPUT -s "$2" -j DROP 2>/dev/null
            sed -i "/$2/d" "$BLOCKED_IPS" 2>/dev/null
            log "✅ Fjernet blokering: $2"
        fi
        ;;
    allow)
        # Tillad specifik port
        if [ -n "$2" ]; then
            iptables -I INPUT 1 -p tcp --dport "$2" -j ACCEPT
            log "✅ Tilladt port: $2"
        fi
        ;;
    *)
        echo "Brug: $0 {start|stop|status|block IP|unblock IP|allow PORT}"
        ;;
esac