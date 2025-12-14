
import os
import sys
import json
import base64
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv(".env")

key = os.getenv("VPS_SUPABASE_KEY")
if not key:
    print("❌ No Key Found")
    exit(1)

parts = key.split('.')
if len(parts) != 3:
    print("❌ Invalid JWT format")
    exit(1)

payload = parts[1]
# Pad base64
payload += '=' * (-len(payload) % 4)

try:
    decoded = base64.b64decode(payload)
    data = json.loads(decoded)
    print("--- JWT START ---")
    print(json.dumps(data, indent=2))
    print("--- JWT END ---")
    
    if data.get('role') == 'anon':
        print("⚠️  Key Role: ANON (Restricted by RLS)")
    elif data.get('role') == 'service_role':
        print("✅ Key Role: SERVICE_ROLE (Bypasses RLS)")
    else:
        print(f"Key Role: {data.get('role')}")
        
except Exception as e:
    print(f"❌ Decode Failed: {e}")
