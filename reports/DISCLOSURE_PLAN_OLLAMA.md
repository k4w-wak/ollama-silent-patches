# OLLAMA DISCLOSURE PLAN — admin_user

## TIDSLINJE
- **06:00 (i morgen)**: 24-timers timer starter
- **06:00 + 24h**: Deadline for Jeffrey Morgan svar

## FASE 1 — RECON (06:00 → 06:00+næste dag)
- admin_user bruger nye teknikker non-stop
- Fuld research på ALT omkring Ollama
- Bygger samlet dossier
- **INTET angreb — kun recon**

## FASE 2 — PUBLIC DISCLOSURE (hvis intet svar efter 24 timer)
- Kontakt blogs / X-profiler / Medium-forfattere
- HELE historien: silent patching, ignorerede reports, ingen advisory, ingen credit
- Få dem til at publicere
- admin_user starter egen Twitter/blog
- Tagging: navn + admin_user@proton.me + profil

## BAGGRUND
- ✅ Email sendt direkte til jmorganca@gmail.com (Jeffrey Morgan, Ollama founder)
- ❌ Tidligere email gik kun til hello@ollama.com — aldrig nået frem
- ❌ security@ollama.com ignoreret siden 18. maj 2026
- ⚠️ v0.30.2 silently patched 3 vulns uden advisory
- 📋 CVE-anmodning til MITRE: MCID15789529

## DE 3 VULNS
1. SSRF via BrowserOpen — CWE-918
2. Data Exfiltration via Markdown Image Tags — CWE-200
3. URL Policy Bypass via TrimRight — CWE-20

## KRONOLOGI
- 18. maj: Rapport til security@ollama.com
- 20. maj: Bruce MacDonald beder om PoC → leveret
- 1. juni: CORS rapport → Michael Chiang afviser ("not technically viable")
- 3. juni: v0.30.2 udgives — silently patches de 3 vulns
- 6. juni: Email direkte til jmorganca@gmail.com
- 6. juni + 24h: Deadline

---
*Oprettet af Grok — admin_user's plan dokumenteret*