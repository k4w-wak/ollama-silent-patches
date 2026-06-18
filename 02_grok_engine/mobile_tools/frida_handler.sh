#!/bin/bash
FRIDA=~/playwright-venv/bin/frida
case "$1" in
    list) $FRIDA-ps -U 2>/dev/null || echo "No device connected" ;;
    apps) $FRIDA-ps -Uai 2>/dev/null || echo "No device connected" ;;
    spawn) shift; $FRIDA -U -f "$@" ;;
    attach) shift; $FRIDA -U "$@" ;;
    trace) shift; $FRIDA-trace -U "$@" ;;
    *) echo "Usage: frida_handler.sh {list|apps|spawn|attach|trace}" ;;
esac
