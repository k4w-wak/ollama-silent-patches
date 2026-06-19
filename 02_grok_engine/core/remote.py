"""Grok Remote Runtime — SSH command execution on remote machines.
Access Grok from any PC on your network via SSH.
"""
import subprocess
import json
from pathlib import Path
from datetime import datetime

SSH_CONFIG_DIR = Path.home() / ".grok" / "ssh"
SSH_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

KNOWN_HOSTS_FILE = SSH_CONFIG_DIR / "known_hosts.json"


# === PERMANENT UTF-8 ENCODING FIX ===
_UTF8_ENV = {**__import__('os').environ, 'PYTHONIOENCODING': 'utf-8', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8'}

def ssh_run(target: str) -> str:
    """Run a command on a remote machine via SSH. 
    Input: 'host command' or 'user@host command' or 'user@host -p port command'
    """
    try:
        parts = target.strip().split()
        if len(parts) < 2:
            return "[FEJL] Angiv: 'user@host command' eller 'host command'"
        
        host = parts[0]
        command = " ".join(parts[1:])
        
        # Build SSH command
        ssh_cmd = ["ssh", "-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=10"]
        
        # Check for port specification
        if "-p" in parts:
            port_idx = parts.index("-p")
            port = parts[port_idx + 1] if port_idx + 1 < len(parts) else "22"
            ssh_cmd.extend(["-p", port])
            # Remove -p and port from command
            command = " ".join([p for i, p in enumerate(parts[1:]) if i not in [port_idx - 1, port_idx]])
        
        ssh_cmd.extend([host, command])
        
        r = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=60, encoding='utf-8', errors='replace', env=_UTF8_ENV)
        output = ""
        if r.stdout:
            output += r.stdout[:3000]
        if r.stderr:
            output += f"\n[STDERR] {r.stderr[:500]}"
        return output if output else "[INGEN OUTPUT]"
    
    except subprocess.TimeoutExpired:
        return "[TIMEOUT] SSH forbindelse tog for lang tid (60s)"
    except Exception as e:
        return f"[FEJL] SSH fejlede: {str(e)[:200]}"


def ssh_copy(target: str) -> str:
    """Copy a file to/from a remote machine via SCP.
    Input: 'source destination' (fx '/local/file user@host:/remote/path' or 'user@host:/remote/file /local/path')
    """
    try:
        parts = target.strip().split()
        if len(parts) < 2:
            return "[FEJL] Angiv: 'source destination'"
        
        src = parts[0]
        dst = parts[1]
        
        r = subprocess.run(["scp", "-o", "StrictHostKeyChecking=accept-new", src, dst],
                          capture_output=True, text=True, timeout=60, encoding='utf-8', errors='replace', env=_UTF8_ENV)
        if r.returncode == 0:
            return f"✅ Fil kopieret: {src} → {dst}"
        return f"[FEJL] {r.stderr[:300]}"
    
    except subprocess.TimeoutExpired:
        return "[TIMEOUT] SCP tog for lang tid"
    except Exception as e:
        return f"[FEJL] {str(e)[:200]}"


def ssh_tunnel(target: str) -> str:
    """Create an SSH tunnel (port forwarding).
    Input: 'user@host local_port remote_port' or 'user@host -R remote_port local_port'
    """
    try:
        parts = target.strip().split()
        if len(parts) < 3:
            return "[FEJL] Angiv: 'user@host local_port remote_port'"
        
        host = parts[0]
        local_port = parts[1]
        remote_port = parts[2]
        
        # -L = local forwarding, -N = no command
        r = subprocess.run(
            ["ssh", "-N", "-L", f"{local_port}:localhost:{remote_port}", host],
            capture_output=True, text=True, timeout=15
        , encoding='utf-8', errors='replace', env=_UTF8_ENV)
        return f"[INFO] SSH tunnel oprettet: localhost:{local_port} → {host}:{remote_port}"
    
    except subprocess.TimeoutExpired:
        return "[INFO] SSH tunnel kører (timeout = normalt for tunnel)"
    except Exception as e:
        return f"[FEJL] {str(e)[:200]}"


def ssh_known_hosts() -> str:
    """List saved SSH hosts."""
    if KNOWN_HOSTS_FILE.exists():
        try:
            data = json.loads(KNOWN_HOSTS_FILE.read_text())
            hosts = data.get("hosts", [])
            if not hosts:
                return "Ingen gemte hosts. Tilføj med ssh_add_host."
            lines = ["Gemte SSH hosts:", ""]
            for h in hosts:
                lines.append(f"  {h.get('alias','?')}: {h.get('user','')}@{h.get('host','')}:{h.get('port',22)}")
                lines.append(f"    Sidst brugt: {h.get('last_used','aldrig')}")
            return "\n".join(lines)
        except:
            pass
    return "Ingen gemte hosts endnu."


def ssh_add_host(target: str) -> str:
    """Add a known SSH host. Input: 'alias user@host port' or 'alias user@host'"""
    try:
        parts = target.strip().split()
        alias = parts[0] if parts else ""
        userhost = parts[1] if len(parts) > 1 else ""
        port = parts[2] if len(parts) > 2 else "22"
        
        if "@" in userhost:
            user, host = userhost.split("@", 1)
        else:
            user, host = "", userhost
        
        # Load existing
        data = {"hosts": []}
        if KNOWN_HOSTS_FILE.exists():
            try:
                data = json.loads(KNOWN_HOSTS_FILE.read_text())
            except:
                pass
        
        # Add
        data["hosts"].append({
            "alias": alias,
            "user": user,
            "host": host,
            "port": int(port),
            "last_used": datetime.now().isoformat()
        })
        KNOWN_HOSTS_FILE.write_text(json.dumps(data, indent=2))
        
        return f"✅ Host gemt: {alias} ({user}@{host}:{port})"
    except Exception as e:
        return f"[FEJL] {str(e)[:200]}"


def grok_server(port: str = "5002") -> str:
    """Start Grok as an SSH-accessible server.
    Input: port number (default 5002)
    Creates a shell wrapper that can be started via SSH.
    """
    try:
        port_num = int(port.strip()) if port.strip() else 5002
        
        # Create the server script
        server_script = SSH_CONFIG_DIR / "grok_ssh_server.py"
        server_script.write_text(f'''#!/usr/bin/env python3
"""Grok SSH Server — Access Grok remotely via SSH."""
import sys, os
sys.path.insert(0, '{Path.home() / "Skrivebord" / "projekter" / "grok"}')
os.chdir('{Path.home() / "Skrivebord" / "projekter" / "grok"}')

from core.agent import GrokAgent

print("╔══════════════════════════════════════════════════╗")
print("║  GROK v3.3 — SSH REMOTE ACCESS                  ║")
print("║  Velkommen! Skriv din kommando til Grok.        ║")
print("║  Skriv 'quit' for at afslutte.                  ║")
print("╚══════════════════════════════════════════════════╝")
print()

agent = GrokAgent()
agent.interactive = True

while True:
    try:
        user_input = input("\\nKAWWAK@GROK> ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("Farvel! 👋")
            break
        if not user_input:
            continue
        result = agent.run(user_input)
    except (KeyboardInterrupt, EOFError):
        print("\\nFarvel! 👋")
        break
    except Exception as e:
        print(f"[FEJL] {{e}}")
''')
        
        # Create shell wrapper for easy SSH access
        shell_wrapper = SSH_CONFIG_DIR / "grok"
        shell_wrapper.write_text(f'''#!/bin/bash
# Grok SSH Remote Access
# Brug: ssh kali@<kali-ip> -t ~/.grok/ssh/grok
cd {Path.home() / "Skrivebord" / "projekter" / "grok"}
python3 {server_script}
''')
        subprocess.run(["chmod", "+x", str(shell_wrapper)], capture_output=True)
        
        return f"""✅ Grok SSH server oprettet!

For at tilgå Grok fra en anden PC:

  ssh kali@<din-kali-ip> -t ~/.grok/ssh/grok

Fra din laptop:
  ssh kali@192.168.32.3 -t ~/.grok/ssh/grok

Tips:
  - Sørg for SSH er slået til på Kali: sudo systemctl start ssh
  - Password: 0000 (din sudo password)
  - Brug -X flag for GUI: ssh -X kali@192.168.32.3 -t ~/.grok/ssh/grok
"""
    except Exception as e:
        return f"[FEJL] {str(e)[:200]}"


def enable_ssh() -> str:
    """Enable SSH server on Kali so other PCs can connect."""
    try:
        # Start SSH
        r = subprocess.run(["sudo", "systemctl", "start", "ssh"], capture_output=True, text=True, timeout=10, encoding='utf-8', errors='replace', env=_UTF8_ENV)
        if r.returncode != 0:
            # Try sshd directly
            r = subprocess.run(["sudo", "sshd"], capture_output=True, text=True, timeout=10, encoding='utf-8', errors='replace', env=_UTF8_ENV)
        
        # Enable on boot
        subprocess.run(["sudo", "systemctl", "enable", "ssh"], capture_output=True, text=True, timeout=10, encoding='utf-8', errors='replace', env=_UTF8_ENV)
        
        # Get IP
        r = subprocess.run(["hostname", "-I"], capture_output=True, text=True, timeout=5, encoding='utf-8', errors='replace', env=_UTF8_ENV)
        ip = r.stdout.strip().split()[0] if r.stdout.strip() else "?"
        
        return f"""✅ SSH server slået til!

  Din Kali IP: {ip}
  
  Forbind fra en anden PC:
    ssh kali@{ip}
  
  Start Grok remotely:
    ssh kali@{ip} -t ~/.grok/ssh/grok
  
  Fra Windows (PowerShell):
    ssh kali@{ip} -t ~/.grok/ssh/grok
  
  Fra telefon (Termux/JuiceSSH):
    ssh kali@{ip}
    ~/.grok/ssh/grok
"""
    except Exception as e:
        return f"[FEJL] {str(e)[:200]}"