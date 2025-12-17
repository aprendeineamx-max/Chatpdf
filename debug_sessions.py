from app.core.database import SessionLocal, ChatSession, ChatMessage

db = SessionLocal()
try:
    sessions = db.query(ChatSession).all()
    print(f"Found {len(sessions)} sessions.")
    for s in sessions:
        print(f" - {s.id}: {s.title} ({len(s.messages)} messages)")
        
    if len(sessions) == 0:
        print("!! NO SESSIONS FOUND !!")
        
        # Check if table exists
        from sqlalchemy import inspect
        inspector = inspect(db.get_bind())
        print("Tables:", inspector.get_table_names())
        
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
