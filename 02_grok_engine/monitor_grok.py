import os, time, json

def get_latest_log():
    path = os.path.expanduser("~/.grok/sessions/")
    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.json')]
    return max(files, key=os.path.getmtime) if files else None

print("📡 STARTING LIVE BOUNTY MONITOR...")
last_size = 0
shown = set()

while True:
    log_file = get_latest_log()
    if log_file:
        current_size = os.path.getsize(log_file)
        if current_size > last_size:
            with open(log_file, 'r') as f:
                try:
                    data = json.load(f)
                    msgs = data.get('messages', data if isinstance(data, list) else [])
                    for i, msg in enumerate(msgs):
                        if i not in shown:
                            shown.add(i)
                            role = msg.get('role','?').upper()
                            content = str(msg.get('content',''))
                            if len(content) > 500:
                                content = content[:500] + '...'
                            print(f"\n--- [{role}] ---")
                            print(content)
                    last_size = current_size
                except: pass
    time.sleep(1)
