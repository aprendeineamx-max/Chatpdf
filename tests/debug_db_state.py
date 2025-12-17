
import sys
import os
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, AtomicContext

def check_db():
    db = SessionLocal()
    try:
        print("Checking for Proxy-Tools...")
        repos = db.query(AtomicContext).all()
        found = False
        for r in repos:
            if "Proxy-Tools" in str(r.folder_name):
                print(f"✅ FOUND: ID={r.id}, Name={r.folder_name}, Scope={r.scope}, SessionID={r.session_id}")
                found = True
        
        if not found:
            print("❌ Proxy-Tools NOT found in AtomicContext.")
            
        print("\nAll Contexts:")
        for r in repos:
             print(f"- {r.folder_name} ({r.scope}) Session: {r.session_id}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
