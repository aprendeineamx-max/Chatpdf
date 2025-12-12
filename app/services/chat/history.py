import logging
from app.database import SessionLocal, ChatSession, ChatMessage, init_db

logger = logging.getLogger(__name__)

# Ensure Tables Exist
try:
    init_db()
except Exception as e:
    logger.error(f"DB Init Failed: {e}")

class ChatHistoryService:
    def create_session(self, title: str = "New Chat"):
        db = SessionLocal()
        try:
            session = ChatSession(title=title)
            db.add(session)
            db.commit()
            db.refresh(session)
            return session.id
        except Exception as e:
            logger.error(f"Create Session Error: {e}")
            return None
        finally:
            db.close()

    def save_interaction(self, session_id: str, user_query: str, ai_response: str, sources: list):
        if not session_id: return
        db = SessionLocal()
        try:
            # User Message
            user_msg = ChatMessage(session_id=session_id, role="user", content=user_query)
            db.add(user_msg)
            
            # AI Message
            ai_msg = ChatMessage(session_id=session_id, role="assistant", content=ai_response, sources=sources)
            db.add(ai_msg)
            
            db.commit()
            logger.info(f"Saved interaction to Session {session_id}")
        except Exception as e:
            logger.error(f"Save History Error: {e}")
        finally:
            db.close()

    def get_session_history(self, session_id: str):
        db = SessionLocal()
        try:
            msgs = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at).all()
            return msgs
        finally:
            db.close()

    def get_recent_sessions(self, limit: int = 20):
        db = SessionLocal()
        try:
            sessions = db.query(ChatSession).order_by(ChatSession.created_at.desc()).limit(limit).all()
            return sessions
        except Exception as e:
            logger.error(f"Get Sessions Error: {e}")
            return []
        finally:
            db.close()

chat_history = ChatHistoryService()
