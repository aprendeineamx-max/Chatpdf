import sys
sys.path.insert(0, r'c:\Users\Administrator\Desktop\Universal Pdf\pdf-cortex')

from dotenv import load_dotenv
load_dotenv(r'c:\Users\Administrator\Desktop\Universal Pdf\pdf-cortex\.env')

from app.core.config import settings
from app.services.llm.snowflake_service import snowflake_client

print("="*60)
print("VERIFICACIÓN COMPLETA DE SNOWFLAKE CORTEX")
print("="*60)

# Test 1: Configuración
print("\n[1] CONFIGURACIÓN:")
print(f"   Account: {settings.SNOWFLAKE_ACCOUNT}")
print(f"   User: {settings.SNOWFLAKE_USER}")
print(f"   Database: {settings.SNOWFLAKE_DATABASE}")
print(f"   Token presente: {bool(settings.SNOWFLAKE_TOKEN)}")
print(f"   Snowflake Client Enabled: {snowflake_client.enabled}")

# Test 2: Conexión Directa
print("\n[2] CONEXIÓN DIRECTA:")
try:
    conn = snowflake_client.connect()
    if conn:
        print("   ✅ Conexión establecida")
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        version = cursor.fetchone()[0]
        print(f"   Snowflake Version: {version}")
        conn.close()
    else:
        print("   ❌ Conexión falló (returned None)")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Cortex COMPLETE
print("\n[3] CORTEX COMPLETE:")
try:
    test_prompt = "Responde EXACTAMENTE: 'Soy Snowflake Cortex funcionando correctamente'"
    response = snowflake_client.complete(test_prompt, model="llama3-70b")
    print(f"   ✅ Respuesta: {response[:200]}")
    if "Snowflake Cortex" in response or "snowflake" in response.lower():
        print("   ✅ CONFIRMADO: Respuesta vino de Snowflake Cortex")
    else:
        print("   ⚠️ Respuesta recibida pero no contiene confirmación esperada")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*60)
print("VERIFICACIÓN COMPLETA")
print("="*60)
