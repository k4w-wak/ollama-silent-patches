#!/usr/bin/env python3
"""
ProtonMail Inbox Checker — admin@local
Usage: python3 check_protonmail.py [PASSWORD]

If no password is provided, will prompt for it.
Checks INBOX and SENT folders for recent emails, especially
from media contacts and security researchers.

After login, also re-authenticates hydroxide for future use.
"""
import imaplib
import email
from email.header import decode_header
import sys
import getpass
import time

# ProtonMail Bridge settings
IMAP_HOST = '127.0.0.1'
IMAP_PORT = 1143  # hydroxide port (or 1143 for ProtonMail Bridge)
USERNAME = 'admin@local'

def decode_header_value(raw):
    """Decode email header with proper encoding handling"""
    decoded = decode_header(raw)
    result = []
    for part, enc in decoded:
        if isinstance(part, bytes):
            result.append(part.decode(enc or 'utf-8', errors='replace'))
        else:
            result.append(str(part))
    return ''.join(result)

def check_inbox(password):
    """Connect to ProtonMail via IMAP and check for recent emails"""
    print(f"[*] Connecting to ProtonMail IMAP at {IMAP_HOST}:{IMAP_PORT}...")
    
    try:
        m = imaplib.IMAP4(IMAP_HOST, IMAP_PORT)
        print(f"[+] Connected! Banner: {m.welcome}")
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        print("[!] Make sure hydroxide is running: /home/admin_user/go/bin/hydroxide serve &")
        return None
    
    try:
        result = m.login(USERNAME, password)
        print(f"[+] Login successful!")
    except imaplib.IMAP4.error as e:
        print(f"[-] Login failed: {e}")
        print("[!] If 'no such user', try: /home/admin_user/go/bin/hydroxide auth admin@local")
        m.logout()
        return None
    
    # List mailboxes
    typ, boxes = m.list()
    print(f"\n[*] Available mailboxes:")
    for b in boxes:
        print(f"  {b.decode()}")
    
    # Check INBOX
    print("\n" + "="*70)
    print("📥 INBOX — Recent emails")
    print("="*70)
    check_folder(m, 'INBOX')
    
    # Check SENT
    print("\n" + "="*70)
    print("📤 SENT — Recent emails")
    print("="*70)
    check_folder(m, 'Sent')
    
    # Check All Mail
    print("\n" + "="*70)
    print("📁 ALL MAIL — Recent emails")
    print("="*70)
    check_folder(m, 'All Mail')
    
    m.logout()
    return m

def check_folder(m, folder_name):
    """Check a specific mail folder for recent emails"""
    try:
        typ, data = m.select(folder_name)
        if typ != 'OK':
            print(f"  [!] Folder '{folder_name}' not accessible")
            return
        
        total = int(data[0])
        print(f"  Total messages: {total}")
        
        # Search for recent messages (last 14 days)
        from datetime import datetime, timedelta
        since = (datetime.now() - timedelta(days=14)).strftime("%d-%b-%Y")
        
        typ, msg_ids = m.search(None, f'(SINCE {since})')
        if typ != 'OK':
            print("  No messages found")
            return
        
        id_list = msg_ids[0].split()
        print(f"  Messages in last 14 days: {len(id_list)}")
        
        # KEY CONTACTS to highlight
        key_contacts = [
            'promptarmor', 'striga', 'cert', 'ollama', 'bruce', 'chiang',
            'hackernews', 'securityweek', 'bleepingcomputer', 'therecord',
            'darkreading', 'threatpost', 'cyera', 'oligo', 'imperva'
        ]
        
        # Get message details (last 30)
        for mid in id_list[-30:]:
            typ, msg_data = m.fetch(mid, '(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE TO CC)])')
            if typ == 'OK':
                for part in msg_data:
                    if isinstance(part, tuple):
                        raw = part[1].decode('utf-8', errors='replace')
                        subject = from_ = date_ = to_ = ''
                        for line in raw.split('\n'):
                            line = line.strip()
                            if line.lower().startswith('subject:'):
                                subject = decode_header_value(line[9:].strip())
                            elif line.lower().startswith('from:'):
                                from_ = decode_header_value(line[6:].strip())
                            elif line.lower().startswith('date:'):
                                date_ = line[6:].strip()
                            elif line.lower().startswith('to:'):
                                to_ = line[4:].strip()
                        
                        # Highlight key contacts
                        is_key = any(kc in from_.lower() for kc in key_contacts)
                        marker = "⭐" if is_key else "  "
                        
                        print(f"  {marker} [{mid.decode()}] {date_}")
                        print(f"  {marker}   From: {from_}")
                        print(f"  {marker}   Subject: {subject}")
                        if to_:
                            print(f"  {marker}   To: {to_}")
                        print()
        
    except Exception as e:
        print(f"  Error checking {folder_name}: {e}")

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════╗
║  ProtonMail Inbox Checker                ║
║  admin@local                       ║
╚══════════════════════════════════════════╝
    """)
    
    # Get password
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        password = getpass.getpass("Enter ProtonMail password: ")
    
    # First, re-authenticate hydroxide if needed
    print("\n[*] Tip: If login fails, run this first:")
    print("    /home/admin_user/go/bin/hydroxide auth admin@local")
    print("    Then: /home/admin_user/go/bin/hydroxide serve &")
    print()
    
    m = check_inbox(password)
    
    if m is None:
        print("\n[!] Quick fix options:")
        print("    1. Re-authenticate hydroxide: /home/admin_user/go/bin/hydroxide auth admin@local")
        print("    2. Start hydroxide: /home/admin_user/go/bin/hydroxide serve &")
        print("    3. Then run this script again with bridge password")