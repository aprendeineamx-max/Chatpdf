"""Ingest into existing session"""
import requests
import uuid
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"
SESSION_ID = "f29d2d0b-c35e-4a72-bfe6-7831a95b5766"  # Pedro Session
BOOK_URL = "https://drive.google.com/file/d/1mU6iMWe0ZxtfJqaTmNqybJyO2ax7JlJI/view?usp=sharing"

print(f"Ingesting into session: {SESSION_ID}")

r = requests.post(f"{BASE_URL}/ingest/pdf", json={
    "url": BOOK_URL,
    "session_id": SESSION_ID,
    "scope": "session",
    "rag_mode": "injection",
    "page_offset": 0,
    "enable_ocr": False
}, timeout=30)
print(f"Status: {r.status_code}")
job_id = r.json().get("job_id")
print(f"Job ID: {job_id}")

# Wait for completion
print("Waiting for completion...")
for i in range(30): # 30 * 10s = 5 mins
    time.sleep(10)
    print(f"Polling {i+1}...")
    status_r = requests.get(f"{BASE_URL}/ingest/jobs/{job_id}")
    if status_r.ok:
        status = status_r.json().get("status")
        print(f"Status: {status}")
        if status == "COMPLETED":
            print("✅ Ingestion Complete!")
            break
        if status == "FAILED":
            print("❌ Failed")
            break
