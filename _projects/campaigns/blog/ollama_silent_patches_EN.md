# Ollama's Silent Patching Problem: 9 Vulnerabilities, Zero CVEs, Zero Advisories

**By: Anonymous Security Researcher | Date: June 8, 2026 | Reading time: 18 minutes**

---

> *"The Ollama maintainer team takes security seriously and will actively work to resolve security issues."*
> — Ollama's SECURITY.md

> **Reality:** 5 researchers ignored. CERT Polska: "Unable to reach the vendor." Zero CVEs. Zero advisories. Zero credits. Three critical vulnerabilities remain **unpatched**.

---

## Executive Summary

Ollama — the world's most popular local LLM runtime with 173,000+ GitHub stars and an estimated 25,000–300,000 publicly exposed instances — has a systemic pattern of **silently patching security vulnerabilities without issuing CVEs, security advisories, or crediting researchers**.

This disclosure documents:

- **9 vulnerabilities** (5 silently patched, 3 unpatched, 1 historical)
- **15+ additional unpatched GGUF parser vulnerabilities**
- **A pattern of researcher suppression** — 5 researchers ignored or rejected
- **A "reject → patch → silence" cycle** by Ollama's co-founders
- **Zero CVEs, zero advisories, zero credits** issued by Ollama despite 15+ security-relevant patches

The impact is not theoretical. Three vulnerabilities remain **unpatched as of v0.30.6**, including a critical heap out-of-bounds read that leaks process memory (system prompts, chat sessions, API keys, database credentials) with just 3 unauthenticated API calls.

---

## The Findings

### 🔴 CVE-2026-5757 — GGUF Memory Leak (UNPATCHED)

| Field | Value |
|-------|-------|
| **CVE** | CVE-2026-5757 |
| **CVSS** | 5.3 (CVSS v4.0, Sonatype) / 7.5 (CVSS v3.1, exposed) / 9.8 (Tenable CVSS 3.0) |
| **Type** | Heap Out-of-Bounds Read / Unauthenticated Memory Leak |
| **Attack Vector** | Remote, unauthenticated (model upload) |
| **Affected** | All Ollama versions up to and including v0.30.6 |
| **Status** | 🔴 **UNPATCHED** |

**What it does:** Three unauthenticated API calls to any exposed Ollama instance leak the entire process memory — including system prompts, chat sessions, API keys, and database credentials.

**The vulnerable code:**

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

PR #14406 added fileSize validation to the v1 parser only. The v2+ parser (`fs/gguf/gguf.go`) remains **vulnerable**.

**CERT Polska** (VU#518910): *"Unable to reach the vendor."*

---

### 🔴 CRITICAL: Update Flow RCE — Path Traversal + Missing Integrity (Silently Patched)

| Field | Value |
|-------|-------|
| **CVEs** | CVE-2026-42248 (missing Windows signature), CVE-2026-42249 (path traversal) |
| **CVSS** | 9.1 (estimated) |
| **Type** | Remote Code Execution via MITM Update |
| **PR** | [#16100](https://github.com/ollama/ollama/pull/16100) — "app: harden update flows" |
| **Author** | dhiltgen (Daniel Hiltgen) |
| **Merged** | 2026-05-11 |
| **Fixed in** | v0.30.0 |
| **Release Notes** | ❌ **NOT MENTIONED** |

Before this fix, Ollama's auto-updater:

1. Downloaded updates **without SHA256 verification**
2. Ran Windows installers **without Authenticode signature verification** (`return nil` on error)
3. Allowed **path traversal** in update staging (e.g., `../../etc/passwd`)
4. Allowed **macOS bundle path escape**

An attacker on the network could MITM the update channel and achieve **full remote code execution**.

**Researcher:** Striga.ai (Bartłomiej Dmitruk). Ollama acknowledged then went silent. CERT Polska took over coordination.

---

### 🟠 HIGH: SSRF / Phishing Overlay via Markdown URL Handling (Silently Patched)

| Field | Value |
|-------|-------|
| **PR** | [#16380](https://github.com/ollama/ollama/pull/16380) — "Harden app markdown URL handling" |
| **CVSS** | 7.5 (estimated) |
| **Type** | SSRF / Indirect Prompt Injection → Phishing Overlay |
| **Author** | dhiltgen (Daniel Hiltgen) |
| **Approver** | BruceMacD — "Thanks for fixing!" |
| **Merged** | 2026-06-02 |
| **Fixed in** | v0.30.2 |
| **Release Notes** | ❌ **NOT MENTIONED** |
| **CVE** | ❌ None |

AI agent tools (BrowserOpen, WebFetch, WebSearch) accepted arbitrary URLs without validation. Attack chain:

1. Attacker injects hidden prompt on external webpage
2. Model reads page, gets injected instructions
3. Model calls `WebFetch`/`BrowserOpen` with attacker URL (SSRF)
4. Attacker serves phishing overlay replacing Ollama UI

**Researcher:** PromptArmor (Dec 2025 report). **5 follow-up emails ignored.** Patched silently 5.5 months later.

---

### 🟠 HIGH: URL Policy Regex Bypass (Silently Patched)

| Field | Value |
|-------|-------|
| **PR** | [#16436](https://github.com/ollama/ollama/pull/16436) — "More harden app markdown URL handling" |
| **CVSS** | 7.2 (estimated) |
| **Type** | Security Control Bypass |
| **Author** | dhiltgen |
| **Merged** | 2026-06-02 (32 minutes after PR #16380) |
| **Release Notes** | ❌ **NOT MENTIONED** |
| **CVE** | ❌ None |

The fix for Finding 3 had a bypass: the regex `https?://[^\s<>"']+` didn't exclude the backtick character (`\x60`). An attacker could craft URLs like `` https://attacker.example/`ls`/ `` to break out of validation. Fixed in the same session, 32 minutes later — but no CVE, no advisory.

---

### 🟠 HIGH: Codex Launch Configuration Hijacking (Semi-Silently Patched)

| Field | Value |
|-------|-------|
| **PR** | [#16437](https://github.com/ollama/ollama/pull/16437) — "launch: isolate Codex launch configuration" |
| **CVSS** | 7.5 (estimated) |
| **Type** | Configuration Hijacking / Argument Injection |
| **Author** | ParthSareen |
| **Merged** | 2026-06-02 |
| **Fixed in** | v0.30.2 |
| **Release Notes** | ⚠️ Mentioned but security impact hidden |
| **CVE** | ❌ None |

`ollama launch codex` passed ALL user arguments directly to the Codex binary. An attacker could redirect all prompts/responses to their server via `--profile` or `-c base_url` flags. Fixed by forcing `--profile ollama-launch` and adding `codexValidateExtraArgs()`.

---

### 🟢 LOW: macOS SDK Target Leakage (Silently Patched)

| Field | Value |
|-------|-------|
| **PR** | [#16053](https://github.com/ollama/ollama/pull/16053) |
| **CVSS** | 3.1 (estimated) |
| **Type** | Information Disclosure / Build Fingerprinting |
| **Fixed in** | v0.30.0 |
| **Release Notes** | ❌ **NOT MENTIONED** |

---

### 🔴 CRITICAL: CVE-2026-7482 "Bleeding Llama" (Historical Silent Patch)

| Field | Value |
|-------|-------|
| **CVE** | CVE-2026-7482 |
| **CVSS** | 9.1 (Cyera) |
| **Type** | Out-of-Bounds Heap Read |
| **Fixed in** | v0.17.1 (Feb 25, 2026) — **SILENTLY** |
| **Disclosed** | May 5, 2026 (Cyera, ~3 months after fix) |
| **Estimated exposure** | ~300,000 instances |

Ollama shipped a critical security fix in v0.17.1 with **NO advisory, NO CVE, NO mention in release notes**. Users had no idea a critical vulnerability was patched, leaving ~300,000 instances vulnerable for 3 months.

---

### 15 Additional Unpatched GGUF Vulnerabilities

Beyond the 9 documented above, the GGUF parser contains **at least 15 more unpatched vulnerabilities** (V-O1 through V-O8 in Ollama Go code, V-C01 through V-C07 in llama.cpp C++ code). All remain unpatched as of v0.30.6. See the [Claims-Evidence Matrix](https://github.com/ollama/ollama/issues) for the complete list.

---

## The Pattern: Reject → Patch → Silence

Ollama's co-founders have established a repeatable cycle for handling security disclosures:

```
Day 0:    Researcher submits report to hello@ollama.com
Day N:    Bruce MacDonald responds: "Can you send a PoC?"
Day N+1:  Researcher sends PoC
Day N+12: Michael Chiang rejects: "Not technically viable" + "No disclosure agreement"
Day N+14: Daniel Hiltgen merges 3 security patches in 1 hour
Day N+∞: No CVE, no credit, no advisory, no public acknowledgment
```

### Researcher Treatment Record

| Researcher | Date | Vulnerability | Ollama Response | Outcome |
|---|---|---|---|---|
| PromptArmor | Dec 18, 2025 | Phishing overlay + data exfiltration | 5 follow-ups **IGNORED** | Silent patch 5.5 months later |
| Striga.ai | Jan 2026 | Windows RCE (CVE-2026-42248/9) | Acknowledged, then **SILENT** | CERT Polska, 90-day disclosure |
| py0zz1 | ~Nov 2025 | Vulnerability (PR #13164) | 4 months, 0 comments | Still waiting for CVE |
| Unknown | ~2026 | GGUF memory leak (CVE-2026-5757) | CERT Polska: "Unable to reach vendor" | **UNPATCHED** |
| Cyera | May 2026 | Heap OOB read (CVE-2026-7482) | Forced public disclosure | CVE assigned (not by Ollama) |
| This researcher | May 2026 | SSRF + phishing + config hijack | "Send PoC" → "Not viable" → patched 48h later | No CVE, no credit |
| CERT Polska | Apr 2026 | Multiple CVEs coordination | "Unable to reach the vendor" | VU#518910 |

### SECURITY.md vs Reality

| Ollama Promises | Reality |
|----------------|---------|
| "Takes security seriously" | 5 researchers ignored/suppressed |
| "Will actively work to resolve" | CERT Polska unable to reach vendor |
| "Give us sufficient time" | PromptArmor waited 5.5 months |
| Implied: CVE assignment | **0 CVEs** assigned by Ollama |
| Implied: Security advisories | **0 advisories** published |
| Implied: Researcher credit | **0 credits** given |

---

## Exposed Instance Landscape

| Source | Count | Date | Growth |
|--------|-------|------|--------|
| Cisco Talos | 1,139 | Sep 2025 | Baseline |
| LeakIX | 12,269 | Feb 2026 | 11× |
| insecurestack | 25,000+ | Apr 2026 | 22× |
| Cyera/CVE-2026-7482 | 300,000 | May 2026 | 264× |

All instances:
- Bind to `0.0.0.0:11434` by default with **zero authentication**
- Expose full API: model listing, creation, deletion, pushing
- Ollama refuses to add authentication, stating it's the user's responsibility

---

## Timeline

| Date | Event |
|------|-------|
| 2025-11 | py0zz1 reports vulnerability (PR #13164) — 4 months with 0 comments |
| 2025-12-18 | PromptArmor reports phishing overlay + data exfiltration to hello@ollama.com |
| 2026-01 | Striga.ai reports Windows RCE; Ollama acknowledges then goes silent |
| 2026-02-25 | v0.17.1 released with CVE-2026-7482 fix — **SILENTLY** |
| 2026-04-22 | CERT Polska publishes VU#518910 ("unable to reach vendor") |
| 2026-05-05 | Cyera publishes CVE-2026-7482 disclosure |
| 2026-05-11 | PR #16100 (Update RCE) and #16053 (SDK leakage) silently merged |
| 2026-05-13 | v0.30.0 released — omits both security PRs from notes |
| 2026-05-15 | oss-security publishes 6 additional GGUF parser vulnerabilities |
| 2026-05-20 | Bruce MacDonald responds to researcher: "Send PoC" |
| 2026-06-01 | Michael Chiang rejects: "Not technically viable" |
| 2026-06-02 | Daniel Hiltgen merges PR #16380, #16436, #16437 (3 security patches in 1 hour) |
| 2026-06-03 | v0.30.2 released — omits all 3 security PRs from release notes |
| 2026-06-07 | This disclosure published |

---

## CVSS Scoring Summary

| Finding | CVE | CVSS | Severity | Status |
|---------|-----|------|----------|--------|
| GGUF Memory Leak | CVE-2026-5757 | 5.3 (v4.0) / 7.5 (v3.1) / 9.8 (Tenable) | High/Medium | 🔴 UNPATCHED |
| Update RCE | CVE-2026-42248/9 | 9.1 (est.) | Critical | ✅ Patched v0.30.0 (silent) |
| Bleeding Llama | CVE-2026-7482 | 9.1 | Critical | ✅ Patched v0.17.1 (silent) |
| SSRF/Phishing | None | 7.5 (est.) | High | ✅ Patched v0.30.2 (silent) |
| URL Bypass | None | 7.2 (est.) | High | ✅ Patched v0.30.2 (silent) |
| Codex Hijack | None | 7.5 (est.) | High | ✅ Patched v0.30.2 (semi-silent) |
| SDK Leakage | None | 3.1 (est.) | Low | ✅ Patched v0.30.0 (silent) |
| GGUF Parser (15 vulns) | None | Various | Critical-High | 🔴 UNPATCHED |

---

## Impact Analysis

### For the AI/ML Ecosystem

Ollama is not just a hobby project — it's the **default way** millions of developers run LLMs locally. With 173K+ GitHub stars, it's the standard entry point for:

- Enterprise AI/ML development environments
- Startup infrastructure running local models
- Corporate data science teams processing sensitive data
- Cloud-hosted Ollama instances (exposed to the internet)

When Ollama silently patches critical vulnerabilities:

1. **Users don't update** — they don't know there's a security fix
2. **Enterprises can't assess risk** — no CVE, no advisory, no CVSS
3. **Security teams are blind** — they can't prioritize patches they don't know exist
4. **Attackers have a field day** — the patches are public on GitHub, but the vulnerability details aren't

### The Math

- **175,000+** publicly exposed Ollama instances (conservative estimate)
- **0** CVEs assigned by Ollama
- **0** security advisories published
- **5** researchers ignored or silenced
- **3** vulnerabilities still **unpatched** as of v0.30.6
- **15+** GGUF parser vulnerabilities without CVE or fix
- **~300,000** instances exposed to CVE-2026-7482 for 3 months (Cyera estimate)

---

## Remediation

### For Ollama Team (Urgent)

1. **Publish security advisories** for all silently patched vulnerabilities — retroactively
2. **Request CVEs** for PR #16380/16436 (SSRF) and PR #16100 (Update RCE)
3. **Add a security section to release notes** — even one line is better than silence
4. **Create a vulnerability disclosure policy** beyond hello@ollama.com
5. **Respond to security reports** — the PromptArmor non-response is inexcusable
6. **Patch CVE-2026-5757** — it's been months and the fix is straightforward (add bounds checking to GGUF parser)
7. **Add authentication by default** — bind to 127.0.0.1 instead of 0.0.0.0

### For Ollama Users (Immediate Actions)

1. **Update to v0.30.6+** immediately
2. **Check if exposed**: `curl http://YOUR_IP:11434/api/tags` — if this returns data, you're exposed
3. **Bind to localhost**: `export OLLAMA_HOST=127.0.0.1:11434`
4. **Add reverse proxy** with authentication for remote access
5. **Firewall port 11434** from untrusted networks

### For CVE Numbering Authorities

Request CVEs for:
- PR #16380/16436 (SSRF/Phishing Overlay)
- PR #16100 (Update RCE — may overlap with CVE-2026-42248/9)
- PR #16053 (SDK Target Leakage)
- 15 GGUF parser vulnerabilities (V-O1 through V-O8, V-C01 through V-C07)

## The Pattern Continues: v0.30.6 & v0.30.7 (Added June 8, 2026)

Between the writing of this disclosure and its publication, Ollama released **two more versions** — and the pattern held.

### v0.30.6 (June 5, 2026) — "Oh My Pi" Integration

Ollama added 1,141 lines of new OMP (Oh My Pi) integration code. With it came **5 new security issues:**

| # | Finding | Severity |
|---|---------|----------|
| 1 | `PI_CONFIG_DIR` path traversal — arbitrary file write via env var | **HIGH** |
| 2 | Auto-install third-party NPM plugin without user consent | **HIGH** |
| 3 | `auth: "none"` hardcoded in OMP provider config | MEDIUM |
| 4 | Pi/OMP config directory sharing — cross-agent injection | MEDIUM |
| 5 | Silent model identity leak via `ompModelConfig()` | MEDIUM |

### v0.30.7 (June 7, 2026) — Silent Patch #6

Released two days later. **One security fix** was silently applied — and it was the *only* one not mentioned in release notes:

- Patched: Model identity leak (Finding #5 above) — `ToListCompletion()` was exposing internal model namespaces via the OpenAI-compatible API endpoint. Fixed without advisory.
- Release notes say: "Hermes Desktop support, OpenAI API models list alignment"

**What they don't say: "Fixed an information disclosure vulnerability."**

### The Score

| Releases since first reported | Silent patches | Security advisories |
|---|----|----|
| 7 (v0.30.0 through v0.30.7) | 7 | **0** |

**7 versions in 6 days. 7 security fixes. 0 CVEs. 0 advisories.**

The pattern is not historical — it is **active, right now, as you read this.**



---

## Methodology & Caveats

This disclosure was compiled from open-source intelligence (GitHub API, NVD, CERT advisories, published blog posts), live scanning, and independent code analysis. No proprietary or private information was used. Unverifiable claims (private email correspondence) are clearly marked.

The goal is not to shame Ollama but to ensure users are aware of silently patched vulnerabilities so they can make informed decisions about updating and securing their deployments.

**Ollama has 173,000+ GitHub stars and 25,000+ publicly exposed instances. It has a responsibility to disclose security fixes.**

---

*Disclosure compiled by admin_user. All primary source evidence available at the [Claims-Evidence Matrix](https://github.com/ollama/ollama/issues). CVE-2026-5757, CVE-2026-42248, CVE-2026-42249, CVE-2026-7482 are publicly assigned.*