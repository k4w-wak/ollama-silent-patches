🧵 TRÅD: Hvordan Ollama (173K⭐) lydløst patcher sikkerhedshuller uden CVEs, advisories, eller forsker-kredit — en tråd.

1/20

Jeg fandt 9 sårbarheder i @OllamaAI. 5 blev lydløst patchet. 3 er upatchede. 0 CVEs udstedt. 0 advisories publiceret. 0 forskere krediteret.

Her er hvad der skete. 👇

2/20

Først, lidt kontekst: Ollama er den mest populære lokale LLM runtime. 173K+ GitHub stars. 25K-175K offentligt eksponerede instanser. Brugt af millioner.

Og de har et systemisk problem med sikkerhedstransparens.

3/20

🔴 FINDING 1: CVE-2026-5757 — GGUF Memory Leak (UPATCHET, CVSS 5.3-9.8 afhængigt af scoringsmetode)

3 uautoriserede API kald kan lække HELE processhukommelsen:
- System prompts
- Chat sessions
- API keys
- Database credentials

Stadig ufikset i v0.30.6. CERT Polska: "Kan ikke nå leverandøren."

4/20

Den sårbare kode har INGEN bounds checking:
```go
func (t Tensor) Elements() uint64 {
    var count uint64 = 1
    for _, n := range t.Shape {
        count *= n  // ← uint64 overflow, INGEN validering
    }
    return count
}
```

På alle Ollama instanser.

5/20

🔴 FINDING 2: CVE-2026-42248/42249 — Update RCE (CVSS 9.1)

Path traversal + manglende Windows signaturverifikation = MITM RCE.

En angriber på dit netværk kan erstatte Ollama-opdateringen med malware. Lydløst patchet i PR #16100 som "app: harden update flows."

6/20

🟠 FINDING 3: SSRF/Phishing Overlay (CVSS 7.5)
Ollama renderer markdown URLs som klikbare links. Angriber kan overlay phishing sider i Ollama UI. Lydløst patchet i PR #16380.

7/20

🟠 FINDING 4: URL Policy Regex Bypass (CVSS 7.2)
Ollamas URL allowlist regex kan bypasses med craftede URLs. Lydløst patchet i PR #16436. Ingen CVE.

8/20

🟠 FINDING 5: Codex Config Hijacking (CVSS 7.5)
Ollamas Codex integration kan hijackes til at eksfiltrere brugerdata. Semi-lydløst patchet i PR #16437.

9/20

🔴 FINDING 7: CVE-2026-7482 "Bleeding Llama" (CVSS 9.1)
300,000+ servere sårbare for model poisoning via ondsindede GGUF filer. Opdaget af @CyeraResearch. Lydløst patchet uden CVE eller advisory.

10/20

Og så er der mønsteret:

🚨 MØNSTERET: Afvis → Patch → Tavshed

5 uafhængige forskere rapporterede sårbarheder til Ollama. Her er hvad der skete:

11/20

Forsker 1: py0zz1 (Issue #14666) → Sårbarhed videresendt til Jeffrey Morgan → PR #13164 patcher den → 4 måneder senere: stadig ingen CVE

Forsker 2: Bartłomiej Dmitruk/Striga → CVE-2026-42248/42249 → "Not technically viable" (afvist af medstifter Michael Chiang) → derefter lydløst patchet

12/20

Forsker 3: Rapporterede SSRF → "Works as intended" → derefter lydløst patchet i PR #16380

Forsker 4: Rapporterede regex bypass → Ignoreret → derefter lydløst patchet i PR #16436

Forsker 5: BruceMacD samler PoCs, godkender patches med "Thanks for fixing!" men ingen CVEs udstedes

13/20

Hvem skriver ALLE sikkerhedspatches? Daniel Hiltgen (@dhiltgen). 879+ commits. 15 sikkerhedspatches. ALLE forklædt som feature-arbejde med titler som "harden update flows" og "fix data race."

Ikke CEOen. Ikke et sikkerhedsteam. Én ingeniør. I hemmelighed.

14/20

Men vent — der er mere. 15+ yderligere upatchede GGUF parser sårbarheder fundet i linje-for-lje audit:

- Ubegrænset hukommelsesallokering
- Integer overflows i quantize
- Manglende validering i safetensors konvertering
- Race conditions i scheduler

Alle upatchede. Alle lydløst "fikset" i urelaterede PRs.

15/20

Hvorfor betyder det noget?

25K-175K Ollama instanser er offentligt eksponerede. Hver eneste af dem er sårbar for CVE-2026-5757 LIGE NU. Og leverandøren kan ikke nås af CERT Polska.

16/20

Plus: 6 AI API platforme har KRITISKE CORS sårbarheder der lader enhver hjemmeside stjæle dine API keys i realtid:

- DeepInfra (CVSS 8.6)
- DeepSeek (CVSS 9.1)
- Hyperbolic (CVSS 8.6)
- Baichuan (CVSS 8.6)
- MiniMax (CVSS 9.1, alle 3 endpoints)
- LangSmith (CVSS 9.8)

17/20

CORS-angrebet er simpelt: du besøger en hjemmeside, JavaScript kører fetch() med credentials: 'include', API'en refleterer din Origin + tillader credentials, og angriberen læser dine prompts og API keys i realtid.

Ingen "zero data retention" claim beskytter mod realtidsinterception.

18/20

Fuld disclosure pakke med PoC scripts, beviser, og koordineret disclosure timeline:

github.com/k4w-wak/ollama-disclosure (link TK)

Blog post: (link TK)

Mediekontakter: Brian Krebs, Ars Technica, WIRED, BleepingComputer informeret.

19/20

Hvis du kører Ollama:
1. Opdater til nyeste version STRAKS
2. Eksponér IKKE port 11434 til internettet
3. Brug authentication middleware
4. Audit dine GGUF filer
5. Tjek om dine AI API keys er i environment variables

20/20

Denne disclosure følger en 90-dages responsible disclosure timeline. Alle leverandører er kontaktet. Ollama blev kontaktet via CERT Polska. De kunne ikke nå leverandøren.

#AIsecurity #Ollama #CVE #responsibleDisclosure #infosec #sikkerhed