
import sys
import os
sys.path.append(os.getcwd())
from app.core.database import SessionLocal, AtomicContext

def clean_global():
    db = SessionLocal()
    try:
        repos_to_delete = ["REPO: crawlbase-node", "REPO: crawlbase-mcp"]
        
        for r_name in repos_to_delete:
            repo = db.query(AtomicContext).filter(AtomicContext.folder_name == r_name).first()
            if repo:
                print(f"Deleting global repo: {repo.folder_name} (ID: {repo.id})")
                db.delete(repo)
        
        db.commit()
        print("✅ Global repos cleaned.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clean_global()
