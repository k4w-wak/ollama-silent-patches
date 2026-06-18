#!/bin/bash
# ============================================================================
# Ollama Exposed Instance Scanner
# Scans for unauthenticated Ollama instances
# Based on LIVE_SCAN_RESULTS.md methodology
# ============================================================================

echo "========================================================================"
echo "  Ollama Exposed Instance Scanner"
echo "  Methodology: Version check → Model enumeration → API deep scan"
echo "========================================================================"
echo ""

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "Installing jq..."
    sudo apt-get install -y jq 2>/dev/null || brew install jq 2>/dev/null
fi

# Target list (from live scan results)
TARGETS=(
    "[REDACTED_IP_1]"
    "[REDACTED_IP_2]"
)

# Or accept targets from command line
if [ $# -gt 0 ]; then
    TARGETS=("$@")
fi

scan_ollama() {
    local TARGET="$1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Scanning: $TARGET:11434"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Step 1: Version check
    echo ""
    echo "[1] VERSION CHECK:"
    VERSION=$(curl -s --connect-timeout 5 "http://$TARGET:11434/api/version" 2>/dev/null)
    if [ -z "$VERSION" ]; then
        echo "  ❌ No response (offline or firewalled)"
        return
    fi
    echo "  ✅ $VERSION"
    
    # Extract version number
    VER_NUM=$(echo "$VERSION" | jq -r '.version // empty')
    if [ -n "$VER_NUM" ]; then
        echo "  Version: $VER_NUM"
        
        # Check CVE-2026-7482 vulnerability
        MAJOR=$(echo "$VER_NUM" | cut -d. -f1)
        MINOR=$(echo "$VER_NUM" | cut -d. -f2)
        PATCH=$(echo "$VER_NUM" | cut -d. -f3)
        
        if [ "$MAJOR" -eq 0 ] && [ "$MINOR" -lt 17 ]; then
            echo "  🔴 VULNERABLE to CVE-2026-7482 (Bleeding Llama)"
        elif [ "$MAJOR" -eq 0 ] && [ "$MINOR" -eq 17 ] && [ "$PATCH" -lt 1 ]; then
            echo "  🔴 VULNERABLE to CVE-2026-7482 (Bleeding Llama)"
        else
            echo "  🟡 May contain other vulnerabilities"
        fi
    fi
    
    # Step 2: Model enumeration
    echo ""
    echo "[2] MODEL ENUMERATION:"
    MODELS=$(curl -s --connect-timeout 5 "http://$TARGET:11434/api/tags" 2>/dev/null)
    if [ -z "$MODELS" ]; then
        echo "  ❌ No response"
        return
    fi
    
    MODEL_COUNT=$(echo "$MODELS" | jq '.models | length' 2>/dev/null)
    echo "  ✅ Found $MODEL_COUNT models"
    
    # List model names
    echo "  Models:"
    echo "$MODELS" | jq -r '.models[].name' 2>/dev/null | while read model; do
        echo "    - $model"
    done
    
    # Check for hermes_pwn (attacker artifact)
    if echo "$MODELS" | jq -r '.models[].name' 2>/dev/null | grep -qi "hermes_pwn\|pwn\|hack\|backdoor"; then
        echo "  🔴 ATTACKER ARTIFACT DETECTED (hermes_pwn or similar)"
    fi
    
    # Calculate total storage
    TOTAL_SIZE=$(echo "$MODELS" | jq '[.models[].size] | add' 2>/dev/null)
    if [ -n "$TOTAL_SIZE" ] && [ "$TOTAL_SIZE" != "null" ]; then
        TOTAL_GB=$(echo "scale=2; $TOTAL_SIZE / 1073741824" | bc 2>/dev/null || echo "$TOTAL_SIZE bytes")
        echo "  Total storage: ${TOTAL_GB} GB"
    fi
    
    # Step 3: Check for path leaks
    echo ""
    echo "[3] PATH LEAK CHECK:"
    PUSH_RESP=$(curl -s --connect-timeout 5 "http://$TARGET:11434/api/push" -d '{"name":"test"}' 2>/dev/null)
    if echo "$PUSH_RESP" | grep -qi "D:\\\\"; then
        echo "  🔴 Windows path leak detected: $(echo "$PUSH_RESP" | grep -o 'D:\\[^"]*')"
    elif echo "$PUSH_RESP" | grep -qi "/root/"; then
        echo "  🔴 Linux path leak detected: $(echo "$PUSH_RESP" | grep -o '/root/[^"]*')"
    elif echo "$PUSH_RESP" | grep -qi "/home/"; then
        echo "  🔴 Linux path leak detected: $(echo "$PUSH_RESP" | grep -o '/home/[^"]*')"
    else
        echo "  🟡 No obvious path leak in push response"
    fi
    
    # Step 4: API endpoints check
    echo ""
    echo "[4] API ENDPOINT CHECK:"
    for endpoint in "api/create" "api/push" "api/pull" "api/delete" "api/copy" "api/generate" "api/chat" "api/embeddings" "api/show"; do
        RESP=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "http://$TARGET:11434/$endpoint" 2>/dev/null)
        if [ "$RESP" != "000" ]; then
            echo "  ✅ /$endpoint → HTTP $RESP"
        fi
    done
    
    # Step 5: CVE checks
    echo ""
    echo "[5] VULNERABILITY ASSESSMENT:"
    if [ -n "$VER_NUM" ]; then
        echo "  Version: $VER_NUM"
        
        # CVE-2024-7773 (RCE zip slip) — pre-v0.1.47
        if [ "$MAJOR" -eq 0 ] && [ "$MINOR" -eq 0 ] && [ "$PATCH" -lt 47 ]; then
            echo "  🔴 CVE-2024-7773 (RCE zip slip) — VULNERABLE"
        fi
        
        # CVE-2024-37032 (RCE path traversal) — pre-v0.1.34
        if [ "$MAJOR" -eq 0 ] && [ "$MINOR" -eq 0 ] && [ "$PATCH" -lt 34 ]; then
            echo "  🔴 CVE-2024-37032 (RCE path traversal) — VULNERABLE"
        fi
        
        # CVE-2025-51471 (token theft) — pre-v0.6.8
        if [ "$MAJOR" -eq 0 ] && [ "$MINOR" -lt 6 ]; then
            echo "  🟡 CVE-2025-51471 (token theft) — possibly vulnerable"
        elif [ "$MAJOR" -eq 0 ] && [ "$MINOR" -eq 6 ] && [ "$PATCH" -lt 8 ]; then
            echo "  🟡 CVE-2025-51471 (token theft) — possibly vulnerable"
        fi
        
        # PR #16380/#16436 (SSRF) — pre-v0.30.2
        if [ "$MAJOR" -eq 0 ] && [ "$MINOR" -lt 30 ]; then
            echo "  🟡 PR #16380/#16436 (SSRF) — vulnerable"
        elif [ "$MAJOR" -eq 0 ] && [ "$MINOR" -eq 30 ] && [ "$PATCH" -lt 2 ]; then
            echo "  🟡 PR #16380/#16436 (SSRF) — vulnerable"
        fi
        
        # PR #16100 (update RCE) — pre-v0.30.0
        if [ "$MAJOR" -eq 0 ] && [ "$MINOR" -lt 30 ]; then
            echo "  🔴 PR #16100 (update MITM RCE) — vulnerable"
        fi
    fi
    
    echo ""
}

# Run scan
for target in "${TARGETS[@]}"; do
    scan_ollama "$target"
done

echo "========================================================================"
echo "  Scan complete. For full methodology see LIVE_SCAN_RESULTS.md"
echo "========================================================================"