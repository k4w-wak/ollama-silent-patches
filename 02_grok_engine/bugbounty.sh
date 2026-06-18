#!/bin/bash
# ═════════════════════════════════════════════════════
#  💀 BUG BOUNTY HUNTER — AUTOMATED RECON PIPELINE
#  Brug: bash bugbounty.sh target.com
# ═════════════════════════════════════════════════════

TARGET=$1
if [ -z "$TARGET" ]; then
    echo "💀 Brug: bash bugbounty.sh target.com"
    echo ""
    echo "Top bug bounty programs:"
    echo "  hackerone.com  — $500-$250K"
    echo "  bugcrowd.com    — $100-$100K"
    echo "  intigriti.com   — €500-€10K"
    echo "  yeswehack.com   — €500-€10K"
    exit 1
fi

echo "╔══════════════════════════════════════════════════╗"
echo "║  💀 BUG BOUNTY HUNTER — $TARGET"
echo "╚══════════════════════════════════════════════════╝"
echo ""

mkdir -p /tmp/bb_$TARGET
cd /tmp/bb_$TARGET

echo "[1/7] 🔍 Subdomain Discovery..."
subfinder -d $TARGET -silent 2>&1 | tee subdomains.txt | wc -l
echo "  Found: $(wc -l < subdomains.txt) subdomains"

echo ""
echo "[2/7] 🌐 Deep DNS Enumeration..."
amass enum -passive -d $TARGET 2>&1 | tee -a subdomains.txt | tail -5
sort -u subdomains.txt -o subdomains.txt
echo "  Total unique: $(wc -l < subdomains.txt)"

echo ""
echo "[3/7] 🔎 HTTP Probe (live hosts)..."
httpx -l subdomains.txt -status-code -title -tech-detect -silent 2>&1 | tee httpx_live.txt | wc -l
echo "  Live hosts: $(wc -l < httpx_live.txt)"

echo ""
echo "[4/7] 💀 Nuclei Vulnerability Scan..."
nuclei -l subdomains.txt -severity critical,high -silent -timeout 10 2>&1 | tee nuclei_vulns.txt | head -30
echo "  Vulnerabilities: $(wc -l < nuclei_vulns.txt)"

echo ""
echo "[5/7] 🔑 Sensitive Data Exposure..."
nuclei -l subdomains.txt -t exposures/ -silent 2>&1 | tee nuclei_exposures.txt | head -20
echo "  Exposures: $(wc -l < nuclei_exposures.txt)"

echo ""
echo "[6/7] 📊 Port Scan (top 1000)..."
nmap -Pn --top-ports 1000 -iL subdomains.txt -open 2>&1 | tee nmap_scan.txt | tail -20

echo ""
echo "[7/7] 📋 REPORT GENERATION..."
echo "========================================" > report_$TARGET.md
echo "Bug Bounty Report: $TARGET" >> report_$TARGET.md
echo "Date: $(date)" >> report_$TARGET.md
echo "========================================" >> report_$TARGET.md
echo "" >> report_$TARGET.md
echo "## Subdomains ($(wc -l < subdomains.txt))" >> report_$TARGET.md
cat subdomains.txt >> report_$TARGET.md
echo "" >> report_$TARGET.md
echo "## Live Hosts ($(wc -l < httpx_live.txt))" >> report_$TARGET.md
cat httpx_live.txt >> report_$TARGET.md
echo "" >> report_$TARGET.md
echo "## Vulnerabilities ($(wc -l < nuclei_vulns.txt))" >> report_$TARGET.md
cat nuclei_vulns.txt >> report_$TARGET.md
echo "" >> report_$TARGET.md
echo "## Exposures ($(wc -l < nuclei_exposures.txt))" >> report_$TARGET.md
cat nuclei_exposures.txt >> report_$TARGET.md

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  ✅ RECON COMPLETE                              ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "  Subdomains:     $(wc -l < subdomains.txt)"
echo "  Live hosts:     $(wc -l < httpx_live.txt)"
echo "  Vulnerabilities: $(wc -l < nuclei_vulns.txt)"
echo "  Exposures:       $(wc -l < nuclei_exposures.txt)"
echo ""
echo "  Report: /tmp/bb_$TARGET/report_$TARGET.md"
echo ""
echo "  🎯 NÆSTE SKRIDT:"
echo "  1. Gennemgå nuclei_vulns.txt for high/critical"
echo "  2. Tjek httpx_live.txt for interessante endpoints"
echo "  3. Manuelt test: XSS, IDOR, auth bypass"
echo "  4. Skriv PoC (Proof of Concept)"
echo "  5. Indsend på HackerOne/Bugcrowd"