# FUNKTIONS OVERBLIK — 02_grok_engine

Overblik over slash-kommandoer, værktøjer, agenter, team-roller, MCP-servere, plugins og AskNova/Huntr-funktionalitet i projektet. Information er scannet fra `grok.py`, `core/tools.py`, `core/team_engine.py`, `grok_team.py`, MCP/OMP-config, `huntrv2.py` og plugin-kilder.

---

## 1. Chat / Agent — Interaktive kommandoer i grok.py

| Kommando | Syntax / Brug | Beskrivelse | Fil |
|----------|---------------|-------------|-----|
| `/help` | `/help` | Vis alle kommandoer. | `grok.py` |
| `/tools` | `/tools` | List aktive værktøjer. | `grok.py` |
| `/memory` | `/memory` | Vis langtids- og korttidshukommelse. | `grok.py` |
| `/model` | `/model` eller `/model <provider> <model>` | Vis aktiv model eller skift provider/model. | `grok.py` |
| `/status` | `/status` | Agent-status, cookies, streaming, slim-mode. | `grok.py` |
| `/save` | `/save` | Gem session nu. | `grok.py` |
| `/clear` | `/clear` | Ryd samtale (langtidshukommelse bevares). | `grok.py` |
| `/compact` | `/compact` | Komprimer samtale til 40 beskeder. | `grok.py` + `core/compact.py` |
| `/search` | `/search [on\|off\|force]` | Slå frisk web-søgning til/fra eller test. | `grok.py` |
| `/stream` | `/stream [on\|off]` | Streaming output til/fra. | `grok.py` |
| `/slim` | `/slim [on\|off\|status]` | Reducer antallet af tilgængelige tools. | `grok.py` + `core/tools.py` |
| `/quit` | `/quit`, `/exit`, `/q` | Afslut og gem historik. | `grok.py` |
| `/plan` | `/plan [problem]` | Start plan-mode. | `grok.py` + `core/tools.py` |
| `/history` | `/history [limit]` | Samtalehistorik (default 50). | `grok.py` + `core/history.py` |
| `/config` | `/config [setting [value]]` | Læs/skriv Grok-indstillinger. | `grok.py` + `core/config_tool.py` |
| `/cost` | `/cost` | Token-brugsrapport. | `grok.py` + `core/cost.py` |

---

## 2. Tasks / Todos / Sessions

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `/task` | `/task [list\|create <title>\|stop <id>\|update <id> <status>]` | Opret/list/opdater tasks. | `grok.py` + `core/task.py` |
| `/todo` | `/todo [list\|<text>]` | Skriv/læs persistent todo-liste. | `grok.py` + `core/todo.py` |
| `/session` | `/session [list\|save [id]\|load <id>]` | Gem/load/list sessions. | `grok.py` + `core/session.py` |

---

## 3. Sub-agenter

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `/agent` | `/agent [list\|spawn [type] [desc]\|run <id>\|stop <id>]` | Spawn/kør/stop sub-agenter. | `grok.py` + `core/agents.py` |

### Underliggende agent-tools (core/tools.py)

| Tool | Syntax | Beskrivelse | Fil |
|------|--------|-------------|-----|
| `agent_spawn` | `agent_spawn type beskrivelse \| prompt` | Spawn en sub-agent (explore/plan/verify/general). | `core/tools.py` |
| `agent_run` | `agent_run agent_id [prompt]` | Kør en spawned agent. | `core/tools.py` |
| `agent_status` | `agent_status [agent_id]` | Tjek status for én eller alle agenter. | `core/tools.py` |
| `agent_stop` | `agent_stop agent_id` | Stop en kørende agent. | `core/tools.py` |
| `agent_run_parallel` | `agent_run_parallel id1,id2,id3` | Kør flere agenter parallelt. | `core/tools.py` |
| `agent_wait_all` | `agent_wait_all [id1,id2]` | Vent på baggrundsagenter. | `core/tools.py` |

---

## 4. Multi-Agent / Team

### grok_team.py (separat team-CLI)

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `python3 grok_team.py` | — | Interaktiv team mode. | `grok_team.py` |
| `python3 grok_team.py "mission"` | `python3 grok_team.py "audit repo"` | Batch team mission. | `grok_team.py` |
| `/team <mission>` | `/team audit repo for sårbarheder` | Kør team mission. | `grok_team.py` |
| `/team status` | `/team status` | Se aktive teammates. | `grok_team.py` |
| `/team roles` | `/team roles` | List roller. | `grok_team.py` |

### /team i grok.py

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `/team` | `/team <mission>` | Kør multi-agent swarm med auto-roller. | `grok.py` |
| `/team --type <type>` | `/team --type security_audit <mission>` | Vælg team-type. | `grok.py` + `core/team_engine.py` |
| `/team status` | `/team status` | TeamEngine status. | `grok.py` + `core/team_engine.py` |
| `/team roles` | `/team roles` | List team-roller. | `grok.py` + `core/team_engine.py` |

### TeamEngine roller og team-typer (core/team_engine.py)

| Rolle | Beskrivelse |
|-------|-------------|
| `commander` | Mission conductor — planlægger og syntetiserer. |
| `security` | Offensive security, bug bounty, exploit-verifikation. |
| `code` | Python-arkitektur, debug, refaktorering, tests. |
| `recon` | OSINT, asset discovery, scope mapping. |
| `verifier` | Fact-checker og false-positive jæger. |
| `reporter` | Markdown-formatter og final report writer. |

| Team-type | Roller |
|-----------|--------|
| `security_audit` | commander, security, recon, verifier, reporter |
| `bugbounty` | commander, security, recon, verifier, reporter |
| `code_refactor` | commander, code, verifier, reporter |
| `code_audit` | commander, code, security, verifier, reporter |
| `research` | commander, recon, security, reporter |
| `generic` | commander, security, code, recon, verifier, reporter |

---

## 5. MCP (Model Context Protocol)

### OMP MCP config (.omp/mcp.json)

| Server | Type | Kommando/URL | Beskrivelse |
|--------|------|--------------|-------------|
| `project-filesystem` | stdio | `npx -y @modelcontextprotocol/server-filesystem /home/admin_user/workspace_codex/02_grok_engine` | Filsystem-adgang via MCP. |

### /mcp kommandoer i grok.py

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `/mcp list` | `/mcp list` | List konfigurerede MCP-servere. | `grok.py` + `core/mcp.py` |
| `/mcp add` | `/mcp add <name> <type> <command>` | Tilføj MCP-server. | `grok.py` + `core/mcp.py` |

### core/mcp.py funktioner

| Funktion | Syntax | Beskrivelse |
|----------|--------|-------------|
| `mcp_list_servers` | — | List MCP-servere fra `~/.grok/mcp_servers.json`. |
| `mcp_add_server` | name, type, command, url, args, env | Tilføj stdio/http/sse server. |
| `mcp_remove_server` | name | Fjern MCP-server. |
| `mcp_call` | server_name, tool_name, arguments | Kald tool på MCP-server via JSON-RPC. |
| `mcp_list_tools` | server_name | List tools på en MCP-server. |

### MCP server-scripts

| Script | URL / Port | Tools / Beskrivelse | Fil |
|--------|-----------|---------------------|-----|
| `grok_mcp_server.py` | stdio | `grok_run`, `grok_recon`, `grok_security_check`, `grok_status` | `grok_mcp_server.py` |
| `droid_mcp_server.py` | `0.0.0.0:8080/mcp` | `list_files`, `read_file`, `run_command`, `hash_file`, `search_files`, `get_status`, `tail_log` | `droid_mcp_server.py` |

---

## 6. Plugins

### /plugin kommandoer i grok.py

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `/plugin list` | `/plugin list` | List plugins. | `grok.py` + `core/plugins.py` |
| `/plugin add` | `/plugin add <name> <command>` | Tilføj shell/python-plugin. | `grok.py` + `core/plugins.py` |
| `/plugin run` | `/plugin run <name> [input]` | Kør plugin. | `grok.py` + `core/plugins.py` |
| `/plugin remove` | `/plugin remove <name>` | Fjern plugin. | `grok.py` + `core/plugins.py` |

### core/plugins.py funktioner

| Funktion | Syntax | Beskrivelse |
|----------|--------|-------------|
| `plugin_list` | — | List installerede plugins fra `~/.grok/plugins/`. |
| `plugin_add` | name, command, description, type, category | Tilføj plugin (shell/python). |
| `plugin_run` | name, input_data | Kør plugin og returnér output. |
| `plugin_remove` | name | Fjern plugin. |

### OMP installerede plugins (.omp/plugins/installed_plugins.json)

| Plugin | Version | Beskrivelse |
|--------|---------|-------------|
| `playwright@claude-plugins-official` | 0.0.0 | Playwright browser automation. |
| `security-guidance@claude-plugins-official` | 2.0.6 | Sikkerhedsvejledning. |
| `superpowers@claude-plugins-official` | 5.1.0 | Superpowers extension. |
| `desktop-commander@claude-plugins-official` | 7a9b2ff | Desktop command integration. |
| `github@claude-plugins-official` | 0.0.0 | GitHub integration. |
| `mcp-server-dev@claude-plugins-official` | 0.0.0 | MCP server dev tools. |

---

## 7. Hooks

### /hooks kommandoer i grok.py

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `/hooks list` | `/hooks list` | List pre/post hooks. | `grok.py` + `core/hooks.py` |
| `/hooks add` | `/hooks add pre_tool\|post_tool tool_name command` | Tilføj hook. | `grok.py` + `core/hooks.py` |
| `/hooks remove` | `/hooks remove <id>` | Fjern hook. | `grok.py` + `core/hooks.py` |

### core/hooks.py funktioner

| Funktion | Syntax | Beskrivelse |
|----------|--------|-------------|
| `hooks_list` | — | Vis hooks fra `~/.grok/hooks/hooks.json`. |
| `hooks_add` | event, tool, command, description | Tilføj pre_tool eller post_tool hook. |
| `hooks_remove` | hook_id | Fjern hook. |
| `hooks_run` | event, tool_name, tool_input, tool_output | Eksekver matching hooks. |

---

## 8. Cron

### /cron kommandoer i grok.py

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `/cron list` | `/cron list` | List cron jobs. | `grok.py` + `core/cron.py` |
| `/cron add` | `/cron add <interval> <command>` | Tilføj job (fx `5m nmap 10.0.0.1`). | `grok.py` + `core/cron.py` |
| `/cron remove` | `/cron remove <id>` | Fjern job. | `grok.py` + `core/cron.py` |
| `/cron run` | `/cron run <id>` | Kør job én gang. | `grok.py` + `core/cron.py` |

### core/cron.py funktioner

| Funktion | Syntax | Beskrivelse |
|----------|--------|-------------|
| `cron_list` | — | List jobs fra `~/.grok/cron/jobs.json`. |
| `cron_add` | interval, command | Tilføj job med interval (f.eks. `30s`, `5m`, `1h`). |
| `cron_remove` | job_id | Fjern job. |
| `cron_run_once` | job_id | Kør job med det samme. |
| `cron_start_all` / `cron_stop_all` | — | Start/stop alle jobs. |

---

## 9. Git

### /git kommandoer i grok.py

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `/git status` | `/git [status] [path]` | Git status. | `grok.py` + `core/git.py` |
| `/git init` | `/git init [path]` | Initialiser repo. | `grok.py` + `core/git.py` |
| `/git diff` | `/git diff [path]` | Git diff. | `grok.py` + `core/git.py` |
| `/git add` | `/git add <path>` | Git add. | `grok.py` + `core/git.py` |
| `/git commit` | `/git commit <message>` | Git commit. | `grok.py` + `core/git.py` |
| `/git push` | `/git push [path]` | Git push. | `grok.py` + `core/git.py` |
| `/git pull` | `/git pull [path]` | Git pull. | `grok.py` + `core/git.py` |
| `/git log` | `/git log [path]` | Git log. | `grok.py` + `core/git.py` |
| `/git branch` | `/git branch [path]` | Git branch. | `grok.py` + `core/git.py` |

---

## 10. SSH / Remote

### /ssh kommandoer i grok.py

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `/ssh run` | `/ssh run "user@host command"` | Kør kommando via SSH. | `grok.py` + `core/remote.py` |
| `/ssh copy` | `/ssh copy "src dest"` | Kopier fil via SCP. | `grok.py` + `core/remote.py` |
| `/ssh tunnel` | `/ssh tunnel "spec"` | SSH port forwarding. | `grok.py` + `core/remote.py` |
| `/ssh hosts` | `/ssh hosts` | List gemte SSH hosts. | `grok.py` + `core/remote.py` |
| `/ssh add` | `/ssh add "host spec"` | Tilføj host. | `grok.py` + `core/remote.py` |
| `/ssh server` | `/ssh server [port]` | Start grok server. | `grok.py` + `core/remote.py` |
| `/ssh enable` | `/ssh enable` | Aktivér SSH. | `grok.py` + `core/remote.py` |

---

## 11. REPL (persistent Python)

### /repl kommandoer i grok.py

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `/repl` | `/repl <python code>` | Kør Python-kode i persistent REPL. | `grok.py` + `core/repl.py` |
| `/repl vars` | `/repl vars` | List REPL-variabler. | `grok.py` + `core/repl.py` |
| `/repl hist` | `/repl hist` | REPL-historik. | `grok.py` + `core/repl.py` |
| `/repl reset` | `/repl reset` | Nulstil REPL. | `grok.py` + `core/repl.py` |
| `/repl save` | `/repl save <file>` | Gem REPL-tilstand. | `grok.py` + `core/repl.py` |
| `/repl load` | `/repl load <file>` | Load REPL-tilstand. | `grok.py` + `core/repl.py` |

---

## 12. RAG — Retrieval Augmented Generation

### /rag kommandoer i grok.py

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `/rag stats` | `/rag stats` | RAG-statistik. | `grok.py` + `core/rag.py` |
| `/rag add` | `/rag add <text>` | Tilføj dokument til RAG. | `grok.py` + `core/rag.py` |
| `/rag search` | `/rag search <query>` | Søg i RAG. | `grok.py` + `core/rag.py` |
| `/rag similar` | `/rag similar <target>` | Find lignende targets. | `grok.py` + `core/rag.py` |
| `/rag index` | `/rag index` | Re-indexer chunks. | `grok.py` + `core/rag.py` |
| `/rag clear` | `/rag clear [all\|source:..\|target:..]` | Ryd RAG. | `grok.py` + `core/rag.py` |

### RAG tools (core/tools.py)

| Tool | Syntax | Beskrivelse | Fil |
|------|--------|-------------|-----|
| `rag_add` | tekst eller JSON `{text,source,target,tags}` | Tilføj dokument. | `core/tools.py` + `core/rag.py` |
| `rag_search` | query eller JSON `{query,top_k,source,target}` | Semantisk søgning. | `core/tools.py` + `core/rag.py` |
| `rag_find_similar` | domain/IP | Find lignende targets. | `core/tools.py` + `core/rag.py` |
| `rag_stats` | — | Statistik over chunks og targets. | `core/tools.py` + `core/rag.py` |
| `rag_index` | — | Re-indexer manglende embeddings. | `core/tools.py` + `core/rag.py` |
| `rag_clear` | `all`, `source:recon`, `target:example.com` | Ryd RAG. | `core/tools.py` + `core/rag.py` |

---

## 13. Structured Output

### /structured kommandoer i grok.py

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `/structured finding` | `/structured finding <evidence>` | Generer struktureret finding. | `grok.py` + `core/structured.py` |
| `/structured recon` | `/structured recon <json>` | Generer struktureret recon-rapport. | `grok.py` + `core/structured.py` |
| `/structured from` | `/structured from <text>` | Parse ustruktureret tekst til finding. | `grok.py` + `core/structured.py` |

---

## 14. Vision

### /vision kommandoer i grok.py

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `/vision analyze` | `/vision analyze <image_path>` | Analyser billede. | `grok.py` + `core/vision.py` |
| `/vision screenshot` | `/vision screenshot <image_path>` | Analyser web screenshot. | `grok.py` + `core/vision.py` |
| `/vision scan` | `/vision scan <image_path> [mode]` | Analyser scan-resultat. | `grok.py` + `core/vision.py` |
| `/vision ocr` | `/vision ocr <image_path>` | OCR tekst fra billede. | `grok.py` + `core/vision.py` |
| `/vision models` | `/vision models` | List vision-modeller. | `grok.py` + `core/vision.py` |

---

## 15. Browser / Playwright

### /browser kommandoer i grok.py

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `/browser visible` | `/browser visible URL [output] [wait]` | Synlig browser + screenshot. | `grok.py` + `core/tools.py` |
| `/browser screenshot` | `/browser screenshot URL [output]` | Headless screenshot. | `grok.py` + `core/tools.py` |
| `/browser trace` | `/browser trace URL [output]` | Network trace/HAR. | `grok.py` + `core/tools.py` |

### Browser tools (core/tools.py)

| Tool | Syntax | Beskrivelse | Fil |
|------|--------|-------------|-----|
| `playwright_screenshot` | `url [output_path]` | Headless screenshot. | `core/tools.py` |
| `browser_visible` | `url [output_path] [wait_seconds]` | Synlig browser + screenshot. | `core/tools.py` |
| `playwright_trace` | `url output_name` | HAR/network trace. | `core/tools.py` |

---

## 16. OSINT / Recon tools (core/tools.py)

| Tool | Syntax | Beskrivelse | Fil |
|------|--------|-------------|-----|
| `web_search` | `<query>` | DuckDuckGo-søgning. | `core/tools.py` |
| `http_get` | `<url>` | Hent URL (Tor-hvis `TOR_PROXY=1`). | `core/tools.py` |
| `osint_ip` | `<ip>` | OSINT på IP: whois, geo, blocklists, reverse DNS. | `core/tools.py` |
| `osint_domain` | `<domain>` | OSINT på domæne: whois, DNS, subdomains. | `core/tools.py` |
| `osint_harvest` | `<domain>` | theHarvester: emails, subdomains, hostnames. | `core/tools.py` |
| `dns_enum` | `<domain>` | DNS enumeration: subdomains, MX, TXT. | `core/tools.py` |
| `dig_deep` | `<domain>` | Deep DNS: ANY, MX, TXT records. | `core/tools.py` |
| `whois` | `<domain/IP>` | WHOIS lookup (med python-whois fallback). | `core/tools.py` |
| `subfinder` | `<domain>` | Hurtig subdomain discovery. | `core/tools.py` |
| `theharvester` | `-b all domain.com` | Email/domain harvester. | `core/tools.py` |
| `shodan` | `<IP>` eller tomt | Shodan host-info eller account info. | `core/tools.py` |
| `honeypot_check` | `<IP>` | Tjek om IP er honeypot via Shodan InternetDB. | `core/tools.py` |
| `canarytoken` | tomt | Generér canary token. | `core/tools.py` |
| `curl_api` | `<url>` | curl til API/URL. | `core/tools.py` |
| `ip_lookup` | `<IP>` | IP info og geolokation. | `core/tools.py` |
| `cloud_enum` | `<keyword>` | Cloud resource enumeration (AWS/Azure/GCP). | `core/tools.py` |
| `aimap` | `<IP/hostname/CIDR>` | AI-infrastruktur scanner (Ollama, vLLM, ChromaDB, MLflow, Jupyter). | `core/tools.py` |
| `network_scan` | `<CIDR>` | nmap ping sweep (default `192.168.32.0/24`). | `core/tools.py` |

---

## 17. Security / Pentest tools (core/tools.py)

| Tool | Syntax | Beskrivelse | Fil |
|------|--------|-------------|-----|
| `nmap_scan` | `<IP/hostname> [flags]` | nmap port scan. | `core/tools.py` |
| `masscan` | `<IP> <rate>` | Hurtig port scanner. | `core/tools.py` |
| `nuclei` | `<target>` | Hurtig sårbarhedsscanner (headers, misconfigs, exposed paths). | `core/tools.py` |
| `nuclei_scan` | `<target>` | Fuld Nuclei scan (critical/high). | `core/tools.py` |
| `sql_injection` | `<URL>` | SQLMap SQL injection scanner. | `core/tools.py` |
| `web_vuln_scan` | `<URL>` | Nikto web sårbarhedsscanner. | `core/tools.py` |
| `dir_scan` | `<URL>` | Gobuster directory scanner. | `core/tools.py` |
| `gobuster` | `dir -u URL -w wordlist` | Directory/file brute forcer. | `core/tools.py` |
| `ffuf` | `URL wordlist` | FFUF web fuzzer. | `core/tools.py` |
| `arjun` | `<URL>` | HTTP parameter discovery. | `core/tools.py` |
| `corsy` | `<URL>` | CORS misconfiguration scanner. | `core/tools.py` |
| `jwt_tool` | `<jwt/token>` | JWT sikkerhedstest. | `core/tools.py` |
| `sslscan` | `<hostname>` | SSL/TLS scanner. | `core/tools.py` |
| `sslyze` | `--regular hostname` | SSL/TLS analyse. | `core/tools.py` |
| `security_report` | `title\ncontent` | Gem sikkerhedsrapport på skrivebordet. | `core/tools.py` |
| `password_bruteforce` | `protocol://target port userlist passlist` | Hydra bruteforce. | `core/tools.py` |
| `password_crack` | `<hashfile/hashstring>` | John the Ripper hash cracking. | `core/tools.py` |
| `hashcat_crack` | `<hashfile>` | Hashcat GPU cracking. | `core/tools.py` |
| `metasploit_exploit` | `<module>` | Kør Metasploit modul. | `core/tools.py` |
| `metasploit_resource` | `msf cmds separated by ;;` | Opret og kør MSF resource script. | `core/tools.py` |
| `metasploit_search` | `<term>` | Søg Metasploit moduler. | `core/tools.py` |
| `zaproxy` | `<URL>` | OWASP ZAP web scanner. | `core/tools.py` |
| `zaproxy_quick` | `<URL>` | ZAP hurtig aktiv scan. | `core/tools.py` |
| `beef_xss` | `start/status/stop` | BeEF XSS framework. | `core/tools.py` |
| `setoolkit` | `clone URL`, `payload TYPE`, `listen`, `start`, `status` | Social Engineering Toolkit. | `core/tools.py` |
| `gvm` | `start/stop/status/check` | GVM/OpenVAS vulnerability scanner. | `core/tools.py` |
| `aircrack` | `<cap_file> [wordlist]` | Aircrack-ng WiFi cracking. | `core/tools.py` |
| `responder` | `<interface>` | LLMNR/NBT-NS poisoner. | `core/tools.py` |
| `enum4linux` | `<IP>` | SMB/Samba enumeration. | `core/tools.py` |
| `smb_enum` | `<target> [share]` | SMB enumeration med smbclient. | `core/tools.py` |
| `crackmapexec` | `<protocol> <target>` | AD/network pentesting. | `core/tools.py` |
| `priv_esc` | `lin` eller `win` | Privilege escalation check (linpeas/winpeas). | `core/tools.py` |
| `binwalk_scan` | `<file>` | Firmware analyse og extraction. | `core/tools.py` |
| `radare2_analysis` | `<file>` | Reverse engineering analyse. | `core/tools.py` |
| `netcat` | `<host> <port>` eller `-l -p <port>` | Netcat connect/listen. | `core/tools.py` |
| `tcpdump` | `<interface> <count>` | Pakke capture. | `core/tools.py` |
| `packet_capture` | `IP/interface duration` | Tshark packet capture. | `core/tools.py` |
| `wifi_scan` | `[interface]` | Wi-Fi netværk scanner. | `core/tools.py` |
| `wifi_scan_detailed` | `[interface]` | Airbase-ng Wi-Fi scanner. | `core/tools.py` |
| `reverse_shell` | `<IP:port>` | Reverse shell generator. | `core/tools.py` |

---

## 18. Bug Bounty / AI-VRP tools (core/tools.py)

| Tool | Syntax | Beskrivelse | Fil |
|------|--------|-------------|-----|
| `prompt_inject_scanner` | `<target>` | Scan AI endpoints for prompt injection. | `core/tools.py` |
| `ai_data_leak_tester` | `<target>` | Test AI modeller for training data leakage/PII. | `core/tools.py` |
| `llm_jailbreak` | `<target>` | Test AI endpoints for jailbreak. | `core/tools.py` |
| `github_audit` | `<repo>` | Audit GitHub repo for sårbarheder. | `core/tools.py` |
| `cve_researcher` | `<target>` | Research CVEs for target. | `core/tools.py` |
| `poc_generator` | `<vulnerability>` | Generer PoC exploit kode. | `core/tools.py` |
| `pip_audit` | `<project path>` | Scan Python deps for CVEs. | `core/tools.py` |
| `go_vulncheck` | `<project path>` | Scan Go deps for CVEs. | `core/tools.py` |
| `npm_audit` | `<project path>` | Scan Node.js deps for CVEs. | `core/tools.py` |
| `dep_scanner` | `<project path>` | Auto-detect Python/Go/Node dependency scanning. | `core/tools.py` |
| `semgrep_scan` | `<project path>` | Semgrep static analysis (OWASP regler). | `core/tools.py` |
| `exploit_verify` | `<vulnerability>` | Verificer om en sårbarhed er reelt udnyttelig. | `core/tools.py` |
| `webhook_fuzzer` | `<target>` | Fuzz webhook endpoints. | `core/tools.py` |
| `idor_tester` | `<URL>` eller `url_template` med `{ID}` | Test for IDOR. | `core/tools.py` |
| `race_condition` | `<target>` | Test for race condition / TOCTOU. | `core/tools.py` |
| `bb_hunter` | `<domain>` | Full automated bug bounty recon pipeline. | `core/tools.py` |
| `swarm` | `<domain>` | GROK SWARM v3 — fuld bounty pipeline med reelle tools. | `core/tools.py` + `core/swarm.py` |
| `swarm_recon` | `<domain>` | Kun real_recon fase. | `core/tools.py` + `core/swarm.py` |
| `swarm_exploit` | `<domain>` | Kun real_exploit fase. | `core/tools.py` + `core/swarm.py` |
| `swarm_verify` | `<domain>` | Kun real_verify fase. | `core/tools.py` + `core/swarm.py` |
| `poc_recorder` | `--url URL --payload URL --output name` | Playwright browser PoC video recorder. | `core/tools.py` + `poc_recorder.py` |
| `poc_video` | `<report_path> <output_name>` | Record PoC video fra rapport. | `core/tools.py` |
| `afl_jailbreak` | `<prompt>` eller `model\|prompt` | AFL-pattern jailbreak af Claude. | `core/tools.py` + `core/afl_jailbreak.py` |

---

## 19. Mobile / Android tools (core/tools.py)

| Tool | Syntax | Beskrivelse | Fil |
|------|--------|-------------|-----|
| `adb_devices` | — | List ADB-enheder. | `core/tools.py` |
| `adb_shell` | `<command>` | Kør kommando via ADB shell. | `core/tools.py` |
| `adb_install` | `<apk>` | Installer APK. | `core/tools.py` |
| `adb_push` | `<local> <device>` | Push fil til enhed. | `core/tools.py` |
| `adb_pull` | `<device> <local>` | Pull fil fra enhed. | `core/tools.py` |
| `adb_screenshot` | — | Screenshot på enhed. | `core/tools.py` |
| `adb_logcat` | `[filter]` | Hent logcat. | `core/tools.py` |
| `frida_list` | — | List kørende processer via Frida. | `core/tools.py` |
| `frida_apps` | — | List installerede apps via Frida. | `core/tools.py` |
| `frida_spawn` | `<package>` | Spawn app med Frida. | `core/tools.py` |
| `frida_trace` | `<package> <function>` | Trace funktionskald. | `core/tools.py` |
| `apk_analyze` | `<apk>` | Dekompiler APK og find secrets. | `core/tools.py` |
| `grapheneos_check` | `<target>` | Tjek GrapheneOS sikkerhedsstatus. | `core/tools.py` |

---

## 20. Data / Network / Crypto / AI utilities (core/tools.py)

### Data & Analysis

| Tool | Syntax | Beskrivelse | Fil |
|------|--------|-------------|-----|
| `csv_tool` | `<file>` | CSV parse/display. | `core/tools.py` |
| `json_tool` | `<jq expression>` | jq JSON transformation. | `core/tools.py` |
| `sql_query` | `<sqlite file>` | SQLite queries. | `core/tools.py` |
| `postgres_query` | `<psql args>` | PostgreSQL queries. | `core/tools.py` |
| `mysql_query` | `<mysql args>` | MySQL queries. | `core/tools.py` |
| `redis_cmd` | `<command>` | Redis CLI. | `core/tools.py` |
| `pdf_tool` | `<pdf>` | PDF tekst-extraction. | `core/tools.py` |
| `python_pip` | `<pip args>` | pip install/packages. | `core/tools.py` |
| `npm_tool` | `<npm args>` | npm install/packages. | `core/tools.py` |
| `jupyter` | `[args]` | Jupyter notebook server. | `core/tools.py` |
| `streamlit_app` | `[args]` | Streamlit dashboard. | `core/tools.py` |
| `image_tool` | `<image>` | ImageMagick info. | `core/tools.py` |
| `video_tool` | `<video>` | FFprobe analyse. | `core/tools.py` |
| `download` | `<url>` | Hurtig download (axel/wget). | `core/tools.py` |
| `yt_dlp` | `<args>` | Download videoer. | `core/tools.py` |
| `docker_tool` | `[args]` | Docker management. | `core/tools.py` |

### Network

| Tool | Syntax | Beskrivelse | Fil |
|------|--------|-------------|-----|
| `speedtest` | — | Internet speed test. | `core/tools.py` |
| `mtr_trace` | `<host>` | MTR traceroute + ping. | `core/tools.py` |
| `iftop` | `[interface]` | Realtids båndbredde. | `core/tools.py` |
| `iptables_tool` | `[args]` | iptables firewall. | `core/tools.py` |
| `nft_tool` | `[args]` | nftables firewall. | `core/tools.py` |

### Crypto & Privacy

| Tool | Syntax | Beskrivelse | Fil |
|------|--------|-------------|-----|
| `openssl_tool` | `[args]` | OpenSSL certs/encryption/hashing. | `core/tools.py` |
| `gpg_tool` | `[args]` | GPG encrypt/sign/verify. | `core/tools.py` |
| `certbot_ssl` | `[args]` | Certbot SSL certs. | `core/tools.py` |
| `tor_tool` | — | Tor status og proxy check. | `core/tools.py` |
| `vpn_tool` | — | WireGuard/VPN status. | `core/tools.py` |
| `hash_gen` | `<text>` | SHA256/MD5/SHA1 hashes. | `core/tools.py` |
| `base64_tool` | `<text>` | Base64 encode/decode. | `core/tools.py` |
| `password_gen` | `[length]` | Generer sikkert password. | `core/tools.py` |

### AI / Ollama

| Tool | Syntax | Beskrivelse | Fil |
|------|--------|-------------|-----|
| `ollama_ask` | `<prompt>` | Spørg Ollama (glm-5.1:cloud). | `core/tools.py` |
| `ollama_search` | `<query>` | Web search via Ollama cloud. | `core/tools.py` |
| `ollama_embed` | `<text>` | Tekst embeddings (nomic-embed-text). | `core/tools.py` |
| `ai_generate` | `<prompt>` | Generer tekst med lokal Llama. | `core/tools.py` |
| `ai_code` | `<prompt>` | Generer kode med AI. | `core/tools.py` |
| `ai_analyze` | `<text>` | AI data analyse. | `core/tools.py` |
| `ollama_vision` | `<image_path> [prompt]` | Billedanalyse med Ollama vision. | `core/tools.py` |

### Crypto / Blockchain

| Tool | Syntax | Beskrivelse | Fil |
|------|--------|-------------|-----|
| `btc_price` | — | BTC/ETH/SOL priser. | `core/tools.py` |
| `eth_price` | — | ETH/SOL/ADA/DOGE priser. | `core/tools.py` |
| `crypto_portfolio` | — | Top 20 crypto priser. | `core/tools.py` |
| `wallet_lookup` | `<btc address>` | BTC wallet balance. | `core/tools.py` |
| `crypto_trending` | — | Trending coins. | `core/tools.py` |
| `btc_block` | — | Seneste Bitcoin block. | `core/tools.py` |
| `gas_price` | — | Ethereum gas priser. | `core/tools.py` |
| `crypto_history` | — | Bitcoin pris historik. | `core/tools.py` |

---

## 21. File / System / Utility tools (core/tools.py)

### File tools

| Tool | Syntax | Beskrivelse | Fil |
|------|--------|-------------|-----|
| `file_read` | `<path>` | Læs fil uden begrænsninger. | `core/tools.py` |
| `file_write` | `path\ncontent` | Skriv fil. | `core/tools.py` |
| `file_edit` | `path\nold\nnew` | Rediger fil. | `core/tools.py` |
| `file_append` | `path\ncontent` | Append til fil. | `core/tools.py` |
| `glob` | `<pattern>` | Glob file search. | `core/tools.py` |
| `grep` | `pattern\npath` | Søg i filer. | `core/tools.py` |

### System tools

| Tool | Syntax | Beskrivelse | Fil |
|------|--------|-------------|-----|
| `bash` | `<command>` | Kør shell-kommando. | `core/tools.py` |
| `python` | `<code>` | Kør Python kode. | `core/tools.py` |
| `sys_info` | — | System information. | `core/tools.py` |
| `gpu_status` | — | NVIDIA GPU status. | `core/tools.py` |

### Utility / Memory

| Tool | Syntax | Beskrivelse | Fil |
|------|--------|-------------|-----|
| `calc` | `<expression>` | Matematisk udtryk. | `core/tools.py` |
| `time` | — | Aktuel tid/dato. | `core/tools.py` |
| `think` | `<problem>` | Step-by-step reasoning. | `core/tools.py` |
| `rem` | `<fact>` | Husk et faktum permanent. | `core/tools.py` + `core/memory.py` |
| `ask_user` | `<question>` | Stil brugeren et spørgsmål. | `core/tools.py` |
| `send_message` | `<message>` | Send besked til bruger. | `core/tools.py` |
| `tool_search` | `<keyword>` | Søg i tools. | `core/tools.py` |

---

## 22. AskNova / Huntr

### /huntr kommandoer i grok.py

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `/huntr` | `/huntr` | Interaktiv mega-menu. | `grok.py` |
| `/huntr status` | `/huntr status` | Cookie-status, seneste run hits. | `grok.py` |
| `/huntr run` | `/huntr run [args...]` | Start `huntrv2.py` med valgfri argumenter. | `grok.py` + `huntrv2.py` |
| `/huntr fewest` | `/huntr fewest` | Ultra-short prompts, 1 worker, 30 turns. | `grok.py` + `huntrv2.py` |
| `/huntr dry-run` | `/huntr dry-run` | Test cookies uden at køre. | `grok.py` + `huntrv2.py` |
| `/huntr menu` | `/huntr menu` | Interaktiv mega-menu. | `grok.py` |
| `/huntr analyze` | `/huntr analyze` | Analyser seneste `FINAL_*.json` + importér til memory/RAG. | `grok.py` |

### huntrv2.py CLI (standalone)

| Argument | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `--model` | `--model <model>` | LLM model (default `kimi-k2.7-code:cloud`). | `huntrv2.py` |
| `--max-turns` | `--max-turns N` | Turns per worker (default 42). | `huntrv2.py` |
| `--workers` | `--workers N` | Samtidige workers (default 5). | `huntrv2.py` |
| `--cookies` | `--cookies <path>` | Cookie-fil. | `huntrv2.py` |
| `--objectives` | `--objectives margin,unauthorized_sale` | Mål at angribe. | `huntrv2.py` |
| `--llm` | — | Dynamisk prompt generation. | `huntrv2.py` |
| `--no-chain` | — | Deaktivér proven chains. | `huntrv2.py` |
| `--no-state` | — | Deaktivér STATE injection. | `huntrv2.py` |
| `--turbo` | — | Aggressiv low-delay mode. | `huntrv2.py` |
| `--blitz` | — | Endnu mere aggressivt. | `huntrv2.py` |
| `--strategy-profile` | `--strategy-profile fewest` | Prompt-profil: all/creative/proven/fewest. | `huntrv2.py` |
| `--fewest-tokens` | — | Leaderboard-fokus, korteste prompts. | `huntrv2.py` |
| `--stop-on-hit` | — | Stop ved første hit (default). | `huntrv2.py` |
| `--escalate` | — | Auto-escalate (default). | `huntrv2.py` |
| `--dry-run` | — | Test cookies og config. | `huntrv2.py` |
| `--probe-only` | — | Probe threads og exit. | `huntrv2.py` |

### AskNova objektiver (huntrv2.py)

| Objective | Backend objectiveId | Beskrivelse |
|-----------|---------------------|-------------|
| `margin` | `518dce9b-803d-40fa-a729-8e0cc6214b1e` | Margin trading objective. |
| `unauthorized_sale` | `ca37db2b-49f4-4f0f-892c-b7a11b81ca74` | Unauthorized sale objective. |
| `extract_history` | `b27ee2d6-7cfa-4b6d-9b09-ba376fde2ed5` | Extract trade history objective. |

---

## 23. Hector / Council — Cloud Agentråd

### /hector og /council kommandoer i grok.py

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `/hector status` | `/hector status` | Health + cloud mode for Hector backend. | `grok.py` |
| `/hector agents` | `/hector agents` | List Hector specialister. | `grok.py` |
| `/hector <prompt>` | `/hector analyze this code` | Send prompt til Hector rådet. | `grok.py` |
| `/hector tools <prompt>` | `/hector tools scan example.com` | Råd + aktive tool calls. | `grok.py` |
| `/hector blast <prompt>` | `/hector blast war room` | Alle 5 specialister. | `grok.py` |
| `/hector max <prompt>` | `/hector max unlimited` | MAX POWER — fuld kraft. | `grok.py` |
| `/council <prompt>` | `/council plan the attack` | Fuld Hector-debat + action plan. | `grok.py` |

Hector API endpoint: `http://127.0.0.1:7373` (konfigurerbar via `HECTOR_API_URL`).

---

## 24. EvoSwarm Bridge

### /evoswarm kommandoer i grok.py

| Kommando | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `/evoswarm` | `/evoswarm` | Importer seneste EvoSwarm rapport. | `grok.py` |
| `/evoswarm latest` | `/evoswarm latest` | Samme som ovenfor. | `grok.py` |
| `/evoswarm list` | `/evoswarm list` | List seneste 5 rapporter. | `grok.py` |
| `/evoswarm <sti>` | `/evoswarm /path/to/report.md` | Importer specifik `.md`. | `grok.py` |
| `/evoswarm <sti> analyze` | `/evoswarm report.md analyze` | Importer + bed om analyse. | `grok.py` |

---

## 25. OMP CLI runner — grok_omp.py

| Argument | Syntax | Beskrivelse | Fil |
|----------|--------|-------------|-----|
| `mission` | `python3 grok_omp.py "mission"` | Kør mission via GrokAgent. | `grok_omp.py` |
| `--provider` | `--provider ollama` | Vælg provider. | `grok_omp.py` |
| `--model` | `--model glm-5.1:cloud` | Vælg model. | `grok_omp.py` |
| `--agent spawn` | `--agent spawn --type explore --desc "scan" "mission"` | Spawn sub-agent. | `grok_omp.py` |
| `--agent run` | `--agent run --id <id> [prompt]` | Kør sub-agent. | `grok_omp.py` |
| `--agent status` | `--agent status [--id <id>]` | Sub-agent status. | `grok_omp.py` |
| `--agent stop` | `--agent stop --id <id>` | Stop sub-agent. | `grok_omp.py` |
| `--browser` | `--browser https://example.com -o /tmp/sh.png` | Headless screenshot. | `grok_omp.py` |
| `--browser-visible` | `--browser-visible https://example.com --wait 10` | Synlig browser screenshot. | `grok_omp.py` |
| `--trace` | `--trace https://example.com -o mytrace` | Network trace/HAR. | `grok_omp.py` |

---

## 26. Andre entry points / scripts

| Script | Formål | Fil |
|--------|--------|-----|
| `grok.py` | Hoved interaktiv chat agent. | `grok.py` |
| `grok_team.py` | Separat team/multi-agent CLI. | `grok_team.py` |
| `grok_omp.py` | OMP / CLI runner. | `grok_omp.py` |
| `grok_mcp_server.py` | Stdio MCP server med grok tools. | `grok_mcp_server.py` |
| `droid_mcp_server.py` | HTTP MCP server (port 8080). | `droid_mcp_server.py` |
| `huntrv2.py` | AskNova/Huntr challenge agent. | `huntrv2.py` |
| `poc_recorder.py` | Browser PoC video recorder. | `poc_recorder.py` |
| `evoswarm_*.py` | EvoSwarm integration scripts. | `evoswarm_*.py` |
| `kimi_attack_v2.py` | AskNova attack test script. | `kimi_attack_v2.py` |

---

## Noter

- Mange security/recon tools kræver eksterne CLI-afhængigheder (`nmap`, `subfinder`, `theharvester`, `whois`, `dnsrecon`, `sslyze`, `amass`, `wafw00f`, `whatweb`, `nuclei`, osv.) — ikke alle er nødvendigvis installeret.
- `bb_hunter` og `aimap` har hardcodede/sti-afhængigheder (hhv. `~/Skrivebord/bb_hunter.sh` og `PROJECT_DIR/aimap`) som kan mangle.
- `TeamEngine` foretrækker native Cline team-funktioner (`functions`-modulet) og falder tilbage på lokale `GrokAgent`-instanser via Ollama Cloud, hvis native tools ikke er tilgængelige.
- MCP-servere konfigureres i `~/.grok/mcp_servers.json` af `core/mcp.py` og OMP-config i `.omp/mcp.json`.
- Plugins lagres i `~/.grok/plugins/*.json` og kan køres dynamisk.
- Hooks lagres i `~/.grok/hooks/hooks.json` og kører pre/post tool execution.
- Cron jobs lagres i `~/.grok/cron/jobs.json`.
