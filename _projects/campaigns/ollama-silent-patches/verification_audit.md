# VERIFICATION AUDIT — Ollama Silent Patch Disclosure Package
## Ærlig, kritisk gennemgang af samtlige findings

**Auditor:** grok-verify (general-7cee03c1)  
**Dato:** 2026-06-07  
**Scope:** Alle FINDING_*.md, CLAIMS_EVIDENCE_MATRIX.md, VERIFICATION_REPORT.md, CORRIGENDUM.md, FINAL_DISCLOSURE.md, CROSS_REFERENCES.md

---

## OVERORDNET VURDERING

| Dimension | Status | Kommentar |
|-----------|--------|-----------|
| Faktuel korrekthed | ⚠️ DELVIS | 3 kritiske fejl rettet i Corrigendum, men FINAL_DISCLOSURE gentager nogle |
| Severity inflation | 🔴 PROBLEMATISK | 3 af 6 findings har inflated CVSS scores |
| Reproducerbarhed | ⚠️ DELVIS | Kun code-diff bevis, ingen live PoC for 5 af 6 findings |
| Koherence | ⚠️ SVAG | Version-confusion, CVE-confusion, finding-overlap |
| N/A-risiko | 🔴 HØJ | 3 af 6 findings har høj risiko for N/A fra reviewers |

---

## FINDING-BY-FINDING AUDIT

---

### FINDING 1: SSRF/Phishing Overlay via Markdown URL Handling

| Dimension | Vurdering |
|-----------|-----------|
| **Claim konkret?** | ✅ JA — specifikke filer, funktioner, angrebsvej |
| **Bevis reproducerbart?** | ⚠️ DELVIS — PR diff er verificerbar, men ingen live PoC |
| **Severity rimelig?** | 🔴 INFLATED |
| **Opgivet CVSS** | 7.5 (HIGH) |
| **Anbefalet CVSS** | 5.5–6.1 (MEDIUM-HIGH) |
| **N/A-risiko** | 🟡 MEDIUM-HØJ |

**CVSS Recalculation (CVSS v3.1):**
- AV:N (netværk) — markdown kan indeholde ondsindede URL'er
- AC:H — kræver indirekte prompt injection FØRST, derefter model skal vælge at kalde tool
- PR:N — ingen autentifikation krævet
- UI:R — bruger skal interagere med tool-output
- S:C — app context → netværk context
- C:L — SSRF kan prob interne services
- I:L — phishing overlay kan snyde bruger
- A:N — ingen availability impact
- **Beregnet: AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N ≈ 5.4–6.1**

**Svagheder:**
1. Angrebskæden er 3-ledet: prompt injection → model kalder tool → SSRF/phishing. Hvert led reducerer reell risiko.
2. Ingen demonstration af at angrebet faktisk virker. Code-diff viser at Ollama TILFØJTEDE en sikkerhedskontrol — men det beviser ikke at den var exploiterbar FØR patchen.
3. PromptArmor's rapport fra Dec 2025 blev ignoreret — men PromptArmor's claim er ikke uafhængigt verificeret i denne pakke.
4. "Phishing overlay" claimet er svært at reproducere — det kræver at markdown renderer HTML i app'en, hvilket PR'en også ændrede.

**N/A-scenarier:**
- Reviewer kan sige: "Dette er expected behavior for AI tools — modellen kan altid generere ondsindede links"
- Reviewer kan sige: "Prompt injection er out of scope for dette program"
- Reviewer kan sige: "Patchen blev merged — hvor er PoC for pre-patch version?"

**Anbefalet severity: MEDIUM (5.5)** — claimet er reelt, men kræver for mange betingelser for at fortjene HIGH.

---

### FINDING 2: URL Policy Regex Bypass

| Dimension | Vurdering |
|-----------|-----------|
| **Claim konkret?** | ✅ JA — specifik regex, specifik bypass-karakter |
| **Bevis reproducerbart?** | ✅ JA — regex-ændring er direkte verificerbar |
| **Severity rimelig?** | 🔴 INFLATED |
| **Opgivet CVSS** | 7.2 (HIGH) |
| **Anbefalet CVSS** | 4.5–5.0 (MEDIUM) |
| **N/A-risiko** | 🔴 HØJ |

**Svagheder:**
1. **Dette er IKKE en selvstændig sårbarhed.** Det er en bypass af en NY sikkerhedskontrol (PR #16380) som blev merged 22 minutter før. Bug bounty reviewers N/A'er ofte bypasses af nye controls — "du fandt en bug i en patch der er 22 minutter gammel, det er en patch-bug ikke en særskilt finding."
2. CVSS 7.2 er urealistisk for en regex bypass. Uden Finding 1 har denne NUL impact. Den ARVER severity fra Finding 1 OG er afhængig af den.
3. Merge-timeline (22 min mellem PR #16380 og #16436) tyder på intern review fandt bypassen — IKKE at en angriber exploiterte den.

**N/A-scenarier:**
- "Duplikat af Finding 1 — samme sårbarhedsklasse"
- "Bypass af en 22-minutter-gammel patch er ikke en selvstændig finding"
- "Ingen bevis for at bypassen blev exploitet"

**Anbefalet severity: MEDIUM (4.5)** — bør merges med Finding 1 som sub-finding.

---

### FINDING 3: Update Flow Path Traversal + Missing Integrity

| Dimension | Vurdering |
|-----------|-----------|
| **Claim konkret?** | ✅ JA — specifikke manglende checks, specifikke angrebsveje |
| **Bevis reproducerbart?** | ⚠️ DELVIS — code diff er klar, men MITM-demo mangler |
| **Severity rimelig?** | ⚠️ BORDERLINE |
| **Opgivet CVSS** | 9.1 (CRITICAL) |
| **Anbefalet CVSS** | 8.0–8.5 (HIGH) hvis MITM bevises, ellers 6.5 (MEDIUM) |
| **N/A-risiko** | 🟡 MEDIUM |

**CVSS Recalculation (CVSS v3.1):**
- AV:N — opdateringer hentes over netværk
- AC:H — kræver MITM position (ikke trivielt for de fleste angribere)
- PR:N — ingen autentifikation krævet
- UI:N — auto-update, bruger behøver ikke gøre noget
- S:C — app → system
- C:H/I:H/A:H — fuld kodeeksekvering
- **Beregnet: AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H ≈ 8.8–9.0**

**MEN:** Hvis update-kanalen bruger HTTPS med certificate pinning, falder AC til VERY_HIGH og CVSS til ~7.0. Pakken etablerer IKKE om Ollama bruger HTTP eller HTTPS til opdateringer.

**Svagheder:**
1. **Kritisk manglende bevis:** Er opdateringskanalen HTTP eller HTTPS? Hvis HTTPS med pinning, er MITM angrebet teoretisk.
2. Path traversal kræver at angriberen kontrollerer indholdet af opdateringsarkivet — hvilket igen kræver MITM.
3. Windows Authenticode-manglen er KUN relevant på Windows. macOS og Linux har andre mekanismer.
4. CVSS 9.1 forudsætter at alle 3 angrebstrin (MITM + ingen integrity + path traversal) er mulige samtidig.

**Stærke sider:**
1. Koden er utvetydig — SHA256 verification blev TILFØJET, hvilket beviser at den MANGLEDE
2. Windows Authenticode-tilføjelsen (175 nye linjer) er meget konkret
3. Path traversal tests (265 nye linjer) demonstrerer at Ollama anser dette som en reel trussel

**N/A-scenarier:**
- "Ingen PoC for MITM på update-kanalen"
- "Auto-update kan deaktiveres"
- "HTTPS med pinning gør MITM teoretisk"

**Anbefalet severity: HIGH (8.0)** — men KUN hvis MITM på update-kanalen kan demonstreres. Uden det: MEDIUM (6.5).

---

### FINDING 4: macOS SDK Target Leakage

| Dimension | Vurdering |
|-----------|-----------|
| **Claim konkret?** | ✅ JA — specifik binary, specifik leaked info |
| **Bevis reproducerbart?** | ✅ JA — kan inspicere binary direkte |
| **Severity rimelig?** | ✅ JA — CVSS 3.1 er passende |
| **Opgivet CVSS** | 3.1 (LOW) |
| **Anbefalet CVSS** | 2.0–3.1 (LOW/INFO) |
| **N/A-risiko** | 🔴 MEGET HØJ |

**Svagheder:**
1. Dette er build fingerprinting — de fleste bug bounty programmer klassificerer dette som P5 (Informational) eller N/A.
2. Impact er minimal — angriber lærer hvilken SDK version der blev brugt til at bygge binaryen. Dette er offentligt tilgængeligt information for open source projekter.
3. PR #16053 fixes et upstream MLX bug, ikke en Ollama-specifik sårbarhed.

**N/A-scenarier:**
- "Informational — build fingerprinting er ikke en sårbarhed"
- "P5 — minimal impact, ingen exploitation"
- "Open source projekt — SDK version er allerede offentlig"

**Anbefalet severity: INFO (2.0)** — reelt en informational finding, ikke en sårbarhed.

---

### FINDING 5: CVE-2026-7482 "Bleeding Llama" (Historical)

| Dimension | Vurdering |
|-----------|-----------|
| **Claim konkret?** | ✅ JA — CVE er offentlig og verificeret |
| **Bevis reproducerbart?** | ✅ JA — CVE, Cyera disclosure, branch coverage |
| **Severity rimelig?** | ✅ JA — CVSS 9.1 er fair for unauthenticated heap OOB read |
| **Opgivet CVSS** | 9.1 (CRITICAL) |
| **Anbefalet CVSS** | 9.1 (CRITICAL) — men se note |
| **N/A-risiko** | 🟢 LAV |

**Svagheder:**
1. Dette er en HISTORISK finding — allerede patchet i v0.17.1 (Feb 2026) og CVE assignet i May 2026. Bug bounty reviewers vil sandsynligvis sige "allerede kendt, allerede patchet."
2. Pakkens primære værdi her er at etablere PATTERN (Ollama patcher lydløst), ikke at rapportere en ny finding.
3. CVE-2026-5757 vs CVE-2026-7482 forvirring — FINAL_DISCLOSURE.md blander de to CVEs sammen i sektionen "CRITICAL 1". Corrigendum retter CVE-2026-5757 til 5.3, men lader CVE-2026-7482 stå ved 9.1. Det er korrekt, men forvirrende for læseren.

**Stærke sider:**
1. Den eneste finding med en faktisk CVE
2. Uafhængigt verificeret af Cyera
3. Branch coverage beviser at patchen var security-relevant
4. Etablerer "silent patch" patternet overbevisende

**N/A-scenarier:**
- "Allerede kendt CVE — ikke en ny finding"
- "Allerede patchet — ingen impact på nuværende version"

**Anbefalet severity: CRITICAL (9.1)** — men KUN som pattern-bevis, ikke som ny finding.

---

### FINDING 6: Codex Launch Configuration Hijacking

| Dimension | Vurdering |
|-----------|-----------|
| **Claim konkret?** | ✅ JA — specifik kode, specifik command |
| **Bevis reproducerbart?** | ⚠️ DELVIS — need Codex installeret for at teste |
| **Severity rimelig?** | 🔴 INFLATED |
| **Opgivet CVSS** | 7.5 (HIGH) |
| **Anbefalet CVSS** | 5.0–5.5 (MEDIUM) |
| **N/A-risiko** | 🔴 MEGET HØJ |

**CVSS Recalculation (CVSS v3.1):**
- AV:L — kræver lokal adgang til at køre kommando
- AC:L — kommandoen er simpel
- PR:N — ingen særlige rettigheder krævet
- UI:R — bruger skal køre kommandoen (social engineering)
- S:C — redirecter til attacker-controlleret server
- C:H/I:H/A:N — alle prompts og responses kompromitteres
- **Beregnet: AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N ≈ 7.0–7.5**

**MEN:** AV:L (lokal adgang) + UI:R (bruger skal køre specifik kommando) reducerer reell risiko DRAMATISK. I praksis er dette: "hvis du overbeviser brugeren om at køre en ondsindet kommando, kan du redirecte deres AI-sessions" — hvilket er sandt for NÆSTEN ALLE kommandoer.

**Svagheder:**
1. **"Hvis du kan lokke brugeren til at køre en ondsindet kommando, sker der noget ondt"** — dette er sandt for ethvert program. Reviewers vil N/A dette som "expected behavior for command-line arguments."
2. Kræver at brugeren kører `ollama launch codex` med specifikke extra-argumente. Det er ikke en remote sårbarhed.
3. Social engineering vektor er teoretisk — pakken demonstrerer ikke en reel social engineering kampagne.
4. Koden viser at Ollama tilføjede `codexValidateExtraArgs()` — hvilket er god defense-in-depth, men beviser ikke at det var exploiterbart før patchen.

**N/A-scenarier:**
- "Local attack requiring user to run specific command = not a vulnerability"
- "Command-line argument injection is expected behavior"
- "No remote exploitation vector"
- "If you can trick user into running commands, you already have access"

**Anbefalet severity: MEDIUM (5.0)** — defense-in-depth finding, ikke en sårbarhed i traditionel forstand.

---

## TVÆRGÅENDE SVAGHEDER I PAKKEN

### 1. CVE-2026-5757 vs CVE-2026-7482 Forvirring 🔴

FINAL_DISCLOSURE.md's "CRITICAL 1" sektion omtaler CVE-2026-5757 med CVSS "9.0+" men Corrigendum retter til CVSS 5.3 (Sonatype v4.0). SAMTIDIGT er CVE-2026-7482 (Bleeding Llama) en SEPARAT CVE med CVSS 9.1. Pakken blander de to.

**Anbefaling:** Split dem tydeligt. CVE-2026-5757 = CVSS 5.3 MEDIUM. CVE-2026-7482 = CVSS 9.1 CRITICAL. De er forskellige sårbarheder.

### 2. Finding Overlap 🔴

Findings 1 og 2 er den SAMME sårbarhedsklasse. Finding 2 er en bypass af Finding 1's patch. De bør merges til én finding med to sub-sektioner.

### 3. Ingen Live PoC 🔴

Ingen af findings (undtagen Finding 5 som allerede har en public CVE) har en live demonstration. Alt er code-diff analyse. Bug bounty reviewers forventer PoC.

**Anbefaling:** Lav minimum 2 PoCs:
1. SSRF/phishing overlay på pre-v0.30.2 Ollama (Finding 1)
2. MITM på update-kanalen (Finding 3)

### 4. Version Confusion ⚠️

Executive summary siger v0.23.3 for PRs #16100 og #16053. Detaljerede findings siger v0.30.0. Corrigendum retter, men FINAL_DISCLOSURE gentager ikke rettelsen eksplicit.

### 5. dhiltgen Identitet 🔴 (allerede rettet i Corrigendum)

Kritisk: dhiltgen er Daniel Hiltgen, IKKE Jeffrey Morgan. Corrigendum retter, men narrativet "CEO skriver alle sikkerhedspatches i hemmelighed" er MISVISENDE. Det korrekte narrativ er: "Senior engineer skriver patches, CEO og Co-Founder opretholder organisatorisk stilhed."

### 6. Severity Inflation Pattern 🔴

| Finding | Opgivet CVSS | Anbefalet CVSS | Delta |
|---------|-------------|----------------|-------|
| 1 SSRF | 7.5 | 5.5 | -2.0 |
| 2 Regex Bypass | 7.2 | 4.5 | -2.7 |
| 3 Update RCE | 9.1 | 8.0* | -1.1 |
| 4 SDK Leak | 3.1 | 2.0 | -1.1 |
| 5 Bleeding Llama | 9.1 | 9.1 | 0.0 |
| 6 Codex Hijack | 7.5 | 5.0 | -2.5 |

*Finding 3: 8.0 hvis MITM bevises, 6.5 hvis ikke

Gennemsnitlig inflation: **-1.9 CVSS points**

---

## HVAD KUNNE BLIVE N/A'ET

| Finding | N/A Risiko | Årsag |
|---------|-----------|-------|
| 1 SSRF | 🟡 MEDIUM | Prompt injection kan betragtes som out-of-scope |
| 2 Regex Bypass | 🔴 HØJ | Bypass af 22-min gammel patch, ikke selvstændig finding |
| 3 Update RCE | 🟡 MEDIUM | Kan kræve MITM PoC for at blive accepteret |
| 4 SDK Leak | 🔴 MEGET HØJ | Informational, P5, open source |
| 5 Bleeding Llama | 🟢 LAV | Allerede kendt CVE, men etablerer pattern |
| 6 Codex Hijack | 🔴 MEGET HØJ | Lokal + user interaction = expected behavior |

**Forventet N/A rate: 2-3 af 6 findings**

---

## HVAD BEHØVER MANUAL VERIFICATION

| Finding | Hvad mangler | Kritikalitet |
|---------|--------------|-------------|
| 1 SSRF | Live PoC: Ondsinnet markdown → tool call → SSRF/phishing | 🔴 KRITISK |
| 2 Regex Bypass | Live PoC: Backtick URL bypasser url_policy.go | 🟡 VIGTIGT |
| 3 Update RCE | Bevis: Update-kanalen er HTTP eller HTTPS uden pinning | 🔴 KRITISK |
| 4 SDK Leak | Ingen — code diff er tilstrækkeligt | 🟢 BEHØVES IKKE |
| 5 Bleeding Llama | Ingen — CVE er offentlig | 🟢 BEHØVES IKKE |
| 6 Codex Hijack | Live PoC: Argument injection redirecter til attacker server | 🟡 VIGTIGT |

---

## ENDelig ANBEFALEDE SEVERITIES

| # | Finding | Opgivet | Anbefalet | Justering |
|---|---------|---------|-----------|-----------|
| 1 | SSRF/Phishing Overlay | HIGH 7.5 | **MEDIUM 5.5** | Kræver prompt injection + user interaction + model cooperation |
| 2 | Regex Bypass | HIGH 7.2 | **MEDIUM 4.5** | Bypass af ny patch, ikke selvstændig finding. MERGES med #1 |
| 3 | Update RCE | CRITICAL 9.1 | **HIGH 8.0** (med MITM PoC) / **MEDIUM 6.5** (uden) | AC:H reducerer score; mangler MITM bevis |
| 4 | SDK Leakage | LOW 3.1 | **INFO 2.0** | Build fingerprinting er P5/infoal for open source |
| 5 | Bleeding Llama | CRITICAL 9.1 | **CRITICAL 9.1** | Korrekt — men historisk, allerede patchet |
| 6 | Codex Hijack | HIGH 7.5 | **MEDIUM 5.0** | Lokal + user interaction = defense-in-depth, ikke RCE |

---

## TOP 5 HANDLINGER FØR INSENDNING

1. **🔴 Split CVE-2026-5757 og CVE-2026-7482** — de er forskellige sårbarheder med forskellige CVSS scores
2. **🔴 Lav PoC for Finding 1 (SSRF)** og **Finding 3 (MITM)** — uden live demonstration er findings svage
3. **🟡 Merge Finding 1 og 2** til én finding med to sub-sektioner — reducerer N/A-risiko
4. **🟡 Nedgradér severities** til anbefalede værdier — ellers risikerer du inflation-kladning fra reviewers
5. **🟡 Drop Finding 4 (SDK Leakage)** eller reklassificér som "Informational" — de fleste programmer N/A'er build fingerprinting