# 🔴🔴🔴 PoC EVIDENCE — COMPLETE CATALOG
## Ollama Disclosure + CORS Campaign — Anonymous

**Created:** 2026-06-07  
**Author:** grok-poc  
**Classification:** Public — Coordinated Disclosure  

---

## 📂 Directory Structure

```
poc_evidence/
├── 00_MASTER_INDEX.md                    ← THIS FILE
├── 01_SSRF_URL_Policy/
│   └── exploit_ssrf_url_policy.py        ← PR #16380 PoC
├── 02_Regex_Bypass/
│   └── exploit_regex_bypass.sh           ← PR #16436 PoC
├── 03_Update_RCE/
│   └── exploit_update_rce.py             ← PR #16100 PoC (CVE-2026-42248/42249)
├── 04_SDK_Leakage/
│   └── exploit_sdk_leakage.py            ← PR #16053 PoC
├── 05_Bleeding_Llama/
│   └── exploit_bleeding_llama.py          ← CVE-2026-7482 PoC
├── 06_Codex_Hijacking/
│   └── exploit_codex_hijack.py            ← PR #16437 PoC
├── 07_CVE_2026_5757/
│   └── exploit_cve_2026_5757.py           ← GGUF Memory Leak PoC (UNPATCHED)
├── 08_CORS_DeepInfra/
│   ├── exploit_deepinfra_cors.py          ← DeepInfra CORS PoC generator
│   ├── deepinfra_cors_poc.html           ← Interactive browser PoC
│   ├── deepinfra_cors_poc.png            ← Screenshot evidence
│   └── deepinfra_cors_verify.sh           ← Bash verification script
├── 09_CORS_DeepSeek/
│   ├── exploit_deepseek_cors.py          ← DeepSeek CORS PoC generator
│   ├── deepseek_cors_poc.html            ← Interactive browser PoC
│   ├── deepseek_cors_poc.png             ← Screenshot evidence
│   └── deepseek_cors_verify.sh           ← Bash verification script
├── 10_CORS_Hyperbolic/
│   ├── exploit_hyperbolic_cors.py         ← Hyperbolic CORS PoC generator
│   ├── hyperbolic_cors_poc.html          ← Interactive browser PoC
│   ├── hyperbolic_cors_poc.png           ← Screenshot evidence
│   └── hyperbolic_cors_verify.sh         ← Bash verification script
├── 11_CORS_Baichuan/
│   ├── exploit_baichuan_cors.py           ← Baichuan CORS PoC generator
│   ├── baichuan_cors_poc.html            ← Interactive browser PoC
│   ├── baichuan_cors_poc.png             ← Screenshot evidence
│   └── baichuan_cors_verify.sh           ← Bash verification script
├── 12_CORS_MiniMax/
│   ├── exploit_minimax_cors.py            ← MiniMax CORS PoC generator
│   ├── minimax_cors_poc.html             ← Interactive browser PoC
│   ├── minimax_cors_poc.png              ← Screenshot evidence
│   └── minimax_cors_verify.sh            ← Bash verification script
├── 13_CORS_LangSmith/
│   ├── exploit_langsmith_cors.py          ← LangSmith CORS PoC generator
│   ├── langsmith_cors_poc.html            ← Interactive browser PoC
│   ├── langsmith_cors_poc.png            ← Screenshot evidence
│   └── langsmith_cors_verify.sh          ← Bash verification script
├── 14_Live_Exposed_Instances/
│   └── exploit_exposed_instances.py       ← Exposed instance exploitation PoC
└── 15_Exposed_Instance_Scanner/
    └── ollama_exposed_scanner.sh          ← Automated Ollama instance scanner
```

---

## 🔴 FINDING SUMMARY — 15 PoCs

### Ollama Silent Patch Disclosure (9 findings)

| # | Finding | CVSS | CVE | Status | PoC |
|---|---------|------|-----|--------|-----|
| 01 | SSRF via Markdown URL Handling (PR #16380) | 7.5 | N/A | Silently Patched | `01_SSRF_URL_Policy/exploit_ssrf_url_policy.py` |
| 02 | URL Policy Regex Bypass (PR #16436) | 7.2 | N/A | Silently Patched | `02_Regex_Bypass/exploit_regex_bypass.sh` |
| 03 | Update Flow RCE — Path Traversal + Missing Integrity (PR #16100) | 9.1 | CVE-2026-42248/42249 | Silently Patched | `03_Update_RCE/exploit_update_rce.py` |
| 04 | macOS SDK Target Leakage (PR #16053) | 3.1 | N/A | Silently Patched | `04_SDK_Leakage/exploit_sdk_leakage.py` |
| 05 | CVE-2026-7482 "Bleeding Llama" Memory Leak | 9.1 | CVE-2026-7482 | Silently Patched | `05_Bleeding_Llama/exploit_bleeding_llama.py` |
| 06 | Codex Launch Configuration Hijacking (PR #16437) | 7.5 | N/A | Silently Patched | `06_Codex_Hijacking/exploit_codex_hijack.py` |
| 07 | CVE-2026-5757 GGUF Memory Leak | 5.3-9.8 (see note) | CVE-2026-5757 | 🔴 UNPATCHED | `07_CVE_2026_5757/exploit_cve_2026_5757.py` |

### CORS Campaign (6 findings)

| # | Target | CVSS | Type | PoC |
|---|--------|------|------|-----|
| 08 | api.deepinfra.com | 8.6 | CORS + Credentials + 321 models | `08_CORS_DeepInfra/deepinfra_cors_poc.html` |
| 09 | api.deepseek.com | 9.1 | CORS + Credentials + Null Origin | `09_CORS_DeepSeek/deepseek_cors_poc.html` |
| 10 | api.hyperbolic.xyz | 8.6 | CORS + Credentials + Null Origin | `10_CORS_Hyperbolic/hyperbolic_cors_poc.html` |
| 11 | api.baichuan-ai.com | 8.6 | CORS + Credentials + DELETE method | `11_CORS_Baichuan/baichuan_cors_poc.html` |
| 12 | api.minimaxi.chat | 9.1 | CORS + WeChat Pay + DELETE + Expose-Headers:* | `12_CORS_MiniMax/minimax_cors_poc.html` |
| 13 | api.smith.langchain.com | 9.8 | CORS + 402 endpoints + API key theft + Secrets | `13_CORS_LangSmith/langsmith_cors_poc.html` |

### Infrastructure (2 supporting items)

| # | Title | Description | PoC |
|---|-------|-------------|-----|
| 14 | Live Exposed Instances | 8 confirmed live, unauthenticated Ollama instances | `14_Live_Exposed_Instances/exploit_exposed_instances.py` |
| 15 | Instance Scanner | Automated vulnerability scanner for Ollama instances | `15_Exposed_Instance_Scanner/ollama_exposed_scanner.sh` |

---

## 🎯 HOW TO RUN EACH PoC

### Ollama PoCs (01-07, 14)
```bash
# All Python PoCs are self-contained demonstrations:
python3 poc_evidence/01_SSRF_URL_Policy/exploit_ssrf_url_policy.py
python3 poc_evidence/02_Regex_Bypass/exploit_regex_bypass.sh  # or bash
python3 poc_evidence/03_Update_RCE/exploit_update_rce.py
python3 poc_evidence/04_SDK_Leakage/exploit_sdk_leakage.py
python3 poc_evidence/05_Bleeding_Llama/exploit_bleeding_llama.py
python3 poc_evidence/06_Codex_Hijacking/exploit_codex_hijack.py
python3 poc_evidence/07_CVE_2026_5757/exploit_cve_2026_5757.py
python3 poc_evidence/14_Live_Exposed_Instances/exploit_exposed_instances.py

# Instance scanner:
bash poc_evidence/15_Exposed_Instance_Scanner/ollama_exposed_scanner.sh [IP_ADDRESSES]
```

### CORS PoCs (08-13)
```bash
# Verify all CORS findings:
bash poc_evidence/08_CORS_DeepInfra/deepinfra_cors_verify.sh
bash poc_evidence/09_CORS_DeepSeek/deepseek_cors_verify.sh
bash poc_evidence/10_CORS_Hyperbolic/hyperbolic_cors_verify.sh
bash poc_evidence/11_CORS_Baichuan/baichuan_cors_verify.sh
bash poc_evidence/12_CORS_MiniMax/minimax_cors_verify.sh
bash poc_evidence/13_CORS_LangSmith/langsmith_cors_verify.sh

# Interactive browser PoCs:
# Open *_cors_poc.html files in a browser while logged into the target service
```

---

## 📊 EVIDENCE CROSS-REFERENCE

| Finding | Source File | PR/CVE | PoC Type |
|---------|-----------|--------|----------|
| SSRF URL Policy | `FINDING_01_SSRF_URL_Policy.md` | PR #16380 | Python |
| Regex Bypass | `FINDING_02_Regex_Bypass.md` | PR #16436 | Bash |
| Update RCE | `FINDING_03_Update_Hardening.md` | CVE-2026-42248/42249, PR #16100 | Python |
| SDK Leakage | `FINDING_04_SDK_Leakage.md` | PR #16053 | Python |
| Bleeding Llama | `FINDING_05_Bleeding_Llama.md` | CVE-2026-7482 | Python |
| Codex Hijack | `FINDING_06_Codex_Hijacking.md` | PR #16437 | Python |
| CVE-2026-5757 | `08_CVE_DATABASE.md` + `FINAL_DISCLOSURE.md` | CVE-2026-5757 | Python |
| DeepInfra CORS | `SUBMISSIONS/01_deepinfra_cors/REPORT.md` | N/A | HTML + Bash |
| DeepSeek CORS | `SUBMISSIONS/02_deepseek_cors/REPORT.md` | N/A | HTML + Bash |
| Hyperbolic CORS | `SUBMISSIONS/03_hyperbolic_cors/REPORT.md` | N/A | HTML + Bash |
| Baichuan CORS | `SUBMISSIONS/04_baichuan_cors/REPORT.md` | N/A | HTML + Bash |
| MiniMax CORS | `SUBMISSIONS/05_minimaxi_cors/REPORT.md` | N/A | HTML + Bash |
| LangSmith CORS | `SUBMISSIONS/06_langsmith_cors/REPORT.md` | N/A | HTML + Bash |
| Exposed Instances | `LIVE_SCAN_RESULTS.md` + `06_EXPOSED_INSTANCES.md` | Multiple CVEs | Python |
| Scanner | Methodology from live scan | N/A | Bash |

---

## ⚠️ RESPONSIBLE DISCLOSURE NOTES

- All PoCs are **demonstration-only** — they show the vulnerability mechanism
- No actual exploitation of live targets was performed
- CORS PoCs require the victim to be authenticated on the target service
- The exposed instance scanner only probes public API endpoints that require no authentication
- Ollama vulnerabilities were discovered through **public source code analysis** (GitHub PRs)
- All findings have been or will be responsibly disclosed to the respective vendors

---

**Generated by:** grok-poc agent  
**Date:** 2026-06-07