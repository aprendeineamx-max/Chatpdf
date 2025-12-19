"""Quick test for greeting fix"""
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Get existing session
from app.core.database import SessionLocal, AtomicContext
db = SessionLocal()
ctx = db.query(AtomicContext).first()
session_id = ctx.session_id if ctx else "test-session-123"
db.close()

print(f"Using session: {session_id}")

# Message 1
print("\n--- MESSAGE 1 ---")
r1 = requests.post(f"{BASE_URL}/query", json={
    "query_text": "Mi nombre es Elena",
    "session_id": session_id,
    "rag_mode": "injection"
}, timeout=120)
print(r1.json().get("answer", "")[:300])

# Message 2 - should NOT re-greet
print("\n--- MESSAGE 2 (should NOT say Hola) ---")
r2 = requests.post(f"{BASE_URL}/query", json={
    "query_text": "¿Cómo me llamo?",
    "session_id": session_id,
    "rag_mode": "injection"
}, timeout=120)
answer = r2.json().get("answer", "")
print(answer[:400])

# Check
if "Hola" in answer[:50]:
    print("\n❌ FAIL: AI still says Hola in response")
else:
    print("\n✅ PASS: AI did NOT re-greet!")
