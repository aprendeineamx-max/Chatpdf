import sys
import os
sys.path.insert(0, r'c:\Users\Administrator\Desktop\Universal Pdf\pdf-cortex')

from dotenv import load_dotenv
load_dotenv(r'c:\Users\Administrator\Desktop\Universal Pdf\pdf-cortex\.env')

from app.core.config import settings
import snowflake.connector

print("=== SNOWFLAKE DEBUG ===")
print(f"Account: {settings.SNOWFLAKE_ACCOUNT}")
print(f"User: {settings.SNOWFLAKE_USER}")
print(f"Database: {settings.SNOWFLAKE_DATABASE}")
print(f"Warehouse: {settings.SNOWFLAKE_WAREHOUSE}")
print(f"Token (first 30): {settings.SNOWFLAKE_TOKEN[:30] if settings.SNOWFLAKE_TOKEN else 'NONE'}")
print()

try:
    print("Attempting connection with Token auth...")
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
    print("✅ CONNECTION SUCCESS!")
    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_VERSION()")
    print(f"Snowflake Version: {cursor.fetchone()[0]}")
    conn.close()
except Exception as e:
    print(f"❌ Token auth failed: {type(e).__name__}: {e}")
    print()
    print("Trying password auth as fallback...")
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
        print("✅ PASSWORD AUTH SUCCESS!")
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        print(f"Snowflake Version: {cursor.fetchone()[0]}")
        conn.close()
    except Exception as e2:
        print(f"❌ Password auth also failed: {type(e2).__name__}: {e2}")
