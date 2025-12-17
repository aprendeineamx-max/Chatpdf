
import requests
import sys

try:
    r = requests.get("http://127.0.0.1:8000/docs", timeout=5)
    if r.status_code == 200:
        print("✅ Server is UP")
    else:
        print(f"❌ Server returned {r.status_code}")
except Exception as e:
    print(f"❌ Server Unreachable: {e}")
