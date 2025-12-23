import sys
sys.path.insert(0, r'c:\Users\Administrator\Desktop\Universal Pdf\pdf-cortex')

from app.services.llm.snowflake_service import snowflake_client

print("Testing Snowflake Cortex Direct Call...")
print(f"Enabled: {snowflake_client.enabled}")

if snowflake_client.enabled:
    try:
        # Very simple prompt
        response = snowflake_client.complete("Di exactamente: PRUEBA EXITOSA", model="llama3-70b")
        print(f"\nSUCCESS! Response: {response}")
    except Exception as e:
        print(f"\nERROR: {e}")
else:
    print("Client not enabled")
