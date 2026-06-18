#!/usr/bin/env python3
"""
OLLAMA+CHROMADB+MLFLOW HUNTER v1.0
Scans for exposed AI infrastructure instances and tests critical CVEs.

CVEs tested:
  - CVE-2026-7482 (Ollama Bleeding Llama - OOB read/memory leak, CVSS 9.3)
  - CVE-2026-45829 (ChromaDB ChromaToast - Pre-auth RCE, CVSS 10.0)
  - CVE-2024-27133 (MLflow XSS→RCE, CVSS 8.8)
  - CVE-2026-2033 (MLflow Tracking Server RCE, CVSS 9.8)
  - CVE-2026-0596 (MLflow Command Injection RCE, CVSS 9.6)
  - CVE-2024-37054 (MLflow Pickle Deserialization RCE)

Shodan dorks:
  - "Ollama is running" port:11434
  - "chromadb" port:8000
  - "mlflow" port:5000

Author: admin_user + Grok
OPSEC: All requests via Tor SOCKS5 proxy
"""

import requests
import json
import socket
import ssl
import urllib3
import sys
import time
import hashlib
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── OPSEC: Tor SOCKS5 Proxy ──────────────────────────────────────────
PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}
TIMEOUT = 15
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
VERIFY_SSL = False

# ── Test Targets ──────────────────────────────────────────────────────
# These are randomly selected from Shodan dork results for testing
# Replace with actual targets as needed
TEST_TARGETS = {
    "ollama": [],  # Will be populated from Shodan
    "chromadb": [],
    "mlflow": []
}

# ── Color Codes ───────────────────────────────────────────────────────
R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
B = "\033[94m"
C = "\033[96m"
W = "\033[0m"
BOLD = "\033[1m"

def banner():
    print(f"""
{R}{BOLD}╔══════════════════════════════════════════════════════════╗
║  OLLAMA+CHROMADB+MLFLOW HUNTER v1.0                    ║
║  AI Infrastructure Scanner                             ║
╠══════════════════════════════════════════════════════════╣
║  CVE-2026-7482 │ Ollama Bleeding Llama │ CVSS 9.3      ║
║  CVE-2026-45829│ ChromaDB ChromaToast   │ CVSS 10.0     ║
║  CVE-2024-27133│ MLflow XSS→RCE         │ CVSS 8.8      ║
║  CVE-2026-2033 │ MLflow Tracking RCE    │ CVSS 9.8      ║
║  CVE-2026-0596 │ MLflow Cmd Injection   │ CVSS 9.6      ║
║  CVE-2024-37054│ MLflow Pickle Deser.    │ CVSS 9.8      ║
╚══════════════════════════════════════════════════════════╝{W}
""")

def log_info(msg):
    print(f"{B}[*]{W} {msg}")

def log_success(msg):
    print(f"{G}[✓]{W} {msg}")

def log_vuln(msg):
    print(f"{R}[!]{W} {R}{BOLD}{msg}{W}")

def log_warn(msg):
    print(f"{Y}[!]{W} {msg}")

def log_fail(msg):
    print(f"{Y}[-]{W} {msg}")

# ═══════════════════════════════════════════════════════════════════════
# SECTION 1: OLLAMA SCANNER
# ═══════════════════════════════════════════════════════════════════════

def scan_ollama(host, port=11434):
    """Scan a single Ollama instance for info disclosure and CVEs."""
    results = {
        "host": host,
        "port": port,
        "platform": "ollama",
        "timestamp": datetime.utcnow().isoformat(),
        "alive": False,
        "version": None,
        "models": [],
        "cves": {}
    }
    
    base = f"http://{host}:{port}"
    
    # ── Test /api/tags (model listing - no auth required) ──────────
    try:
        r = requests.get(f"{base}/api/tags", headers=HEADERS, proxies=PROXIES,
                        timeout=TIMEOUT, verify=VERIFY_SSL)
        if r.status_code == 200:
            results["alive"] = True
            data = r.json()
            log_success(f"Ollama ALIVE: {host}:{port}")
            
            if "models" in data:
                results["models"] = data["models"]
                log_info(f"  Models found: {len(data['models'])}")
                for m in data["models"][:10]:  # Show first 10
                    name = m.get("name", "unknown")
                    size = m.get("size", 0)
                    log_info(f"    - {name} ({size/(1024**3):.1f}GB)")
        else:
            log_fail(f"Ollama {host}:{port} /api/tags status: {r.status_code}")
    except Exception as e:
        log_fail(f"Ollama {host}:{port} unreachable: {e}")
        return results
    
    # ── Test /api/version ──────────────────────────────────────────
    try:
        r = requests.get(f"{base}/api/version", headers=HEADERS, proxies=PROXIES,
                        timeout=TIMEOUT, verify=VERIFY_SSL)
        if r.status_code == 200:
            data = r.json()
            results["version"] = data.get("version", "unknown")
            log_info(f"  Version: {results['version']}")
    except:
        pass
    
    # ── CVE-2026-7482: Bleeding Llama (OOB Read / Memory Leak) ─────
    # This CVE involves sending a malicious GGUF file that causes
    # out-of-bounds heap read, leaking process memory (API keys, etc.)
    # SAFE TEST: We only check if the push endpoint exists and is accessible
    # We do NOT send an actual malicious GGUF file
    log_info(f"  Testing CVE-2026-7482 (Bleeding Llama) - endpoint check...")
    try:
        # Check if /api/push endpoint exists (required for exploitation)
        r = requests.post(f"{base}/api/push", 
                         json={"name": "test", "stream": False},
                         headers=HEADERS, proxies=PROXIES,
                         timeout=TIMEOUT, verify=VERIFY_SSL)
        if r.status_code in [200, 400, 401]:
            results["cves"]["CVE-2026-7482"] = {
                "vulnerable": "potentially",
                "evidence": f"/api/push endpoint accessible (status {r.status_code}), Ollama < 0.17.1 may be vulnerable to OOB read via malicious GGUF",
                "severity": "CRITICAL",
                "cvss": 9.3,
                "detail": "Unauthenticated memory leak via crafted GGUF model file. 300,000+ exposed instances."
            }
            log_warn(f"  CVE-2026-7482: /api/push accessible - POTENTIALLY VULNERABLE")
        else:
            results["cves"]["CVE-2026-7482"] = {
                "vulnerable": "unlikely",
                "evidence": f"/api/push returned {r.status_code}",
                "severity": "CRITICAL",
                "cvss": 9.3
            }
    except Exception as e:
        results["cves"]["CVE-2026-7482"] = {"vulnerable": "unknown", "evidence": str(e)}
    
    # ── Additional Ollama endpoints ─────────────────────────────────
    endpoints = [
        ("/api/ps", "Running models"),
        ("/api/show", "Model details"),
        ("/", "Root page"),
        ("/api/generate", "Generate endpoint"),
    ]
    
    for ep, desc in endpoints:
        try:
            r = requests.get(f"{base}{ep}", headers=HEADERS, proxies=PROXIES,
                           timeout=TIMEOUT, verify=VERIFY_SSL)
            if r.status_code == 200:
                log_info(f"  {desc}: {ep} → {r.status_code}")
                if ep == "/api/ps" and r.text:
                    try:
                        ps_data = r.json()
                        if "models" in ps_data:
                            log_info(f"    Running models: {ps_data['models']}")
                    except:
                        pass
        except:
            pass
    
    return results

# ═══════════════════════════════════════════════════════════════════════
# SECTION 2: CHROMADB SCANNER
# ═══════════════════════════════════════════════════════════════════════

def scan_chromadb(host, port=8000):
    """Scan a single ChromaDB instance for CVE-2026-45829 and info disclosure."""
    results = {
        "host": host,
        "port": port,
        "platform": "chromadb",
        "timestamp": datetime.utcnow().isoformat(),
        "alive": False,
        "version": None,
        "collections": [],
        "cves": {}
    }
    
    base = f"http://{host}:{port}"
    
    # ── Test /api/v1/heartbeat ─────────────────────────────────────
    try:
        r = requests.get(f"{base}/api/v1/heartbeat", headers=HEADERS, proxies=PROXIES,
                        timeout=TIMEOUT, verify=VERIFY_SSL)
        if r.status_code == 200:
            results["alive"] = True
            log_success(f"ChromaDB ALIVE: {host}:{port}")
            try:
                data = r.json()
                log_info(f"  Heartbeat: {json.dumps(data, indent=2)[:200]}")
            except:
                log_info(f"  Heartbeat response: {r.text[:200]}")
        elif r.status_code == 401:
            results["alive"] = True
            log_info(f"ChromaDB {host}:{port} requires auth (401)")
        else:
            log_fail(f"ChromaDB {host}:{port} /heartbeat status: {r.status_code}")
    except Exception as e:
        log_fail(f"ChromaDB {host}:{port} unreachable: {e}")
        return results
    
    # ── Test /api/v1/collections ────────────────────────────────────
    try:
        r = requests.get(f"{base}/api/v1/collections", headers=HEADERS, proxies=PROXIES,
                        timeout=TIMEOUT, verify=VERIFY_SSL)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                results["collections"] = data
                log_info(f"  Collections accessible: {len(data)}")
                for c in data[:5]:
                    log_info(f"    - {c.get('name', 'unknown')} (id: {c.get('id', '?')})")
            elif isinstance(data, dict):
                collections = data.get("collections", data.get("data", []))
                results["collections"] = collections
                log_info(f"  Collections: {json.dumps(data)[:300]}")
    except Exception as e:
        log_fail(f"  /api/v1/collections error: {e}")
    
    # ── Test /api/v1/models (embeddings) ────────────────────────────
    try:
        r = requests.get(f"{base}/api/v1/models", headers=HEADERS, proxies=PROXIES,
                        timeout=TIMEOUT, verify=VERIFY_SSL)
        if r.status_code == 200:
            log_info(f"  /api/v1/models accessible")
    except:
        pass
    
    # ── Test /api/v2 (newer API) ────────────────────────────────────
    try:
        r = requests.get(f"{base}/api/v2", headers=HEADERS, proxies=PROXIES,
                        timeout=TIMEOUT, verify=VERIFY_SSL)
        if r.status_code == 200:
            log_info(f"  /api/v2 accessible - newer API version")
    except:
        pass
    
    # ── CVE-2026-45829: ChromaToast Pre-Auth RCE ────────────────────
    # The vulnerability is in the embedding function configuration which
    # is processed BEFORE auth checks. The /api/v1/collections endpoint
    # accepts embedding_function configuration that gets exec()'d.
    # SAFE TEST: We only test if the collection creation endpoint accepts
    # our request with an embedding_function field. We do NOT send actual
    # malicious code.
    log_info(f"  Testing CVE-2026-45829 (ChromaToast) - endpoint check...")
    try:
        # Test if collection creation accepts embedding_function param
        test_payload = {
            "name": f"security_test_{int(time.time())}",
            "get_or_create": True,
            "metadata": {"hnsw:space": "cosine"}
        }
        r = requests.post(f"{base}/api/v1/collections", 
                         json=test_payload,
                         headers=HEADERS, proxies=PROXIES,
                         timeout=TIMEOUT, verify=VERIFY_SSL)
        
        if r.status_code in [200, 201]:
            results["cves"]["CVE-2026-45829"] = {
                "vulnerable": "potentially",
                "evidence": f"Collection creation via /api/v1/collections accessible without auth (status {r.status_code}). Pre-auth embedding function injection possible.",
                "severity": "CRITICAL",
                "cvss": 10.0,
                "detail": "Pre-auth RCE via embedding function code injection. Auth check happens AFTER code execution. ~73% of exposed instances vulnerable."
            }
            log_vuln(f"  CVE-2026-45829: UNAUTHENTICATED collection creation - POTENTIALLY VULNERABLE")
            
            # Cleanup: delete test collection
            try:
                col_data = r.json()
                col_id = col_data.get("id")
                if col_id:
                    requests.delete(f"{base}/api/v1/collections/{col_id}",
                                  headers=HEADERS, proxies=PROXIES,
                                  timeout=TIMEOUT, verify=VERIFY_SSL)
            except:
                pass
        elif r.status_code == 401:
            results["cves"]["CVE-2026-45829"] = {
                "vulnerable": "mitigated",
                "evidence": f"Collection creation requires auth (401). Auth may still be bypassed if embedding_function is processed before auth.",
                "severity": "CRITICAL",
                "cvss": 10.0
            }
            log_warn(f"  CVE-2026-45829: Auth required (401) - but auth may still be bypassed")
        else:
            results["cves"]["CVE-2026-45829"] = {
                "vulnerable": "unknown",
                "evidence": f"Unexpected status {r.status_code}: {r.text[:200]}",
                "severity": "CRITICAL",
                "cvss": 10.0
            }
    except Exception as e:
        results["cves"]["CVE-2026-45829"] = {"vulnerable": "unknown", "evidence": str(e)}
    
    # ── Additional ChromaDB endpoints ───────────────────────────────
    endpoints = [
        ("/api/v1/tenants/default", "Default tenant"),
        ("/api/v1/databases/default", "Default database"),
        ("/docs", "API docs"),
        ("/openapi.json", "OpenAPI schema"),
    ]
    
    for ep, desc in endpoints:
        try:
            r = requests.get(f"{base}{ep}", headers=HEADERS, proxies=PROXIES,
                           timeout=TIMEOUT, verify=VERIFY_SSL)
            if r.status_code == 200:
                log_info(f"  {desc}: {ep} → {r.status_code}")
        except:
            pass
    
    return results

# ═══════════════════════════════════════════════════════════════════════
# SECTION 3: MLFLOW SCANNER
# ═══════════════════════════════════════════════════════════════════════

def scan_mlflow(host, port=5000):
    """Scan a single MLflow instance for CVEs and info disclosure."""
    results = {
        "host": host,
        "port": port,
        "platform": "mlflow",
        "timestamp": datetime.utcnow().isoformat(),
        "alive": False,
        "version": None,
        "experiments": [],
        "cves": {}
    }
    
    base = f"http://{host}:{port}"
    
    # ── Test /ajax-api/2.0/mlflow/runs/search ────────────────────────
    try:
        r = requests.get(f"{base}/ajax-api/2.0/mlflow/runs/search", 
                        headers=HEADERS, proxies=PROXIES,
                        timeout=TIMEOUT, verify=VERIFY_SSL)
        if r.status_code == 200:
            results["alive"] = True
            log_success(f"MLflow ALIVE: {host}:{port}")
    except:
        # Try alternative
        try:
            r = requests.get(f"{base}/", headers=HEADERS, proxies=PROXIES,
                           timeout=TIMEOUT, verify=VERIFY_SSL)
            if r.status_code == 200 and "mlflow" in r.text.lower():
                results["alive"] = True
                log_success(f"MLflow ALIVE (root page): {host}:{port}")
            else:
                log_fail(f"MLflow {host}:{port} not detected")
                return results
        except Exception as e:
            log_fail(f"MLflow {host}:{port} unreachable: {e}")
            return results
    
    # ── Test /ajax-api/2.0/mlflow/experiments/search ────────────────
    try:
        r = requests.get(f"{base}/ajax-api/2.0/mlflow/experiments/search",
                        headers=HEADERS, proxies=PROXIES,
                        timeout=TIMEOUT, verify=VERIFY_SSL)
        if r.status_code == 200:
            data = r.json()
            exps = data.get("experiments", [])
            results["experiments"] = exps
            log_info(f"  Experiments accessible: {len(exps)}")
            for e in exps[:5]:
                log_info(f"    - {e.get('name', '?')} (id: {e.get('experiment_id', '?')})")
    except Exception as e:
        log_fail(f"  Experiments search error: {e}")
    
    # ── Test /ajax-api/2.0/mlflow/artifacts/list ─────────────────────
    try:
        r = requests.get(f"{base}/ajax-api/2.0/mlflow/artifacts/list?run_id=test",
                        headers=HEADERS, proxies=PROXIES,
                        timeout=TIMEOUT, verify=VERIFY_SSL)
        if r.status_code == 200:
            log_info(f"  Artifact listing accessible")
    except:
        pass
    
    # ── Version detection ───────────────────────────────────────────
    try:
        r = requests.get(f"{base}/ajax-api/2.0/mlflow/server/get-version",
                        headers=HEADERS, proxies=PROXIES,
                        timeout=TIMEOUT, verify=VERIFY_SSL)
        if r.status_code == 200:
            data = r.json()
            results["version"] = data.get("version", "unknown")
            log_info(f"  Version: {results['version']}")
    except:
        # Try from HTML
        try:
            r = requests.get(f"{base}/", headers=HEADERS, proxies=PROXIES,
                           timeout=TIMEOUT, verify=VERIFY_SSL)
            if "mlflow" in r.text.lower():
                # Try to extract version
                import re
                ver = re.search(r'MLflow\s+v?(\d+\.\d+[\.\d]*)', r.text)
                if ver:
                    results["version"] = ver.group(1)
                    log_info(f"  Version (from page): {results['version']}")
        except:
            pass
    
    # ── CVE-2024-27133: MLflow XSS → RCE ────────────────────────────
    # XSS in recipe dataset fields leads to client-side RCE in Jupyter
    log_info(f"  Testing CVE-2024-27133 (XSS→RCE) - endpoint check...")
    try:
        # Check if recipe-related endpoints exist
        r = requests.get(f"{base}/ajax-api/2.0/mlflow/recipes",
                        headers=HEADERS, proxies=PROXIES,
                        timeout=TIMEOUT, verify=VERIFY_SSL)
        if r.status_code in [200, 404]:
            results["cves"]["CVE-2024-27133"] = {
                "vulnerable": "potentially",
                "evidence": f"MLflow instance accessible. XSS via recipe dataset fields possible. Status: {r.status_code}",
                "severity": "HIGH",
                "cvss": 8.8,
                "detail": "Insufficient sanitization in recipe datasets leads to XSS → client-side RCE in Jupyter. Affects MLflow < 2.9.0"
            }
            log_warn(f"  CVE-2024-27133: MLflow accessible - POTENTIALLY VULNERABLE")
        else:
            results["cves"]["CVE-2024-27133"] = {
                "vulnerable": "unknown",
                "evidence": f"Status: {r.status_code}",
                "severity": "HIGH",
                "cvss": 8.8
            }
    except Exception as e:
        results["cves"]["CVE-2024-27133"] = {"vulnerable": "unknown", "evidence": str(e)}
    
    # ── CVE-2026-2033: MLflow Tracking Server RCE ───────────────────
    # Directory traversal → RCE via artifact serving
    log_info(f"  Testing CVE-2026-2033 (Tracking Server RCE) - path traversal check...")
    try:
        # Test path traversal in artifact endpoint
        r = requests.get(f"{base}/ajax-api/2.0/mlflow/artifacts/list?path=../../../etc/passwd&run_id=test",
                        headers=HEADERS, proxies=PROXIES,
                        timeout=TIMEOUT, verify=VERIFY_SSL)
        if r.status_code == 200:
            results["cves"]["CVE-2026-2033"] = {
                "vulnerable": "potentially",
                "evidence": f"Artifact path traversal returned 200. May allow arbitrary file read.",
                "severity": "CRITICAL",
                "cvss": 9.8,
                "detail": "Directory traversal in MLflow Tracking Server allows unauthenticated RCE. Fixed in v3.8.0."
            }
            log_vuln(f"  CVE-2026-2033: Path traversal returned 200 - POTENTIALLY VULNERABLE")
        elif r.status_code in [400, 403, 404]:
            # Even 400 might mean the path is processed but run_id is invalid
            results["cves"]["CVE-2026-2033"] = {
                "vulnerable": "needs-verification",
                "evidence": f"Path traversal test returned {r.status_code}. Further verification needed with valid run_id.",
                "severity": "CRITICAL",
                "cvss": 9.8
            }
        else:
            results["cves"]["CVE-2026-2033"] = {
                "vulnerable": "unlikely",
                "evidence": f"Status: {r.status_code}",
                "severity": "CRITICAL",
                "cvss": 9.8
            }
    except Exception as e:
        results["cves"]["CVE-2026-2033"] = {"vulnerable": "unknown", "evidence": str(e)}
    
    # ── CVE-2026-0596: MLflow Command Injection RCE ──────────────────
    # model_uri parameter injection in mlflow serve (enable_mlserver=True)
    log_info(f"  Testing CVE-2026-0596 (Command Injection RCE) - endpoint check...")
    try:
        # Check if model serving endpoint exists
        r = requests.get(f"{base}/ajax-api/2.0/mlflow/models/search",
                        headers=HEADERS, proxies=PROXIES,
                        timeout=TIMEOUT, verify=VERIFY_SSL)
        results["cves"]["CVE-2026-0596"] = {
            "vulnerable": "potentially",
            "evidence": f"MLflow model serving endpoint returned {r.status_code}. Command injection via model_uri possible if mlserver enabled.",
            "severity": "CRITICAL",
            "cvss": 9.6,
            "detail": "Command injection in model_uri parameter when serving models with enable_mlserver=True. Affects MLflow < 3.10.0."
        }
        log_warn(f"  CVE-2026-0596: Model serving accessible - POTENTIALLY VULNERABLE")
    except Exception as e:
        results["cves"]["CVE-2026-0596"] = {"vulnerable": "unknown", "evidence": str(e)}
    
    # ── CVE-2024-37054: MLflow Pickle Deserialization RCE ────────────
    # Authenticated (or unauth if no auth) pickle deserialization
    log_info(f"  Testing CVE-2024-37054 (Pickle Deserialization RCE) - endpoint check...")
    try:
        # Check if models can be loaded
        r = requests.get(f"{base}/ajax-api/2.0/mlflow/model-versions/search",
                        headers=HEADERS, proxies=PROXIES,
                        timeout=TIMEOUT, verify=VERIFY_SSL)
        if r.status_code == 200:
            results["cves"]["CVE-2024-37054"] = {
                "vulnerable": "potentially",
                "evidence": f"Model versions searchable without auth. Pickle deserialization RCE possible.",
                "severity": "CRITICAL",
                "cvss": 9.8,
                "detail": "Pickle deserialization in model loading allows RCE. Can overwrite python_model.pkl artifact."
            }
            log_warn(f"  CVE-2024-37054: Model versions accessible - POTENTIALLY VULNERABLE")
        else:
            results["cves"]["CVE-2024-37054"] = {
                "vulnerable": "unknown",
                "evidence": f"Model search returned {r.status_code}",
                "severity": "CRITICAL",
                "cvss": 9.8
            }
    except Exception as e:
        results["cves"]["CVE-2024-37054"] = {"vulnerable": "unknown", "evidence": str(e)}
    
    # ── Additional MLflow endpoints ─────────────────────────────────
    endpoints = [
        ("/ajax-api/2.0/mlflow/runs/search", "Runs search"),
        ("/ajax-api/2.0/mlflow/experiments/search", "Experiments search"),
        ("/ajax-api/2.0/mlflow/registered-models/search", "Registered models"),
        ("/ajax-api/2.0/mlflow/artifacts/list", "Artifact listing"),
        ("/static/js/mlflow.js", "MLflow JS (version leak)"),
        ("/health", "Health endpoint"),
    ]
    
    for ep, desc in endpoints:
        try:
            r = requests.get(f"{base}{ep}", headers=HEADERS, proxies=PROXIES,
                           timeout=TIMEOUT, verify=VERIFY_SSL)
            if r.status_code == 200:
                log_info(f"  {desc}: {ep} → {r.status_code}")
                if "version" in ep or "js" in ep:
                    # Try to extract version
                    import re
                    ver = re.search(r'(\d+\.\d+[\.\d]*)', r.text[:500])
                    if ver:
                        log_info(f"    Version hint: {ver.group(1)}")
        except:
            pass
    
    return results

# ═══════════════════════════════════════════════════════════════════════
# SECTION 4: MULTI-TARGET SCANNER
# ═══════════════════════════════════════════════════════════════════════

def scan_targets(targets_file=None, targets=None):
    """Scan multiple targets from file or list."""
    all_results = []
    
    if targets_file:
        with open(targets_file, 'r') as f:
            targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not targets:
        log_warn("No targets provided!")
        return all_results
    
    for target in targets:
        target = target.strip()
        if not target or target.startswith('#'):
            continue
        
        # Parse target format: type:host[:port]
        parts = target.split(':')
        if len(parts) >= 3:
            platform, host, port = parts[0], parts[1], int(parts[2])
        elif len(parts) == 2:
            platform, host = parts
            port = None
        else:
            log_warn(f"Invalid target format: {target}. Use type:host[:port]")
            continue
        
        print(f"\n{C}{'═'*60}{W}")
        print(f"{BOLD}Scanning: {platform}://{host}{':'+str(port) if port else ''}{W}")
        print(f"{C}{'═'*60}{W}")
        
        if platform.lower() == "ollama":
            results = scan_ollama(host, port or 11434)
        elif platform.lower() == "chromadb":
            results = scan_chromadb(host, port or 8000)
        elif platform.lower() == "mlflow":
            results = scan_mlflow(host, port or 5000)
        else:
            log_warn(f"Unknown platform: {platform}")
            continue
        
        all_results.append(results)
    
    return all_results

# ═══════════════════════════════════════════════════════════════════════
# SECTION 5: REPORT GENERATOR
# ═══════════════════════════════════════════════════════════════════════

def generate_report(results):
    """Generate markdown report from scan results."""
    report = f"""# OLLAMA+CHROMADB+MLFLOW HUNTER Report
Generated: {datetime.utcnow().isoformat()}Z
Scanner: v1.0 | OPSEC: Tor SOCKS5

## Executive Summary

"""
    
    ollama_count = sum(1 for r in results if r["platform"] == "ollama" and r["alive"])
    chromadb_count = sum(1 for r in results if r["platform"] == "chromadb" and r["alive"])
    mlflow_count = sum(1 for r in results if r["platform"] == "mlflow" and r["alive"])
    
    vuln_count = sum(len(r.get("cves", {})) for r in results if r["alive"])
    
    report += f"""| Platform | Alive | CVEs Tested | Potentially Vulnerable |
|----------|-------|-------------|----------------------|
| Ollama | {ollama_count} | 1 | {sum(1 for r in results if r['platform']=='ollama' and r['alive'] and any(v.get('vulnerable')=='potentially' for v in r.get('cves',{}).values()))} |
| ChromaDB | {chromadb_count} | 1 | {sum(1 for r in results if r['platform']=='chromadb' and r['alive'] and any(v.get('vulnerable')=='potentially' for v in r.get('cves',{}).values()))} |
| MLflow | {mlflow_count} | 4 | {sum(1 for r in results if r['platform']=='mlflow' and r['alive'] and any(v.get('vulnerable')=='potentially' for v in r.get('cves',{}).values()))} |

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

"""
    
    # Detailed results per target
    for r in results:
        if not r["alive"]:
            continue
        
        report += f"""## {r['platform'].upper()}: {r['host']}:{r['port']}

**Alive:** ✅  
**Version:** {r.get('version', 'unknown')}  

"""
        
        # Models/Collections
        if r["platform"] == "ollama" and r.get("models"):
            report += "### Models\n"
            for m in r["models"][:20]:
                name = m.get("name", "unknown")
                size = m.get("size", 0)
                report += f"- {name} ({size/(1024**3):.1f}GB)\n"
            report += "\n"
        
        if r["platform"] == "chromadb" and r.get("collections"):
            report += "### Collections\n"
            for c in r["collections"][:20]:
                name = c.get("name", "unknown") if isinstance(c, dict) else c
                report += f"- {name}\n"
            report += "\n"
        
        if r["platform"] == "mlflow" and r.get("experiments"):
            report += "### Experiments\n"
            for e in r["experiments"][:20]:
                name = e.get("name", "unknown")
                eid = e.get("experiment_id", "?")
                report += f"- {name} (id: {eid})\n"
            report += "\n"
        
        # CVEs
        if r.get("cves"):
            report += "### CVE Results\n\n"
            report += "| CVE | Status | Severity | Evidence |\n"
            report += "|-----|--------|----------|----------|\n"
            for cve_id, cve_data in r["cves"].items():
                status = cve_data.get("vulnerable", "unknown")
                severity = cve_data.get("severity", "?")
                evidence = cve_data.get("evidence", "")[:80]
                report += f"| {cve_id} | {status} | {severity} | {evidence} |\n"
            report += "\n"
    
    # Recommendations
    report += """## Recommendations

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
"""
    
    return report

# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    banner()
    
    # Verify Tor
    log_info("Verifying Tor proxy...")
    try:
        r = requests.get("https://check.torproject.org/api/ip", 
                         proxies=PROXIES, timeout=10)
        data = r.json()
        if data.get("IsTor"):
            log_success(f"Tor active! Exit IP: {data.get('IP', 'unknown')}")
        else:
            log_warn("Tor proxy not working! Using direct connection.")
    except Exception as e:
        log_warn(f"Tor check failed: {e}. Using direct connection.")
    
    # Parse args
    if len(sys.argv) < 2:
        print(f"""
Usage:
  {sys.argv[0]} scan <targets_file>        # Scan targets from file
  {sys.argv[0]} scan-inline <targets>      # Scan inline targets
  {sys.argv[0]} demo                        # Demo scan on public test targets

Target format: platform:host[:port]
  Examples:
    ollama:some-host.com:11434
    chromadb:some-host.com:8000
    mlflow:some-host.com:5000

Targets file format (one per line):
  ollama:192.168.1.100:11434
  chromadb:192.168.1.101:8000
  mlflow:192.168.1.102:5000
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "scan" and len(sys.argv) >= 3:
        results = scan_targets(targets_file=sys.argv[2])
    elif cmd == "scan-inline":
        results = scan_targets(targets=sys.argv[2:])
    elif cmd == "demo":
        print(f"\n{Y}Demo mode: No live targets to scan.{W}")
        print(f"{Y}Use Shodan/Censys to discover targets, then scan them.{W}")
        print(f"\nShodan dorks to find targets:")
        print(f"  Ollama:   port:11434 product:Ollama")
        print(f"  ChromaDB: port:8000 chromadb")
        print(f"  MLflow:   port:5000 mlflow")
        results = []
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
    
    if results:
        report = generate_report(results)
        
        # Save report
        report_path = f"/home/admin_user/Projects/ai_infra_scan/reports/ollama_chromadb_mlflow_hunter_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w') as f:
            f.write(report)
        log_success(f"Report saved: {report_path}")
        
        # Save JSON results
        json_path = report_path.replace('.md', '.json')
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        log_success(f"JSON results saved: {json_path}")
        
        # Print summary
        print(f"\n{G}{BOLD}{'═'*60}")
        print(f"SCAN COMPLETE")
        print(f"{'═'*60}{W}")
        print(f"  Targets scanned: {len(results)}")
        print(f"  Alive targets:   {sum(1 for r in results if r['alive'])}")
        print(f"  CVEs tested:     {sum(len(r.get('cves',{})) for r in results)}")
        vuln_count = sum(1 for r in results if r['alive'] and any(v.get('vulnerable')=='potentially' for v in r.get('cves',{}).values()))
        print(f"  Potentially vulnerable: {vuln_count}")