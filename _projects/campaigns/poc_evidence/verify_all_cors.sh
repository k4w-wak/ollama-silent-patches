#!/bin/bash
# 🔴 CORS Verification Script — All 6 Critical Findings
# Run this to verify all CORS vulnerabilities before disclosure
# Author: Anonymous | Date: 2026-05-30

echo "============================================"
echo "  CORS Verification — 6 CRITICAL Findings"
echo "  Run via: bash verify_all_cors.sh"
echo "============================================"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_cors() {
    local name="$1"
    local url="$2"
    local origin="$3"
    local expected="$4"
    
    echo -e "${YELLOW}[$name]${NC} Testing Origin: $origin"
    result=$(curl -sI -H "Origin: $origin" "$url" 2>/dev/null | grep -i "access-control-allow-origin")
    
    if echo "$result" | grep -qi "$expected"; then
        echo -e "  ${GREEN}✅ VULNERABLE${NC}: $result"
    else
        echo -e "  ${RED}❌ NOT VULNERABLE${NC}: $result"
    fi
    
    # Check credentials
    creds=$(curl -sI -H "Origin: $origin" "$url" 2>/dev/null | grep -i "access-control-allow-credentials")
    if echo "$creds" | grep -qi "true"; then
        echo -e "  ${RED}⚠️  Credentials: true${NC}"
    else
        echo -e "  ${GREEN}Credentials: false or missing${NC}"
    fi
    echo ""
}

echo "=== 1. DeepInfra ==="
check_cors "DeepInfra" "https://api.deepinfra.com/v1/openai/models" "https://evil.com" "evil.com"
check_cors "DeepInfra-null" "https://api.deepinfra.com/v1/openai/models" "null" "null"

echo "=== 2. DeepSeek ==="
check_cors "DeepSeek" "https://api.deepseek.com/v1/models" "https://evil.com" "evil.com"
check_cors "DeepSeek-null" "https://api.deepseek.com/v1/models" "null" "null"

echo "=== 3. Hyperbolic ==="
check_cors "Hyperbolic" "https://api.hyperbolic.xyz/v1/models" "https://evil.com" "evil.com"
check_cors "Hyperbolic-null" "https://api.hyperbolic.xyz/v1/models" "null" "null"

echo "=== 4. Baichuan AI ==="
check_cors "Baichuan" "https://api.baichuan-ai.com/v1/chat/completions" "https://evil.com" "evil.com"
check_cors "Baichuan-null" "https://api.baichuan-ai.com/v1/chat/completions" "null" "null"

echo "=== 5. MiniMax ==="
check_cors "MiniMax" "https://api.minimaxi.chat/v1/chat/completions" "https://evil.com" "evil.com"
check_cors "MiniMax-null" "https://api.minimaxi.chat/v1/chat/completions" "null" "null"

echo "=== 6. LangSmith ==="
check_cors "LangSmith" "https://api.smith.langchain.com/api/v1/sessions" "https://evil.com" "evil.com"
check_cors "LangSmith-null" "https://api.smith.langchain.com/api/v1/sessions" "null" "null"

echo ""
echo "============================================"
echo "  Verification Complete"
echo "============================================"
echo ""
echo "For detailed testing, open the HTML PoC files in a browser."
echo "PoC files are in: ~/Skrivebord/SUBMISSIONS/*/