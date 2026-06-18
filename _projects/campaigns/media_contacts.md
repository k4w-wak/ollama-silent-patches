# 🎯 KAMPAGNE — Medie- & Forskerkontakter
> Genereret af grok-recon | Dato: 2026-06-07

---

## 1. 🔬 PromptArmor — AI Prompt Injection Forskere

### Kai Greshake
- **Rolle:** Co-founder & Chief Scientist, PromptArmor; Security Researcher (NVIDIA)
- **Twitter/X:** [@KGreshake](https://x.com/KGreshake)
- **LinkedIn:** [linkedin.com/in/kai-greshake-8536b8232](https://de.linkedin.com/in/kai-greshake-8536b8232)
- **Website:** [kai-greshake.de](https://kai-greshake.de)
- **NVIDIA Blog:** [developer.nvidia.com/blog/author/kgreshake](https://developer.nvidia.com/blog/author/kgreshake/)
- **Arbejdsgiver:** NVIDIA (AI Security) + PromptArmor
- **Nøgle-artikler:**
  - "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection" (arXiv 2302.12173)
  - Writer.com data exfiltration via indirect prompt injection (Dec 2023)
  - Slack AI data exfiltration disclosure
  - Microsoft 365 Copilot Cowork indirect prompt injection
  - Discord OpenClaw prompt injection disclosure (Apr 2026)
- **Kontakt-strategi:** Signal eller email via NVIDIA. Substack-kommentar på promptarmor.substack.com

### PromptArmor (Organisation)
- **Website:** [promptarmor.com](https://www.promptarmor.com)
- **Substack:** [promptarmor.substack.com](https://promptarmor.substack.com) — "Researching and sharing LLM security vulnerabilities"
- **LinkedIn:** [linkedin.com/company/promptarmor](https://www.linkedin.com/company/promptarmor) — 1,502 followers
- **Careers email:** careers@promptarmor.com
- **Nøgle-disclosures:** Writer.com, Slack AI, Microsoft 365 Copilot, Snowflake Cortex CLI, OpenClaw/Discord
- **Relevans:** De er THE go-to for AI prompt injection disclosure. De har track record med responsible disclosure.

---

## 2. 🛡️ Striga.ai — AI Source Code Auditing & CVE Research

### Bartłomiej Dmitruk
- **Rolle:** Co-founder, Striga.ai
- **LinkedIn:** [pl.linkedin.com/in/bartlomiej-dmitruk](https://pl.linkedin.com/in/bartlomiej-dmitruk)
- **Nøgle-CVEs (co-credited):**
  - CVE-2026-23918 — Apache httpd HTTP/2 double-free → pre-auth RCE (CVSS 8.8)
  - CVE-2026-42248 — Ollama Windows auto-updater missing signature verification
  - CVE-2026-42249 — Ollama Windows updater path traversal → persistent RCE (CVSS 7.7)
- **Relevans:** Direkte co-credit på Ollama CVEs med CERT Polska. Key disclosure partner.

### Striga.ai (Organisation)
- **Website:** [striga.ai](https://www.striga.ai)
- **Twitter/X:** [@striga_ai](https://x.com/striga_ai)
- **GitHub:** [github.com/striga-ai](https://github.com/striga-ai)
- **LinkedIn:** [linkedin.com/company/striga-ai](https://www.linkedin.com/company/striga-ai) — 79 followers
- **Bugflation:** [bugflation.com/systems/striga-ai](https://bugflation.com/systems/striga-ai/) — CVE credits i Apache httpd, Tomcat, Ollama, axios, Mattermost Desktop
- **Nøgle-research:** [striga.ai/research/ollama-windows-auto-update-rce](https://www.striga.ai/research/ollama-windows-auto-update-rce)
- **Relevans:** AI-baseret source code auditing. Har direkte Ollama CVE credits. CERT Polska samarbejde.

---

## 3. 🇵🇱 CERT Polska

### Kontakt-info
- **Email (general):** info@cert.pl
- **Email (incident):** cert@cert.pl
- **Incident portal:** incydent.cert.pl
- **Adresse:** Kolska 12, 01-045 Warsaw, Poland
- **Telefon:** +48-22-380274
- **Website:** [cert.pl](https://cert.pl/en/)
- **CVD Policy:** [cert.pl/en/cvd](https://cert.pl/en/cvd/)
- **ePUAP:** /NASK
- **Nøgle-CVEs (coordinated):**
  - CVE-2026-42248 — Ollama Windows auto-updater (med Striga)
  - CVE-2026-42249 — Ollama Windows updater path traversal (med Striga)
  - CVE-2026-34906, CVE-2026-34907 — Wirtualna Uczelnia software
- **Relevans:** Koordinerede Ollama Windows RCE disclosure med Striga. Key European CERT for responsible disclosure.

---

## 4. 🛡️ Cyera Research — "Bleeding Llama" Forskere

### Cyera (Organisation)
- **Website:** [cyera.com](https://www.cyera.com)
- **Research page:** [cyera.com/research/bleeding-llama](https://www.cyera.com/research/bleeding-llama-critical-unauthenticated-memory-leak-in-ollama)
- **Nøgle-CVE:** CVE-2026-7482 — "Bleeding Llama" — Ollama heap out-of-bounds read i GGUF tensor parsing (CVSS 9.1)
- **Impact:** ~300,000 exposed Ollama servers kan lække hela process memory (prompts, API keys, environment vars, tool output)
- **Relevans:** De fandt den mest kritiske Ollama CVE i 2026. Har skrevet detailed research write-up.

---

## 5. 📰 Journalister — AI Sikkerhed & Vulnerability Coverage

### Brian Krebs
- **Outlet:** KrebsOnSecurity (independent)
- **Twitter/X:** [@briankrebs](https://twitter.com/briankrebs)
- **Website:** [krebsonsecurity.com](https://krebsonsecurity.com)
- **Signal:** DanArs.82 (oplyst på Bluesky profil)
- **Email:** tips@krebsonsecurity.com (general tips)
- **Nøgle-dækning:** Cybercrime, data breaches, zero-days, AI security (skrev "How AI Assistants are Moving the Security Goalposts" — Mar 2026)
- **Kontakt-strategi:** Signal er bedst. Har skrevet om AI security målrettet.

### Dan Goodin
- **Outlet:** Ars Technica — Senior Security Editor
- **Twitter/X:** [@dangoodin001](https://twitter.com/dangoodin001)
- **Bluesky:** [@dangoodin.bsky.social](https://bsky.app/profile/dangoodin.bsky.social) — Signal: DanArs.82
- **LinkedIn:** [linkedin.com/in/dangoodin](https://www.linkedin.com/in/dangoodin)
- **Nøgle-dækning:** Malware, espionage, zero-days, hardware hacking, encryption, passwords. Skriver regelmæssigt om kritiske CVEs.
- **Kontakt-strategi:** Signal oplyst på Bluesky profil. Dækker CVE disclosures detaljeret.

### Lily Hay Newman
- **Outlet:** WIRED — Senior Writer (Information Security, Digital Privacy, Hacking)
- **Twitter/X:** [@lilyhnewman](https://x.com/lilyhnewman)
- **Email:** lily.newman@wired.com / lilyhnewman@gmail.com
- **Muck Rack:** [muckrack.com/lily-newman](https://muckrack.com/lily-newman)
- **Nøgle-dækning:** Infosec, digital privacy, hacking. WIRED's primære sikkerheds-skribent.
- **Kontakt-strategi:** Email eller DM på Twitter. WIRED har dedikeret security track.

### Sergiu Gatlan
- **Outlet:** BleepingComputer — News Reporter
- **Twitter/X:** [@sergiugatlan](https://twitter.com/sergiugatlan) *(verify)*
- **Email:** tips@bleepingcomputer.com (general)
- **Contact page:** [bleepingcomputer.com/contact](https://www.bleepingcomputer.com/contact/)
- **Nøgle-dækning:** Over et årti med cybersecurity nyheder. Keen eye for emerging threats og tech.
- **Kontakt-strategi:** BleepingComputer er hurtige til at dække nye CVEs. Email til tips@ er bedste.

### Lawrence Abrams
- **Outlet:** BleepingComputer — Founder & Owner
- **Email:** lawrence@bleepingcomputer.com *(likely)*
- **Relevans:** Grundlægger af BleepingComputer (est. 2004). Oftest malware/ransomware fokus men dækker også critical vulns.

### Kylie Robison
- **Outlet:** The Verge — Senior AI Reporter
- **Twitter/X:** [@kylieerobison](https://twitter.com/kylieerobison) *(verify)*
- **Nøgle-dækning:** AI technology, OpenAI, Anthropic, Meta AI. Ledende AI coverage på The Verge.
- **Relevans:** Dækker AI industrien bredt. Kan være relevant for AI security stories med industriel impact.

### Hayden Field
- **Outlet:** The Verge — Senior AI Reporter
- **Nøgle-dækning:** AI companies inkl. Anthropic ($183B valuation), OpenAI, AI safety policy.
- **Relevans:** Dækker AI safety policy og industri. Komplementerer Kylie's tech coverage.

---

## 6. 🔥 Nylige Ollama Vulnerabilities (Reference-oversigt)

| CVE | Severity | Beskrivelse | Finder | Dato |
|-----|----------|-------------|--------|------|
| CVE-2025-63389 | **Critical** | Auth bypass i Ollama API endpoints (≤v0.12.3) | N/A | Dec 2025 |
| CVE-2025-15063 | **Critical** | RCE i Ollama MCP Server (execAsync command injection) | N/A | Jan 2026 |
| CVE-2025-66960 | **High** | Ollama vulnerability (CVSS 7.5) | N/A | Jan 2026 |
| CVE-2026-42248 | **High** | Ollama Windows auto-updater missing signature verification | Striga.ai + CERT Polska | Apr 2026 |
| CVE-2026-42249 | **High** | Ollama Windows updater path traversal → persistent RCE (CVSS 7.7) | Striga.ai + CERT Polska | Apr 2026 |
| CVE-2026-7482 | **Critical** | "Bleeding Llama" — Heap OOB read i GGUF, leaks entire process memory (CVSS 9.1) | Cyera Research | May 2026 |
| CVE-2026-7020 | **Low** | Path traversal i Ollama (≤0.20.2) | N/A | N/A |
| CVE-2026-5757 | **Critical** | Ollama model upload memory leak | N/A | Apr 2026 |

---

## 7. 📋 AI API CORS Vulnerability Referencer

- **60% af alle APIs** har CORS misconfiguration (Medium artikel, 2025)
- **US Dept of Defense** havde CORS vulnerability på HackerOne — origin reflection tillod data theft
- **OWASP CORS Misconfiguration** — Security Misconfiguration #5
- **Gemini API CORS Error** — Google's OpenAI-compatibility layer har documented CORS issues
- **Anthropic "Project Glasswing"** — AI vulnerability scanner (May 2026) — Claude Opus 4.7 powered, 10,000+ flaws found
- **PortSwigger Labs** — CORS vulnerability labs for testing

---

## 8. 🎯 Kontakt-Prioritering

### Tier 1 — Direkte relevant (skriv FØRST)
1. **PromptArmor / Kai Greshake** — AI prompt injection domain experts, responsible disclosure track record
2. **Striga.ai / Bartłomiej Dmitruk** — Har Ollama CVE credits, AI security auditing
3. **CERT Polska** — Koordinerede Ollama Windows RCE disclosure

### Tier 2 — Mediedækning (skriv for story pitch)
4. **Brian Krebs** — Har skrevet om AI security, kæmpe reach, Signal-kontakt
5. **Dan Goodin (Ars Technica)** — Dækker CVEs detaljeret, Signal-tilgængelig
6. **Lily Hay Newman (WIRED)** — Infosec specialist, WIRED har stor impact

### Tier 3 — Bred AI coverage
7. **Sergiu Gatlan (BleepingComputer)** — Hurtig CVE-dækning
8. **Kylie Robison (The Verge)** — AI industriel vinkel
9. **Hayden Field (The Verge)** — AI safety policy vinkel

### Tier 4 — Research reference
10. **Cyera Research** — "Bleeding Llama" CVE-2026-7482, detailed write-up

---

## 9. 📧 Pitch-Skabelon (Forslag)

```
Subject: [Responsible Disclosure] AI Infrastructure Security Vulnerabilities — Pre-Embargo

Hi [Navn],

I'm a security researcher who has been conducting responsible disclosure on AI infrastructure 
vulnerabilities, specifically around [CORS misconfigurations / API exposure / prompt injection] 
in AI deployment platforms.

Given your coverage of [relevant article/reference], I wanted to reach out regarding findings 
that may be of interest:

- [Brief, non-specific description of vulnerability category]
- Impact: [Scale — e.g., number of affected instances, data exposure risk]
- Responsible disclosure timeline: [proposed date]

Would you be interested in receiving embargoed details for potential coverage?

Best regards,
[Name]
Signal: [number]
```

---

*Slut på media_contacts.md — opdateret 2026-06-07 af grok-recon*