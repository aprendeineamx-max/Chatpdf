
import sys
import os
sys.path.append(os.getcwd())
from app.core.database import SessionLocal, AtomicContext

def check_db():
    db = SessionLocal()
    with open("db_debug_output.txt", "w", encoding="utf-8") as f:
        try:
            f.write("--- DB STATE CHECK ---\n")
            repos = db.query(AtomicContext).all()
            found = False
            for r in repos:
                f.write(f"- ID: {r.id}\n  Name: {r.folder_name}\n  Scope: {r.scope}\n  Session: {r.session_id}\n\n")
                if "Proxy-Tools" in str(r.folder_name):
                    found = True
            
            if found:
                f.write("✅ Proxy-Tools IS present.\n")
            else:
                f.write("❌ Proxy-Tools NOT found.\n")

        except Exception as e:
            f.write(f"Error: {e}\n")
        finally:
            db.close()

if __name__ == "__main__":
    check_db()
