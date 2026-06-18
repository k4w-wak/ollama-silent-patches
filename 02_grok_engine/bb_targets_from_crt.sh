#!/usr/bin/env bash
# ===================================================================
# bb_targets_from_crt.sh - Mål høstning fra Certificate Transparency
# Bruger crt.sh API med wildcard/percentage queries
# ===================================================================
set -e
export PATH="$HOME/go/bin:/usr/local/go/bin:$HOME/.local/bin:$PATH"
RED='\033[0;31m'; GRN='\033[0;32m'; YEL='\033[1;33m'; BLU='\033[0;34m'; MAG='\033[0;35m'; CYN='\033[0;36m'; NC='\033[0m'

DOMAIN="${1:-rapid7.com}"
OUT="${2:-targets_$DOMAIN.txt}"

echo -e "${MAG}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAG}║  🎯 Target Harvesting: $DOMAIN                             ║${NC}"
echo -e "${MAG}╚══════════════════════════════════════════════════════════════╝${NC}"

# 1: Subfinder (hurtig, 5.5K subs er MASSE input)
echo -e "${BLU}[+] Running subfinder on $DOMAIN${NC}"
subfinder -d "$DOMAIN" -all -silent > /tmp/sf_${DOMAIN}.txt 2>&1
SF=$(wc -l < /tmp/sf_${DOMAIN}.txt)
echo -e "${GRN}  ✓ subfinder: $SF subs${NC}"

# 2: Extract root domains of interesting subdomains
echo -e "${BLU}[+] Extracting unique root targets${NC}"
cat /tmp/sf_${DOMAIN}.txt | awk -F. '{n=NF-1; if(n>=2) print $(n-1)"."$n}' | sort -u > "$OUT"
ROOTS=$(wc -l < "$OUT")
echo -e "${GRN}  ✓ $ROOTS unique root domains${NC}"

# 3: Expand with subdomain wordlists (quick)
echo -e "${BLU}[+] Expanding with common subdomains${NC}"
WORDLIST="/usr/share/amass/wordlists/bitquark_subdomains_top100k.txt"
if [ -f "$WORDLIST" ]; then
  echo -e "${CYN}  → Using amass wordlist${NC}"
  for root in $(head -10 "$OUT"); do
    while read w; do echo "$w.$root"; done < <(head -100 "$WORDLIST")
  done > "${OUT%.txt}_expanded.txt"
  EXP=$(wc -l < "${OUT%.txt}_expanded.txt")
  echo -e "${GRN}  ✓ $EXP expanded permutations${NC}"
else
  echo -e "${YEL}  ! No amass wordlist found${NC}"
fi

# 4: Wildcard cert.sh query for related orgs
echo -e "${BLU}[+] Querying crt.sh for related domains${NC}"
curl -s "https://crt.sh/?q=%.$DOMAIN&output=json" 2>&1 | python3 -c "
import json, sys, re
try: data = json.load(sys.stdin)
except: data = []
seen = set()
for entry in data[:500]:
    name = entry.get('name_value', '')
    for sub in name.split('\n'):
        sub = sub.strip()
        if sub and sub not in seen:
            seen.add(sub)
            print(sub)
" > "${OUT%.txt}_crt.txt"
CRT=$(wc -l < "${OUT%.txt}_crt.txt")
echo -e "${GRN}  ✓ $CRT entries from crt.sh${NC}"

# 5: Combine all
cat "$OUT" "${OUT%.txt}_crt.txt" 2>/dev/null | grep -v "^$" | sort -u > "${OUT%.txt}_all.txt"
ALL=$(wc -l < "${OUT%.txt}_all.txt")
echo -e "${MAG}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAG}║  🚀 Combined results: $ALL unique targets${NC}"
echo -e "${MAG}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${CYN}║  Files:                                                     ${NC}"
echo -e "${CYN}║    $OUT                (roots)${NC}"
echo -e "${CYN}║    ${OUT%.txt}_expanded.txt (permutations)${NC}"
echo -e "${CYN}║    ${OUT%.txt}_crt.txt       (cert transparency)${NC}"
echo -e "${CYN}║    ${OUT%.txt}_all.txt       (combined)${NC}"
echo -e "${MAG}╚══════════════════════════════════════════════════════════════╝${NC}"

echo -e "${GRN}Next steps:${NC}"
echo -e "${CYN}  1. Batch recon: for d in \$(head -20 ${OUT%.txt}_all.txt); do ./bb_turbo.sh \$d /tmp/recon/\$d; done${NC}"
echo -e "${CYN}  2. httpx probe: cat ${OUT%.txt}_all.txt | httpx -title${NC}"
echo -e "${CYN}  3. nuclei scan: cat ${OUT%.txt}_all.txt | httpx -silent | nuclei -severity critical,high${NC}"
