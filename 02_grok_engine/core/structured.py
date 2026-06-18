#!/usr/bin/env python3
"""
Grok Structured Output Module — tvunget JSON skema for Finding-rapporter
Bruger Ollama's JSON mode til at garantere korrekt output format.
Matcher FP-filter og Finding format fra config.py.
"""

import json
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from datetime import datetime

try:
    from .models import ModelRouter
    from .config import OLLAMA_BASE_URL
except ImportError:
    from models import ModelRouter
    from config import OLLAMA_BASE_URL


# ═══════════════════════════════════════════════════════════════
# FINDING JSON SCHEMA — STRICT
# ═══════════════════════════════════════════════════════════════

FINDING_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Kort navn for fundet, f.eks. 'Exposed .git Directory' eller 'Reflected XSS on /search'"
        },
        "severity": {
            "type": "string",
            "enum": ["critical", "high", "medium", "low", "info"],
            "description": "CVSS-baseret severity. Auth-required = HIGH max. Aldrig CRITICAL for CORS alone."
        },
        "vuln_type": {
            "type": "string",
            "enum": [
                "xss", "sqli", "rce", "lfi", "rfi", "ssrf", "idor", 
                "info_disclosure", "cors_misconfig", "subdomain_takeover",
                "auth_bypass", "session_fixation", "csrf", "open_redirect",
                "xxe", "deserialization", "path_traversal", "command_injection",
                "ssrf", "broken_access_control", "jwt_vulnerability",
                "api_exposure", "dns_rebinding", "host_header_injection",
                "cache_poisoning", "race_condition", "data_leak", "other"
            ],
            "description": "Vuln type klassificering"
        },
        "target": {
            "type": "string",
            "description": "Fuld URL eller IP:port for fundet"
        },
        "endpoint": {
            "type": "string",
            "description": "Specifik endpoint/path hvor vuln findes"
        },
        "evidence": {
            "type": "string",
            "description": "Rå tool output der beviser vuln. Exact request + response."
        },
        "poc": {
            "type": "string",
            "description": "Reproducerbar PoC — curl kommando eller script"
        },
        "fp_check": {
            "type": "string",
            "enum": ["Verified", "Needs Manual", "Filtered Out"],
            "description": "False positive status. Verified = reproducerbar, Needs Manual = usikker, Filtered Out = sandsynligvis FP"
        },
        "reasoning": {
            "type": "string",
            "description": "Hvorfor dette er (eller ikke er) en reel vuln. Konkret argumentation."
        },
        "cvss_score": {
            "type": "number",
            "description": "Estimeret CVSS score (0-10). Ikke altid 9.1.",
            "minimum": 0,
            "maximum": 10
        },
        "impact": {
            "type": "string",
            "description": "Hvad kan en angriber opnå? Konkret impact beskrivelse."
        },
        "remediation": {
            "type": "string",
            "description": "Hvordan fixes det? Konkret remediation råd."
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Tags for kategorisering"
        },
        "timestamp": {
            "type": "string",
            "description": "ISO timestamp for hvornår fundet blev opdaget"
        }
    },
    "required": ["name", "severity", "vuln_type", "target", "evidence", "fp_check", "reasoning"]
}

# Simplified recon report schema
RECON_REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "target": {"type": "string"},
        "phase": {
            "type": "string",
            "enum": ["scope", "asset_discovery", "port_scan", "content_discovery", "tech_fingerprint", "low_hanging_fruit", "logging"]
        },
        "subdomains": {"type": "array", "items": {"type": "string"}},
        "live_hosts": {"type": "array", "items": {"type": "string"}},
        "open_ports": {"type": "array", "items": {"type": "object", "properties": {"host": {"type": "string"}, "port": {"type": "integer"}, "service": {"type": "string"}, "version": {"type": "string"}}}},
        "technologies": {"type": "array", "items": {"type": "object", "properties": {"name": {"type": "string"}, "version": {"type": "string"}, "url": {"type": "string"}}}},
        "findings": {"type": "array", "items": FINDING_SCHEMA},
        "summary": {"type": "string"},
        "recommendations": {"type": "array", "items": {"type": "string"}},
        "timestamp": {"type": "string"}
    },
    "required": ["target", "phase", "summary"]
}

# Mission result schema
MISSION_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "mission": {"type": "string"},
        "target": {"type": "string"},
        "status": {"type": "string", "enum": ["completed", "partial", "failed"]},
        "tools_used": {"type": "array", "items": {"type": "string"}},
        "findings": {"type": "array", "items": FINDING_SCHEMA},
        "duration_seconds": {"type": "number"},
        "model": {"type": "string"},
        "summary": {"type": "string"},
        "errors": {"type": "array", "items": {"type": "string"}},
        "timestamp": {"type": "string"}
    },
    "required": ["mission", "target", "status", "summary"]
}


# ═══════════════════════════════════════════════════════════════
# STRUCTURED OUTPUT CLASS
# ═══════════════════════════════════════════════════════════════

class StructuredOutput:
    """
    Tvunget JSON output via Ollama's format parameter.
    
    Usage:
        so = StructuredOutput(router)
        finding = so.generate_finding(
            evidence="curl output here...",
            target="https://example.com",
            vuln_type="info_disclosure"
        )
    """
    
    def __init__(self, router: ModelRouter = None):
        self.router = router or ModelRouter()
    
    def _generate_structured(
        self,
        prompt: str,
        schema: dict,
        model: str = None,
        max_retries: int = 2,
    ) -> Optional[dict]:
        """
        Generer struktureret JSON output via Ollama JSON mode.
        
        Args:
            prompt: Bruger prompt der beskriver hvad der skal analyseres
            schema: JSON schema der definerer output formatet
            model: Model navn (default: glm-5.1:cloud)
            max_retries: Antal forsøg hvis JSON parsing fejler
        
        Returns:
            Parsed dict eller None hvis alle forsøg fejler
        """
        model = model or "glm-5.1:cloud"
        import requests as req
        
        messages = [
            {"role": "system", "content": """Du er en security findings analyst. Du SKAL output valid JSON der matcher det angivne skema.
REGEL:
- Output KUN valid JSON — ingen markdown, ingen kommentarer, ingen forklaring
- Alle required felter SKAL være udfyldt
- severity SKAL være realistic — auth-required = HIGH max, CORS alone = LOW/info
- fp_check SKAL være ærlig — bedre Needs Manual end falsk Verified
- evidence SKAL indeholde konkret tool output, ikke vag beskrivelse"""},
            {"role": "user", "content": prompt}
        ]
        
        for attempt in range(max_retries):
            try:
                # Ollama local JSON mode
                if not self.router.is_cloud_model(model):
                    payload = {
                        "model": model,
                        "messages": messages,
                        "stream": False,
                        "format": schema,
                        "keep_alive": "5m",
                        "options": {
                            "temperature": 0.3,  # Lav temperatur for konsistent output
                            "num_ctx": 32768,
                        }
                    }
                    
                    response = req.post(
                        f"{self.router.OLLAMA_BASE_URL if hasattr(self.router, 'OLLAMA_BASE_URL') else OLLAMA_BASE_URL}/api/chat",
                        json=payload,
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        content = data.get("message", {}).get("content", "")
                        return self._parse_json(content)
                
                # Cloud model — /v1/chat/completions med response_format
                else:
                    cloud_model = model.replace(":cloud", "")
                    import re
                    cloud_model = re.sub(r':[\d]+[bB]$', '', cloud_model)
                    
                    api_key = self.router.OLLAMA_CLOUD_KEY
                    payload = {
                        "model": cloud_model,
                        "messages": messages,
                        "max_tokens": 8192,
                        "temperature": 0.3,
                        "response_format": {"type": "json_object"},
                    }
                    
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    }
                    
                    response = req.post(
                        "https://ollama.com/v1/chat/completions",
                        json=payload,
                        headers=headers,
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        return self._parse_json(content)
                
            except Exception as e:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)
                    continue
                return None
        
        return None
    
    def _parse_json(self, content: str) -> Optional[dict]:
        """Parse JSON fra model output — håndterer markdown fences etc."""
        if not content:
            return None
        
        # Prøv direkte JSON parse
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Prøv at extracte JSON fra markdown fences
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass
        
        # Prøv at finde første { ... } block
        brace_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None
    
    def generate_finding(
        self,
        evidence: str,
        target: str = "",
        vuln_type: str = "",
        context: str = "",
        model: str = None,
    ) -> Optional[dict]:
        """
        Generer et struktureret Finding ud fra rå evidence.
        
        Args:
            evidence: Rå tool output (curl, nmap, ffuf, etc.)
            target: Target domæne/IP
            vuln_type: Hint om vuln type
            context: Ekstra kontekst (hvilken recon fase, etc.)
            model: Model navn
        
        Returns:
            Finding dict eller None
        """
        prompt = f"""Analyser følgende evidence og opret et struktureret Finding.

Target: {target}
Vuln type hint: {vuln_type}
Kontekst: {context}

Evidence:
{evidence[:4000]}

VIGTIGT:
- Vær ærlig om severity — bedre honest DOWNGRADED HIGH end inflated CRITICAL
- Auth required = HIGH max, never CRITICAL
- CORS alone is NOT a vulnerability
- fp_check SKAL være ærlig: Verified kun hvis reproducerbar med konkret PoC
- Evidence SKAL indeholde konkret request/response, ikke vag beskrivelse"""

        result = self._generate_structured(prompt, FINDING_SCHEMA, model)
        
        if result:
            # Valider og tilføj defaults
            result.setdefault("target", target)
            result.setdefault("vuln_type", vuln_type or "other")
            result.setdefault("timestamp", datetime.now().isoformat())
            result.setdefault("tags", [vuln_type] if vuln_type else [])
            
            # FP-filter check
            result = self._fp_filter_check(result)
        
        return result
    
    def generate_recon_report(
        self,
        target: str,
        phase: str,
        raw_output: str,
        model: str = None,
    ) -> Optional[dict]:
        """
        Generer et struktureret recon report ud fra rå tool output.
        """
        prompt = f"""Opret et struktureret recon report for følgende data.

Target: {target}
Fase: {phase}

Rå output:
{raw_output[:6000]}

Analyser output og udtræk subdomains, live hosts, open ports, technologies, og eventuelle findings."""

        result = self._generate_structured(prompt, RECON_REPORT_SCHEMA, model)
        
        if result:
            result.setdefault("target", target)
            result.setdefault("phase", phase)
            result.setdefault("timestamp", datetime.now().isoformat())
        
        return result
    
    def _fp_filter_check(self, finding: dict) -> dict:
        """
        Kør FP-filter checklist på et finding.
        Tilføjer fp_validation resultater.
        """
        checks = {
            "concrete claim": bool(finding.get("name") and finding.get("endpoint") or finding.get("target")),
            "has_poc": bool(finding.get("poc") or finding.get("evidence")),
            "evidence_proves_vuln": bool(finding.get("evidence") and len(finding.get("evidence", "")) > 20),
            "reasonable_severity": finding.get("severity", "").lower() in ["critical", "high", "medium", "low", "info"],
            "reproducible": finding.get("fp_check") == "Verified",
        }
        
        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        
        finding["fp_validation"] = {
            "checks": checks,
            "passed": passed,
            "total": total,
            "status": "PASS" if passed >= 4 else "NEEDS_REVIEW" if passed >= 2 else "FAIL",
        }
        
        # Auto-downgrade hvis for få checks passerer
        if passed < 3 and finding.get("severity") in ["critical", "high"]:
            finding["severity"] = "medium"
            finding["fp_validation"]["auto_downgraded"] = True
            finding["fp_validation"]["original_severity"] = finding.get("severity", "medium")
        
        return finding
    
    def format_finding_markdown(self, finding: dict) -> str:
        """Format et finding dict som markdown (matching config Finding format)."""
        lines = [
            f"## Finding: {finding.get('name', 'Unknown')}",
            f"- **Severity:** {finding.get('severity', 'N/A')} (CVSS: {finding.get('cvss_score', 'N/A')})",
            f"- **Type:** {finding.get('vuln_type', 'N/A')}",
            f"- **Target:** {finding.get('target', 'N/A')}",
            f"- **Endpoint:** {finding.get('endpoint', 'N/A')}",
            f"- **Evidence:**",
            f"```",
            f"{finding.get('evidence', 'N/A')[:1000]}",
            f"```",
            f"- **PoC:** `{finding.get('poc', 'N/A')}`",
            f"- **FP Check:** {finding.get('fp_check', 'Needs Manual')}",
            f"- **Reasoning:** {finding.get('reasoning', 'N/A')}",
            f"- **Impact:** {finding.get('impact', 'N/A')}",
            f"- **Remediation:** {finding.get('remediation', 'N/A')}",
        ]
        
        # Tilføj FP validation hvis tilgængelig
        fp_val = finding.get("fp_validation", {})
        if fp_val:
            lines.append(f"- **FP Validation:** {fp_val.get('status', 'N/A')} ({fp_val.get('passed', 0)}/{fp_val.get('total', 0)} checks passed)")
            if fp_val.get("auto_downgraded"):
                lines.append(f"  - ⚠️ Auto-downgraded from {fp_val.get('original_severity', '?')} to medium")
        
        lines.append(f"- **Tags:** {', '.join(finding.get('tags', []))}")
        lines.append(f"- **Timestamp:** {finding.get('timestamp', 'N/A')}")
        
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# TOOL FUNKTIONER TIL INTEGRATION MED tools.py
# ═══════════════════════════════════════════════════════════════

def structured_finding_tool(data: str) -> str:
    """
    Generate a structured vulnerability finding from raw evidence.
    Input: evidence text or JSON with evidence, target, vuln_type, context.
    Enforces Finding format with FP-filter validation.
    """
    import json
    
    try:
        parsed = json.loads(data)
        evidence = parsed.get("evidence", data)
        target = parsed.get("target", "")
        vuln_type = parsed.get("vuln_type", "")
        context = parsed.get("context", "")
        model = parsed.get("model", "glm-5.1:cloud")
    except (json.JSONDecodeError, TypeError):
        evidence = data
        target = ""
        vuln_type = ""
        context = ""
        model = "glm-5.1:cloud"
    
    so = StructuredOutput()
    finding = so.generate_finding(
        evidence=evidence,
        target=target,
        vuln_type=vuln_type,
        context=context,
        model=model,
    )
    
    if finding:
        md = so.format_finding_markdown(finding)
        return f"{md}\n\n---\n[RAW JSON]\n{json.dumps(finding, indent=2, ensure_ascii=False)}"
    else:
        return "[FEJL] Kunne ikke generere struktureret finding. Prøv med mere konkret evidence."


def structured_recon_tool(data: str) -> str:
    """
    Generate a structured recon report from raw scan output.
    Input: JSON with target, phase, raw_output, model (optional).
    """
    import json
    
    try:
        parsed = json.loads(data)
        target = parsed.get("target", "")
        phase = parsed.get("phase", "unknown")
        raw_output = parsed.get("raw_output", data)
        model = parsed.get("model", "glm-5.1:cloud")
    except (json.JSONDecodeError, TypeError):
        target = ""
        phase = "unknown"
        raw_output = data
        model = "glm-5.1:cloud"
    
    so = StructuredOutput()
    report = so.generate_recon_report(
        target=target,
        phase=phase,
        raw_output=raw_output,
        model=model,
    )
    
    if report:
        return json.dumps(report, indent=2, ensure_ascii=False)
    else:
        return "[FEJL] Kunne ikke generere struktureret recon report."


def structured_finding_from_text_tool(data: str) -> str:
    """
    Parse unstructured vulnerability text into structured Finding format.
    Input: raw text description of a finding.
    """
    so = StructuredOutput()
    finding = so.generate_finding(
        evidence=data,
        target="",
        vuln_type="",
        context="Ustruktureret fund — genkendes fra tekst",
    )
    
    if finding:
        md = so.format_finding_markdown(finding)
        import json
        return f"{md}\n\n---\n[RAW JSON]\n{json.dumps(finding, indent=2, ensure_ascii=False)}"
    else:
        # Fallback: returner formatted text med manuelle felter
        return f"""## Finding: [MANUAL ANALYSIS NEEDED]
- **Severity:** Needs Manual Review
- **Type:** other
- **Evidence:**
```
{data[:2000]}
```
- **FP Check:** Needs Manual
- **Reasoning:** Struktureret analyse fejlede — manuel review påkrævet."""
