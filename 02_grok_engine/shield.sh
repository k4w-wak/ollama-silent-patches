#!/bin/bash
# ============================================================
#  🛡️  KONGE SHIELD — Hacker Defense System
#  Blokkerer hackerens IP + Bouygues range + hardening
# ============================================================

set -e
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${RED}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║    🛡️  KONGE SHIELD — AKTIVERER FORSVAR    🛡️    ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# ═══ PHASE 1: BLOCK HACKER IP ═══
echo -e "${YELLOW}[1/7] 🔴 Blokerer hacker IP 176.130.181.234...${NC}"
sudo iptables -I INPUT -s 176.130.181.234 -j DROP
sudo iptables -I OUTPUT -d 176.130.181.234 -j DROP
sudo iptables -I FORWARD -s 176.130.181.234 -j DROP
sudo iptables -I FORWARD -d 176.130.181.234 -j DROP
echo -e "${GREEN}  ✅ 176.130.181.234 BLOKKERET (IN + OUT + FORWARD)${NC}"

# ═══ PHASE 2: BLOCK BOUYGUES RANGE ═══
echo -e "${YELLOW}[2/7] 🔴 Blokerer Bouygues ISP range 176.128.0.0/10...${NC}"
sudo iptables -I INPUT -s 176.128.0.0/10 -j DROP
sudo iptables -I OUTPUT -d 176.128.0.0/10 -j DROP
echo -e "${GREEN}  ✅ 176.128.0.0/10 BLOKKERET${NC}"

# ═══ PHASE 3: BLOCK KNOWN ATTACK NETWORKS ═══
echo -e "${YELLOW}[3/7] 🔴 Blokerer kendte angrebs-netværk...${NC}"
# Block common Tor exit nodes (optional, aggressive)
# Block known malicious ASN ranges
sudo iptables -I INPUT -s 185.220.101.0/24 -j DROP 2>/dev/null || true  # Common Tor exit
echo -e "${GREEN}  ✅ Kendte angrebsnetværk blokkeret${NC}"

# ═══ PHASE 4: SSH HARDENING ═══
echo -e "${YELLOW}[4/7] 🟡 SSH hardening...${NC}"
# Only allow SSH from local network + localhost
sudo iptables -I INPUT -p tcp --dport 22 -s 192.168.32.0/24 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 22 -s 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j DROP
# Disable root SSH login
sudo sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config 2>/dev/null || true
sudo sed -i 's/^#*MaxAuthTries.*/MaxAuthTries 3/' /etc/ssh/sshd_config 2>/dev/null || true
sudo sed -i 's/^#*LoginGraceTime.*/LoginGraceTime 30/' /etc/ssh/sshd_config 2>/dev/null || true
echo -e "${GREEN}  ✅ SSH kun fra 192.168.32.0/24 + localhost${NC}"

# ═══ PHASE 5: CLOSE EXTERNAL HOENYPOT PORTS ═══
echo -e "${YELLOW}[5/7] 🟡 Restrikt Honeypot til lokal netværk...${NC}"
HONEYPOT_PORTS="21 25 53 80 88 110 135 139 143 389 443 445 587 636 993 1433 3128 3389 48191 5985 5986"
for port in $HONEYPOT_PORTS; do
    # Allow from local network
    sudo iptables -I INPUT -p tcp --dport $port -s 192.168.32.0/24 -j ACCEPT 2>/dev/null || true
    sudo iptables -I INPUT -p tcp --dport $port -s 127.0.0.1 -j ACCEPT 2>/dev/null || true
    # Drop from outside
    sudo iptables -A INPUT -p tcp --dport $port -j DROP 2>/dev/null || true
done
echo -e "${GREEN}  ✅ Honeypot porte kun tilgængelige fra lokal netværk${NC}"

# ═══ PHASE 6: GENERAL HARDENING ═══
echo -e "${YELLOW}[6/7] 🟡 Generel hardening...${NC}"
# Drop invalid packets
sudo iptables -A INPUT -m state --state INVALID -j DROP
# Allow established connections
sudo iptables -I INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
# Allow loopback
sudo iptables -I INPUT -i lo -j ACCEPT
# Allow local network
sudo iptables -I INPUT -s 192.168.32.0/24 -j ACCEPT
# Rate limit new connections (anti-DDoS)
sudo iptables -A INPUT -p tcp --syn -m limit --limit 10/s --limit-burst 20 -j ACCEPT
sudo iptables -A INPUT -p tcp --syn -j DROP
# Log dropped packets from suspicious sources
sudo iptables -A INPUT -j LOG --log-prefix "SHIELD_DROP: " --log-level 4 2>/dev/null || true
echo -e "${GREEN}  ✅ Generel hardening aktiv${NC}"

# ═══ PHASE 7: PERSIST RULES ═══
echo -e "${YELLOW}[7/7] 💾 Gemmer iptables rules permanent...${NC}"
sudo iptables-save > /etc/iptables/rules.v4 2>/dev/null || sudo sh -c "iptables-save > /etc/iptables.rules" 2>/dev/null || true
# Make it persistent across reboots
if ! grep -q "iptables-restore" /etc/rc.local 2>/dev/null; then
    sudo sh -c "echo '#!/bin/bash' > /etc/rc.local"
    sudo sh -c "echo 'iptables-restore < /etc/iptables.rules' >> /etc/rc.local" 2>/dev/null || true
    sudo chmod +x /etc/rc.local 2>/dev/null || true
fi
echo -e "${GREEN}  ✅ Regler gemt og persistent${NC}"

echo ""
echo -e "${RED}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     🛡️  KONGE SHIELD — AKTIV!  🛡️              ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}  Blokeret:${NC}"
echo -e "${RED}  • 176.130.181.234 (hacker)  — IN + OUT + FORWARD${NC}"
echo -e "${RED}  • 176.128.0.0/10 (Bouygues) — IN + OUT${NC}"
echo -e "${RED}  • 185.220.101.0/24 (Tor)    — IN${NC}"
echo ""
echo -e "${CYAN}  Tilladt:${NC}"
echo -e "${GREEN}  • SSH (22)          — kun 192.168.32.0/24${NC}"
echo -e "${GREEN}  • Honeypot (25 port) — kun 192.168.32.0/24${NC}"
echo -e "${GREEN}  • Lokalt netværk    — alt tilladt${NC}"
echo ""
echo -e "${CYAN}  Hardening:${NC}"
echo -e "${GREEN}  • Invalid packets: DROP${NC}"
echo -e "${GREEN}  • SYN flood limit:  10/s burst 20${NC}"
echo -e "${GREEN}  • SSH: root login disabled, max 3 auth${NC}"
echo -e "${GREEN}  • Logging: aktivt (SHIELD_DROP)${NC}"
echo ""

# Show current rules
echo -e "${CYAN}  Aktuelle INPUT regler:${NC}"
sudo iptables -L INPUT -n --line-numbers 2>&1 | head -20