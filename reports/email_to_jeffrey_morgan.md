Subject: Ollama Desktop Security — 3 Silently Patched Vulnerabilities & Disclosure Process

Jeffrey,

I'm writing to you directly because you're the only person at Ollama I believe will take this seriously.

My name is admin_user. I'm a security researcher who has been in contact with your security team through security@ollama.com since May 18, 2026. The experience has been, to be frank, deeply disappointing — and I believe it does not reflect the values of the company you built.

Here's the situation in brief:

---

THE FACTS

1. On May 18, 2026, I reported a critical vulnerability to security@ollama.com: unauthenticated model injection from arbitrary registries and GGUF memory safety issues. Bruce MacDonald responded on May 20 asking for a PoC for the GGUF OOB read. I provided it.

2. On June 1, 2026, I reported a second issue: a CORS attack chain via MiniMax's API that enables PII theft from Ollama Cloud users (name, email, Stripe Customer ID, subscription data). Michael Chiang responded the same day dismissing it as "not technically viable" and stated: "we haven't entered into any disclosure agreement or timeline."

3. On June 3, 2026 — two days after Michael dismissed my report — Ollama released v0.30.2, which included PRs #16380 and #16436 by @dhiltgen that silently patched three vulnerabilities I had identified:

   - SSRF via Browser Tool (BrowserOpen) — CWE-918
     A malicious model could emit tool-call arguments containing URLs pointing to internal network resources (cloud metadata endpoints, localhost services). The fix introduced url_policy.go with an allowlist mechanism.

   - Data Exfiltration via Markdown Image Tags — CWE-200
     The React UI rendered markdown image tags from LLM responses without sanitization, allowing outbound HTTP requests to attacker-controlled servers carrying conversation context and system information. The fix removed rehype-raw and replaced <img> with a text-only fallback.

   - Tool Argument Manipulation / URL Policy Bypass — CWE-20
     The initial SSRF fix used strings.TrimRight to clean URLs before matching. A model could bypass this by appending suffix characters to user-provided URLs (e.g., https://example.com/page.attacker.com). The subsequent fix (PR #16436) replaced TrimRight with proper URL parsing and exact-match validation.

4. No security advisory was published. No CVE was assigned by Ollama. No credit was given. The release notes for v0.30.2 mention "Harden app markdown URL handling" — a description so vague it could refer to a cosmetic change.

---

THE PROBLEM

Your team received a vulnerability report, dismissed it, and then silently patched the exact same class of vulnerabilities within 48 hours — without disclosure, without advisories, and without credit.

This is not responsible disclosure. This is silent patching, and it creates three serious problems:

- **Users remain uninformed.** Anyone running pre-v0.30.2 Ollama Desktop still has these vulnerabilities. They don't know they need to update, and they don't know what they're vulnerable to.

- **The security community is disincentivized.** Researchers who invest time finding and reporting vulnerabilities expect basic acknowledgement. When their findings are silently patched without credit, they stop reporting — and start publishing zero-days instead.

- **It contradicts Ollama's own security policy.** Your SECURITY.md says: "We ask that you give us sufficient time to investigate and address the vulnerability before disclosing it publicly." I honored that. Your team did not honor the reciprocal obligation: to disclose the fix once it's deployed.

---

THE CVE REQUEST

On June 3, 2026, I submitted a CVE ID request to MITRE (MCID15789529) for all three vulnerabilities. Since Ollama does not have a CNA covering desktop application vulnerabilities, I requested CVEs directly from MITRE. This was a last resort — I would have preferred Ollama to assign these through GitHub Security Advisories.

---

WHAT I'M ASKING

1. **Acknowledge the vulnerabilities.** Issue a security advisory for the three silently patched issues in v0.30.2. The community deserves to know.

2. **Establish a proper vulnerability disclosure process.** Your current process — a Google Group that dismisses reports and patches silently — is not working. Consider joining a CNA, publishing an SLA for security responses, and committing to disclosure timelines.

3. **Credit researchers.** When you patch a vulnerability that was reported to you, credit the reporter. This costs nothing and incentivizes future responsible disclosure.

I'm not asking for a bug bounty. I'm asking for what every security researcher asks for: transparency, credit, and a process that works.

I'm happy to discuss this further. I believe Ollama is an important project and that this can be resolved constructively.

Best regards,
admin_user
Security Researcher
admin_user@proton.me

---

References:
- PR #16380: https://github.com/ollama/ollama/pull/16380
- PR #16436: https://github.com/ollama/ollama/pull/16436
- v0.30.2 release: https://github.com/ollama/ollama/releases/tag/v0.30.2
- CVE Request: MCID15789529
- Ollama SECURITY.md: https://github.com/ollama/ollama/blob/main/SECURITY.md
