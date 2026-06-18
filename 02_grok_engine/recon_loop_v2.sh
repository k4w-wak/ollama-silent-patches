#!/bin/bash
export PATH=/home/admin_user/go/bin:$PATH
export GOPATH=/home/admin_user/go
RECON_DIR="$HOME/06_osint_forensics/live"
NUCLEI_DIR="$HOME/06_osint_forensics/nuclei"
mkdir -p "$RECON_DIR" "$NUCLEI_DIR"
LOG="$RECON_DIR/recon_v2.log"
TARGETS=(coinbase.com kraken.com bitfinex.com slack.com netflix.com snapchat.com dropbox.com discord.com spotify.com airbnb.com stake.com roobet.com rollbit.com primedice.com duelbits.com cloudbet.com luckyblock.com bc.game bitstarz.com)
echo "[$(date)] RECON LOOP v2 started - ${#TARGETS[@]} targets" >> "$LOG"
while true; do
    TIMESTAMP=$(date +%Y%m%d_%H%M)
    ALL_LIVE="/tmp/all_live_$TIMESTAMP.txt"
    > "$ALL_LIVE"
    for TARGET in "${TARGETS[@]}"; do
        SAFE=$(echo "$TARGET" | tr '.' '_')
        DIR="$RECON_DIR/$SAFE"
        mkdir -p "$DIR"
        echo "[$(date)] === $TARGET ===" >> "$LOG"
        subfinder -d "$TARGET" -silent -all 2>/dev/null | sort -u > "$DIR/subs_$TIMESTAMP.txt"
        SUB_COUNT=$(wc -l < "$DIR/subs_$TIMESTAMP.txt" 2>/dev/null || echo 0)
        echo "  subfinder: $SUB_COUNT subs" >> "$LOG"
        cat "$DIR"/subs_*.txt 2>/dev/null | sort -u > "$DIR/subs_all.txt"
        if [ -f "$DIR/subs_all.txt" ] && [ -s "$DIR/subs_all.txt" ]; then
            /home/admin_user/go/bin/httpx -l "$DIR/subs_all.txt" -silent -status-code -title -tech-detect -follow-redirects -rate-limit 200 2>/dev/null | sort -u > "$DIR/live_$TIMESTAMP.txt"
            LIVE_COUNT=$(wc -l < "$DIR/live_$TIMESTAMP.txt" 2>/dev/null || echo 0)
            echo "  httpx: $LIVE_COUNT live hosts" >> "$LOG"
            cat "$DIR/live_$TIMESTAMP.txt" >> "$ALL_LIVE"
            cat "$DIR"/live_*.txt 2>/dev/null | sort -u > "$DIR/live_all.txt"
        fi
        dnsx -l "$DIR/subs_all.txt" -silent -a -aaaa -cname -mx -ns -txt 2>/dev/null | sort -u > "$DIR/dns_$TIMESTAMP.txt"
        echo "  dnsx: $(wc -l < "$DIR/dns_$TIMESTAMP.txt" 2>/dev/null || echo 0) records" >> "$LOG"
        ls -t "$DIR"/subs_*.txt 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null
        ls -t "$DIR"/live_*.txt 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null
        ls -t "$DIR"/dns_*.txt 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null
        TOTAL_SUBS=$(wc -l < "$DIR/subs_all.txt" 2>/dev/null || echo 0)
        TOTAL_LIVE=$(wc -l < "$DIR/live_all.txt" 2>/dev/null || echo 0)
        echo "[$(date)] $TARGET done - subs: $TOTAL_SUBS, live: $TOTAL_LIVE" >> "$LOG"
    done
    if [ -s "$ALL_LIVE" ]; then
        echo "[$(date)] NUCLEI scan - $(wc -l < $ALL_LIVE) live hosts" >> "$LOG"
        /home/admin_user/go/bin/nuclei -l "$ALL_LIVE" -severity critical,high -o "$NUCLEI_DIR/nuclei_$TIMESTAMP.txt" -rl 150 -c 50 2>>"$LOG"
        echo "[$(date)] Nuclei done - $(wc -l < $NUCLEI_DIR/nuclei_$TIMESTAMP.txt 2>/dev/null || echo 0) findings" >> "$LOG"
    fi
    rm -f "$ALL_LIVE"
    echo "[$(date)] CYCLE COMPLETE - sleeping 4h" >> "$LOG"
    sleep 14400
done