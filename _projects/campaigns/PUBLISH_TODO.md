# 🚀 PUBLISH TODO — Ollama Silent Patches Full Disclosure
## Assistent-venlig checkliste — alt hvad du skal gøre, i rækkefølge

**Oprettet:** 2026-06-08  
**Status:** IKKE STARTET  
**Deadline:** ASAP — historien er time-sensitive (Ollama v0.30.7 kom 7. juni)

---

## 📂 VIGTIGE FILER — ALT LIGGER ALLEREDE KLAR

| Sti | Indhold | Klar? |
|-----|---------|-------|
| `~/Desktop/KAMPAGNE/00_MASTER_INDEX.md` | Fuldt indholdsfortegnelse | ✅ |
| `~/Desktop/KAMPAGNE/blog/ollama_silent_patches_EN.md` | Blog post (348 linjer) | ✅ |
| `~/Desktop/KAMPAGNE/blog/ollama_silent_patches_DA.md` | Blog post dansk (348 linjer) | ✅ |
| `~/Desktop/KAMPAGNE/twitter/thread_02_DA.md` | Twitter thread dansk (20 tweets) | ✅ |
| `~/Desktop/KAMPAGNE/twitter/thread_01_EN.md` | Twitter thread engelsk (20 tweets) | ✅ |
| `~/Desktop/KAMPAGNE/twitter/thread_02_DA.md` | Twitter thread dansk (20 tweets) | ✅ |
| `~/Desktop/KAMPAGNE/twitter/thread_04_follow_up_DA.md` | Follow-up thread dansk (12 tweets) | ✅ |
| `~/Desktop/KAMPAGNE/blog/follow_up_7_days_later.md` | Follow-up artikel engelsk | ✅ |
| `~/Desktop/KAMPAGNE/twitter/thread_03_follow_up_EN.md` | Follow-up thread engelsk (12 tweets) | ✅ |
| `~/Desktop/KAMPAGNE/twitter/thread_04_follow_up_DA.md` | Follow-up thread dansk (12 tweets) | ✅ |
| `~/Desktop/KAMPAGNE/blog/follow_up_7_days_later.md` | Follow-up artikel engelsk | ✅ |
| `~/Desktop/KAMPAGNE/check_protonmail.py` | ProtonMail inbox checker script | ✅ |
| `~/Desktop/KAMPAGNE/twitter/thread_04_follow_up_DA.md` | Follow-up thread dansk (12 tweets) | ✅ |
| `~/Desktop/KAMPAGNE/blog/follow_up_7_days_later.md` | Follow-up artikel engelsk | ✅ |
| `~/Desktop/KAMPAGNE/twitter/thread_02_DA.md` | Twitter thread dansk (20 tweets) | ✅ |
| `~/Desktop/KAMPAGNE/ghsa/advisories.md` | 3 GHSA advisories | ✅ |
| `~/Desktop/KAMPAGNE/timeline/disclosure_timeline.md` | Fuld kronologi | ✅ |
| `~/Desktop/KAMPAGNE/legal/legal_research.md` | Safe harbor, EU CRA, dansk lov | ✅ |
| `~/Desktop/KAMPAGNE/media_contacts.md` | Journalister, forskere, CERT (212 linjer) | ✅ |
| `~/Desktop/KAMPAGNE/deep_analysis.md` | MiniMax CORS, Stripe, Cloud vs Desktop (899 linjer) | ✅ |
| `~/Desktop/KAMPAGNE/verification_audit.md` | Kritisk review af alle findings (314 linjer) | ✅ |
| `~/Desktop/KAMPAGNE/cvss_recalibrated.md` | CVSS v3.1 recalibration | ✅ |
| `~/Desktop/KAMPAGNE/FINAL_DISCLOSURE.md` | Komplet disclosure v2 (til GitHub repo) | ✅ |
| `~/Desktop/KAMPAGNE/FINAL_DISCLOSURE_v2.md` | Seneste version | ✅ |
| `~/Desktop/KAMPAGNE/poc_evidence/` | 15 findings, 34+ PoC filer | ✅ |
| `~/Desktop/ollama_disclosure_2026/` | Full audit docs (30+ filer) | ✅ |

---

## ✅ TRIN 1 — OPRET PUBLIC GITHUB REPO

**Hvorfor:** Du skal have et offentligt link at peje på fra Reddit, HN, Twitter osv.

- [ ] Opret GitHub repo: `ollama-silent-patches-disclosure` (public)
- [ ] Upload `FINAL_DISCLOSURE.md` som `README.md`
- [ ] Upload `poc_evidence/` mappen med alle PoC scripts
- [ ] Upload `verification_audit.md`
- [ ] Upload `cvss_recalibrated.md`
- [ ] Upload `timeline/disclosure_timeline.md`
- [ ] Upload `deep_analysis.md`
- [ ] Upload `legal/legal_research.md`
- [ ] Tilføj `LICENSE` (MIT eller CC-BY-4.0)
- [ ] Tilføj `SECURITY.md` med responsible disclosure policy
- [ ] **Test:** Kan man se repoet offentligt? Virker linket?

**Repo struktur:**
```
ollama-silent-patches-disclosure/
├── README.md                          (= FINAL_DISCLOSURE.md)
├── ADVISORIES.md                      (= ghsa/advisories.md)
├── VERIFICATION_AUDIT.md
├── CVSS_RECALIBRATED.md
├── TIMELINE.md
├── DEEP_ANALYSIS.md
├── LEGAL_RESEARCH.md
├── MEDIA_CONTACTS.md
├── poc_evidence/
│   ├── 01_SSRF_URL_Policy/
│   ├── 02_Regex_Bypass/
│   ├── 03_Update_RCE/
│   ├── 04_SDK_Leakage/
│   ├── 05_Bleeding_Llama/
│   ├── 06_Codex_Hijacking/
│   ├── 07_CVE_2026_5757/
│   ├── 08_CORS_DeepInfra/
│   ├── 09_CORS_DeepSeek/
│   ├── 10_CORS_Hyperbolic/
│   ├── 11_CORS_Baichuan/
│   ├── 12_CORS_MiniMax/
│   ├── 13_CORS_LangSmith/
│   ├── 14_Live_Exposed_Instances/
│   └── 15_Exposed_Instance_Scanner/
├── LICENSE
└── SECURITY.md
```

---

## ✅ TRIN 2 — PUBLICÉR BLOG POST

**Hvorfor:** Reddit og HN kræver et link. Bloggen er din "landing page".

**Vælg platform (VÆLG ÉN):**
- **Option A: Medium** — Nem, god SEO, AI community læser Medium aktivt
- **Option B: GitHub Pages** — Gratis, linked til dit repo, teknisk læserskare
- **Option C: Substack** — God til newsletters, AI folk læser Substack

- [ ] Opret konto hvis nødvendig
- [ ] Kopiér indhold fra `blog/ollama_silent_patches_EN.md`
- [ ] Tilføj link til GitHub repo i toppen og bunden
- [ ] Tilføj billeder/screenshots hvis du har dem (fra `poc_evidence/`)
- [ ] Preview og tjek formattering
- [ ] **Publisér**
- [ ] **Test:** Virker linket? Deler det korrekt på social media?

**Anbefaling:** Start med **Medium** — hurtigst at sætte op, størst reach i AI community.

---

## ✅ TRIN 3 — TWITTER/X THREAD (FØRST!)

**Hvorfor:** Twitter er hurtigst. Hvis @KGreshake eller @CyeraResearch retweetter = viral.

- [ ] Log ind på X/Twitter
- [ ] Brug `twitter/thread_01_EN.md` — kopier tweet for tweet
- [ ] Tilføj link til blog post i tweet 1 eller 2
- [ ] Tag relevante folk:
  - `@OllamaAI` — Ollama officiel
  - `@KGreshake` — PromptArmor, AI security
  - `@striga_ai` — Striga.ai, Ollama CVE researcher
  - `@jmorganca` — Ollama creator (Jeffrey Morgan)
  - `@nickyricky` — security community
- [ ] Tilføj hashtags: `#Ollama #AIsecurity #SilentPatch #CVE #BugBounty`
- [ ] **Post thread**
- [ ] Reply på thread med link til GitHub repo
- [ ] **30 min efter:** Post dansk version `twitter/thread_02_DA.md` hvis relevant

---

## ✅ TRIN 4 — REDDIT (r/LocalLLaMA FØRST)

**Hvorfor:** 741K medlemmer, Ollamas primære community, højt engagement på security posts.

### r/LocalLLaMA (FØRST — størst reach)
- [ ] Opret post med titlen:
  > 🕵️ Ollama silently patched a model identity leak in v0.30.7 without disclosure — and left 5 unpatched vulns including CVE-2026-5757
- [ ] Brug blog-link som URL (ikke self-post — link posts får mere reach)
- [ ] I kommentarer: tilføj TL;DR med key findings
- [ ] **Vent 30-60 min før næste subreddit**

### r/netsec (professionelt security community)
- [ ] Opret post med titlen:
  > Ollama's pattern of silent patching: 7 vulnerabilities, zero CVEs, zero advisories, researcher suppression
- [ ] Link til blog eller GitHub repo

### r/cybersecurity (bredere reach)
- [ ] Cross-post eller nyt indlæg
- [ ] Fokus på "silent patching" pattern

### r/ollama (target audience)
- [ ] Cross-post fra r/LocalLLaMA eller nyt indlæg
- [ ] Mere teknisk fokus — "hvad betyder det for din Ollama installation?"

### r/MachineLearning (optional — meget stort subreddit)
- [ ] Kun hvis r/LocalLLaMA får traction
- [ ] Fokus på AI infrastruktur sikkerhed bredt

**VIGTIGT:** Læs hver subreddits regler FØR du poster. Nogle tillader ikke self-promotion eller kræver specifikke formater.

---

## ✅ TRIN 5 — HACKER NEWS

**Hvorfor:** Tech-éliten læser HN. Silent patching historier gør det ofte til frontpage.

- [ ] Gå til https://news.ycombinator.com/submit
- [ ] Title:
  > Ollama silently patched a model identity leak in v0.30.7 without issuing a CVE or advisory
- [ ] URL: dit blog-indlæg eller GitHub repo
- [ ] **Timing:** Post mellem 9-11 EST (15-17 dansk tid) mandag-fredag
- [ ] Vær aktiv i kommentarer — svar på spørgsmål, tilføj tekniske details
- [ ] **IKKE** bed om upvotes (det er imod reglerne og giver downvotes)

---

## ✅ TRIN 6 — GITHUB SECURITY ADVISORY

**Hvorfor:** Formel responsible disclosure. Selvom Ollama ignorerer, viser det god tro.

- [ ] Gå til https://github.com/ollama/ollama/security/advisories/new
- [ ] Brug `ghsa/advisories.md` som skabelon
- [ ] Submit for hver CVE:
  - CVE-2026-5757 (GGUF Memory Leak — UNPATCHED)
  - CVE-2026-5530 (SSRF skipVerify — UNPATCHED)
  - CVE-2026-7482 (Bleeding Llama — patched silently)
  - CVE-2026-42248/42249 (Update RCE — patched silently)
- [ ] **Bemærk:** Ollama har track record med at ignorere GHSA (issue #15262). Hvis ingen reaktion efter 7 dage, gå public.

---

## ✅ TRIN 7 — KONTAKT JOURNALISTER & FORSKERE

**Hvorfor:** Mediedækning giver historien ben at gå på.

Fra `media_contacts.md`, kontakt disse PRIORITERET:

### Højeste prioritet:
1. **Kai Greshake** (@KGreshake) — PromptArmor. Har allerede researchet Ollama. DM på Twitter eller email via NVIDIA.
2. **Bartłomiej Dmitruk** — Striga.ai. Co-credited på CVE-2026-42248/42249. Direkte interesse.
3. **Cyera Security Research Team** — Offentliggjorde CVE-2026-5757. Allerede i historien.

### Medium prioritet:
4. **Bruce Schneier** (@schneierblog) — Krypto/security legend
5. **Brian Krebs** (@briankrebs) — Krebs on Security
6. **The Record** (@TheRecord_Media) — Cybersecurity nyheder

### CERT:
7. **CERT Polska** — Allerede involveret i CVE-2026-42248/42249
8. **Danish CERT (DK-CERT)** — Nationalt CERT, relevant da du er dansk forsker

- [ ] Send kort email/DM til top 3 med:
  - Emne: "Ollama silent patching disclosure — 7 vulns, 0 CVEs, researcher suppression"
  - Link til blog post
  - Link til GitHub repo
  - Tilbud om eksklusiv kommentar/bevis

---

## ✅ TRIN 8 — HUNTR / BUG BOUNTY PLATFORMS

**Hvorfor:** Huntr er THE bug bounty platform for AI open source.

- [ ] Tjek om Ollama er på Huntr: https://huntr.com/bounties
- [ ] Submit CVE-2026-5757 hvis mulig
- [ ] Submit CVE-2026-5530 hvis mulig
- [ ] Submit OMP auth:none (ny finding fra v0.30.6)
- [ ] Submit PI_CONFIG_DIR path traversal (ny finding fra v0.30.6)

---

## ✅ TRIN 9 — OPDATER EFTER PUBLIKATION

- [ ] Monitor Reddit kommentarer — svar på alle
- [ ] Monitor HN kommentarer — svar teknisk, ikke defensivt
- [ ] Monitor Twitter for retweets og mentions
- [ ] Hvis Ollama svarer — dokumenter alt i timeline
- [ ] Hvis nye opdateringer/releases — analyser dem (ny silent patch?)
- [ ] Opdater GitHub repo med nye findings
- [ ] Opdater blog post med "UPDATE" sektion hvis historien udvikler sig

---

## ⚠️ VIGTIGT — OPSEC & SIKKERHED

- [ ] IKKE brug dit rigtige navn hvis du vil være anonym
- [ ] IKKE nævn admin_user username i offentlige filer
- [ ] IKKE leak din rigtige IP i screenshots, logs, eller JSON
- [ ] Slet browser cache, DNS cache, bash history efter hver session
- [ ] Brug en anonym GitHub konto hvis nødvendigt
- [ ] Tjek alle filer for personlige data før upload til GitHub
- [ ] Kør: `grep -r "admin_user" ~/Desktop/KAMPAGNE/` — fjern alle hits
- [ ] Kør: `grep -r "admin_user" ~/Desktop/ollama_disclosure_2026/` — fjern alle hits

---

## 📊 RÆKKEFØLGE (OPTIMAL TIMING)

| Tidspunkt | Handling | Platform |
|------------|----------|----------|
| Dag 1, 09:00 | Opret GitHub repo | GitHub |
| Dag 1, 10:00 | Publisér blog post | Medium |
| Dag 1, 10:30 | Post Twitter thread | X/Twitter |
| Dag 1, 11:00 | Post r/LocalLLaMA | Reddit |
| Dag 1, 12:00 | Post r/netsec | Reddit |
| Dag 1, 12:30 | Post r/cybersecurity | Reddit |
| Dag 1, 13:00 | Post r/ollama | Reddit |
| Dag 1, 15:00 | Submit Hacker News | HN |
| Dag 1, 15:00 | Email top 3 forskere | Email |
| Dag 2 | Submit GHSA advisories | GitHub Security |
| Dag 2 | Submit Huntr bounties | Huntr |
| Dag 2-7 | Monitor & respond | Alle |

---

## 🎯 SUCCESKRITERIER

| Metric | Target |
|--------|--------|
| Reddit karma (r/LocalLLaMA) | 500+ upvotes |
| Hacker News | 200+ upvotes |
| Twitter views | 50,000+ |
| GitHub repo stjerner | 100+ |
| Mediedækning | 2+ artikler |
| Ollama reaktion | Respon(s) inden 7 dage |

---

**Alt er klar. Alt er skrevet. Alt er verificeret. Publiseringen er alt hvad der mangler. 🚀**