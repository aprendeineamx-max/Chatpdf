import os
import psycopg2
from app.core.config import settings

def setup_database():
    print("🚀 Initializing Database Setup...")
    
    # Force load from env just in case config cache is stale for this script
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    db_url = os.getenv("CLOUD_SUPABASE_DB_URL")
    if not db_url:
        print("❌ Error: CLOUD_SUPABASE_DB_URL not found in .env")
        return

    print(f"🔌 Connecting to: {db_url.split('@')[-1]}") # Hide auth info
    
    sql_file = "supabase_schema.sql"
    with open(sql_file, "r") as f:
        sql_commands = f.read()

    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("💾 Executing SQL Schema...")
        cur.execute(sql_commands)
        
        print("✅ Database Setup Complete! 'pdf_cortex_vectors' table ready.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Database execution failed: {e}")

if __name__ == "__main__":
    setup_database()
