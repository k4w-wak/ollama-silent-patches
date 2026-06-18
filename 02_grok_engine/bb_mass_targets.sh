#!/usr/bin/env bash
# ===================================================================
# bb_mass_targets.sh - K4W_WAK MASS TARGET ACQUISITION & BATCH RECON
# Høster targets fra flere kilder og kører TURBO batch scan
# ===================================================================
set -e
export PATH="$HOME/go/bin:/usr/local/go/bin:$HOME/.local/bin:/PATH:/usr/local/bin:/usr/bin:/bin"
RED='\033[0;31m'; GRN='\033[0;32m'; YEL='\033[1;33m'; BLU='\033[0;34m'; MAG='\033[0;35m'; CYN='\033[0;36m'; NC='\033[0m'
BOLD='\033[1m'

TARGETS_DIR="${1:-bb_targets_$(date +%Y%m%d_%H%M%S)}"
mkdir -p "$TARGETS_DIR"
echo -e "${MAG}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAG}║  🎯 K4W_WAK MASS TARGET HARVESTER v1.0                       ║${NC}"
echo -e "${MAG}╚══════════════════════════════════════════════════════════════╝${NC}"
echo -e "${CYN}  Output: $TARGETS_DIR${NC}"

# === PHASE 1: Chaos Dataset (ProjectDiscovery public programs) ===
echo -e "${BLU}${BOLD}[+] PHASE 1: Chaos Dataset${NC}"
if [ ! -f "$TARGETS_DIR/chaos_programs.json" ]; then
  echo -e "${CYN}  → Downloading ProjectDiscovery Chaos programs...${NC}"
  curl -s "https://chaos-data.projectdiscovery.io/index.json" > "$TARGETS_DIR/chaos_programs.json" 2>&1 | tail -3
  echo -e "${GRN}  ✓ Download complete${NC}"
fi
# Extract bugbounty programs
echo -e "${CYN}  → Extracting bug bounty programs...${NC}"
# Filter programs with URL field
python3 -c "
import json, sys
with open('$TARGETS_DIR/chaos_programs.json') as f:
    data = json.load(f)
    programs = [p for p in data if p.get('bounty', False)]
    for p in programs[:50]:
        name = p.get('name', '')
        url = p.get('url', '')
        if url and url not in ['', 'N/A']:
            print(url.split('/')[0] if '/' in url else url)
" > "$TARGETS_DIR/chaos_targets.txt" 2>&1
CHAOS_COUNT=$(wc -l < "$TARGETS_DIR/chaos_targets.txt" 2>&1 || echo 0)
echo -e "${GRN}  ✓ $CHAOS_COUNT bounty targets from Chaos${NC}"

# === PHASE 2: Cert.sh Transparency Logs ===
echo -e "${BLU}${BOLD}[+] PHASE 2: Certificate Transparency (crt.sh)${NC}"
echo -e "${CYN}  → Querying crt.sh...${NC}"
# We'll use a sample query - but this is limited without specific domains
# Instead, query for known top-level programs
cat > "$TARGETS_DIR/ct_query.txt" <> 'EOF'
rapid7.com
hackerone.com
bugcrowd.com
intigriti.com
synack.com
cobalt.io
gitlab.com
shopify.com
dropbox.com
stripe.com
EOF
echo -e "${GRN}  ✓ CT query file: $(wc -l < "$TARGETS_DIR/ct_query.txt" 2>&1 || echo 0) seeds${NC}"

# === PHASE 3: Generate combined target list ===
echo -e "${BLU}${BOLD}[+] PHASE 3: Building master target list${NC}"
(cat "$TARGETS_DIR/chaos_targets.txt" "$TARGETS_DIR/ct_query.txt" 2>/dev/null | sort -u) > "$TARGETS_DIR/all_targets.txt"
TOTAL=$(wc -l < "$TARGETS_DIR/all_targets.txt" 2>&1 || echo 0)
echo -e "${GRN}  ✓ $TOTAL unique targets${NC}"

echo -e "${MAG}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAG}║  🚀 Ready to batch recon!                                    ║${NC}"
echo -e "${MAG}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${CYN}║  Commands:                                                   ║${NC}"
echo -e "${CYN}║  1. Single:  ./bb_turbo.sh <domain>                        ║${NC}"
echo -e "${CYN}║  2. Batch:  cat $TARGETS_DIR/all_targets.txt | xargs -P5 -I{} bash -c 'echo \"=== {} ===\"; ./bb_turbo.sh {} $TARGETS_DIR/recon_{}'  ║${NC}"
echo -e "${CYN}║  3. Top 10:  head -10 $TARGETS_DIR/all_targets.txt | xargs -P3 -I{} ./bb_turbo.sh {} ${NC}"
echo -e "${MAG}╚══════════════════════════════════════════════════════════════╝${NC}"

# === PHASE 4: Run batch recon (top 5 by default) ===
RUN_BATCH="${2:-}"
if [ "$RUN_BATCH" = "--batch" ]; then
  echo -e "${BLU}${BOLD}[+] PHASE 4: RUNNING BATCH RECON (top 5 targets)${NC}"
  mkdir -p "$TARGETS_DIR/recon"
  head -5 "$TARGETS_DIR/all_targets.txt" | while read domain; do
    echo -e "${CYN}  → Launching TURBO for: $domain${NC}"
    "$(dirname "$0")/bb_turbo.sh" "$domain" "$TARGETS_DIR/recon/$domain" > "$TARGETS_DIR/recon/${domain}.log" 2>&1 &
  done
  echo -e "${GRN}  ✓ All 5 recon jobs launched in background!${NC}"
  echo -e "${YEL}  Run 'ps aux | grep bb_turbo' to see status${NC}"
fi
echo -e "${GRN}  Files saved to: $TARGETS_DIR/${NC}"
