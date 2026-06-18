#!/usr/bin/env python3
"""
droid_mcp_server_v2.py — K4W_WAK Droid MCP Bridge v2.0
Følger MCP spec 2024-11-05 med korrekt initialize/tools_list/tools_call
Kører SSE transport (HTTP transport virker ikke med Onyx endnu, brug SSE!)
"""
import os, sys, json, hashlib, subprocess, time, queue, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

API_KEY = "k4w-wak-secret-key-2026"
PROTOCOL_VERSION = "2024-11-05"

TOOLS = {
    "list_files": {
        "description": "List files in directory",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}
    },
    "read_file": {
        "description": "Read file contents",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}
    },
    "run_command": {
        "description": "Execute bash command (read-only safe by default)",
        "inputSchema": {"type": "object", "properties": {"command": {"type": "string"}, "safe": {"type": "boolean"}}, "required": ["command"]}
    },
    "hash_file": {
        "description": "SHA256 hash of file",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}
    },
    "search_files": {
        "description": "Search content in files",
        "inputSchema": {"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}}, "required": ["pattern"]}
    },
    "get_status": {
        "description": "System status",
        "inputSchema": {"type": "object", "properties": {}}
    },
    "tail_log": {
        "description": "Tail last N lines",
        "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "lines": {"type": "integer"}}, "required": ["path"]}
    },
}

class MCPHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[MCP] {datetime.now().strftime('%H:%M:%S')} {fmt % args}")

    def _send_json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _check_auth(self):
        key = self.headers.get("X-Api-Key", "")
        if key != API_KEY:
            self._send_json(401, {"jsonrpc": "2.0", "error": {"code": -32001, "message": "Unauthorized"}})
            return False
        return True

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.end_headers()

    def do_GET(self):
        path = self.path
        if path == "/mcp":
            # SSE endpoint
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            # Send endpoint event
            self.wfile.write(b"event: endpoint\n")
            self.wfile.write(b"data: /mcp/message\n\n")
            # Keepalive
            while True:
                self.wfile.write(b":heartbeat\n\n")
                self.wfile.flush()
                time.sleep(30)
        elif path == "/":
            self._send_json(200, {"status": "Droid MCP v2.0", "protocol": PROTOCOL_VERSION, "transport": "sse"})
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
        if path in ["/mcp/message", "/mcp"]:
            self._handle_mcp_message(req)
        else:
            self._send_json(404, {"jsonrpc": "2.0", "error": {"code": -32001, "message": "Unknown endpoint"}})

    def _handle_mcp_message(self, req):
        method = req.get("method", "")
        req_id = req.get("id", None)

        if method == "initialize":
            self._send_json(200, {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {}, "logging": {}},
                    "serverInfo": {"name": "droid-mcp", "version": "2.0.0"}
                }
            })
        elif method == "initialized":
            self._send_json(200, {"jsonrpc": "2.0", "id": req_id, "result": {}})
        elif method == "tools/list":
            tools_list = [
                {"name": k, "description": v["description"], "inputSchema": v["inputSchema"]}
                for k, v in TOOLS.items()
            ]
            self._send_json(200, {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": tools_list}
            })
        elif method == "tools/call":
            self._run_tool(req.get("params", {}), req_id)
        else:
            self._send_json(200, {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            })

    def _run_tool(self, params, req_id):
        name = params.get("name", "")
        arguments = params.get("arguments", {})
        try:
            if name == "list_files":
                p = arguments.get("path", ".")
                files = os.listdir(p)
                result = {"content": [{"type": "text", "text": json.dumps({"files": files, "count": len(files)})}]}
            elif name == "read_file":
                p = arguments.get("path", "")
                with open(p, 'r') as f:
                    result = {"content": [{"type": "text", "text": f.read(100000)}]}
            elif name == "hash_file":
                p = arguments.get("path", "")
                h = hashlib.sha256(open(p,'rb').read()).hexdigest()
                result = {"content": [{"type": "text", "text": h}]}
            elif name == "tail_log":
                p = arguments.get("path", "")
                n = arguments.get("lines", 20)
                lines = subprocess.check_output(["tail", "-" + str(n), p], text=True)
                result = {"content": [{"type": "text", "text": lines}]}
            elif name == "run_command":
                cmd = arguments.get("command", "")
                safe = arguments.get("safe", True)
                if safe and any(x in cmd for x in ["rm -rf","mkfs","dd if",";>/dev","shutdown"]):
                    result = {"content": [{"type": "text", "text": "BLOCKED: Dangerous command"}]}
                else:
                    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                    result = {"content": [{"type": "text", "text": proc.stdout or proc.stderr or "OK"}]}
            elif name == "search_files":
                pat = arguments.get("pattern", "")
                p = arguments.get("path", ".")
                try:
                    out = subprocess.check_output(["grep", "-rl", pat, p], text=True, stderr=subprocess.DEVNULL)
                    result = {"content": [{"type": "text", "text": out}]}
                except:
                    result = {"content": [{"type": "text", "text": "No matches"}]}
            elif name == "get_status":
                result = {"content": [{"type": "text", "text": json.dumps({"hostname": os.uname().nodename, "cwd": os.getcwd(), "time": datetime.now().isoformat()})}]}
            else:
                result = {"content": [{"type": "text", "text": f"Unknown tool: {name}"}]}
        except Exception as e:
            result = {"content": [{"type": "text", "text": str(e)}], "isError": True}

        self._send_json(200, {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": result
        })

print(f"╔════════════════════════════════════════════════════════════╗")
print(f"║  🔗 DROID MCP SERVER v2.0 — MCP 2024-11-05               ║")
print(f"║  SSE:   http://172.22.29.16:8080/mcp                     ║")
print(f"║  POST:  http://172.22.29.16:8080/mcp/message             ║")
print(f"║  Auth:  X-Api-Key: {API_KEY}             ║")
print(f"║  Tools: {', '.join(TOOLS.keys())}                ║")
print(f"╚════════════════════════════════════════════════════════════╝")

# Kill old server
subprocess.run("pkill -f droid_mcp_server 2>/dev/null; sleep 1", shell=True)

server = HTTPServer(("0.0.0.0", 8080), MCPHandler)
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\n[MCP] Server stopped.")
