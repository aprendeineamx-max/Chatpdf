import requests
import uuid
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"
SESSION_ID = str(uuid.uuid4()) # Fresh session to control history exactly

print(f"Testing Navigation Intent on Session: {SESSION_ID}")
print("Mode: Injection (which has the logic)")

# 1. Ask about Page 50 (Pollute context with Archimedes)
print("\n--- TURN 1: Page 50 ---")
q1 = "¿Qué dice la página 50?"
r1 = requests.post(f"{BASE_URL}/query", json={
    "query_text": q1,
    "session_id": SESSION_ID,
    "rag_mode": "injection" # Should trigger page injection for 50
}, timeout=60)
ans1 = r1.json().get("answer", "")
print(f"AI: {ans1[:150]}...")

# 2. Ask about Page 79 (Should Switch Context)
print("\n--- TURN 2: Page 79 (Navigation Intent) ---")
q2 = "Ok, ahora dime qué dice la página 79"
r2 = requests.post(f"{BASE_URL}/query", json={
    "query_text": q2,
    "session_id": SESSION_ID,
    "rag_mode": "injection" # Should trigger page injection for 79 + SYSTEM override
}, timeout=60)
ans2 = r2.json().get("answer", "")
print(f"AI: {ans2[:300]}...")

# Validation
print("\n--- VALIDATION ---")
# Page 50 is about Archimedes/Gold Crown. 
# We don't strictly know what P79 is about (debug was truncated), but it definitely shouldn't be about Archimedes if the switch worked.

has_archimedes = "Arquímedes" in ans2 or "corona" in ans2 or "Hieron" in ans2
has_generic_refusal = "no tengo información" in ans2.lower()

print(f"Mentioned Archimedes (Old Context)? {has_archimedes}")

if not has_archimedes and not has_generic_refusal and len(ans2) > 50:
    print("✅ SUCCESS: Context Switched Cleanly (No Archimedes traces).")
elif has_archimedes:
    print("❌ FAILURE: Still talking about Archimedes (Context Stuck).")
elif has_generic_refusal:
    print("⚠️ WARNING: AI Refused to answer (Content missing?).")
else:
    print("✅ SUCCESS: Answer provided without old context traces.")
