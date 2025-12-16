
import requests
import time

# URL provided by user
target_repo = "https://github.com/aprendeineamx-max/crawlbase-mcp"

url = "http://127.0.0.1:8000/api/v1/ingest/repo"
payload = {"url": target_repo}
headers = {"Content-Type": "application/json"}

print(f"--- TESTING INGESTION FOR: {target_repo} ---")
try:
    res = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {res.status_code}")
    if res.status_code == 200:
        print("Response:", res.json())
        job_id = res.json().get("job_id")
        print(f"Job ID: {job_id}")
    else:
        print("Error Response:", res.text)
except Exception as e:
    print(f"Request Failed: {e}")
