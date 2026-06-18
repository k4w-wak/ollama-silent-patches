"""
GROK SWARM v4 — Lokal Multi-Agent Security System
Bygget på Ollama 0.30.7: GGUF + Tool Calling + Structured Outputs

Arkitektur:
  Orchestrator → [ReconAgent, ExploitAgent, ReportAgent]
  Hver agent har sine egne tools + structured output schema
  Kommunikation mellem agenter via JSON Schema
"""
__version__ = "4.0.0"
