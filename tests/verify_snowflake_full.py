    
import sys
import os
import requests
import asyncio

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env from pdf-cortex folder
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from app.core.config import settings
from app.services.llm.snowflake_service import snowflake_client

def test_direct_connection():
    print("--- 1. Testing Direct Snowflake Connection ---")
    print(f"Account: {settings.SNOWFLAKE_ACCOUNT}")
    print(f"User: {settings.SNOWFLAKE_USER}")
    print(f"Token Present: {bool(settings.SNOWFLAKE_TOKEN)}")
    
    try:
        conn = snowflake_client.connect()
        if conn:
            print("✅ Connection Successful!")
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_VERSION()")
            version = cursor.fetchone()[0]
            print(f"❄️  Snowflake Version: {version}")
            conn.close()
            return True
        else:
            print("❌ Connection returned None (Disabled?)")
            return False
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return False

def test_cortex_query():
    print("\n--- 2. Testing Cortex AI (SQL) ---")
    try:
        response = snowflake_client.complete("Say 'Hello from Snowflake Cortex!' in Spanish.")
        print(f"🤖 Cortex Response: {response}")
        if "Error" not in response:
            print("✅ Cortex Working!")
            return True
        else:
            print("⚠️ Cortex returned error (might be distinct from connection error)")
            return False
    except Exception as e:
        print(f"❌ Cortex Test Failed: {e}")
        return False

def test_api_health():
    print("\n--- 3. Testing Local API Health ---")
    try:
        # Assuming port 8000
        url = "http://127.0.0.1:8000/docs"
        res = requests.get(url, timeout=2)
        if res.status_code == 200:
            print("✅ API is UP and Running (Docs accessible)")
            return True
        else:
            print(f"⚠️ API responded with {res.status_code}")
            return False
    except Exception as e:
        print(f"❌ API is unreachable: {e}")
        print("   (Note: verification might run before server fully starts if just restarted)")
        return False

if __name__ == "__main__":
    print("=== STARTING VERIFICATION ===\n")
    
    snowflake_ok = test_direct_connection()
    if snowflake_ok:
        test_cortex_query()
    
    test_api_health()
    
    print("\n=== VERIFICATION COMPLETE ===")
