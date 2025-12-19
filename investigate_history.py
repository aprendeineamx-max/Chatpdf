"""Investigate chat history issue"""
import requests

BASE_URL = 'http://127.0.0.1:8000/api/v1'
session_id = '032574a7-e38b-4ff2-a990-67c1ed22074d'

# Check history in DB
from app.core.database import SessionLocal, ChatMessage
db = SessionLocal()
msgs = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
print(f"Messages in DB for this session: {len(msgs)}")
for m in msgs[-8:]:
    print(f"  {m.role}: {m.content[:60]}...")
db.close()

# Send a new message
print("\nSending: 'Me llamo TESTNAME999'")
r1 = requests.post(f"{BASE_URL}/query", json={
    "query_text": "Me llamo TESTNAME999",
    "session_id": session_id,
    "rag_mode": "injection"
}, timeout=120)
print(f"Response 1: {r1.json().get('answer', '')[:100]}")

# Check DB again
db = SessionLocal()
msgs = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
print(f"\nMessages in DB now: {len(msgs)}")
for m in msgs[-4:]:
    print(f"  {m.role}: {m.content[:60]}...")
db.close()

# Ask for name
print("\nSending: 'What is my name?'")
r2 = requests.post(f"{BASE_URL}/query", json={
    "query_text": "Cual es mi nombre? Responde solo con mi nombre.",
    "session_id": session_id,
    "rag_mode": "injection"
}, timeout=120)
a2 = r2.json().get("answer", "")
print(f"Response 2: {a2[:200]}")
print(f"\nContains TESTNAME999: {'TESTNAME999' in a2}")
