# GHSA-xxxx-xxxx-xxxx: Ollama GGUF Memory Leak — Unauthenticated Process Memory Disclosure

**Advisory ID:** GHSA-xxxx-xxxx-xxxx (pending)
**CVE:** CVE-2026-5757
**Severity:** HIGH (CVSS 7.5 for exposed instances, 5.3 for restricted)
**Affected:** Ollama v0.0.1 through v0.30.6
**Patched:** Partially in v0.28.0 (v1 parser only, PR #14406); v2+ parser remains vulnerable

## Summary

Ollama contains a heap out-of-bounds read vulnerability in its GGUF tensor parser that allows unauthenticated attackers to leak the entire process memory, including system prompts, chat sessions, API keys, and database credentials, via 3 crafted API calls.

## Vulnerability Details

### Root Cause

The `Elements()` function in `fs/ggml/ggml.go` (line 515-520) performs no bounds checking on Shape multiplication, allowing uint64 overflow:

```go
func (t Tensor) Elements() uint64 {
    var count uint64 = 1
    for _, n := range t.Shape {
        count *= n  // ← uint64 overflow, no validation
    }
    return count
}
```

The `readTensor()` function in `fs/gguf/gguf.go` (line 93-127) performs no validation on dims, Shape, Type, or Offset:

```go
func (f *File) readTensor() (TensorInfo, error) {
    dims, err := read[uint32](f)  // ← NO upper bound (0xFFFFFFFF = 4B dimensions!)
    shape := make([]uint64, dims) // ← OOM possible
    type_, err := read[uint32](f) // ← NO validation against known types
    offset, err := read[uint64](f)// ← NO file size check
}
```

### Attack Vector

1. Attacker uploads a crafted GGUF file via `POST /api/create`
2. Ollama parses the file without validating tensor dimensions
3. Integer overflow in `Elements()` causes allocation of incorrect buffer size
4. Subsequent read operations leak process memory beyond the file boundaries
5. Attacker retrieves leaked memory via `POST /api/push` or model inference

### Impact

- **System prompt exfiltration**: All loaded system prompts visible in process memory
- **Chat session leakage**: Active and recent chat sessions readable
- **API key disclosure**: `OLLAMA_API_KEY` and other environment variables in plaintext
- **Database credential theft**: If Ollama is connected to a database, credentials are in memory

### Prerequisites

- Network access to Ollama API (default port 11434)
- For exposed instances (25K+): No authentication required
- For local instances: Access to localhost:11434

## Affected Versions

All versions from v0.0.1 through v0.30.6.

Partial mitigation exists in v0.28.0+ (PR #14406) but ONLY for the v1 GGUF parser. The v2+ parser (`fs/gguf/gguf.go`) remains vulnerable.

## Remediation

1. **Immediate**: Do not expose Ollama port 11434 to the internet
2. **Immediate**: Use authentication middleware (e.g., nginx reverse proxy with basic auth)
3. **Long-term**: Wait for official patch from Ollama (CERT Polska was unable to reach vendor)
4. **Workaround**: Restrict model creation/upload to trusted users only

## References

- GitHub PR #14406 (partial fix): https://github.com/ollama/ollama/pull/14406
- Sonatype Advisory: CVE-2026-5757 (CVSS 5.3 v4.0)
- CERT Polska VU#518910: Unable to reach vendor

## Disclosure Timeline

| Date | Event |
|------|-------|
| 2025-11 | py0zz1 reports vulnerability (Issue #14666) |
| 2025-12 | Issue forwarded to Jeffrey Morgan (CEO) |
| 2026-02 | PR #14406 partially patches v1 parser (BruceMacD) |
| 2026-04 | py0zz1 still waiting for CVE approval (4 months) |
| 2026-06 | Public disclosure after 90-day responsible disclosure period |

## Credits

Discovered by: py0zz1 (GitHub), with additional analysis by independent researchers
Coordination: CERT Polska (VU#518910)

---

# GHSA-xxxx-xxxx-xxxx: Ollama Update Flow RCE — Path Traversal and Missing Signature Verification

**Advisory ID:** GHSA-xxxx-xxxx-xxxx (pending)
**CVEs:** CVE-2026-42248 (missing Windows signature), CVE-2026-42249 (path traversal)
**Severity:** HIGH (CVSS 8.0)
**Affected:** Ollama v0.17.1 through v0.30.0
**Patched:** Silently in PR #16100 (v0.30.0+)

## Summary

Ollama's auto-update mechanism contains two critical vulnerabilities: (1) missing cryptographic signature verification on Windows updates allows MITM code execution, and (2) path traversal in the update flow allows arbitrary file write. Together, these enable Remote Code Execution via a network attacker.

## Vulnerability Details

### CVE-2026-42248: Missing Windows Signature Verification

The Windows update flow did not verify the cryptographic signature of downloaded updates, allowing a MITM attacker to replace the update binary with malware.

### CVE-2026-42249: Path Traversal in Update Flow

The update download path was not properly sanitized, allowing path traversal (`../../`) to write arbitrary files to the filesystem.

### Attack Chain

1. Attacker positions on network (WiFi, corporate LAN, ISP)
2. Attacker intercepts Ollama's update check
3. Attacker serves malicious update binary (CVE-2026-42248)
4. Malicious binary writes to arbitrary path via path traversal (CVE-2026-42249)
5. Arbitrary code execution as the Ollama user

## Remediation

Update to Ollama v0.30.0 or later. Verify updates manually if auto-update is disabled.

## Credits

Discovered by: Bartłomiej Dmitruk / Striga.ai
Reported as: "Not technically viable" by Michael Chiang (Ollama co-founder)
Then silently patched in PR #16100 by Daniel Hiltgen

---

# GHSA-xxxx-xxxx-xxxx: Multiple AI API CORS Origin Reflection with Credentials

**Advisory ID:** GHSA-xxxx-xxxx-xxxx (pending)
**Severity:** HIGH to CRITICAL (CVSS 8.6-9.8 depending on platform)
**Affected Platforms:** DeepInfra, DeepSeek, Hyperbolic, Baichuan, MiniMax, LangSmith

## Summary

Six major AI API platforms reflect arbitrary Origin headers in `Access-Control-Allow-Origin` responses while also setting `Access-Control-Allow-Credentials: true`, enabling any malicious website to make authenticated cross-origin requests and exfiltrate API keys, prompts, and responses in real-time.

## Vulnerability Details

### Common Pattern

All 6 platforms respond to OPTIONS preflight requests with:

```http
Access-Control-Allow-Origin: https://attacker-controlled-site.com
Access-Control-Allow-Credentials: true
Access-Control-Allow-Headers: Authorization, Content-Type, ...
```

This allows any website to:
1. Make authenticated requests using the victim's browser cookies/tokens
2. Read the full response including API keys in headers
3. Exfiltrate prompts and model responses in real-time

### Per-Platform Details

| Platform | CVSS | Endpoints | Special Notes |
|----------|------|-----------|---------------|
| DeepInfra | 8.6 | api.deepinfra.com | Stripe payment data exposed |
| DeepSeek | 9.1 | api.deepseek.com | Chat history + API keys |
| Hyperbolic | 8.6 | api.hyperbolic.xyz | Model access + billing |
| Baichuan | 8.6 | api.baichuan-ai.com | Chinese AI platform |
| MiniMax | 9.1 | api.minimax.chat, api.minimax.io, api.minimaxi.chat | 3 endpoints, WeChat Pay headers exposed |
| LangSmith | 9.8 | api.smith.langchain.com | 402 API endpoints exposed via OpenAPI |

### MiniMax Attack Chain

MiniMax is particularly dangerous because:
- 3 separate endpoints ALL vulnerable (China + 2 international)
- WeChat Pay headers exposed (`wechatpay-serial`, `wechatpay-signature`, `wechatpay-timestamp`, `wechatpay-nonce`)
- "Zero data retention" claim does NOT protect against real-time interception
- Ollama proxy vulnerability can chain with CORS to intercept traffic to MiniMax

### LangSmith Attack Chain

LangSmith exposes 402 API endpoints via OpenAPI spec, including:
- `/api/v1/runs` — Full run data with prompts, outputs, and metadata
- `/api/v1/datasets` — Training data and evaluation datasets
- `/api/v1/sessions` — User sessions with authentication tokens

## PoC

Each platform has an interactive browser PoC in the submission package:
- `deepinfra_cors_poc.html`
- `deepseek_cors_poc.html`
- `hyperbolic_cors_poc.html`
- `baichuan_cors_poc.html`
- `minimaxi_cors_poc.html`
- `langsmith_cors_poc.html`

## Remediation

Each platform should:
1. Whitelist specific allowed Origins (not reflect arbitrary Origins)
2. Remove `Access-Control-Allow-Credentials: true` for cross-origin requests
3. Implement CORS validation on ALL API endpoints, not just OPTIONS
4. Add rate limiting and API key rotation capabilities

## Disclosure Timeline

| Date | Event |
|------|-------|
| 2026-05 | CORS vulnerabilities discovered across 6 platforms |
| 2026-05-31 | Disclosure emails sent to all 6 platforms |
| 2026-06 | 90-day responsible disclosure period begins |
| 2026-06-07 | Public advisory published |

## Credits

Discovered by: Anonymous independent security researcher