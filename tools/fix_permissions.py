
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv(".env")
load_dotenv("genesis-web/.env")

db_url = os.getenv("SUPABASE_DB_URL") or os.getenv("VPS_SUPABASE_DB_URL") 
if not db_url:
    print("❌ No SUPABASE_DB_URL found.")
    exit(1)

safe_url = db_url.split('@')[1] if '@' in db_url else 'DB'
try:
    engine = create_engine(db_url)
    
    # Policies for Public/Anon access (Dev Mode)
    sql = """
    -- 1. Chat Messages
    alter table chat_messages enable row level security;
    create policy "Public Access Messages" on chat_messages 
    for all using (true) with check (true);
    
    -- 2. Chat Sessions
    alter table chat_sessions enable row level security;
    create policy "Public Access Sessions" on chat_sessions 
    for all using (true) with check (true);

    -- 3. Orchestrator Tasks
    alter table orchestrator_tasks enable row level security;
    create policy "Public Access Tasks" on orchestrator_tasks 
    for all using (true) with check (true);
    
    -- Grant usage to postgres/anon just in case
    grant all privileges on table chat_messages to anon;
    grant all privileges on table chat_sessions to anon;
    grant all privileges on table orchestrator_tasks to anon;
    """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
        print("✅ Permissions Fixed: Public Access Enabled.")
        
except Exception as e:
    # If policy exists, it might error, but that's fine for now, we just want to ensure access.
    # We'll print the error to see.
    print(f"Update Result (might be 'already exists'): {e}")
