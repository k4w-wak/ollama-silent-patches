# OLLAMA+CHROMADB+MLFLOW HUNTER Report
Generated: 2026-06-02T21:13:01.359683Z
Scanner: v1.0 | OPSEC: Tor SOCKS5

## Executive Summary

| Platform | Alive | CVEs Tested | Potentially Vulnerable |
|----------|-------|-------------|----------------------|
| Ollama | 1 | 1 | 0 |
| ChromaDB | 1 | 1 | 0 |
| MLflow | 0 | 4 | 0 |

## CVEs Tested

| CVE | Platform | CVSS | Type | Status |
|-----|----------|------|------|--------|
| CVE-2026-7482 | Ollama | 9.3 | OOB Read / Memory Leak | Bleeding Llama |
| CVE-2026-45829 | ChromaDB | 10.0 | Pre-Auth RCE | ChromaToast |
| CVE-2024-27133 | MLflow | 8.8 | XSS → Client RCE | Recipe Dataset |
| CVE-2026-2033 | MLflow | 9.8 | Path Traversal RCE | Tracking Server |
| CVE-2026-0596 | MLflow | 9.6 | Command Injection RCE | Model Serving |
| CVE-2024-37054 | MLflow | 9.8 | Pickle Deserialization RCE | Model Loading |

## Shodan Dorks

| Platform | Dork | Estimated Exposed |
|----------|------|------------------|
| Ollama | `"Ollama is running" port:11434` | ~175,000 |
| ChromaDB | `"chromadb" port:8000` | ~10,000 |
| MLflow | `"mlflow" port:5000` | ~5,000 |

## OLLAMA: 207.244.225.101:11434

**Alive:** ✅  
**Version:** 0.9.4  

### CVE Results

| CVE | Status | Severity | Evidence |
|-----|--------|----------|----------|
| CVE-2026-7482 | unlikely | CRITICAL | /api/push returned 500 |

## CHROMADB: 207.244.225.101:8000

**Alive:** ✅  
**Version:** None  

### CVE Results

| CVE | Status | Severity | Evidence |
|-----|--------|----------|----------|
| CVE-2026-45829 | mitigated | CRITICAL | Collection creation requires auth (401). Auth may still be bypassed if embedding |

## Recommendations

### Ollama
- Bind to 127.0.0.1 only, never 0.0.0.0
- Add authentication proxy (nginx + basic auth)
- Upgrade to Ollama ≥ 0.17.1 (fixes CVE-2026-7482)
- Block port 11434 at firewall level
- Monitor /api/tags for unauthorized access

### ChromaDB
- Use Rust implementation instead of Python FastAPI
- Enable authentication (currently no auth by default)
- Bind to 127.0.0.1, never 0.0.0.0
- Apply patches for CVE-2026-45829 when available
- Block port 8000 at firewall level

### MLflow
- Upgrade to MLflow ≥ 3.8.0 (fixes CVE-2026-2033)
- Upgrade to MLflow ≥ 3.10.0 (fixes CVE-2026-0596)
- Enable authentication on Tracking Server
- Restrict artifact serving paths
- Block port 5000 at firewall level
- Never serve models with enable_mlserver=True on public endpoints

## OPSEC Notes
- All scans conducted via Tor SOCKS5 proxy (127.0.0.1:9050)
- No malicious payloads sent - endpoint accessibility checks only
- Test collections auto-deleted after creation
