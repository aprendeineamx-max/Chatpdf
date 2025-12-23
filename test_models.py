import sys
sys.path.insert(0, r'c:\Users\Administrator\Desktop\Universal Pdf\pdf-cortex')

from dotenv import load_dotenv
load_dotenv()

import snowflake.connector
from app.core.config import settings

print("Testing Snowflake Connection and CORTEX...")

conn = snowflake.connector.connect(
    account=settings.SNOWFLAKE_ACCOUNT,
    user=settings.SNOWFLAKE_USER,
    password=settings.SNOWFLAKE_TOKEN,
    warehouse=settings.SNOWFLAKE_WAREHOUSE,
    database=settings.SNOWFLAKE_DATABASE,
    schema=settings.SNOWFLAKE_SCHEMA
)

cursor = conn.cursor()

# Test 1: Simple version check
print("\n1. Version Check:")
cursor.execute("SELECT CURRENT_VERSION()")
print(f"   Version: {cursor.fetchone()[0]}")

# Test 2: List available models
print("\n2. Testing CORTEX with simplest possible query:")
try:
    # Try with snowflake-arctic (known to work)
    cursor.execute("SELECT SNOWFLAKE.CORTEX.COMPLETE('snowflake-arctic', 'Say: TEST') as response")
    result = cursor.fetchone()
    print(f"   SUCCESS with snowflake-arctic: {result[0][:100]}")
except Exception as e:
    print(f"   FAILED: {e}")

# Test 3: Try with llama3-70b
print("\n3. Testing with llama3-70b:")
try:
    cursor.execute("SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3-70b', 'Say: TEST') as response")
    result = cursor.fetchone()
    print(f"   SUCCESS with llama3-70b: {result[0][:100]}")
except Exception as e:
    print(f"   FAILED: {e}")

conn.close()
print("\nDone!")
