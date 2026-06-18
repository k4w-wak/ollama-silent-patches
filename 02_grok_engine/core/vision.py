#!/usr/bin/env python3
"""
Grok Vision Module — Screenshot & image analyse med Ollama vision models
Analyserer web screenshots, Nmap grafer, Kismet kort, og andre billeder.
Understøtter både lokale Ollama vision models og cloud models.
"""

import os
import json
import base64
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    from .config import OLLAMA_BASE_URL, VISION_CONFIG, VISION_MODELS_LOCAL, VISION_MODELS_CLOUD
except ImportError:
    try:
        from config import OLLAMA_BASE_URL, VISION_CONFIG, VISION_MODELS_LOCAL, VISION_MODELS_CLOUD
    except ImportError:
        OLLAMA_BASE_URL = "http://localhost:11434"
        VISION_CONFIG = {"default_model": "gemma4:31b-cloud"}
        VISION_MODELS_LOCAL = ["llama3.2-vision:latest", "llava:13b", "llava:7b"]
        VISION_MODELS_CLOUD = ["gemma4:31b-cloud", "glm-5.1:cloud"]

# Vision models indlæses fra config.py — se VISION_MODELS_LOCAL og VISION_MODELS_CLOUD
# Fallback hvis config ikke kan importeres
_VISION_MODELS_LOCAL = VISION_MODELS_LOCAL if 'VISION_MODELS_LOCAL' in dir() else [
    "llama3.2-vision:latest",
    "llava:13b",
    "llava:7b",
    "bakllava:latest",
    "moondream:latest",
]
_VISION_MODELS_CLOUD = VISION_MODELS_CLOUD if 'VISION_MODELS_CLOUD' in dir() else [
    "gemma4:31b-cloud",
    "glm-5.1:cloud",
    "kimi-k2.6:cloud",
    "qwen3.5:397b:cloud",
]


# ═══════════════════════════════════════════════════════════════
# VISION ANALYSIS PRESETS — Security-focused prompts
# ═══════════════════════════════════════════════════════════════

VISION_PRESETS = {
    "web_screenshot": {
        "name": "Web Screenshot Analysis",
        "prompt": """Analyser dette web screenshot som en security researcher.

Identificer:
1. **Login forms** — Er der autentificering? Kan den bypasses?
2. **Error messages** — Lækker de information? (stack traces, internal paths, version numbers)
3. **Exposed directories** — Er der directory listings, backup files (.bak, .old, .swp)?
4. **JavaScript** — Kommentarer, hardcoded URLs, API endpoints, tokens i source visible?
5. **CORS/headers** — Nogen obvious misconfigs baseret påhvad der vises?
6. **Interesting links** — Admin panels, debug endpoints, API docs, swagger
7. **Technology stack** — Frameworks, CMS, server based on page content

Vær specifik — nævn konkrete elementer du ser, ikke generelle antagelser.""",
    },
    "nmap_graph": {
        "name": "Nmap/Network Scan Analysis",
        "prompt": """Analyser dette netværks-scan billede (Nmap output, netværkskort, eller lignende).

Identificer:
1. **Open ports** — Hvilke porte er åbne? Hvad kører på dem?
2. **Services** — Versionsnumre der kan have CVEs?
3. **Network topology** — Hvordan er netværket struktureret?
4. **Interesting hosts** — Unusual services, management interfaces?
5. **Potential entry points** — Hvilke services ser mest angribelige ud?

Vær specifik — oversæt text fra billedet når muligt.""",
    },
    "kismet_wifi": {
        "name": "Kismet/WiFi Map Analysis",
        "prompt": """Analyser dette WiFi/kort billede fra Kismet eller lignende værktøj.

Identificer:
1. **Access points** — SSIDs,加密 type, signal styrke
2. **Client devices** — Hidden probes, deauth potential?
3. **Network names** — Default SSIDs der indikerer default credentials?
4. **Encryption** — WEP, WPA, WPA2, WPA3? Open networks?
5. **Channel overlap** — Kanal-konflikter der kan udnyttes?
6. **GPS coordinates** — Er der lokations-data synlig?

Vær specifik med det du kan aflæse fra billedet.""",
    },
    "error_page": {
        "name": "Error Page Analysis",
        "prompt": """Analyser denne error page som en security researcher.

Identificer:
1. **Information leakage** — Stack traces, internal paths, version numbers, database errors
2. **Debug mode** — Er aplikationen i debug mode? Viser den request details?
3. **Internal IPs/hostnames** — Lækker den internal infrastructure info?
4. **Framework** — Hvad er teknologien? Express, Django, Laravel, ASP.NET?
5. **Attack vectors** — Hvad kan udnyttes baseret på informationen der lekkede?
6. **Remediation** — Hvad skal fixes for at stoppe information leakage?

Nævn SPECIFIKKE details du ser i billedet.""",
    },
    "dashboard": {
        "name": "Dashboard/Admin Panel Analysis",
        "prompt": """Analyser dette dashboard/admin panel som en security researcher.

Identificer:
1. **Admin functionality** — Hvilke funktioner er tilgængelige? (user management, config, logs)
2. **Authentication** — Er der session-tokens synlige i URL? Cookie-based auth visible?
3. **IDOR potential** — Kan man se user IDs, kan man enumerere andre brugere?
4. **Sensitive data** — PII, API keys, internal URLs visible on screen?
5. **Privilege escalation** — Er der role-based access controls synlige? Kan de bypasses?
6. **Export/download** — Bulk data export funktioner der kan misbruges?

Vær specifik med hvad du ser.""",
    },
    "general": {
        "name": "General Security Analysis",
        "prompt": """Analyser dette billede fra et security perspektiv.

Kig efter:
1. Svagheder eller sårbarheder
2. Information lækage
3. Misconfigs
4. Angrebsflader
5. Alt der ser usædvanligt ud

Vær specifik med hvad du ser i billedet.""",
    },
    "ocr": {
        "name": "OCR — Text Extraction",
        "prompt": """Udtræk al tekst fra dette billede. 

Kopiér alt synligt tekst nøjagtigt som det vises. Inkluder:
- Headers og labels
- URLs, emails, telefonnumre
- Kode og kommandoer
- Error messages
- Version numbers og versions strings

Formatér output som plaintext med struktur bevaret.""",
    },
}


class VisionAnalyzer:
    """
    Analysér billeder med Ollama vision models.
    
    Features:
    - Automatisk model detektion (finder tilgængelig vision model)
    - Pre-built security analysis prompts
    - Base64 encoding af lokale billeder
    - URL support for remote billeder
    - Batch analyse af flere billeder
    """
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or OLLAMA_BASE_URL
        self._available_model = None
        self._model_checked = False
    
    def _find_vision_model(self) -> Optional[str]:
        """Find en tilgængelig vision model."""
        import requests as req
        
        if self._model_checked and self._available_model:
            return self._available_model
        
        # Tjek lokale vision models
        try:
            response = req.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                local_models = [m["name"] for m in response.json().get("models", [])]
                for model in VISION_MODELS_LOCAL:
                    # Tjek både exact match og uden :latest suffix
                    if model in local_models or model.replace(":latest", "") in local_models:
                        self._available_model = model
                        self._model_checked = True
                        return model
        except Exception:
            pass
        
        # Fallback til cloud model
        self._available_model = "glm-5.1:cloud"
        self._model_checked = True
        return self._available_model
    
    def analyze(
        self,
        image_path: str,
        prompt: str = None,
        preset: str = "general",
        model: str = None,
    ) -> Dict[str, Any]:
        """
        Analysér et billede med en vision model.
        
        Args:
            image_path: Sti til lokalt billede eller URL
            prompt: Custom prompt (overrides preset)
            preset: Pre-built prompt preset ("web_screenshot", "nmap_graph", etc.)
            model: Specifik model (auto-detect hvis None)
        
        Returns:
            Dict med analysis, model brugt, og metadata
        """
        import requests as req
        
        # Vælg model
        model = model or self._find_vision_model()
        if not model:
            return {"error": "Ingen vision model tilgængelig", "analysis": ""}
        
        # Vælg prompt
        if prompt:
            analysis_prompt = prompt
        elif preset in VISION_PRESETS:
            analysis_prompt = VISION_PRESETS[preset]["prompt"]
        else:
            analysis_prompt = VISION_PRESETS["general"]["prompt"]
        
        # Load billede
        image_path = os.path.expanduser(image_path.strip())
        
        if not os.path.exists(image_path):
            # Prøv at parse "image_path\nprompt" format
            if "\\n" in image_path:
                parts = image_path.split("\\n", 1)
                image_path = os.path.expanduser(parts[0].strip())
                if len(parts) > 1 and not prompt:
                    analysis_prompt = parts[1].strip() + "\n\n" + analysis_prompt
            
            if not os.path.exists(image_path):
                return {"error": f"Billede ikke fundet: {image_path}", "analysis": ""}
        
        # Encode billede
        try:
            with open(image_path, "rb") as f:
                file_size = os.path.getsize(image_path)
                # Max 20MB billeder
                if file_size > 20 * 1024 * 1024:
                    return {"error": f"Billede for stort: {file_size / 1024 / 1024:.1f}MB (max 20MB)", "analysis": ""}
                image_data = base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            return {"error": f"Kunne ikke læse billede: {e}", "analysis": ""}
        
        # Kør vision analyse
        is_cloud = ":cloud" in model
        
        if is_cloud:
            return self._analyze_cloud(model, image_data, analysis_prompt, image_path)
        else:
            return self._analyze_local(model, image_data, analysis_prompt, image_path)
    
    def _analyze_local(
        self, model: str, image_data: str, prompt: str, image_path: str
    ) -> Dict[str, Any]:
        """Analysér med lokal Ollama vision model."""
        import requests as req
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_data],
                }
            ],
            "stream": False,
            "keep_alive": "5m",
            "options": {
                "temperature": 0.3,
                "num_ctx": 8192,
            }
        }
        
        try:
            start = time.time()
            response = req.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120,
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("message", {}).get("content", "")
                
                return {
                    "analysis": content,
                    "model": model,
                    "image": image_path,
                    "elapsed_seconds": round(elapsed, 2),
                    "preset": "local_vision",
                    "status": "success",
                }
            else:
                return {
                    "error": f"Vision API fejl: HTTP {response.status_code}",
                    "analysis": response.text[:500],
                    "model": model,
                    "image": image_path,
                    "status": "error",
                }
        except Exception as e:
            return {
                "error": f"Vision analyse fejlede: {e}",
                "analysis": "",
                "model": model,
                "image": image_path,
                "status": "error",
            }
    
    def _analyze_cloud(
        self, model: str, image_data: str, prompt: str, image_path: str
    ) -> Dict[str, Any]:
        """Analysér med cloud model via OpenAI-kompatibel API med vision."""
        import requests as req
        import re
        
        cloud_model = model.replace(":cloud", "")
        cloud_model = re.sub(r':[\d]+[bB]$', '', cloud_model)
        
        api_key = os.environ.get("OLLAMA_API_KEY", "27be72d8f0ff4ef79db5bee0f8758b63.6SrdafFDTNf9RoGMFy_HrB_h")
        
        # OpenAI vision format med image_url
        # Cloud API bruger image_url med base64 data URL
        payload = {
            "model": cloud_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}",
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4096,
            "temperature": 0.3,
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            start = time.time()
            response = req.post(
                "https://ollama.com/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=120,
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                return {
                    "analysis": content,
                    "model": model,
                    "image": image_path,
                    "elapsed_seconds": round(elapsed, 2),
                    "preset": "cloud_vision",
                    "status": "success",
                }
            else:
                return {
                    "error": f"Cloud Vision API fejl: HTTP {response.status_code}",
                    "analysis": response.text[:500],
                    "model": model,
                    "image": image_path,
                    "status": "error",
                }
        except Exception as e:
            # Fallback til lokal model
            local_model = self._find_vision_model()
            if local_model and ":cloud" not in local_model:
                return self._analyze_local(local_model, image_data, prompt, image_path)
            return {
                "error": f"Cloud vision fejlede og ingen lokal fallback: {e}",
                "analysis": "",
                "model": model,
                "image": image_path,
                "status": "error",
            }
    
    def analyze_batch(
        self,
        image_paths: List[str],
        prompt: str = None,
        preset: str = "general",
        model: str = None,
    ) -> List[Dict[str, Any]]:
        """Analysér flere billeder i batch."""
        results = []
        for path in image_paths:
            result = self.analyze(path, prompt=prompt, preset=preset, model=model)
            results.append(result)
            time.sleep(0.5)  # Rate limiting
        return results
    
    def analyze_screenshot(
        self,
        url_or_path: str,
        model: str = None,
    ) -> Dict[str, Any]:
        """Quick web screenshot analysis med web_screenshot preset."""
        return self.analyze(url_or_path, preset="web_screenshot", model=model)
    
    def analyze_scan_result(
        self,
        image_path: str,
        scan_type: str = "nmap",
        model: str = None,
    ) -> Dict[str, Any]:
        """Analysér scan resultater (Nmap, Kismet, etc.)."""
        preset_map = {
            "nmap": "nmap_graph",
            "wifi": "kismet_wifi",
            "kismet": "kismet_wifi",
            "error": "error_page",
            "dashboard": "dashboard",
        }
        preset = preset_map.get(scan_type, "general")
        return self.analyze(image_path, preset=preset, model=model)
    
    def extract_text(
        self,
        image_path: str,
        model: str = None,
    ) -> Dict[str, Any]:
        """Extract tekst fra et billede (OCR mode)."""
        return self.analyze(image_path, preset="ocr", model=model)
    
    def list_available_models(self) -> List[str]:
        """List tilgængelige vision models."""
        import requests as req
        available = []
        
        try:
            response = req.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                local_models = [m["name"] for m in response.json().get("models", [])]
                for model in VISION_MODELS_LOCAL:
                    if model in local_models or model.replace(":latest", "") in local_models:
                        available.append(model)
        except Exception:
            pass
        
        # Cloud models er altid tilgængelige (teoretisk)
        available.extend(VISION_MODELS_CLOUD)
        
        return available


# ═══════════════════════════════════════════════════════════════
# TOOL FUNKTIONER TIL INTEGRATION MED tools.py
# ═══════════════════════════════════════════════════════════════

def vision_analyze_tool(data: str) -> str:
    """
    Analyze an image with vision model. Input: image path or JSON with image_path, preset, model.
    Presets: web_screenshot, nmap_graph, kismet_wifi, error_page, dashboard, general, ocr
    """
    import json
    
    # Prøv JSON parse
    try:
        parsed = json.loads(data)
        image_path = parsed.get("image_path", data)
        preset = parsed.get("preset", "general")
        model = parsed.get("model")
        prompt = parsed.get("prompt")
    except (json.JSONDecodeError, TypeError):
        image_path = data
        preset = "general"
        model = None
        prompt = None
    
    # Tjek for "path preset" format: "/path/to/image.png web_screenshot"
    if " " in image_path and not image_path.startswith("{"):
        parts = image_path.split(" ", 1)
        image_path = parts[0]
        preset_or_prompt = parts[1]
        if preset_or_prompt in VISION_PRESETS:
            preset = preset_or_prompt
        else:
            prompt = preset_or_prompt
    
    va = VisionAnalyzer()
    result = va.analyze(image_path, prompt=prompt, preset=preset, model=model)
    
    if result.get("status") == "success":
        lines = [
            f"[VISION] Analyse af {result.get('image', image_path)}",
            f"Model: {result.get('model', 'unknown')}",
            f"Tid: {result.get('elapsed_seconds', 0)}s",
            "",
            result.get("analysis", "[INGEN ANALYSE]"),
        ]
        return "\n".join(lines)
    else:
        return f"[VISION FEJL] {result.get('error', 'Unknown error')}"


def vision_screenshot_tool(data: str) -> str:
    """Analyze a web screenshot for security issues. Input: image path."""
    va = VisionAnalyzer()
    result = va.analyze_screenshot(data.strip())
    
    if result.get("status") == "success":
        return f"[SCREENSHOT ANALYSE] {result.get('image', data)}\nModel: {result.get('model')}\nTid: {result.get('elapsed_seconds')}s\n\n{result.get('analysis', '[INGEN ANALYSE]')}"
    return f"[VISION FEJL] {result.get('error', 'Unknown error')}"


def vision_scan_tool(data: str) -> str:
    """Analyze a scan result image (Nmap, Kismet, etc). Input: image path [nmap|wifi|error|dashboard]."""
    import json
    
    image_path = data.strip()
    scan_type = "nmap"
    
    # Parse "path type" format
    if " " in image_path:
        parts = image_path.split(" ", 1)
        image_path = parts[0]
        scan_type = parts[1]
    
    va = VisionAnalyzer()
    result = va.analyze_scan_result(image_path, scan_type=scan_type)
    
    if result.get("status") == "success":
        return f"[SCAN ANALYSE] {result.get('image')} ({scan_type})\nModel: {result.get('model')}\nTid: {result.get('elapsed_seconds')}s\n\n{result.get('analysis', '[INGEN ANALYSE]')}"
    return f"[VISION FEJL] {result.get('error', 'Unknown error')}"


def vision_ocr_tool(data: str) -> str:
    """Extract text from an image (OCR mode). Input: image path."""
    va = VisionAnalyzer()
    result = va.extract_text(data.strip())
    
    if result.get("status") == "success":
        return f"[OCR] {result.get('image')}\nModel: {result.get('model')}\nTid: {result.get('elapsed_seconds')}s\n\n{result.get('analysis', '[INGEN TEKST]')}"
    return f"[VISION FEJL] {result.get('error', 'Unknown error')}"


def vision_models_tool(query: str = "") -> str:
    """List available vision models. Input: empty."""
    import json
    va = VisionAnalyzer()
    models = va.list_available_models()
    return json.dumps({"available_vision_models": models}, indent=2)
