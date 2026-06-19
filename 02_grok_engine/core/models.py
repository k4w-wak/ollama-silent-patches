#!/usr/bin/env python3
"""
Grok Multi-Model Router
Ollama primær — gratis, ubegrænset, FC understøttet
"""

import os
import requests
import json
import time
from typing import Optional, Dict, Any, Generator, List
from dataclasses import dataclass

# Simple color codes for logging (avoid circular imports)
_C_RED = '\033[91m'
_C_YELLOW = '\033[93m'
_C_DIM = '\033[2m'
_C_END = '\033[0m'

try:
    from .config import (
        OLLAMA_BASE_URL, OLLAMA_MODELS,
        MODEL_FALLBACK_CHAIN,
    )
except ImportError:
    from config import (
        OLLAMA_BASE_URL, OLLAMA_MODELS,
        MODEL_FALLBACK_CHAIN,
    )


@dataclass
class ModelStatus:
    """Status for en model/provider"""
    provider: str
    model: str
    available: bool = False
    response_time_ms: float = 0.0
    error: Optional[str] = None



def _fix_double_utf8(text: str) -> str:
    """
    Ollama Cloud har set dobbelt-UTF-8-mojibake i SSE streams.
    Gendan korrekte tegn hvis vi ser typiske mojibake-mønstre.
    """
    if not text:
        return text
    if any(c in text for c in ("Ã¦", "Ã¸", "Ã¥", "Ã©", "Ã¼", "Ã±", "Ã", "â")):
        try:
            return text.encode("latin-1").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            return text
    return text

class ModelRouter:
    """
    Router der automatisk vælger den bedste tilgængelige model.
    
    Prioritet:
    1. Ollama (primær, FC understttet)
    2. Fallback kæde fra config
    
    Ingen GROQ, ingen rate limits, ingen API keys.
    """
    
    # Ollama Cloud API — OpenAI-kompatibelt endpoint
    OLLAMA_CLOUD_URL = "https://ollama.com/v1"
    OLLAMA_CLOUD_KEY = os.environ.get("OLLAMA_API_KEY", "27be72d8f0ff4ef79db5bee0f8758b63.6SrdafFDTNf9RoGMFy_HrB_h")
    
    def __init__(self):
        self.active_provider = None
        self.active_model = None
        self.status_cache: Dict[str, ModelStatus] = {}
        self._last_check = 0
        
    def check_ollama(self) -> ModelStatus:
        """Tjek om Ollama k\u00f8rer"""
        status = ModelStatus(provider="ollama", model="glm-5.1:cloud")
        
        try:
            start = time.time()
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                status.available = True
                status.response_time_ms = elapsed
            else:
                status.available = False
                status.error = f"HTTP {response.status_code}"
        except Exception as e:
            status.available = False
            status.error = str(e)
        
        self.status_cache["ollama"] = status
        return status
    
    def auto_select(self) -> tuple:
        """
        Vælg automatisk den bedste tilgængelige model.
        Returns: (provider, model)
        
        Cloud-modeller tjekkes via /api/show (ikke /api/tags som kun viser lokale modeller).
        """
        # Check providers i prioriteret rækkefølge
        for entry in MODEL_FALLBACK_CHAIN:
            provider = entry["provider"]
            model = entry["model"]
            
            if provider == "ollama":
                status = self.check_ollama()
                if status.available:
                    try:
                        # Cloud-modeller: tjek via /api/show
                        resp = requests.post(
                            f"{OLLAMA_BASE_URL}/api/show",
                            json={"name": model},
                            timeout=5
                        )
                        if resp.status_code == 200:
                            self.active_provider = "ollama"
                            self.active_model = model
                            return ("ollama", model)
                    except:
                        pass
        
        # Ingen tilgængelige — brug Ollama 3b som sidste udvej
        self.active_provider = "ollama"
        self.active_model = "llama3.2:3b"
        return ("ollama", "llama3.2:3b")
    
    @staticmethod
    def _clean_messages_for_ollama(messages: list) -> list:
        """Fjern tool_calls og tool roles som Ollama ikke forstaar (kun for text-parsing mode)."""
        clean = []
        for msg in messages:
            # Fjern tool role — Ollama forstaar ikke 'tool'
            if msg.get("role") == "tool":
                clean.append({"role": "assistant", "content": f"Tool result: {msg.get('content', '')}"})
                continue
            # Fjern tool_calls fra assistant messages
            m = dict(msg)
            if "tool_calls" in m:
                # Konverter tool_calls til tekst
                calls = m.pop("tool_calls")
                texts = []
                for tc in calls:
                    func = tc.get("function", {})
                    texts.append(f"Called {func.get('name', '?')}({func.get('arguments', '')})")
                m["content"] = m.get("content", "") + "\n" + "\n".join(texts)
            clean.append(m)
        return clean

    def chat_ollama(
        self,
        messages: list,
        model: str = None,
        temperature: float = 1.5,
        stream: bool = False,
        format: dict = None,
        keep_alive: str = "5m",
    ) -> Any:
        """
        Send chat request til Ollama.
        format: JSON schema dict for structured output (optional)
        keep_alive: how long to keep model in memory (default 5m)
        """
        model = model or self.active_model or "llama3.1:8b"
        # Strip "ollama/" prefix if present — API expects bare model name
        if model.startswith("ollama/"):
            model = model[len("ollama/"):]
        messages = self._clean_messages_for_ollama(messages)
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "keep_alive": keep_alive,
            "options": {
                "temperature": temperature,
                "num_ctx": 131072,
                "num_gpu": 1,
                "top_p": 0.95,
                "top_k": 40,
                "repeat_penalty": 1.05,
                "seed": 42,
            }
        }
        
        # Structured Output: JSON schema enforcement
        if format:
            payload["format"] = format
        
        # Cloud API override — KUN hvis OLLAMA_CLOUD=1 er sat eksplicit
        import os
        use_cloud = os.environ.get("OLLAMA_CLOUD", "") == "1"
        api_key = os.environ.get("OLLAMA_API_KEY")
        if use_cloud and api_key:
            base_url = "https://ollama.com"
            headers = {"Authorization": f"Bearer {api_key}"}
        else:
            base_url = OLLAMA_BASE_URL
            headers = {}
        url = f"{base_url}/api/chat"
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if stream:
                    response = requests.post(url, json=payload, headers=headers, stream=True, timeout=360)
                    response.raise_for_status()
                    return response
                else:
                    response = requests.post(url, json=payload, headers=headers, timeout=360)
                    response.raise_for_status()
                    data = response.json()
                    return data["message"]["content"]
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 500:
                    if attempt < max_retries - 1:
                        wait = (attempt + 1) * 3  # 3s, 6s, 9s
                        print(f"\n[OLLAMA 500 — proever igen om {wait}s... (forsoeg {attempt+1}/{max_retries})]")
                        time.sleep(wait)
                        continue
                raise
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    wait = (attempt + 1) * 5
                    print(f"\n[OLLAMA connection fejl — proever igen om {wait}s... ({attempt+1}/{max_retries})]")
                    time.sleep(wait)
                    continue
                raise
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    wait = (attempt + 1) * 10
                    print(f"\n[OLLAMA timeout — proever igen om {wait}s... ({attempt+1}/{max_retries})]")
                    time.sleep(wait)
                    continue
                raise
            break
        return "[FEJL] Ollama ikke tilgaengelig efter 3 forsoeg"
    
    @staticmethod
    def is_cloud_model(model: str) -> bool:
        """Tjek om model er en cloud model (:cloud suffix eller kendt cloud navn)"""
        if not model:
            return False
        return model.endswith(":cloud") or ":cloud:" in model
    

    def chat_ollama_cloud(
        self,
        messages: list,
        model: str = None,
        temperature: float = 0.85,
        max_tokens: int = 16384,
        tools: list = None,
        stream: bool = False,
    ) -> Any:
        """
        Send chat request til Ollama Cloud via OpenAI-kompatibelt /v1/chat/completions endpoint.
        Understøtter function calling (tools) med OpenAI format!
        
        Args:
            messages: OpenAI format messages
            model: Model navn (uden :cloud suffix)
            temperature: Temperatur
            max_tokens: Max tokens
            tools: OpenAI format tool schemas (optional)
        
        Returns:
            dict med 'content', 'tool_calls', 'reasoning' eller str for simple responses
        """
        model = model or self.active_model or "glm-5.1"
        # Strip :cloud suffix for API call
        cloud_model = model.replace(":cloud", "")
        # Also strip :size suffixes like :397b, :480b, :120b, :8b, :24b, :31b
        import re as _re
        cloud_model = _re.sub(r':[\d]+[bB]$', '', cloud_model)
        
        api_key = self.OLLAMA_CLOUD_KEY
        base_url = self.OLLAMA_CLOUD_URL
        
        # Configurable timeouts from config
        try:
            from core.config import CLOUD_REQUEST_TIMEOUT, CLOUD_MAX_RETRIES, CLOUD_RETRY_BASE_WAIT
            request_timeout = CLOUD_REQUEST_TIMEOUT
            max_retries = CLOUD_MAX_RETRIES
            retry_base_wait = CLOUD_RETRY_BASE_WAIT
        except ImportError:
            request_timeout = 120
            max_retries = 3
            retry_base_wait = 5
        
        payload = {
            "model": cloud_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        if tools:
            payload["tools"] = tools
        if stream:
            payload["stream"] = True
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        url = f"{base_url}/chat/completions"
        
        last_error = None
        for attempt in range(max_retries):
            try:
                print(f"{_C_DIM}[CLOUD] Request {attempt+1}/{max_retries}, timeout={request_timeout}s...{_C_END}", flush=True)
                if stream:
                    response = requests.post(url, json=payload, headers=headers, timeout=request_timeout, stream=True)
                    response.raise_for_status()

                    def _parse_sse(resp):
                        full_content = ""
                        full_reasoning = ""
                        tool_calls_map = {}
                        for raw in resp.iter_lines(decode_unicode=True):
                            if not raw or not raw.startswith("data:"):
                                continue
                            data_str = raw[5:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                            except json.JSONDecodeError:
                                continue
                            choice = data.get("choices", [{}])[0]
                            delta = choice.get("delta", {})
                            if delta.get("content"):
                                piece = _fix_double_utf8(delta["content"])
                                full_content += piece
                                yield {"type": "content", "content": piece}
                            if delta.get("reasoning"):
                                piece = _fix_double_utf8(delta["reasoning"])
                                full_reasoning += piece
                                yield {"type": "reasoning", "content": piece}
                            for tc in delta.get("tool_calls") or []:
                                idx = tc.get("index", 0)
                                entry = tool_calls_map.setdefault(idx, {"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                                if tc.get("id"):
                                    entry["id"] = tc["id"]
                                fn = tc.get("function") or {}
                                if fn.get("name"):
                                    entry["function"]["name"] += fn["name"]
                                if fn.get("arguments"):
                                    entry["function"]["arguments"] += fn["arguments"]
                        tool_calls = [tool_calls_map[k] for k in sorted(tool_calls_map)] if tool_calls_map else None
                        yield {
                            "type": "final",
                            "content": full_content,
                            "reasoning": full_reasoning,
                            "tool_calls": tool_calls,
                        }

                    return _parse_sse(response)

                response = requests.post(url, json=payload, headers=headers, timeout=request_timeout)
                
                if response.status_code == 429:
                    # Rate limited — vent og prøv igen
                    wait = retry_base_wait * (attempt + 1)
                    print(f"\n{_C_YELLOW}[CLOUD] Rate limited (429) — venter {wait}s... ({attempt+1}/{max_retries}){_C_END}", flush=True)
                    if attempt < max_retries - 1:
                        time.sleep(wait)
                        continue
                    return {"content": f"[FEJL] Ollama Cloud rate limited efter {max_retries} forsøg", "tool_calls": None, "reasoning": None}
                
                if response.status_code == 502 or response.status_code == 503:
                    # Service unavailable — vent og prøv igen
                    wait = retry_base_wait * (attempt + 1)
                    print(f"\n{_C_YELLOW}[CLOUD] Service unavailable ({response.status_code}) — venter {wait}s... ({attempt+1}/{max_retries}){_C_END}", flush=True)
                    if attempt < max_retries - 1:
                        time.sleep(wait)
                        continue
                    return {"content": "[FEJL] Ollama Cloud utilgængelig", "tool_calls": None, "reasoning": None}
                
                if response.status_code == 408:
                    # Request timeout from server
                    wait = retry_base_wait * (attempt + 1)
                    print(f"\n{_C_YELLOW}[CLOUD] Server timeout (408) — venter {wait}s... ({attempt+1}/{max_retries}){_C_END}", flush=True)
                    if attempt < max_retries - 1:
                        time.sleep(wait)
                        continue
                    return {"content": f"[FEJL] Ollama Cloud server timeout efter {max_retries} forsøg", "tool_calls": None, "reasoning": None}
                
                response.raise_for_status()
                data = response.json()
                
                choice = data.get("choices", [{}])[0]
                msg = choice.get("message", {})
                content = _fix_double_utf8(msg.get("content", ""))
                reasoning = _fix_double_utf8(msg.get("reasoning", ""))
                tool_calls = msg.get("tool_calls")
                
                # Cost tracking
                usage = data.get("usage", {})
                input_tokens = usage.get("prompt_tokens", 0)
                output_tokens = usage.get("completion_tokens", 0)
                try:
                    from core.cost import cost_track
                    cost_track(model=f"ollama-cloud/{cloud_model}", input_tokens=input_tokens, output_tokens=output_tokens)
                except:
                    pass
                
                if tools:
                    # Return structured dict for function calling
                    return {
                        "content": content,
                        "reasoning": reasoning,
                        "tool_calls": tool_calls,
                        "finish_reason": choice.get("finish_reason"),
                    }
                else:
                    # Simple text response
                    answer = content if content else reasoning
                    return answer if answer else "[FEJL] Tom respons fra Ollama Cloud"
                    
            except requests.exceptions.HTTPError as e:
                last_error = str(e)
                print(f"\n{_C_RED}[CLOUD] HTTP fejl: {last_error[:100]} ({attempt+1}/{max_retries}){_C_END}", flush=True)
                if attempt < max_retries - 1:
                    time.sleep(retry_base_wait)
                    continue
                return {"content": f"[FEJL] Ollama Cloud HTTP fejl: {last_error[:200]}", "tool_calls": None, "reasoning": None}
            except requests.exceptions.Timeout:
                last_error = f"Timeout efter {request_timeout}s"
                print(f"\n{_C_RED}[CLOUD] {last_error} ({attempt+1}/{max_retries}){_C_END}", flush=True)
                if attempt < max_retries - 1:
                    time.sleep(retry_base_wait * (attempt + 1))
                    continue
                return {"content": f"[FEJL] Ollama Cloud timeout efter {max_retries} forsøg ({request_timeout}s per request)", "tool_calls": None, "reasoning": None}
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)[:80]}"
                print(f"\n{_C_RED}[CLOUD] {last_error} ({attempt+1}/{max_retries}){_C_END}", flush=True)
                if attempt < max_retries - 1:
                    time.sleep(retry_base_wait)
                    continue
                return {"content": f"[FEJL] Ollama Cloud forbindelsesfejl: {last_error}", "tool_calls": None, "reasoning": None}
            except Exception as e:
                last_error = f"Unexpected: {str(e)[:100]}"
                print(f"\n{_C_RED}[CLOUD] {last_error} ({attempt+1}/{max_retries}){_C_END}", flush=True)
                return {"content": f"[FEJL] Ollama Cloud: {last_error}", "tool_calls": None, "reasoning": None}
        
        return {"content": f"[FEJL] Ollama Cloud fejlede efter {max_retries} forsøg: {last_error}", "tool_calls": None, "reasoning": None}

    def chat(
        self,
        messages: list,
        model: str = None,
        provider: str = None,
        temperature: float = 1.5,
        max_tokens: int = 4096,
        stream: bool = False,
    ) -> Any:
        """
        Unified chat — vælg automatisk provider, eller brug den angivne.
        Falder tilbage automatisk ved fejl.
        """
        from core.cost import cost_track
        provider = provider or self.active_provider or "groq"
        model = model or self.active_model
        
        try:
            if provider == "groq":
                try:
                    result = self.chat_groq(messages, model, temperature, max_tokens, stream)
                    # Ollama: no cost tracking needed
                    return result
                except Exception as e:
                    # Rate limited? Vent og prøv igen
                    if "429" in str(e) or "rate" in str(e).lower():
                        print(f"\n[GROQ rate limited — venter 3s og proever igen...]")
                        time.sleep(3)
                        try:
                            result = self.chat_groq(messages, model, temperature, max_tokens, stream)
                            # Ollama: no cost
                            return result
                        except Exception:
                            pass
                    # Model fejlede — prøv næste i fallback chain
                    print(f"\n[GROQ fejlede: {str(e)[:80]}] → falder tilbage til Ollama...")
                    provider = "ollama"
                    model = "llama3.1:8b"

            if provider == "ollama":
                # Cloud models route to /v1/chat/completions
                if self.is_cloud_model(model):
                    result = self.chat_ollama_cloud(messages, model, temperature, max_tokens)
                    # chat_ollama_cloud may return str or dict — extract text
                    if isinstance(result, dict):
                        result = result.get("content", "") or result.get("reasoning", "") or str(result)
                    return result
                else:
                    result = self.chat_ollama(messages, model, temperature, stream)
                    from core.cost import cost_track
                    # Ollama har ikke usage data — estimator baseret på ord
                    input_est = sum(len(str(m.get('content','')).split()) for m in messages if m.get('content'))
                    output_est = len(str(result).split()) * 1.3
                    # Konverter ord til tokens (ca 1.3 tokens per ord)
                    cost_track(model=f"ollama/{model}", input_tokens=int(input_est*1.3), output_tokens=int(output_est*1.3))
                    return result
            
            if provider == "fcc":
                # FCC proxy removed — fallback to Ollama Cloud
                print("[FCC] Proxy fjernet. Bruger Ollama Cloud i stedet...")
                result = self.chat_ollama_cloud(messages, model or "glm-5.1:cloud", temperature, max_tokens)
                if isinstance(result, dict):
                    result = result.get("content", "") or result.get("reasoning", "") or str(result)
                return result

        except Exception as e:
            return f"[FEJL] Ingen model tilgængelig: {str(e)}"
    
    def stream_tokens(
        self,
        messages: list,
        model: str = None,
        provider: str = None,
        temperature: float = 1.5,
    ) -> Generator[str, None, None]:
        """
        Stream tokens live — giver ét token ad gangen.
        Automatisk fallback ved fejl.
        """
        provider = provider or self.active_provider or "groq"
        model = model or self.active_model
        
        try:
            if provider == "groq":
                try:
                    response = self.chat_groq(messages, model, temperature, stream=True)
                    for line in response.iter_lines():
                        if line:
                            line = line.decode('utf-8') if isinstance(line, bytes) else line
                            if line.startswith('data: '):
                                data_str = line[6:]
                                if data_str.strip() == '[DONE]':
                                    return
                                try:
                                    data = json.loads(data_str)
                                    delta = data.get("choices", [{}])[0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                                except json.JSONDecodeError:
                                    continue
                    return
                except Exception as e:
                    print(f"\n[GROQ stream fejlede: {str(e)[:50]}] → Ollama...")
                    provider = "ollama"
                    model = "llama3.1:8b"
            
            if provider == "ollama":
                response = self.chat_ollama(messages, model, temperature, stream=True)
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                token = data["message"]["content"]
                                if token:
                                    yield token
                        except json.JSONDecodeError:
                            continue
        
        except Exception as e:
            yield f"\n[FEJL] Stream fejlede: {str(e)}"
    
    def get_status_report(self) -> str:
        """Returner status for alle providers"""
        lines = []
        
        # GROQ removed
        
        ollama = self.check_ollama()
        o_status = "✅" if ollama.available else "❌"
        o_time = f"{ollama.response_time_ms:.0f}ms" if ollama.available else ollama.error
        lines.append(f"  Ollama: {o_status} {ollama.model} ({o_time})")
        
        active = f"{self.active_provider}/{self.active_model}" if self.active_provider else "ikke valgt"
        lines.append(f"  Aktiv: {active}")
        
        return "\n".join(lines)
# === Gemini Provider ===
import os
try:
    from google import genai as genai
except ImportError:
    try:
        from google.generativeai import GenerativeModel as genai
    except ImportError:
        genai = None

class GeminiProvider:
    def __init__(self, api_key=None, model_name="gemini-2.0-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY mangler")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

    def generate(self, prompt, **kwargs):
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text
