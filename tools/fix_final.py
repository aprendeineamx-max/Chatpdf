
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv(".env")

url = os.getenv("SUPABASE_DB_URL") or os.getenv("VPS_SUPABASE_DB_URL") 
if not url:
    print("❌ URL Missing")
    exit(1)

# FORCE DIRECT CONNECTION (Bypass Pooler for DDL)
# Pooler: aws-0-us-east-1.pooler.supabase.com
# Direct: db.jrjsxjmjfsjltgutssib.supabase.co
# We need to extract the Ref from the URL or Config.
# VPS_SUPABASE_URL=https://jrjsxjmjfsjltgutssib.supabase.co
# Ref = jrjsxjmjfsjltgutssib

if "pooler" in url:
    url = url.replace("aws-0-us-east-1.pooler.supabase.com:6543", "db.jrjsxjmjfsjltgutssib.supabase.co:5432")
    # Also remove sslmode=require if needed, or keep it. Direct usually needs it.
    if "sslmode" not in url:
        url += "?sslmode=require"

print(f"🔌 Connecting to DIRECT DB (Port 5432)...")
print(f"URL: {url.split('@')[1]}") # Log safe part

try:
    engine = create_engine(url)
    
    # 1. Verify connection
    with engine.connect() as conn:
        print("✅ Connected!")
        
        # 2. Run DDL
        cmds = [
            # Chat Messages - The critical one
            "alter table chat_messages enable row level security",
            "drop policy if exists \"Public Access Messages\" on chat_messages",
            "create policy \"Public Access Messages\" on chat_messages for all using (true) with check (true)",
            "grant all on chat_messages to anon",
            "grant all on chat_messages to authenticated",
            "grant all on chat_messages to service_role",
            
            # Tasks
            "alter table orchestrator_tasks enable row level security",
            "drop policy if exists \"Public Access Tasks\" on orchestrator_tasks",
            "create policy \"Public Access Tasks\" on orchestrator_tasks for all using (true) with check (true)",
            "grant all on orchestrator_tasks to anon"
        ]
        
        for sql in cmds:
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f"✅ Executed: {sql[:40]}...")
            except Exception as e:
                print(f"⚠️ Cmd Failed: {sql[:20]}... {e}")
                
        print("🚀 FIX COMPLETE.")

except Exception as e:
    print(f"❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
