#!/usr/bin/env python3
"""
AI Infrastructure Vulnerability Scanner v2.0
Detects exposed AI services and checks for known CVEs
Uses Tor proxy for OPSEC
"""
import requests
import json
import sys
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROXY = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}
TIMEOUT = 12

# Service detection fingerprints
SERVICES = {
    "chromadb": {
        "ports": [8000],
        "endpoints": [
            ("/api/v2/tenants/default/databases/default/collections", "GET"),
            ("/api/v1/heartbeat", "GET"),
        ],
        "match": ["chroma", "chromadb"],
        "cves": ["CVE-2026-45829"],
        "severity": "CRITICAL"
    },
    "ollama": {
        "ports": [11434],
        "endpoints": [
            ("/", "GET"),
            ("/api/tags", "GET"),
            ("/api/version", "GET"),
        ],
        "match": ["ollama is running", "ollama"],
        "cves": ["CVE-2024-39720", "CVE-2024-39721", "CVE-2024-39722", "CVE-2024-28224", "CVE-2024-8063"],
        "severity": "CRITICAL"
    },
    "vllm": {
        "ports": [8000],
        "endpoints": [
            ("/v1/models", "GET"),
            ("/health", "GET"),
            ("/docs", "GET"),
        ],
        "match": ["vllm", "fastapi", "openai"],
        "cves": ["CVE-2025-24357", "CVE-2024-8768"],
        "severity": "HIGH"
    },
    "mlflow": {
        "ports": [5000],
        "endpoints": [
            ("/", "GET"),
            ("/ajax-api/2.0/mlflow/experiments/search", "GET"),
            ("/api/2.0/mlflow/runs/search", "GET"),
        ],
        "match": ["mlflow", "databricks"],
        "cves": ["CVE-2024-27132", "CVE-2024-27133"],
        "severity": "CRITICAL"
    },
    "qdrant": {
        "ports": [6333],
        "endpoints": [
            ("/", "GET"),
            ("/collections", "GET"),
        ],
        "match": ["qdrant"],
        "cves": [],
        "severity": "HIGH"
    },
    "litellm": {
        "ports": [4000],
        "endpoints": [
            ("/", "GET"),
            ("/health", "GET"),
        ],
        "match": ["litellm"],
        "cves": [],
        "severity": "HIGH"
    },
    "gradio": {
        "ports": [7860],
        "endpoints": [
            ("/", "GET"),
            ("/info", "GET"),
        ],
        "match": ["gradio"],
        "cves": [],
        "severity": "MEDIUM"
    }
}

def detect_service(host, port, service_name, config):
    """Probe a host for a specific AI service"""
    findings = []
    for endpoint, method in config["endpoints"]:
        for scheme in ["http", "https"]:
            url = f"{scheme}://{host}:{port}{endpoint}"
            try:
                r = requests.request(
                    method, url,
                    proxies=PROXY,
                    timeout=TIMEOUT,
                    verify=False,
                    allow_redirects=True,
                    headers={"User-Agent": "Mozilla/5.0 (AI-Infra-Scanner/2.0)"}
                )
                if r.status_code == 200:
                    content_lower = r.text.lower()
                    for match in config["match"]:
                        if match in content_lower:
                            finding = {
                                "service": service_name,
                                "host": host,
                                "port": port,
                                "url": url,
                                "status": r.status_code,
                                "content_length": len(r.text),
                                "severity": config["severity"],
                                "cves": config["cves"],
                                "match": match,
                                "snippet": r.text[:300]
                            }
                            # Extract extra info
                            if service_name == "ollama" and endpoint == "/api/tags":
                                try:
                                    data = r.json()
                                    finding["models"] = [m.get("name","") for m in data.get("models", [])]
                                except: pass
                            if service_name == "ollama" and endpoint == "/api/version":
                                try:
                                    finding["version"] = r.json().get("version", "")
                                except: pass
                            findings.append(finding)
                            break
            except:
                pass
    return findings

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 ai_scanner.py <host> [port]")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    print(f"\n{'='*70}")
    print(f"  AI INFRASTRUCTURE VULNERABILITY SCANNER v2.0")
    print(f"  Target: {host}")
    print(f"{'='*70}")
    
    all_findings = []
    
    for service_name, config in SERVICES.items():
        ports = [port] if port else config["ports"]
        for p in ports:
            results = detect_service(host, p, service_name, config)
            all_findings.extend(results)
    
    if all_findings:
        print(f"\n[!] FOUND {len(all_findings)} EXPOSED AI SERVICE(S):\n")
        for f in all_findings:
            print(f"  ╔══ {f['service'].upper()} DETECTED")
            print(f"  ╠═ URL: {f['url']}")
            print(f"  ╠═ Severity: {f['severity']}")
            if f.get('version'):
                print(f"  ╠═ Version: {f['version']}")
            if f.get('models'):
                print(f"  ╠═ Models: {', '.join(f['models'][:5])}")
            print(f"  ╠═ CVEs: {', '.join(f['cves']) if f['cves'] else 'N/A'}")
            print(f"  ╚═ Match: '{f['match']}' in response")
            print()
    else:
        print(f"\n[-] No exposed AI services detected on {host}")
    
    # Save results
    output_file = f"/home/admin_user/Projects/ai_infra_scan/findings/{host}_scan.json"
    with open(output_file, 'w') as f:
        json.dump({"timestamp": datetime.now().isoformat(), "host": host, "findings": all_findings}, f, indent=2)
    print(f"[+] Results saved to {output_file}")
