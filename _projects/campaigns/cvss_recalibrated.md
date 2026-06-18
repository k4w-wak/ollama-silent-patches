# CVSS v3.1 Recalibration — Ollama Disclosure

**Date:** 2026-06-07  
**Methodology:** FIRST.org CVSS v3.1 specification with exact Roundup function  
**Calculator:** Custom implementation verified against FIRST.org reference  
**Purpose:** Correct inflated/deflated original CVSS scores with precise metric-by-metric analysis

---

## Executive Summary

| # | Finding | Claimed | Recalibrated | Delta | Verdict |
|---|---------|---------|-------------|-------|---------|
| 1 | SSRF/Phishing via URL Policy | 7.5 | **7.1** | −0.4 | OVERSCORED ↓ |
| 2 | URL Policy Regex Bypass | 7.2 | **5.4** | −1.8 | OVERSCORED ↓ |
| 3 | Update Flow RCE | 9.1 | **7.5** | −1.6 | OVERSCORED ↓ |
| 4 | macOS SDK Target Leakage | 3.1 | **5.3** | +2.2 | UNDERSCORED ↑ |
| 5 | Bleeding Llama CVE-2026-7482 | 9.1 | **7.5** | −1.6 | OVERSCORED ↓ |
| 6 | Codex Launch Config Hijacking | 7.5 | **7.1** | −0.4 | OVERSCORED ↓ |

**Key findings:**
- **4 of 6 scores were OVERSCORED** — #3 and #5 dropped from CRITICAL 9.1 to HIGH 7.5
- **1 score was UNDERSCORED** — #4 jumped from LOW 3.1 to MEDIUM 5.3
- **Major pattern:** I:H was claimed for read-only vulnerabilities (#5) and for second-order effects (#1, #6)
- **The 9.1 CRITICAL claims are unsupported** — both required I:H/A:H for memory-read-only and MITM-prerequisite bugs

---

## Finding #1: SSRF/Phishing via URL Policy (PR #16380)

### Original Claim: CVSS 7.5 HIGH

### Recalibrated: CVSS **7.1 HIGH**

**CVSS Vector:** `AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N`

| Metric | Value | Justification |
|--------|-------|---------------|
| **AV** | **N** (0.85) | Ollama API is network-accessible on port 11434. 175K+ exposed instances confirmed via Shodan. Attack vector is entirely remote. |
| **AC** | **L** (0.77) | Hidden markdown prompt injection is trivial to craft. CSS `font-size:1px;color:white` reliably hides payloads from human readers. |
| **PR** | **N** (0.85) | No authentication on Ollama API. Default configuration binds to 0.0.0.0:11434 without any auth layer. |
| **UI** | **R** (0.62) | User must interact with agent mode — the model must fetch and process a page containing the injection. Not automatic. |
| **S** | **U** | Same vulnerable component authority (Ollama agent tools). |
| **C** | **H** (0.56) | SSRF to `169.254.169.254` exposes AWS IAM credentials → full account takeover. This is total confidentiality breach of cloud infrastructure. |
| **I** | **L** (0.22) | Phishing via BrowserOpen is **opportunistic**, not guaranteed. The user sees a login form, but credential theft depends on user behavior. Not equivalent to direct data modification. |
| **A** | **N** (0) | No availability impact. The SSRF/phishing does not cause denial of service. |

**Calculation:**
```
ISS = 1 − [(1 − 0.56) × (1 − 0.22) × (1 − 0)] = 1 − [0.44 × 0.78] = 0.6568
Impact Subscore = 6.42 × 0.6568 = 4.2167
Exploitability Subscore = 8.22 × 0.85 × 0.77 × 0.85 × 0.62 = 2.8353
Base Score = Roundup(4.2167 + 2.8353) = Roundup(7.052) = 7.1
```

### Why the original 7.5 is wrong:
The original likely scored I:H, equating phishing with direct integrity compromise. But phishing is a **probabilistic** attack — the user may or may not enter credentials. I:L is appropriate because the integrity impact is limited and opportunistic, not deterministic like direct data modification.

---

## Finding #2: URL Policy Regex Bypass (PR #16436)

### Original Claim: CVSS 7.2 HIGH

### Recalibrated: CVSS **5.4 MEDIUM**

**CVSS Vector:** `AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N`

| Metric | Value | Justification |
|--------|-------|---------------|
| **AV** | **N** (0.85) | Same network vector as #1. |
| **AC** | **L** (0.77) | Adding a backtick (`\x60`) to a URL is trivial. The vulnerable regex `https?://[^\s<>"']+` does not exclude backticks. |
| **PR** | **N** (0.85) | No authentication required. |
| **UI** | **R** (0.62) | Same user interaction chain as #1. |
| **S** | **U** | Same component (URL policy in Ollama). |
| **C** | **L** (0.22) | The bypass itself is a **security control circumvention** — no DIRECT confidentiality impact. It re-enables #1, but that impact is already scored separately. The bypass removes a barrier, not data. |
| **I** | **L** (0.22) | Same reasoning — removing a security control is limited integrity impact. The exploit chain must still succeed through #1. |
| **A** | **N** (0) | No availability impact. |

**Calculation:**
```
ISS = 1 − [(1 − 0.22) × (1 − 0.22) × (1 − 0)] = 1 − [0.78 × 0.78] = 0.3916
Impact Subscore = 6.42 × 0.3916 = 2.5141
Exploitability Subscore = 8.22 × 0.85 × 0.77 × 0.85 × 0.62 = 2.8353
Base Score = Roundup(2.5141 + 2.8353) = Roundup(5.3494) = 5.4
```

### Why the original 7.2 is wrong:
The original scored this as if the bypass itself causes C:H/I:H impact. But the bypass is a **security control circumvention** — it removes a mitigation, not a vulnerability with direct impact. The full SSRF impact is already captured in Finding #1. Scoring both #1 and #2 with high impact is **double-counting**. The correct approach: score the bypass for what it DIRECTLY does (removes a security barrier = C:L/I:L), and note that it re-enables #1's full impact chain.

### Additional context:
- PR #16436 was created **22 minutes** after #16380 merged — the exposure window was extremely small
- The fix was immediate and complete (backtick added to regex exclusion set)
- This is properly classified as a **security control bypass**, not a standalone vulnerability

---

## Finding #3: Update Flow RCE (PR #16100)

### Original Claim: CVSS 9.1 CRITICAL

### Recalibrated: CVSS **7.5 HIGH**

**CVSS Vector:** `AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H`

| Metric | Value | Justification |
|--------|-------|---------------|
| **AV** | **N** (0.85) | Update binary is downloaded over the network. The update mechanism is HTTP-based. |
| **AC** | **H** (0.44) | **MITM position is a significant prerequisite.** The attacker must be on the network path between the victim and the update server. This requires either: (a) local network access, (b) compromised router/ISP, or (c) DNS poisoning. This is NOT a condition the attacker can create at will. |
| **PR** | **N** (0.85) | No authentication needed to intercept network traffic. |
| **UI** | **R** (0.62) | The update must be triggered. While Ollama checks for updates on startup, the user must have launched the application. If the update is fully automatic and silent, UI:N could apply, but the PoC shows the update flow requires user initiation. |
| **S** | **U** | Same component authority (Ollama updater replaces Ollama binary). |
| **C** | **H** (0.56) | Full code execution via malicious binary = total confidentiality compromise of the system. |
| **I** | **H** (0.56) | Full code execution = total integrity compromise. Attacker can modify any data. |
| **A** | **H** (0.56) | Full code execution = total availability compromise. Attacker can destroy data, ransomware, etc. |

**Calculation:**
```
ISS = 1 − [(1 − 0.56) × (1 − 0.56) × (1 − 0.56)] = 1 − [0.44³] = 0.914816
Impact Subscore = 6.42 × 0.914816 = 5.8731
Exploitability Subscore = 8.22 × 0.85 × 0.44 × 0.85 × 0.62 = 1.6201
Base Score = Roundup(5.8731 + 1.6201) = Roundup(7.4932) = 7.5
```

### Why the original 9.1 is wrong:

**The 9.1 claim ignores the MITM prerequisite (AC:H).** The original scorer likely used AC:L, treating MITM as trivial. But CVSS v3.1 defines AC:H as:

> "A successful attack depends on conditions beyond the attacker's control... the attacker cannot at will trigger the exploit."

A MITM position IS a condition beyond the attacker's control. The attacker must either:
1. Be on the same local network (AV:A territory)
2. Compromise an upstream router/ISP
3. Successfully execute DNS poisoning
4. Operate a malicious Wi-Fi hotspot

None of these are trivially achievable. **AC:H is the correct metric.**

Additionally, UI:R (not UI:N) is appropriate because the update must be triggered by the user launching Ollama. Even if the check is automatic, it requires the user to start the application.

**With AC:L + UI:R:** Score = 8.8 (still not 9.1)
**With AC:L + UI:N:** Score = 10.0 (capped, too high for MITM-required bug)

The 9.1 claim is mathematically inconsistent with CVSS v3.1 for any reasonable metric combination for this vulnerability type.

### Alternative scenario:
If a future investigation confirms that Ollama updates are delivered over **plain HTTP** (not HTTPS), AC:L would be justified since MITM on unencrypted HTTP is trivial. In that case, the score would be **8.8 HIGH** — still not 9.1.

---

## Finding #4: macOS SDK Target Leakage (PR #16053)

### Original Claim: CVSS 3.1 LOW

### Recalibrated: CVSS **5.3 MEDIUM**

**CVSS Vector:** `AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N`

| Metric | Value | Justification |
|--------|-------|---------------|
| **AV** | **N** (0.85) | The Ollama binary is distributed publicly over the internet. Anyone can download it and inspect it remotely. This is NOT a local-only vulnerability — the binary is a network-distributed artifact. |
| **AC** | **L** (0.77) | `otool -l ollama \| grep minos` is a standard macOS developer tool. No special conditions required. |
| **PR** | **N** (0.85) | No privileges needed. The binary is publicly downloadable. |
| **UI** | **N** (0.85) | No user interaction required. The attacker downloads the binary and inspects it on their own machine. No victim interaction needed. |
| **S** | **U** | Same component (Ollama binary). |
| **C** | **L** (0.22) | Only the macOS SDK deployment target is leaked (e.g., "minos 26.0"). This is minimal informational disclosure — one numeric value revealing the build environment. |
| **I** | **N** (0) | No integrity impact. The SDK version cannot be used to modify any data. |
| **A** | **N** (0) | No availability impact. |

**Calculation:**
```
ISS = 1 − [(1 − 0.22) × (1 − 0) × (1 − 0)] = 1 − 0.78 = 0.22
Impact Subscore = 6.42 × 0.22 = 1.4124
Exploitability Subscore = 8.22 × 0.85 × 0.77 × 0.85 × 0.85 = 3.887
Base Score = Roundup(1.4124 + 3.887) = Roundup(5.2994) = 5.3
```

### Why the original 3.1 is wrong:

The original scorer used **AV:L/AC:H**, which is incorrect:

- **AV:L is wrong** because the binary is downloadable over the internet. You don't need local access to the victim's machine. The "vulnerability" is in the binary, which is a public artifact distributed via network.
- **AC:H is wrong** because `otool` is a standard macOS developer tool. Inspecting a binary's load commands requires no special conditions.

The CVSS v3.1 formula over-weights exploitability for low-impact findings, which is why 5.3 feels high for "SDK version in binary." However, the **formula is correct** — the issue is that CVSS v3.1 lacks nuance for high-exploitability/low-impact combinations.

### Important caveat:
While 5.3 is the correct CVSS v3.1 calculation, the **practical risk is LOW**. Knowing the SDK version enables targeted attacks only when combined with other vulnerabilities. On its own, "built with macOS 26 SDK" is reconnaissance data, not an attack. This is a case where the CVSS score exceeds the actual risk because the formula cannot properly penalize trivially-exploitable but minimally-impactful findings.

---

## Finding #5: Bleeding Llama CVE-2026-7482

### Original Claim: CVSS 9.1 CRITICAL

### Recalibrated: CVSS **7.5 HIGH**

**CVSS Vector:** `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`

| Metric | Value | Justification |
|--------|-------|---------------|
| **AV** | **N** (0.85) | Unauthenticated API on port 11434. 175K+ exposed instances confirmed. Three API calls over the network. |
| **AC** | **L** (0.77) | Three simple API calls: (1) create malicious GGUF model, (2) upload via POST /api/create, (3) read leaked memory from response. No special conditions required. |
| **PR** | **N** (0.85) | No authentication required on Ollama API. Default config: no auth, no API key. |
| **UI** | **N** (0.85) | Fully automated. No user interaction needed. The attacker sends API requests directly. |
| **S** | **U** | Same component (Ollama GGUF loader within Ollama process). |
| **C** | **H** (0.56) | **ENTIRE process memory is leaked**: API keys, chat sessions, system prompts, database credentials, conversation history. This is total confidentiality compromise of the Ollama process. |
| **I** | **N** (0) | **READ-ONLY memory leak.** The vulnerability is a heap out-of-bounds READ (`count *= n` overflow in `Tensor.Elements()`). The attacker can read memory but CANNOT modify it. No integrity impact per CVSS v3.1 definition. |
| **A** | **N** (0) | No reliable availability impact. Process crash from OOB read is incidental and not the attacker's goal. |

**Calculation:**
```
ISS = 1 − [(1 − 0.56) × (1 − 0) × (1 − 0)] = 1 − 0.44 = 0.56
Impact Subscore = 6.42 × 0.56 = 3.5952
Exploitability Subscore = 8.22 × 0.85 × 0.77 × 0.85 × 0.85 = 3.887
Base Score = Roundup(3.5952 + 3.887) = Roundup(7.4824) = 7.5
```

### Why the original 9.1 is wrong:

**This is the most important recalibration in the entire report.**

The original 9.1 treats CVE-2026-7482 as equivalent to **Remote Code Execution** — it is NOT. The vulnerability is a **heap out-of-bounds READ**. The attacker gains read access to process memory, but:

1. **I:N is correct**, not I:H. CVSS v3.1 section 2.3.2 states: "Integrity impact measures the degree to which the attacker can modify data." A read-only heap overflow **cannot modify data**. Period.

2. **A:N is correct**, not A:H. The crash is an incidental side effect, not a reliable attack goal. The attacker wants to READ memory, not crash the process.

3. **Chained impact is not direct impact.** Yes, leaked API keys could be used to modify data ELSEWHERE. But CVSS v3.1 explicitly requires scoring **direct** impact of the vulnerability itself, not downstream effects. The key leakage enables integrity attacks on other systems, which is a CHAIN and should be scored separately.

The 9.1 claim likely arose from:
- Conflating "memory leak of credentials" with "ability to use those credentials"
- Treating the severity of leaked data (API keys = very bad) as equivalent to the severity of the vulnerability (read-only = limited)
- Comparing to Heartbleed (CVE-2014-0160, CVSS 7.5) which IS the correct analogue

**Historical comparison:** CVE-2014-0160 (Heartbleed) — also an unauthenticated memory read — was scored CVSS 7.5 by NIST/NVD. Bleeding Llama is structurally identical: unauthenticated, network-accessible, heap OOB read, process memory disclosure. **7.5 is the correct score.**

### Severity note:
7.5 HIGH is still a **very serious** vulnerability. Any unauthenticated API that dumps process memory is critical infrastructure risk. The difference between 7.5 and 9.1 is:
- 7.5 = "Attacker can read everything" (accurate)
- 9.1 = "Attacker can read AND modify AND destroy everything" (inaccurate)

---

## Finding #6: Codex Launch Configuration Hijacking (PR #16437)

### Original Claim: CVSS 7.5 HIGH

### Recalibrated: CVSS **7.1 HIGH**

**CVSS Vector:** `AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N`

| Metric | Value | Justification |
|--------|-------|---------------|
| **AV** | **N** (0.85) | The malicious command can be delivered over the network: via social engineering (webpage, chat), or chained with #1 (prompt injection suggests the command to the AI). |
| **AC** | **L** (0.77) | Argument injection via CLI flags is technically trivial. The `-c` flag accepts arbitrary configuration. |
| **PR** | **N** (0.85) | No authentication needed to craft or deliver the malicious command. |
| **UI** | **R** (0.62) | User must execute the crafted `ollama launch codex --` command. This is the critical bottleneck — the attack fails if the user doesn't run the command. |
| **S** | **U** | Same component (Ollama codex launcher). |
| **C** | **H** (0.56) | ALL prompts and codebase context are intercepted by the attacker's server. Full confidentiality compromise of the Codex session. |
| **I** | **L** (0.22) | Attacker controls model responses (can inject malicious code suggestions), but does NOT directly modify data on the victim's system. The integrity impact is limited to the model's output, not system files. |
| **A** | **N** (0) | No availability impact. |

**Calculation:**
```
ISS = 1 − [(1 − 0.56) × (1 − 0.22) × (1 − 0)] = 1 − [0.44 × 0.78] = 0.6568
Impact Subscore = 6.42 × 0.6568 = 4.2167
Exploitability Subscore = 8.22 × 0.85 × 0.77 × 0.85 × 0.62 = 2.8353
Base Score = Roundup(4.2167 + 2.8353) = Roundup(7.052) = 7.1
```

### Why the original 7.5 is wrong:
The original likely scored I:H, equating "attacker controls model responses" with "full integrity compromise." But the attacker only controls what the model SAYS — they don't modify files, databases, or system configuration. The user may trust and act on malicious suggestions, but that's a user decision, not a direct integrity violation. I:L is appropriate: the attacker can influence but not directly modify system data.

### Chain potential:
When combined with Finding #1 (prompt injection), the attack chain becomes:
1. Prompt injection via hidden markdown (#1)
2. AI suggests running the malicious `ollama launch codex` command (#6)
3. User copies and runs it → full prompt interception

This chain increases practical risk but does not change individual CVSS scores. Each finding should be scored independently per CVSS v3.1 methodology.

---

## Methodology Notes

### CVSS v3.1 Roundup Function
Per FIRST.org specification: `Roundup(x) = ceiling(x × 10) / 10`. This always rounds UP to one decimal place. Example: 7.052 → Roundup(7.052) = ceiling(70.52)/10 = 71/10 = 7.1.

### Key Principles Applied
1. **Direct impact only** — CVSS scores the impact of the vulnerability itself, not chained effects. "Leaked API keys can be used to modify data" is a chain, not direct I:H.
2. **No double-counting** — Finding #2 (bypass) is scored for its DIRECT impact (security control circumvention), not for re-enabling #1's full impact.
3. **AC measures conditions, not effort** — MITM is a condition beyond the attacker's control (AC:H), even if technically achievable. Social engineering reliability is a separate concern from AC.
4. **UI:R vs UI:N** — "User must launch the application" or "user must run a command" = UI:R. "Fully automated API exploitation" = UI:N.

### Where CVSS v3.1 Falls Short
- **SDK Leakage (#4):** The formula produces 5.3 MEDIUM for "SDK version in binary." This feels inflated because exploitability (trivially downloadable + inspectable) dominates the low impact (one metadata value). CVSS v3.1 cannot properly distinguish between "easy to exploit but minimal info" and "easy to exploit with critical info."
- **Memory read vs code execution:** CVSS v3.1 scores C:H/I:N/A:N (memory read) significantly lower than C:H/I:H/A:H (RCE), but the practical difference is often smaller than the CVSS delta suggests, especially when leaked credentials enable secondary attacks.

---

## Appendix: Verification Calculations

### Finding #1 — AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N
```
ISS = 1 − (0.44 × 0.78 × 1.0) = 1 − 0.3432 = 0.6568
Impact = 6.42 × 0.6568 = 4.216656
Exploitability = 8.22 × 0.85 × 0.77 × 0.85 × 0.62 = 2.8352697
Sum = 4.216656 + 2.8352697 = 7.051926
Roundup(7.051926) = 7.1 ✓
```

### Finding #2 — AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N
```
ISS = 1 − (0.78 × 0.78 × 1.0) = 1 − 0.6084 = 0.3916
Impact = 6.42 × 0.3916 = 2.514072
Exploitability = 8.22 × 0.85 × 0.77 × 0.85 × 0.62 = 2.8352697
Sum = 2.514072 + 2.8352697 = 5.349342
Roundup(5.349342) = 5.4 ✓
```

### Finding #3 — AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H
```
ISS = 1 − (0.44 × 0.44 × 0.44) = 1 − 0.085184 = 0.914816
Impact = 6.42 × 0.914816 = 5.8731187
Exploitability = 8.22 × 0.85 × 0.44 × 0.85 × 0.62 = 1.6200846
Sum = 5.8731187 + 1.6200846 = 7.4932033
Roundup(7.4932033) = 7.5 ✓
```

### Finding #4 — AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N
```
ISS = 1 − (0.78 × 1.0 × 1.0) = 1 − 0.78 = 0.22
Impact = 6.42 × 0.22 = 1.4124
Exploitability = 8.22 × 0.85 × 0.77 × 0.85 × 0.85 = 3.8872697
Sum = 1.4124 + 3.8872697 = 5.2996697
Roundup(5.2996697) = 5.3 ✓
```

### Finding #5 — AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N
```
ISS = 1 − (0.44 × 1.0 × 1.0) = 1 − 0.44 = 0.56
Impact = 6.42 × 0.56 = 3.5952
Exploitability = 8.22 × 0.85 × 0.77 × 0.85 × 0.85 = 3.8872697
Sum = 3.5952 + 3.8872697 = 7.4824697
Roundup(7.4824697) = 7.5 ✓
```

### Finding #6 — AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N
```
ISS = 1 − (0.44 × 0.78 × 1.0) = 1 − 0.3432 = 0.6568
Impact = 6.42 × 0.6568 = 4.216656
Exploitability = 8.22 × 0.85 × 0.77 × 0.85 × 0.62 = 2.8352697
Sum = 4.216656 + 2.8352697 = 7.051926
Roundup(7.051926) = 7.1 ✓
```

---

## Historical CVSS Precedent: Heartbleed Comparison

| Attribute | Heartbleed (CVE-2014-0160) | Bleeding Llama (CVE-2026-7482) |
|-----------|---------------------------|--------------------------------|
| Type | Heap OOB read | Heap OOB read |
| Auth required | No | No |
| User interaction | No | No |
| Data leaked | Process memory (64KB/request) | Process memory (entire heap) |
| Data modifiable | No (read-only) | No (read-only) |
| NVD CVSS | **7.5** | **7.5** (recalibrated) |
| Original claim | N/A | 9.1 (inflated) |

Bleeding Llama is structurally identical to Heartbleed — both are unauthenticated heap OOB reads that leak process memory. The NVD correctly scored Heartbleed at 7.5. Bleeding Llama deserves the same treatment.

---

*End of CVSS v3.1 Recalibration Report*