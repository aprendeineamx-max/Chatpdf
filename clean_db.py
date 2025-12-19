"""
Clean database of ALL atomic contexts and artifacts
This gives us a fresh environment to test session isolation
"""
from app.core.database import SessionLocal, AtomicContext, AtomicArtifact

db = SessionLocal()
try:
    # Delete all artifacts first (foreign key constraint)
    artifacts_deleted = db.query(AtomicArtifact).delete()
    print(f"Deleted {artifacts_deleted} artifacts")
    
    # Delete all contexts
    contexts_deleted = db.query(AtomicContext).delete()
    print(f"Deleted {contexts_deleted} contexts")
    
    db.commit()
    print("\n✅ Database cleaned successfully!")
    print("Now you can test with fresh sessions.")
except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
finally:
    db.close()
