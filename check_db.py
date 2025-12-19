"""Check database for ingested content"""
from app.core.database import SessionLocal, AtomicContext, AtomicArtifact

db = SessionLocal()
try:
    contexts = db.query(AtomicContext).all()
    print(f"\n=== CONTEXTS ({len(contexts)}) ===")
    for ctx in contexts:
        print(f"  - {ctx.id[:8]}... | {ctx.folder_name} | scope={ctx.scope} | session={ctx.session_id}")
    
    artifacts = db.query(AtomicArtifact).all()
    print(f"\n=== ARTIFACTS ({len(artifacts)}) ===")
    for art in artifacts:
        content_len = len(art.content) if art.content else 0
        print(f"  - {art.artifact_type} | {content_len} chars | context={art.atomic_context_id[:8]}...")
    
    # Check ChromaDB collections
    from app.services.knowledge.vector_store import vector_store
    collections = vector_store.list_collections()
    print(f"\n=== VECTOR STORE COLLECTIONS ({len(collections)}) ===")
    for col in collections:
        print(f"  - {col}")

finally:
    db.close()
