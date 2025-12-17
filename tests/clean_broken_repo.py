
import sys
import os
sys.path.append(os.getcwd())
from app.core.database import SessionLocal, AtomicContext

def clean_proxy_tools():
    db = SessionLocal()
    try:
        # Find the specific broken entry
        repo = db.query(AtomicContext).filter(
            AtomicContext.folder_name == "REPO: Proxy-Tools",
            AtomicContext.session_id == None
        ).first()

        if repo:
            print(f"Deleting broken repo: {repo.folder_name} (ID: {repo.id})")
            db.delete(repo)
            db.commit()
            print("✅ Deleted.")
        else:
            print("⚠️ No broken 'Proxy-Tools' entry found (maybe already deleted or session_id is set).")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clean_proxy_tools()
