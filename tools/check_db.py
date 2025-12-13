
import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Add root to path
sys.path.append(os.getcwd())

load_dotenv(".env")
load_dotenv("genesis-web/.env") 

url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL") or os.getenv("VPS_SUPABASE_URL")
key = os.getenv("VITE_SUPABASE_KEY") or os.getenv("SUPABASE_KEY") or os.getenv("VPS_SUPABASE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(url, key)

print("--- Recent Timeline Entries ---")
try:
    response = supabase.table("atomic_contexts").select("*").order("created_at", desc=True).limit(5).execute()
    for row in response.data:
        print(f"ID: {row.get('id')}")
        print(f"Folder: {row.get('folder_name')}")
        print(f"Timestamp: {row.get('timestamp')}")
        print("---")
except Exception as e:
    print(f"Error fetching contexts: {e}")
    response = None

print("\n--- Checking Artifacts for Latest Context ---")
if response and response.data:
    latest_id = response.data[0]['id']
    try:
        arts = supabase.table("atomic_artifacts").select("*").eq("context_id", latest_id).execute()
        for art in arts.data:
            print(f"Artifact: {art.get('filename')} (Type: {art.get('file_type')})")
    except Exception as e:
        print(f"Error fetching artifacts: {e}")
