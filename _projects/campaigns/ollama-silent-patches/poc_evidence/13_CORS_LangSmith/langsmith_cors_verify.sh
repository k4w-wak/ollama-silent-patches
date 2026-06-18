#!/bin/bash
echo "============================================================"
echo "  🔴🔴🔴 LangSmith 402-Endpoint CORS Verification"
echo "============================================================"
echo ""
echo "[1] Arbitrary Origin with ALL Methods:"
curl -sI -H "Origin: https://evil.com" -X OPTIONS \
  -H "Access-Control-Request-Method: DELETE" \
  https://api.smith.langchain.com/api/v1/workspaces/current/secrets | \
  grep -i "access-control"
echo ""
echo "[2] Null Origin Bypass:"
curl -sI -H "Origin: null" https://api.smith.langchain.com/api/v1/sessions | \
  grep -i "access-control"
echo ""
echo "[3] API Key Endpoint:"
curl -sI -H "Origin: https://evil.com" https://api.smith.langchain.com/api/v1/api-key | \
  grep -i "access-control"
echo ""
echo "============================================================"
