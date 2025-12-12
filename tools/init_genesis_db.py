import os
import sys
# Add project root to sys.path to allow 'from app...' imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlalchemy
from app.core.config import settings
from sqlalchemy import text

def init_genesis_db():
    print("🌋 Initializing Genesis Database (Liquid Memory)...")
    
    # Force connection string to use postgresql:// if needed, or rely on settings
    # Assuming settings.SUPABASE_DB_URL is correctly set for direct connection
    db_url = settings.SUPABASE_DB_URL
    if not db_url:
        print("❌ Error: SUPABASE_DB_URL is not set.")
        return
        
    print(f"   Connecting to: {db_url.split('@')[-1]}") # Hide auth details
    
    try:
        engine = sqlalchemy.create_engine(db_url)
        with engine.connect() as conn:
            # Read schema file
            with open("supabase_schema.sql", "r") as f:
                schema_sql = f.read()
            
            # Split by statement (rough split by ;) or execute as one block if supported
            # Verify if sending whole block works
            print("   Applying Schema...")
            
            # Simple dirty split
            statements = schema_sql.split(';')
            for stmt in statements:
                if stmt.strip():
                    conn.execute(text(stmt))
                    conn.commit()
                    
            print("✅ Genesis Database Initialized Successfully!")
            
    except Exception as e:
        print(f"❌ Database Initialization Failed: {e}")

if __name__ == "__main__":
    init_genesis_db()
