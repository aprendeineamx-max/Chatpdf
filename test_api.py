import requests
import json

try:
    url = "http://127.0.0.1:8000/api/v1/sessions"
    print(f"Fetching {url}...")
    res = requests.get(url)
    
    if res.status_code == 200:
        data = res.json()
        print(f"✅ Success! Got {len(data)} sessions.")
        if len(data) > 0:
            print("Sample:", data[0])
    else:
        print(f"❌ Failed: {res.status_code}")
        print(res.text)
except Exception as e:
    print(f"❌ Error: {e}")
