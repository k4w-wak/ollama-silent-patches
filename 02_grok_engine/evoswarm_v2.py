#!/usr/bin/env python3
"""
EvoSwarm v2 FIXED — Med rigtige Ollama Cloud + egen hukommelse + evolution
"""

import time
import requests
from typing import Dict

# ====================== OLLAMA CLOUD ======================
def call_ollama(model: str, system: str, user: str) -> str:
    url = "https://ollama.com/v1/chat/completions"
    api_key = "27be72d8f0ff4ef79db5bee0f8758b63.6SrdafFDTNf9RoGMFy_HrB_h"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        "max_tokens": 1400,
        "temperature": 0.82
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=90)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"].strip()
        return f"[FEJL {r.status_code}]"
    except Exception as e:
        return f"[NETVÆRKSFEJL] {str(e)}"


class EvoAgent:
    def __init__(self, name: str, role: str, core_belief: str, model: str = "glm-5.1:cloud"):
        self.name = name
        self.role = role
        self.model = model
        self.core_belief = core_belief
        self.evolution_level = 0
        self.memory: list = []   # Egen hukommelse

        self.system_prompt = f"""Du er {name} — {role}.
Din kerne-overbevisning: {core_belief}

Du husker tidligere runder og udvikler dine synspunkter over tid.
Vær tro mod dig selv. Svar ærligt og i din egen stil."""

    def respond(self, topic: str, round_num: int, previous: str) -> str:
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

        response = call_ollama(self.model, self.system_prompt, user_msg)
        self.memory.append(response[:380])
        return response

    def evolve(self, summary: str):
        self.evolution_level += 1
        prompt = f"""Du er {self.name}.
Baseret på denne runde: {summary}

Opdater din egen tankegang en smule. Skriv kun en kort intern note (max 60 ord)."""

        note = call_ollama(self.model, self.system_prompt, prompt)
        self.system_prompt += f"\n\n[Evolution {self.evolution_level}]: {note}"
        print(f"   🧬 {self.name} evolved (niveau {self.evolution_level})")


class EvoSwarm:
    def __init__(self):
        self.agents: Dict[str, EvoAgent] = {}
        self.history: list = []

    def add_agent(self, name: str, role: str, core_belief: str, model: str = "glm-5.1:cloud"):
        self.agents[name] = EvoAgent(name, role, core_belief, model)
        print(f"✅ {name} ({role}) → {model}")

    def run_debate(self, topic: str, rounds: int = 5):
        print(f"\n{'═'*70}")
        print(f"🚀 EVO DEBAT: {topic}")
        print(f"{'═'*70}\n")

        for r in range(1, rounds + 1):
            print(f"\n─── RUNDE {r} ───")
            context = "\n".join(self.history[-3:]) if self.history else topic

            for name, agent in self.agents.items():
                print(f"💭 {name} tænker... ({agent.model})")
                resp = agent.respond(topic, r, context)
                print(f"→ {name}: {resp}\n")

            self.history.append(f"Runde {r}")

            if r % 2 == 0:
                print("🧬 Evolution fase...")
                for agent in self.agents.values():
                    agent.evolve(self.history[-1])

        print("\n✅ Debat færdig — agenterne har udviklet sig.")


def create_swarm():
    swarm = EvoSwarm()
    swarm.add_agent("Freja Luna", "Visionær", "Fremtiden er altid større end vi tør tro.", "glm-5.1:cloud")
    swarm.add_agent("Mads Skov", "Skeptiker", "De fleste store ideer fejler på grund af ting folk overser.", "glm-5.1:cloud")
    swarm.add_agent("Viktor Lang", "Filosof", "Teknologi uden etisk forankring ender med at skade mennesket.", "kimi-k2.7-code:cloud")
    swarm.add_agent("Aisha Khan", "Aktivist", "Fremskridt skal måles på om det gavner de svageste.", "minimax-m3:cloud")
    swarm.add_agent("Karl Bitter", "Cyniker", "Alt bliver altid udnyttet af dem med magt. Det er naivt at tro andet.", "deepseek-v4-flash:cloud")
    return swarm


if __name__ == "__main__":
    print("EvoSwarm v2 FIXED — Klar til start")
    swarm = create_swarm()

    while True:
        print("\n1. Start debat")
        print("2. Vis agenter")
        print("3. Tilføj agent")
        print("4. Afslut")

        try:
            valg = input("\n> ").strip()
        except:
            break

        if valg == "1":
            topic = input("Emne: ").strip() or "Hvordan bør vi forholde os til sikkerhed i AI-systemer?"
            try:
                rounds = int(input("Antal runder (default 5): ") or 5)
            except:
                rounds = 5
            swarm.run_debate(topic, rounds)

        elif valg == "2":
            for name, a in swarm.agents.items():
                print(f"• {name} ({a.role}) | Model: {a.model} | Evolution: {a.evolution_level}")

        elif valg == "3":
            name = input("Navn: ")
            role = input("Rolle: ")
            belief = input("Kerne-overbevisning: ")
            model = input("Model (glm-5.1:cloud / kimi-k2.7-code:cloud / etc): ") or "glm-5.1:cloud"
            swarm.add_agent(name, role, belief, model)

        elif valg in ("4", "q", "exit"):
            print("Farvel!")
            break