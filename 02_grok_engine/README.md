# 💀 GROK v4 — Autonomous Security Agent

Ollama FC • Thinking Mode • 6 Konger • 155 Tools • No GROQ

## Features

### 🧠 Ollama Integration
- **Tool Calling (FC)** — 138 tools, ingen rate limits, ingen 413 errors
- **Thinking Mode** — viser 💭 reasoning trace (glm-5.1:cloud, glm-5:cloud, minimax-m2.7:cloud)
- **Structured Output** — JSON schema enforcement (fallback mode)
- **keep_alive** — 5m model caching for hurtigere responses
- **Vision** — ollama_vision tool (billedanalyse)
- **Embeddings** — ollama_embed tool (nomic-embed-text, 768 dims)
- **Cloud Search** — ollama_search tool

### 💀 6 Konger (Security Tools)
| Konge | Tool | Status |
|-------|------|--------|
| 💀 Metasploit | metasploit, msf_search, msf_script, metasploit_exploit | ✅ Auto LHOST, resource scripts, smart timeout |
| 🕸️ BeEF | beef | ✅ Auto IP, hook/status/start |
| 🎭 SET | setoolkit | ✅ clone/payload/listen |
| 🔍 ZAP | zaproxy, zap_scan | ✅ Daemon API, cleanup, -cmd fix |
| 🛡️ GVM | gvm | ✅ fix certs, status check, auto-init |
| 📡 Burp | burpsuite | ✅ Info page (GUI required) |

### 🔧 Agent Features
- Auto LHOST detection (_get_local_ip)
- Smart timeouts (scanner=300s, exploit=180s)
- Universal fallback (input→target parameter mapping)
- Ollama FC with 138 tools (no GROQ)
- Memory with thinking trace
- Background hacker IP monitor (176.130.181.234)

### 🛠️ CLI Tools (for assistant)
- `ollama-think 'problem'` — Thinking Mode
- `ollama-see image.png` — Vision analysis
- `ollama-embed 'text'` — Text embeddings
- `ollama-ask [model] 'prompt'` — Ask any model

## Models
| Model | Capabilities | Type |
|-------|-------------|------|
| glm-5.1:cloud | thinking, completion, tools | Cloud |
| glm-5:cloud | thinking, completion, tools | Cloud |
| minimax-m2.7:cloud | completion, tools, thinking | Cloud |
| llama3.1:8b | completion, tools | Local |
| llama3.2:3b | completion, tools | Local |
| nomic-embed-text | embeddings | Local |

## Architecture
```
User → grok_run.py → GrokAgent → ModelRouter → Ollama (glm-5.1:cloud)
                                          ↓
                                    FC (138 tools)
                                          ↓
                                    execute_tool_call()
                                          ↓
                                    6 Konger + OSINT + web + file + system
```

## Konfiguration
- Provider: Ollama (GROQ fjernet)
- Default model: glm-5.1:cloud
- Fallback: glm-5:cloud → minimax-m2.7:cloud → llama3.1:8b → llama3.2:3b
- Max iterations: 20
- No sandbox, no command filters

## Hackers IP Monitor
- Target: 176.130.181.234 (Bouygues Telecom, Pierrelatte FR)
- Monitor: Ping hvert minut, nmap scan ved online
- Logs: ~/Skrivebord/hacker_undersoegelse/hacker_ip_monitor.log
