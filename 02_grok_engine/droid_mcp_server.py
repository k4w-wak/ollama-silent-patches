#!/usr/bin/env python3
"""
don_mcp_server.py — K4W_WAK Droid MCP Bridge v1.0
Enkel MCP HTTP server der udstiller Droid tools til Onyx app.
Kører på 0.0.0.0:8080 så Onyx (Windows) kan se den.
Auth: API key via X-Api-Key header.
"""
import os, sys, json, hashlib, subprocess, threading, re
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

API_KEY = "k4w-wak-secret-key-2026"
MCP_VERSION = "2024-11-05"
SERVER_PORT = 8080

TOOLS = {
    "list_files": {
        "description": "List files in directory",
        "parameters": {"path": {"type": "string", "description": "Dir path"}},
        "returns": ["file_list"]
    },
    "read_file": {
        "description": "Read file contents",
        "parameters": {"path": {"type": "string", "description": "File path"}},
        "returns": ["content"]
    },
    "run_command": {
        "description": "Execute bash command safely (read-only by default)",
        "parameters": {
            "command": {"type": "string", "description": "Shell command"},
            "safe": {"type": "boolean", "description": "Read-only safe mode", "default": True}
        },
        "returns": ["stdout", "stderr", "exit_code"]
    },
    "hash_file": {
        "description": "SHA256 hash of file",
        "parameters": {"path": {"type": "string"}},
        "returns": ["sha256"]
    },
    "search_files": {
        "description": "Search content in files",
        "parameters": {"pattern": {"type": "string"}, "path": {"type": "string"}},
        "returns": ["matches"]
    },
    "get_status": {
        "description": "System status and uptime",
        "parameters": {},
        "returns": ["status"]
    },
    "tail_log": {
        "description": "Tail last N lines of file",
        "parameters": {"path": {"type": "string"}, "lines": {"type": "integer", "default": 20}},
        "returns": ["lines"]
    },
}

class MCPHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[MCP] {datetime.now().strftime('%H:%M:%S')} {self.address_string()} {fmt % args}")

    def _send_json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _check_auth(self):
        key = self.headers.get("X-Api-Key", "")
        if key != API_KEY:
            self._send_json(401, {"error": "Invalid API key"})
            return False
        return True

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        if self.path in ["/mcp", "/"]:
            self._send_json(200, {
                "status": "Droid MCP v1.2",
                "protocol": "mcp",
                "tools_available": len(TOOLS),
                "tools":[
                    {"name":k,"description":v["description"],"inputSchema":{"type":"object","properties":v["parameters"]}}
                    for k,v in TOOLS.items()
                ],
                "auth":"API Key",
                "time": datetime.now().isoformat()
            })
        elif self.path == "/tools" or self.path == "/mcp/v1/tools" or self.path == "/list_tools":
            self._send_json(200, {"tools": [
                {"name":k,"description":v["description"],"inputSchema":{"type":"object","properties":v["parameters"]}}
                for k,v in TOOLS.items()
            ]})
        elif self.path.startswith("/health"):
            self._send_json(200, {"healthy": True})
        else:
            self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        if not self._check_auth():
            return

        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len).decode() if content_len > 0 else "{}"
        try:
            req = json.loads(body)
        except:
            req = {}

        path = self.path
        if path in ["/call", "/mcp/call"]:
            tool = req.get("tool", "")
            params = req.get("params", {})
            self._run_tool(tool, params)
        elif path in ["/message", "/mcp/message"]:
            self._handle_mcp_message(req)
        else:
            self._send_json(404, {"error": "Unknown endpoint"})

    def _run_tool(self, tool, params):
        try:
            result = {"status": "ok", "tool": tool, "result": None}
            if tool == "list_files":
                p = params.get("path", ".")
                files = os.listdir(p)
                result["result"] = {"files": files, "count": len(files)}
            elif tool == "read_file":
                p = params.get("path", "")
                with open(p, 'r') as f:
                    result["result"] = {"content": f.read(100000), "preview": True}
            elif tool == "hash_file":
                p = params.get("path", "")
                h = hashlib.sha256(open(p,'rb').read()).hexdigest()
                result["result"] = {"sha256": h}
            elif tool == "tail_log":
                p = params.get("path", "")
                n = params.get("lines", 20)
                lines = subprocess.check_output(["tail", "-" + str(n), p], text=True)
                result["result"] = {"lines": lines.split("\n")}
            elif tool == "run_command":
                cmd = params.get("command", "")
                safe = params.get("safe", True)
                if safe and any(x in cmd for x in ["rm -rf","mkfs","dd if",";>/dev","shutdown"]):
                    result = {"status": "blocked", "error": "Dangerous command blocked"}
                else:
                    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                    result["result"] = {
                        "stdout": proc.stdout,
                        "stderr": proc.stderr,
                        "exit_code": proc.returncode
                    }
            elif tool == "search_files":
                pat = params.get("pattern", "")
                p = params.get("path", ".")
                out = subprocess.check_output(["grep", "-rl", pat, p], text=True, stderr=subprocess.DEVNULL)
                result["result"] = {"matches": out.strip().split("\n") if out else []}
            elif tool == "get_status":
                result["result"] = {
                    "hostname": os.uname().nodename,
                    "cwd": os.getcwd(),
                    "time": datetime.now().isoformat(),
                    "tools_available": list(TOOLS.keys())
                }
            else:
                result = {"status": "error", "error": f"Unknown tool: {tool}"}

            self._send_json(200, result)
        except Exception as e:
            self._send_json(500, {"status": "error", "error": str(e)})

    def _handle_mcp_message(self, req):
        method = req.get("method", "")
        if method == "initialize":
            self._send_json(200, {
                "jsonrpc": "2.0",
                "id": req.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}, "logging": {}},
                    "serverInfo": {"name": "droid-mcp", "version": "1.1.0"}
                }
            })
        elif method == "initialized":
            self._send_json(200, {"jsonrpc": "2.0", "id": req.get("id"), "result": {}})
        elif method == "tools/list":
            self._send_json(200, {
                "jsonrpc": "2.0",
                "id": req.get("id"),
                "result": {"tools": [
                    {"name": k, "description": v["description"], "inputSchema": {"type": "object", "properties": v["parameters"]}}
                    for k, v in TOOLS.items()
                ]}
            })
        elif method == "tools/call":
            tool = req.get("params", {}).get("name", "")
            params = req.get("params", {}).get("arguments", {})
            self._run_tool(tool, params)
        else:
            self._send_json(400, {"jsonrpc": "2.0", "id": req.get("id"), "error": {"code": -32601, "message": f"Unknown method: {method}"}})

print(f"╔══════════════════════════════════════════════════════╗")
print(f"║  🔗 DROID MCP SERVER v1.0                            ║")
print(f"║  URL: http://0.0.0.0:{SERVER_PORT}/mcp              ║")
print(f"║  Auth: X-Api-Key: {API_KEY}              ║")
print(f"║  WSL2: http://{os.popen('hostname -I').read().split()[0] if os.popen('hostname -I').read() else 'localhost'}:{SERVER_PORT}/mcp  ║")
print(f"╚══════════════════════════════════════════════════════╝")
print(f"[INFO] Tools: {', '.join(TOOLS.keys())}")
server = HTTPServer(("0.0.0.0", SERVER_PORT), MCPHandler)
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\n[MCP] Server stopped.")
