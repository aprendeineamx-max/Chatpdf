import requests
import json

API_URL = "http://127.0.0.1:8000/api/v1/query"

# Test directo con provider=snowflake
payload = {
    "query_text": "Di exactamente: PRUEBA DIRECTA SNOWFLAKE",
    "pdf_id": "all",
    "mode": "standard",
    "provider": "snowflake",  # EXPLÍCITAMENTE snowflake
    "model": "llama3-70b",
    "rag_mode": "injection",
    "persona": "architect"
}

print("="*60)
print("TEST DIRECTO API - Provider: snowflake")
print("="*60)
print(f"\nPayload enviado:")
print(json.dumps(payload, indent=2))
print("\n" + "="*60)

try:
    response = requests.post(API_URL, json=payload, timeout=40)
    print(f"\nStatus Code: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        
        print("RESPUESTA DEL BACKEND:")
        print(f"  - answer: {data.get('answer', '')[:300]}...")
        print(f"  - metadata: {data.get('metadata', {})}")
        print(f"  - session_id: {data.get('session_id', 'N/A')}")
        
        # VERIFICACIÓN CRÍTICA
        metadata = data.get('metadata', {})
        actual_provider = metadata.get('provider', 'NO METADATA')
        
        print("\n" + "="*60)
        print("VERIFICACIÓN:")
        print("="*60)
        print(f"  Provider solicitado: snowflake")
        print(f"  Provider que respondió: {actual_provider}")
        
        if 'snowflake' in str(actual_provider).lower():
            print("\n  ✅ ÉXITO: Snowflake procesó la solicitud")
        else:
            print(f"\n  ❌ ERROR: Se envió 'snowflake' pero respondió '{actual_provider}'")
            print("  -> El routing NO está funcionando")
    else:
        print(f"ERROR HTTP {response.status_code}:")
        print(response.text)
        
except Exception as e:
    print(f"\n❌ Exception durante la prueba: {e}")

print("\n" + "="*60)
