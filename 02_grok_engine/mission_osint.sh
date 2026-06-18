#!/bin/bash
# Phase 1: OSINT Recon on Hacker Infrastructure
# Target: 176.130.181.234 / Bouygues Telecom / Pierrelatte / rambler.ru

echo "💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀"
echo "  OPERATION: KONGER VS HACKER — OSINT DEEP DIVE"
echo "💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀💀"
echo ""

TARGET_IP="176.130.181.234"
LOGDIR="/home/kali/Skrivebord/grok_rapporter"
mkdir -p "$LOGDIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG="$LOGDIR/osint_mission_${TIMESTAMP}.log"

echo "[*] Phase 1: WHOIS Deep Dive"
echo "============================================" | tee -a "$LOG"
echo "[1a] WHOIS IP:" | tee -a "$LOG"
whois "$TARGET_IP" 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"

echo "[1b] Reverse DNS:" | tee -a "$LOG"
dig -x "$TARGET_IP" +noall +answer 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"

echo "[1c] Reverse WHOIS (Bouygues):" | tee -a "$LOG"
whois -h whois.ripe.net "$TARGET_IP" 2>&1 | head -80 | tee -a "$LOG"
echo "" | tee -a "$LOG"

echo "[*] Phase 2: DNS Intelligence"
echo "============================================" | tee -a "$LOG"
echo "[2a] DNS ANY records for rambler.ru:" | tee -a "$LOG"
dig rambler.ru ANY +noall +answer 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "[2b] MX records:" | tee -a "$LOG"
dig rambler.ru MX +noall +answer 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "[2c] TXT records:" | tee -a "$LOG"
dig rambler.ru TXT +noall +answer 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "[2d] NS records:" | tee -a "$LOG"
dig rambler.ru NS +noall +answer 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "[2e] SPF/DMARC:" | tee -a "$LOG"
dig _dmarc.rambler.ru TXT +noall +answer 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"

echo "[*] Phase 3: Passive Recon"
echo "============================================" | tee -a "$LOG"
echo "[3a] Shodan (via curl):" | tee -a "$LOG"
curl -s "https://internetdb.shodan.io/$TARGET_IP" 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'  {k}: {v}') for k,v in d.items()]" 2>&1 | tee -a "$LOG"
echo "" | tee -a "$LOG"

echo "[3b] AbuseIPDB check:" | tee -a "$LOG"
curl -s "https://api.abuseipdb.com/api/v2/check?ipAddress=$TARGET_IP" -H "Key: " -H "Accept: application/json" 2>&1 | head -20 | tee -a "$LOG"
echo "" | tee -a "$LOG"

echo "[3c] VirusTotal info:" | tee -a "$LOG"
curl -s "https://www.virustotal.com/api/v3/ip_addresses/$TARGET_IP" -H "x-apikey: " 2>&1 | head -20 | tee -a "$LOG"
echo "" | tee -a "$LOG"

echo "[*] Phase 4: Bouygues Network Range"
echo "============================================" | tee -a "$LOG"
echo "[4a] IP range scan (Bouygels network):" | tee -a "$LOG"
whois "$TARGET_IP" 2>&1 | grep -iE "netrange|cidr|inetnum|network|descr|owner|abuse" | tee -a "$LOG"
echo "" | tee -a "$LOG"

echo "[*] Phase 5: Subdomain Discovery"
echo "============================================" | tee -a "$LOG"
echo "[5a] Subfinder on rambler.ru:" | tee -a "$LOG"
subfinder -d rambler.ru -all -silent 2>&1 | head -100 | tee -a "$LOG"
echo "" | tee -a "$LOG"

echo "[6a] Amass on rambler.ru (quick):" | tee -a "$LOG"
timeout 120 amass enum -passive -d rambler.ru 2>&1 | head -100 | tee -a "$LOG"
echo "" | tee -a "$LOG"

echo "[*] Phase 6: Nuclei templates check on rambler.ru" | tee -a "$LOG"
echo "============================================" | tee -a "$LOG"
nuclei -u rambler.ru -severity critical,high -silent -timeout 5 2>&1 | head -50 | tee -a "$LOG"
echo "" | tee -a "$LOG"

echo "" | tee -a "$LOG"
echo "💀 MISSION COMPLETE — Results: $LOG" | tee -a "$LOG"