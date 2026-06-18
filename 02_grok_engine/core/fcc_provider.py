#!/usr/bin/env python3
"""FCC (free-claude-code) proxy provider for Grok's ModelRouter.

Tillader Grok at bruge NVIDIA NIM (gratis), OpenRouter, Ollama Cloud gennem FCC proxy.
Start FCC: cd ~/free-claude-code && uv run uvicorn server:app --host 127.0.0.1 --port 8082
Brug: model="fcc/claude-opus-4" eller model="fcc/nvidia_nim" i Grok prompts
"""
import requests
import json
import time

FCC_BASE_URL = "http://127.0.0.1:8082"

def chat_fcc(
    messages: list,
    model: str = "claude-opus-4-20250514",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    stream: bool = False,
) -> str:
    """
    Send chat request gennem free-claude-code proxy.
    """
    # Map model names
    model_map = {
        "claude-opus-4": "claude-opus-4-20250514",
        "claude-sonnet-4": "claude-sonnet-4-20250514",
        "claude-haiku-4": "claude-haiku-4-20250514",
        "claude-3-opus": "claude-3-opus-20240229",
        "claude-3.5-sonnet": "claude-3-5-sonnet-20241022",
        "nvidia_nim": "claude-sonnet-4-20250514",  # Default NIM model
    }
    
    # Extract model after "fcc/" prefix if present
    if model.startswith("fcc/"):
        model = model[4:]
    
    resolved_model = model_map.get(model, model)
    
    # Anthropic Messages API format
    payload = {
        "model": resolved_model,
        "max_tokens": max_tokens,
        "messages": [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in messages],
        "temperature": temperature,
        "stream": False,
    }
    
    try:
        response = requests.post(
            f"{FCC_BASE_URL}/v1/messages",
            json=payload,
            timeout=300,
            headers={"x-api-key": "freecc", "anthropic-version": "2023-06-01"},
        )
        
        # Handle SSE streaming responses
        content_type = response.headers.get("content-type", "")
        if "text/event-stream" in content_type or response.text.startswith("event:"):
            # Parse SSE format
            text_parts = []
            for line in response.text.split("\n"):
                if line.startswith("data:"):
                    try:
                        data = json.loads(line[5:].strip())
                        if data.get("type") == "content_block_delta":
                            delta = data.get("delta", {})
                            if delta.get("type") == "text_delta":
                                text_parts.append(delta.get("text", ""))
                        elif data.get("type") == "message_stop":
                            break
                    except:
                        pass
            return "".join(text_parts) if text_parts else response.text[:1000]
        
        response.raise_for_status()
        data = response.json()
        
        # Parse Anthropic format response
        content_blocks = data.get("content", [])
        text_parts = []
        for block in content_blocks:
            if block.get("type") == "text":
                text_parts.append(block.get("text", ""))
        return "\n".join(text_parts) if text_parts else json.dumps(data)
    
    except requests.exceptions.ConnectionError:
        return "[FEJL] FCC proxy kører ikke. Start med: cd ~/free-claude-code && uv run uvicorn server:app --host 127.0.0.1 --port 8082"
    except Exception as e:
        return f"[FEJL] FCC: {str(e)}"


def fcc_available() -> bool:
    """Tjek om FCC proxy kører"""
    try:
        r = requests.get(f"{FCC_BASE_URL}/v1/models", timeout=3)
        return r.status_code == 200
    except:
        return False
