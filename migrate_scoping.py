import sqlite3
import os

DB_PATH = "data/db/local_core.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Update OrchestratorTasks (Roadmap)
        print("Migrating orchestrator_tasks...")
        cursor.execute("PRAGMA table_info(orchestrator_tasks)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "session_id" not in columns:
            cursor.execute("ALTER TABLE orchestrator_tasks ADD COLUMN session_id TEXT")
            print("✅ Added 'session_id' to orchestrator_tasks")
        else:
            print("ℹ️ 'session_id' already exists in orchestrator_tasks")

        # 2. Update AtomicContext (Ingested Repos)
        print("Migrating atomic_contexts...")
        cursor.execute("PRAGMA table_info(atomic_contexts)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "session_id" not in columns:
            cursor.execute("ALTER TABLE atomic_contexts ADD COLUMN session_id TEXT")
            print("✅ Added 'session_id' to atomic_contexts")
        
        if "scope" not in columns:
            cursor.execute("ALTER TABLE atomic_contexts ADD COLUMN scope TEXT DEFAULT 'global'")
            print("✅ Added 'scope' to atomic_contexts")
            
            # Set default scope to 'global' for existing records
            cursor.execute("UPDATE atomic_contexts SET scope = 'global' WHERE scope IS NULL")

        conn.commit()
        print("🎉 Migration Complete!")

    except Exception as e:
        print(f"❌ Migration Failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
