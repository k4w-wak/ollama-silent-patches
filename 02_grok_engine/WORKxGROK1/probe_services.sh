#!/bin/bash
# Probe for exposed AI services
RESULTS="/home/admin_user/grok_engine/8hour_deep_dive/probe_results.txt"
> $RESULTS

check_service() {
    local ip=$1
    local port=$2
    local service=$3
    local path=$4
    
    result=$(curl -sk --connect-timeout 3 --max-time 5 "http://${ip}:${port}${path}" 2>/dev/null | head -c 200)
    if [ ! -z "$result" ]; then
        echo "[FOUND] ${service} at ${ip}:${port}${path} - ${result:0:100}" >> $RESULTS
    fi
}

echo "Probing started at $(date)"
echo "Results will be saved to $RESULTS"
