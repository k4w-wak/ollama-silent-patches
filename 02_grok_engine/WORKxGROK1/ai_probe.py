#!/usr/bin/env python3
"""AI Infrastructure Prober - Checks exposed AI/ML endpoints"""
import json
import sys
import time

# Known AI infrastructure endpoints and their signatures
PROBES = {
    "ollama": {
        "port": 11434,
        "paths": ["/", "/api/tags", "/api/version"],
        "signature": "Ollama is running",
        "cve": "CVE-2026-7482",
        "severity": "CRITICAL"
    },
    "vllm": {
        "port": 8000,
        "paths": ["/v1/models", "/v1/chat/completions", "/health", "/metrics"],
        "signature": "model",
        "cve": "CVE-2026-22778",
        "severity": "CRITICAL"
    },
    "mlflow": {
        "port": 5000,
        "paths": ["/ajax-api/2.0/mlflow/experiments/search", "/api/2.0/mlflow/experiments/search", "/static/mlflow.js"],
        "signature": "mlflow",
        "cve": "CVE-2025-11201",
        "severity": "CRITICAL"
    },
    "n8n": {
        "port": 5678,
        "paths": ["/api/v1/environment", "/webhook/", "/login", "/api/v1/workflows"],
        "signature": "n8n",
        "cve": "CVE-2026-21858",
        "severity": "CRITICAL"
    },
    "langflow": {
        "port": 7860,
        "paths": ["/api/v1/config", "/api/v1/flows", "/login"],
        "signature": "langflow",
        "cve": "CVE-2026-33017",
        "severity": "CRITICAL"
    },
    "chromadb": {
        "port": 8000,
        "paths": ["/api/v1/heartbeat", "/api/v1/version", "/api/v1/collections"],
        "signature": "chroma",
        "cve": "CVE-2026-45829",
        "severity": "CRITICAL"
    },
    "qdrant": {
        "port": 6333,
        "paths": ["/collections", "/healthz", "/metrics"],
        "signature": "qdrant",
        "cve": "No auth by default",
        "severity": "HIGH"
    },
    "jupyter": {
        "port": 8888,
        "paths": ["/tree", "/api", "/login", "/terminals"],
        "signature": "jupyter",
        "cve": "Multiple",
        "severity": "HIGH"
    },
    "ray_dashboard": {
        "port": 8265,
        "paths": ["/api/actors", "/api/jobs", "/api/overview"],
        "signature": "ray",
        "cve": "CVE-2023-6019",
        "severity": "CRITICAL"
    },
    "docker_api": {
        "port": 2375,
        "paths": ["/v1.24/containers/json", "/v1.24/info", "/version"],
        "signature": "Docker",
        "cve": "Full host RCE",
        "severity": "CRITICAL"
    },
    "kubernetes": {
        "port": 6443,
        "paths": ["/api/v1/nodes", "/api/v1/pods", "/version"],
        "signature": "kubernetes",
        "cve": "Cluster takeover",
        "severity": "CRITICAL"
    },
    "openclaw": {
        "port": 18789,
        "paths": ["/api/v1/status", "/api/v1/agents"],
        "signature": "openclaw",
        "cve": "CVE-2026-25253",
        "severity": "CRITICAL"
    },
    "mcp_inspector": {
        "port": 3001,
        "paths": ["/sse", "/mcp", "/api/mcp"],
        "signature": "mcp",
        "cve": "CVE-2026-23744",
        "severity": "CRITICAL"
    },
    "langfuse": {
        "port": 3000,
        "paths": ["/api/public/ingest", "/api/auth/session", "/api/traces"],
        "signature": "langfuse",
        "cve": "CVE-2026-41487",
        "severity": "HIGH"
    },
    "flowise": {
        "port": 3000,
        "paths": ["/api/v1/chatflows", "/api/v1/chatflows-streaming"],
        "signature": "flowise",
        "cve": "CVE-2025-59528",
        "severity": "CRITICAL"
    },
    "litellm": {
        "port": 4000,
        "paths": ["/health", "/v1/models", "/config/list"],
        "signature": "litellm",
        "cve": "Key exposure",
        "severity": "HIGH"
    }
}

def generate_curl_commands(target_ip):
    """Generate curl commands for probing a target"""
    commands = []
    for name, probe in PROBES.items():
        port = probe["port"]
        for path in probe["paths"]:
            url = f"http://{target_ip}:{port}{path}"
            commands.append({
                "service": name,
                "url": url,
                "signature": probe["signature"],
                "cve": probe["cve"],
                "severity": probe["severity"]
            })
    return commands

if __name__ == "__main__":
    # Generate probe commands for batch scanning
    print(json.dumps(list(PROBES.keys()), indent=2))
    print(f"\nTotal services to probe: {len(PROBES)}")
    print(f"Total endpoints per target: {sum(len(p['paths']) for p in PROBES.values())}")
    
    # Example: generate commands for a target
    if len(sys.argv) > 1:
        target = sys.argv[1]
        cmds = generate_curl_commands(target)
        for cmd in cmds:
            print(f"curl -sk --connect-timeout 5 '{cmd['url']}' | head -c 200  # {cmd['service']} - {cmd['cve']}")
