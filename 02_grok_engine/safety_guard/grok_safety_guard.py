#!/usr/bin/env python3
"""
🔥 GROK SAFETY GUARD — MISSION MODE 🔥
========================================
Alt-i-én sikkerhedsmonitor der overvåger:
- IP-trusler (port scans, angreb)
- Netværksaktivitet (mystiske forbindelser)
- Filændringer (modificerede/systemfiler)
- Processer (skjulte, suspekte)
- System-sundhed (CPU, RAM, disk)
- USB/eksterne enheder
- Firewall-status
- WiFi-sikkerhed
"""

import os
import sys
import json
import time
import socket
import subprocess
import hashlib
import platform
from datetime import datetime
from pathlib import Path

# === KONFIGURATION ===
ALERT_DIR = os.path.expanduser("~/02_grok_engine/safety_guard/alerts")
LOG_DIR = os.path.expanduser("~/02_grok_engine/safety_guard/logs")
SNAPSHOT_DIR = os.path.expanduser("~/02_grok_engine/safety_guard/snapshots")
ALERT_LOG = os.path.join(LOG_DIR, "alerts.log")
THREAT_LOG = os.path.join(LOG_DIR, "threats.log")

# Opret mapper
for d in [ALERT_DIR, LOG_DIR, SNAPSHOT_DIR]:
    os.makedirs(d, exist_ok=True)

# Farlige porte der overvåges
DANGEROUS_PORTS = [
    22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995,
    1433, 1521, 3306, 3389, 5432, 5900, 5985, 5986, 6379, 8080,
    8443, 8888, 9090, 27017
]

# Mistænkelige procesnavne
SUSPICIOUS_PROCESSES = [
    "ncat", "nc", "netcat", "nc.openbsd", "nmap", "masscan",
    "hydra", "medusa", "john", "hashcat", "aircrack",
    "ettercap", "bettercap", "wireshark", "tcpdump", "tshark",
    "responder", "crackmapexec", "mimikatz", "mimipenguin",
    "keylogger", "rootkit", "backdoor", "reverse", "shell",
    "cryptominer", "xmrig", "minerd", "cpuminer"
]

# Vigtige filer der overvåges for ændringer
CRITICAL_FILES = [
    "/etc/passwd", "/etc/shadow", "/etc/hosts", "/etc/resolv.conf",
    "/etc/ssh/sshd_config", "/etc/crontab", "/etc/sudoers",
    "/etc/firefox/syspref.js", "/etc/proxychains.conf",
    os.path.expanduser("~/.ssh/authorized_keys"),
    os.path.expanduser("~/.bashrc"),
    os.path.expanduser("~/.bash_history"),
    os.path.expanduser("~/.ssh/config"),
]

# Farlige udgående IP-mønstre (Tor, kendte C2, etc)
SUSPICIOUS_IP_RANGES = [
    "10.0.0.", "192.168.", "172.16.", "172.17.", "172.18.",
    "172.19.", "172.20.", "172.21.", "172.22.", "172.23.",
    "172.24.", "172.25.", "172.26.", "172.27.", "172.28.",
    "172.29.", "172.30.", "172.31.",
]

# ============================================================
# HJÆLPEFUNKTIONER
# ============================================================

def log_alert(level, category, message):
    """Log en alarm med niveau og kategori"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_line = f"[{timestamp}] [{level}] [{category}] {message}\n"
    
    with open(ALERT_LOG, "a") as f:
        f.write(alert_line)
    
    if level in ["CRITICAL", "HIGH"]:
        with open(THREAT_LOG, "a") as f:
            f.write(alert_line)
        # Skriv separat alert-fil
        alert_file = os.path.join(ALERT_DIR, f"{category}_{int(time.time())}.json")
        alert_data = {
            "timestamp": timestamp,
            "level": level,
            "category": category,
            "message": message,
            "hostname": socket.gethostname(),
            "user": os.environ.get("USER", "unknown")
        }
        with open(alert_file, "w") as f:
            json.dump(alert_data, f, indent=2)
    
    # Console output med farver
    colors = {"CRITICAL": "\033[91m", "HIGH": "\033[93m", "MEDIUM": "\033[96m", "LOW": "\033[92m", "INFO": "\033[97m"}
    color = colors.get(level, "\033[97m")
    reset = "\033[0m"
    print(f"{color}{'='*60}{reset}")
    print(f"{color}🚨 [{level}] {category}: {message}{reset}")
    print(f"{color}{'='*60}{reset}")
    return alert_line

def run_cmd(cmd):
    """Kør shell-kommando og returner output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except Exception as e:
        return f"ERROR: {e}"

def hash_file(filepath):
    """Beregn SHA256 hash af en fil"""
    try:
        if not os.path.exists(filepath):
            return "MISSING"
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except:
        return "ERROR"

# ============================================================
# MONITORERINGSMODULER
# ============================================================

class NetworkMonitor:
    """Overvåg netværksforbindelser og port-aktivitet"""
    
    def check_listening_ports(self):
        """Find alle lyttende porte"""
        output = run_cmd("ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null")
        suspicious = []
        for line in output.split("\n")[1:]:
            for port in DANGEROUS_PORTS:
                if f":{port}" in line:
                    suspicious.append(line.strip())
                    break
        if suspicious:
            log_alert("HIGH", "NETWORK", f"Mistenkelige lyttende porte fundet: {len(suspicious)} stk")
            for s in suspicious:
                log_alert("HIGH", "NETWORK_PORT", s)
        else:
            log_alert("INFO", "NETWORK", "Ingen mistænkelige lyttende porte")
        return suspicious
    
    def check_established_connections(self):
        """Find alle etablerede forbindelser"""
        output = run_cmd("ss -tnp state established 2>/dev/null || netstat -tnp 2>/dev/null | grep ESTABLISHED")
        foreign_ips = set()
        for line in output.split("\n"):
            parts = line.strip().split()
            if len(parts) >= 5:
                addr = parts[4] if "ss" in run_cmd("which ss") else parts[4]
                if ":" in addr and addr.count(":") == 1:
                    ip = addr.split(":")[0]
                    if ip not in ["127.0.0.1", "0.0.0.0"]:
                        foreign_ips.add(ip)
        
        if foreign_ips:
            log_alert("MEDIUM", "NETWORK", f"Aktive forbindelser til {len(foreign_ips)} eksterne IP'er")
            for ip in list(foreign_ips)[:10]:
                log_alert("LOW", "CONNECTION", f"Forbundet til: {ip}")
        return foreign_ips
    
    def check_dns_queries(self):
        """Tjek mistænkelige DNS-forespørgsler"""
        output = run_cmd("cat /etc/resolv.conf 2>/dev/null")
        if "8.8.8.8" in output or "1.1.1.1" in output:
            log_alert("LOW", "DNS", "Bruger kendte sikre DNS-servere")
        else:
            log_alert("MEDIUM", "DNS", f"DNS-konfiguration kan være ændret: {output[:200]}")
    
    def check_arp_table(self):
        """Tjek ARP-tabellen for MITM"""
        output = run_cmd("arp -an 2>/dev/null || ip neigh show 2>/dev/null")
        macs = []
        for line in output.split("\n"):
            if "lladdr" in line or "(" in line:
                macs.append(line.strip())
        if len(macs) > 10:
            log_alert("MEDIUM", "ARP", f"Mange ARP-entries ({len(macs)}), muligt ARP spoofing")
        else:
            log_alert("INFO", "ARP", f"{len(macs)} ARP-entries fundet")

class ProcessMonitor:
    """Overvåg kørende processer for trusler"""
    
    def check_suspicious_processes(self):
        """Find mistænkelige processer"""
        output = run_cmd("ps aux")
        found = []
        for line in output.split("\n"):
            for proc in SUSPICIOUS_PROCESSES:
                if proc in line.lower():
                    # Undgå at alarmere om os selv
                    if "safety_guard" in line or "grok" in line.lower():
                        continue
                    found.append(line.strip())
                    break
        
        if found:
            for f in found:
                log_alert("CRITICAL", "PROCESS", f"Mistenkelig proces fundet: {f[:150]}")
        else:
            log_alert("INFO", "PROCESS", "Ingen mistænkelige processer fundet")
        return found
    
    def check_reverse_shells(self):
        """Søg efter reverse shell-indikatorer"""
        output = run_cmd("ps aux | grep -iE '/dev/tcp|nc.*-e|bash.*-i|python.*socket|perl.*socket|socat|pwncat' | grep -v grep")
        if output:
            log_alert("CRITICAL", "REVERSE_SHELL", f"Mulig reverse shell detekteret: {output[:300]}")
        else:
            log_alert("INFO", "REVERSE_SHELL", "Ingen reverse shells fundet")
    
    def check_crypto_miners(self):
        """Søg efter cryptominers"""
        output = run_cmd("ps aux | grep -iE 'xmrig|minerd|cpuminer|cryptonight|stratum' | grep -v grep")
        if output:
            log_alert("CRITICAL", "CRYPTOMINER", f"Cryptominer fundet: {output[:300]}")
        else:
            log_alert("INFO", "CRYPTOMINER", "Ingen cryptominers fundet")

class FileMonitor:
    """Overvåg filer for uautoriserede ændringer"""
    
    def __init__(self):
        self.baseline_file = os.path.join(SNAPSHOT_DIR, "file_baseline.json")
        self.baseline = self._load_baseline()
    
    def _load_baseline(self):
        if os.path.exists(self.baseline_file):
            with open(self.baseline_file, "r") as f:
                return json.load(f)
        return {}
    
    def _save_baseline(self):
        with open(self.baseline_file, "w") as f:
            json.dump(self.baseline, f, indent=2)
    
    def create_baseline(self):
        """Opret baseline-hash for alle kritiske filer"""
        log_alert("INFO", "FILE_BASELINE", "Opretter fil-baseline...")
        for filepath in CRITICAL_FILES:
            h = hash_file(filepath)
            self.baseline[filepath] = {
                "hash": h,
                "mtime": str(os.path.getmtime(filepath)) if os.path.exists(filepath) else "MISSING",
                "size": os.path.getsize(filepath) if os.path.exists(filepath) else 0
            }
        self._save_baseline()
        log_alert("INFO", "FILE_BASELINE", f"Baseline oprettet for {len(self.baseline)} filer")
    
    def check_file_changes(self):
        """Tjek om kritiske filer er ændret"""
        changes = []
        for filepath in CRITICAL_FILES:
            current_hash = hash_file(filepath)
            if filepath in self.baseline:
                if self.baseline[filepath]["hash"] != current_hash:
                    log_alert("HIGH", "FILE_CHANGE", f"ÆNDRET: {filepath}")
                    changes.append(filepath)
                    # Opdater baseline
                    self.baseline[filepath]["hash"] = current_hash
            else:
                log_alert("MEDIUM", "FILE_NEW", f"Ny fil i overvågning: {filepath}")
                self.baseline[filepath] = {"hash": current_hash}
        
        if not changes:
            log_alert("INFO", "FILE_CHANGE", "Ingen uautoriserede filændringer")
        self._save_baseline()
        return changes
    
    def check_ssh_keys(self):
        """Tjek for uautoriserede SSH-nøgler"""
        ssh_dir = os.path.expanduser("~/.ssh")
        auth_keys = os.path.join(ssh_dir, "authorized_keys")
        if os.path.exists(auth_keys):
            with open(auth_keys, "r") as f:
                keys = f.readlines()
            if len(keys) > 5:
                log_alert("MEDIUM", "SSH_KEYS", f"{len(keys)} SSH-nøgler i authorized_keys — tjek for uautoriserede!")
            else:
                log_alert("INFO", "SSH_KEYS", f"{len(keys)} SSH-nøgler fundet")
    
    def check_hidden_files(self):
        """Find nyligt oprettede skjulte filer i home"""
        output = run_cmd("find ~ -name '.*' -mtime -1 -type f 2>/dev/null | head -20")
        if output:
            log_alert("MEDIUM", "HIDDEN_FILES", f"Nye skjulte filer: {output[:300]}")

class SystemMonitor:
    """Overvåg system-sundhed og sikkerhed"""
    
    def check_failed_logins(self):
        """Tjek for mislykkede login-forsøg"""
        output = run_cmd("lastb 2>/dev/null | head -20 || journalctl -u sshd --since '1 hour ago' 2>/dev/null | grep -i failed | head -20")
        if output and len(output) > 10:
            lines = output.split("\n")
            if len(lines) > 5:
                log_alert("HIGH", "BRUTE_FORCE", f"Mange mislykkede logins ({len(lines)}), muligt brute force!")
            else:
                log_alert("LOW", "LOGIN_ATTEMPT", f"{len(lines)} mislykkede login-forsøg")
        else:
            log_alert("INFO", "LOGIN_ATTEMPT", "Ingen bemærkelsesværdige mislykkede logins")
    
    def check_sudo_usage(self):
        """Tjek for sudo-aktivitet"""
        output = run_cmd("journalctl -t sudo --since '1 hour ago' 2>/dev/null || grep -i sudo /var/log/auth.log 2>/dev/null | tail -10")
        if output:
            log_alert("LOW", "SUDO", f"Sudo-aktivitet fundet: {output[:200]}")
    
    def check_disk_usage(self):
        """Tjek diskforbrug"""
        output = run_cmd("df -h / | tail -1")
        if output:
            parts = output.split()
            if len(parts) >= 5:
                use_pct = parts[4].replace("%", "")
                if int(use_pct) > 90:
                    log_alert("CRITICAL", "DISK", f"Disk er {use_pct}% fuld — KRITISK!")
                elif int(use_pct) > 80:
                    log_alert("MEDIUM", "DISK", f"Disk er {use_pct}% fuld")
                else:
                    log_alert("INFO", "DISK", f"Disk-forbrug: {use_pct}%")
    
    def check_memory(self):
        """Tjek hukommelsesforbrug"""
        output = run_cmd("free -m | grep Mem")
        if output:
            parts = output.split()
            if len(parts) >= 3:
                total = int(parts[1])
                used = int(parts[2])
                pct = (used / total) * 100
                if pct > 90:
                    log_alert("HIGH", "MEMORY", f"Hukommelse {pct:.0f}% brugt — muligt minne-lækage!")
                else:
                    log_alert("INFO", "MEMORY", f"Hukommelse: {pct:.0f}% brugt")
    
    def check_usb_devices(self):
        """Tjek for USB-enheder"""
        output = run_cmd("lsusb 2>/dev/null || ls /dev/disk/by-id/ 2>/dev/null")
        if output:
            log_alert("LOW", "USB", f"USB-enheder: {output[:200]}")

class FirewallMonitor:
    """Overvåg firewall-regler"""
    
    def check_iptables(self):
        """Tjek iptables-regler"""
        output = run_cmd("iptables -L -n 2>/dev/null || echo 'No iptables access'")
        if "No iptables access" in output:
            log_alert("LOW", "FIREWALL", "Kan ikke læse iptables (kræver sudo)")
        else:
            # Tjek om der er DROP/REJECT regler
            drop_count = output.count("DROP") + output.count("REJECT")
            accept_count = output.count("ACCEPT")
            log_alert("INFO", "FIREWALL", f"Iptables: {accept_count} ACCEPT, {drop_count} DROP/REJECT regler")
    
    def check_open_ports_quick(self):
        """Hurtig tjek af åbne porte"""
        output = run_cmd("ss -tlnp 2>/dev/null | grep LISTEN | wc -l")
        port_count = int(output) if output.isdigit() else 0
        if port_count > 20:
            log_alert("HIGH", "PORTS", f"{port_count} åbne porte — usædvanligt mange!")
        elif port_count > 10:
            log_alert("MEDIUM", "PORTS", f"{port_count} åbne porte")
        else:
            log_alert("INFO", "PORTS", f"{port_count} åbne porte")

class ExternalThreatMonitor:
    """Overvåg eksterne trusler mod din IP"""
    
    def __init__(self, public_ip):
        self.public_ip = public_ip
    
    def check_public_ip(self):
        """Verificer at din offentlige IP ikke er ændret"""
        current_ip = run_cmd("curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null")
        if current_ip and current_ip != self.public_ip:
            log_alert("CRITICAL", "IP_CHANGE", f"OFFENTLIG IP ÆNDRING! Gammel: {self.public_ip}, Ny: {current_ip}")
        else:
            log_alert("INFO", "IP", f"Offentlig IP verificeret: {current_ip}")
    
    def check_incoming_connections(self):
        """Tjek indgående forbindelser"""
        output = run_cmd("ss -tnp state established | grep -v '127.0.0.1' | wc -l")
        count = int(output) if output.isdigit() else 0
        log_alert("INFO", "INCOMING", f"{count} aktive indgående forbindelser")

# ============================================================
# HOVEDMÅL — KØR ALLE CHECKS
# ============================================================

def run_full_scan(public_ip="<REDACTED_IP>"):
    """Kør komplet sikkerhedsscanning"""
    print("\n" + "="*60)
    print("🔥 GROK SAFETY GUARD — FULL SCAN 🔥")
    print(f"   Tidspunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   IP: {public_ip}")
    print(f"   Host: {socket.gethostname()}")
    print("="*60 + "\n")
    
    findings = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    
    # 1. Netværk
    print("\n📡 Netværksovervågning...")
    net = NetworkMonitor()
    net.check_listening_ports()
    net.check_established_connections()
    net.check_dns_queries()
    net.check_arp_table()
    
    # 2. Processer
    print("\n⚙️ Procesovervågning...")
    proc = ProcessMonitor()
    proc.check_suspicious_processes()
    proc.check_reverse_shells()
    proc.check_crypto_miners()
    
    # 3. Filer
    print("\n📁 Filovervågning...")
    fm = FileMonitor()
    if not os.path.exists(os.path.join(SNAPSHOT_DIR, "file_baseline.json")):
        fm.create_baseline()
    fm.check_file_changes()
    fm.check_ssh_keys()
    fm.check_hidden_files()
    
    # 4. System
    print("\n🖥️ Systemovervågning...")
    sys_mon = SystemMonitor()
    sys_mon.check_failed_logins()
    sys_mon.check_sudo_usage()
    sys_mon.check_disk_usage()
    sys_mon.check_memory()
    sys_mon.check_usb_devices()
    
    # 5. Firewall
    print("\n🧱 Firewall-overvågning...")
    fw = FirewallMonitor()
    fw.check_iptables()
    fw.check_open_ports_quick()
    
    # 6. Eksterne trusler
    print("\n🌐 Ekstern trussels-overvågning...")
    ext = ExternalThreatMonitor(public_ip)
    ext.check_public_ip()
    ext.check_incoming_connections()
    
    # Opsummering
    print("\n" + "="*60)
    print("📊 SCAN OPSUMMERING")
    print("="*60)
    
    # Tæl alerts
    if os.path.exists(ALERT_LOG):
        with open(ALERT_LOG, "r") as f:
            lines = f.readlines()
        for line in lines:
            if "[CRITICAL]" in line: findings["critical"] += 1
            elif "[HIGH]" in line: findings["high"] += 1
            elif "[MEDIUM]" in line: findings["medium"] += 1
            elif "[LOW]" in line: findings["low"] += 1
            elif "[INFO]" in line: findings["info"] += 1
    
    total_threats = findings["critical"] + findings["high"] + findings["medium"]
    print(f"\n  🔴 CRITICAL: {findings['critical']}")
    print(f"  🟠 HIGH:     {findings['high']}")
    print(f"  🟡 MEDIUM:   {findings['medium']}")
    print(f"  🔵 LOW:      {findings['low']}")
    print(f"  ⚪ INFO:     {findings['info']}")
    print(f"\n  ⚡ SAMLEDE TRUSLER: {total_threats}")
    
    if total_threats > 0:
        print(f"\n  🚨 ALARM — {total_threats} trusler detekteret!")
    else:
        print("\n  ✅ System ser rent ud — ingen trusler!")
    
    print("="*60)
    
    return findings

def quick_check():
    """Hurtig tjek — kun de vigtigste"""
    print(f"\n⚡ GROK SAFETY GUARD — Quick Check [{datetime.now().strftime('%H:%M:%S')}]\n")
    
    proc = ProcessMonitor()
    proc.check_suspicious_processes()
    proc.check_reverse_shells()
    
    fw = FirewallMonitor()
    fw.check_open_ports_quick()
    
    net = NetworkMonitor()
    net.check_listening_ports()
    
    print("✅ Quick check færdig\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_check()
    elif len(sys.argv) > 1 and sys.argv[1] == "baseline":
        fm = FileMonitor()
        fm.create_baseline()
    elif len(sys.argv) > 1 and sys.argv[1] == "monitor":
        # Kontinuerlig overvågning
        print("🔥 GROK SAFETY GUARD — KONTINuerLIG OVERVÅGNING")
        print("   Tryk Ctrl+C for at stoppe\n")
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        try:
            while True:
                run_full_scan()
                print(f"\n⏰ Næste scan om {interval} sekunder...\n")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n🛑 Overvågning stoppet")
    else:
        run_full_scan()