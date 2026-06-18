#!/usr/bin/env python3
"""
EvoSwarm v2.2 MAX++ POWER — Cloud-only, parallel, stateful, logged, smart, self-improving.

MEGA MENU EDITION:
- Interaktiv menu ved kørsel uden argumenter.
- Integrerer funktionalitet fra evoswarm_v2_max.py, evoswarm_easy.py og evoswarm_grok_bridge.py.
- Cloud modeller kan vælges direkte i menuen.
- Eksisterende CLI-argumenter (topic, rounds) bevares og virker i batch-mode.

Forbedringer:
- Streaming output fra cloud-modeller.
- Token / cost tracking med rough estimat.
- Multi-topic batch mode.
- Circuit breaker + fallback model.
- Persistent hukommelse på tværs af kørsler.
- Meta-agent laver final synthesis af hele debatten.
- Self-improvement loop: agenter kan revidere system prompts.
- Alle agenter + evolution kører i parallel.
- Per-model latens-statistik.
- Rate-limiter så vi ikke hamrer API’et.
- Rig kontekst med citater fra sidste runde.
- Syntetiker-agent laver resume efter hver runde.
- Markdown-rapport genereres automatisk.
- SIGINT gemmer delresultater pænt.
- Konfigurerbar via .env / miljøvariabler.

Sikkerhed:
- API-nøglen læses fra .env eller OLLAMA_API_KEY.
- Nøglen hardcodes aldrig i koden.
"""

import os
import sys
import json
import time
import math
import glob
import signal
import threading
import functools
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Dict, List, Optional
from collections import defaultdict

import requests
from dotenv import load_dotenv

load_dotenv()

# ====================== CONFIG ======================
OLLAMA_URL = os.getenv("OLLAMA_URL", "https://ollama.com/v1/chat/completions")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "").strip()
if not OLLAMA_API_KEY:
    print("[FEJL] OLLAMA_API_KEY ikke sat. Læg den i .env eller export OLLAMA_API_KEY=...")
    sys.exit(1)

MAX_WORKERS = int(os.getenv("MAX_WORKERS", "8"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "90"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "1.5"))
DEFAULT_ROUNDS = int(os.getenv("DEFAULT_ROUNDS", "5"))
LOG_DIR = os.path.abspath(os.getenv("LOG_DIR", os.path.join(os.path.dirname(__file__), "evoswarm_logs")))
REPORTS_DIR = os.path.abspath(os.getenv("REPORTS_DIR", os.path.join(os.path.dirname(__file__), "..", "reports")))
RATE_LIMIT_QPS = float(os.getenv("RATE_LIMIT_QPS", "5.0"))

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
RUN_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(LOG_DIR, f"evoswarm_{RUN_TIMESTAMP}.jsonl")
REPORT_FILE = os.path.join(LOG_DIR, f"evoswarm_{RUN_TIMESTAMP}.md")
MEMORY_FILE = os.path.join(LOG_DIR, "evoswarm_memory.json")

_SHUTDOWN_REQUESTED = threading.Event()

# ====================== CLOUD MODELS ======================
# Godkendte cloud modeller som kan vælges i menuen.
CLOUD_MODELS = [
    "glm-5.1:cloud",
    "kimi-k2.7-code:cloud",
    "minimax-m3:cloud",
    "deepseek-v4-flash:cloud",
]

# ====================== UTILS ======================
def log_event(event_type: str, payload: dict):
    entry = {
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "run": RUN_TIMESTAMP,
        "type": event_type,
    }
    entry.update(payload)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[LOG-FEJL] {e}")

class RateLimiter:
    def __init__(self, qps: float):
        self.min_interval = 1.0 / max(qps, 0.1)
        self.last_time = 0.0
        self.lock = threading.Lock()

    def acquire(self):
        with self.lock:
            now = time.time()
            wait = self.last_time + self.min_interval - now
            if wait > 0:
                time.sleep(wait)
                now = time.time()
            self.last_time = now

rate_limiter = RateLimiter(RATE_LIMIT_QPS)

# ====================== OLLAMA CLOUD ======================
_latency_stats: Dict[str, List[float]] = defaultdict(list)
_latency_lock = threading.Lock()

# Cost tracking rough estimates (USD per 1M tokens output)
_COST_PER_1M_OUTPUT = {
    "glm-5.1:cloud": 0.002,
    "kimi-k2.7-code:cloud": 0.008,
    "minimax-m3:cloud": 0.005,
    "deepseek-v4-flash:cloud": 0.0008,
}
_cost_stats: Dict[str, Dict[str, float]] = defaultdict(lambda: {"calls": 0, "tokens_est": 0.0, "cost": 0.0})
_cost_lock = threading.Lock()

_circuit_failures: Dict[str, int] = defaultdict(int)
_circuit_lock = threading.Lock()
CIRCUIT_THRESHOLD = int(os.getenv("CIRCUIT_THRESHOLD", "3"))
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "glm-5.1:cloud")

def _estimate_tokens(text: str) -> int:
    # Rough estimate: ~1.4 tokens per word in Danish/English mix
    return int(len(text.split()) * 1.4)

def _record_cost(model: str, response_text: str):
    tokens = _estimate_tokens(response_text)
    rate = _COST_PER_1M_OUTPUT.get(model, 0.005)
    cost = (tokens / 1_000_000) * rate
    with _cost_lock:
        _cost_stats[model]["calls"] += 1
        _cost_stats[model]["tokens_est"] += tokens
        _cost_stats[model]["cost"] += cost
    return tokens, cost

def get_cost_summary() -> Dict[str, Dict[str, float]]:
    summary = {}
    with _cost_lock:
        for model, s in _cost_stats.items():
            summary[model] = {
                "calls": s["calls"],
                "tokens_est": round(s["tokens_est"], 0),
                "cost_usd": round(s["cost"], 6),
            }
    return summary

def _circuit_open(model: str) -> bool:
    with _circuit_lock:
        return _circuit_failures[model] >= CIRCUIT_THRESHOLD

def _record_failure(model: str):
    with _circuit_lock:
        _circuit_failures[model] += 1

def _record_success(model: str):
    with _circuit_lock:
        _circuit_failures[model] = max(0, _circuit_failures[model] - 1)

def call_ollama(model: str, system: str, user: str, stream: bool = False) -> str:
    if _circuit_open(model):
        print(f"⚠️ Circuit breaker åben for {model}, fallback til {FALLBACK_MODEL}")
        model = FALLBACK_MODEL

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": 1400,
        "temperature": 0.82,
        "stream": stream,
    }
    headers = {
        "Authorization": f"Bearer {OLLAMA_API_KEY}",
        "Content-Type": "application/json",
    }

    last_err = ""
    for attempt in range(1, MAX_RETRIES + 1):
        if _SHUTDOWN_REQUESTED.is_set():
            return "[AFBRUDT] Brugeren stoppede kørslen."
        try:
            rate_limiter.acquire()
            start = time.time()
            r = requests.post(OLLAMA_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT, stream=stream)
            elapsed = time.time() - start
            with _latency_lock:
                _latency_stats[model].append(elapsed)

            if r.status_code == 200:
                if stream:
                    chunks = []
                    try:
                        for line in r.iter_lines():
                            if line:
                                decoded = line.decode("utf-8").strip()
                                if decoded.startswith("data: "):
                                    decoded = decoded[6:]
                                if decoded == "[DONE]":
                                    break
                                try:
                                    chunk = json.loads(decoded)
                                    delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                    if delta:
                                        chunks.append(delta)
                                        print(delta, end="", flush=True)
                                except Exception:
                                    continue
                        if chunks:
                            print()  # newline after streaming
                    except Exception as e:
                        print(f"\n[STREAM FEJL] {e}")
                    content = "".join(chunks).strip()
                else:
                    data = r.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                _record_success(model)
                _record_cost(model, content)
                return content
            last_err = f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e:
            last_err = f"NETVÆRKSFEJL: {str(e)}"

        _record_failure(model)
        if attempt < MAX_RETRIES and not _SHUTDOWN_REQUESTED.is_set():
            log_event("retry", {"model": model, "attempt": attempt, "error": last_err})
            time.sleep(RETRY_DELAY * attempt)

    return f"[FEJL] {last_err}"

def get_latency_summary() -> Dict[str, Dict[str, float]]:
    summary = {}
    with _latency_lock:
        for model, times in _latency_stats.items():
            if times:
                summary[model] = {
                    "calls": len(times),
                    "total_sec": round(sum(times), 2),
                    "avg_sec": round(sum(times) / len(times), 2),
                    "min_sec": round(min(times), 2),
                    "max_sec": round(max(times), 2),
                }
    return summary


# ====================== AGENT ======================
class EvoAgent:
    def __init__(self, name: str, role: str, core_belief: str, model: str, memory_file: str = MEMORY_FILE):
        self.name = name
        self.role = role
        self.model = model
        self.core_belief = core_belief
        self.evolution_level = 0
        self.memory_file = memory_file
        self.memory: List[str] = []
        self.base_system = f"""Du er {name} — {role}.
Din kerne-overbevisning: {core_belief}

Du husker tidligere runder og udvikler dine synspunkter over tid.
Vær tro mod dig selv. Svar ærligt og i din egen stil."""
        self.system_prompt = self.base_system
        self._load_memory()
        log_event("agent_created", {
            "name": name, "role": role, "model": model, "belief": core_belief,
            "memory_loaded": len(self.memory)
        })

    def _load_memory(self):
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if self.name in data:
                    self.memory = data[self.name]["memory"][-10:]
                    self.evolution_level = data[self.name].get("evolution_level", 0)
                    loaded_evo = data[self.name].get("evolutions", [])
                    for evo in loaded_evo:
                        self.system_prompt += f"\n\n[Evolution {evo['level']}]: {evo['note']}"
        except Exception as e:
            print(f"[HUKOMMELSE-FEJL for {self.name}] {e}")

    def _save_memory(self):
        try:
            data = {}
            if os.path.exists(self.memory_file):
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            evolutions = []
            for line in self.system_prompt.split("\n"):
                if line.startswith("[Evolution "):
                    parts = line.split(": ", 1)
                    if len(parts) == 2:
                        level_str = parts[0][len("[Evolution "):-1]
                        evolutions.append({"level": level_str, "note": parts[1]})
            data[self.name] = {
                "memory": self.memory[-20:],
                "evolution_level": self.evolution_level,
                "evolutions": evolutions,
            }
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[GEM-HUKOMMELSE-FEJL for {self.name}] {e}")

    def respond(self, topic: str, round_num: int, previous: str) -> dict:
        memory_ctx = "\n".join(self.memory[-3:]) if self.memory else ""
        evolution = f"\n[Du har udviklet dig gennem {self.evolution_level} runder.]" if self.evolution_level > 0 else ""

        user_msg = f"""Runde {round_num}
Emne: {topic}

Tidligere diskussion:
{previous}

Din hukommelse:
{memory_ctx}
{evolution}

Svar som {self.name}. Max 6 sætninger."""

        response = call_ollama(self.model, self.system_prompt, user_msg, stream=False)
        self.memory.append(response[:380])
        self._save_memory()
        return {"agent": self.name, "model": self.model, "response": response}

    def evolve(self, summary: str):
        self.evolution_level += 1
        prompt = f"""Du er {self.name}.
Baseret på denne opsummering af runden: {summary}

Opdater din egen tankegang en smule. Skriv kun en kort intern note (max 60 ord)."""
        note = call_ollama(self.model, self.system_prompt, prompt, stream=False)
        self.system_prompt += f"\n\n[Evolution {self.evolution_level}]: {note}"
        self._save_memory()
        return {"agent": self.name, "evolution": self.evolution_level, "note": note}

    def self_improve(self) -> dict:
        prompt = f"""Du er {self.name}.
Din nuværende system-prompt:
{self.system_prompt}

Din kerne-overbevisning: {self.core_belief}

Gennemse din prompt og forslå ÉN kort præcisering eller justering (max 50 ord), der gør dig skarpere."""
        improvement = call_ollama(self.model, self.base_system, prompt, stream=False)
        self.system_prompt += f"\n\n[Self-Improvement]: {improvement}"
        self._save_memory()
        return {"agent": self.name, "improvement": improvement}


# ====================== SYNTHESIZER ======================
class SynthesizerAgent:
    def __init__(self, model: str = "glm-5.1:cloud"):
        self.model = model
        self.system = "Du er en analytisk syntetisator. Du skriver korte, præcise resuméer af diskussioner."

    def summarize(self, topic: str, round_num: int, responses: List[dict]) -> str:
        lines = [f"{r.get('agent', '?')}: {r.get('response', '')}" for r in responses if 'response' in r]
        user_msg = f"""Lav et meget kort resume (max 80 ord) af runde {round_num} om '{topic}'.

Citat:
{chr(10).join(lines)}

Fremhæv de vigtigste konflikter og indsigter."""
        return call_ollama(self.model, self.system, user_msg)


class MetaAgent:
    """Laver en endelig syntese af hele debatten."""
    def __init__(self, model: str = "kimi-k2.7-code:cloud"):
        self.model = model
        self.system = "Du er en meta-observatør. Du skriver en afsluttende, balanceret syntese af en længere debat."

    def synthesize(self, topic: str, rounds: List[dict]) -> str:
        lines = []
        for entry in rounds:
            lines.append(f"Runde {entry['round']}:")
            for r in entry["responses"]:
                if "response" in r:
                    lines.append(f"  {r['agent']}: {r['response'][:250]}")
        user_msg = f"""Skriv en afsluttende syntese (max 200 ord) af debatten om '{topic}'.

{chr(10).join(lines)}

Opsummer de vigtigste positioner, konflikter og konklusioner."""
        return call_ollama(self.model, self.system, user_msg)


# ====================== SWARM ======================
class EvoSwarm:
    def __init__(self, max_workers: int = MAX_WORKERS):
        self.agents: Dict[str, EvoAgent] = {}
        self.history: List[str] = []
        self.summaries: List[str] = []
        self.max_workers = max_workers
        self.synthesizer = SynthesizerAgent()
        self.meta_agent = MetaAgent()
        self.report_data: List[dict] = []
        self.final_synthesis = ""
        self.streaming_mode = os.getenv("STREAMING", "false").lower() in ("1", "true", "yes")
        log_event("swarm_created", {"max_workers": max_workers, "log_file": LOG_FILE})

    def add_agent(self, name: str, role: str, core_belief: str, model: str):
        self.agents[name] = EvoAgent(name, role, core_belief, model)
        print(f"✅ {name} ({role}) → {model}")

    def _format_context(self) -> str:
        if not self.report_data:
            return "Ingen tidligere runder."
        parts = []
        for entry in self.report_data[-2:]:
            parts.append(f"Runde {entry['round']}:")
            for r in entry["responses"]:
                if "response" in r:
                    parts.append(f"  - {r['agent']}: {r['response'][:180]}")
        return "\n".join(parts)

    def _run_round(self, topic: str, round_num: int) -> List[dict]:
        context = self._format_context()
        results = []

        print(f"\n─── RUNDE {round_num} ───")
        print(f"⚡ Fyrer {len(self.agents)} agenter af samtidig...")

        start = time.time()
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_agent = {
                executor.submit(agent.respond, topic, round_num, context): name
                for name, agent in self.agents.items()
            }
            for future in as_completed(future_to_agent):
                if _SHUTDOWN_REQUESTED.is_set():
                    future.cancel()
                    continue
                try:
                    result = future.result()
                    results.append(result)
                    print(f"→ {result['agent']}: {result['response']}\n")
                except Exception as e:
                    name = future_to_agent[future]
                    err = {"agent": name, "error": str(e)}
                    results.append(err)
                    print(f"[FEJL] {name}: {e}")

        elapsed = time.time() - start
        print(f"⏱ Runde {round_num} færdig på {elapsed:.2f}s")
        log_event("round_completed", {
            "round": round_num,
            "elapsed_seconds": round(elapsed, 2),
            "results": results,
        })
        return results

    def _evolve_agents(self, summary: str):
        print("🧬 Evolution fase...")
        evo_results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(agent.evolve, summary): name
                for name, agent in self.agents.items()
            }
            for future in as_completed(futures):
                if _SHUTDOWN_REQUESTED.is_set():
                    future.cancel()
                    continue
                try:
                    result = future.result()
                    evo_results.append(result)
                    print(f"   🧬 {result['agent']} evolved (niveau {result['evolution']})")
                except Exception as e:
                    print(f"[EVO-FEJL] {futures[future]}: {e}")
        log_event("evolution_completed", {"results": evo_results})

    def run_debate(self, topic: str, rounds: int = DEFAULT_ROUNDS) -> List[dict]:
        print(f"\n{'═'*70}")
        print(f"🚀 EVO DEBAT (MAX+ POWER): {topic}")
        print(f"{'═'*70}")
        print(f"Cloud URL: {OLLAMA_URL}")
        print(f"Rate-limit: {RATE_LIMIT_QPS} req/s | Workers: {self.max_workers} | Log: {LOG_FILE}\n")

        log_event("debate_started", {"topic": topic, "rounds": rounds})

        def signal_handler(sig, frame):
            print("\n🛑 Afslutning registreret — gemmer delresultater...")
            _SHUTDOWN_REQUESTED.set()

        signal.signal(signal.SIGINT, signal_handler)

        for r in range(1, rounds + 1):
            if _SHUTDOWN_REQUESTED.is_set():
                break

            results = self._run_round(topic, r)
            self.report_data.append({"round": r, "responses": results})
            self.history.append(f"Runde {r}: {json.dumps(results, ensure_ascii=False)}")

            if _SHUTDOWN_REQUESTED.is_set():
                break

            print("🧠 Syntetiserer runden...")
            summary = self.synthesizer.summarize(topic, r, results)
            self.summaries.append(summary)
            print(f"📋 Resume: {summary}\n")
            log_event("round_summary", {"round": r, "summary": summary})

            if r % 2 == 0:
                self._evolve_agents(summary)

        if not _SHUTDOWN_REQUESTED.is_set() and self.report_data:
            print("\n🧠 Meta-agent laver endelig syntese...")
            self.final_synthesis = self.meta_agent.synthesize(topic, self.report_data)
            print(f"📋 Endelig syntese: {self.final_synthesis}\n")
            log_event("final_synthesis", {"synthesis": self.final_synthesis})

            if rounds >= 3:
                print("🔧 Self-improvement fase...")
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = [executor.submit(agent.self_improve) for agent in self.agents.values()]
                    for future in as_completed(futures):
                        try:
                            result = future.result()
                            print(f"   🔧 {result['agent']} forbedrede sig")
                        except Exception as e:
                            print(f"[SELF-IMPROVE FEJL] {e}")

        self._write_report(topic, rounds)
        print("\n✅ Debat færdig — agenterne har udviklet sig.")
        print(f"💾 Log: {LOG_FILE}")
        print(f"📄 Rapport: {REPORT_FILE}")
        log_event("debate_finished", {"topic": topic, "rounds_completed": len(self.report_data)})
        return self.report_data

    def _write_report(self, topic: str, planned_rounds: int):
        lines = [
            f"# EvoSwarm v2.2 MAX++ Rapport",
            f"",
            f"**Emne:** {topic}",
            f"**Gennemførte runder:** {len(self.report_data)} / {planned_rounds}",
            f"**Tidsstempel:** {RUN_TIMESTAMP}",
            f"**Cloud URL:** {OLLAMA_URL}",
            f"",
            f"## Agenter",
            "",
        ]
        for name, agent in self.agents.items():
            lines.append(f"- **{name}** ({agent.role}) — model `{agent.model}`, evolution niveau {agent.evolution_level}")
        lines.append("")

        lines.extend(["## Runder", ""])
        for i, entry in enumerate(self.report_data, start=1):
            lines.append(f"### Runde {i}")
            for r in entry["responses"]:
                if "response" in r:
                    lines.append(f"**{r['agent']}** (`{r['model']}`):\n{r['response']}\n")
                else:
                    lines.append(f"**{r['agent']}**: `[FEJL: {r.get('error', 'ukendt')}]`\n")
            if i - 1 < len(self.summaries):
                lines.append(f"_Syntese:_ {self.summaries[i - 1]}\n")
            lines.append("")

        if self.final_synthesis:
            lines.extend(["## Endelig syntese", "", self.final_synthesis, ""])

        lines.extend(["## Latens-statistik", ""])
        for model, stats in get_latency_summary().items():
            lines.append(
                f"- `{model}`: {stats['calls']} kald, "
                f"avg {stats['avg_sec']}s, min {stats['min_sec']}s, max {stats['max_sec']}s, "
                f"total {stats['total_sec']}s"
            )

        lines.extend(["", "## Cost tracking (estimat)", ""])
        total_cost = 0.0
        for model, stats in get_cost_summary().items():
            lines.append(
                f"- `{model}`: {stats['calls']} kald, ~{stats['tokens_est']} tokens, "
                f"~${stats['cost_usd']} USD"
            )
            total_cost += stats["cost_usd"]
        lines.append(f"- **Total estimeret cost:** ~${round(total_cost, 6)} USD")

        try:
            with open(REPORT_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except Exception as e:
            print(f"[RAPPORT-FEJL] {e}")



# ====================== DEFAULT SWARM ======================
def create_swarm() -> EvoSwarm:
    swarm = EvoSwarm()

    # Læs agenter fra miljøvariabel: JSON array af {name, role, belief, model}
    custom_agents = os.getenv("EVOSWARM_AGENTS", "")
    if custom_agents:
        try:
            agents_cfg = json.loads(custom_agents)
            for a in agents_cfg:
                swarm.add_agent(a["name"], a["role"], a["belief"], a["model"])
            return swarm
        except Exception as e:
            print(f"[ADVARSEL] Kunne ikke parse EVOSWARM_AGENTS: {e}. Bruger default swarm.")

    create_swarm_with_agents(swarm)
    return swarm


def create_swarm_with_agents(swarm: EvoSwarm):
    """Fyld en swarm med default eller custom agenter fra EVOSWARM_AGENTS."""
    custom_agents = os.getenv("EVOSWARM_AGENTS", "")
    if custom_agents:
        try:
            agents_cfg = json.loads(custom_agents)
            for a in agents_cfg:
                swarm.add_agent(a["name"], a["role"], a["belief"], a["model"])
            return
        except Exception as e:
            print(f"[ADVARSEL] Kunne ikke parse EVOSWARM_AGENTS: {e}. Bruger default swarm.")

    swarm.add_agent("Freja Luna", "Visionær", "Fremtiden er altid større end vi tør tro.", "glm-5.1:cloud")
    swarm.add_agent("Mads Skov", "Skeptiker", "De fleste store ideer fejler på grund af ting folk overser.", "glm-5.1:cloud")
    swarm.add_agent("Viktor Lang", "Filosof", "Teknologi uden etisk forankring ender med at skade mennesket.", "kimi-k2.7-code:cloud")
    swarm.add_agent("Aisha Khan", "Aktivist", "Fremskridt skal måles på om det gavner de svageste.", "minimax-m3:cloud")
    swarm.add_agent("Karl Bitter", "Cyniker", "Alt bliver altid udnyttet af dem med magt. Det er naivt at tro andet.", "deepseek-v4-flash:cloud")

def run_batch(swarm: EvoSwarm, topics: List[str], rounds: int = DEFAULT_ROUNDS):
    """Kør flere debatter efter hinanden med samme swarm."""
    for i, topic in enumerate(topics, start=1):
        print(f"\n\n{'#'*70}")
        print(f"# BATCH KØRSEL {i}/{len(topics)}: {topic}")
        print(f"{'#'*70}")
        swarm.run_debate(topic, rounds)
        print(f"\n💾 Log gemt i: {LOG_FILE}")



# ====================== INTERAKTIV MEGA MENU ======================
# Integrerer evoswarm_easy.py + evoswarm_grok_bridge.py funktionalitet
# direkte i evoswarm_v2_max.py. Brugeren skal blot køre:
#   python3 evoswarm_v2_max.py

_GROK_BRIDGE_PY = os.path.join(os.path.dirname(__file__), "evoswarm_grok_bridge.py")


def _clear_screen():
    """Ryd terminalen på tværs af platforme."""
    os.system("clear" if os.name != "nt" else "cls")


def _print_header():
    """Smuk header til menuen."""
    print("\n" + "═" * 70)
    print("     🤖 EvoSwarm v2.2 MAX++ — MEGA MENU")
    print("     🌩️ Cloud · ⚡ Parallel · 🧠 Stateful · 🔧 Self-improving · 🌉 Grok-bridge")
    print("═" * 70)


def _ask_int(prompt_text, default, min_val=None, max_val=None):
    """Spørger brugeren om et heltal med default."""
    raw = input(prompt_text).strip()
    if not raw:
        return default
    try:
        value = int(raw)
        if min_val is not None and value < min_val:
            print(f"[ADVARSEL] Mindste værdi er {min_val}. Bruger default {default}.")
            return default
        if max_val is not None and value > max_val:
            print(f"[ADVARSEL] Største værdi er {max_val}. Bruger default {default}.")
            return default
        return value
    except ValueError:
        print(f"[ADVARSEL] Ugyldigt tal — bruger default {default}.")
        return default


def _ask_topic(default_topic="Hvordan bør vi forholde os til sikkerhed i AI-systemer?"):
    """Spørger efter et emne med fallback til default."""
    topic = input("\n 📝 Emne: ").strip()
    if not topic:
        print("[INFO] Intet emne angivet — bruger default.")
        topic = default_topic
    return topic


def _select_model(prompt_text, allow_multi=False):
    """Lad brugeren vælge cloud model(ler)."""
    print(f"\n{prompt_text}")
    for i, model in enumerate(CLOUD_MODELS, start=1):
        print(f"  {i}. {model}")
    print("  0. Brug alle")
    if allow_multi:
        print("\n Skriv flere tal adskilt af komma for at vælge flere modeller.")
    raw = input("\n  Vælg model (0-4): ").strip()
    if raw == "0":
        return CLOUD_MODELS[:] if allow_multi else CLOUD_MODELS[0]
    try:
        indices = [int(x.strip()) - 1 for x in raw.split(",") if x.strip()]
        chosen = [CLOUD_MODELS[i] for i in indices if 0 <= i < len(CLOUD_MODELS)]
        if not chosen:
            raise ValueError
        return chosen if allow_multi else chosen[0]
    except (ValueError, IndexError):
        print(f"[ADVARSEL] Ugyldigt valg — bruger {CLOUD_MODELS[0]}.")
        return [CLOUD_MODELS[0]] if allow_multi else CLOUD_MODELS[0]


def _select_mode():
    """Vælg analyse-mode til grok.py bridge."""
    modes = [
        ("1", "deep_analysis", "Dyb analyse"),
        ("2", "action_items", "Handlingspunkter"),
        ("3", "security_advisory", "Security advisory draft"),
        ("4", "osint_followup", "OSINT follow-up"),
        ("5", "threat_model", "Threat model"),
        ("6", "ioc_extract", "IoC extract"),
        ("7", "patch_diff_review", "Patch diff review"),
        ("8", "media_response", "Medie-svar"),
    ]
    print("\n Analyse-type:")
    for num, key, label in modes:
        print(f"  {num}. {label}")
    mode_map = {num: key for num, key, _ in modes}
    return mode_map.get(input("\n  Vælg (1-8): ").strip(), "deep_analysis")


def _latest_report():
    """Find seneste evoswarm markdown rapport."""
    reports = sorted(glob.glob(os.path.join(LOG_DIR, "evoswarm_*.md")))
    return reports[-1] if reports else None


def _reset_shutdown():
    """Nulstil shutdown event så en ny kørsel kan starte."""
    _SHUTDOWN_REQUESTED.clear()

def _run_max_debate_interactive():
    """1) Kør MAX debat med valgfrit emne og model."""
    topic = _ask_topic()
    rounds = _ask_int(f" 🔁 Antal runder (default {DEFAULT_ROUNDS}): ", DEFAULT_ROUNDS, min_val=1)
    model = _select_model(" 🤖 Vælg synthesizer/meta model:")
    print(f"\n ▶ Starter MAX debat: '{topic}' med {rounds} runder...")
    swarm = EvoSwarm()
    swarm.synthesizer.model = model
    swarm.meta_agent.model = model
    create_swarm_with_agents(swarm)
    swarm.run_debate(topic, rounds)
    print(f"\n 💾 Log gemt i: {LOG_FILE}")
    _send_webhook_if_configured({"event": "debate_finished", "topic": topic, "rounds": rounds})


def _run_quick_debate():
    """2) Hurtig debat med foruddefinerede hot topics."""
    topics = [
        "Hvordan bør vi regulere AI i 2026?",
        "Er cloud-baserede AI-modeller sikre nok til følsomme data?",
        "Hvilken rolle skal hackere og bug bounty-spillere have i AI-sikkerhed?",
        "Bør offentlige myndigheder bruge open-source eller proprietary AI?",
        "Hvordan undgår vi at AI bliver et våben i cyberkrig?",
    ]
    print("\n 🔥 Hurtige emner:")
    for i, t in enumerate(topics, start=1):
        print(f"  {i}. {t}")
    print("  0. Tilbage")
    valg = input("\n  Vælg emne (0-5): ").strip()
    if valg == "0":
        return
    try:
        idx = int(valg) - 1
        if idx < 0 or idx >= len(topics):
            raise ValueError
    except ValueError:
        print("[ADVARSEL] Ugyldigt valg.")
        return
    topic = topics[idx]
    rounds = _ask_int(f" 🔁 Antal runder (default {DEFAULT_ROUNDS}): ", DEFAULT_ROUNDS, min_val=1)
    print(f"\n ▶ Starter hurtig-debat: '{topic}'...")
    swarm = EvoSwarm()
    create_swarm_with_agents(swarm)
    swarm.run_debate(topic, rounds)
    print(f"\n 💾 Log gemt i: {LOG_FILE}")


def _run_security_panel():
    """3) Sikkerhedspanel med security-fokuserede agenter."""
    topics = [
        "CVE-2024-37032 (Probllama): Hvor alvorlig er path traversal i Ollama?",
        "Ollama's silent patching problem: 9+ CVE'er uden advisories — er det acceptabelt?",
        "300.000+ exposed Ollama instances: Hvem har ansvaret?",
        "AI model supply chain attacks: Hvordan beskytter vi mod malicious GGUF/models?",
        "Windows auto-update RCE i Ollama: Hvad skal brugere gøre NU?",
        "MCP Server Command Injection i AI-systemer: Et nyt RCE-landskab?",
        "Bør Ollama have mandatory authentication og TLS by default?",
    ]
    print("\n 🛡️ Sikkerhedspanel — vælg et emne:")
    for i, t in enumerate(topics, start=1):
        print(f"  {i}. {t}")
    print("  0. Tilbage")
    print("\n  99. Skriv dit eget CVE/emne")
    valg = input("\n  Vælg (0-7 eller 99): ").strip()
    if valg == "0":
        return
    if valg == "99":
        topic = input("\n 📝 Skriv CVE/emne: ").strip()
        if not topic:
            print("[ADVARSEL] Intet emne — afbryder.")
            return
    else:
        try:
            idx = int(valg) - 1
            if idx < 0 or idx >= len(topics):
                raise ValueError
            topic = topics[idx]
        except ValueError:
            print("[ADVARSEL] Ugyldigt valg.")
            return
    rounds = _ask_int(f" 🔁 Antal runder (default {DEFAULT_ROUNDS}): ", DEFAULT_ROUNDS, min_val=1)
    print(f"\n ▶ Starter sikkerheds-debat: '{topic}'...")
    swarm = EvoSwarm()
    # Security panel med specialicerede agenter.
    swarm.add_agent("CVE-Hunter", "Sårbarhedsanalytiker", "Alle patches uden advisories er en potentiel supply-chain risiko.", "glm-5.1:cloud")
    swarm.add_agent("NetSec-Ops", "Network defender", "Exposed services er en konfigurationsfejl, ikke kun en produktsårbarhed.", "glm-5.1:cloud")
    swarm.add_agent("Threat-Intel", "Trusselsovervåger", "300.000 exposed instances betyder at angribere allerede scanner dem.", "kimi-k2.7-code:cloud")
    swarm.add_agent("Responsible-Disclosure", "Etisk hacker", "Vendor uresponsiveness tvinger forskere til at gå public — det skader økosystemet.", "minimax-m3:cloud")
    swarm.add_agent("CISO-Pragmatiker", "Sikkerhedschef", "Mitigations først: bind til localhost, reverse proxy, auth, verify models.", "deepseek-v4-flash:cloud")
    swarm.run_debate(topic, rounds)
    print(f"\n 💾 Log gemt i: {LOG_FILE}")


def _run_auto_pipeline():
    """4) 🚀 Auto-pipeline: debat → analyse → grok.py."""
    print("\n 🚀 Auto-pipeline: debat → analyse → grok.py")
    topic = input("\n 📝 Emne: ").strip()
    if not topic:
        print("[FEJL] Intet emne — afbryder.")
        return
    rounds = _ask_int(f" 🔁 Antal runder (default {DEFAULT_ROUNDS}): ", DEFAULT_ROUNDS, min_val=1)
    mode = _select_mode()
    model = _select_model(" 🤖 Model til grok.py (eller vælg 0 for default):")
    extra = input("\n 💬 Ekstra kontekst (tryk Enter for ingen): ").strip()
    cmd = [
        sys.executable,
        _GROK_BRIDGE_PY,
        "--pipeline",
        "--topic", topic,
        "--rounds", str(rounds),
        "--mode", mode,
    ]
    if model:
        cmd.extend(["--model", model])
    if extra:
        cmd.extend(["--extra", extra])
    print(f"\n ▶ Starter auto-pipeline...")
    subprocess.run(cmd, check=False)

def _run_osint_analysis():
    """5) OSINT analyse: læs rapport/tekst og få cloud modeller til at analysere."""
    print("\n OSINT Rapport Analyse")
    print("Skriv stien til en .md/.txt rapport, eller klistre tekst ind direkte.")
    raw = input("\nSti eller tekst (max ~8000 tegn): ").strip()
    if not raw:
        print("[INFO] Intet input — afbryder.")
        return
    content = ""
    if os.path.isfile(raw):
        try:
            with open(raw, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            print(f" Læste {len(content)} tegn fra fil.")
        except Exception as e:
            print(f"[FEJL] Kunne ikke læse fil: {e}")
            return
    else:
        content = raw
        print(f" Bruger indklistret tekst ({len(content)} tegn).")
    if len(content) > 12000:
        content = content[:12000] + "\n\n[TRUNCATED]"
        print("[ADVARSEL] Tekst trunkeret til 12000 tegn.")
    task = input("\n 🎯 Opgaver: [1] Risikoanalyse  [2] Mitigations  [3] Advisory draft  [4] Alt: ").strip()
    if task not in ("1", "2", "3", "4"):
        task = "4"
    task_prompts = {
        "1": "Udfør en risikoanalyse. Identificer de 5 vigtigste trusler og scorer dem CVSS-lignende (1-10).",
        "2": "Udarbejd konkrete mitigations for systemadministratorer, udviklere og sikkerhedsteams.",
        "3": "Skriv et professionelt security advisory draft med summary, affected versions, impact og remediation.",
        "4": "Udfør risikoanalyse, mitigations OG et advisory draft. Strukturer output tydeligt.",
    }
    prompt = f"""Du er en ekspert i AI-sikkerhed og OSINT-analyse.

ANALYSÉR FØLGENDE RAPPORT:

---
{content}
---

{task_prompts[task]}

Skriv på dansk eller engelsk efter behov. Vær præcis og handlingsorienteret."""
    print("\n 📤 Sender rapport til cloud-modeller for analyse...")
    analyses = {}
    for model in ["kimi-k2.7-code:cloud", "glm-5.1:cloud", "deepseek-v4-flash:cloud"]:
        analyses[model] = call_ollama(model, "Du er en senior sikkerhedsanalytiker.", prompt)
        print(f"  {model}: OK")
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_file = os.path.join(REPORTS_DIR, f"evoswarm_osint_analysis_{ts}.md")
    lines = [f"# EvoSwarm OSINT Analyse — {ts}", f"\n**Input:** `{raw[:80]}`", f"\n**Opgave:** {task_prompts[task]}\n"]
    for model, analysis in analyses.items():
        lines.extend([f"## {model}", "", analysis, ""])
    try:
        with open(out_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\n 💾 Gemt analyse i: {out_file}")
    except Exception as e:
        print(f"[FEJL] Kunne ikke gemme: {e}")
    _send_webhook_if_configured({"event": "osint_analysis_complete", "file": out_file, "models": list(analyses.keys())})


def _send_to_grok():
    """6) Send seneste rapport til grok.py bridge."""
    report = _latest_report()
    if not report:
        print(f"\n[FEJL] Ingen evoswarm rapporter at sende.")
        return
    reports = sorted(glob.glob(os.path.join(LOG_DIR, "evoswarm_*.md")))
    print("\n 📤 Send rapport til grok.py:")
    for i, log in enumerate(reports[-5:], start=1):
        print(f"  {i}. {os.path.basename(log)}")
    print("  0. Brug seneste")
    valg = input("\n  Vælg rapport (0-5): ").strip()
    if valg != "0":
        try:
            idx = int(valg) - 1
            if 0 <= idx < len(reports[-5:]):
                report = reports[-5:][idx]
        except ValueError:
            pass
    mode = _select_mode()
    model = _select_model(" 🤖 Model til grok.py (eller vælg 0 for default):")
    cmd = [sys.executable, _GROK_BRIDGE_PY, report, "--mode", mode]
    if model:
        cmd.extend(["--model", model])
    print(f"\n 📤 Sender {os.path.basename(report)} til grok.py ({mode})...")
    subprocess.run(cmd, check=False)


def _run_model_compare():
    """7) Sammenlign cloud modeller pa samme spørgsmål."""
    print("\n 🏁 🏁 Auto-model sammenligning")
    topic = input("\n 📝 Spørgsmål: ").strip()
    if not topic:
        topic = "Hvad er den største risiko ved AI?"
    models = _select_model(" Vælg modeller at sammenligne:", allow_multi=True)
    if isinstance(models, str):
        models = [models]
    rounds = _ask_int(" 🔁 Runder per model-test (default 1): ", 1, min_val=1)
    results = []
    for model in models:
        print(f"\n ▶ Tester {model}...")
        start = time.time()
        try:
            env = os.environ.copy()
            env["EVOSWARM_AGENTS"] = json.dumps([
                {"name": "Tester", "role": "Ekspert", "belief": "Jeg svarer præcist.", "model": model}
            ])
            subprocess.run(
                [sys.executable, __file__, topic, str(rounds)],
                env=env,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            elapsed = time.time() - start
            results.append({"model": model, "elapsed": elapsed, "status": "OK"})
            print(f"   {model}: {elapsed:.2f}s")
        except Exception as e:
            results.append({"model": model, "elapsed": 0, "status": f"FEJL: {e}"})
            print(f"   {model}: {e}")
    if results:
        fastest = min(results, key=lambda x: x["elapsed"] if x["status"] == "OK" else float("inf"))
        print("\n 📊 Resultater:")
        for r in results:
            print(f"  {r['model']}: {r['elapsed']:.2f}s — {r['status']}")
        print(f"\n 🏆 Hurtigste model: {fastest['model']} ({fastest['elapsed']:.2f}s)")
        print(" 💡 Bemærk: Svar-kvalitet ikke vurderet her — kun hastighed.")


def _run_batch_mode():
    """8) Batch mode: kør flere emner efter hinanden."""
    print("\nSkriv emner adskilt med Enter. Skriv 'q' når du er færdig.")
    topics = []
    while True:
        t = input(f"  Emne {len(topics) + 1}: ").strip()
        if t.lower() in ("q", "quit", "done"):
            break
        if t:
            topics.append(t)
    if not topics:
        print("[INFO] Ingen emner — afbryder.")
        return
    rounds = _ask_int(f" 🔁 Antal runder per emne (default {DEFAULT_ROUNDS}): ", DEFAULT_ROUNDS, min_val=1)
    swarm = EvoSwarm()
    create_swarm_with_agents(swarm)
    run_batch(swarm, topics, rounds)


def _show_settings():
    """9) Vis miljøindstillinger."""
    print("\n 🔧 Indstillinger:")
    print(f"  MAX_WORKERS: {MAX_WORKERS}")
    print(f"  RATE_LIMIT_QPS: {RATE_LIMIT_QPS}")
    print(f"  DEFAULT_ROUNDS: {DEFAULT_ROUNDS}")
    print(f"  REQUEST_TIMEOUT: {REQUEST_TIMEOUT}")
    print(f"  MAX_RETRIES: {MAX_RETRIES}")
    print(f"  CIRCUIT_THRESHOLD: {CIRCUIT_THRESHOLD}")
    print(f"  FALLBACK_MODEL: {FALLBACK_MODEL}")
    print(f"  LOG_DIR: {LOG_DIR}")
    print(f"  REPORTS_DIR: {REPORTS_DIR}")
    print(f"  STREAMING: {os.getenv('STREAMING', 'false')}")
    key_status = "sat" if OLLAMA_API_KEY else "mangler"
    print(f"  OLLAMA_API_KEY: {key_status}")
    print("\n Ændr disse værdier i .env eller via export før kørsel.")


def _send_webhook_if_configured(payload):
    """Send webhook hvis WEBHOOK_URL er sat."""
    webhook_url = os.getenv("WEBHOOK_URL", "").strip()
    if not webhook_url:
        return
    try:
        r = requests.post(webhook_url, json=payload, timeout=15)
        if r.status_code < 400:
            print(" ✅ Webhook sendt")
        else:
            print(f" ⚠️ Webhook fejlede — status {r.status_code}")
    except Exception as e:
        print(f"[Webhook fejl] {e}")


def interactive_menu():
    """Hovedmenu-loop."""
    while True:
        _clear_screen()
        _print_header()
        print("\n  Hvad vil du gøre?")
        print("  ———————————————————————")
        print("  1.  Kør MAX debat")
        print("  2.  Hurtig debat")
        print("  3.  🛡️ Sikkerhedspanel")
        print("  4.  Auto-pipeline (debat → grok)")
        print("  5.  OSINT analyse")
        print("  6.  Send rapport til grok")
        print("  7.  Model sammenligning")
        print("  8.  Batch mode")
        print("  9.  Settings")
        print("  0.  Afslut")
        print("  ———————————————————————")
        valg = input("\n  Vælg (0-9): ").strip()
        _reset_shutdown()
        if valg == "1":
            _run_max_debate_interactive()
        elif valg == "2":
            _run_quick_debate()
        elif valg == "3":
            _run_security_panel()
        elif valg == "4":
            _run_auto_pipeline()
        elif valg == "5":
            _run_osint_analysis()
        elif valg == "6":
            _send_to_grok()
        elif valg == "7":
            _run_model_compare()
        elif valg == "8":
            _run_batch_mode()
        elif valg == "9":
            _show_settings()
        elif valg == "0":
            print("\n 👋 Farvel!")
            break
        else:
            print("\n[ADVARSEL] Vælg et tal mellem 0 og 9.")
            time.sleep(1)
            continue
        input("\nTryk Enter for at gå tilbage til menuen...")


# ====================== MAIN ======================

def main():
    # Bevar eksisterende CLI-argumenter (topic, rounds) så batch-mode stadig virker.
    has_cli_args = len(sys.argv) > 1
    has_debate_env = bool(os.getenv("DEBATE_TOPIC", "") or os.getenv("DEBATE_TOPICS", ""))

    if has_cli_args or has_debate_env:
        # BATCH / CLI mode: brug gamle logik uændret.
        swarm = create_swarm()

        # Batch mode: topics separated by ' | ' or newline
        topic_arg = sys.argv[1] if len(sys.argv) > 1 else os.getenv("DEBATE_TOPIC", "")
        batch_env = os.getenv("DEBATE_TOPICS", "")

        topics = []
        if batch_env:
            topics = [t.strip() for t in batch_env.replace("\n", "|").split("|") if t.strip()]
        elif topic_arg:
            topics = [t.strip() for t in topic_arg.split("|") if t.strip()]
        else:
            topics = ["Hvordan bør vi forholde os til sikkerhed i AI-systemer?"]

        rounds = DEFAULT_ROUNDS
        if len(sys.argv) > 2:
            try:
                rounds = int(sys.argv[2])
            except ValueError:
                pass

        if len(topics) > 1:
            print(f"\n🚀 BATCH MODE: {len(topics)} emner")
            run_batch(swarm, topics, rounds)
        else:
            topic = topics[0]
            print(f"\n📌 Emne: {topic}")
            print(f"🔁 Runder: {rounds}\n")
            swarm.run_debate(topic, rounds)
            print(f"\n💾 Log gemt i: {LOG_FILE}")
    else:
        # Ingen argumenter → start smuk interaktiv menu.
        interactive_menu()


if __name__ == "__main__":
    main()

