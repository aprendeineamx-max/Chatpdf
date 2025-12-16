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

            # [NEW] Simple Task Extraction for "Road Map" requests
            # If the user asked for a plan/roadmap, try to extract numbered items as tasks.
            # Heuristic: User query contains "road map" or "roadmap" or "plan"
            if any(k in user_query.lower() for k in ["road map", "roadmap", "plan", "tareas", "todo"]):
                self._extract_and_save_tasks(session_id, ai_response, db)

        except Exception as e:
            logger.error(f"Save Interaction Error: {e}")
        finally:
            db.close()

    def _extract_and_save_tasks(self, session_id: str, text: str, db: SessionLocal):
        import re
        from app.core.database import OrchestratorTask
        
        # Regex for "1. Task Title" or "- Task Title"
        # We'll be generous and capture anything that looks like a list item
        # patterns: 
        #   1. **Title**: Description
        #   1. Title
        #   - **Title**
        
        lines = text.split('\n')
        tasks_found = []
        
        for line in lines:
            line = line.strip()
            # Check for numbered list "1. Task"
            match_num = re.match(r'^\d+\.\s+(.*)', line)
            if match_num:
                tasks_found.append(match_num.group(1))
                continue
                
            # Check for generic bullet "- Task"
            match_bull = re.match(r'^-\s+(.*)', line)
            if match_bull:
                content = match_bull.group(1)
                # Filter out short bullets that might be just conversational
                if len(content) > 5: 
                    tasks_found.append(content)
        
        # Save to DB
        for t_title in tasks_found:
            # Clean formatting (remove ** **)
            clean_title = t_title.replace('**', '').split(':')[0].strip() # Take first part if colon exists
            
            new_task = OrchestratorTask(
                id=str(uuid.uuid4()),
                title=clean_title[:100], # Trucate for title
                description=t_title,     # Full text in description
                status="PENDING",
                evidence={"source_session": session_id}
            )
            db.add(new_task)
        
        if tasks_found:
            db.commit()
            logger.info(f"✅ Auto-extracted {len(tasks_found)} tasks from roadmap.")

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
