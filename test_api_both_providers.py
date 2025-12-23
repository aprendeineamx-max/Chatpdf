import requests
import json

API_URL = "http://127.0.0.1:8000/api/v1"

# Test 1: Organic System (Sambanova)
print("=== TEST 1: Sistema Orgánico (Sambanova) ===")
payload1 = {
    "query_text": "Hola, ¿está funcionando el sistema orgánico?",
    "pdf_id": "all",
    "mode": "standard",
    "provider": "sambanova",
    "model": "Meta-Llama-3.3-70B-Instruct",
    "rag_mode": "injection",
    "persona": "architect"
}

try:
    response1 = requests.post(f"{API_URL}/query", json=payload1, timeout=30)
    print(f"Status: {response1.status_code}")
    if response1.status_code == 200:
        result = response1.json()
        print(f"✅ Respuesta: {result.get('answer', '')[:200]}...")
        print(f"Session ID: {result.get('session_id')}")
    else:
        print(f"❌ Error: {response1.text}")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n")

# Test 2: Snowflake Cortex
print("=== TEST 2: Snowflake Cortex ===")
payload2 = {
    "query_text": "¿Funciona Snowflake Cortex correctamente?",
    "pdf_id": "all",
    "mode": "standard",
    "provider": "snowflake",
    "model": "llama3-70b",
    "rag_mode": "injection",
    "persona": "architect"
}

try:
    response2 = requests.post(f"{API_URL}/query", json=payload2, timeout=30)
    print(f"Status: {response2.status_code}")
    if response2.status_code == 200:
        result = response2.json()
        print(f"✅ Respuesta: {result.get('answer', '')[:200]}...")
        print(f"Provider Metadata: {result.get('metadata', {})}")
    else:
        print(f"❌ Error: {response2.text}")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n=== TESTS COMPLETE ===")
