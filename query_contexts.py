from app.core.database import SessionLocal, AtomicContext, AtomicArtifact

db = SessionLocal()
contexts = db.query(AtomicContext).all()

with open("db_output.txt", "w", encoding="utf-8") as f:
    f.write(f"Total contexts: {len(contexts)}\n")
    f.write("-" * 100 + "\n")
    for c in contexts:
        sid = c.session_id[:8] if c.session_id else "None"
        bid = c.batch_id[:20] if c.batch_id else "None"
        f.write(f"{c.id[:12]:12} | {c.folder_name[:35]:35} | scope={c.scope:8} | session={sid:8} | batch={bid}\n")

    f.write("\n\nArtifacts:\n")
    f.write("-" * 100 + "\n")
    artifacts = db.query(AtomicArtifact).all()
    for a in artifacts:
        f.write(f"{a.filename:25} | context={a.context_id[:12]} | size={len(a.content) if a.content else 0}\n")
db.close()
print("Output written to db_output.txt")

