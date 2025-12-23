"""
Test minimalista para verificar routing de Snowflake
"""
import sys
sys.path.insert(0, r'c:\Users\Administrator\Desktop\Universal Pdf\pdf-cortex')

# Simular request
class FakeRequest:
    provider = "snowflake"
    model = "llama3-70b"

request = FakeRequest()

print("="*60)
print("TEST: SIMULANDO ROUTING LOGIC")
print("="*60)

print(f"\n1. request.provider = '{request.provider}'")
print(f"2. Comparando: request.provider == 'snowflake' -> {request.provider == 'snowflake'}")

if request.provider == "snow flake":
    print("3. [OK] Entró al bloque Snowflake")
    
    from app.services.llm.snowflake_service import snowflake_client
    print(f"4. snowflake_client importado, enabled={snowflake_client.enabled}")
    
    if snowflake_client.enabled:
        print("5. [OK] Client habilitado")
        
        try:
            test_query = "Di: TEST MINIMO"
            resp = snowflake_client.complete(test_query, model="llama3-70b")
            print(f"6. [SUCCESS] Respuesta: {resp[:200]}")
        except Exception as e:
            print(f"6. [ERROR] En complete(): {e}")
    else:
        print("5. [FAIL] Client NO habilitado")
else:
    print(f"3. [FAIL] NO entró al if. Provider value: '{request.provider}'")

print("\n" + "="*60)
