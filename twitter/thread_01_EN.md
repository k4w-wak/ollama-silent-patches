🧵 THREAD: How Ollama (173K⭐) silently patches security vulnerabilities without CVEs, advisories, or researcher credits — a thread.

1/20

I found 9 vulnerabilities in @OllamaAI. 5 were silently patched. 3 remain unpatched. 0 CVEs issued. 0 advisories published. 0 researchers credited.

Here's what happened. 👇

2/20

First, some context: Ollama is the most popular local LLM runtime. 173K+ GitHub stars. 25K-175K publicly exposed instances. Used by millions.

And they have a systemic problem with security transparency.

3/20

🔴 FINDING 1: CVE-2026-5757 — GGUF Memory Leak (UNPATCHED, CVSS 5.3-9.8 depending on scoring methodology)

3 unauthenticated API calls can leak the ENTIRE process memory:
- System prompts
- Chat sessions
- API keys
- Database credentials

Still unfixed in v0.30.6. CERT Polska: "Unable to reach vendor."

4/20

The vulnerable code:
```go
func (t Tensor) Elements() uint64 {
    var count uint64 = 1
    for _, n := range t.Shape {
        count *= n  // ← uint64 overflow, NO validation
    }
    return count
}
```

No bounds checking. On any Ollama instance.

5/20

🔴 FINDING 2: CVE-2026-42248/42249 — Update RCE (CVSS 9.1)

Path traversal + missing Windows signature verification = MITM RCE.

An attacker on your network can replace the Ollama update with malware. Silently patched in PR #16100 as "app: harden update flows."

6/20

🟠 FINDING 3: SSRF/Phishing Overlay (CVSS 7.5)

Ollama renders markdown URLs as clickable links. An attacker can overlay phishing pages inside the Ollama UI. Silently patched in PR #16380 as "fix markdown rendering."

7/20

🟠 FINDING 4: URL Policy Regex Bypass (CVSS 7.2)

Ollama's URL allowlist regex can be bypassed with crafted URLs. Silently patched in PR #16436. No CVE.

8/20

🟠 FINDING 5: Codex Config Hijacking (CVSS 7.5)

Ollama's Codex integration can be hijacked to exfiltrate user data. Semi-silently patched in PR #16437.

9/20

🔴 FINDING 7: CVE-2026-7482 "Bleeding Llama" (CVSS 9.1)

300,000+ servers vulnerable to model poisoning attacks via malicious GGUF files. Discovered by @CyeraResearch. Silently patched without CVE or advisory.

10/20

And then there's the pattern:

🚨 THE PATTERN: Reject → Patch → Silence

5 independent researchers reported vulnerabilities to Ollama. Here's what happened:

11/20

Researcher 1: py0zz1 (Issue #14666) → Vulnerability forwarded to Jeffrey Morgan → PR #13164 patches it → 4 months later, still no CVE

Researcher 2: Bartłomiej Dmitruk/Striga → CVE-2026-42248/42249 → "Not technically viable" (rejected by co-founder Michael Chiang) → then silently patched

12/20

Researcher 3: Reported SSRF → "Works as intended" → then silently patched in PR #16380

Researcher 4: Reported regex bypass → Ignored → then silently patched in PR #16436

Researcher 5: BruceMacD collects PoCs, approves patches with "Thanks for fixing!" but no CVEs issued

13/20

Who writes ALL the security patches? Daniel Hiltgen (@dhiltgen). 879+ commits. 15 security patches. ALL disguised as feature work with titles like "harden update flows" and "fix data race."

Not the CEO. Not a security team. One engineer. In secret.

14/20

But wait — there's more. 15+ additional unpatched GGUF parser vulnerabilities found in line-by-line audit:

- Unbounded memory allocation
- Integer overflows in quantize
- Missing validation in safetensors conversion
- Race conditions in scheduler

All unpatched. All silently "fixed" in unrelated PRs.

15/20

Why does this matter?

25K-175K Ollama instances are publicly exposed. Every one of them is vulnerable to CVE-2026-5757 RIGHT NOW. And the vendor can't be reached by CERT Polska.

16/20

Plus: 6 AI API platforms have CRITICAL CORS vulnerabilities that let any website steal your API keys in real-time:

- DeepInfra (CVSS 8.6)
- DeepSeek (CVSS 9.1)
- Hyperbolic (CVSS 8.6)
- Baichuan (CVSS 8.6)
- MiniMax (CVSS 9.1, all 3 endpoints)
- LangSmith (CVSS 9.8)

17/20

The CORS attack is simple: you visit a website, JavaScript runs fetch() with credentials: 'include', the API reflects your Origin + allows credentials, and the attacker reads your prompts and API keys in real-time.

No "zero data retention" claim protects against real-time interception.

18/20

Full disclosure package with PoC scripts, evidence, and coordinated disclosure timeline:

Full disclosure blog post with all evidence:
[Medium Article]

Media contacts: Brian Krebs, Ars Technica, WIRED, BleepingComputer notified.

19/20

If you're running Ollama:
1. Update to latest version IMMEDIATELY
2. Don't expose port 11434 to the internet
3. Use authentication middleware
4. Audit your GGUF files
5. Check if your AI API keys are in environment variables

20/20

This disclosure follows a 90-day responsible disclosure timeline. All vendors were contacted. Ollama was contacted via CERT Polska. They couldn't reach the vendor.

#AIsecurity #Ollama #CVE #responsibleDisclosure #infosec