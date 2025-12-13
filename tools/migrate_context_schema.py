
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add root to path
sys.path.append(os.getcwd())

from app.core.config import settings

def run_migration():
    db_url = settings.SUPABASE_DB_URL
    if not db_url:
        print("Error: SUPABASE_DB_URL not found in settings.")
        return

    print(f"Connecting to DB...")
    engine = create_engine(db_url)
    
    statements = [
        "ALTER TABLE atomic_contexts ADD COLUMN IF NOT EXISTS type text DEFAULT 'ingestion';",
        "ALTER TABLE atomic_contexts ADD COLUMN IF NOT EXISTS content text;",
        "ALTER TABLE atomic_contexts ADD COLUMN IF NOT EXISTS metadata jsonb DEFAULT '{}'::jsonb;",
        "ALTER TABLE atomic_contexts ALTER COLUMN folder_name DROP NOT NULL;"
    ]

    with engine.connect() as conn:
        for sql in statements:
            try:
                print(f"Executing: {sql}")
                conn.execute(text(sql))
                conn.commit()
                print("Success.")
            except Exception as e:
                print(f"Error executing {sql}: {e}")
                # Continue if error (e.g. column exists)

if __name__ == "__main__":
    run_migration()
