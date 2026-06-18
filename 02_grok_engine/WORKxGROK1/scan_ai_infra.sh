#!/bin/bash
# AI Infrastructure Scanner - 8 Hour Deep Dive
# Scanning for exposed AI/ML endpoints

TARGETS_FILE="/home/admin_user/grok_engine/8hour_deep_dive/live_targets.txt"
RESULTS_DIR="/home/admin_user/grok_engine/8hour_deep_dive/results"
mkdir -p "$RESULTS_DIR"

echo "=== AI INFRASTRUCTURE SCANNER ==="
echo "Started: $(date)"
echo ""

# Check a list of known AI service ports on random targets
# These are ports commonly exposed for AI/ML services
declare -A PORTS
PORTS[11434]="Ollama"
PORTS[8000]="vLLM/FastAPI"
PORTS[5000]="MLflow"
PORTS[5678]="n8n"
PORTS[7860]="Gradio/Langflow"
PORTS[8501]="Streamlit"
PORTS[6333]="Qdrant"
PORTS[19530]="Milvus"
PORTS[9091]="Milvus"
PORTS[2375]="Docker_API"
PORTS[6443]="Kubernetes"
PORTS[8888]="Jupyter"
PORTS[3000]="Langfuse/Grafana"
PORTS[3001]="MCP_Inspector"
PORTS[4000]="LiteLLM"
PORTS[8080]="Weaviate/LocalAI"
PORTS[1234]="LM_Studio"
PORTS[4891]="GPT4All"
PORTS[5001]="KoboldCpp"
PORTS[18789]="OpenClaw"

for port in "${!PORTS[@]}"; do
    echo "  Port $port - ${PORTS[$port]}"
done

echo ""
echo "Scan script ready. Run with specific targets."
echo "Use: shodan search, censys search, or curl probes"
