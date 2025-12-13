
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

print(f"🔌 Applying Schema Forcefully to DB...")

try:
    engine = create_engine(db_url)
    
    sql_commands = [
        "alter table chat_sessions enable row level security",
        "alter table chat_messages enable row level security",
        "alter table orchestrator_tasks enable row level security",
        """
        do $$ begin
          create policy "Public Access Sessions" on chat_sessions for all using (true) with check (true);
        exception when duplicate_object then null; end $$;
        """,
        """
        do $$ begin
          create policy "Public Access Messages" on chat_messages for all using (true) with check (true);
        exception when duplicate_object then null; end $$;
        """,
        """
        do $$ begin
          create policy "Public Access Tasks" on orchestrator_tasks for all using (true) with check (true);
        exception when duplicate_object then null; end $$;
        """
    ]

    with engine.connect() as conn:
        for cmd in sql_commands:
            try:
                conn.execute(text(cmd))
                conn.commit()
                print(f"✅ Executed: {cmd[:40]}...")
            except Exception as e:
                print(f"⚠️ Failed: {cmd[:20]}... {e}")
                
        print("✅ RLS Policies Applied.")
        
except Exception as e:
    print(f"❌ Application Failed: {e}")
