import requests
import json
import time

url = "http://127.0.0.1:8000/api/v1/query"
payload = {
    "query_text": "Hola",
    "pdf_id": "all"
}
headers = {
    "Content-Type": "application/json"
}

print(f"🚀 Sending request to {url}...")
start = time.time()
try:
    response = requests.post(url, json=payload, headers=headers)
    elapsed = time.time() - start
    print(f"⏱️ Time taken: {elapsed:.2f}s")
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(response.text)
except Exception as e:
    print(f"❌ Request failed: {e}")
