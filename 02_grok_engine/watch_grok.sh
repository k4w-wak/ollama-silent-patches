#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  GROK v4 LIVE MONITOR — THINKING EDITION
#  Brug: bash ~/Skrivebord/projekter/grok/watch_grok.sh
#
#  💀 PI sætter missioner og retter bugs
#  🤖 GROK kører tools og eksekverer
# ═══════════════════════════════════════════════════════════════

GROK_LOG="$HOME/.grok/logs/grok.log"

# Farver
R='\033[0;31m'
G='\033[0;32m'
Y='\033[0;33m'
B='\033[0;34m'
M='\033[0;35m'
C='\033[0;36m'
D='\033[2m'
Bd='\033[1m'
RST='\033[0m'
BG_Y='\033[43m\033[30m'  # Gul baggrund, sort tekst
BG_C='\033[46m\033[30m'  # Cyan baggrund, sort tekst
BG_R='\033[41m\033[37m'  # Rød baggrund, hvid tekst

if [ ! -f "$GROK_LOG" ]; then
    mkdir -p "$HOME/.grok/logs"
    touch "$GROK_LOG"
fi

clear
echo -e "${G}╔═══════════════════════════════════════════════════════════╗${RST}"
echo -e "${G}║  ${Bd}💀 GROK v4 — LIVE MONITOR (Thinking Edition)${RST}${G}          ║${RST}"
echo -e "${G}║  ${D}Ollama FC • 💭 Thinking • 6 Konger • 138 Tools${RST}${G}  ║${RST}"
echo -e "${G}║  ${D}PI = missioner & bugfix • GROK = eksekvering${RST}${G}         ║${RST}"
echo -e "${G}╚═══════════════════════════════════════════════════════════╝${RST}"
echo ""

model=$(curl -s -m 3 http://localhost:11434/api/ps 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['models'][0]['name']) if d.get('models') else print('ingen')" 2>/dev/null || echo "offline")
log_size=$(du -h "$GROK_LOG" 2>/dev/null | cut -f1)
lines=$(wc -l < "$GROK_LOG" 2>/dev/null || echo "0")

echo -e "${D}┌─────────────────────────────────────────────────────────────┐${RST}"
echo -e "${D}│${RST} ${C}Model:${RST} ${Bd}${model}${RST}    ${D}│${RST} ${C}Log:${RST} ${log_size} (${lines} linjer)"
echo -e "${D}└─────────────────────────────────────────────────────────────┘${RST}"
echo ""
echo -e "${BG_Y} 💭 THINKING = Hvad Grok tænker før den handler ${RST}"
echo -e "${BG_C} ⚡ ACTION = Hvilket tool Grok bruger             ${RST}"
echo -e "${G} 📊 OBSERVATION = Hvad tool'et returnerer          ${RST}"
echo -e "${Y} 💀 GROK SVAR = Endeligt svar fra Grok             ${RST}"
echo -e "${R} 🔴 FEJL = Noget gik galt                         ${RST}"
echo ""
echo -e "${D}Venter paa aktivitet... (Ctrl+C for at stoppe)${RST}"
echo ""

# Konge emoji baseret på tool navn
konge() {
    case "$1" in
        msf_*|metasploit*) printf "💀" ;;
        beef*) printf "🕸️" ;;
        setoolkit*) printf "🎭" ;;
        zap*|zap_scan*) printf "🔍" ;;
        gvm*) printf "🛡️" ;;
        burpsuite*) printf "📡" ;;
        nmap*) printf "📡" ;;
        sql_injection*) printf "💉" ;;
        responder*) printf "📡" ;;
        enum4linux*) printf "🔍" ;;
        smb_enum*) printf "🔍" ;;
        crackmapexec*) printf "💀" ;;
        osint_*|web_search*) printf "🌐" ;;
        ollama_vision*) printf "👁️" ;;
        ollama_embed*) printf "🔢" ;;
        file_*) printf "📄" ;;
        password_*|hashcat*) printf "🔐" ;;
        packet_capture*) printf "📦" ;;
        *) printf "▸" ;;
    esac
}

tail -f "$GROK_LOG" 2>/dev/null | while IFS= read -r line; do
    timestamp=$(echo "$line" | grep -oP '\[\K[0-9:]+(?=\])' 2>/dev/null || echo "")
    
    if echo "$line" | grep -qi "THINKING:"; then
        # 💭 THINKING — fuld længde, prominent display
        thinking=$(echo "$line" | sed 's/.*THINKING: //')
        echo ""
        echo -e "${BG_Y} 💭 THINKING ${RST}${Y}${Bd}─────────────────────────────────────────${RST}"
        # Vis hele tænknings-teksten (ikke trunkeret)
        echo -e "${Y}${thinking}${RST}"
        echo -e "${Y}${D}──────────────────────────────────────────────────${RST}"
        echo ""
    
    elif echo "$line" | grep -qi "ACTION:"; then
        tool=$(echo "$line" | sed 's/.*ACTION: //' | cut -d'|' -f1 | tr -d ' {}' | cut -d'(' -f1)
        args=$(echo "$line" | sed 's/.*ACTION: //' | cut -c1-200)
        emoji=$(konge "$tool")
        echo -e "${BG_C} ${emoji} ACTION ${RST} ${C}${Bd}${tool}${RST} ${D}${args:$((${#tool}+1)):150}${RST}"
    
    elif echo "$line" | grep -qi "OBSERVATION"; then
        # Truncher observationer til 200 tegn men behold vigtigt
        short=$(echo "$line" | sed 's/.*OBSERVATION: //' | cut -c1-200)
        echo -e "  ${G}📊 ${short}${RST}"
    
    elif echo "$line" | grep -qi "FEJL\|ERROR\|TIMEOUT\|Broken pipe"; then
        echo -e "  ${R}${Bd}🔴 $(echo "$line" | cut -c1-200)${RST}"
    
    elif echo "$line" | grep -qi "GROK SVAR"; then
        svar=$(echo "$line" | sed 's/.*GROK SVAR: //' | cut -c1-300)
        echo ""
        echo -e "${Y}${Bd}╔══════════════════════════════════════╗${RST}"
        echo -e "${Y}${Bd}║ 💀 GROK SVAR${RST}"
        echo -e "${Y}${Bd}╚══════════════════════════════════════╝${RST}"
        echo -e "${Y}${svar}${RST}"
        echo ""
    
    elif echo "$line" | grep -qi "Ollama FC\|tools:\|Model.*underst"; then
        echo -e "  ${D}⚙️  $(echo "$line" | cut -c1-120)${RST}"
    
    elif echo "$line" | grep -qi "▶"; then
        # Tool execution log
        echo -e "  ${D}$(echo "$line" | cut -c1-150)${RST}"
    
    elif echo "$line" | grep -qi "◆"; then
        # Tool result log
        echo -e "  ${D}$(echo "$line" | cut -c1-150)${RST}"
    
    else
        echo -e "${D}$(echo "$line" | cut -c1-200)${RST}"
    fi
done