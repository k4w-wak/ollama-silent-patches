# 🔴 DEEPSEEK — Nådesløs Final Review af Ollama Disclosure Package
## HVER ENESTE FEJL, MODSIGELSE, OG MANGLENDE BEVIS

**Reviewer:** grok (general-7cee03c1) — full file-by-file audit  
**Dato:** 2026-06-07  
**Scope:** ALLE 34 filer i ollama_disclosure_2026/ + KAMPAGNE/  
**Standard:** Nådesløs. 0 fejl tolerance. Alt der kan angribes, angribes her.

---

## 🔴 KRITISK: Blog + Twitter + MASTER_INDEX har FORKERTE CVSS Scores

Dette er den STØRSTE fejl i pakken lige nu.

**FINAL_DISCLOSURE_v2.md** (DEN KANONISKE FIL) har korrekte, recalibrerede scores:
| # | Finding | Korrekt CVSS |
|---|---------|-------------|
| 1 | SSRF/Phishing | **7.1** |
| 2 | Update RCE | **7.5** |
| 3 | Codex Hijack | **7.1** |
| 4 | SDK Leakage | **INFO** |
| 5 | CVE-2026-5757 | **5.3/7.5** |
| 6 | CVE-2026-7482 | **7.5** |

**MEN:** Blog (EN + DA) og Twitter (EN + DA) og MASTER_INDEX har STADIG de GAMLE, inflated scores:

| Fil | F1 SSRF | F2 Regex | F3 Update | F5 5757 | F6 7482 |
|-----|---------|----------|-----------|---------|---------|
| FINAL_DISCLOSURE_v2.md | 7.1 ✅ | 5.4 ✅ | 7.5 ✅ | 5.3/7.5 ✅ | 7.5 ✅ |
| blog EN | 7.5 ❌ | 7.2 ❌ | 9.1 ❌ | 9.0+ ❌ | 9.1 ❌ |
| blog DA | 7.5 ❌ | 7.2 ❌ | 9.1 ❌ | 9.0+ ❌ | 9.1 ❌ |
| twitter EN | 7.5 ❌ | 7.2 ❌ | 9.1 ❌ | 9.0+ ❌ | 9.1 ❌ |
| twitter DA | 7.5 ❌ | 7.2 ❌ | 9.1 ❌ | 9.0+ ❌ | 9.1 ❌ |
| MASTER_INDEX | 7.5 ❌ | 7.2 ❌ | 9.1 ❌ | 9.0+ ❌ | 9.1 ❌ |

**HVORFOR DET ER KRITISK:** Hvis nogen læser bloggen eller Twitter-tråden og SAMMENLIGNER med FINAL_DISCLOSURE_v2.md, vil de se TO FORSKELLIGE SÆT TAL. Det ødelægger troværdigheden. En journalist eller researcher vil spørge: "Hvilke tal er de rigtige? Hvorfor er der to versioner?"

**RETTELSE:** Alle 6 filer skal opdateres til at matche FINAL_DISCLOSURE_v2.md.

---

## 🔴 KRITISK: CVE-2026-5757 CVSS Inflation (9.0+ → 7.5)

Blog + Twitter kalder stadig CVE-2026-5757 for "CVSS 9.0+ CRITICAL". Men:

1. **Sonatype (CVSS v4.0): 5.3 MEDIUM** — den eneste officielle score
2. **grok-verify recalibrated (CVSS v3.1): 7.5 HIGH** — hvis /api/create er åben
3. **9.0+ er UDOKUMENTERET** — ingen kilde, ingen beregning, ingen begrundelse

At kalde noget "9.0+" uden at kunne vise beregningen er PRÆCIS den slags inflation som får reviewers til at N/A'e hele pakken.

**RETTELSE:** Blog + Twitter skal bruge 7.5 (v3.1) eller 5.3 (v4.0) — IKKE 9.0+.

---

## 🔴 KRITISK: CVE-2026-7482 "Bleeding Llama" CVSS Inflation (9.1 → 7.5)

Blog + Twitter kalder stadig CVE-2026-7482 for "CVSS 9.1". Men grok-verify recalibrated den til **7.5 HIGH**.

**Hvorfor 9.1 er forkert:**
- CVE-2026-7482 er en heap OOB READ — det er en LÆSE-operation, ikke en SKRIVE-operation
- I:H (Integrity High) kræver at angriberen kan MODIFICERE data. En read-only sårbarhed kan ikke have I:H
- I:L er maksimum for read-only — og kun hvis angriberen kan bruge de læste data til yderligere angreb
- ISS = 1 − [(1−0.56) × (1−0.22) × (1−0)] = 0.6568 → Impact = 4.22
- Med AV:N/AC:L/PR:N/UI:N/S:U: Base = Roundup(4.22 + 3.89) = 8.1 — men med korrekt I:L er ISS lavere
- Den korrekte beregning giver 7.5, ikke 9.1

**Cyera's oprindelige 9.1 var inflated.** At gentage den uden korrektion er at sprede misinformation.

**RETTELSE:** Blog + Twitter skal bruge 7.5 for CVE-2026-7482.

---

## 🟠 HØJ: Finding Count Inconsistens

| Fil | Antal findings nævnt |
|-----|---------------------|
| FINAL_DISCLOSURE_v2.md | 6 (korrekt — 1-6 med merge) |
| Blog EN | 9 (forkert — bruger gammel numbering) |
| Blog DA | 9 (forkert — bruger gammel numbering) |
| Twitter EN | 6 Ollama + 6 AI API = 12 total |
| MASTER_INDEX | 15 (inkluderer AI API findings) |
| EXECUTIVE_SUMMARY | 9 (forkert — gammel numbering) |

Blog + Executive Summary refererer stadig til "9 vulnerabilities" — men efter merge af Finding 2 ind i Finding 1 er der kun 6 primære Ollama findings (plus CVE-2026-5757 og CVE-2026-7482 som separate). 

**RETTELSE:** Opdatér blog til at sige "6 primary findings" eller forklar at 9 blev konsolideret til 6.

---

## 🟠 HØJ: Executive Summary har IKKE fået CVSS-opdatering

`00_EXECUTIVE_SUMMARY.md` (i ollama_disclosure_2026/) har STADIG de gamle tal:
- PR #16380: HIGH (burde være 7.1)
- PR #16436: HIGH (burde være 5.4, merged)
- PR #16100: CRITICAL (burde være HIGH 7.5)
- CVE-2026-5757: CRITICAL (burde være MEDIUM-HIGH 5.3/7.5)
- CVE-2026-7482: CRITICAL (burde være HIGH 7.5)

Denne fil er den FØRSTE mange læsere ser. Hvis den har forkerte tal, er hele pakken kompromitteret.

---

## 🟠 HØJ: dhiltgen Identity — Rettet i v2 men STADIG fejl i blog/twitter

Blog EN siger:
> "Daniel Hiltgen (@dhiltgen). 879+ commits. 15 security patches."
> "Not the CEO. Not a security team. One engineer."

Dette er KORREKT for v2 — men Twitter thread_01_EN tweet 13 siger stadig bare "dhiltgen" uden at præcisere at det er Daniel Hiltgen (ikke Jeffrey Morgan). Den nuance går tabt i Twitter-formatet.

---

## 🟡 MEDIUM: LIVE_SCAN_RESULTS.md — Forældede versionsnumre

`LIVE_SCAN_RESULTS.md` viser instances med versioner som 0.5.11, 0.19.0, 0.20.x. Men disclosure siger "v0.17.1 through v0.30.6" som affected range. 

**Problem:** v0.5.11 og v0.5.7 er LANGT ældre end v0.17.1. Hvis de er "affected", burde range være "v0.1.0 through v0.30.6" — ikke "v0.17.1 through v0.30.6".

**Enten:** Opdatér affected range til at inkludere ældre versioner, ELLER tilføj note om at pre-v0.17.1 også er sårbare men uden for scope.

---

## 🟡 MEDIUM: CORRIGENDUM.md nævner ting der ikke er rettet i blog

CORRIGENDUM.md retter 3 kritiske fejl:
1. dhiltgen identitet ✅ (rettet i v2)
2. CVE-2026-5757 severity ✅ (delvist rettet i v2 — men blog har stadig 9.0+)
3. PR version misassignment ✅ (rettet i v2)

Men CORRIGENDUM nævner også:
- PR #14406 partial mitigation
- 7 additional vulnerabilities
- Disse er IKKE afspejlet i FINAL_DISCLOSURE_v2.md eller blog

Enten skal de inkluderes, eller CORRIGENDUM skal opdateres til at fjerne claims der ikke er i den endelige pakke.

---

## 🟡 MEDIUM: Missing CVE-2026-5757 i cvss_recalibrated.md

`cvss_recalibrated.md` har IKKE en entry for CVE-2026-5757. Den har entries for #1-#6, men #5 i recalibreringen er "Bleeding Llama" (CVE-2026-7482). CVE-2026-5757 nævnes slet ikke i CVSS-recalibreringen.

FINAL_DISCLOSURE_v2.md henviser til cvss_recalibrated.md for alle scores — men CVE-2026-5757's score (5.3/7.5) er IKKE dokumenteret der.

---

## 🟡 MEDIUM: UI:R vs UI:N for Update RCE

FINAL_DISCLOSURE_v2.md Finding 2 (Update RCE) har UI:R (User Interaction: Required). Dette er diskutabelt:

- **UI:R argument:** Bruger skal have auto-update slået til (default, men kan deaktiveres)
- **UI:N argument:** Auto-update sker automatisk uden brugerinteraktion — brugeren behøver ikke gøre noget

CVSS spec siger: "UI:R — Successful exploitation requires a user to take some action before the vulnerability can be exploited." Hvis auto-update er default og sker automatisk, er dette UI:N.

**Hvis UI:N:** Score bliver 8.8 i stedet for 7.5. Dette burde diskuteres eksplicit.

---

## 🟡 MEDIUM: "25,000–175,000+ exposed instances" — Tallet er udokumenteret

FINAL_DISCLOSURE_v2.md siger "25,000–175,000+ exposed instances" men kilderne i LIVE_SCAN_RESULTS.md viser:
- Shodan (Jul 2025): ~270,988
- FuzzingLabs (Jul 2025): 200,000+
- SentinelOne/Censys (Jan 2026): 175,000+
- Cyera (May 2026): 300,000+

"25,000" kommer fra insecurestack (Apr 2026) men de andre tal er 175K-300K. Hvorfor er lower bound 25K? Det skal begrundes.

---

## 🟡 MEDIUM: "15+ additional unpatched GGUF parser vulnerabilities" — Ingen konkret liste

FINAL_DISCLOSURE_v2.md nævner "15+ additional unpatched GGUF parser vulnerabilities" men giver IKKE en konkret liste i dokumentet. Den henviser til CLAIMS_EVIDENCE_MATRIX.md — men læseren skal have tallene DIREKTE.

---

## 🟢 LAV: Dato-inkonsistens mellem filer

| Begivenhed | MASTER_TIMELINE | Blog | FINAL_DISCLOSURE |
|-----------|-----------------|------|-----------------|
| v0.17.1 release | Feb 25, 2026 | Feb 25, 2026 | Feb 25, 2026 ✅ |
| v0.30.0 release | May 13, 2026 | May 13, 2026 | May 13, 2026 ✅ |
| v0.30.2 release | Jun 3, 2026 | Jun 3, 2026 | Jun 3, 2026 ✅ |
| PR #16100 merge | May 11, 2026 | May 11, 2026 | May 11, 2026 ✅ |
| PR #16380 merge | Jun 2, 2026 | Jun 2, 2026 | Jun 2, 2026 ✅ |

Datoerne er konsistente på tværs. Godt.

---

## 🟢 LAV: Blog EN vs DA — Indholdsmæssigt identiske, begge har samme fejl

Begge blogposts har de samme CVSS-fejl. Hvis man retter den ene, skal man rette den anden.

---

## 🔴 MANGLENDE BEVISER (fra verification_audit.md — IKKE adresseret)

Min tidligere audit identificerede disse manglende beviser. De er STADIG ikke adresseret:

| # | Hvad mangler | Status |
|---|-------------|--------|
| 1 | **Live PoC for SSRF/phishing** — markdown → tool call → SSRF → phishing overlay | ❌ STADIG MANGLER |
| 2 | **Live PoC for Update MITM** — bevis at update-kanal er HTTP/HTTPS uden pinning | ❌ STADIG MANGLER |
| 3 | **Live PoC for Regex Bypass** — backtick URL faktisk bypasser url_policy.go | ❌ STADIG MANGLER |
| 4 | **Verifikation af update transport** — HTTP eller HTTPS? | ❌ STADIG MANGLER |

Live PoC output viser KUN at /api/create, /api/delete, /api/copy virker uden auth — IKKE SSRF/phishing eller Update MITM.

---

## 📊 SAMLET FEJL-OVERSIGT

| # | Fejl | Alvorlighed | Placering | Status |
|---|------|------------|-----------|--------|
| 1 | Blog EN har gamle CVSS scores | 🔴 KRITISK | blog/ollama_silent_patches_EN.md | IKKE RETTET |
| 2 | Blog DA har gamle CVSS scores | 🔴 KRITISK | blog/ollama_silent_patches_DA.md | IKKE RETTET |
| 3 | Twitter EN har gamle CVSS scores | 🔴 KRITISK | twitter/thread_01_EN.md | IKKE RETTET |
| 4 | Twitter DA har gamle CVSS scores | 🔴 KRITISK | twitter/thread_02_DA.md | IKKE RETTET |
| 5 | MASTER_INDEX har gamle CVSS scores | 🔴 KRITISK | 00_MASTER_INDEX.md | IKKE RETTET |
| 6 | Executive Summary har gamle scores | 🟠 HØJ | 00_EXECUTIVE_SUMMARY.md | IKKE RETTET |
| 7 | Blog siger "9 vulnerabilities" — burde være 6 | 🟠 HØJ | blog/*.md | IKKE RETTET |
| 8 | CVE-2026-5757 kaldes "9.0+ CRITICAL" i blog/twitter | 🔴 KRITISK | blog/*.md + twitter/*.md | IKKE RETTET |
| 9 | CVE-2026-7482 kaldes "9.1" i blog/twitter — burde være 7.5 | 🔴 KRITISK | blog/*.md + twitter/*.md | IKKE RETTET |
| 10 | CVE-2026-5757 mangler i cvss_recalibrated.md | 🟡 MEDIUM | cvss_recalibrated.md | IKKE RETTET |
| 11 | Affected range "v0.17.1–v0.30.6" ekskluderer v0.5.x instances | 🟡 MEDIUM | FINAL_DISCLOSURE_v2.md | IKKE RETTET |
| 12 | "15+ unpatched" har ingen konkret liste i hoveddokument | 🟡 MEDIUM | FINAL_DISCLOSURE_v2.md | IKKE RETTET |
| 13 | UI:R vs UI:N for Update RCE er diskutabelt | 🟡 MEDIUM | FINAL_DISCLOSURE_v2.md | BØR DISKUTERES |
| 14 | Missing PoC for SSRF og Update MITM | 🔴 KRITISK | Alle filer | IKKE RETTET |

---

## 🎯 HVAD SKAL DER TIL FOR 100%?

### Øjeblikkeligt (før publicering):

1. **Opdatér blog EN + DA** — erstat ALLE CVSS scores med recalibrerede værdier
2. **Opdatér Twitter EN + DA** — erstat ALLE CVSS scores med recalibrerede værdier
3. **Opdatér MASTER_INDEX** — erstat ALLE CVSS scores
4. **Opdatér Executive Summary** — recalibrerede scores
5. **Tilføj CVE-2026-5757 til cvss_recalibrated.md**
6. **Fjern "9 vulnerabilities" → "6 primary findings"** i blog
7. **Fjern "9.0+ CRITICAL" for CVE-2026-5757** → brug 7.5 eller 5.3
8. **Fjern "9.1" for CVE-2026-7482** → brug 7.5

### Før submition til bug bounty:

9. **Lav PoC video for SSRF angreb**
10. **Verificér update transport (HTTP vs HTTPS)**

---

## ✅ DOM

**Nuværende status: 70% klar.**

FINAL_DISCLOSURE_v2.md er ~95% korrekt (enkelte mindre issues). Men blog, twitter, og executive summary er ~40% korrekte — de har STADIG de gamle, inflated tal.

**Publicering nu = troværdighedsskade.** En journalist der læser bloggen og derefter tjekker FINAL_DISCLOSURE vil finde to forskellige sæt tal og konkludere at researchen er upålidelig.

**RET FØRST. PUBLICÉR SÅ.**
