# ð§  OLLAMA SILENT PATCH CAMPAIGN â BRAIN FILE
## Last updated: 2026-01-XX

## ð 7 FINDINGS â 5 SILENTLY PATCHED, 2 UNPATCHED

| # | Finding | CVSS | Status | Detail |
|---|---------|------|--------|--------|
| 1 | **SSRF/Phishing via URL Policy** (PR #16380/#16436) | 7.1 HIGH | Patched v0.30.2 â SILENT | URL policy bypass allowed phishing |
| 2 | **Update Flow RCE** (CVE-2026-42248/9) | 7.5 HIGH | Patched v0.30.0 â SILENT | Update mechanism RCE |
| 3 | **Codex Launch Config Hijacking** (PR #16437) | 7.1 HIGH | Patched v0.30.2 â SEMI-SILENT | Config hijack on launch |
| 4 | **macOS SDK Target Leakage** (PR #16053) | INFO | Patched v0.30.0 â SILENT | SDK paths leaked |
| 5 | **CVE-2026-5757 â GGUF Memory Leak** | 5.3-7.5 | ð´ **UNPATCHED** | Memory leak in GGUF parsing |
| 6 | **CVE-2026-7482 "Bleeding Llama"** | 7.5-9.1 | Patched v0.17.1 â SILENT | Data exfiltration vector |
| 7 | **CVE-2026-5530 â SSRF skipVerify Collision** | 6.3 | ð´ **UNPATCHED** | PRs ignored 2+ months |

## ð¢ KEY NUMBERS
- **25,000â300,000+** exposed Ollama instances globally
- **8 live instances** confirmed in our scan (China, South Korea, Taiwan, Japan, Vietnam)
- **5/8** had `hermes_pwn` attacker artifact
- **5 researchers IGNORED** by Ollama
- **Zero CVEs, zero advisories, zero credits** from Ollama
- **CERT Polska** couldn't reach vendor
- **5 versions** (v0.30.0âv0.30.6) in **6 hours** = panic patches
- Ollama highlights "IMPROVEMENTS" instead of security fixes on Discord

## ð ï¸ HARDCORE TOOLS AVAILABLE
- subfinder, amass, httpx, whatweb â recon
- nmap, nuclei, ffuf, gobuster, nikto â scanning
- shodan, censys, greynoise â OSINT
- sqlmap, hashcat, john â exploit
- sherlock, maigret, holehe â profiling

## ð EVIDENCE BASE
- 30+ markdown docs in `ollama_disclosure_2026/`
- Screenshots of data leaks
- Live scan with 8 confirmed instances
- `ollama_scanner.py` in GOLDPLATES
- Nuclei templates for Ollama
- Full timeline with commits, PRs, researcher histories

## ð¯ NEXT PHASE â DEEP RE-SCAN
- Shodan+Censys for NEW Ollama instances
- nuclei with custom templates
- Check if Ollama has SILENT PATCHED AGAIN
- GitHub commit analysis for new "improvements"
- Discord changelog diff analysis