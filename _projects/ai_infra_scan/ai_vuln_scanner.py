#!/usr/bin/env python3
"""
AI Infrastructure Vulnerability Scanner
Scans for exposed AI services and verifies known CVEs
Targets: Ollama, vLLM, MLflow, Open WebUI, Gradio, ComfyUI, etc.
"""
import requests
import json
import socket
import sys
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Proxy config for OPSEC
PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}
TIMEOUT = 10

# AI service fingerprints and their checks
AI_SERVICES = {
    "ollama": {
        "port": 11434,
        "paths": ["/", "/api/tags", "/api/version", "/api/ps"],
        "title_match": "Ollama is running",
        "cves": ["CVE-2024-39720", "CVE-2024-39721", "CVE-2024-39722", "CVE-2024-28224"],
        "severity": "CRITICAL",
        "description": "Unauthenticated API access - model theft, compute theft, path traversal, DoS"
    },
    "vllm": {
        "port": 8000,
        "paths": ["/v1/models", "/v1/chat/completions", "/docs", "/health"],
        "title_match": "FastAPI",
        "cves": [],
        "severity": "HIGH",
        "description": "OpenAI-compatible API without auth - model access, prompt injection, compute theft"
    },
    "mlflow": {
        "port": 5000,
        "paths": ["/", "/ajax-api/2.0/mlflow/experiments/search", "/api/2.0/mlflow/runs/search", "/mlflow", "/static/mlflow.js"],
        "title_match": "MLflow",
        "cves": ["CVE-2024-27132", "CVE-2023-6889", "CVE-2023-6890"],
        "severity": "CRITICAL",
        "description": "XSS → client-side RCE, path traversal, SSRF via model artifacts"
    },
    "gradio": {
        "port": 7860,
        "paths": ["/", "/info", "/config", "/queue/join"],
        "title_match": "Gradio",
        "cves": [],
        "severity": "MEDIUM",
        "description": "Exposed ML demo apps - potential data exfiltration, prompt injection"
    },
    "streamlit": {
        "port": 8501,
        "paths": ["/", "/_stcore/health", "/api/health"],
        "title_match": "Streamlit",
        "cves": [],
        "severity": "LOW",
        "description": "Exposed Streamlit dashboard - information disclosure"
    },
    "litellm": {
        "port": 4000,
        "paths": ["/", "/health", "/v1/models", "/v1/chat/completions"],
        "title_match": "LiteLLM",
        "cves": [],
        "severity": "HIGH",
        "description": "LLM proxy without auth - API key abuse, compute theft"
    },
    "open_webui": {
        "port": 3000,
        "paths": ["/", "/api/v1/auths/signin", "/api/v1/configs"],
        "title_match": "Open WebUI",
        "cves": [],
        "severity": "HIGH",
        "description": "ChatGPT-like UI - potential auth bypass, data exfiltration"
    },
    "comfyui": {
        "port": 7860,
        "paths": ["/", "/prompt", "/object_info", "/view"],
        "title_match": "ComfyUI",
        "cves": [],
        "severity": "HIGH",
        "description": "Image generation without auth - arbitrary workflow execution"
    },
    "lm_studio": {
        "port": 1234,
        "paths": ["/v1/models", "/v1/chat/completions"],
        "title_match": "LM Studio",
        "cves": [],
        "severity": "HIGH",
        "description": "Local LLM server exposed - model theft, prompt injection"
    },
    "qdrant": {
        "port": 6333,
        "paths": ["/", "/collections", "/collections/list"],
        "title_match": "qdrant",
        "cves": [],
        "severity": "HIGH",
        "description": "Vector database exposed - data exfiltration, collection manipulation"
    }
}

def check_service(host, service_name, config):
    """Check if an AI service is exposed on a host"""
    results = {
        "service": service_name,
        "host": host,
        "port": config["port"],
        "found": False,
        "authenticated": False,
        "version": None,
        "models": [],
        "evidence": [],
        "cves": config["cves"],
        "severity": config["severity"],
        "description": config["description"]
    }
    
    base_url = f"http://{host}:{config['port']}"
    
    for path in config["paths"]:
        url = f"{base_url}{path}"
        try:
            r = requests.get(
                url, 
                proxies=PROXIES,
                timeout=TIMEOUT,
                verify=False,
                allow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 (AI-Infra-Scanner)"}
            )
            
            if r.status_code == 200:
                results["found"] = True
                results["evidence"].append({
                    "path": path,
                    "status": r.status_code,
                    "content_snippet": r.text[:500] if r.text else ""
                })
                
                # Check for specific responses
                if service_name == "ollama" and path == "/api/tags":
                    try:
                        data = r.json()
                        if "models" in data:
                            results["models"] = [m.get("name", "") for m in data["models"]]
                    except:
                        pass
                
                if service_name == "ollama" and path == "/api/version":
                    try:
                        data = r.json()
                        results["version"] = data.get("version", "")
                    except:
                        pass
                
                if service_name == "vllm" and path == "/v1/models":
                    try:
                        data = r.json()
                        if "data" in data:
                            results["models"] = [m.get("id", "") for m in data["data"]]
                    except:
                        pass
                
                if service_name == "qdrant" and path == "/collections":
                    try:
                        data = r.json()
                        if "result" in data:
                            results["models"] = [c.get("name", "") for c in data["result"].get("collections", [])]
                    except:
                        pass
                
                # Check for auth
                if r.status_code == 401 or r.status_code == 403:
                    results["authenticated"] = True
                    
        except requests.exceptions.SSLError:
            # Try HTTPS
            try:
                url_https = f"https://{host}:{config['port']}{path}"
                r = requests.get(url_https, proxies=PROXIES, timeout=TIMEOUT, verify=False)
                if r.status_code == 200:
                    results["found"] = True
                    results["evidence"].append({"path": path, "status": r.status_code, "content_snippet": r.text[:500]})
            except:
                pass
        except Exception as e:
            continue
    
    return results

def scan_target(host):
    """Scan a single target for all AI services"""
    findings = []
    for service_name, config in AI_SERVICES.items():
        result = check_service(host, service_name, config)
        if result["found"]:
            findings.append(result)
    return findings

if __name__ == "__main__":
    print("=" * 70)
    print("  AI INFRASTRUCTURE VULNERABILITY SCANNER")
    print("  Targeting: Ollama, vLLM, MLflow, Gradio, ComfyUI, etc.")
    print("=" * 70)
    
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if not target:
        print("Usage: python3 ai_vuln_scanner.py <host_or_ip>")
        sys.exit(1)
    
    print(f"\n[*] Scanning {target} for exposed AI services...")
    print(f"[*] Checking {len(AI_SERVICES)} service types...")
    print(f"[*] Using Tor proxy: socks5h://127.0.0.1:9050\n")
    
    results = scan_target(target)
    
    if results:
        print(f"\n[!] FOUND {len(results)} EXPOSED AI SERVICE(S):\n")
        for r in results:
            print(f"  ╔══ SERVICE: {r['service'].upper()}")
            print(f"  ╠═ Port: {r['port']}")
            print(f"  ╠═ Severity: {r['severity']}")
            print(f"  ╠═ Auth Required: {r['authenticated']}")
            print(f"  ╠═ Version: {r['version'] or 'Unknown'}")
            if r['models']:
                print(f"  ╠═ Models/Data: {', '.join(r['models'][:5])}")
            if r['cves']:
                print(f"  ╠═ Known CVEs: {', '.join(r['cves'])}")
            print(f"  ╠═ Description: {r['description']}")
            print(f"  ╚═ Evidence: {len(r['evidence'])} endpoints responded")
            for e in r['evidence'][:3]:
                print(f"      - {e['path']} → HTTP {e['status']}")
            print()
    else:
        print(f"\n[-] No exposed AI services found on {target}")
    
    # Save results
    output_file = f"/home/admin_user/Projects/ai_infra_scan/findings/{target.replace('.', '_')}_scan.json"
    with open(output_file, 'w') as f:
        json.dump({"target": target, "timestamp": datetime.now().isoformat(), "results": results}, f, indent=2)
    print(f"\n[+] Results saved to {output_file}")
