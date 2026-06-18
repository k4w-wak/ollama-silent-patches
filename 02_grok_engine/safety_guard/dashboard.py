#!/usr/bin/env python3
"""
🔥 GROK SAFETY GUARD — STATUS DASHBOARD 🔥
Viser aktuel sikkerhedsstatus på én skærm
"""

import os
import json
import subprocess
from datetime import datetime

GUARD_DIR = os.path.expanduser("~/02_grok_engine/safety_guard")
LOG_DIR = os.path.join(GUARD_DIR, "logs")
ALERT_DIR = os.path.join(GUARD_DIR, "alerts")

def run(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10).stdout.strip()
    except:
        return "N/A"

def count_alerts():
    """Tæl alerts i dag"""
    alert_log = os.path.join(LOG_DIR, "alerts.log")
    today = datetime.now().strftime("%Y-%m-%d")
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    if os.path.exists(alert_log):
        with open(alert_log) as f:
            for line in f:
                if today in line:
                    for level in counts:
                        if f"[{level}]" in line:
                            counts[level] += 1
    return counts

def get_last_alerts(n=5):
    """Hent de seneste alerts"""
    alert_log = os.path.join(LOG_DIR, "alerts.log")
    alerts = []
    if os.path.exists(alert_log):
        with open(alert_log) as f:
            lines = f.readlines()
        alerts = [l.strip() for l in lines[-n:]]
    return alerts

def dashboard():
    os.system('clear')
    
    print("\n" + "="*70)
    print("🔥 GROK SAFETY GUARD — DASHBOARD 🔥")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | IP: <REDACTED_IP> | admin_user")
    print("="*70)
    
    # System status
    print("\n📊 SYSTEM STATUS")
    print("-"*40)
    print(f"  Host:     {run('hostname')}")
    print(f"  Uptime:   {run('uptime -p 2>/dev/null || uptime')}")
    print(f"  CPU:      {run('top -bn1 | grep Cpu | awk \"{print \\$2}\"')}%")
    print(f"  RAM:      {run('free -m | grep Mem | awk \"{printf \\\"%s/%s MB (%.0f%%)\\\", \\$3, \\$2, \\$3*100/\\$2}\"')}")
    print(f"  Disk:     {run('df -h / | tail -1 | awk \"{print \\$3\\\"/\\\"\\$2\\\" (\\\"\\$5\\\")\\\"}\"')}")
    
    # Netværk
    print("\n📡 NETVÆRK")
    print("-"*40)
    pub_ip = run("curl -s --max-time 3 ifconfig.me 2>/dev/null")
    print(f"  Offentlig IP: {pub_ip}")
    local_ip = run("ip -4 addr show eth0 | grep inet | awk '{print $2}'")
    print(f"  Lokal IP:     {local_ip}")
    print(f"  Åbne porte:   {run('ss -tlnp 2>/dev/null | grep LISTEN | wc -l')}")
    print(f"  Forbindelser: {run('ss -tnp state established 2>/dev/null | wc -l')}")
    
    # Sikkerhed
    alerts = count_alerts()
    total_threats = alerts["CRITICAL"] + alerts["HIGH"] + alerts["MEDIUM"]
    
    print("\n🛡️ SIKKERHEDSALARMER (i dag)")
    print("-"*40)
    print(f"  🔴 CRITICAL: {alerts['CRITICAL']}")
    print(f"  🟠 HIGH:     {alerts['HIGH']}")
    print(f"  🟡 MEDIUM:   {alerts['MEDIUM']}")
    print(f"  🔵 LOW:      {alerts['LOW']}")
    print(f"  ⚪ INFO:     {alerts['INFO']}")
    
    if total_threats > 0:
        print(f"\n  ⚡ SAMLEDE TRUSLER: {total_threats}")
        if alerts["CRITICAL"] > 0:
            print("  🚨🚨🚨 KRITISKE TRUSLER DETEKTERET!")
    else:
        print("\n  ✅ Ingen trusler — alt ser godt ud!")
    
    # Seneste alerts
    print("\n📋 SENESTE ALERTS")
    print("-"*40)
    last = get_last_alerts(8)
    for a in last:
        if "[CRITICAL]" in a:
            print(f"  🔴 {a[-80:]}")
        elif "[HIGH]" in a:
            print(f"  🟠 {a[-80:]}")
        else:
            print(f"  ⚪ {a[-80:]}")
    
    # Blokerede IP'er
    blocked_file = os.path.join(GUARD_DIR, "blocked_ips.txt")
    blocked = 0
    if os.path.exists(blocked_file):
        with open(blocked_file) as f:
            blocked = len(f.readlines())
    print(f"\n🚫 BLOKEREDE IP'ER: {blocked}")
    
    # Cron jobs
    print("\n⏱️ AKTIVE OVERVÅGNINGS-JOBS")
    print("-"*40)
    cron_log = os.path.join(LOG_DIR, "cron_watchdog.log")
    if os.path.exists(cron_log):
        mtime = os.path.getmtime(cron_log)
        ago = int(datetime.now().timestamp() - mtime)
        print(f"  Watchdog:    Sidst kørt for {ago}s siden")
    else:
        print("  Watchdog:    Endnu ikke kørt")
    
    print("\n" + "="*70)
    print("  Opdater med: python3 dashboard.py")
    print("="*70 + "\n")

if __name__ == "__main__":
    dashboard()