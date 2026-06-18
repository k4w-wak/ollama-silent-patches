#!/usr/bin/env bash
# ====================================================================
# BB_LAUNCHER.sh - K4W_WAK Bug Bounty Arsenal Launcher v1.0
# ====================================================================
set -e
export PATH="$HOME/go/bin:/usr/local/go/bin:$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
RED='\033[0;31m'; GRN='\033[0;32m'; YEL='\033[1;33m'; BLU='\033[0;34m'; MAG='\033[0;35m'; CYN='\033[0;36m'; NC='\033[0m'
BOLD='\033[1m'

banner() {
echo -e "${MAG}|===========[ K4W_WAK BB LAUNCHER v1.0 ]================|${NC}"
}

# --- Dependency Check ---
check_deps() {
  local missing=""
  for t in subfinder httpx naabu katana dalfox ffuf nuclei amass bbot gau waybackurls; do
    if ! command -v "$t" > /dev/null 2>&1; then echo -e "${RED}[MISS]${NC} $t"; missing="$missing $t"
    else echo -e "${GRN}[ OK ]${NC} $t"; fi
  done
  if [ -n "$missing" ]; then
    echo -e "${RED}[!] Missing tools: $missing${NC}"
    echo -e "${YEL}[i] Run updater first: ./bb_launcher.sh --update${NC}"
  fi
}

# --- Tools installer ---
update_tools() {
  echo -e "${CYN}[+] Updating Go tools...${NC}"
  export GOBIN="$HOME/go/bin"
  mkdir -p "$GOBIN"
  for pkg in \
    "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest" \
    "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest" \
    "github.com/projectdiscovery/httpx/cmd/httpx@latest" \
    "github.com/projectdiscovery/naabu/cmd/naabu@latest" \
    "github.com/projectdiscovery/katana/cmd/katana@latest" \
    "github.com/ffuf/ffuf/v2@latest" \
    "github.com/tomnomnom/waybackurls@latest" \
    "github.com/lc/gau/v2/cmd/gau@latest" \
    "github.com/hahwul/dalfox/v2@latest" \
    "github.com/tomnomnom/httprobe@latest" \
    "github.com/tomnomnom/assetfinder@latest"; do
    echo -e "${YEL}  → $pkg${NC}"
    go install "$pkg" 2>&1 | tail -1
done
  echo -e "${YEL}  → github.com/owasp-amass/amass/v4/...@master${NC}"
  go install github.com/owasp-amass/amass/v4/...@master 2>&1 | tail -1
  echo -e "${CYN}[+] Updating BBOT...${NC}"
  pip install --user --upgrade --break-system-packages bbot 2>&1 | tail -3
  pip install --user --upgrade --break-system-packages git-dumper linkfinder truffleHog 2>&1 | tail -3
  echo -e "${GRN}[OK] All tools updated!${NC}"
}

# --- Full Recon Pipeline ---
run_recon() {
  local TARGET="$1"
  local OUTDIR="${2:-bb_recon_$(date +%Y%m%d_%H%M%S)}"
  [ -z "$TARGET" ] && { echo -e "${RED}Usage: $0 --recon domain.com [output_dir]${NC}"; exit 1; }
  mkdir -p "$OUTDIR"
  banner
echo -e "${BLU}${BOLD}[+] PHASE 0: Subdomain Enumeration${NC}"
  echo -e "${CYN}  → subfinder -d $TARGET -all${NC}"
  subfinder -d "$TARGET" -all -o "$OUTDIR/subfinder.txt" 2>&1
  echo -e "${GRN}  ✓ subfinder: $(wc -l "$OUTDIR/subfinder.txt" 2>/dev/null | awk '{print $1}' || echo 0) subdomains${NC}"
  echo -e "${CYN}  → amass enum -d $TARGET${NC}"
  amass enum -d "$TARGET" -o "$OUTDIR/amass.txt" -passive 2>&1
  echo -e "${GRN}  ✓ amass: $(wc -l < "$OUTDIR/amass.txt" 2>/dev/null || echo 0) subdomains${NC}"

echo -e "${BLU}${BOLD}[+] PHASE 1: Asset Discovery + Probing${NC}"
  (cat "$OUTDIR/subfinder.txt" "$OUTDIR/amass.txt" 2>/dev/null | sort -u) > "$OUTDIR/all_subs.txt"
  TOTAL=$(wc -l < "$OUTDIR/all_subs.txt" 2>/dev/null || echo 0)
  echo -e "${YEL}  📊 Total unique subdomains: $TOTAL${NC}"
  echo -e "${CYN}  → httpx probing all hosts...${NC}"
  cat "$OUTDIR/all_subs.txt" | httpx -title -td -sc -o "$OUTDIR/httpx.txt" -silent 2>&1
  echo -e "${GRN}  ✓ httpx: $(wc -l < "$OUTDIR/httpx.txt" 2>/dev/null || echo 0) live hosts${NC}"

echo -e "${BLU}${BOLD}[+] PHASE 2: Port Scanning${NC}"
  echo -e "${CYN}  → naabu top-1000 ports...${NC}"
  naabu -list "$OUTDIR/all_subs.txt" -o "$OUTDIR/naabu.txt" -top-ports 1000 2>&1
  echo -e "${GRN}  ✓ naabu: $(wc -l < "$OUTDIR/naabu.txt" 2>/dev/null || echo 0) open ports${NC}"

echo -e "${BLU}${BOLD}[+] PHASE 3: Web Crawling (Katana)${NC}"
  echo -e "${CYN}  → katana crawling all hosts...${NC}"
  katana -list "$OUTDIR/all_subs.txt" -o "$OUTDIR/katana.txt" -jc 2>&1
  echo -e "${GRN}  ✓ katana: $(wc -l < "$OUTDIR/katana.txt" 2>/dev/null || echo 0) URLs crawled${NC}"

echo -e "${BLU}${BOLD}[+] PHASE 4: URL Discovery${NC}"
  echo -e "${CYN}  → waybackurls...${NC}"
  cat "$OUTDIR/all_subs.txt" | waybackurls 2>&1 | tee "$OUTDIR/waybackurls.txt" >/dev/null
  echo -e "${GRN}  ✓ waybackurls: $(wc -l < "$OUTDIR/waybackurls.txt" 2>/dev/null || echo 0) URLs${NC}"
  echo -e "${CYN}  → gau...${NC}"
  cat "$OUTDIR/all_subs.txt" | gau 2>&1 | tee "$OUTDIR/gau.txt" >/dev/null
  echo -e "${GRN}  ✓ gau: $(wc -l < "$OUTDIR/gau.txt" 2>/dev/null || echo 0) URLs${NC}"

echo -e "${BLU}${BOLD}[+] PHASE 5: Fuzzing (FFUF)${NC}"
  local COUNT=0
  for line in $(head -5 "$OUTDIR/all_subs.txt"); do
    echo -e "${CYN}  → ffuf https://$line/FUZZ${NC}"
    ffuf -u "https://$line/FUZZ" -w /usr/share/wordlists/dirb/common.txt -mc 200,301,302,403 -o "$OUTDIR/ffuf_${line}.json" -of json 2>&1
    COUNT=$((COUNT+1))
  done
  echo -e "${GRN}  ✓ ffuf: $COUNT targets fuzzed${NC}"

echo -e "${BLU}${BOLD}[+] PHASE 6: Vulnerability Scanning (Nuclei)${NC}"
  echo -e "${CYN}  → nuclei scanning...${NC}"
  nuclei -l "$OUTDIR/all_subs.txt" -o "$OUTDIR/nuclei.txt" -severity critical,high,medium 2>&1
  echo -e "${GRN}  ✓ nuclei: $(wc -l < "$OUTDIR/nuclei.txt" 2>/dev/null || echo 0) findings${NC}"

echo -e "${BLU}${BOLD}[+] PHASE 7: XSS Scanning (Dalfox)${NC}"
  echo -e "${CYN}  → dalfox XSS scan...${NC}"
  dalfox file "$OUTDIR/all_subs.txt" --output "$OUTDIR/dalfox.txt" 2>&1
  echo -e "${GRN}  ✓ dalfox: $(wc -l < "$OUTDIR/dalfox.txt" 2>/dev/null || echo 0) XSS findings${NC}"

echo -e "${GRN}${BOLD}[★] DONE! Results in: $OUTDIR/${NC}"
ls -lah "$OUTDIR/"
}

# --- Deep BBOT Recon ---
run_bbot() {
  local TARGET="$1"
  [ -z "$TARGET" ] && { echo -e "${RED}Usage: $0 --bbot domain.com${NC}"; exit 1; }
  echo -e "${MAG}[+] BBOT Full Recon on $TARGET${NC}"
  bbot -t "$TARGET" -f subdomain-enum web-basic paramminer web-screenshots 2>&1 | tail -10
}

# --- WiFi Challenge Launcher ---
run_wifi() {
  echo -e "${MAG}[+] WiFi Challenge: CHALLENGE5${NC}"
  hashcat -m 22000 /home/admin_user/grok_engine/CHALLENGE5_WIFI.hc22000 /usr/share/wordlists/rockyou.txt.gz --force -a 0 -o /tmp/wifi_cracked.txt 2>&1 | tail -10
  echo -e "${GRN}[+] Result:"${NC}
  cat /tmp/wifi_cracked.txt 2>&1
}

# --- Main Menu ---
case "${1:-}" in
  --check|-c)   banner; check_deps ;;
  --update|-u)  update_tools ;;
  --recon|-r)   shift; run_recon "$@" ;;
  --bbot|-b)    shift; run_bbot "$@" ;;
  --wifi|-w)    run_wifi ;;
  --full|-f)    shift; run_recon "$@" ;;
  --help|-h|'') banner
echo -e "${CYN}  --check   Check all tools${NC}"
echo -e "${CYN}  --update  Install/update all tools${NC}"
echo -e "${CYN}  --recon <domain>  Full recon pipeline${NC}"
echo -e "${CYN}  --bbot  <domain>  BBOT aggressive scan${NC}"
echo -e "${CYN}  --wifi           WiFi Challenge 5${NC}"
echo -e "${CYN}  --full  <domain>  Alias for --recon${NC}"
    echo -e "${MAG}|=================================================|${NC}"
    ;;
  *) echo -e "${RED}Unknown: $1${NC}"; $0 --help ;;
esac
