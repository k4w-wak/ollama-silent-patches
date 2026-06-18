#!/bin/bash
# ═══════════════════════════════════════════════════════
# RECON LOOP — Continuously harvest fresh intel for Grok
# Runs 24/7 in background, feeds ~/06_osint_forensics/live/
# ═══════════════════════════════════════════════════════

RECON_DIR="$HOME/06_osint_forensics/live"
mkdir -p "$RECON_DIR"
LOG="$RECON_DIR/recon.log"

# Bounty targets - add more as needed
TARGETS=(
    "coinbase.com"
    "kraken.com"
    "bitfinex.com"
    "slack.com"
    "netflix.com"
    "snapchat.com"
    "dropbox.com"
    "discord.com"
    "spotify.com"
    "airbnb.com"
)

echo "[$(date)] RECON LOOP started — $(echo ${TARGETS[@]} | wc -w) targets" >> "$LOG"

while true; do
    TIMESTAMP=$(date +%Y%m%d_%H%M)
    
    for TARGET in "${TARGETS[@]}"; do
        SAFE=$(echo "$TARGET" | tr '.' '_')
        DIR="$RECON_DIR/$SAFE"
        mkdir -p "$DIR"
        
        echo "[$(date)] === $TARGET ===" >> "$LOG"
        
        # 1. Subfinder — fresh subdomains
        subfinder -d "$TARGET" -silent -all 2>/dev/null | sort -u > "$DIR/subs_$TIMESTAMP.txt" 2>/dev/null
        SUB_COUNT=$(wc -l < "$DIR/subs_$TIMESTAMP.txt" 2>/dev/null || echo 0)
        echo "  subfinder: $SUB_COUNT subs" >> "$LOG"
        
        # Merge into master subs list (dedup)
        cat "$DIR"/subs_*.txt 2>/dev/null | sort -u > "$DIR/subs_all.txt"
        
        # 2. httpx — live hosts
        if [ -f "$DIR/subs_all.txt" ] && [ -s "$DIR/subs_all.txt" ]; then
            httpx -l "$DIR/subs_all.txt" -silent -status-code -title -tech-detect -follow-redirects 2>/dev/null | sort -u > "$DIR/live_$TIMESTAMP.txt"
            LIVE_COUNT=$(wc -l < "$DIR/live_$TIMESTAMP.txt" 2>/dev/null || echo 0)
            echo "  httpx: $LIVE_COUNT live hosts" >> "$LOG"
            
            # Merge
            cat "$DIR"/live_*.txt 2>/dev/null | sort -u > "$DIR/live_all.txt"
        fi
        
        # 3. dnsx — DNS records
        if [ -f "$DIR/subs_all.txt" ] && [ -s "$DIR/subs_all.txt" ]; then
            dnsx -l "$DIR/subs_all.txt" -silent -a -aaaa -cname -mx -ns -txt 2>/dev/null | sort -u > "$DIR/dns_$TIMESTAMP.txt"
            echo "  dnsx: $(wc -l < "$DIR/dns_$TIMESTAMP.txt" 2>/dev/null || echo 0) records" >> "$LOG"
        fi
        
        # Clean old files (keep last 10 runs per target)
        ls -t "$DIR"/subs_*.txt 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null
        ls -t "$DIR"/live_*.txt 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null
        ls -t "$DIR"/dns_*.txt 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null
        
        echo "[$(date)] $TARGET done — subs: $(wc -l < "$DIR/subs_all.txt" 2>/dev/null || echo 0), live: $(wc -l < "$DIR/live_all.txt" 2>/dev/null || echo 0)" >> "$LOG"
    done
    
    echo "[$(date)] === CYCLE COMPLETE — sleeping 6h ===" >> "$LOG"
    sleep 21600  # 6 hours between cycles
done
