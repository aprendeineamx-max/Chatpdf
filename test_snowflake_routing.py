import requests
import json

API_URL = "http://127.0.0.1:8000/api/v1"

print("=== PRUEBA DIRECTA DE ROUTING ===\n")

# Test con provider explícito
payload_snowflake = {
    "query_text": "Di exactamente: 'Respuesta desde Snowflake Cortex'",
    "pdf_id": "all",
    "mode": "standard",
    "provider": "snowflake",  # EXPLÍCITO
    "model": "llama3-70b",
    "rag_mode": "injection",
    "persona": "architect"
}

print("1. Enviando request con provider='snowflake'...")
print(f"   Payload: {json.dumps(payload_snowflake, indent=2)}\n")

try:
    response = requests.post(f"{API_URL}/query", json=payload_snowflake, timeout=30)
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Respuesta recibida:")
        print(f"      - answer: {result.get('answer', '')[:150]}...")
        print(f"      - metadata: {result.get('metadata', {})}")
        
        # Verificar si realmente vino de Snowflake
        metadata = result.get('metadata', {})
        actual_provider = metadata.get('provider', 'UNKNOWN')
        
        if actual_provider.lower() == 'snowflake':
            print(f"\n   ✅ CORRECTO: La respuesta vino de Snowflake")
        else:
            print(f"\n   ❌ ERROR: Se solicitó Snowflake pero la respuesta vino de: {actual_provider}")
    else:
        print(f"   ❌ Error HTTP: {response.text}")
except Exception as e:
    print(f"   ❌ Exception: {e}")

print("\n" + "="*50)
