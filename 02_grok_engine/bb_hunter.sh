#!/bin/bash
# ═══════════════════════════════════════════════════════════
#  💀 AUTOMATED BUG BOUNTY HUNTER v2.0
#  Brug: bash bb_hunter.sh target.com [mode]
#  Mode: recon | vuln | full | report
# ═══════════════════════════════════════════════════════════

TARGET=${1:-""}
MODE=${2:-"full"}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

if [ -z "$TARGET" ]; then
    echo "💀 Bug Bounty Hunter v2.0"
    echo ""
    echo "Brug: bash bb_hunter.sh target.com [mode]"
    echo ""
    echo "Modes:"
    echo "  recon   — Subdomain + DNS + HTTP probe"
    echo "  vuln    — Vulnerability scan (nuclei)"
    echo "  full    — Full pipeline (recon + vuln + report)"
    echo "  report  — Generate report only"
    echo ""
    echo "Examples:"
    echo "  bash bb_hunter.sh example.com recon"
    echo "  bash bb_hunter.sh example.com full"
    exit 1
fi

WORKDIR="/tmp/bbh_${TARGET}_${TIMESTAMP}"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${RED}╔══════════════════════════════════════════════╗${NC}"
echo -e "${RED}║  💀 BUG BOUNTY HUNTER v2.0                ║${NC}"
echo -e "${RED}║  Target: $TARGET${NC}"
echo -e "${RED}║  Mode: $MODE${NC}"
echo -e "${RED}╚══════════════════════════════════════════════╝${NC}"
echo ""

# ═══ PHASE 1: RECON ═══
if [ "$MODE" = "recon" ] || [ "$MODE" = "full" ]; then
    echo -e "${YELLOW}[1/6] 🔍 Subdomain Discovery (subfinder)...${NC}"
    subfinder -d "$TARGET" -all -silent 2>&1 | tee sub_subfinder.txt | wc -l
    
    echo -e "${YELLOW}[2/6] 🔍 Deep DNS (amass, 60s timeout)...${NC}"
    timeout 60 amass enum -passive -d "$TARGET" 2>&1 | tee -a sub_amass.txt | tail -5
    
    # Merge and deduplicate
    cat sub_subfinder.txt sub_amass.txt 2>/dev/null | sort -u > subdomains_all.txt
    TOTAL_SUBS=$(wc -l < subdomains_all.txt)
    echo -e "  ${GREEN}✅ Total subdomains: $TOTAL_SUBS${NC}"
    
    echo -e "${YELLOW}[3/6] 🌐 HTTP Probe (live hosts)...${NC}"
    cat subdomains_all.txt | httpx -status-code -title -tech-detect -silent 2>&1 | tee httpx_live.txt | wc -l
    LIVE=$(wc -l < httpx_live.txt)
    echo -e "  ${GREEN}✅ Live hosts: $LIVE${NC}"
    
    echo -e "${YELLOW}[4/6] 📊 DNS Records...${NC}"
    dig "$TARGET" ANY +noall +answer 2>&1 | tee dns_records.txt | head -10
    dig "$TARGET" MX +noall +answer 2>&1 | tee -a dns_records.txt | head -5
    dig "$TARGET" TXT +noall +answer 2>&1 | tee -a dns_records.txt | head -5
    
    echo -e "${YELLOW}[5/6] 🗂️ Wayback URLs...${NC}"
    curl -s "https://web.archive.org/cdx/search/cdx?url=*.$TARGET/*&output=list&fl=original&collapse=urlkey" 2>&1 | head -200 | tee wayback_urls.txt | wc -l
    WAYBACK=$(wc -l < wayback_urls.txt 2>/dev/null || echo 0)
    echo -e "  ${GREEN}✅ Wayback URLs: $WAYBACK${NC}"
fi

# ═══ PHASE 2: VULNERABILITY SCAN ═══
if [ "$MODE" = "vuln" ] || [ "$MODE" = "full" ]; then
    echo -e "${RED}[6/6] 💀 NUCLEI VULNERABILITY SCAN...${NC}"
    
    # Critical + High
    echo -e "  Scanning critical/high..."
    nuclei -l subdomains_all.txt -severity critical,high -silent -timeout 10 2>&1 | tee nuclei_critical.txt | head -30
    
    # Medium
    echo -e "  Scanning medium..."
    nuclei -l subdomains_all.txt -severity medium -silent -timeout 10 2>&1 | tee nuclei_medium.txt | head -20
    
    # Exposures
    echo -e "  Scanning exposures..."
    nuclei -l subdomains_all.txt -t exposures/ -silent -timeout 10 2>&1 | tee nuclei_exposures.txt | head -20
    
    # CVEs
    echo -e "  Scanning CVEs..."
    nuclei -l subdomains_all.txt -t cves/ -severity critical,high -silent -timeout 10 2>&1 | tee nuclei_cves.txt | head -20
    
    CRIT=$(wc -l < nuclei_critical.txt 2>/dev/null || echo 0)
    MED=$(wc -l < nuclei_medium.txt 2>/dev/null || echo 0)
    EXP=$(wc -l < nuclei_exposures.txt 2>/dev/null || echo 0)
    CVE=$(wc -l < nuclei_cves.txt 2>/dev/null || echo 0)
    
    echo -e ""
    echo -e "${RED}  💀 Critical/High: $CRIT${NC}"
    echo -e "${YELLOW}  ⚠️  Medium: $MED${NC}"
    echo -e "${CYAN}  🔑 Exposures: $EXP${NC}"
    echo -e "${GREEN}  🛡️  CVEs: $CVE${NC}"
fi

# ═══ PHASE 3: REPORT ═══
if [ "$MODE" = "report" ] || [ "$MODE" = "full" ]; then
    echo ""
    echo -e "${YELLOW}📋 Generating report...${NC}"
    
    REPORT="$WORKDIR/report_${TARGET}_${TIMESTAMP}.md"
    
    cat > "$REPORT" << EOF
# Bug Bounty Report: $TARGET
**Date:** $(date)
**Hunter:** admin_user + Grok v4 (251 tools)
**Target:** $TARGET

## Recon Summary
- **Subdomains found:** $(wc -l < subdomains_all.txt 2>/dev/null || echo 0)
- **Live hosts:** $(wc -l < httpx_live.txt 2>/dev/null || echo 0)
- **Wayback URLs:** $(wc -l < wayback_urls.txt 2>/dev/null || echo 0)

## Vulnerabilities
### Critical/High ($(wc -l < nuclei_critical.txt 2>/dev/null || echo 0))
\`\`\`
$(cat nuclei_critical.txt 2>/dev/null || echo "None found")
\`\`\`

### Medium ($(wc -l < nuclei_medium.txt 2>/dev/null || echo 0))
\`\`\`
$(cat nuclei_medium.txt 2>/dev/null || echo "None found")
\`\`\`

### Exposures ($(wc -l < nuclei_exposures.txt 2>/dev/null || echo 0))
\`\`\`
$(cat nuclei_exposures.txt 2>/dev/null || echo "None found")
\`\`\`

### CVEs ($(wc -l < nuclei_cves.txt 2>/dev/null || echo 0))
\`\`\`
$(cat nuclei_cves.txt 2>/dev/null || echo "None found")
\`\`\`

## Live Hosts
\`\`\`
$(cat httpx_live.txt 2>/dev/null || echo "None")
\`\`\`

## Subdomains
\`\`\`
$(head -50 subdomains_all.txt 2>/dev/null || echo "None")
\`\`\`

## DNS Records
\`\`\`
$(cat dns_records.txt 2>/dev/null || echo "None")
\`\`\`

---
*Generated by Bug Bounty Hunter v2.0 + Grok v4 (251 tools)*
EOF

    echo -e "${GREEN}✅ Report saved: $REPORT${NC}"
    echo ""
    echo -e "${YELLOW}🎯 NÆSTE SKRIDT:${NC}"
    echo "  1. Gennemgå nuclei_critical.txt for verificerbare findings"
    echo "  2. For hvert finding: skriv PoC (Proof of Concept)"
    echo "  3. Tjek scope på HackerOne/Bugcrowd programmet"
    echo "  4. Indsend med professionel rapport"
    echo ""
    echo -e "${RED}⚠️  VIGTIGT:${NC} Tjek ALTID program scope før du scanner!"
    echo "  Out-of-scope scanning = ban fra platformen."
fi

echo ""
echo -e "${RED}╔══════════════════════════════════════════════╗${NC}"
echo -e "${RED}║  ✅ MISSION COMPLETE                          ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo "  Working directory: $WORKDIR"
echo "  Report: $WORKDIR/report_*.md"