#!/bin/bash
# GROK LIVE MONITOR - append mode, ingen clear/dropdown
# Kør: bash live_monitor.sh

echo "=== GROK LIVE MONITOR ==="
echo ""

LAST_FILES=""
while true; do
    NOW=$(date '+%H:%M:%S')
    
    # Tjek om nye sub-agenter er dukket op
    FILES=$(ls ~/.grok/agents/*.json 2>/dev/null | wc -l)
    
    # Tjek om nye osint filer
    OSINT=$(ls ~/06_osint_forensics/*.txt 2>/dev/null)
    
    # Se om noget har ændret sig
    CURRENT="$FILES|$OSINT"
    
    if [ "$CURRENT" != "$LAST_FILES" ]; then
        echo "[$NOW] Agenter: $FILES | Osint filer:"
        for f in ~/06_osint_forensics/*.txt 2>/dev/null; do
            echo "  $(basename $f) ($(du -h "$f" | cut -f1))"
        done
        echo ""
        LAST_FILES="$CURRENT"
    fi
    
    # Vis output fra den nyeste kørende agent
    for f in $(ls -t ~/.grok/agents/*-output.txt 2>/dev/null | head -1); do
        id=$(basename "$f" | cut -d- -f1)
        status=$(python3 -c "import json; d=json.load(open('$HOME/.grok/agents/$id.json')); print(d.get('status','?'))" 2>/dev/null)
        if [ "$status" = "running" ] || [ "$status" = "completed" ]; then
            NEW=$(tail -n +$((LAST_LINE_$id + 1)) "$f" 2>/dev/null | head -5)
            if [ -n "$NEW" ]; then
                echo "[$NOW] $id ($status):"
                echo "$NEW" | sed 's/^/  /'
                echo ""
            fi
            eval "LAST_LINE_$id=\$(wc -l < \"$f\")"
        fi
    done
    
    sleep 1.5
done
