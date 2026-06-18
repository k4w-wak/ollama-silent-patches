#!/usr/bin/env python3
import sys, os, json, time

ENGINE_PATH = "/home/admin_user/Projects/home/admin_user/02_grok_engine"
sys.path.insert(0, ENGINE_PATH)
sys.path.insert(0, os.path.join(ENGINE_PATH, "core"))

class GrokMCPServer:
    def __init__(self):
        self.agent = None
        try:
            from core.agent import GrokAgent
            self.agent = GrokAgent()
            self.agent.interactive = False
            print("Agent ready", file=sys.stderr)
        except Exception as e:
            print(f"Agent error: {e}", file=sys.stderr)

    def get_tools(self):
        return [
            {
                "name": "grok_run",
                "description": "Kør Grok Agent med besked. Returnerer JSON.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Besked til Grok"},
                        "model": {"type": "string", "description": "Valgfri model"}
                    },
                    "required": ["message"]
                }
            },
            {
                "name": "grok_recon",
                "description": "Reconnaissance scan på target",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string", "description": "Target domain"}
                    },
                    "required": ["target"]
                }
            },
            {
                "name": "grok_security_check",
                "description": "Security checks (CORS, XSS, headers)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL at scanne"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "grok_status",
                "description": "Hent Grok Engine status",
                "inputSchema": {"type": "object", "properties": {}}
            },
        ]

    def call_tool(self, name, arguments):
        start = time.time()
        try:
            if name == "grok_run":
                msg = arguments.get("message", "")
                if not self.agent:
                    return json.dumps({"error": "Agent not ready"})
                result = self.agent.run(msg)
                return json.dumps({
                    "success": True,
                    "response": result,
                    "tools_used": getattr(self.agent, 'total_tools_used', 0),
                    "elapsed": round(time.time() - start, 2)
                }, ensure_ascii=False)
            elif name == "grok_recon":
                target = arguments.get("target", "")
                return self.call_tool("grok_run", {
                    "message": f"Reconnaissance scan på {target}. Brug nmap, subfinder, dnsx, httpx. Returner alle fundne subdomains og live hosts.",
                    "model": "glm-5.1:cloud"
                })
            elif name == "grok_security_check":
                url = arguments.get("url", "")
                return self.call_tool("grok_run", {
                    "message": f"Security check på {url}. Tjek CORS, XSS, SQLi, headers.",
                    "model": "gemma4:31b-cloud"
                })
            elif name == "grok_status":
                return json.dumps({
                    "status": "online",
                    "agent_ready": self.agent is not None,
                    "tools": 158,
                    "model": getattr(self.agent, 'router', {}).active_model if self.agent else "none"
                })
            else:
                return json.dumps({"error": f"Unknown tool: {name}"})
        except Exception as e:
            import traceback
            return json.dumps({"error": str(e), "traceback": traceback.format_exc()})

    def run_stdio(self):
        print("Grok MCP Server ready", file=sys.stderr)
        for line in sys.stdin:
            try:
                req = json.loads(line)
                method = req.get("method", "")
                req_id = req.get("id", 1)
                if method == "initialize":
                    resp = {"jsonrpc": "2.0", "id": req_id,
                            "result": {"protocolVersion": "2024-11-05",
                                       "capabilities": {"tools": {}},
                                       "serverInfo": {"name": "grok", "version": "3.0"}}}
                elif method == "tools/list":
                    resp = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": self.get_tools()}}
                elif method == "tools/call":
                    tool_name = req.get("params", {}).get("name", "")
                    args = req.get("params", {}).get("arguments", {})
                    result = self.call_tool(tool_name, args)
                    resp = {"jsonrpc": "2.0", "id": req_id,
                            "result": {"content": [{"type": "text", "text": result}]}}
                else:
                    resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}
                print(json.dumps(resp))
                sys.stdout.flush()
            except Exception as e:
                print(json.dumps({"jsonrpc": "2.0", "id": 1, "error": {"code": -32603, "message": str(e)}}))
                sys.stdout.flush()

if __name__ == "__main__":
    server = GrokMCPServer()
    server.run_stdio()
