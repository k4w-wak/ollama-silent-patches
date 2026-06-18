#!/bin/bash
ADB=~/02_grok_engine/mobile_tools/adb
case "$1" in
    devices) $ADB devices -l ;;
    shell) shift; $ADB shell "$@" ;;
    install) shift; $ADB install -r "$@" ;;
    push) shift; $ADB push "$@" ;;
    pull) shift; $ADB pull "$@" ;;
    screenshot) 
        $ADB shell screencap -p /sdcard/screen.png
        $ADB pull /sdcard/screen.png "${2:-./phone_screenshot.png}"
        $ADB shell rm /sdcard/screen.png
        ;;
    logcat) shift; $ADB logcat -d "$@" ;;
    *) echo "Usage: adb_handler.sh {devices|shell|install|push|pull|screenshot|logcat}" ;;
esac
