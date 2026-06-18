#!/bin/bash
# Watch Grok log in real-time
# Brug: ./watch_log.sh [antal_linjer]
# Eksempel: ./watch_log.sh 50

clear_log() {
    > ~/.grok/logs/grok.log
    echo "Log cleared!"
}

watch_log() {
    LINES=${1:-50}
    mkdir -p ~/.grok/logs
    touch ~/.grok/logs/grok.log
    tail -n "$LINES" -f ~/.grok/logs/grok.log
}

case "$1" in
    clear) clear_log ;;
    *) watch_log "$2" ;;
esac
