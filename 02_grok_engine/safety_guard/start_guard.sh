#!/bin/bash
# ================================================================
# 🔥 GROK SAFETY GUARD — MASTER START SCRIPT 🔥
# Start alt overvågning på én gang
# ================================================================

GUARD_DIR="$HOME/02_grok_engine/safety_guard"

RED='\033[91m'; GREEN='\033[92m'; YELLOW='\033[93m'; CYAN='\033[96m'; BOLD='\033[1m'; RESET='\033[0m'

echo -e "${BOLD}${RED}══════════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${RED}     🔥🔥🔥 GROK SAFETY GUARD — MISSION MODE START 🔥🔥🔥${RESET}"
echo -e "${BOLD}${RED}══════════════════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "  ${BOLD}Din IP:${RESET}    <REDACTED_IP> (TDC Mobile, DK)"
echo -e "  ${BOLD}Lokal IP:${RESET}  172.22.29.16"
echo -e "  ${BOLD}Host:${RESET}     DESKTOP-P7SU64O"
echo -e "  ${BOLD}User:${RESET}     admin_user"
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}  OVERVÅGNINGSAKTIVERET:${RESET}"
echo ""
echo -e "  ${RED}🔴  IP-overvågning${RESET}        — Alarmerer hvis din IP ændres"
echo -e "  ${RED}🔴  Port-scan detektion${RESET}   — Nye porte = ALARM"
echo -e "  ${RED}🔴  Reverse shell detektion${RESET}— Skjulte shells = KRITISK ALARM"
echo -e "  ${RED}🔴  Cryptominer detektion${RESET} — Xmrig etc = KRITISK ALARM"
echo -e "  ${YELLOW}🟡  Procesovervågning${RESET}     — Mistænkelige processer"
echo -e "  ${YELLOW}🟡  Filændrings-detektion${RESET}— Kritiske filer overvåges"
echo -e "  ${CYAN}🔵  Netværksforbindelser${RESET}  — Eksterne forbindelser logges"
echo -e "  ${CYAN}🔵  SSH-nøgler${RESET}           — Uautoriserede nøgler alarmeres"
echo -e "  ${CYAN}🔵  ARP/MITM detektion${RESET}   — ARP spoofing detekteres"
echo -e "  ${CYAN}🔵  Brute force detektion${RESET}— Mislykkede logins tælles"
echo -e "  ${CYAN}🔵  USB-enheder${RESET}          — Nye USB-enheder logges"
echo -e "  ${CYAN}🔵  Disk/RAM/CPU${RESET}         — System-sundhed overvåges"
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}  CRON-JOBS AKTIVE:${RESET}"
echo -e "  ⏱️  Watchdog:      Hvert 2. minut"
echo -e "  ⏱️  Full Python:   Hvert 10. minut"
echo -e "  ⏱️  Aggressive:    Hvert 5. minut"
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}  KOMMANDOER:${RESET}"
echo ""
echo -e "  ${GREEN}./watchdog.sh${RESET}           — Én gang fuld scanning"
echo -e "  ${GREEN}./realtime_guard.sh 30${RESET}  — Real-tid overvågning (30s interval)"
echo -e "  ${GREEN}./aggressive_guard.sh run${RESET}— Scan + bloker trusler"
echo -e "  ${GREEN}./aggressive_guard.sh block IP${RESET} — Bloker en IP"
echo -e "  ${GREEN}./aggressive_guard.sh status${RESET}  — Vis blokerings-status"
echo -e "  ${GREEN}python3 grok_safety_guard.py monitor 60${RESET} — Python real-tid"
echo ""
echo -e "${BOLD}${RED}══════════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${RED}  🔥 ALT ER AKTIVERET — DU ER BESKYTTET 🔥${RESET}"
echo -e "${BOLD}${RED}══════════════════════════════════════════════════════════════════${RESET}"

# Kør første scan
echo ""
echo -e "${BOLD}Kører første scanning...${RESET}"
bash "$GUARD_DIR/watchdog.sh" 2>&1 | tail -5

echo ""
echo -e "${GREEN}${BOLD}✅ SAFETY GUARD AKTIV — Kører i baggrunden via cron${RESET}"