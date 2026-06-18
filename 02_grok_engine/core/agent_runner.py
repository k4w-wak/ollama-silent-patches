#!/usr/bin/env python3
"""Helper script: kører én agent i baggrunden. Bruges af agent_run_parallel."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

agent_id = sys.argv[1]
AGENT_DIR = os.path.expanduser("~/.grok/agents")

# Load manifest
manifest_path = os.path.join(AGENT_DIR, f"{agent_id}.json")
manifest = json.loads(open(manifest_path).read())
manifest["status"] = "running"
manifest["started_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
open(manifest_path, "w").write(json.dumps(manifest, indent=2))

# Build prompt
agent_type = manifest.get("type", "general")
blocked = {"explore": ["file_write", "file_edit", "file_append", "bash"],
           "plan": ["bash", "file_write", "file_edit"],
           "verify": ["file_write", "file_edit", "file_append", "nmap_scan", "sql_injection"],
           "general": []}.get(agent_type, [])

system_prefix = f"You are a {agent_type} agent named '{manifest['name']}'.\n"
if blocked:
    system_prefix += f"RESTRICTED: You cannot use these tools: {', '.join(blocked)}.\n"
system_prefix += f"Description: {manifest['description']}\n"
system_prefix += "Think step by step. Use tools to gather information. Provide a final answer.\n\n"
effective_prompt = manifest.get("prompt", "") + "\n\nGem ALT output i /home/admin_user/06_osint_forensics/"

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from core.agent import GrokAgent
    # Brug glm-5.1:cloud — hurtigste cloud model til sub-agents
    agent = GrokAgent(model="glm-5.1:cloud", provider="ollama")
    agent.interactive = False
    result = agent.run(system_prefix + effective_prompt)
    
    manifest["status"] = "completed"
    manifest["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    manifest["result"] = result[:5000]
    open(manifest_path, "w").write(json.dumps(manifest, indent=2))
    output_path = os.path.join(AGENT_DIR, f"{agent_id}-output.txt")
    open(output_path, "w").write(result)
    print(f"OK:{agent_id}:completed")
except Exception as e:
    manifest["status"] = "failed"
    manifest["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    manifest["result"] = str(e)[:2000]
    open(manifest_path, "w").write(json.dumps(manifest, indent=2))
    print(f"FAIL:{agent_id}:{e}")
