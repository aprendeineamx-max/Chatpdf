import requests
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"
# Use pending "Pedro" session to see if it picks up the new prompt
SESSION_ID = "f29d2d0b-c35e-4a72-bfe6-7831a95b5766" 

print(f"Testing Prompt Loading on Session: {SESSION_ID}")

# Query that requires educational explanation
query = "¿Qué dice la página 50?"

print(f"Sending Query: {query}")
r = requests.post(f"{BASE_URL}/query", json={
    "query_text": query,
    "session_id": SESSION_ID,
    "rag_mode": "injection"
}, timeout=60)

if r.ok:
    ans = r.json().get("answer", "")
    print("\n=== AI RESPONSE ===")
    print(ans)
    print("===================\n")
    
    # Check for keywords from the new prompt
    if "Tutor" in ans or "enseñar" in ans or "guía" in ans or "Arquímedes" in ans:
        print("✅ Content seems relevant.")
    else:
        print("⚠️ Response might be generic.")
else:
    print(f"❌ Error: {r.status_code} - {r.text}")
