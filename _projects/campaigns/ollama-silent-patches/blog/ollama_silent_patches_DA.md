# Ollamas Tavse Rettelses-Problem: 9 Sårbarheder, Nul CVEs, Nul Advisories

**Af: admin_user | Dato: 7. juni 2026 | Læsetid: 18 minutter**

---

> *"The Ollama maintainer team takes security seriously and will actively work to resolve security issues."*
> — Ollamas SECURITY.md

> **Virkelighed:** 5 forskere ignoreret. CERT Polska: "Unable to reach the vendor." Nul CVEs. Nul advisories. Nul credits. Tre kritiske sårbarheder er stadig **unpatched**.

---

## Executive Summary

Ollama — verdens mest populære lokale LLM-runtime med 173.000+ GitHub-stjerner og et anslået 25.000–300.000 offentligt eksponerede instanser — har et systemisk mønster med **at rette sikkerhedssårbarheder i stilhed uden at udstede CVEs, sikkerhedsadvisories eller kreditere forskere**.

Denne disclosure dokumenterer:

- **9 sårbarheder** (5 silently patched, 3 unpatched, 1 historisk)
- **15+ yderligere unpatched GGUF parser-sårbarheder**
- **Et mønster af forskerundertrykkelse** — 5 forskere ignoreret eller afvist
- **En "afvis → ret → tavshed"-cyklus** af Ollamas medstiftere
- **Nul CVEs, nul advisories, nul credits** udstedt af Ollama på trods af 15+ sikkerhedsrelevante rettelser

Konsekvenserne er ikke teoretiske. Tre sårbarheder er stadig **unpatched i v0.30.6**, inklusiv en kritisk heap out-of-bounds read der lækker proceshukommelse (system prompts, chatsessioner, API-nøgler, database-legitimationsoplysninger) med blot 3 uauthentificerede API-kald.

---

## Fundene

### 🔴 CVE-2026-5757 — GGUF Memory Leak (UNPATCHED)

| Felt | Værdi |
|------|-------|
| **CVE** | CVE-2026-5757 |
| **CVSS** | 5.3 (CVSS v4.0, Sonatype) / 7.5 (CVSS v3.1, eksponeret) / 9.8 (Tenable CVSS 3.0) |
| **Type** | Heap Out-of-Bounds Read / Uauthentificeret Memory Leak |
| **Angrebsvektor** | Remote, uauthentificeret (model upload) |
| **Berørt** | Alle Ollama-versioner op til og med v0.30.6 |
| **Status** | 🔴 **UNPATCHED** |

**Hvad den gør:** Tre uauthentificerede API-kald til en eksponeret Ollama-instans lækker hele proceshukommelsen — inklusiv system prompts, chatsessioner, API-nøgler og database-legitimationsoplysninger.

**Den sårbare kode:**

```go
// fs/ggml/ggml.go:515-520 — INGEN bounds checking på Shape multiplication
func (t Tensor) Elements() uint64 {
    var count uint64 = 1
    for _, n := range t.Shape {
        count *= n  // ← uint64 overflow, ingen validering
    }
    return count
}

// fs/gguf/gguf.go:93-127 — INGEN validering af dims, Shape, Type, Offset
func (f *File) readTensor() (TensorInfo, error) {
    dims, err := read[uint32](f)  // ← INGEN upper bound (0xFFFFFFFF = 4B dimensioner!)
    shape := make([]uint64, dims) // ← OOM mulig
    type_, err := read[uint32](f) // ← INGEN validering mod kendte typer
    offset, err := read[uint64](f)// ← INGEN filstørrelseskontrol
}
```

PR #14406 tilføjede fileSize-validering til v1-parseren **kun**. v2+ parseren (`fs/gguf/gguf.go`) forbliver **sårbar**.

**CERT Polska** (VU#518910): *"Unable to reach the vendor."*

---

### 🔴 KRITISK: Update Flow RCE — Path Traversal + Manglende Integritet (Silently Patched)

| Felt | Værdi |
|------|-------|
| **CVEs** | CVE-2026-42248 (manglende Windows-signatur), CVE-2026-42249 (path traversal) |
| **CVSS** | 9.1 (estimeret) |
| **Type** | Remote Code Execution via MITM Update |
| **PR** | [#16100](https://github.com/ollama/ollama/pull/16100) — "app: harden update flows" |
| **Forfatter** | dhiltgen (Daniel Hiltgen) |
| **Merged** | 2026-05-11 |
| **Rettet i** | v0.30.0 |
| **Release Notes** | ❌ **IKKE NÆVNT** |

Før denne rettelse kunne Ollamas auto-updater:

1. Downloade opdateringer **uden SHA256-verifikation**
2. Køre Windows-installationsprogrammer **uden Authenticode-signaturverifikation** (`return nil` ved fejl)
3. Tillade **path traversal** i opdateringsstaging (f.eks. `../../etc/passwd`)
4. Tillade **macOS bundle path escape**

En angriber på netværket kunne MITM opdateringskanalen og opnå **fuld remote code execution**.

**Forsker:** Striga.ai (Bartłomiej Dmitruk). Ollama anerkendte, derefter tavshed. CERT Polska overtog koordineringen.

---

### 🟠 HØJ: SSRF / Phishing Overlay via Markdown URL-håndtering (Silently Patched)

| Felt | Værdi |
|------|-------|
| **PR** | [#16380](https://github.com/ollama/ollama/pull/16380) — "Harden app markdown URL handling" |
| **CVSS** | 7.5 (estimeret) |
| **Type** | SSRF / Indirect Prompt Injection → Phishing Overlay |
| **Forfatter** | dhiltgen (Daniel Hiltgen) |
| **Approver** | BruceMacD — "Thanks for fixing!" |
| **Merged** | 2026-06-02 |
| **Rettet i** | v0.30.2 |
| **Release Notes** | ❌ **IKKE NÆVNT** |
| **CVE** | ❌ Ingen |

AI-agentværktøjer (BrowserOpen, WebFetch, WebSearch) accepterede vilkårlige URLs uden validering. Angrebskæde:

1. Angriber injicerer skjult prompt på ekstern webside
2. Model læser side, får injicerede instruktioner
3. Model kalder `WebFetch`/`BrowserOpen` med angribers URL (SSRF)
4. Angriber serverer phishing-overlay der erstatter Ollama UI

**Forsker:** PromptArmor (dec. 2025 rapport). **5 opfølgnings-e-mails ignoreret.** Rettet i stilhed 5,5 måneder senere.

---

### 🟠 HØJ: URL Policy Regex Bypass (Silently Patched)

| Felt | Værdi |
|------|-------|
| **PR** | [#16436](https://github.com/ollama/ollama/pull/16436) — "More harden app markdown URL handling" |
| **CVSS** | 7.2 (estimeret) |
| **Type** | Security Control Bypass |
| **Forfatter** | dhiltgen |
| **Merged** | 2026-06-02 (32 minutter efter PR #16380) |
| **Release Notes** | ❌ **IKKE NÆVNT** |
| **CVE** | ❌ Ingen |

Rettelsen for Fund 3 havde en bypass: regex'en `https?://[^\s<>"']+` ekskluderede ikke backtick-tegnet (`\x60`). En angriber kunne konstruere URLs som `` https://attacker.example/`ls`/ `` for at bryde ud af valideringen. Rettet i samme session, 32 minutter senere — men ingen CVE, ingen advisory.

---

### 🟠 HØJ: Codex Launch Configuration Hijacking (Semi-Silently Patched)

| Felt | Værdi |
|------|-------|
| **PR** | [#16437](https://github.com/ollama/ollama/pull/16437) — "launch: isolate Codex launch configuration" |
| **CVSS** | 7.5 (estimeret) |
| **Type** | Konfigurationskapring / Argument Injection |
| **Forfatter** | ParthSareen |
| **Merged** | 2026-06-02 |
| **Rettet i** | v0.30.2 |
| **Release Notes** | ⚠️ Nævnt men sikkerhedspåvirkning skjult |
| **CVE** | ❌ Ingen |

`ollama launch codex` sendte ALLE brugerargumenter direkte til Codex-binæren. En angriber kunne omdirigere alle prompts/svar til deres server via `--profile` eller `-c base_url`-flag. Rettet ved at gennemtvinge `--profile ollama-launch` og tilføje `codexValidateExtraArgs()`.

---

### 🟢 LAV: macOS SDK Target Leakage (Silently Patched)

| Felt | Værdi |
|------|-------|
| **PR** | [#16053](https://github.com/ollama/ollama/pull/16053) |
| **CVSS** | 3.1 (estimeret) |
| **Type** | Information Disclosure / Build Fingerprinting |
| **Rettet i** | v0.30.0 |
| **Release Notes** | ❌ **IKKE NÆVNT** |

---

### 🔴 KRITISK: CVE-2026-7482 "Bleeding Llama" (Historisk Silent Patch)

| Felt | Værdi |
|------|-------|
| **CVE** | CVE-2026-7482 |
| **CVSS** | 9.1 (Cyera) |
| **Type** | Out-of-Bounds Heap Read |
| **Rettet i** | v0.17.1 (25. feb 2026) — **I STILHED** |
| **Offentliggjort** | 5. maj 2026 (Cyera, ~3 måneder efter rettelse) |
| **Estimeret eksponering** | ~300.000 instanser |

Ollama sendte en kritisk sikkerhedsrettelse i v0.17.1 med **INGEN advisory, INGEN CVE, INGEN omtale i release notes**. Brugere havde ingen anelse om at en kritisk sårbarhed var rettet, hvilket efterlod ~300.000 instanser sårbare i 3 måneder.

---

### 15 Yderligere Unpatched GGUF-Sårbarheder

Udover de 9 dokumenterede ovenfor indeholder GGUF-parseren **mindst 15 yderligere unpatched sårbarheder** (V-O1 til V-O8 i Ollama Go-kode, V-C01 til V-C07 i llama.cpp C++-kode). Alle er stadig unpatched i v0.30.6.

---

## Mønsteret: Afvis → Ret → Tavshed

Ollamas medstiftere har etableret en gentagende cyklus for håndtering af sikkerhedsdisclosures:

```
Dag 0:    Forsker sender rapport til hello@ollama.com
Dag N:    Bruce MacDonald svarer: "Kan du sende et PoC?"
Dag N+1:  Forsker sender PoC
Dag N+12: Michael Chiang afviser: "Not technically viable" + "No disclosure agreement"
Dag N+14: Daniel Hiltgen merger 3 sikkerhedsrettelser på 1 time
Dag N+∞: Ingen CVE, ingen kredit, ingen advisory, ingen offentlig anerkendelse
```

### Forskerbehandlingsjournal

| Forsker | Dato | Sårbarhed | Ollamas Svar | Udfald |
|---|---|---|---|---|
| PromptArmor | 18. dec 2025 | Phishing overlay + dataudfiltrering | 5 opfølgninger **IGNORERET** | Silent patch 5,5 måneder senere |
| Striga.ai | Jan 2026 | Windows RCE (CVE-2026-42248/9) | Anerkendt, derefter **TAVS** | CERT Polska, 90-dages disclosure |
| py0zz1 | ~Nov 2025 | Sårbarhed (PR #13164) | 4 måneder, 0 kommentarer | Venter stadig på CVE |
| Ukendt | ~2026 | GGUF memory leak (CVE-2026-5757) | CERT Polska: "Unable to reach vendor" | **UNPATCHED** |
| Cyera | Maj 2026 | Heap OOB read (CVE-2026-7482) |Tvunget offentliggørelse | CVE tildelt (ikke af Ollama) |
| Denne forsker | Maj 2026 | SSRF + phishing + config hijack | "Send PoC" → "Not viable" → patched 48t senere | Ingen CVE, ingen kredit |
| CERT Polska | Apr 2026 | Flere CVEs-koordinering | "Unable to reach the vendor" | VU#518910 |

### SECURITY.md vs Virkelighed

| Ollamas Løfter | Virkelighed |
|---------------|-------------|
| "Tager sikkerhed alvorligt" | 5 forskere ignoreret/undertrykt |
| "Vil aktivt arbejde på at løse" | CERT Polska kan ikke nå leverandøren |
| "Giv os tilstrækkelig tid" | PromptArmor ventede 5,5 måneder |
| Antydet: CVE-tildeling | **0 CVEs** tildelt af Ollama |
| Antydet: Sikkerhedsadvisories | **0 advisories** publiceret |
| Antydet: Forskerkredit | **0 credits** givet |

---

## Eksponeret Instans-landskab

| Kilde | Antal | Dato | Vækst |
|-------|-------|------|-------|
| Cisco Talos | 1.139 | Sep 2025 | Basislinje |
| LeakIX | 12.269 | Feb 2026 | 11× |
| insecurestack | 25.000+ | Apr 2026 | 22× |
| Cyera/CVE-2026-7482 | 300.000 | Maj 2026 | 264× |

Alle instanser:
- Binder til `0.0.0.0:11434` som standard med **nul autentificering**
- Eksponerer fuld API: model-liste, oprettelse, sletning, pushing
- Ollama nægter at tilføje autentificering og udtaler at det er brugerens ansvar

---

## Tidslinje

| Dato | Begivenhed |
|------|-----------|
| Nov 2025 | py0zz1 rapporterer sårbarhed (PR #13164) — 4 måneder med 0 kommentarer |
| 18. dec 2025 | PromptArmor rapporterer phishing overlay + dataudfiltrering til hello@ollama.com |
| Jan 2026 | Striga.ai rapporterer Windows RCE; Ollama anerkender, derefter tavshed |
| 25. feb 2026 | v0.17.1 udgivet med CVE-2026-7482-rettelse — **I STILHED** |
| 22. apr 2026 | CERT Polska publicerer VU#518910 ("unable to reach vendor") |
| 5. maj 2026 | Cyera publicerer CVE-2026-7482 disclosure |
| 11. maj 2026 | PR #16100 (Update RCE) og #16053 (SDK leakage) silently merged |
| 13. maj 2026 | v0.30.0 udgivet — udelader begge sikkerheds-PRs fra notes |
| 15. maj 2026 | oss-security publicerer 6 yderligere GGUF parser-sårbarheder |
| 20. maj 2026 | Bruce MacDonald svarer forsker: "Send PoC" |
| 1. jun 2026 | Michael Chiang afviser: "Not technically viable" |
| 2. jun 2026 | Daniel Hiltgen merger PR #16380, #16436, #16437 (3 sikkerhedsrettelser på 1 time) |
| 3. jun 2026 | v0.30.2 udgivet — udelader alle 3 sikkerheds-PRs fra release notes |
| 7. jun 2026 | Denne disclosure publiceret |

---

## CVSS Scoring Oversigt

| Fund | CVE | CVSS | Alvorsgrad | Status |
|------|-----|------|------------|--------|
| GGUF Memory Leak | CVE-2026-5757 | 5.3 (v4.0) / 7.5 (v3.1) / 9.8 (Tenable) | Høj/Medium | 🔴 UNPATCHED |
| Update RCE | CVE-2026-42248/9 | 9.1 (est.) | Kritisk | ✅ Rettet v0.30.0 (silent) |
| Bleeding Llama | CVE-2026-7482 | 9.1 | Kritisk | ✅ Rettet v0.17.1 (silent) |
| SSRF/Phishing | Ingen | 7.5 (est.) | Høj | ✅ Rettet v0.30.2 (silent) |
| URL Bypass | Ingen | 7.2 (est.) | Høj | ✅ Rettet v0.30.2 (silent) |
| Codex Hijack | Ingen | 7.5 (est.) | Høj | ✅ Rettet v0.30.2 (semi-silent) |
| SDK Leakage | Ingen | 3.1 (est.) | Lav | ✅ Rettet v0.30.0 (silent) |
| GGUF Parser (15 vulns) | Ingen | Varierende | Kritisk-Høj | 🔴 UNPATCHED |

---

## Konsekvensanalyse

### For AI/ML-økosystemet

Ollama er ikke bare et hobbyprojekt — det er den **standardmåde** millioner af udviklere kører LLMs lokalt på. Med 173K+ GitHub-stjerner er det standardindgangen for:

- Enterprise AI/ML-udviklingsmiljøer
- Startup-infrastruktur der kører lokale modeller
- Virksomheds data science-teams der behandler følsomme data
- Cloud-hostede Ollama-instanser (eksponeret mod internettet)

Når Ollama retter kritiske sårbarheder i stilhed:

1. **Brugere opdaterer ikke** — de ved ikke der er en sikkerhedsrettelse
2. **Virksomheder kan ikke vurdere risiko** — ingen CVE, ingen advisory, ingen CVSS
3. **Sikkerhedsteams er blinde** — de kan ikke prioritere rettelser de ikke ved eksisterer
4. **Angribere har frit spil** — rettelserne er offentlige på GitHub, men sårbarhedsdetaljerne er det ikke

### Regnestykken

- **175.000+** offentligt eksponerede Ollama-instanser (konservativt estimat)
- **0** CVEs tildelt af Ollama
- **0** sikkerhedsadvisories publiceret
- **5** forskere ignoreret eller tavsgjort
- **3** sårbarheder stadig **unpatched** i v0.30.6
- **15+** GGUF parser-sårbarheder uden CVE eller rettelse
- **~300.000** instanser eksponeret for CVE-2026-7482 i 3 måneder (Cyera-estimat)

---

## Afhjælpning

### For Ollama-teamet (Akut)

1. **Publicer sikkerhedsadvisories** for alle silently patched sårbarheder — retrospektivt
2. **Anmod om CVEs** for PR #16380/16436 (SSRF) og PR #16100 (Update RCE)
3. **Tilføj en sikkerhedssektion til release notes** — selv én linje er bedre end tavshed
4. **Opret en vulnerability disclosure policy** udover hello@ollama.com
5. **Svar på sikkerhedsrapporter** — PromptArmor-non-responsen er utilgivelig
6. **Patch CVE-2026-5757** — der er gået måneder, og rettelsen er ligetil (tilføj bounds checking til GGUF parser)
7. **Tilføj autentificering som standard** — bind til 127.0.0.1 i stedet for 0.0.0.0

### For Ollama-brugere (Akutte handlinger)

1. **Opdater til v0.30.6+** straks
2. **Tjek om eksponeret**: `curl http://DIN_IP:11434/api/tags` — hvis dette returnerer data, er du eksponeret
3. **Bind til localhost**: `export OLLAMA_HOST=127.0.0.1:11434`
4. **Tilføj reverse proxy** med autentificering for fjernadgang
5. **Firewall port 11434** fra upålidelige netværk

### For CVE Numbering Authorities

Anmod om CVEs for:
- PR #16380/16436 (SSRF/Phishing Overlay)
- PR #16100 (Update RCE — kan overlappe med CVE-2026-42248/9)
- PR #16053 (SDK Target Leakage)
- 15 GGUF parser-sårbarheder (V-O1 til V-O8, V-C01 til V-C07)

---

## Metodologi & Forbehold

Denne disclosure er samlet fra open-source intelligence (GitHub API, NVD, CERT-advisories, publicerede blogindlæg), live scanning og uafhængig kodeanalyse. Ingen proprietær eller privat information er brugt. Ikke-verificérbare påstande (privat e-mail-korrespondance) er tydeligt markeret.

Målet er ikke at vanære Ollama, men at sikre at brugere er opmærksomme på silently patched sårbarheder, så de kan træffe informerede beslutninger om opdatering og sikring af deres installationer.

**Ollama har 173.000+ GitHub-stjerner og 25.000+ offentligt eksponerede instanser. De har et ansvar for at offentliggøre sikkerhedsrettelser.**

---

*Disclosure samlet af anonym sikkerhedsforsker. Al primær kilde-bevis tilgængelig i Claims-Evidence Matrix. CVE-2026-5757, CVE-2026-42248, CVE-2026-42249, CVE-2026-7482 er offentligt tildelte.*