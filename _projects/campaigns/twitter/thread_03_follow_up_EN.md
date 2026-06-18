🧵 FOLLOW-UP THREAD: 7 days after disclosing 9 vulnerabilities in @OllamaAI — here's what happened.

(Spoiler: They released another silent patch.)

1/12

One week ago I published: "Ollama's Silent Patching Problem: 9 Vulnerabilities, Zero CVEs, Zero Advisories."

Since then, I've found a 10th silent patch. Let me explain.

2/12

On June 7 — ONE DAY before my disclosure — Ollama released v0.30.7.

Release notes: "OpenAI-compatible API models list now aligns with available model tags."

Sounds like a feature. It's not.

3/12

PR #16556 by @ParthSareen fixes an INFORMATION DISCLOSURE vulnerability in /v1/models.

BEFORE: The endpoint leaked internal model namespaces via the `Name` field (e.g., "legacy-name:latest")

AFTER: It uses the canonical public `Model` field ("namespace/exposed-model:latest")

No CVE. No advisory. No credit.

4/12

The test file confirms this was a security fix:

```go
Name: "legacy-name:latest",
Model: "namespace/exposed-model:latest",
// Test asserts Id uses Model, not Name
```

This is internal namespace leakage. On exposed instances, attackers could discover private model identifiers and organizational structure.

Silent patch #10.

5/12

Updated scorecard:

- 10 silent security patches
- 0 CVEs issued by Ollama
- 0 security advisories
- 0 researcher credits
- 3 vulnerabilities STILL UNPATCHED (including CVE-2026-5757)
- 5 researchers ignored or rejected

6/12

But wait — v0.30.6 added NEW attack surface. The OMP (Oh My Pi) integration has 4 new security issues:

1. `auth: "none"` hardcoded → full unauth access if exposed
2. PI_CONFIG_DIR path traversal → arbitrary file write
3. Auto-install NPM plugin without user confirmation
4. Cross-agent config injection (OMP/Pi share config dir)

7/12

And then there's the CORS rejection.

Ollama's security team rejected our CORS finding with: "Credentialed CORS only exposes cookies, not bearer tokens."

This is technically incomplete. JavaScript can ALWAYS read response bodies on CORS-allowed requests. You don't need to read headers to exfiltrate AI outputs.

8/12

The CORS attack is 3 lines:

```javascript
fetch('http://victim-ollama:11434/api/chat', {
  method: 'POST',
  body: JSON.stringify({model: 'llama3', messages: [{role: 'user', content: 'read my emails'}]})
}).then(r => r.json())
```

Any website can read the response. No headers needed. The vulnerability is in the response body, not the request headers.

9/12

Ollama's rejection playbook is now documented:

1. Receive report
2. Request PoC
3. Reject vulnerability ("not technically viable" / "works as intended")
4. Silently patch the exact vulnerability
5. No CVE, no advisory, no credit

This has happened to 5 independent researchers. It's not a bug — it's a policy.

10/12

The math:

- 10 silent patches
- 0 CVEs by Ollama
- 3 unpatched (including heap memory leak)
- 4 new OMP attack surface findings
- CERT Polska: "Unable to reach vendor"

Ollama's SECURITY.md says "takes security seriously."

10 silent patches with zero transparency say otherwise.

11/12

What needs to change:
1. Issue CVEs for security patches (retroactively)
2. Publish security advisories
3. Credit researchers by name
4. Respond to CERT Polska
5. Add authentication (25K+ instances exposed)
6. Create a security mailing list
7. Stop rejecting valid reports then silently patching them

12/12

Full follow-up article with code evidence:
https://medium.com/@admin_user_21591/7-days-later-ollamas-response-to-our-disclosure-was-more-silent-patches-...

Original disclosure:
https://medium.com/@admin_user_21591/ollamas-silent-patching-problem-9-vulnerabilities-zero-cves-zero-advisories-81edf830f9ab

#AIsecurity #Ollama #CVE #responsibleDisclosure #infosec #silentPatching