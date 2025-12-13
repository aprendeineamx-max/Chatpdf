
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv(".env")

db_url = os.getenv("SUPABASE_DB_URL") or os.getenv("VPS_SUPABASE_DB_URL") 
if not db_url:
    print("❌ No SUPABASE_DB_URL found.")
    exit(1)

# Modify URL for Session Mode if needed? 
# Usually Pooler supports basic DDL.
print(f"🔌 Connecting to DB...")

try:
    engine = create_engine(db_url)
    
    cmds = [
        # Chat Sessions
        "alter table chat_sessions enable row level security",
        "drop policy if exists \"Public Access Sessions\" on chat_sessions",
        "create policy \"Public Access Sessions\" on chat_sessions for all using (true) with check (true)",
        
        # Chat Messages
        "alter table chat_messages enable row level security",
        "drop policy if exists \"Public Access Messages\" on chat_messages",
        "create policy \"Public Access Messages\" on chat_messages for all using (true) with check (true)",
        
        # Tasks
        "alter table orchestrator_tasks enable row level security",
        "drop policy if exists \"Public Access Tasks\" on orchestrator_tasks",
        "create policy \"Public Access Tasks\" on orchestrator_tasks for all using (true) with check (true)",
        
        # Grants (Just in case RLS is bypassed but perms are missing)
        "grant all on chat_sessions to anon",
        "grant all on chat_messages to anon",
        "grant all on orchestrator_tasks to anon",
        "grant all on chat_sessions to service_role",
        "grant all on chat_messages to service_role",
        "grant all on orchestrator_tasks to service_role"
    ]

    with engine.connect() as conn:
        for sql in cmds:
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f"✅ Executed: {sql[:50]}...")
            except Exception as e:
                print(f"⚠️ Error on: {sql[:30]}... -> {str(e)[:100]}")
                
        print("🎉 RLS Refreshed Successfully.")
        
except Exception as e:
    print(f"❌ Connection Failed: {e}")
