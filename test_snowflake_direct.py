import sys
sys.path.insert(0, r'c:\Users\Administrator\Desktop\Universal Pdf\pdf-cortex')

from dotenv import load_dotenv
load_dotenv(r'c:\Users\Administrator\Desktop\Universal Pdf\pdf-cortex\.env')

from app.core.config import settings
import snowflake.connector

with open(r'c:\Users\Administrator\Desktop\Universal Pdf\pdf-cortex\snowflake_test_result.txt', 'w') as f:
    f.write("=== SNOWFLAKE CONNECTION TEST ===\n\n")
    f.write(f"Account: {settings.SNOWFLAKE_ACCOUNT}\n")
    f.write(f"User: {settings.SNOWFLAKE_USER}\n")
    f.write(f"Database: {settings.SNOWFLAKE_DATABASE}\n")
    f.write(f"Warehouse: {settings.SNOWFLAKE_WAREHOUSE}\n")
    f.write(f"Token present: {bool(settings.SNOWFLAKE_TOKEN)}\n")
    f.write(f"Token (first 30): {settings.SNOWFLAKE_TOKEN[:30] if settings.SNOWFLAKE_TOKEN else 'NONE'}\n\n")
    
    f.write("--- Testing Token Auth ---\n")
    try:
        conn = snowflake.connector.connect(
            user=settings.SNOWFLAKE_USER,
            account=settings.SNOWFLAKE_ACCOUNT,
            authenticator="oauth",
            token=settings.SNOWFLAKE_TOKEN,
            warehouse=settings.SNOWFLAKE_WAREHOUSE,
            database=settings.SNOWFLAKE_DATABASE,
            schema=settings.SNOWFLAKE_SCHEMA,
            role=settings.SNOWFLAKE_ROLE
        )
        f.write("✅ TOKEN AUTH SUCCESS!\n")
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        version = cursor.fetchone()[0]
        f.write(f"Snowflake Version: {version}\n")
        conn.close()
    except Exception as e:
        f.write(f"❌ Token auth failed:\n")
        f.write(f"   Error type: {type(e).__name__}\n")
        f.write(f"   Error message: {str(e)}\n\n")
        
        f.write("--- Testing Password Auth ---\n")
        try:
            conn = snowflake.connector.connect(
                user=settings.SNOWFLAKE_USER,
                password=settings.SNOWFLAKE_PASSWORD,
                account=settings.SNOWFLAKE_ACCOUNT,
                warehouse=settings.SNOWFLAKE_WAREHOUSE,
                database=settings.SNOWFLAKE_DATABASE,
                schema=settings.SNOWFLAKE_SCHEMA,
                role=settings.SNOWFLAKE_ROLE
            )
            f.write("✅ PASSWORD AUTH SUCCESS!\n")
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_VERSION()")
            version = cursor.fetchone()[0]
            f.write(f"Snowflake Version: {version}\n")
            conn.close()
        except Exception as e2:
            f.write(f"❌ Password auth also failed:\n")
            f.write(f"   Error type: {type(e2).__name__}\n")
            f.write(f"   Error message: {str(e2)}\n")

print("Test complete. Results saved to snowflake_test_result.txt")
