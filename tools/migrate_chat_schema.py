
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
print(f"🔌 Connecting to: ...@{safe_url}")

try:
    engine = create_engine(db_url)
    
    sql = """
    -- 1. Chat Sessions
    create table if not exists chat_sessions (
      id uuid primary key default gen_random_uuid(),
      user_id uuid,
      title text default 'New Conversation',
      created_at timestamptz default now(),
      updated_at timestamptz default now()
    );

    -- 2. Chat Messages
    create table if not exists chat_messages (
      id uuid primary key default gen_random_uuid(),
      session_id uuid references chat_sessions(id) on delete cascade,
      role text not null check (role in ('user', 'assistant', 'system')),
      content text not null,
      sources jsonb default '[]'::jsonb,
      created_at timestamptz default now()
    );
    
    -- Index
    create index if not exists idx_messages_session_id on chat_messages(session_id);
    """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
        print("✅ Migration Applied: Chat Tables created.")
        
except Exception as e:
    print(f"❌ Migration Failed: {e}")
