
import requests
import time

url = "http://127.0.0.1:8000/api/v1/ingest/repo"
payload = {"url": "https://github.com/octocat/Hello-World"}
headers = {"Content-Type": "application/json"}

try:
    print(f"Triggering ingestion for {payload['url']}...")
    res = requests.post(url, json=payload, headers=headers)
    print(f"Status: {res.status_code}")
    print(res.json())
except Exception as e:
    print(f"Failed: {e}")
