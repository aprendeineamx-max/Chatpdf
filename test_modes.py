"""Test both RAG modes with the ingested PDF"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Get the session from database
from app.core.database import SessionLocal, AtomicContext
db = SessionLocal()
ctx = db.query(AtomicContext).first()
if not ctx:
    print("❌ No contexts found!")
    exit()

session_id = ctx.session_id or "test-session-1"
print(f"Using session_id: {session_id}")
print(f"Context: {ctx.folder_name}")
db.close()

# Test 1: Injection Mode
print("\n" + "="*60)
print("TEST 1: INJECTION MODE")
print("="*60)
response = requests.post(
    f"{BASE_URL}/query",
    json={
        "query_text": "¿De qué trata este documento?",
        "session_id": session_id,
        "rag_mode": "injection"
    },
    timeout=120
)
if response.ok:
    data = response.json()
    answer = data.get("answer", str(data))[:500]
    print(f"✅ Response: {answer}...")
else:
    print(f"❌ Error: {response.status_code}")

# Test 2: Semantic Mode
print("\n" + "="*60)
print("TEST 2: SEMANTIC MODE")
print("="*60)
response = requests.post(
    f"{BASE_URL}/query",
    json={
        "query_text": "¿Qué es el planeta Tierra?",
        "session_id": session_id,
        "rag_mode": "semantic"
    },
    timeout=120
)
if response.ok:
    data = response.json()
    answer = data.get("answer", str(data))[:500]
    rag_mode = data.get("rag_mode_used", "unknown")
    print(f"RAG Mode Used: {rag_mode}")
    print(f"✅ Response: {answer}...")
else:
    print(f"❌ Error: {response.status_code}")

print("\n" + "="*60)
print("TESTS COMPLETE")
print("="*60)
