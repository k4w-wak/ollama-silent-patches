Now I have enough data to compile the comprehensive shopping tour. Let me write it up.

---

# 🔫 GitHub Security/Recon Shopping Tour — Hidden Gems 2025-2026

> Focus: **Lesser-known tools under 5000 stars**, actively maintained, fresh & useful.

---

## 🤖 1. AI-Powered Security Scanners

### **MEDUSA** — AI-First Security Scanner
| | |
|---|---|
| **Repo** | [Pantheon-Security/medusa](https://github.com/Pantheon-Security/medusa) |
| **Stars** | 592 ⭐ |
| **Language** | Python |
| **Last Updated** | 2026-06-01 |
| **Created** | 2025-11-15 |

**What it does:** Scans any GitHub repo for AI/ML security vulnerabilities — repo poisoning, prompt injection in agent configs, MCP server risks, hardcoded secrets. **9,600+ detection rules** across 76 analyzers, plus 514 FP-filter patterns (96.8% noise reduction).

**Why it's useful:** The *only* tool that specifically targets AI/LLM agent supply chain attacks. If you're running Ollama, MCP servers, or Claude Code locally — this finds the backdoors nobody else checks for. `medusa scan --git user/repo` and you're done.

---

### **AgentShield** — AI Agent Config Auditor
| | |
|---|---|
| **Repo** | [affaan-m/agentshield](https://github.com/affaan-m/agentshield) |
| **Stars** | 770 ⭐ |
| **Language** | TypeScript |
| **Last Updated** | 2026-06-02 |
| **Created** | 2026-02-11 |

**What it does:** Scans Claude Code setups for hardcoded secrets, permission misconfigs, hook injection vectors, MCP server risks, and prompt injection in agent configs. Available as CLI, GitHub Action, and ECC plugin.

**Why it's useful:** Built by Affaan Mustafa (the Everything Claude Code creator). It's the *first* dedicated auditor for agentic AI configs. If you run any AI coding agent — this catches what MEDUSA misses (config-level, not code-level). Featured at Anthropic's Cerebral Valley event.

---

### **ZIRAN** — AI Agent Tool Chain Security Tester
| | |
|---|---|
| **Repo** | [taoq-ai/ziran](https://github.com/taoq-ai/ziran) |
| **Stars** | 6 ⭐ (ultra-hidden gem!) |
| **Language** | Python |
| **Last Updated** | 2026-05-29 |
| **Created** | 2026-02-09 |

**What it does:** Models AI agents as knowledge graphs and discovers **dangerous tool chain compositions** — i.e., where two individually safe tools become exploitable when chained. First tool to test Google's Agent-to-Agent protocol.

**Why it's useful:** Nobody else is testing agent *compositional* security. If you're building multi-tool AI pipelines, this catches emergent vulnerabilities that single-tool scanners completely miss. Very early-stage, high upside.

---

### **Cisco DefenseClaw** — Security Governance for Agentic AI
| | |
|---|---|
| **Repo** | [cisco-ai-defense/defenseclaw](https://github.com/cisco-ai-defense/defenseclaw) |
| **Stars** | 700 ⭐ |
| **Language** | Go + Python |
| **Last Updated** | 2026-06-02 |
| **Created** | 2026-03-23 |

**What it does:** Enterprise-grade security governance for AI agents. Ingests external skill/MCP catalogs with SSRF guards, scanner-driven verdicts, and auto-promotion into asset policies. Pairs a Python CLI with a Go gateway sidecar.

**Why it's useful:** Backed by Cisco's AI Defense team. It's the *runtime* complement to MEDUSA/AgentShield — while they scan configs pre-deployment, DefenseClaw monitors agent behavior *live* and enforces policy on tool calls in real-time.

---

### **Cisco MCP Scanner** — MCP Server Threat Scanner
| | |
|---|---|
| **Repo** | [cisco-ai-defense/mcp-scanner](https://github.com/cisco-ai-defense/mcp-scanner) |
| **Stars** | 951 ⭐ |
| **Language** | Python |
| **Last Updated** | 2026-06-02 |
| **Created** | 2025-09-24 |

**What it does:** Scans Model Context Protocol (MCP) servers for threats — malicious behaviors, hidden instructions, vulnerable tool definitions — using behavioral code threat analysis.

**Why it's useful:** MCP servers are the *hottest* attack surface in 2026. Every AI agent connects through them, but almost nobody validates them. Cisco's tool is production-quality and free.

---

### **Cisco Skill Scanner** — Agent Skill Security Scanner
| | |
|---|---|
| **Repo** | [cisco-ai-defense/skill-scanner](https://github.com/cisco-ai-defense/skill-scanner) |
| **Stars** | 2,113 ⭐ |
| **Language** | Python |
| **Last Updated** | 2026-06-02 |
| **Created** | 2026-01-29 |

**What it does:** Pre-execution security scanner for AI agent "skills" (Markdown-defined capabilities). Detects prompt injection, data exfiltration, and malicious payloads *before* skills are installed.

**Why it's useful:** Skills are the new package dependencies. Cisco's scanner is the `npm audit` for the agent world. 1.5k stars in the first week — this is becoming standard infrastructure.

---

### **NVIDIA Garak** — LLM Vulnerability Scanner
| | |
|---|---|
| **Repo** | [NVIDIA/garak](https://github.com/NVIDIA/garak) |
| **Stars** | 8,001 ⭐ (slightly above threshold, but essential) |
| **Language** | Python |
| **Last Updated** | 2026-06-02 |
| **Created** | 2023-05-10 |

**What it does:** "The Nessus for LLMs" — probes LLMs for hallucination, data leakage, prompt injection, jailbreaks, misinformation, and dozens of other vulnerability classes. Built by NVIDIA's AI Red Team.

**Why it's useful:** If you deploy *any* LLM (Ollama, vLLM, commercial APIs), garak is the red team baseline. 80+ probe generators, supports all major models. The only production-grade LLM scanner backed by a major vendor.

---

## 🕵️ 2. Bug Bounty Recon Tools

### **God's Eye** — AI-Powered Subdomain Enumeration
| | |
|---|---|
| **Repo** | [Vyntral/god-eye](https://github.com/Vyntral/god-eye) |
| **Stars** | 472 ⭐ |
| **Language** | Go |
| **Last Updated** | 2026-06-02 |
| **Created** | 2025-11-19 |

**What it does:** Integrates 26 passive subdomain sources + active probing + local LLM analysis (via Ollama). Zero API costs, 100% private. Full pipeline in under 2.5 minutes.

**Why it's useful:** The *only* subdomain tool that adds AI triage to raw results. The LLM prioritizes findings, filters noise, and suggests attack vectors. No API keys needed. `--profile bugbounty` mode pre-configures all sources.

---

### **CSPRecon** — Discover Domains via Content Security Policy
| | |
|---|---|
| **Repo** | [edoardottt/csprecon](https://github.com/edoardottt/csprecon) |
| **Stars** | 514 ⭐ |
| **Language** | Go |
| **Last Updated** | 2026-05-28 |
| **Created** | 2022-11-18 |

**What it does:** Parses Content-Security-Policy headers to discover hidden subdomains and third-party domains. CSP headers often reveal internal staging domains, CDN backends, and API endpoints.

**Why it's useful:** *Nobody* checks CSP headers during recon, but they're a goldmine. You'll find staging/dev domains that don't appear in any subdomain enumeration tool. Written in Go, pipeable, fast.

---

### **Cero** — SSL Certificate Domain Scraper
| | |
|---|---|
| **Repo** | [glebarez/cero](https://github.com/glebarez/cero) |
| **Stars** | 691 ⭐ |
| **Language** | Go |
| **Last Updated** | 2026-05-23 |
| **Created** | 2020-04-26 |

**What it does:** Connects to arbitrary hosts and scrapes domain names from their SSL certificates (Subject Alternative Names). Works through certificate transparency logs *and* direct TLS connections.

**Why it's useful:** Finds internal domains hidden behind load balancers — certificates expose SAN entries that DNS enumeration completely misses. Ultra-fast Go binary. Great for finding wildcard cert subdomains.

---

### **URLFinder** — Passive URL Discovery
| | |
|---|---|
| **Repo** | [projectdiscovery/urlfinder](https://github.com/projectdiscovery/urlfinder) |
| **Stars** | 875 ⭐ |
| **Language** | Go |
| **Last Updated** | 2026-05-31 |
| **Created** | 2024-04-30 |

**What it does:** High-speed passive URL discovery from Wayback Machine, Common Crawl, AlienVault OTX, URLScan, and 20+ other sources. No active scanning — purely passive.

**Why it's useful:** The missing link between subdomain enumeration and vulnerability hunting. After you find subdomains, URLFinder gives you the *endpoints* — hidden paths, old API versions, debug endpoints. By ProjectDiscovery, so it integrates perfectly with httpx/nuclei.

---

### **BBH-Recon** — Structured Bug Bounty Recon Methodology
| | |
|---|---|
| **Repo** | [RemmyNine/BBH-Recon](https://github.com/RemmyNine/BBH-Recon) |
| **Stars** | 40 ⭐ (ultra-hidden!) |
| **Last Updated** | 2026-06-01 |
| **Created** | 2024-05-30 |

**What it does:** Not a tool — a *structured methodology repository*. Covers the full recon workflow from scope definition through subdomain enumeration, port scanning, content discovery, and tech fingerprinting. Includes checklists and tool recommendations.

**Why it's useful:** Perfect for beginners building their recon pipeline, or veterans who want a structured reference. Active community with recent updates. Complements automated tools like reconFTW.

---

## 🎯 3. CVE Exploit Scripts

### **0xMarcio/cve** — Latest CVEs with PoC Exploits
| | |
|---|---|
| **Repo** | [0xMarcio/cve](https://github.com/0xMarcio/cve) |
| **Stars** | 1,298 ⭐ |
| **Language** | Python |
| **Last Updated** | 2026-06-02 |
| **Created** | 2024-05-24 |

**What it does:** Continuously updated collection of the *latest* CVEs with their Proof of Concept exploits. Includes writeups and ready-to-run exploit scripts.

**Why it's useful:** Unlike `trickest/cve` (which is massive and noisy), this focuses on *fresh* CVEs with *working* PoCs. When a new critical CVE drops, this repo has the exploit within days. Essential for bounty hunters tracking fresh attack surface.

---

### **Nuclei Templates AI** — AI-Generated Nuclei Templates
| | |
|---|---|
| **Repo** | [projectdiscovery/nuclei-templates-ai](https://github.com/projectdiscovery/nuclei-templates-ai) |
| **Stars** | 121 ⭐ (very hidden!) |
| **Language** | YAML (templates) |
| **Last Updated** | 2026-05-21 |
| **Created** | 2024-12-04 |

**What it does:** AI-generated Nuclei templates for CVEs *not yet covered* by the main nuclei-templates repo. Uses ProjectDiscoveryAI API to automatically generate detection templates for newly disclosed vulnerabilities.

**Why it's useful:** The main templates repo takes days/weeks to cover new CVEs. This repo has AI-generated templates *immediately*. If you run Nuclei in your recon pipeline (you should), add this as a second templates path for zero-day coverage.

---

## 🕷️ 4. OSINT Tools

### **CrossLinked** — LinkedIn Employee Enumeration
| | |
|---|---|
| **Repo** | [m8sec/CrossLinked](https://github.com/m8sec/CrossLinked) |
| **Stars** | 1,542 ⭐ |
| **Language** | Python |
| **Last Updated** | 2026-06-01 |
| **Created** | 2019-05-16 |

**What it does:** Enumerates valid employee names from organizations via search engine scraping (Google, Bing). Outputs formatted username lists for brute-force and phishing simulations.

**Why it's useful:** LinkedIn OSINT is one of the most effective ways to build username lists for password spraying and phishing. This tool automates the entire process. Essential for red team ops and social engineering pretexts.

---

### **HawkScan** — Web Recon & Information Gathering
| | |
|---|---|
| **Repo** | [c0dejump/HawkScan](https://github.com/c0dejump/HawkScan) |
| **Stars** | 462 ⭐ |
| **Language** | Python |
| **Last Updated** | 2026-04-15 |
| **Created** | 2018-12-12 |

**What it does:** All-in-one web reconnaissance tool — subdomain enumeration, port scanning, CMS detection, WHOIS, DNS, and vulnerability scanning in a single Python script with a colorful CLI.

**Why it's useful:** Great for quick recon on a single target when you don't want to set up a full pipeline. Lightweight, no Docker required, single-command execution. Good for initial triage before deep-diving with specialized tools.

---

### **SecretMagpie** — Multi-Repo Secret Detection
| | |
|---|---|
| **Repo** | [punk-security/secret-magpie](https://github.com/punk-security/secret-magpie) |
| **Stars** | 243 ⭐ |
| **Language** | HTML/Python |
| **Last Updated** | 2026-05-13 |
| **Created** | 2022-05-10 |

**What it does:** Scans *all* repositories across GitHub, GitLab, Azure DevOps, and Bitbucket for leaked secrets — API keys, credentials, tokens. Runs Gitleaks, TruffleHog, and detect-secrets in parallel for maximum coverage.

**Why it's useful:** Most secret scanners work on one repo at a time. SecretMagpie scans *every repo in your org* across multiple platforms simultaneously. Perfect for bug bounty — point it at a target org and find secrets across all their repos in one shot.

---

## 🧬 5. Subdomain Enumeration Tools

### **God's Eye** (covered above) — AI-powered, local LLM triage
### **CSPRecon** (covered above) — CSP header parsing
### **Cero** (covered above) — SSL certificate SAN extraction

### **WayMore** — Wayback Machine URL Discovery
| | |
|---|---|
| **Repo** | [xnl-h4ck3r/waymore](https://github.com/xnl-h4ck3r/waymore) |
| **Stars** | 2,658 ⭐ |
| **Language** | Python |
| **Last Updated** | 2026-06-01 |
| **Created** | 2022-06-24 |

**What it does:** Finds *way more* URLs from Wayback Machine, Common Crawl, AlienVault OTX, URLScan, VirusTotal, GhostArchive & Intelligence X. Not just subdomains — actual endpoints, parameters, paths.

**Why it's useful:** Wayback Machine + 6 other sources = historical endpoint discovery that no other tool matches. Finds old API versions, debug pages, and forgotten endpoints that have been removed from current DNS but still respond. Essential for finding hidden attack surface.

---

## 💣 6. Fuzzing & Bypass Tools

### **ffufai** — AI-Powered FFUF Wrapper
| | |
|---|---|
| **Repo** | [jthack/ffufai](https://github.com/jthack/ffufai) |
| **Stars** | 779 ⭐ |
| **Language** | Python |
| **Last Updated** | 2026-06-02 |
| **Created** | 2024-08-22 |

**What it does:** Wraps ffuf with AI — automatically suggests file extensions for fuzzing based on target URL and response headers using GPT/Claude. Now also generates *contextual wordlists* based on target technology stack.

**Why it's useful:** The biggest problem with ffuf is choosing the right wordlist and extensions. ffufai analyzes the target first, then builds optimized fuzzing payloads. Saves hours on content discovery. By Joseph Thacker (reliable security researcher).

---

### **GoBypass403** — WAF & 403 Bypass Tool
| | |
|---|---|
| **Repo** | [slicingmelon/gobypass403](https://github.com/slicingmelon/gobypass403) |
| **Stars** | 31 ⭐ (deepest hidden gem!) |
| **Language** | Go |
| **Last Updated** | 2026-05-28 |
| **Created** | 2024-11-13 |

**What it does:** Tests 403/401 bypasses with *exact URL path preservation* — a critical detail most bypass tools get wrong. Also includes CDN bypass support via host substitution. Custom URL parser maintains path integrity.

**Why it's useful:** Most 403 bypass tools mangle URLs during payload insertion. This tool's custom parser preserves exact paths and structures — the difference between a bypass working and not. CDN bypass mode is unique. Only 31 stars but more effective than tools with 10k+.

---

### **Nuclei AI Extension** — Browser Extension for Template Generation
| | |
|---|---|
| **Repo** | [projectdiscovery/nuclei-ai-extension](https://github.com/projectdiscovery/nuclei-ai-extension) |
| **Stars** | 551 ⭐ |
| **Language** | JavaScript |
| **Last Updated** | 2026-05-26 |
| **Created** | 2023-05-22 |

**What it does:** Browser extension that extracts vulnerability info from any webpage and auto-generates Nuclei templates. Click a button on a CVE advisory → get a ready-to-run detection template.

**Why it's useful:** Normally writing Nuclei templates requires YAML expertise and understanding the template DSL. This extension makes it *instant* — browse to a vulnerability advisory, extract, generate, scan. Dramatically lowers the bar for custom vulnerability detection.

---

## 🤖 7. Interesting One-Person / Solo Projects

### **Guardian-CLI** — AI-Powered Pentest Automation
| | |
|---|---|
| **Repo** | [zakirkun/guardian-cli](https://github.com/zakirkun/guardian-cli) |
| **Stars** | 1,444 ⭐ |
| **Language** | Python |
| **Last Updated** | 2026-06-02 |
| **Created** | 2025-12-22 |

**What it does:** Production-ready CLI that orchestrates Google Gemini + LangChain to perform automated penetration testing. Handles recon, vulnerability scanning, and reporting through a single command.

**Why it's useful:** Solo developer project that went viral. Unlike PentAGI (17k stars, enterprise), Guardian is a single-person tool you can run in 5 minutes. Great for automating routine pentest tasks. Uses Gemini's free tier so no API costs for basic usage.

---

### **Claude Bug Bounty** — AI-Powered Bug Bounty from Terminal
| | |
|---|---|
| **Repo** | [shuvonsec/claude-bug-bounty](https://github.com/shuvonsec/claude-bug-bounty) |
| **Stars** | 2,372 ⭐ |
| **Language** | Python |
| **Last Updated** | 2026-06-02 |
| **Created** | 2026-03-08 |

**What it does:** Runs entirely inside Claude Code terminal — autonomous bug bounty hunting with 20 vulnerability classes, recon, and report generation. No separate tool installation needed.

**Why it's useful:** If you use Claude Code (and you should), this is a single CLAUDE.md file that turns it into a bug bounty machine. 2,372 stars in ~3 months shows massive community adoption. The fastest way to start AI-assisted hunting.

---

### **PentAGI** — Autonomous AI Pentest System
| | |
|---|---|
| **Repo** | [vxcontrol/pentagi](https://github.com/vxcontrol/pentagi) |
| **Stars** | 17,402 ⭐ (above threshold, but notable) |
| **Language** | Go + Python |
| **Last Updated** | 2026-06-02 |
| **Created** | 2025-01-06 |

**What it does:** Fully autonomous AI agent system with 4 sub-agents in Docker sandboxes — orchestrates recon, vulnerability scanning, exploitation, and reporting. Supports Claude, GPT, and Gemini models.

**Why it's useful:** The most mature autonomous pentest agent. Production Docker setup, proper sandboxing, multi-model support. Went from 0 to 17k stars in ~16 months. Serious tool for serious hunters.

---

## 📊 Quick Reference Table

| Tool | Stars | Category | Language | Why Hidden Gem |
|------|-------|-----------|----------|----------------|
| MEDUSA | 592 | AI Security Scanner | Python | Only tool for AI/ML supply chain attacks |
| AgentShield | 770 | AI Config Auditor | TypeScript | First dedicated agent config scanner |
| ZIRAN | 6 | AI Agent Testing | Python | Tests dangerous tool chain compositions |
| DefenseClaw | 700 | AI Runtime Governance | Go+Python | Cisco-backed runtime agent security |
| MCP Scanner | 951 | AI Security | Python | Scans the hottest 2026 attack surface |
| Skill Scanner | 2,113 | AI Security | Python | npm audit for agent skills |
| Garak | 8,001 | LLM Scanner | Python | Nessus for LLMs — NVIDIA backed |
| God's Eye | 472 | Subdomain Enum | Go | AI triage on subdomain results |
| CSPRecon | 514 | Subdomain Enum | Go | Finds domains in CSP headers |
| Cero | 691 | Subdomain Enum | Go | Extracts domains from SSL certs |
| URLFinder | 875 | URL Discovery | Go | Passive endpoint finder by PD |
| WayMore | 2,658 | URL Discovery | Python | 7 sources for historical endpoints |
| CrossLinked | 1,542 | OSINT | Python | LinkedIn employee enumeration |
| HawkScan | 462 | Recon Suite | Python | All-in-one quick recon |
| SecretMagpie | 243 | Secret Detection | Python | Multi-platform org-wide scanning |
| 0xMarcio/cve | 1,298 | CVE PoCs | Python | Fresh CVEs with working exploits |
| Nuclei Templates AI | 121 | Vuln Detection | YAML | AI-generated templates for new CVEs |
| ffufai | 779 | Fuzzing | Python | AI-powered ffuf wrapper |
| GoBypass403 | 31 | Bypass | Go | Preserves URL paths during bypass |
| Nuclei AI Extension | 551 | Vuln Detection | JS | Browser-based template generator |
| Guardian-CLI | 1,444 | AI Pentest | Python | Solo-dev AI pentest automation |
| Claude Bug Bounty | 2,372 | AI Bug Bounty | Python | AI hunting in Claude Code |
| BBH-Recon | 40 | Methodology | Markdown | Structured recon playbook |
| PentAGI | 17,402 | AI Pentest | Go | Autonomous multi-agent pentest |

---

## 🔥 Top 5 Picks for Immediate Installation

1. **MEDUSA** — `pip install medusa-scanner` → Your AI infra is probably vulnerable. Fix it.
2. **God's Eye** — `go install` → The only subdomain tool with AI triage. No API keys.
3. **ffufai** — `pip install ffufai` → Stop guessing extensions. Let AI choose.
4. **GoBypass403** — `go install` → 31 stars but outperforms 10k-star bypass tools.
5. **ZIRAN** — `pip install ziran` → 6 stars. Tests compositional AI agent attacks. Nobody's using this yet.