
import os
import sys
import time
from sqlalchemy import create_engine, text

# Add root
sys.path.append(os.getcwd())

# LOCAL DB CONFIG
DB_URL = "postgresql://postgres:postgres@localhost:54322/postgres"

def wait_for_db():
    print("⏳ Waiting for Local DB (Port 54322)...")
    for i in range(30):
        try:
            engine = create_engine(DB_URL)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ DB Connection Established!")
            return True
        except Exception:
            time.sleep(1)
            print(".", end="", flush=True)
    return False

def init_db():
    if not wait_for_db():
        print("❌ Could not connect to Local DB. Is Docker running?")
        exit(1)
        
    engine = create_engine(DB_URL)
    
    # 1. Apply Roles (Idempotent)
    print("\n--- Applying Roles ---")
    try:
        with open("data/init/00_roles.sql", "r") as f:
            sql = f.read()
        # Create connection with isolation level autocommit for roles if needed? No, roles are transactional in Postgres usually.
        with engine.connect() as conn:
            # simple split by semicolon
            stmts = sql.split(';')
            for stmt in stmts:
                if stmt.strip():
                    try:
                        conn.execute(text(stmt))
                        conn.commit()
                    except Exception as e:
                        print(f"⚠️ Role/Grant exists or error: {e}")
    except Exception as e:
        print(f"❌ Failed to apply roles: {e}")

    # 2. Apply Schema
    print("\n--- Applying Schema ---")
    try:
        with open("supabase_schema.sql", "r") as f:
            full_sql = f.read()
            
        # We need to run the [RLS POLICIES] blocks correctly.
        # But `supabase_schema.sql` has `do $$` blocks which split() breaks if we naively split by `;`.
        # For Local Dev, we can try to run the whole thing or careful split.
        # Let's try running specific creation statements.
        # Actually, let's use the same logic as `fix_final.py` for RLS, but for tables we need the big file.
        
        # Naive split works for `create table`, fails on `do $$`.
        # Simplified approach: Use `psql` via subprocess if available? No guarentee.
        # We will iterate and try to execute.
        
        with engine.connect() as conn:
            # This is risky but standard for dev scripts without migration tool.
            # Splitting by double newline is often safer for blocks.
            blocks = full_sql.split('\n\n')
            for block in blocks:
                if block.strip() and not block.strip().startswith('--'):
                    try:
                        conn.execute(text(block))
                        conn.commit()
                    except Exception as e:
                        # Ignore "already exists"
                        if "already exists" not in str(e):
                            print(f"⚠️ Block error: {str(e)[:100]}")
                            
        print("✅ Schema Applied (Best Effort).")
        
    except Exception as e:
        print(f"❌ Schema Failed: {e}")

if __name__ == "__main__":
    init_db()
