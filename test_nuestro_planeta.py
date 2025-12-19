"""Ingest Nuestro Planeta book via API and test both modes"""
import requests
import time
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"
BOOK_URL = "https://drive.google.com/file/d/1mU6iMWe0ZxtfJqaTmNqybJyO2ax7JlJI/view?usp=sharing"

# Create a session ID
session_id = str(uuid.uuid4())
print(f"Session ID: {session_id}")

# Step 1: Ingest the PDF
print("\n" + "="*60)
print("STEP 1: INGESTING NUESTRO PLANETA LA TIERRA")
print("="*60)

job_id = str(uuid.uuid4())
response = requests.post(
    f"{BASE_URL}/ingest/pdf",
    json={
        "url": BOOK_URL,
        "session_id": session_id,
        "scope": "session",
        "rag_mode": "injection",
        "page_offset": 0,
        "enable_ocr": False
    },
    timeout=30
)

if response.ok:
    data = response.json()
    print(f"✅ Ingestion started: {data}")
    job_id = data.get("job_id", job_id)
else:
    print(f"❌ Error starting ingestion: {response.status_code}")
    print(response.text)
    exit(1)

# Wait for ingestion to complete
print("\nWaiting for ingestion to complete (checking every 10s)...")
max_wait = 300  # 5 minutes max
waited = 0
while waited < max_wait:
    time.sleep(10)
    waited += 10
    print(f"  Waited {waited}s...")
    
    # Check job status
    try:
        status_resp = requests.get(f"{BASE_URL}/ingest/jobs/{job_id}", timeout=10)
        if status_resp.ok:
            job_data = status_resp.json()
            status = job_data.get("status", "UNKNOWN")
            print(f"  Status: {status}")
            if status == "COMPLETED":
                print("✅ Ingestion COMPLETED!")
                break
            elif status == "FAILED":
                print(f"❌ Ingestion FAILED: {job_data.get('error')}")
                exit(1)
    except:
        pass

# Step 2: Test Injection Mode
print("\n" + "="*60)
print("STEP 2: TEST INJECTION MODE - Page 70")
print("="*60)

response = requests.post(
    f"{BASE_URL}/query",
    json={
        "query_text": "¿Qué dice la página 70 del libro?",
        "session_id": session_id,
        "rag_mode": "injection"
    },
    timeout=180
)

if response.ok:
    data = response.json()
    answer = data.get("answer", str(data))
    print(f"✅ INJECTION MODE Response:\n{answer[:800]}")
else:
    print(f"❌ Error: {response.status_code}")

# Step 3: Test Semantic Mode
print("\n" + "="*60)
print("STEP 3: TEST SEMANTIC MODE - What is Earth?")
print("="*60)

response = requests.post(
    f"{BASE_URL}/query",
    json={
        "query_text": "¿Qué es la Tierra según el documento?",
        "session_id": session_id,
        "rag_mode": "semantic"
    },
    timeout=180
)

if response.ok:
    data = response.json()
    answer = data.get("answer", str(data))
    rag_mode = data.get("rag_mode_used", "unknown")
    print(f"RAG Mode Used: {rag_mode}")
    print(f"✅ SEMANTIC MODE Response:\n{answer[:800]}")
else:
    print(f"❌ Error: {response.status_code}")

# Step 4: Test Chat History (multiple turns)
print("\n" + "="*60)
print("STEP 4: TEST CHAT HISTORY")
print("="*60)

# First message
response = requests.post(
    f"{BASE_URL}/query",
    json={
        "query_text": "Mi nombre es Carlos y estoy estudiando geografía",
        "session_id": session_id,
        "rag_mode": "injection"
    },
    timeout=120
)
print("First message sent...")

# Second message - should NOT re-greet
response = requests.post(
    f"{BASE_URL}/query",
    json={
        "query_text": "¿Recuerdas cómo me llamo y qué estoy estudiando?",
        "session_id": session_id,
        "rag_mode": "injection"
    },
    timeout=120
)

if response.ok:
    data = response.json()
    answer = data.get("answer", str(data))
    print(f"✅ CHAT HISTORY Response:\n{answer[:600]}")
    
    # Check if it re-greeted (BAD) or not (GOOD)
    if "¡Hola" in answer or "Hola de nuevo" in answer:
        print("\n⚠️ WARNING: AI still re-greeting (should be fixed)")
    else:
        print("\n✅ SUCCESS: AI did NOT re-greet, responded naturally!")
else:
    print(f"❌ Error: {response.status_code}")

print("\n" + "="*60)
print("ALL TESTS COMPLETE")
print("="*60)
