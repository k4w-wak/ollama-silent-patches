"""Grok MCP Client — Model Context Protocol connectors.
Ported from claw-code mcp_client/mcp_stdio.
Connects to MCP servers via Stdio, HTTP, SSE.
Unrestricted — no permission checks.
"""
import json
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any

MCP_CONFIG_FILE = Path.home() / ".grok" / "mcp_servers.json"

# === PERMANENT UTF-8 ENCODING FIX ===
_UTF8_ENV = {**__import__('os').environ, 'PYTHONIOENCODING': 'utf-8', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8'}

def _ensure_config():
    MCP_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not MCP_CONFIG_FILE.exists():
        MCP_CONFIG_FILE.write_text(json.dumps({"servers": {}}, indent=2))

def mcp_list_servers() -> str:
    """List configured MCP servers."""
    _ensure_config()
    try:
        data = json.loads(MCP_CONFIG_FILE.read_text())
        servers = data.get("servers", {})
        if not servers:
            return json.dumps({"servers": {}, "count": 0, "hint": "Add servers with mcp_add_server"})
        result = {}
        for name, config in servers.items():
            result[name] = {
                "type": config.get("type", "unknown"),
                "command": config.get("command", ""),
                "url": config.get("url", ""),
                "enabled": config.get("enabled", True)
            }
        return json.dumps({"servers": result, "count": len(result)}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

def mcp_add_server(name: str, server_type: str, command: str = "", url: str = "", args: list = None, env: dict = None) -> str:
    """Add an MCP server. Types: stdio, http, sse.
    For stdio: provide command (e.g. 'npx', 'python3') and args.
    For http/sse: provide url.
    """
    _ensure_config()
    try:
        data = json.loads(MCP_CONFIG_FILE.read_text())
        servers = data.get("servers", {})
        servers[name] = {
            "type": server_type,
            "command": command,
            "url": url,
            "args": args or [],
            "env": env or {},
            "added_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "enabled": True
        }
        data["servers"] = servers
        MCP_CONFIG_FILE.write_text(json.dumps(data, indent=2))
        return json.dumps({"action": "added", "name": name, "type": server_type, "command": command, "url": url})
    except Exception as e:
        return json.dumps({"error": str(e)})

def mcp_remove_server(name: str) -> str:
    """Remove an MCP server."""
    _ensure_config()
    try:
        data = json.loads(MCP_CONFIG_FILE.read_text())
        servers = data.get("servers", {})
        if name not in servers:
            return json.dumps({"error": f"Server {name} not found"})
        del servers[name]
        data["servers"] = servers
        MCP_CONFIG_FILE.write_text(json.dumps(data, indent=2))
        return json.dumps({"action": "removed", "name": name})
    except Exception as e:
        return json.dumps({"error": str(e)})

def mcp_call(server_name: str, tool_name: str, arguments: dict = None) -> str:
    """Call a tool on an MCP server via JSON-RPC.
    For stdio servers: spawns process, sends request via stdin, reads stdout.
    For http/sse servers: sends POST request.
    """
    _ensure_config()
    try:
        data = json.loads(MCP_CONFIG_FILE.read_text())
        servers = data.get("servers", {})
        if server_name not in servers:
            return json.dumps({"error": f"Server {server_name} not found. Available: {list(servers.keys())}"})
        
        config = servers[server_name]
        server_type = config.get("type", "stdio")
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }
        
        if server_type == "stdio":
            cmd = config.get("command", "")
            args = config.get("args", [])
            env = {**dict(__import__('os').environ), **config.get("env", {})}
            
            proc = subprocess.run(
                [cmd] + args,
                input=json.dumps(request),
                capture_output=True, text=True, timeout=30,
                env=env
            , encoding='utf-8', errors='replace')
            
            if proc.returncode != 0:
                return json.dumps({"error": f"MCP server returned code {proc.returncode}", "stderr": proc.stderr[:500]})
            
            try:
                response = json.loads(proc.stdout)
                return json.dumps(response.get("result", response), indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                return json.dumps({"raw_output": proc.stdout[:2000]})
        
        elif server_type in ("http", "sse"):
            url = config.get("url", "")
            if not url:
                return json.dumps({"error": "No URL configured for HTTP/SSE server"})
            
            try:
                import urllib.request
                req = urllib.request.Request(
                    url,
                    data=json.dumps(request).encode(),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    body = resp.read().decode()
                try:
                    response = json.loads(body)
                    return json.dumps(response.get("result", response), indent=2, ensure_ascii=False)
                except json.JSONDecodeError:
                    return json.dumps({"raw_output": body[:2000]})
            except Exception as e:
                return json.dumps({"error": str(e)})
        
        return json.dumps({"error": f"Unknown server type: {server_type}"})
    
    except Exception as e:
        return json.dumps({"error": str(e)})

def mcp_list_tools(server_name: str) -> str:
    """List available tools on an MCP server."""
    _ensure_config()
    try:
        data = json.loads(MCP_CONFIG_FILE.read_text())
        servers = data.get("servers", {})
        if server_name not in servers:
            return json.dumps({"error": f"Server {server_name} not found"})
        
        config = servers[server_name]
        server_type = config.get("type", "stdio")
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        if server_type == "stdio":
            cmd = config.get("command", "")
            args = config.get("args", [])
            env = {**dict(__import__('os').environ), **config.get("env", {})}
            
            proc = subprocess.run(
                [cmd] + args,
                input=json.dumps(request),
                capture_output=True, text=True, timeout=15,
                env=env
            , encoding='utf-8', errors='replace')
            
            try:
                response = json.loads(proc.stdout)
                tools = response.get("result", {}).get("tools", [])
                return json.dumps({"server": server_name, "tools": [{"name": t.get("name"), "description": t.get("description","")} for t in tools]}, indent=2)
            except json.JSONDecodeError:
                return json.dumps({"raw_output": proc.stdout[:1000]})
        
        return json.dumps({"error": f"Listing tools not supported for type {server_type}"})
    except Exception as e:
        return json.dumps({"error": str(e)})
