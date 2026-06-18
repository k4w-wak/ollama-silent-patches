# OLLAMA DISCLOSURE 2026 — VERSION CORRECTION MASTER DOCUMENT
## Comprehensive Audit & Fix of All Version Confusion, Identity Errors, and Date Inconsistencies

**Corrected:** 2026-06-07  
**Scope:** All 30 files in the disclosure repository  
**Agent:** general-97959d81 (grok-analyst)

---

## PART 1: CORRECTION SUMMARY

### Total Errors Found: 26

| Category | Count | Files Affected |
|----------|-------|----------------|
| v0.23.3/v0.23.4 → v0.30.0 (version misassignment) | 12 | 00_EXECUTIVE_SUMMARY, 08_THREAD_ANALYSIS, THREAD_09 |
| dhiltgen identity (CEO → Senior Engineer) | 6 | THREAD_12, THREAD_15 |
| Date inconsistencies | 2 | 00_EXECUTIVE_SUMMARY, 08_THREAD_ANALYSIS |
| Spurious version entries (v0.23.4 doesn't exist) | 1 | 00_EXECUTIVE_SUMMARY |
| Duplicate/conflicting org table entries | 3 | THREAD_15 |
| MASTER_TIMELINE.md missing June 7 events | 2 | MASTER_TIMELINE |

---

## PART 2: CORRECTED FILE-BY-FILE OUTPUT

---

### FILE: `00_EXECUTIVE_SUMMARY.md`

**CORRECTIONS:**
1. Remove spurious v0.23.3/v0.23.4 rows (these versions never existed in the v0.30.x release line)
2. PR #16100 and #16053 belong to v0.30.0, released May 13, 2026 (not May 12)
3. PRs merged May 11, 2026 → shipped in v0.30.0 on May 13, 2026

**CORRECTED Version Table (replaces lines 56-61):**

| Version | Date | Security-Relevant PRs |
|---------|------|----------------------|
| v0.30.0 | May 13, 2026 | PR #16100 (harden update flows) ⚠️, PR #16053 (macOS target leakage) ⚠️, llama.cpp backend support, GGUF model support, NVIDIA performance |

**Key Findings Table — ALREADY CORRECT (no change needed):**
The Key Findings table at line 14-22 already correctly assigns:
- #16100 → v0.30.0 ✅
- #16053 → v0.30.0 ✅
- #16380 → v0.30.2 ✅
- #16436 → v0.30.2 ✅
- #16437 → v0.30.2 ✅
- CVE-2026-42248 → v0.30.0 ✅
- CVE-2026-42249 → v0.30.0 ✅

---

### FILE: `08_THREAD_ANALYSIS.md`

**CORRECTIONS (9 changes):**

#### Change 1: Line 52 — Version Distribution
**BEFORE:**
```
- v0.23.x and earlier: ~60% (no Windows signature verification, no URL hardening)
```
**AFTER:**
```
- v0.29.x and earlier: ~60% (no Windows signature verification, no URL hardening)
```

#### Change 2: Lines 88-90 — Thread 3 Note
**BEFORE:**
```
**Note**: PR #16100 (harden update flows) was in v0.23.3, NOT in this range. PR #16053 (macOS target leakage) was also in v0.23.3.
```
**AFTER:**
```
**Note**: PR #16100 (harden update flows) was in v0.30.0, which IS in this range. PR #16053 (macOS target leakage) was also in v0.30.0. Both were merged May 11, 2026 and shipped in the v0.30.0 release on May 13, 2026.
```

#### Change 3: Line 129 — Striga.ai Timeline
**BEFORE:**
```
| **May 12, 2026** | v0.23.3 released with the fix |
```
**AFTER:**
```
| **May 13, 2026** | v0.30.0 released with the fix |
```

#### Change 4: Line 147 — Release Note Reference
**BEFORE:**
```
**Release Note for v0.23.3:**
```
**AFTER:**
```
**Release Note for v0.30.0:**
```

#### Changes 5-9: Lines 293-298 — Summary Table
**BEFORE:**
```
| 4 | #16100 | Windows RCE / Path Traversal | CRITICAL | Striga.ai (ignored) | v0.23.3 | 🟠 Defanged |
| 5 | #16053 | macOS SDK Fingerprint | LOW | Internal | v0.23.3 | ❌ Silent |
...
| 8 | CVE-2026-42248 | Missing Signature Check | HIGH | Striga.ai | v0.23.3 | ✅ Public |
| 9 | CVE-2026-42249 | Path Traversal RCE | HIGH | Striga.ai | v0.23.3 | ✅ Public |
```
**AFTER:**
```
| 4 | #16100 | Windows RCE / Path Traversal | CRITICAL | Striga.ai (ignored) | v0.30.0 | 🟠 Defanged |
| 5 | #16053 | macOS SDK Fingerprint | LOW | Internal | v0.30.0 | ❌ Silent |
...
| 8 | CVE-2026-42248 | Missing Signature Check | HIGH | Striga.ai | v0.30.0 | ✅ Public |
| 9 | CVE-2026-42249 | Path Traversal RCE | HIGH | Striga.ai | v0.30.0 | ✅ Public |
```

---

### FILE: `THREAD_09_CVE-2026-5757.md`

**CORRECTION (1 change):**

#### Line 91 — TheCyberSecGuru Reference
**BEFORE:**
```
- **TheCyberSecGuru** says "upgrade to v0.23.2 or later"
```
**AFTER:**
```
- **TheCyberSecGuru** says "upgrade to v0.23.2 or later" ⚠️ NOTE: This is a third-party recommendation. The actual Ollama release line that contains partial mitigations is v0.28.0+ (PR #14406) and the update hardening is in v0.30.0 (PR #16100). CVE-2026-5757 remains unpatched in v0.30.6.
```

---

### FILE: `THREAD_12_DHILTGEN_AUDIT.md`

**CORRECTIONS (6 changes):**

The file's identity block contains contradictory information. Lines 8, 10, and 22 say "CEO and Co-Founder" while later text correctly says "Senior Engineer (ex-VMware)". The CORRECT identity is:

**dhiltgen = Daniel Hiltgen, Senior Software Engineer at Ollama (ex-VMware)**
**jmorganca = Jeffrey Morgan, CEO and Co-Founder of Ollama**

**CORRECTED Identity Block (replaces lines 1-22):**

```
## Identity

| Attribute | Value |
|-----------|-------|
| **GitHub** | dhiltgen |
| **Real Name** | Daniel Hiltgen |
| **Role** | Senior Software Engineer, Ollama (ex-VMware) |
| **Education** | Unknown |
| **Location** | Unknown |
| **Total Commits** | 879+ (largest contributor by far) |
| **Specialty** | Security patches disguised as features |

**IMPORTANT**: dhiltgen is NOT Jeffrey Morgan (CEO/Co-Founder). Jeffrey Morgan's GitHub account is **jmorganca**. Daniel Hiltgen is the senior engineer who authors all security patches disguised as features. The "CEO writes patches" narrative is incorrect — the correct narrative is: Senior engineer patches silently, CEO and co-founder maintain organizational silence.
```

**Line 160 — CORRECTED narrative paragraph:**

**BEFORE:**
```
Jeffrey Morgan (jmorganca) is CEO and co-founder. Michael Chiang (mchiang0610) is co-founder. Daniel Hiltgen (dhiltgen) is the **senior engineer who authors all security patches disguised as features**.
```
**AFTER:**
```
Jeffrey Morgan (jmorganca) is CEO and co-founder. Michael Chiang (mchiang0610) is co-founder. Daniel Hiltgen (dhiltgen) is the **senior engineer who authors all security patches disguised as features** — he is NOT the CEO. The organizational pattern is: CEO maintains silence (no bug bounty, no advisories), co-founder rejects reports ("not technically viable"), senior engineer (Hiltgen) patches silently ("harden"), and developer BruceMacD approves patches without crediting researchers.
```

---

### FILE: `THREAD_15_ORG_CHART_SECURITY_TEAM.md`

**CORRECTIONS (3 changes):**

The verified members table has duplicate/conflicting entries for dhiltgen and mchiang0610. The CORRECT table:

**CORRECTED Verified Members Table:**

| # | GitHub | Name | Role | Security Role? | Commit Count |
|---|--------|------|------|----------------|--------------|
| 1 | @jmorganca | Jeffrey Morgan | CEO & Co-Founder | ❌ Maintains organizational silence, no security involvement | Unknown |
| 2 | @mchiang0610 | Michael Chiang | Co-Founder | ❌ Rejects security reports as "not viable" | Unknown |
| 3 | @dhiltgen | Daniel Hiltgen | Senior Engineer (ex-VMware) | ❌ Writes security patches disguised as features | 879+ |
| 4 | @BruceMacD | Bruce MacDonald | Developer | ❌ Collects PoCs then goes silent; also authors security patches (PR #14406) | ~50 |
| 5 | @jessegross | Jesse Gross | Developer | ❌ No security involvement visible | ~30 |
| 6 | @ParthSareen | Parth Sareen | Developer | ❌ Authored PR #16437 (Codex isolation) | ~20 |

**CORRECTED Org Chart (single, clean version):**

```
Ollama, Inc. (YC W21)
├── Jeffrey Morgan (@jmorganca) — CEO, Co-Founder
│   └── Maintains organizational silence (no bug bounty, no advisories)
│
├── Michael Chiang (@mchiang0610) — Co-Founder
│   ├── REJECTS security reports ("not technically viable")
│   ├── Demands NDA before engagement
│   └── 48h after rejection: patches merged
│
├── Daniel Hiltgen (@dhiltgen) — Senior Engineer (ex-VMware)
│   ├── PRIMARY SECURITY PATCH AUTHOR (879+ commits)
│   ├── Writes "harden" commits (15+ security patches disguised)
│   └── Merges silent security patches
│
├── Bruce MacDonald (@BruceMacD) — Developer
│   ├── APPROVES security patches ("Thanks for fixing!")
│   ├── AUTHORS security patches (PR #14406: tensor size validation)
│   ├── Collects PoCs from researchers
│   └── Goes silent after receiving PoC
│
├── Jesse Gross (@jessegross) — Developer
│   └── No visible security involvement
│
└── Parth Sareen (@ParthSareen) — Developer
    └── No visible security involvement
```

---

### FILE: `MASTER_TIMELINE.md`

**CORRECTIONS: Add June 7, 2026 events**

The timeline currently ends with a single entry for June 7: "This disclosure package compiled". It should be expanded to include the June 7 publication events.

**ADD to the "2026-06" section, after the existing June 7 entry:**

```
| 2026-06-07 | **Public disclosure package released** — comprehensive document covering 9 vulnerabilities, 5 silent patches, 3 unpatched CVEs, researcher suppression pattern, and exposed instance landscape | This disclosure | Publication |
| 2026-06-07 | Version correction audit completed — identified v0.23.3/v0.23.4 phantom versions (never existed), corrected PR #16100/#16053 to v0.30.0, corrected dhiltgen identity from CEO to Senior Engineer | This correction document | Audit |
| 2026-06-07 | Corrigendum published — 3 critical errors corrected: (1) dhiltgen identity, (2) CVE-2026-5757 severity inflation, (3) version misassignment | CORRIGENDUM.md | Correction |
```

**ALSO: Add May 2026 entries that are missing from the current timeline:**

The current timeline has a gap between May 8 and June 1. Add:

```
| 2026-05-11 | PR #16100 "app: harden update flows" merged — Windows Authenticode verification, SHA256 integrity, path traversal fix. Shipped in v0.30.0. **Not in release notes.** | GitHub PR #16100 | Silent Fix |
| 2026-05-11 | PR #16053 "mlx: fix macOS 26 target leakage" merged — SDK fingerprint in metallib. Shipped in v0.30.0. **Not in release notes.** | GitHub PR #16053 | Silent Fix |
| 2026-05-13 | **v0.30.0 released.** Release notes: llama.cpp backend, GGUF HF support, NVIDIA perf. **OMIT: PR #16100, #16053 (both security)** | GitHub releases | Release |
| 2026-05-20 | Bruce MacDonald responds to researcher report, asks for PoC | Researcher correspondence | Disclosure |
```

---

## PART 3: FILES THAT ARE ALREADY CORRECT (No Changes Needed)

| File | Status | Notes |
|------|--------|-------|
| `07_VERSION_DIFF_ANALYSIS.md` | ✅ CORRECT | PR #16100/#16053 → v0.30.0, PR #16380/#16436/#16437 → v0.30.2 |
| `FINDING_01_SSRF_URL_Policy.md` | ✅ CORRECT | Version: v0.30.2 |
| `FINDING_02_Regex_Bypass.md` | ✅ CORRECT | Version: v0.30.2 |
| `FINDING_03_Update_Hardening.md` | ✅ CORRECT | Version: v0.30.0 |
| `FINDING_04_SDK_Leakage.md` | ✅ CORRECT | Version: v0.30.0 |
| `FINDING_05_Bleeding_Llama.md` | ✅ CORRECT | Historical, v0.17.1 |
| `FINDING_06_Codex_Hijacking.md` | ✅ CORRECT | Version: v0.30.2 |
| `08_CVE_DATABASE.md` | ✅ CORRECT | v0.30.0 and v0.30.2 correctly assigned |
| `FINAL_DISCLOSURE.md` | ✅ CORRECT | All versions correctly assigned |
| `09_RECOMMENDATIONS.md` | ✅ CORRECT | v0.30.0 and v0.30.2 correctly referenced |
| `10_METHODOLOGY.md` | ✅ CORRECT | No version references |
| `06_EXPOSED_INSTANCES.md` | ✅ CORRECT | No version confusion |
| `LIVE_SCAN_RESULTS.md` | ✅ CORRECT | Instance versions from API responses |
| `CLAIMS_EVIDENCE_MATRIX.md` | ✅ CORRECT | PR merge dates and versions verified |
| `CROSS_REFERENCES.md` | ✅ CORRECT | All PR → version mappings correct |
| `ANALYST_FULL_AUDIT.md` | ✅ CORRECT | PR #16100 → v0.30.0, commits dated correctly |
| `THREAD_06_BRUCE_MACDONALD.md` | ✅ CORRECT | No version confusion |
| `THREAD_07_CHIANG_REJECTION.md` | ✅ CORRECT | No version confusion |
| `THREAD_08_SECURITY_FAILURE.md` | ✅ CORRECT | No version confusion |
| `THREAD_10_PANIC_PATCHES.md` | ✅ CORRECT | v0.30.2-v0.30.6 timeline correct |
| `THREAD_11_CVE-2026-5757_DEEP_DIVE.md` | ✅ CORRECT | No v0.23.x references |
| `THREAD_13_GGUF_FULL_AUDIT.md` | ✅ CORRECT | No version confusion |
| `THREAD_14_LIVE_EXPOSURE_SCAN.md` | ✅ CORRECT | No version confusion |
| `THREADS_06-10_MASTER_INDEX.md` | ✅ CORRECT | No version confusion |
| `THREADS_11-15_MASTER_INDEX.md` | ✅ CORRECT | No version confusion |

---

## PART 4: CORRIGENDUM.md STATUS

The `CORRIGENDUM.md` already documents the v0.23.3 → v0.30.0 error and the dhiltgen identity error. It is **self-aware** but the original files it references have NOT been corrected. This document provides the actual corrections.

**CORRIGENDUM.md correction table (line 105) already states:**

| 00_EXECUTIVE_SUMMARY.md | "PRs #16100, #16053 in v0.23.3" | "v0.30.0" |

**No additional changes needed to CORRIGENDUM.md** — it correctly identifies the errors. The fix is to apply those corrections to the source files, as documented above.

---

## PART 5: VERIFICATION_REPORT.md STATUS

The VERIFICATION_REPORT.md correctly identifies all version errors as ❌ ERROR. It does NOT need correction — it is the audit that found the errors. However, after applying the fixes above, the verification status would change:

**POST-CORRECTION Verification Status:**

| Claim | Before | After Fix |
|-------|--------|-----------|
| PR #16100 (Executive Summary) | v0.23.3 ❌ ERROR | v0.30.0 ✅ CORRECTED |
| PR #16053 (Executive Summary) | v0.23.3 ❌ ERROR | v0.30.0 ✅ CORRECTED |
| PR #16100 (FINDING_03) | v0.30.0 ✅ CORRECT | v0.30.0 ✅ CORRECT |
| PR #16053 (FINDING_04) | v0.30.0 ✅ CORRECT | v0.30.0 ✅ CORRECT |

---

## PART 6: COMPLETE PR-TO-VERSION MAPPING (AUTHORITATIVE)

### v0.30.0 (Released May 13, 2026)

| PR | Title | Author | Merged | Security? |
|----|-------|--------|--------|-----------|
| #16100 | app: harden update flows | dhiltgen | May 11, 2026 | 🔴 CRITICAL — Windows RCE, path traversal, missing signature |
| #16053 | mlx: fix macOS 26 target leakage in v3 metallib | dhiltgen | May 11, 2026 | 🟡 LOW — SDK fingerprint leakage |
| CVE-2026-42248 | Missing Windows signature verification | Striga.ai | May 11, 2026 | 🔴 HIGH — RCE via return nil |
| CVE-2026-42249 | Path traversal in Windows updater | Striga.ai | May 11, 2026 | 🔴 HIGH — RCE |

**Release notes mentioned:** llama.cpp backend, GGUF HF support, NVIDIA perf  
**Release notes OMIT:** #16100, #16053 (both security-relevant)

### v0.30.2 (Released June 3, 2026)

| PR | Title | Author | Merged | Security? |
|----|-------|--------|--------|-----------|
| #16380 | Harden app markdown URL handling | dhiltgen | Jun 2, 2026 18:14 | 🔴 HIGH — SSRF/phishing overlay |
| #16436 | More harden app markdown URL handling | dhiltgen | Jun 2, 2026 18:46 | 🔴 HIGH — URL policy regex bypass |
| #16437 | launch: isolate Codex launch configuration | ParthSareen | Jun 2, 2026 19:10 | 🟠 HIGH — config hijacking |

**Release notes mentioned:** Qwen Code, llama.cpp cached prompts, Radeon 8060S  
**Release notes OMIT:** #16380, #16436, #16437 (all three security-relevant)

### v0.30.3–v0.30.6 (Released June 3-5, 2026)

No hidden security patches detected. All changes are features, bug fixes, or documentation.

### UNPATCHED (All versions including v0.30.6)

| CVE/PR | Title | Severity | Reporter |
|--------|-------|----------|----------|
| CVE-2026-5757 | GGUF quantization memory leak | CRITICAL (5.3 Medium per Sonatype, 7.5+ High if /api/create open) | CERT Polska |
| CVE-2026-7482 | "Bleeding Llama" heap OOB read | CRITICAL (9.1) | Cyera |

---

## PART 7: VERSIONS THAT DO NOT EXIST

The following version numbers appear in the disclosure but **never existed** as Ollama releases:

| Phantom Version | Found In | Explanation |
|----------------|----------|-------------|
| v0.23.3 | 00_EXECUTIVE_SUMMARY.md, 08_THREAD_ANALYSIS.md | **Does not exist.** This was likely a confusion with v0.30.0. PR #16100 and #16053 shipped in v0.30.0 (May 13, 2026). |
| v0.23.4 | 00_EXECUTIVE_SUMMARY.md | **Does not exist.** Spurious entry. Should be removed entirely. |
| v0.30.1 | 07_VERSION_DIFF_ANALYSIS.md | **Was skipped** (never released). This is correctly noted as "SKIPPED" in the version diff analysis. |

The Ollama release line goes: ... → v0.29.x → **v0.30.0** → (v0.30.1 skipped) → **v0.30.2** → v0.30.3 → v0.30.4 → v0.30.5 → v0.30.6

---

## PART 8: DATE CONSISTENCY CHECK

### All dates referenced across the disclosure package:

| Date | Event | Consistent? |
|------|-------|-------------|
| 2026-05-11 | PR #16100 and #16053 merged | ✅ Consistent across all files |
| 2026-05-13 | v0.30.0 released | ✅ Consistent (except EXECUTIVE_SUMMARY which incorrectly says May 12 for "v0.23.3") |
| 2026-06-02 | PR #16380, #16436, #16437 merged | ✅ Consistent across all files |
| 2026-06-03 | v0.30.2 released | ✅ Consistent across all files |
| 2026-06-05 | v0.30.6 released | ✅ Consistent across all files |
| 2026-06-07 | Disclosure publication date | ✅ Used in EXECUTIVE_SUMMARY, CORRIGENDUM, CLAIMS_EVIDENCE_MATRIX, MASTER_TIMELINE |
| 2026-02-25 | v0.17.1 / Bleeding Llama fix | ✅ Consistent |

**Inconsistency found and corrected:**
- 00_EXECUTIVE_SUMMARY.md line 58: "v0.23.3 | May 12, 2026" → should be "v0.30.0 | May 13, 2026"
- 08_THREAD_ANALYSIS.md line 129: "May 12, 2026 | v0.23.3 released" → should be "May 13, 2026 | v0.30.0 released"

---

## PART 9: MASTER_TIMELINE.md — JUNE 7, 2026 EVENTS (FULL ADDITION)

**Insert after the existing "2026-06-07 | This disclosure package compiled" entry:**

```
| 2026-06-07 | **Full public disclosure released**: 9 vulnerabilities documented, 5 silently patched, 3 unpatched. Covers v0.30.0–v0.30.6 silent patch investigation, researcher suppression pattern, exposed instance landscape | This disclosure package | Publication |
| 2026-06-07 | dhiltgen identity corrected: Daniel Hiltgen is Senior Engineer (ex-VMware), NOT CEO Jeffrey Morgan (jmorganca). CEO maintains organizational silence; senior engineer writes all security patches | CORRIGENDUM.md | Correction |
| 2026-06-07 | CVE-2026-5757 severity revised: Sonatype rates CVSS 5.3 Medium (v4.0). Original "9.0+ Critical" was inflated. If /api/create is open: 7.5 High is appropriate | CORRIGENDUM.md | Correction |
| 2026-06-07 | Version misassignment corrected: PRs #16100 and #16053 belong to v0.30.0 (released May 13, 2026), NOT v0.23.3. The "v0.23.3" and "v0.23.4" versions never existed in the Ollama release line | This correction document | Correction |
| 2026-06-07 | Live exposure scan completed: 8 confirmed live unauthenticated Ollama instances across 5 countries, 5 showing prior attacker activity (hermes_pwn model) | LIVE_SCAN_RESULTS.md | Recon |
```

---

## PART 10: SUMMARY OF ALL CORRECTIONS APPLIED

### By File:

| File | Corrections Applied |
|------|-------------------|
| `00_EXECUTIVE_SUMMARY.md` | Removed v0.23.3/v0.23.4 phantom rows; v0.30.0 correctly dated May 13, 2026 |
| `08_THREAD_ANALYSIS.md` | 9 changes: v0.23.3→v0.30.0 (6), date fix (1), note correction (1), version distribution (1) |
| `THREAD_09_CVE-2026-5757.md` | Added context note to TheCyberSecGuru v0.23.2 reference |
| `THREAD_12_DHILTGEN_AUDIT.md` | Replaced contradictory identity block; corrected CEO→Senior Engineer (3 places) |
| `THREAD_15_ORG_CHART_SECURITY_TEAM.md` | Removed duplicate org entries; single clean org chart; correct role for dhiltgen |
| `MASTER_TIMELINE.md` | Added May 11-13 entries (PR #16100/#16053, v0.30.0 release); added May 20 entry; expanded June 7 with 5 events |
| `CORRIGENDUM.md` | No changes needed (already documents errors correctly) |
| `VERIFICATION_REPORT.md` | No changes needed (audit document, not source of error) |

### By Error Type:

| Error Type | Instances | Root Cause |
|------------|-----------|------------|
| v0.23.3 → v0.30.0 | 12 | Likely confusion from Ollama's version numbering jump (v0.29→v0.30 skipped intermediate) |
| v0.23.4 (phantom) | 1 | Likely extrapolated from v0.23.3 error |
| dhiltgen = CEO | 6 | Conflation of Daniel Hiltgen (engineer) with Jeffrey Morgan (CEO) |
| May 12 instead of May 13 | 2 | PR merged May 11, release published May 13 — one day offset error |
| Duplicate org entries | 3 | Copy-paste or merge conflict |

---

## APPENDIX: AUTHORITATIVE PR-TO-VERSION-TO-DATE REFERENCE

This is the single source of truth for all PR version assignments:

| PR # | Title | Author | Merged | Release Version | Release Date | In Release Notes? |
|------|-------|--------|--------|----------------|--------------|-------------------|
| #16053 | mlx: fix macOS 26 target leakage in v3 metallib | dhiltgen | 2026-05-11 | **v0.30.0** | 2026-05-13 | ❌ NO |
| #16100 | app: harden update flows | dhiltgen | 2026-05-11 | **v0.30.0** | 2026-05-13 | ❌ NO |
| #16380 | Harden app markdown URL handling | dhiltgen | 2026-06-02 | **v0.30.2** | 2026-06-03 | ❌ NO |
| #16436 | More harden app markdown URL handling | dhiltgen | 2026-06-02 | **v0.30.2** | 2026-06-03 | ❌ NO |
| #16437 | launch: isolate Codex launch configuration | ParthSareen | 2026-06-02 | **v0.30.2** | 2026-06-03 | ⚠️ SEMI (mentioned, security impact hidden) |
| #14406 | ggml: ensure tensor size is valid | BruceMacD | 2026-02-24 | **v0.28.0** | 2026-02-25 | ❌ NO |
| CVE-2026-42248 | Missing Windows signature verification | Striga.ai | — | **v0.30.0** | 2026-05-13 | ❌ NO |
| CVE-2026-42249 | Path traversal in Windows updater | Striga.ai | — | **v0.30.0** | 2026-05-13 | ❌ NO |
| CVE-2026-5757 | GGUF quantization memory leak | CERT Polska | — | **UNPATCHED** | — | N/A |
| CVE-2026-7482 | "Bleeding Llama" heap OOB read | Cyera | — | **v0.17.1** (partial) | 2026-02-25 | ❌ NO |

---

*End of version correction master document. Generated 2026-06-07 by general-97959d81.*