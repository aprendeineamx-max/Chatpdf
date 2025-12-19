"""Simple comprehensive test - API only"""
import requests
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"

# SESSION 1: Fresh for History Test
session_id_fresh = str(uuid.uuid4())
print(f"Fresh Session: {session_id_fresh}")

# SESSION 2: Existing for RAG Test (has book)
session_id_rag = "032574a7-e38b-4ff2-a990-67c1ed22074d"
print(f"RAG Session:   {session_id_rag}")
print("="*60)

# Test 1: Greeting Fix + History (FRESH SESSION)
print("\n--- TEST 1: Chat History + Greeting Fix ---")
print("Message 1: 'Me llamo Juan'")
r1 = requests.post(f"{BASE_URL}/query", json={
    "query_text": "Me llamo Juan y estoy feliz de conocerte",
    "session_id": session_id_fresh,
    "rag_mode": "injection"
}, timeout=120)
a1 = r1.json().get("answer", "ERROR")
print(f"Response 1 (first 150 chars): {a1[:150]}...\n")

print("Message 2: '¿Cómo me llamo?'")
r2 = requests.post(f"{BASE_URL}/query", json={
    "query_text": "¿Cómo me llamo? Responde solo con mi nombre.",
    "session_id": session_id_fresh,
    "rag_mode": "injection"
}, timeout=120)
a2 = r2.json().get("answer", "ERROR")
print(f"Response 2 (first 300 chars): {a2[:300]}...")

# Check results
no_hola = not (a2[:30].lower().startswith("¡hola") or a2[:30].lower().startswith("hola"))
remembers = "juan" in a2.lower()
print(f"\n✅ No re-greeting: {no_hola} (first 30: '{a2[:30]}')")
print(f"✅ Remembers Juan: {remembers}")

# Test 2: Injection Mode (RAG SESSION)
print("\n--- TEST 2: Injection Mode - Page Query ---")
print("Query: '¿Qué dice la página 70?'")
r3 = requests.post(f"{BASE_URL}/query", json={
    "query_text": "¿Qué dice la página 70 del libro Nuestro Planeta la Tierra?",
    "session_id": session_id_rag,
    "rag_mode": "injection"
}, timeout=180)
a3 = r3.json().get("answer", "ERROR")
print(f"Response (first 400 chars): {a3[:400]}...")
has_content = len(a3) > 100
print(f"\n✅ Has content: {has_content} ({len(a3)} chars)")

# Test 3: Semantic Mode (RAG SESSION)
print("\n--- TEST 3: Semantic Mode - Topic Query ---")
print("Query: '¿Qué es la Tierra?' (SEMANTIC)")
r4 = requests.post(f"{BASE_URL}/query", json={
    "query_text": "¿Qué es la Tierra según este documento?",
    "session_id": session_id_rag,
    "rag_mode": "semantic"
}, timeout=180)
d4 = r4.json()
a4 = d4.get("answer", "ERROR")
mode = d4.get("rag_mode_used", "unknown")
print(f"Mode used: {mode}")
print(f"Response (first 400 chars): {a4[:400]}...")
print(f"\n✅ Semantic response: {len(a4) > 50}")

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
all_pass = no_hola and remembers and has_content
if all_pass:
    print("✅ ALL TESTS PASSED!")
else:
    print("❌ SOME TESTS FAILED")
    if not no_hola: print("  - Greeting fix failed")
    if not remembers: print("  - Chat history failed")
    if not has_content: print("  - Injection mode failed")
