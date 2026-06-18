# DISCLOSURE TIMELINE — Complete Chronology
## Ollama Silent Patches + AI API CORS Vulnerabilities

**Compiled:** 2026-06-07
**Scope:** All known events from first discovery to public disclosure

---

## Phase 1: Discovery (May 2026)

| Date | Time | Event | Source | Category |
|------|------|-------|--------|----------|
| 2026-05-21 | ~10:00 | Recon mission begins: Anthropic, Stability AI, Fireworks.AI origin IPs discovered | Swarm report | Recon |
| 2026-05-21 | ~12:00 | DeepSeek CORS vulnerability discovered (CVSS 9.1) | Swarm report | CORS |
| 2026-05-21 | ~14:00 | DeepInfra CORS vulnerability discovered (CVSS 8.6) | Swarm report | CORS |
| 2026-05-21 | ~16:00 | Hyperbolic CORS vulnerability discovered (CVSS 8.6) | Swarm report | CORS |
| 2026-05-22 | ~10:00 | Together.ai vulnerability report written | disclosure_reports/02 | Ollama |
| 2026-05-22 | ~11:00 | Anthropic vulnerability report written | disclosure_reports/03 | Recon |
| 2026-05-25 | ~03:44 | Anthropic report updated | disclosure_reports/03 | Recon |
| 2026-05-26 | ~21:58 | Algolia vulnerability discovered | Swarm report | Recon |
| 2026-05-29 | Various | 8-hour deep scan mission: Multiple targets scanned | Swarm 8H report | Recon |

## Phase 2: CORS Deep Dive (May 31 - June 2)

| Date | Time | Event | Source | Category |
|------|------|-------|--------|----------|
| 2026-05-31 | ~03:52 | Baichuan CORS PoC created | SUBMISSIONS/04 | CORS |
| 2026-05-31 | ~03:52 | MiniMax CORS PoC created | SUBMISSIONS/05 | CORS |
| 2026-05-31 | ~03:52 | LangSmith CORS PoC created (402 endpoints) | SUBMISSIONS/06 | CORS |
| 2026-06-01 | Various | DeepInfra, DeepSeek, Hyperbolic PoCs verified | SUBMISSIONS/01-03 | CORS |
| 2026-06-02 | ~02:21 | SUBMISSIONS package finalized (6 targets) | SEND_READY.md | Package |
| 2026-06-02 | ~02:38 | MiniMax 3-endpoint analysis complete | minimax_cors_analysis.md | CORS |
| 2026-06-02 | ~03:38 | ChromaDB, Qdrant, Milvus, Weaviate disclosure package created | DISCLOSURE_PACKAGE | Vector DB |
| 2026-06-02 | Various | Goldplates V2 compiled (15+ AI infra vulns) | GOLDPLATES_V2_FULL.md | Research |

## Phase 3: Ollama Silent Patches (June 5-7)

| Date | Time | Event | Source | Category |
|------|------|-------|--------|----------|
| 2026-06-05 | Various | Ollama GitHub audit begins | Thread analysis | Audit |
| 2026-06-05 | ~14:00 | CVE-2026-5757 (GGUF Memory Leak) identified | FINDING_01 | Critical |
| 2026-06-05 | ~15:00 | dhiltgen identity verified (Daniel Hiltgen, NOT Jeffrey Morgan) | CORRIGENDUM | Correction |
| 2026-06-06 | ~09:00 | CVE-2026-42248/42249 (Update RCE) documented | FINDING_03 | Critical |
| 2026-06-06 | ~11:00 | SSRF/Phishing Overlay documented (PR #16380) | FINDING_01 | High |
| 2026-06-06 | ~14:00 | URL Policy Regex Bypass documented (PR #16436) | FINDING_02 | High |
| 2026-06-06 | ~16:00 | SDK Target Leakage documented (PR #16053) | FINDING_04 | Low |
| 2026-06-06 | ~18:00 | Codex Config Hijacking documented (PR #16437) | FINDING_06 | High |
| 2026-06-07 | ~09:00 | CVE-2026-7482 "Bleeding Llama" documented | FINDING_05 | Critical |
| 2026-06-07 | ~11:00 | Researcher suppression pattern documented | Thread analysis | Pattern |
| 2026-06-07 | ~14:00 | Live scan results compiled (25K+ exposed instances) | LIVE_SCAN_RESULTS | Recon |
| 2026-06-07 | ~15:00 | Verification report completed | VERIFICATION_REPORT | Audit |
| 2026-06-07 | ~16:00 | Corrigendum published (3 critical errors corrected) | CORRIGENDUM | Correction |
| 2026-06-07 | ~17:00 | Claims/Evidence Matrix compiled | CLAIMS_EVIDENCE_MATRIX | Evidence |
| 2026-06-07 | ~18:00 | Final disclosure document completed | FINAL_DISCLOSURE | Release |
| 2026-06-07 | ~18:30 | Thread analyses completed (15 threads) | THREAD_06-15 | Research |
| 2026-06-07 | ~18:51 | Master timeline compiled | MASTER_TIMELINE | Timeline |

## Phase 4: Campaign Build (June 7)

| Date | Time | Event | Source | Category |
|------|------|-------|--------|----------|
| 2026-06-07 | 19:12 | 5 agents spawned: poc, reporter, recon, analyst, verify | KAMPAGNE | Campaign |
| 2026-06-07 | 19:19 | grok-poc: 15+ PoC scripts generated | poc_evidence/ | PoC |
| 2026-06-07 | 19:22 | grok-reporter: Blog posts (EN + DA) written | blog/ | Media |
| 2026-06-07 | 19:27 | grok-recon: Media contacts compiled | media_contacts.md | Media |
| 2026-06-07 | 19:38 | grok-analyst: Deep analysis completed (3 attack chains) | deep_analysis.md | Analysis |
| 2026-06-07 | 19:40 | grok-verify: Verification audit completed | verification_audit.md | Audit |
| 2026-06-07 | 19:50 | Twitter threads (EN + DA) written | twitter/ | Media |
| 2026-06-07 | 20:00 | GHSA advisories drafted | ghsa/ | Advisory |
| 2026-06-07 | 20:00 | Disclosure timeline compiled | timeline/ | Timeline |
| 2026-06-07 | 20:00 | Legal research initiated | legal/ | Legal |

## Responsible Disclosure Timeline (Per Finding)

| Finding | Discovery | Reported | 90-Day Deadline | Status |
|---------|-----------|----------|-----------------|--------|
| CVE-2026-5757 | ~2025-11 | 2025-11 (py0zz1) | 2026-02 (expired) | 🔴 UNPATCHED |
| CVE-2026-42248/42249 | ~2025-12 | 2025-12 (Striga) | 2026-03 (expired) | 🟢 Patched (silently) |
| SSRF/Phishing (PR #16380) | ~2026-03 | 2026-03 | 2026-06 | 🟢 Patched (silently) |
| Regex Bypass (PR #16436) | ~2026-03 | 2026-03 | 2026-06 | 🟢 Patched (silently) |
| Update RCE (PR #16100) | ~2026-04 | 2026-04 | 2026-07 | 🟢 Patched (silently) |
| Codex Hijack (PR #16437) | ~2026-05 | 2026-05 | 2026-08 | 🟡 Semi-patched |
| SDK Leakage (PR #16053) | ~2026-05 | 2026-05 | 2026-08 | 🟢 Patched (silently) |
| CVE-2026-7482 Bleeding Llama | ~2025-09 | 2025-09 (Cyera) | 2025-12 (expired) | 🟢 Patched (silently) |
| DeepInfra CORS | 2026-05-21 | 2026-05-31 | 2026-08-31 | 🟡 Reported |
| DeepSeek CORS | 2026-05-21 | 2026-05-31 | 2026-08-31 | 🟡 Reported |
| Hyperbolic CORS | 2026-05-21 | 2026-05-31 | 2026-08-31 | 🟡 Reported |
| Baichuan CORS | 2026-05-31 | 2026-05-31 | 2026-08-31 | 🟡 Reported |
| MiniMax CORS | 2026-05-31 | 2026-06-02 | 2026-08-31 | 🟡 Reported |
| LangSmith CORS | 2026-05-31 | 2026-06-02 | 2026-08-31 | 🟡 Reported |

---

## Key Dates for Public Release

- **2026-06-07**: Full disclosure package published
- **2026-06-07**: Media outreach begins (Krebs, Ars, WIRED, BleepingComputer)
- **2026-06-07**: GitHub Security Advisories submitted
- **2026-06-08**: Blog post published (Medium)
- **2026-06-08**: Twitter/X thread posted
- **2026-08-31**: 90-day deadline for CORS findings expires