# 🥷 SuperNinja Sandbox – Din egen AI-agent computer i VS Code

Dette projekt genskaber den fulde SuperNinja AI-agent sandbox-maskine som et VS Code Dev Container. Du får præcis det samme miljø som jeg kører i – Debian 12, Python 3.11, Node.js 20, og alle mine værktøjer.

## Hvad er inkluderet

**Operativsystem:** Debian 12 (bookworm) – det samme Linux som SuperNinja kører på

**Programmeringssprog:**
- Python 3.11 med 50+ pakker (fastapi, pandas, numpy, matplotlib, mcp, og meget mere)
- Node.js 20.x med TypeScript, pm2, serve, nodemon

**Værktøjer:**
| Værktøj | Formål |
|---------|--------|
| `git`, `gh` (GitHub CLI) | Versionsstyring & GitHub |
| `jq`, `csvkit`, `xmlstarlet` | Data behandling (JSON, CSV, XML) |
| `poppler-utils`, `wkhtmltopdf` | PDF generering og konvertering |
| `antiword`, `unrtf`, `catdoc` | Dokument konvertering |
| `grep`, `awk`, `sed` | Tekst søgning og manipulation |
| `wget`, `curl` | HTTP klienter |
| `tmux`, `vim`, `tree` | Terminal værktøjer |
| `rsync`, `zip`, `unzip` | Fil synkronisering og arkivering |
| `htop`, `procps` | Proces overvågning |
| `ruff`, `pylance` | Python linting & type checking |

**VS Code Extensions (auto-installeret):**
- Python, Pylance, Jupyter
- GitLens, ESLint, Prettier
- Continue.dev (AI coding assistant – kan forbindes til Ollama!)
- Docker, YAML, TOML, Markdown

## 🚀 Installation – Trin for Trin

### Forudsætninger

1. **Installer Docker Desktop**
   - macOS: https://docker.com/products/docker-desktop
   - Windows: https://docker.com/products/docker-desktop (kræver WSL 2)
   - Linux: `curl -fsSL https://get.docker.com | sh`

2. **Installer VS Code**
   - Download: https://code.visualstudio.com

3. **Installer Dev Containers extension**
   - Åbn VS Code
   - Gå til Extensions (Ctrl/Cmd + Shift + X)
   - Søg efter "Dev Containers"
   - Klik Install

### Opsætning

#### Metode 1: Brug denne mappe direkte

```bash
# Clone dette projekt
git clone https://github.com/k4w-wak/ollama-silent-patches.git
cd ollama-silent-patches/superninja-devcontainer

# Åbn i VS Code
code .
```

I VS Code:
1. Tryk `Ctrl/Cmd + Shift + P`
2. Skriv "Dev Containers: Reopen in Container"
3. Vælg det
4. Vent mens Docker imaget bygges (5-10 minutter første gang)
5. 🎉 Du er nu inde i SuperNinja-maskinen!

#### Metode 2: Kopier .devcontainer til dit eget projekt

```bash
# Kopier .devcontainer mappen til dit projekt
cp -r superninja-devcontainer/.devcontainer /din/projekt/mappe/

# Åbn dit projekt i VS Code
code /din/projekt/mappe

# Tryk Ctrl/Cmd + Shift + P → "Dev Containers: Reopen in Container"
```

#### Metode 3: Quick start uden Git

1. Opret en ny mappe
2. Opret `.devcontainer/devcontainer.json` og `.devcontainer/Dockerfile` (kopier fra dette repo)
3. Åbn i VS Code → Reopen in Container

## 🔧 Efter Installation

Når containeren kører, har du:

```bash
🥷 superninja:/workspace$ python3 --version
Python 3.11.x

🥷 superninja:/workspace$ node --version
v20.x.x

🥷 superninja:/workspace$ jq --version
jq-1.6

🥷 superninja:/workspace$ gh --version
gh version 2.x.x
```

### Forbind Ollama (valgfrit)

Hvis du har Ollama kørende på din værtsmaskine:

```bash
# Fra containeren, test forbindelse
curl http://host.docker.internal:11434/version
```

I Continue.dev (allerede installeret), konfigurer modeller ved at klikke ⚙️ i Continue sidepanelet:

```json
{
  "models": [
    {
      "title": "Ollama Llama 3.1",
      "provider": "ollama",
      "model": "llama3.1:8b",
      "apiBase": "http://host.docker.internal:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Qwen Coder",
    "provider": "ollama",
    "model": "qwen2.5-coder:1.5b",
    "apiBase": "http://host.docker.internal:11434"
  }
}
```

## 🛠 Tilpasning

### Tilføj flere Python pakker

Rediger `Dockerfile` og tilføj til pip install sektionen:

```dockerfile
RUN pip3 install --no-cache-dir \
    din-pakke-her
```

### Tilføj flere VS Code extensions

Rediger `devcontainer.json` under `customizations.vscode.extensions`:

```json
"extensions": [
  "din-extension-id"
]
```

### Tilføj system pakker

Rediger `Dockerfile` og tilføj til apt-get sektionen:

```dockerfile
RUN apt-get update && apt-get install -y \
    din-pakke \
    && rm -rf /var/lib/apt/lists/*
```

Husk at rebuild containeren efter ændringer: `Ctrl/Cmd + Shift + P` → "Dev Containers: Rebuild Container"

## ⚡ Port Forwarding

Følgende ports er automatisk forwardet:

| Port | Typisk brug |
|------|-------------|
| 3000 | React, Next.js dev server |
| 5000 | Flask, Python server |
| 8000 | FastAPI, Django |
| 8080 | Node.js server |
| 11434 | Ollama API |

## 🐳 Docker Kommandoer

```bash
# Byg manuelt (hvis nødvendigt)
docker build -t superninja-sandbox .devcontainer/

# Kør manuelt
docker run -it -v $(pwd):/workspace superninja-sandbox

# Stop alle containere
docker stop $(docker ps -q)
```

## ❓ Fejlfinding

**"Cannot connect to Docker"**
- Sørg for Docker Desktop kører
- Prøv: `docker ps` i terminalen

**"Dev Containers: Reopen in Container fejler"**
- Tjek Docker logs: `docker logs <container-id>`
- Prøv at rebuild: `Ctrl/Cmd + Shift + P` → "Dev Containers: Rebuild Container"

**Langsom første build**
- Første build tager 5-10 minutter (downloader og installerer alt)
- Efterfølgende builds er hurtige takket være Docker cache

**Python pakke mangler**
- Tilføj den i Dockerfile og rebuild
- Eller installer midlertidigt: `pip3 install pakke-navn` (mistet ved rebuild)

## 📄 Licens

Dette dev container setup er open-source. Brug det som du vil!

---

🥷 **SuperNinja Sandbox** – Nu er MIN computer DIN computer!
