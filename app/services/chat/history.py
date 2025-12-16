import logging
import uuid
# Use the CORE database to share state with Ingestion/Tasks
from app.core.database import SessionLocal, ChatSession, ChatMessage 

logger = logging.getLogger(__name__)

class ChatHistoryService:
    def create_session(self, title: str = "New Chat"):
        db = SessionLocal()
        try:
            # Explicitly generate ID to ensure compatibility with core models
            session_id = str(uuid.uuid4())
            session = ChatSession(id=session_id, title=title)
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
            # User Msg
            user_msg = ChatMessage(
                id=str(uuid.uuid4()),
                session_id=session_id, 
                role="user", 
                content=user_query,
                sources=[]
            )
            db.add(user_msg)
            
            # AI Msg
            ai_msg = ChatMessage(
                id=str(uuid.uuid4()),
                session_id=session_id, 
                role="assistant", 
                content=ai_response, 
                sources=sources
            )
            db.add(ai_msg)
            
            db.commit()
        except Exception as e:
            logger.error(f"Save Interaction Error: {e}")
        finally:
            db.close()

    def get_session_history(self, session_id: str):
        db = SessionLocal()
        try:
            messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at).all()
            return messages
        except Exception as e:
            logger.error(f"Get History Error: {e}")
            return []
        finally:
            db.close()

    def get_recent_sessions(self, limit: int = 50):
        db = SessionLocal()
        try:
            sessions = db.query(ChatSession).order_by(ChatSession.created_at.desc()).limit(limit).all()
            return sessions
        except Exception as e:
            logger.error(f"Get Sessions Error: {e}")
            return []
        finally:
            db.close()

    def clone_session(self, original_session_id: str):
        db = SessionLocal()
        try:
            original = db.query(ChatSession).filter(ChatSession.id == original_session_id).first()
            if not original: return None
            
            # Create Copy
            new_id = str(uuid.uuid4())
            new_session = ChatSession(id=new_id, title=f"Copy of {original.title}")
            db.add(new_session)
            
            # Copy Messages
            original_msgs = db.query(ChatMessage).filter(ChatMessage.session_id == original_session_id).all()
            for msg in original_msgs:
                new_msg = ChatMessage(
                    id=str(uuid.uuid4()),
                    session_id=new_id,
                    role=msg.role,
                    content=msg.content,
                    sources=msg.sources
                )
                db.add(new_msg)
            
            db.commit()
            return new_id
        except Exception as e:
            logger.error(f"Clone Error: {e}")
            return None
        finally:
            db.close()

    def delete_session(self, session_id: str):
        db = SessionLocal()
        try:
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if session:
                db.delete(session)
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Delete Error: {e}")
            return False
        finally:
            db.close()

chat_history = ChatHistoryService()
