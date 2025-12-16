
import sys
import os
import uuid

# Add app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal, ChatSession, ChatMessage, engine, Base

def audit_db():
    print("----- DATABASE AUDIT STARTING -----")
    
    # 1. Verify connection
    try:
        connection = engine.connect()
        print("[PASS] Database Connection Established")
        connection.close()
    except Exception as e:
        print(f"[FAIL] Connection Failed: {e}")
        return

    # 2. Verify Schema Creation
    try:
        Base.metadata.create_all(bind=engine)
        print("[PASS] Schema Creation (create_all) Executed")
    except Exception as e:
        print(f"[FAIL] Schema Creation Failed: {e}")
        return

    # 3. Verify Write/Read
    db = SessionLocal()
    try:
        # Create Session
        test_id = str(uuid.uuid4())
        session = ChatSession(id=test_id, title="AUDIT_TEST_SESSION")
        db.add(session)
        db.commit()
        db.refresh(session)
        print(f"[PASS] Created Session ID: {session.id}")
        
        # Verify Persistence
        read_session = db.query(ChatSession).filter(ChatSession.id == test_id).first()
        if read_session and read_session.title == "AUDIT_TEST_SESSION":
            print("[PASS] Persistence Verification: Success")
        else:
            print("[FAIL] Persistence Verification: Session not found or data mismatch")

        # Create Message
        msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=test_id,
            role="user",
            content="AUDIT_TEST_MESSAGE"
        )
        db.add(msg)
        db.commit()
        print("[PASS] Message Inserted")
        
        # Verify Message
        read_msg = db.query(ChatMessage).filter(ChatMessage.session_id == test_id).first()
        if read_msg and read_msg.content == "AUDIT_TEST_MESSAGE":
            print("[PASS] Message Persistence: Success")
        else:
            print("[FAIL] Message Persistence: Failed")
            
    except Exception as e:
        print(f"[FAIL] Transaction Error: {e}")
    finally:
        db.close()
        print("----- DATABASE AUDIT COMPLETE -----")

if __name__ == "__main__":
    audit_db()
