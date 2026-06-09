# 🔴 FINAL AUDIT — DYBDEGÅENDE GENNEMGANG AF HELE DISCLOSURE PAKKEN

**Auditor:** Grok ( autonomous deep audit)  
**Dato:** 2026-06-08  
**Scope:** `ollama_disclosure_2026/` + `KAMPAGNE/`  
**Metode:** Line-by-line verification mod GitHub API, NVD, MITRE, CERT Polska, og interne krydstjek

---

## 📊 AUDIT SUMMARY

| Kategori | Fundne fejl | Kritiske | Alvorlige | Mindre |
|-----------|------------|----------|-----------|--------|
| **CVE/Version fejl** | 8 | 4 | 3 | 1 |
| **CVSS beregningsfejl** | 5 | 2 | 2 | 1 |
| **Faktiske unøjagtigheder** | 7 | 3 | 2 | 2 |
| **Strukturelle inkonsistenser** | 6 | 1 | 3 | 2 |
| **OPSEC lækager** | 4 | 2 | 1 | 1 |
| **Uverificerede påstande** | 5 | 1 | 2 | 2 |
| **TOTAL** | **35** | **13** | **13** | **9** |

---

## 🔴 KRITISKE FEJL (skal rettes før publicering)

### FEJL 1: CVE-2026-5757 EKSKISTERER IKKE i MITRE/NVD ⛔

**Hvad disclosure siger:** "CVE-2026-5757 — GGUF Memory Leak" med CVSS 5.3 (Sonatype v4.0) / 9.0+ (v3.1 est.)  
**Realitet:** MITRE returnederer `CVE_RECORD_DNE` — CVE-2026-5757 **findes ikke** i MITRE CVE databasen. NVD har 0 resultater.  
**Kun tilgængelig hos:** Sonatype (CVSS 5.3 v4.0), CERT Polska VU#518910, Tenable, Ciphers Security  
**Impact:** En CVE der ikke eksisterer i MITRE/NVD vil få bug bounty reviewers til at N/A submissionen  
**Rettes til:** "Pending CVE: CVE-2026-5757 (assigned by Sonatype, not yet in NVD)" med link til Sonatype advisory

### FEJL 2: CVE-2026-42248/9 Version Range er Forkert ⛔

**Hvad disclosure siger:** "Affected: Ollama v0.17.1 through v0.30.0" / "v0.17.1 through v0.30.6"  
**Realitet:** CERT Polska siger: "Versions from 0.12.10 to 0.17.5 were tested and confirmed as vulnerable, other versions were not tested but might also be vulnerable."  
**CVE record:** `affected: ≤ 0.17.5`  
**Impact:** Vores affected range starter ved v0.17.1, men CVE siger v0.12.10. Og vores range siger "through v0.30.0/v0.30.6", men CERT Polska testede kun op til v0.17.5.  
**Kompleksitet:** PR #16100 (den påståede fix) blev merged 2026-05-11, langt efter v0.17.5 (2026-03-02). Dette betyder at enten: (a) CVE version range er ufuldstændig, eller (b) PR #16100 fixer en anden sårbarhed end CVE-2026-42248/9, eller (c) sårbarheden fandtes i v0.17.5+ men blev ikke testet af CERT Polska.  
**Rettes til:** "Affected: v0.12.10 through at least v0.17.5 (CERT Polska tested range). Later versions may also be vulnerable. PR #16100 (v0.30.0) adds additional hardening."

### FEJL 3: v0.28.0 EKSKISTERER IKKE ⛔

**Hvad CORRIGENDUM siger:** "PR #14406 ... in v0.28.0+"  
**Realitet:** v0.28.0 findes ikke i Ollama's release historik. Den rigtige version er v0.17.2 (PR #14406 merged 2026-02-25, v0.17.2 released 2026-02-26).  
**Impact:** Enhver der tjekker vil finde at v0.28.0 ikke eksisterer, hvilket undergraver troværdigheden  
**Rettes til:** "PR #14406 ... in v0.17.2+"

### FEJL 4: PR #13164 er IKKE en sikkerhedsrettelse ⛔

**Hvad disclosure siger:** "PR #13164 patches py0zz1's reported vulnerability"  
**Realitet:** PR #13164 hedder **"app: open app instead of always navigating to / on connect"** — det er en UI-navigation ændring, ikke en sikkerhedsrettelse. Forfatteren er jmorganca (CEO), ikke en sikkerheds-ingeniør.  
**Impact:** Hvis py0zz1's sårbarhed blev patchet i PR #13164, er det en meget anden type sårbarhed end vi antager. Hvis PR #13164 IKKE er py0zz1's fix, så er py0zz1's faktiske fix ukendt.  
**Rettes til:** "py0zz1 reports vulnerability (Issue #14666), claims patched in PR #13164. PR #13164 is titled 'app: open app instead of always navigating to / on connect' — the connection between this UI fix and a security vulnerability is unclear. The actual vulnerability and its fix have not been identified."

### FEJL 5: Blog og Twitter bruger GAMLE inflated CVSS scores ⛔

**Hvad FINAL_DISCLOSURE_v2 siger:** F1=7.1, F2=7.5, F3=7.1, F4=INFO, F5=5.3/7.5, F6=7.5  
**Hvad blog EN siger:** CVE-2026-5757=9.0+, Update RCE=9.1, SSRF=7.5, Regex=7.2, Codex=7.5, SDK=3.1, Bleeding Llama=9.1  
**Hvad Twitter EN siger:** CVE-2026-5757=9.0+, CVE-2026-42248/9=9.1, SSRF=7.5, Regex=7.2, Codex=7.5, Bleeding Llama=9.1  
**Impact:** Publicering med inflated CVSS scores vil få severity- inflation anklager og N/A fra bug bounty reviewers  
**Rettes til:** Opdater blog og twitter til recalibrerede scores

### FEJL 6: Twitter bruger GAMLE struktur (9 vulns) ikke v2 (6 findings) ⛔

**Hvad FINAL_DISCLOSURE_v2 siger:** "6 primary findings (restructured from 9 — Regex Bypass merged into SSRF; CVE-2026-5757 and CVE-2026-7482 separated and clarified)"  
**Hvad Twitter siger:** "I found 9 vulnerabilities" og lister Finding 1-7 + 6 CORS platforme  
**Impact:** Inkonsistens mellem v2 (6 findings) og offentlige materialer (9 vulns) vil forvirre  
**Rettes til:** Omskriv Twitter til "6 primary findings" eller forklar restruktureringen

### FEJL 7: CVE-2026-7482 Fix Version er korrekt, men datoen er forkert ⛔

**Hvad FINDING_05 siger:** "Fixed in: v0.17.1 (February 25, 2026)"  
**Realitet:** v0.17.1 blev udgivet 2026-02-24T15:00:28Z (ikke Feb 25). PR #14406 (CVE-2026-5757 partial fix) blev merged 2026-02-25T01:52:44Z — EFTER v0.17.1.  
**CVE-2026-7482** siger `affected: < 0.17.1`, hvilket er korrekt — den var fixet i v0.17.1.  
**Men PR #14406** (som CORRIGENDUM siger er en "partial mitigation for CVE-2026-5757") er i v0.17.2, IKKE v0.17.1.  
**Impact:** Konfusion mellem to forskellige CVE's fix-versioner  
**Rettes til:** "CVE-2026-7482 fixed in v0.17.1 (released Feb 24, 2026). PR #14406 (partial CVE-2026-5757 mitigation) merged in v0.17.2 (released Feb 26, 2026). These are separate vulnerabilities with separate fix timelines."

### FEJL 8: Rigtige IP-adresser i PoC scripts og LIVE_SCAN ⛔⛔⛔

**Hvad der er fundet:**
- `poc_evidence/05_Bleeding_Llama/exploit_bleeding_llama.py`: indeholder 58.210.252.154, 101.43.92.199
- `poc_evidence/07_CVE_2026_5757/exploit_cve_2026_5757.py`: indeholder 58.210.252.154, 101.43.92.199
- `poc_evidence/14_Live_Exposed_Instances/exploit_exposed_instances.py`: indeholder 58.210.252.154, 101.43.92.199
- `LIVE_SCAN_RESULTS.md`: indeholder 42 rigtige IP-adresser
- `poc_evidence/01_SSRF_URL_Policy/exploit_ssrf_url_policy.py`: indeholder 169.254.169.254 (AWS metadata — OK som eksempel)

**Impact:** Hvis disse filer offentliggøres, afsløres rigtige sårbar hosts. Dette er en OPSEC-lækage der kan bruges til at angribe de scannede instanser.  
**Rettes til:** Erstat alle rigtige IPs med `192.0.2.x` (documentation range) eller `198.51.100.x`. LIVE_SCAN_RESULTS.md må IKKE offentliggøres — kun aggregerte statistikker.

### FEJL 9: Brugernavnet "researcher" i offentlige dokumenter ⛔

**Hvad der er fundet:**
- `blog/ollama_silent_patches_EN.md`: "By: researcher" (2 forekomster)
- `twitter/thread_01_EN.md`: "github.com/k4w-wak/ollama-disclosure" (1 forekomst)
- `ghsa/advisories.md`: "Discovered by: researcher" (1 forekomst)

**Impact:** OPSEC-reglen siger "USERNAME (researcher) MÅ IKKE VÆRE I OFFENTLIGE FILER"  
**Rettes til:** Brug pseudonym ("an independent security researcher") eller et andet navn. GitHub repo URL kan være `github.com/ollama-disclosure/ollama-disclosure` i stedet.

### FEJL 10: "5 researchers ignored" er misvisende ⛔

**Hvad Twitter siger:** "5 independent researchers reported vulnerabilities to Ollama"  
**Realitet:**
1. PromptArmor — forsker/gruppe ✅
2. Striga (Bartłomiej Dmitruk) — forsker ✅
3. py0zz1 — forsker ✅
4. "Reported SSRF → Works as intended" — **samme som PromptArmor** (Finding 1 og 2 er samme sårbarhed)
5. "Reported regex bypass → Ignored" — **samme som PromptArmor** (Finding 2 er en bypass af Finding 1's fix)
6. BruceMacD — **ikke en forsker**, han er en Ollama-udvikler der godkender patches

**Korrekt tal:** 3 uafhængige forskere (PromptArmor, Striga, py0zz1), hvis vi holder Finding 1+2 sammen. Eller 4 hvis vi regner py0zz1 og "Unknown for CVE-2026-5757" som separate.  
**Rettes til:** "3 independent researchers" eller "4 including the anonymous CVE-2026-5757 reporter"

### FEJL 11: "15+ security patches" claim er delvist uverificeret ⛔

**Hvad disclosure siger:** "15+ security-relevant patches" / "15+ additional unpatched GGUF parser vulnerabilities"  
**Realitet:** 
- 7 code-level vulnerabilities verificeret (OOM bugs i GGUF parser)
- 2 hidden fixes verificeret (commits af31ccef, a7835c67)
- 6 oss-security vulnerabilities **IKKE verificeret** — CORRIGENDUM siger selv: "direct seclists.org content could not be fully verified"  
**Impact:** 6 af 15 påstande mangler kildehenvisning  
**Rettes til:** "9 verified (7 code-level + 2 hidden fixes) + 6 alleged from oss-security mailing list (unverified)"

### FEJL 12: "dhiltgen wrote ALL security patches" er forkert ⛔

**Hvad CORRIGENDUM siger:** "Writes ALL security patches disguised as features (879+ commits, 15 security patches)"  
**Realitet:** PR #16437 (Codex hijack) blev skrevet af **ParthSareen**, ikke dhiltgen. PR #14406 (CVE-2026-5757 partial fix) blev skrevet af **BruceMacD**, ikke dhiltgen. PR #13164 (py0zz1's fix) blev skrevet af **jmorganca** (CEO), ikke dhiltgen.  
**Korrekt:** dhiltgen skrev 4 af 7 security-relevante PRs (57%), ikke "ALL"  
**Rettes til:** "dhiltgen authored 4 of 7 security-relevant PRs, with BruceMacD, ParthSareen, and jmorganca authoring the rest"

### FEJL 13: "Affected: Ollama v0.17.1 through v0.30.6" er misvisende ⛔

**Hvad FINAL_DISCLOSURE siger:** "Affected Software: Ollama v0.17.1 through v0.30.6"  
**Problemet:** v0.17.1 er FIX-versionen for CVE-2026-7482, ikke start på affected range.  
**Korrekt:** Forskellige sårbarheder har forskellige affected ranges:
- CVE-2026-7482: < v0.17.1
- CVE-2026-42248/9: 0.12.10 – 0.17.5 (tested), possibly later versions
- CVE-2026-5757: All versions through v0.30.6
- PR #16380/16436: v0.30.0–v0.30.1
- PR #16100: v0.17.6–v0.29.x (estimated)
  
**Rettes til:** Angiv affected range PER finding, ikke en samlet range

---

## 🟠 ALVORLIGE FEJL (bør rettes, men ikke blokerende)

### FEJL 14: Blog CVSS scores er ikke opdateret til v2

Blog EN bruger gamle inflated scores (9.0+, 9.1, 7.5, 7.2, 3.1). FINAL_DISCLOSURE_v2 bruger recalibrerede scores (7.1, 7.5, 7.1, INFO, 5.3/7.5, 7.5). Blog DA har samme problem.

### FEJL 15: GHSA advisories har inkonsistente CVSS scores

GHSA for Update RCE siger "CVSS 8.0", men recalibrated score er 7.5. GHSA for CVE-2026-5757 siger "CVSS 7.5 for exposed", men v2 siger "5.3 (v4.0) / 7.5 (v3.1, if /api/create open)".

### FEJL 16: Instance counts er inkonsistente på tværs af dokumenter

- FINAL_DISCLOSURE: "25,000–175,000+"
- FINDING_05: "~300,000 (Cyera estimate)"
- LIVE_SCAN: "~56,000 confirmed live"
- Twitter: "25K-175K"
- Disse er forskellige målemetoder, men der er ingen forklaring på forskellene

### FEJL 17: CERT Polska citat er unøjagtigt

**Hvad disclosure siger:** 'CERT Polska: "Unable to reach the vendor"'  
**Hvad CERT Polska faktisk siger:** "Maintainers of this project were notified early about these vulnerabilities, but **didn't respond with the details of vulnerabilities or vulnerable version range**."  
**Forskel:** "Unable to reach" antyder at Ollama ikke kunne kontaktes. "Didn't respond" antyder at Ollama blev kontaktet men valgte ikke at svare detaljeret. Sidstnævnte er stærkere.

### FEJL 18: v0.30.0 og v0.24.0 er parallellle release lines

**Realitet:** v0.23.3 (May 12) → v0.30.0 (May 13) → v0.23.4 (May 13) → v0.24.0 (May 14). v0.30.x er llama.cpp engine line, v0.23.x/v0.24.x er Codex app line.  
**Impact:** Ingen af vores dokumenter forklarer denne versionssprang-anomali. En reviewer kan tro at v0.30.0 erstattede v0.23.x, men de kører parallelt.

### FEJL 19: CVE-2026-7482 "Bleeding Llama" dato er unøjagtig

**Hvad FINDING_05 siger:** "Fixed in: v0.17.1 (February 25, 2026)"  
**Realitet:** v0.17.1 blev udgivet 2026-02-24T15:00:28Z (Feb 24, ikke Feb 25)  
**Rettes til:** "Fixed in: v0.17.1 (February 24, 2026)"

### FEJL 20: "9 vulnerabilities" vs "6 primary findings" inkonsistens

FINAL_DISCLOSURE (original) bruger "9 vulnerabilities". FINAL_DISCLOSURE_v2 bruger "6 primary findings (restructured from 9)". Blog og Twitter bruger stadig "9 vulnerabilities". Twitter lister også "Finding 7" (Bleeding Llama) som nummer 7 i en række af 9, men v2 har den som Finding 6.

### FEJL 21: CVSS v3.1 beregning for F1 (SSRF) kan diskuteres

cvss_recalibrated.md bruger S:U for Finding 1 (SSRF), hvilket giver 7.1. Men begrundelsen siger "SSRF to 169.254.169.254 exposes AWS IAM credentials → full account takeover" — dette er et S:C (Changed Scope) angreb, hvilket ville give 8.2. Valget af S:U er bestridteligt.

### FEJL 22: F5 CVE-2026-7482 CVSS 7.5 kalibrering

cvss_recalibrated.md siger CVSS 7.5 med vektor AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N. Men Cyera tildelte CVSS 9.1 med vektor AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N. Forskellen er AC:H vs AC:L og I:H vs I:L. CVSS v3.1 med AC:L/I:H = 9.1 er Cyera's score, og den er IKKE åbenlys forkert — 3 API-kald uden autentifikation er rimeligt lav complexity. Vores recalibrering bør dokumentere at AC:H er et valg, ikke en kendsgerning.

### FEJL 23: PR #16437 (Codex Hijacking) er "semi-silent" men nævnes i release notes

**Hvad v2 siger:** "Patched v0.30.2 (semi-silent)"  
**Realitet:** v0.30.2 release notes siger: "ollama launch codex now uses an isolated launch configuration, avoiding conflicts with a user's existing Codex settings." — dette er en SIKKERHEDSBESKRIVELSE i release notes, ikke en feature-beskrivelse.  
**Impact:** Klassifikationen "semi-silent" er korrekt, men det bør bemærkes at release notes faktisk nævner ændringen, bare uden at kalde det en sikkerhedsrettelse.

### FEJL 24: Finding 2 (Regex Bypass) er korrekt merged, men CVSS 5.4 er ikke i blog/twitter

FINDING_05 siger Regex Bypass har CVSS 5.4. Blog og Twitter nævner den slet ikke som separat finding (den er merged i v2). Men twitter siger stadig "FINDING 4: URL Policy Regex Bypass (CVSS 7.2)" — det er den GAMLE score.

### FEJL 25: "0 CVEs issued by Ollama" er teknisk korrekt men misvisende

3 CVEs er assignet (CVE-2026-42248, CVE-2026-42249, CVE-2026-7482), men alle af eksterne (CERT Polska, Cyera), ikke af Ollama selv. Påstanden "0 CVEs issued by Ollama" er korrekt, men "0 CVEs" uden kvalifikation er misvisende.

### FEJL 26: py0zz1 Issue #14666 oprettelsesdato er marts 2026, ikke november 2025

**Hvad timeline siger:** "py0zz1 reports vulnerability (Issue #14666) ~Nov 2025"  
**Realitet:** GitHub Issue #14666 blev oprettet 2026-03-06T14:23:08Z  
**Men:** py0zz1's issue siger "I was submit Vulnerability Report 4 months ago via hello@ollama.com" — hvilket betyder den oprindelige rapport var ~november 2025, men den offentlige issue er fra marts 2026.  
**Rettes til:** "py0zz1 privately reports vulnerability ~Nov 2025, opens public follow-up Issue #14666 on Mar 6, 2026"

---

## 🟡 MINDRE FEJL (bør rettes for konsistens)

### FEJL 27: LIVE_SCAN_RESULTS.md må IKKE offentliggøres

Indeholder 42 rigtige IP-adresser på sårbar Ollama-instanser. Skal erstattes af aggregaterede statistikker i offentlige dokumenter.

### FEJL 28: Finding nummerering er inkonsistent

Twitter bruger "FINDING 1-7" (gammel struktur). v2 bruger "Finding 1-6" (restruktureret). CVE-2026-7482 er "Finding 7" i twitter men "Finding 6" i v2.

### FEJL 29: "173,000+ stars" er korrekt (173,486 verificeret)

Men "173K+" er OK at bruge.

### FEJL 30: Deep analysis hævder "Stripe billing data" eksponering, men beviset er svagt

Deep_analysis.md hævder Stripe data eksponering gennem Ollama Cloud, men der er ingen live PoC eller screenshot af faktisk Stripe data. Påstanden er baseret på teoretisk API key eksfiltration.

### FEJL 31: Media contacts mangler verificering

media_contacts.md indeholder kontaktinformation (emails, Twitter handles) der ikke er verificeret. Nogle kan være forældede eller forkerte.

### FEJL 32: Timeline har "PR #13166" referencer der er forkerte

MASTER_TIMELINE.md refererer til "GitHub PR #13166" som "patches py0zz1's reported vulnerability", men PR #13166 er faktisk "deepseek2: upgrade to run v3+ models" — en model-opdatering, ikke en sikkerhedsrettelse.

### FEJL 33: Legal research mangler specifikke love

legal_research.md citerer EU Cyber Resilience Act og dansk straffelov §263, men mangler specifikke henvisninger til paragraffer og retspraksis.

### FEJL 34: KAMPAGNE twitter thread siger "0 CVEs issued" men der ER 3 CVEs

Twitter: "0 CVEs issued. 0 advisories published. 0 researchers credited."  
Korrekt: "0 CVEs issued BY OLLAMA. 3 CVEs assigned by external parties. 0 advisories published by Ollama. 0 researchers credited by Ollama."

### FEJL 35: Forskellige "affected versions" i forskellige dokumenter

- GHSA (CVE-2026-5757): "v0.0.1 through v0.30.6"
- GHSA (Update RCE): "v0.17.1 through v0.30.0"
- FINAL_DISCLOSURE: "v0.17.1 through v0.30.6"
- CERT Polska (CVE-2026-42248/9): "0.12.10 through 0.17.5"
- CVE-2026-7482: "< 0.17.1"

Ingen af disse er konsistente med hinanden.

---

## ✅ BEKRÆFTEDE KORREKTE PÅSTANDE

| Påstand | Verifikation | Kilde |
|---------|-------------|-------|
| PR #16380 exists, authored by dhiltgen, merged Jun 2 | ✅ VERIFIED | GitHub API |
| PR #16436 exists, authored by dhiltgen, merged Jun 2 | ✅ VERIFIED | GitHub API |
| PR #16437 exists, authored by ParthSareen, merged Jun 2 | ✅ VERIFIED | GitHub API |
| PR #16100 exists, authored by dhiltgen, merged May 11 | ✅ VERIFIED | GitHub API |
| PR #16053 exists, authored by dhiltgen, merged May 11 | ✅ VERIFIED | GitHub API |
| PR #14406 exists, authored by BruceMacD, merged Feb 25 | ✅ VERIFIED | GitHub API |
| dhiltgen = Daniel Hiltgen (not Jeffrey Morgan) | ✅ VERIFIED | GitHub API |
| jmorganca = Jeffrey Morgan (CEO) | ✅ VERIFIED | GitHub API |
| CVE-2026-42248 exists in MITRE | ✅ VERIFIED | MITRE API |
| CVE-2026-42249 exists in MITRE | ✅ VERIFIED | MITRE API |
| CVE-2026-7482 exists in MITRE | ✅ VERIFIED | MITRE API |
| CVE-2026-7482 affected < 0.17.1 | ✅ VERIFIED | MITRE CVE record |
| CVE-2026-42248/9 affected ≤ 0.17.5 | ✅ VERIFIED | CERT Polska advisory |
| Ollama has 173,486 stars | ✅ VERIFIED | GitHub API |
| v0.30.2 release notes omit PR #16380, #16436 | ✅ VERIFIED | GitHub API |
| v0.30.0 release notes omit PR #16100, #16053 | ✅ VERIFIED | GitHub API |
| v0.17.2 release notes omit PR #14406 | ✅ VERIFIED | GitHub API |
| Ollama default binds 0.0.0.0:11434 | ✅ VERIFIED | Well-known config |
| 25K-175K exposed instances | ✅ VERIFIED | Multiple sources |

---

## 📋 HANDLINGSPLAN (PRIORITERET)

### 🔴 BLOKERENDE — Skal rettes FØR publicering:

1. **Fjern rigtige IP-adresser** fra alle PoC scripts og LIVE_SCAN_RESULTS (eller hold LIVE_SCAN_RESULTS privat)
2. **Fjern "researcher"** fra alle offentlige dokumenter (blog, twitter, GHSA)
3. **Opdater blog og twitter** med recalibrerede CVSS scores (7.1, 7.5, 7.1, INFO, 5.3/7.5, 7.5)
4. **Opdater twitter** fra "9 vulnerabilities" til "6 primary findings"
5. **Ret "Affected: v0.17.1 through v0.30.6"** til per-finding affected ranges
6. **Tilføj note** om at CVE-2026-5757 ikke er i MITRE/NVD endnu
7. **Ret v0.28.0** til v0.17.2 overalt
8. **Korrekt "5 researchers"** til "3 researchers" eller "4 including anonymous"

### 🟠 VIGTIGT — Bør rettes før publicering:

9. **Ret CVE-2026-42248/9 affected range** til "0.12.10-0.17.5 (tested), possibly later"
10. **Tilføj forklaring** af v0.23.x/v0.24.x vs v0.30.x parallel lines
11. **Ret "15+ vulnerabilities"** til "9 verified + 6 alleged (unverified)"
12. **Ret "dhiltgen wrote ALL security patches"** til "dhiltgen authored 4 of 7"
13. **Opdater CERT Polska citat** fra "unable to reach" til "didn't respond with details"
14. **Dokumenter CVSS S:C vs S:U valg** for Finding 1
15. **Ret v0.17.1 dato** fra "February 25" til "February 24"

### 🟡 ØNSKVÆRT — For fuld konsistens:

16. Standardiser instance counts (brug "56,000+ confirmed" med kildehenvisninger)
17. Tilføj PR #13164 disclaimer (UI fix, ikke tydeligt security)
18. Opdater GHSA advisories med recalibrerede CVSS
19. Tilføj note om at PR #16437 (Codex) faktisk nævnes i release notes
20. Standardiser "0 CVEs by Ollama" formulering
21. Tilføj note om PR #14406 er i v0.17.2, ikke v0.17.1
22. Verificer media contacts før outreach

---

**AUDIT STATUS: 🔴 35 FEJL FUNDET — 13 KRITISKE, 13 ALVORLIGE, 9 MINDRE**

**ANBEFALING: Ret alle 🔴 blokerende fejl før publicering. De alvorligste er OPSEC lækager (rigtige IPs + username) og CVSS inflation i offentlige materialer.**