"""Grok Sub-Agent System — Fork, Explore, Plan, Verify agents.
Ported from claw-code AgentTool/forkSubagent/runAgent.
Unrestricted — each agent gets full tool access.
"""
import json
import time
import uuid
import sys
import subprocess
from pathlib import Path
from typing import Optional

AGENT_DIR = Path.home() / ".grok" / "agents"

# Agent types and their capabilities
AGENT_TYPES = {
    "explore": {
        "desc": "Read-only exploration agent. Searches, reads, analyzes. No writes.",
        "allowed_cats": ["file", "web", "system", "security", "utility", "meta", "session"],
        "blocked_tools": ["file_write", "file_edit", "file_append", "bash"],
    },
    "plan": {
        "desc": "Planning agent. Creates plans, todos, tasks. Can search and read.",
        "allowed_cats": ["file", "web", "system", "utility", "meta", "task", "planning"],
        "blocked_tools": ["bash", "file_write", "file_edit"],
    },
    "verify": {
        "desc": "Verification agent. Runs bash read-only commands to verify results.",
        "allowed_cats": ["file", "system", "web", "utility", "meta"],
        "blocked_tools": ["file_write", "file_edit", "file_append", "nmap_scan", "sql_injection"],
    },
    "general": {
        "desc": "General purpose agent. Full unrestricted access to all tools.",
        "allowed_cats": None,  # All categories
        "blocked_tools": [],
    },
}

def _ensure_dir():
    AGENT_DIR.mkdir(parents=True, exist_ok=True)

def agent_spawn(agent_type: str, description: str, prompt: str, name: str = "") -> str:
    """Spawn a sub-agent with a specific type and prompt.
    
    Args:
        agent_type: One of 'explore', 'plan', 'verify', 'general'
        description: Short description of what the agent should do
        prompt: Full prompt/instructions for the agent
        name: Optional name for the agent
    
    Returns:
        Agent manifest JSON
    """
    agent_type = agent_type.lower().strip()
    if agent_type not in AGENT_TYPES:
        return json.dumps({"error": f"Unknown agent type: {agent_type}. Available: {list(AGENT_TYPES.keys())}"}, ensure_ascii=False)
    
    # Normalize aliases
    type_aliases = {
        "explorer": "explore", "search": "explore", "read": "explore",
        "planner": "plan", "planning": "plan", "todo": "plan",
        "verification": "verify", "test": "verify", "check": "verify",
        "full": "general", "all": "general", "unrestricted": "general",
    }
    agent_type = type_aliases.get(agent_type, agent_type)
    
    _ensure_dir()
    
    agent_id = str(uuid.uuid4())[:8]
    agent_name = name.strip() or f"{agent_type}-{agent_id}"
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    
    config = AGENT_TYPES[agent_type]
    
    manifest = {
        "id": agent_id,
        "name": agent_name,
        "type": agent_type,
        "description": description.strip(),
        "prompt": prompt.strip(),
        "status": "spawned",
        "allowed_cats": config["allowed_cats"],
        "blocked_tools": config["blocked_tools"],
        "created_at": now,
        "started_at": None,
        "completed_at": None,
        "result": None,
    }
    
    # Save manifest
    manifest_path = AGENT_DIR / f"{agent_id}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    
    # Save prompt as output file
    output_path = AGENT_DIR / f"{agent_id}-output.txt"
    output_path.write_text(f"[{now}] Agent {agent_name} spawned\nType: {agent_type}\nDescription: {description}\n\nPrompt:\n{prompt}")
    
    return json.dumps({
        "action": "spawned",
        "id": agent_id,
        "name": agent_name,
        "type": agent_type,
        "description": description.strip(),
        "status": "spawned",
        "blocked_tools": config["blocked_tools"],
        "created_at": now,
        "hint": f"Use agent_run with id '{agent_id}' to execute, or agent_status to check."
    }, indent=2, ensure_ascii=False)

def agent_run(agent_id: str = "", user_prompt: str = "") -> str:
    """Execute a spawned sub-agent. Runs the agent's prompt through Grok.
    
    Args:
        agent_id: The agent ID from agent_spawn (also accepts 'input' for compatibility)
        user_prompt: Optional additional prompt to add
    
    Returns:
        Agent execution result
    """
    # Normalize: caller might pass the ID via 'agent_id' or embedded in a
    # whitespace-separated string like "ID extra_prompt" (from tools.py wrapper).
    # Strip and extract just the ID portion if extra text is present.
    agent_id = agent_id.strip()
    if not agent_id:
        return json.dumps({"error": "No agent_id provided. Use agent_list to see available agents."}, ensure_ascii=False)

    # If the id contains spaces, take only the first token (the actual ID).
    # The tools.py wrapper already splits, but some call paths don't.
    _id = agent_id.split(None, 1)[0] if " " in agent_id else agent_id

    manifest_path = AGENT_DIR / f"{_id}.json"
    if not manifest_path.exists():
        # Fallback: try a fuzzy match against stored agent IDs in case
        # the caller passed a full UUID or a differently-cased short ID.
        _ensure_dir()
        for p in AGENT_DIR.glob("*.json"):
            try:
                data = json.loads(p.read_text())
                stored_id = data.get("id", "")
                if stored_id == _id or stored_id.startswith(_id) or _id.startswith(stored_id):
                    manifest_path = p
                    _id = stored_id
                    break
            except Exception:
                pass
        else:
            return json.dumps({"error": f"Agent {_id} not found. Use agent_list to see available agents."}, ensure_ascii=False)
    
    manifest = json.loads(manifest_path.read_text())
    
    if manifest["status"] in ("completed", "failed", "stopped"):
        return json.dumps({"error": f"Agent {_id} is {manifest['status']}. Create a new one with agent_spawn."}, ensure_ascii=False)
    
    # Update status
    manifest["status"] = "running"
    manifest["started_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    
    # Build effective prompt
    agent_type = manifest["type"]
    type_config = AGENT_TYPES.get(agent_type, AGENT_TYPES["general"])
    blocked = type_config["blocked_tools"]
    
    system_prefix = f"You are a {agent_type} agent named '{manifest['name']}'.\n"
    if blocked:
        system_prefix += f"RESTRICTED: You cannot use these tools: {', '.join(blocked)}.\n"
    system_prefix += f"Description: {manifest['description']}\n"
    system_prefix += "Think step by step. Use tools to gather information. Provide a final answer.\n\n"
    
    effective_prompt = manifest["prompt"]
    if user_prompt:
        effective_prompt += f"\n\nAdditional instruction: {user_prompt}"
    
    # Try to run through GrokAgent
    try:
        from core.agent import GrokAgent
        agent = GrokAgent()
        agent.interactive = False
        
        result = agent.run(system_prefix + effective_prompt)
        
        # Save result
        manifest["status"] = "completed"
        manifest["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        manifest["result"] = result[:5000]
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
        
        # Save full output
        output_path = AGENT_DIR / f"{_id}-output.txt"
        output_path.write_text(result)
        
        return json.dumps({
            "id": _id,
            "name": manifest["name"],
            "type": agent_type,
            "status": "completed",
            "result_preview": result[:1000],
            "full_output": str(output_path),
            "completed_at": manifest["completed_at"]
        }, indent=2, ensure_ascii=False)
    
    except Exception as e:
        manifest["status"] = "failed"
        manifest["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        manifest["result"] = str(e)[:2000]
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
        
        return json.dumps({
            "id": _id,
            "name": manifest["name"],
            "type": agent_type,
            "status": "failed",
            "error": str(e)
        }, indent=2, ensure_ascii=False)

def agent_status(agent_id: str = "") -> str:
    """Check status of an agent or all agents.
    
    Args:
        agent_id: Specific agent ID, or empty for all agents
    """
    _ensure_dir()
    
    if agent_id and agent_id.strip():
        path = AGENT_DIR / f"{agent_id.strip()}.json"
        if not path.exists():
            return json.dumps({"error": f"Agent {agent_id} not found"}, ensure_ascii=False)
        return path.read_text()
    
    # List all agents
    agents = []
    for path in sorted(AGENT_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text())
            agents.append({
                "id": data.get("id"),
                "name": data.get("name"),
                "type": data.get("type"),
                "status": data.get("status"),
                "created_at": data.get("created_at"),
            })
        except:
            pass
    
    return json.dumps({"count": len(agents), "agents": agents}, indent=2, ensure_ascii=False)

def agent_stop(agent_id: str) -> str:
    """Stop a running agent.
    
    Args:
        agent_id: The agent ID to stop
    """
    manifest_path = AGENT_DIR / f"{agent_id.strip()}.json"
    if not manifest_path.exists():
        return json.dumps({"error": f"Agent {agent_id} not found"}, ensure_ascii=False)
    
    manifest = json.loads(manifest_path.read_text())
    manifest["status"] = "stopped"
    manifest["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    
    return json.dumps({"action": "stopped", "id": agent_id, "name": manifest.get("name")}, ensure_ascii=False)


def agent_run_parallel(agent_ids: list) -> str:
    """Spawn multiple agents i baggrundsprocesser. Kører ALLE samtidig.
    
    Args:
        agent_ids: Liste af agent IDs at køre
    
    Returns:
        JSON med process IDs for hver agent
    """
    _ensure_dir()
    procs = []
    runner = Path(__file__).parent / "agent_runner.py"
    
    for aid in agent_ids:
        manifest_path = AGENT_DIR / f"{aid}.json"
        if not manifest_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text())
        if manifest["status"] in ("completed", "failed", "stopped"):
            continue
        
        # Sæt til pending før spawn
        manifest["status"] = "pending"
        manifest_path.write_text(json.dumps(manifest, indent=2))
        
        # Spawn som baggrundsproces
        proc = subprocess.Popen(
            [sys.executable, str(runner), aid],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=str(Path(__file__).parent.parent)
        )
        procs.append({"agent_id": aid, "pid": proc.pid, "name": manifest.get("name")})
    
    return json.dumps({
        "action": "parallel_spawned",
        "count": len(procs),
        "agents": procs,
        "note": "Agents kører i baggrunden. Brug agent_status for at tjekke fremskridt."
    }, indent=2, ensure_ascii=False)


def agent_wait_all(agent_ids: list = None, timeout: int = 300) -> str:
    """Vent på alle agents. Returnerer status for alle.
    
    Args:
        agent_ids: Liste af agent IDs. None = alle pending/running
        timeout: Max sekunder at vente
    
    Returns:
        JSON med status for alle agents
    """
    _ensure_dir()
    start = time.time()
    results = []
    
    # Find relevante agents
    targets = set(agent_ids or [])
    all_agents = []
    for path in sorted(AGENT_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text())
            if not targets or data.get("id") in targets:
                all_agents.append(data)
        except:
            pass
    
    # Wait loop
    while time.time() - start < timeout:
        done = True
        results = []
        for agent in all_agents:
            try:
                data = json.loads((AGENT_DIR / f"{agent['id']}.json").read_text())
                results.append({"id": data["id"], "name": data.get("name"), "status": data["status"]})
                if data["status"] in ("pending", "running"):
                    done = False
            except:
                pass
        if done:
            break
        time.sleep(2)
    
    return json.dumps({
        "action": "wait_complete",
        "completed": done,
        "count": len(results),
        "agents": results
    }, indent=2, ensure_ascii=False)