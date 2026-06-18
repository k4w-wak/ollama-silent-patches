# 🔴 N8N + Flowise + Langflow Hunter — Vulnerability Intelligence Report

**Date:** 2026-06-03  
**Author:** admin_user  
**Classification:** CRITICAL — Active Exploitation Confirmed

---

## 📋 Executive Summary

Three critical workflow automation / AI pipeline platforms — **n8n**, **Flowise**, and **Langflow** — are widely exposed on the internet with known, actively exploited RCE vulnerabilities. Combined, **~50,000+ instances** are publicly accessible, many running unpatched versions.

| Platform | Exposed Instances (est.) | Critical CVE | CVSS | Auth Required | Impact |
|----------|-------------------------|--------------|------|---------------|--------|
| **n8n** | ~30,000 | CVE-2026-21858 | **10.0** | None (unauth) | Full RCE, credential theft, lateral movement |
| **Flowise** | ~15,000 | CVE-2025-59528 | **10.0** | Auth (but often default/no auth) | Full RCE via customMCP |
| **Langflow** | ~5,000 | CVE-2026-33017 | **9.3** | None (unauth via public flows) | Full RCE via exec() injection |

---

## 🔴 CVE-2026-21858 — n8n "Ni8mare" Unauthenticated RCE

### Overview
- **CVSS:** 10.0 CRITICAL
- **Published:** 2026-01-07
- **Affected:** n8n < 1.121.0 (patched in 1.121.0+)
- **Authentication:** NONE required
- **Attack Vector:** Network (remote)

### Vulnerability Details
n8n's webhook request handling fails to validate Content-Type headers properly before processing file uploads. An attacker can:
1. Send a crafted POST to any active webhook endpoint
2. Override `req.body` and `req.files` via multipart/form-data manipulation
3. Read arbitrary files from the server
4. Chain to full RCE via credential theft + workflow manipulation

### Key Endpoints
| Endpoint | Method | Exposure | Risk |
|----------|--------|----------|------|
| `/rest/settings` | GET | **No auth required** | Leaks: version, instanceId, deploymentType, oauthEnabled, releaseChannel |
| `/rest/workflows` | GET | Auth-dependent | Lists all workflows if auth disabled |
| `/rest/credentials` | GET | Auth-dependent | Leaks credential metadata |
| `/rest/executions` | GET | Auth-dependent | Execution history |
| `/webhook` | POST | **No auth required** | CVE-2026-21858 exploitation vector |
| `/rest/systemInfo` | GET | **No auth required** | Server version, node.js version |

### Detection (Shodan Dorks)
```
port:5678 title:"n8n"
port:5678 "n8n" http.title:"n8n"
product:"n8n"
```
~30,000 publicly exposed instances indexed.

### /rest/settings Information Disclosure
The `/rest/settings` endpoint returns sensitive configuration **without authentication**:
```json
{
  "version": "1.120.0",
  "oauthType": "default",
  "oauthEnabled": false,
  "publicApiEnabled": true,
  "instanceId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "deploymentType": "default",
  "releaseChannel": "stable"
}
```
This reveals the exact version (for targeting specific CVEs), deployment type, and API status.

### Exploit Chain
1. **Recon:** `GET /rest/settings` → version confirmation
2. **File Read:** `POST /webhook/{id}` with crafted multipart → read `/etc/passwd`, `/home/*/.ssh/id_rsa`
3. **Credential Theft:** Read n8n config files containing database credentials, API keys
4. **RCE:** Use stolen credentials to create malicious workflow → execute arbitrary commands

---

## 🔴 CVE-2025-59528 — Flowise CustomMCP RCE

### Overview
- **CVSS:** 10.0 CRITICAL (some sources: 9.8)
- **Published:** 2025-09-22
- **Affected:** Flowise ≤ 3.0.4 (patched in 3.0.5+)
- **Authentication:** Required (but often default/no auth on instances)
- **Attack Vector:** Network (remote)

### Vulnerability Details
Flowise's `/api/v1/node-load-method/customMCP` endpoint allows authenticated users to inject arbitrary Python code through the CustomMCP node configuration. The code is executed via `exec()` on the server, leading to full system compromise.

### Key Endpoints
| Endpoint | Method | Exposure | Risk |
|----------|--------|----------|------|
| `/api/v1` | GET | Public | API version, health check |
| `/api/v1/chatflows` | GET | Auth-dependent | Lists all chatflows (data exposure) |
| `/api/v1/workflows` | GET | Auth-dependent | Lists all workflows |
| `/api/v1/credentials` | GET | Auth-dependent | Credential metadata |
| `/api/v1/node-load-method/customMCP` | POST | **Auth required** | CVE-2025-59528 exploitation vector |
| `/api/v1/predictions` | POST | Varies | Run predictions (data exfil) |
| `/api/v1/config` | GET | Varies | Server configuration |

### Detection (Shodan Dorks)
```
port:3000 title:"Flowise"
port:3000 "flowise" http.title:"Flowise"
product:"Flowise"
```
~15,000 publicly exposed instances.

### Additional Flowise CVEs
| CVE | CVSS | Description |
|-----|------|-------------|
| CVE-2026-40933 | 9.9 | One-click RCE via malicious chatflow import |
| CVE-2024-36425 | 9.1 | Prompt injection leading to code execution |

---

## 🔴 CVE-2026-33017 — Langflow Unauthenticated RCE

### Overview
- **CVSS:** 9.3 CRITICAL
- **Published:** 2026-03-20
- **Affected:** Langflow ≤ 1.8.2 (patched in 1.9.0+)
- **Authentication:** NONE required (when public flows exist)
- **Attack Vector:** Network (remote)

### Vulnerability Details
Langflow's public flow build endpoint allows unauthenticated remote code execution via `exec()` injection. When AUTO_LOGIN is enabled (common for demos/chatbots), an attacker can:
1. Discover public flow UUIDs via shared links or API
2. Send crafted build requests with Python code injection
3. Execute arbitrary commands on the server

This is the **fourth RCE-class vulnerability** in Langflow since 2025, revealing a systemic pattern of unsafe `exec()` usage.

### Key Endpoints
| Endpoint | Method | Exposure | Risk |
|----------|--------|----------|------|
| `/api/v1` | GET | Public | API health |
| `/api/v1/flows` | GET | Varies | List flows |
| `/api/v1/flows/public` | GET | **No auth** | Public flow discovery |
| `/api/v1/build` | POST | **No auth (with public flow)** | CVE-2026-33017 exploitation vector |
| `/api/v1/auto_login` | POST | Public | Confirms AUTO_LOGIN enabled |
| `/api/v1/process` | POST | Varies | Process execution |
| `/api/v1/config` | GET | Varies | Configuration disclosure |

### Detection (Shodan Dorks)
```
port:7860 title:"Langflow"
port:7860 "langflow" http.title:"Langflow"
product:"Langflow"
```
~5,000 publicly exposed instances.

### Exploit Chain
1. **Recon:** `GET /api/v1/auto_login` → confirm AUTO_LOGIN enabled
2. **Flow Discovery:** `GET /api/v1/flows/public` → get flow UUIDs
3. **Code Injection:** `POST /api/v1/build/{flow_id}` with Python payload
4. **RCE:** Arbitrary command execution on server

### Previous Langflow CVEs (Pattern)
| CVE | Description |
|-----|-------------|
| CVE-2025-3248 | Similar exec() injection |
| CVE-2025-4673 | Another code execution flaw |
| CVE-2025-5627 | Further exec() abuse vector |

---

## 🛠️ Scanner Tool

**File:** `/home/admin_user/Projects/ai_infra_scan/scanners/n8n_flowise_langflow_hunter.py`

### Usage
```bash
# Single target
python3 n8n_flowise_langflow_hunter.py http://target:5678

# Multiple targets
python3 n8n_flowise_langflow_hunter.py http://target1:5678 http://target2:3000 http://target3:7860

# From file
python3 n8n_flowise_langflow_hunter.py --file targets.txt
```

### OPSEC
- All requests routed through **Tor SOCKS5 proxy** (127.0.0.1:9050)
- No real IP leakage
- Randomized User-Agent headers

---

## 📊 Shodan Search Strategies

### n8n Discovery
```
port:5678 title:"n8n"
port:5678 "n8n" http.title:"n8n"
product:"n8n" country:US
```

### Flowise Discovery
```
port:3000 title:"Flowise"
port:3000 "flowise" http.title:"Flowise"  
product:"Flowise" country:US
```

### Langflow Discovery
```
port:7860 title:"Langflow"
port:7860 "langflow" http.title:"Langflow"
product:"Langflow" country:US
```

### Combined (all three)
```
(port:5678 title:"n8n") OR (port:3000 title:"Flowise") OR (port:7860 title:"Langflow")
```

---

## 🎯 Attack Priority Matrix

| Priority | Platform | CVE | Auth Needed? | Ease | Impact |
|----------|----------|-----|-------------|------|--------|
| 🥇 **1** | n8n | CVE-2026-21858 | None | Easy | Full RCE + credential theft |
| 🥈 **2** | Langflow | CVE-2026-33017 | None (public flows) | Medium | Full RCE |
| 🥉 **3** | Flowise | CVE-2025-59528 | Auth required | Medium | Full RCE |

### Low-Hanging Fruit
1. **n8n `/rest/settings`** — No auth required, leaks version + config on ~30K instances
2. **Langflow `/api/v1/auto_login`** — Confirms AUTO_LOGIN enabled (no auth needed)
3. **Flowise `/api/v1/chatflows`** — Often accessible without auth, leaks flow data
4. **All platforms** — Default credentials on fresh deployments
5. **n8n webhook URLs** — Guessable webhook IDs for workflow manipulation

---

## 🔧 Recommended Remediation

### n8n (CVE-2026-21858)
- Upgrade to **n8n ≥ 1.121.0**
- Restrict `/rest/settings` to authenticated users
- Block webhook access from untrusted networks
- Enable authentication on all instances

### Flowise (CVE-2025-59528)
- Upgrade to **Flowise ≥ 3.0.5** (or latest 3.1.0+ for CVE-2026-40933)
- Restrict `/api/v1/node-load-method/customMCP` to admin users
- Enable authentication on all instances
- Monitor POST requests to customMCP endpoint

### Langflow (CVE-2026-33017)
- Upgrade to **Langflow ≥ 1.9.0**
- Disable AUTO_LOGIN in production
- Restrict public flow access
- Remove or sandbox `exec()` capabilities

---

## 📝 References

1. [Cyera: Ni8mare - n8n Unauthenticated RCE](https://www.cyera.com/research/ni8mare-unauthenticated-remote-code-execution-in-n8n-cve-2026-21858)
2. [Orca Security: CVE-2026-21858 n8n RCE](https://orca.security/resources/blog/cve-2026-21858-n8n-rce-vulnerability/)
3. [Hacker News: Critical n8n CVSS 10.0](https://thehackernews.com/2026/01/critical-n8n-vulnerability-cvss-100.html)
4. [CSA: CVE-2026-33017 Langflow RCE](https://labs.cloudsecurityalliance.org/research/csa-research-note-cve-2026-33017-langflow-ai-pipeline-rce-20/)
5. [SonicWall: Flowise CustomMCP RCE](https://www.sonicwall.com/blog/flowiseai-custom-mcp-node-remote-code-execution-)
6. [Exploit-DB: Flowise 3.0.4 RCE](https://www.exploit-db.com/exploits/52440)
7. [GitHub: CVE-2026-21858 PoC](https://github.com/Chocapikk/CVE-2026-21858)
8. [GitHub: CVE-2026-33017 Exploit](https://github.com/oscar-mine/CVE-2026-33017-Exploit)
9. [GitHub: Flowise RCE CVE-2025-59528](https://github.com/r3nsi15/Flowise-RCE-CVE-2025-59528)
10. [pwned.nexus: Langflow Public Flow RCE](https://pwned.nexus/posts/2026-03-22-langflow-public-flow-rce/)

---

**Report generated:** 2026-06-03  
**Scanner:** n8n_flowise_langflow_hunter.py v1.0  
**OPSEC:** All traffic via Tor SOCKS5 proxy