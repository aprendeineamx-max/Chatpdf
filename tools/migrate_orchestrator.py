
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv(".env")
load_dotenv("genesis-web/.env")

# Try to find the DB URL
db_url = os.getenv("SUPABASE_DB_URL") or os.getenv("VPS_SUPABASE_DB_URL") 

if not db_url:
    # Fallback: Maybe construct it if we have host/user/pass? 
    # But usually it's in the .env as a full string for Prisma/SQLAlchemy
    print("❌ No SUPABASE_DB_URL found in .env")
    exit(1)

# Mask password for printing
safe_url = db_url.split('@')[1] if '@' in db_url else 'DB'
print(f"🔌 Connecting to: ...@{safe_url}")

try:
    engine = create_engine(db_url)
    
    sql = """
    create table if not exists orchestrator_tasks (
      id uuid primary key default gen_random_uuid(),
      title text not null,
      description text,
      status text default 'PENDING', -- PENDING, IN_PROGRESS, DONE, FAILED
      priority text default 'MEDIUM', -- LOW, MEDIUM, HIGH
      assigned_agent text default 'auto', -- 'auto', 'coder', 'architect'
      evidence jsonb default '{}'::jsonb, -- Links to created files/proof
      created_at timestamptz default now(),
      updated_at timestamptz default now()
    );
    """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
        print("✅ Migration Applied: 'orchestrator_tasks' table created.")
        
except Exception as e:
    print(f"❌ Migration Failed: {e}")
