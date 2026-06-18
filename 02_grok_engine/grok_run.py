#!/usr/bin/env python3
"""
Grok Programmatic Runner
Brug: python3 grok_run.py "din mission her"

Lader eksterne scripts kalde Grok uden at skulle lave import acrobatics.
"""

import sys
import os

# Sæt path korrekt — uanset hvor scriptet kaldes fra
GROK_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, GROK_DIR)
sys.path.insert(0, os.path.join(GROK_DIR, 'core'))

os.chdir(GROK_DIR)

from core.agent import GrokAgent

def run_mission(prompt: str, provider: str = 'groq', model: str = 'qwen/qwen3-32b', iterations: int = 20) -> str:
    """
    Kør en mission med Grok. Returnerer det fulde svar.
    
    Args:
        prompt: Missionen/beskeden til Grok
        provider: Tving provider (groq/ollama), default: groq
        model: Tving model, default: qwen/qwen3-32b (best FC support)
        iterations: Max ReAct iterations (default: 20)
    """
    agent = GrokAgent(provider=provider, model=model)
    agent.interactive = True  # Vis REACT output
    
    # Overskriv iteration limit for denne mission
    from core import config as cfg
    cfg.MAX_REACT_ITERATIONS = iterations
    
    response = agent.run(prompt)
    return response


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Brug: python3 grok_run.py \"din mission her\" [--provider groq|ollama] [--model modelnavn]")
        sys.exit(1)
    
    mission = sys.argv[1]
    provider = None
    model = None
    
    # Parse flags
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--provider" and i + 1 < len(sys.argv):
            provider = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--model" and i + 1 < len(sys.argv):
            model = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    result = run_mission(mission, provider=provider, model=model)
    print(result)