import sys
import os
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, AtomicContext

def clean_repos():
    db = SessionLocal()
    try:
        repos_to_delete = ["crawlbase-node", "crawlbase-mcp", "repo-a", "repo-b", "Hello-World"]
        deleted_count = 0
        for name in repos_to_delete:
            # Match folder_name usually derived from repo name
            query = db.query(AtomicContext).filter(AtomicContext.folder_name == name)
            contexts = query.all()
            for ctx in contexts:
                db.delete(ctx)
                deleted_count += 1
        
        db.commit()
        print(f"✅ Deleted {deleted_count} contexts.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clean_repos()
