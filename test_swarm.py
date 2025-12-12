import requests
import json

url = "http://127.0.0.1:8000/api/v1/query"
payload = {
    "query_text": "Que es el calentamiento global?",
    "pdf_id": "all",
    "mode": "swarm"
}
headers = {'Content-Type': 'application/json'}

try:
    print("🐝 Sending SWARM Request...")
    r = requests.post(url, json=payload, headers=headers)
    
    if r.status_code == 200:
        data = r.json()
        print("✅ Status Code: 200 OK")
        print(f"🤖 Answer Start: {data['answer'][:100]}...")
        if "Hydra Swarm" in data['answer']:
             print("✅ Hydra Swarm Tag Found!")
        else:
             print("❌ Hydra Swarm Tag NOT Found (Check Mode logic)")
    else:
        print(f"❌ Error: {r.status_code}")
        print(r.text)

except Exception as e:
    print(f"❌ Connection Failed: {e}")
