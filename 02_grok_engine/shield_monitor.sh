#!/bin/bash
# ============================================================
#  🛡️  KONGE SHIELD MONITOR — Overvåger angreb real-time
#  Kører som cron hver 5 minut eller som daemon
# ============================================================

LOG="/home/kali/.grok/logs/shield_monitor.log"
HACKER_IP="176.130.181.234"
BOUYGUES="176.128.0.0/10"
mkdir -p /home/kali/.grok/logs/

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🛡️ Shield Monitor started" >> "$LOG"

# 1. Ensure hacker IP is still blocked
if ! sudo iptables -L INPUT -n | grep -q "$HACKER_IP"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔴 RE-BLOCKING $HACKER_IP" >> "$LOG"
    sudo iptables -I INPUT -s "$HACKER_IP" -j DROP
    sudo iptables -I OUTPUT -d "$HACKER_IP" -j DROP
fi

# 2. Ensure Bouygues range is still blocked
if ! sudo iptables -L INPUT -n | grep -q "176.128.0.0/10"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔴 RE-BLOCKING Bouygues range" >> "$LOG"
    sudo iptables -I INPUT -s "$BOUYGUES" -j DROP
    sudo iptables -I OUTPUT -d "$BOUYGUES" -j DROP
fi

# 3. Check if hacker is online (ping)
if ping -c 1 -W 3 "$HACKER_IP" &>/dev/null; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ HACKER ONLINE — $HACKER_IP svarer på ping!" >> "$LOG"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚪ Hacker offline — $HACKER_IP svarer ikke" >> "$LOG"
fi

# 4. Check auth log for SSH attacks
SSH_ATTACKS=$(sudo grep -i "Failed password\|Invalid user\|Attack attempt" /var/log/auth.log 2>/dev/null | tail -5)
if [ -n "$SSH_ATTACKS" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔴 SSH ANGREB DETECTED:" >> "$LOG"
    echo "$SSH_ATTACKS" >> "$LOG"
    
    # Auto-block attacking IPs
    echo "$SSH_ATTACKS" | grep -oP 'from \K[0-9.]+' | sort -u | while read ip; do
        if [ "$ip" != "192.168.32."* ] && [ "$ip" != "127.0.0.1" ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔴 Auto-blocking SSH attacker: $ip" >> "$LOG"
            sudo iptables -I INPUT -s "$ip" -j DROP
        fi
    done
fi

# 5. Check for new suspicious connections
SUSPICIOUS=$(sudo ss -tn | grep -v "192.168.32" | grep -v "127.0.0" | grep ESTAB | head -10)
if [ -n "$SUSPICIOUS" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🟡 Suspicious established connections:" >> "$LOG"
    echo "$SUSPICIOUS" >> "$LOG"
fi

# 6. Check shield drop log
SHIELD_DROPS=$(sudo dmesg 2>/dev/null | grep "SHIELD_DROP" | tail -5)
if [ -n "$SHIELD_DROPS" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔴 Shield dropped packets:" >> "$LOG"
    echo "$SHIELD_DROPS" >> "$LOG"
fi

# 7. Save rules periodically
sudo iptables-save | sudo tee /etc/iptables/rules.v4 > /dev/null 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Shield check complete" >> "$LOG"