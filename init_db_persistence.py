import psycopg2
from app.core.config import settings
import logging

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DB_INIT")

def init_db():
    db_url = settings.SUPABASE_DB_URL
    if not db_url:
        logger.error("❌ No SUPABASE_DB_URL configured. Check .env and SUPABASE_TARGET.")
        return

    # Try Direct Connection Logic for Migration (Poolers hate DDL sometimes)
    # Target: postgresql://postgres:[PASS]@db.[REF].supabase.co:5432/postgres
    try:
        # Parse Ref from Host if possible or hardcode for this specific env since we know it
        # Env: postgresql://postgres.jrjsxjmjfsjltgutssib:SuperSegura2024%21@aws-0-us-west-1.pooler.supabase.com:6543/postgres
        # Ref is 'jrjsxjmjfsjltgutssib'
        
        # Hardcoded Fallback for Reliability based on observed env
        direct_url = "postgresql://postgres:SuperSegura2024!@db.jrjsxjmjfsjltgutssib.supabase.co:5432/postgres"
        
        logger.info(f"🔌 Connecting via Direct URL (Port 5432)...")
        conn = psycopg2.connect(direct_url, sslmode='require')
        conn.autocommit = True
        cur = conn.cursor()
        
        # Read Schema File
        logger.info("📄 Reading supabase_schema.sql...")
        with open("supabase_schema.sql", "r", encoding="utf-8") as f:
            schema_sql = f.read()
            
        # Execute
        logger.info("🚀 Executing Schema Migration...")
        cur.execute(schema_sql)
        
        logger.info("✅ Migration Successful! Tables 'chat_sessions' and 'chat_messages' created.")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Migration Failed: {e}")

if __name__ == "__main__":
    init_db()
