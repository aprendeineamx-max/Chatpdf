
import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Add root to path
sys.path.append(os.getcwd())

# 1. Load Root .env
print("--- Loading Root .env ---")
load_dotenv(".env")
root_url = os.getenv("SUPABASE_URL")
root_key = os.getenv("SUPABASE_KEY")
print(f"ROOT URL: {root_url}")
print(f"ROOT KEY: {root_key[:5]}..." if root_key else "None")

# 2. Check Tables via Service Role (Admin)
print("\n--- Checking DB Tables (Admin) ---")
try:
    admin_client = create_client(root_url, root_key)
    
    # Try select
    res = admin_client.table("chat_messages").select("count", count="exact").execute()
    print(f"✅ 'chat_messages' exists. Row count: {res.count}")
    
    res = admin_client.table("orchestrator_tasks").select("count", count="exact").execute()
    print(f"✅ 'orchestrator_tasks' exists. Row count: {res.count}")
    
except Exception as e:
    print(f"❌ Admin Check Failed: {e}")

# 3. Load Frontend .env and Simulate User
print("\n--- Simulating Frontend (Anon) ---")
load_dotenv("genesis-web/.env", override=True)
vite_url = os.getenv("VITE_SUPABASE_URL")
vite_key = os.getenv("VITE_SUPABASE_KEY")

print(f"VITE URL: {vite_url}")
print(f"VITE KEY: {vite_key[:5]}..." if vite_key else "None")

if root_url != vite_url:
    print("⚠️  WARNING: URL Mismatch between Root and Frontend!")

try:
    anon_client = create_client(vite_url, vite_key)
    
    # Test Insert
    print("Attempting INSERT with ANON key...")
    data = {"role": "user", "content": "AUDIT_TEST_MESSAGE"}
    res = anon_client.table("chat_messages").insert(data).execute()
    print("✅ Insert Success! RLS is configured correctly.")
    
    # Clean up
    if res.data:
        mid = res.data[0]['id']
        # Anon might not be able to delete depending on policy, but that's fine.
        print(f"Inserted ID: {mid}")

except Exception as e:
    print(f"❌ Frontend Simulation Failed: {e}")
    print("   -> This confirms the User's issue. The Frontend cannot write to the DB.")
