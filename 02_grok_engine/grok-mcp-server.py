#!/usr/bin/env python3
"""
Grok Engine MCP Server — Exposes Grok Engine (grok_run.py) as MCP tools.

Allows Hermes to invoke Grok missions and read Grok state (sessions, findings,
RAG stats, lessons) directly, without spawning the interactive REPL.

Transport: stdio (default) — started by Hermes MCP client.
"""

import asyncio
import json
import os
import sys
import glob
import logging
from datetime import datetime
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ServerCapabilities,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GROK_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, GROK_DIR)
sys.path.insert(0, os.path.join(GROK_DIR, 'core'))

GROK_SESSIONS_DIR = os.path.expanduser("~/.grok/sessions")
GROK_LESSONS_DIR = os.path.expanduser("~/.grok/lessons")
GROK_RAG_DIR = os.path.expanduser("~/.grok/rag")
GROK_FACTS = os.path.expanduser("~/.grok/facts.json")
GROK_HISTORY = os.path.expanduser("~/.grok/history.jsonl")

logging.basicConfig(level=logging.INFO, stream=sys.stderr,
                    format="[grok-mcp] %(levelname)s: %(message)s")
log = logging.getLogger("grok-mcp")

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def grok_run_task(prompt: str, model: str = "glm-5.1:cloud", iterations: int = 20) -> str:
    """Run a Grok mission non-interactively via grok_run.run_mission()."""
    try:
        from grok_run import run_mission
        result = run_mission(prompt, model=model, iterations=iterations)
        return result if result else "(no output)"
    except Exception as e:
        return f"Error: {e}"


def grok_list_sessions(limit: int = 10) -> str:
    """List recent Grok session files."""
    if not os.path.isdir(GROK_SESSIONS_DIR):
        return f"Sessions dir not found: {GROK_SESSIONS_DIR}"
    files = sorted(glob.glob(os.path.join(GROK_SESSIONS_DIR, "*.jsonl")),
                   key=os.path.getmtime, reverse=True)[:limit]
    if not files:
        return "No sessions found."
    lines = [f"Recent {len(files)} sessions in {GROK_SESSIONS_DIR}:"]
    for f in files:
        size = os.path.getsize(f)
        mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M")
        lines.append(f"  {os.path.basename(f):40}  {size:>8} bytes  {mtime}")
    return "\n".join(lines)


def grok_read_session(filename: str, max_lines: int = 50) -> str:
    """Read a Grok session file (.jsonl). Returns last N entries."""
    path = os.path.join(GROK_SESSIONS_DIR, filename)
    if not os.path.exists(path):
        return f"Session not found: {path}"
    try:
        with open(path) as f:
            lines = f.readlines()
        # Show last N lines
        tail = lines[-max_lines:] if len(lines) > max_lines else lines
        return f"=== {filename} ({len(lines)} total lines, showing last {len(tail)}) ===\n" + "".join(tail)
    except Exception as e:
        return f"Error: {e}"


def grok_get_facts(limit: int = 20) -> str:
    """Read facts database (key-value store of learned facts)."""
    if not os.path.exists(GROK_FACTS):
        return f"Facts file not found: {GROK_FACTS}"
    try:
        with open(GROK_FACTS) as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return f"Facts file is not a dict: {type(data).__name__}"
        items = list(data.items())[:limit]
        lines = [f"Facts ({len(data)} total, showing first {len(items)}):"]
        for k, v in items:
            v_str = str(v)[:200]
            lines.append(f"  {k}: {v_str}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def grok_list_lessons(limit: int = 10) -> str:
    """List recent lesson files (learned patterns from past sessions)."""
    if not os.path.isdir(GROK_LESSONS_DIR):
        return f"Lessons dir not found: {GROK_LESSONS_DIR}"
    files = sorted(glob.glob(os.path.join(GROK_LESSONS_DIR, "*")),
                   key=os.path.getmtime, reverse=True)[:limit]
    if not files:
        return "No lessons found."
    lines = [f"Recent {len(files)} lessons in {GROK_LESSONS_DIR}:"]
    for f in files:
        size = os.path.getsize(f)
        mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M")
        lines.append(f"  {os.path.basename(f):50}  {size:>8} bytes  {mtime}")
    return "\n".join(lines)


def grok_rag_stats() -> str:
    """Show RAG knowledge base statistics."""
    if not os.path.isdir(GROK_RAG_DIR):
        return f"RAG dir not found: {GROK_RAG_DIR}"
    try:
        items = []
        for root, _, files in os.walk(GROK_RAG_DIR):
            for f in files:
                fp = os.path.join(root, f)
                items.append((fp, os.path.getsize(fp)))
        items.sort(key=lambda x: x[1], reverse=True)
        total_size = sum(s for _, s in items)
        lines = [
            f"RAG dir: {GROK_RAG_DIR}",
            f"Total files: {len(items)}",
            f"Total size: {total_size:,} bytes",
            "Top 10 largest files:"
        ]
        for fp, sz in items[:10]:
            lines.append(f"  {sz:>10,}  {os.path.relpath(fp, GROK_RAG_DIR)}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def grok_search_history(query: str, limit: int = 10) -> str:
    """Search Grok history (jsonl) for a substring across prompts/responses."""
    if not os.path.exists(GROK_HISTORY):
        return f"History file not found: {GROK_HISTORY}"
    try:
        matches = []
        with open(GROK_HISTORY) as f:
            for ln, line in enumerate(f, 1):
                if query.lower() in line.lower():
                    try:
                        obj = json.loads(line)
                        snippet = str(obj)[:200]
                        matches.append(f"L{ln}: {snippet}")
                    except:
                        matches.append(f"L{ln}: {line[:200].strip()}")
                if len(matches) >= limit:
                    break
        if not matches:
            return f"No matches for '{query}' in {GROK_HISTORY}"
        return f"Found {len(matches)} matches for '{query}':\n" + "\n".join(matches)
    except Exception as e:
        return f"Error: {e}"


# ---------------------------------------------------------------------------
# MCP server setup
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "name": "grok_run_task",
        "description": "Run a Grok Engine mission non-interactively. Returns the final response. Use for complex multi-step security/recon tasks that need Grok's full tool set.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "The task/prompt for Grok."},
                "model": {"type": "string", "description": "Model ID (default: glm-5.1:cloud).", "default": "glm-5.1:cloud"},
                "iterations": {"type": "integer", "description": "Max ReAct iterations (default: 20).", "default": 20},
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "grok_list_sessions",
        "description": "List recent Grok session files.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max sessions to show (default: 10).", "default": 10},
            },
        },
    },
    {
        "name": "grok_read_session",
        "description": "Read a Grok session transcript (.jsonl).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Session filename (e.g. session_20260528_214421.jsonl)."},
                "max_lines": {"type": "integer", "description": "Max lines to return (default: 50).", "default": 50},
            },
            "required": ["filename"],
        },
    },
    {
        "name": "grok_get_facts",
        "description": "Read Grok's facts database (key-value store of learned facts).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max facts to show (default: 20).", "default": 20},
            },
        },
    },
    {
        "name": "grok_list_lessons",
        "description": "List recent lesson files (learned patterns from past Grok sessions).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max lessons to show (default: 10).", "default": 10},
            },
        },
    },
    {
        "name": "grok_rag_stats",
        "description": "Show Grok RAG knowledge base statistics (file count, sizes).",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "grok_search_history",
        "description": "Search Grok history file for a substring.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query substring."},
                "limit": {"type": "integer", "description": "Max matches (default: 10).", "default": 10},
            },
            "required": ["query"],
        },
    },
]

TOOL_HANDLERS = {
    "grok_run_task": lambda args: grok_run_task(
        args["prompt"],
        args.get("model", "glm-5.1:cloud"),
        args.get("iterations", 20),
    ),
    "grok_list_sessions": lambda args: grok_list_sessions(args.get("limit", 10)),
    "grok_read_session": lambda args: grok_read_session(args["filename"], args.get("max_lines", 50)),
    "grok_get_facts": lambda args: grok_get_facts(args.get("limit", 20)),
    "grok_list_lessons": lambda args: grok_list_lessons(args.get("limit", 10)),
    "grok_rag_stats": lambda args: grok_rag_stats(),
    "grok_search_history": lambda args: grok_search_history(args["query"], args.get("limit", 10)),
}

server = Server("grok-mcp-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name=t["name"], description=t["description"], inputSchema=t["inputSchema"])
        for t in TOOL_DEFINITIONS
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    handler = TOOL_HANDLERS.get(name)
    if handler is None:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    try:
        result = handler(arguments)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        log.exception("Tool %s failed", name)
        return [TextContent(type="text", text=f"Error in {name}: {e}")]


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

async def main_stdio():
    log.info("Starting Grok MCP Server (stdio transport)")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="grok-mcp-server",
                server_version="1.0.0",
                capabilities=ServerCapabilities(),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main_stdio())
