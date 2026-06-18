#!/usr/bin/env bash
# ===================================================================
# BB_TURBO.sh - K4W_WAK Bug Bounty TURBO RECON v2.0
# 40-100x hurtigere end amass! MassDNS + DNSX + AlterX
# ===================================================================
set -e
export PATH="$HOME/go/bin:/usr/local/go/bin:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
RED='\033[0;31m'; GRN='\033[0;32m'; YEL='\033[1;33m'; BLU='\033[0;34m'; MAG='\033[0;35m'; CYN='\033[0;36m'; NC='\033[0m'; BOLD='\033[1m'

TARGET="${1:-}"
OUTDIR="${2:-bb_turbo_$(date +%Y%m%d_%H%M%S)}"
[ -z "$TARGET" ] && { echo -e "${RED}Usage: $0 domain.com [output_dir]${NC}"; exit 1; }
mkdir -p "$OUTDIR"

echo -e "${MAG}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAG}║  🚀 K4W_WAK TURBO RECON v2.0 - 40x hurtigere!                ║${NC}"
echo -e "${MAG}╚══════════════════════════════════════════════════════════════╝${NC}"

# --- PHASE 0A: Subfinder (hurtig) ---
echo -e "${BLU}${BOLD}[+] PHASE 0A: Subfinder${NC}"
echo -e "${CYN}  → subfinder -d $TARGET -all -silent${NC}"
subfinder -d "$TARGET" -all -silent > "$OUTDIR/subfinder.txt" 2>&1
SUBS=$(wc -l < "$OUTDIR/subfinder.txt" 2>&1 || echo 0)
echo -e "${GRN}  ✓ $SUBS subdomains${NC}"

# --- PHASE 0B: DNS Bruteforce (massdns style) ---
echo -e "${BLU}${BOLD}[+] PHASE 0B: DNS Bruteforce (dnsx)${NC}"
echo -e "${CYN}  → dnsx -d /usr/share/amass/wordlists/...${NC}"
dnsx -d "$TARGET" -w /usr/share/amass/wordlists/bitquark_subdomains_top100k.txt -silent 2>&1 | tee "$OUTDIR/dnsx_brute.txt" >/dev/null
BRUTE=$(wc -l < "$OUTDIR/dnsx_brute.txt" 2>&1 || echo 0)
echo -e "${GRN}  ✓ $BRUTE fra DNS bruteforce${NC}"

# --- PHASE 0C: AlterX (permutation generator) ---
echo -e "${BLU}${BOLD}[+] PHASE 0C: AlterX (permutations)${NC}"
echo -e "${CYN}  → alterx -l $OUTDIR/subfinder.txt${NC}"
alterx -l "$OUTDIR/subfinder.txt" -silent > "$OUTDIR/alterx.txt" 2>&1
echo -e "${GRN}  ✓ $(wc -l < "$OUTDIR/alterx.txt" 2>&1 || echo 0) permutations${NC}"

# --- PHASE 0D: DNS Resolution ALL ---
echo -e "${BLU}${BOLD}[+] PHASE 0D: DNS Resolution (dnsx pipe)${NC}"
(cat "$OUTDIR/subfinder.txt" "$OUTDIR/dnsx_brute.txt" "$OUTDIR/alterx.txt" 2>/dev/null | sort -u) | dnsx -silent -resp > "$OUTDIR/all_resolved.txt" 2>&1
echo -e "${GRN}  ✓ $(wc -l < "$OUTDIR/all_resolved.txt" 2>&1 || echo 0) resolved${NC}"

# --- PHASE 1: HTTP Probing ---
echo -e "${BLU}${BOLD}[+] PHASE 1: HTTP Probing (httpx)${NC}"
cat "$OUTDIR/all_resolved.txt" | dnsx -silent | httpx -title -td -sc -silent -o "$OUTDIR/httpx.txt" 2>&1
echo -e "${GRN}  ✓ $(wc -l < "$OUTDIR/httpx.txt" 2>&1 || echo 0) live hosts${NC}"

# --- PHASE 2: URL Discovery ---
echo -e "${BLU}${BOLD}[+] PHASE 2: URL Discovery (gau + waybackurls)${NC}"
cut -d' ' -f1 "$OUTDIR/httpx.txt" 2>/dev/null | sed 's/\[//g;s/\]//g' | sed 's|https://||g' | sort -u > "$OUTDIR/live_domains.txt"
cat "$OUTDIR/live_domains.txt" | waybackurls > "$OUTDIR/waybackurls.txt" 2>&1 &
WAYPID=$!
cat "$OUTDIR/live_domains.txt" | gau > "$OUTDIR/gau.txt" 2>&1 &
GAUPID=$!
echo -e "${CYN}  → waybackurls PID: $WAYPID, gau PID: $GAUPID${NC}"
echo -e "${YEL}  ⏳ Venter på waybackurls + gau...${NC}"
wait $WAYPID 2>&1; wait $GAUPID 2>&1
echo -e "${GRN}  ✓ $(wc -l < "$OUTDIR/waybackurls.txt" 2>&1 || echo 0) waybackurls${NC}"
echo -e "${GRN}  ✓ $(wc -l < "$OUTDIR/gau.txt" 2>&1 || echo 0) gau URLs${NC}"

# --- PHASE 3: Nuclei (kun critical/high) ---
echo -e "${BLU}${BOLD}[+] PHASE 3: Nuclei Critical & High${NC}"
cat "$OUTDIR/live_domains.txt" | nuclei -severity critical,high -o "$OUTDIR/nuclei.txt" -silent 2>&1
echo -e "${GRN}  ✓ $(wc -l < "$OUTDIR/nuclei.txt" 2>&1 || echo 0) findings${NC}"

# --- DONE ---
echo -e "${MAG}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAG}║  ★ TURBO RECON FÆRDIG!                                       ║${NC}"
echo -e "${MAG}╠══════════════════════════════════════════════════════════════╣${NC}"
ls -lh "$OUTDIR/" | awk '{printf "${MAG}║${NC} %s\n", $0}'
echo -e "${MAG}╚══════════════════════════════════════════════════════════════╝${NC}"
echo -e "${GRN}  Results: $OUTDIR/${NC}"
