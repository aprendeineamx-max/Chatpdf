
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid
import os
from datetime import datetime

from app.core.config import settings
from app.core.database import get_db, ChatMessage, ChatSession, OrchestratorTask
from app.services.hive.hive_mind import HiveMind

# Initialize Router
router = APIRouter(prefix="/api/v1/orchestrator", tags=["orchestrator"])
hive_mind = HiveMind()

# Models
class MessageCreate(BaseModel):
    content: str
    role: str = "user"
    session_id: Optional[str] = None  # [FIX] Accept session_id from frontend
    provider: Optional[str] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    status: str
    assigned_agent: str

# --- LOGIC ---

@router.get("/chat")
def get_chat_history(db: Session = Depends(get_db)):
    if settings.CORE_MODE == "LOCAL":
        # SQLite
        return db.query(ChatMessage).order_by(ChatMessage.created_at.asc()).all()
    else:
        # Cloud (Supabase) - Not implemented here, frontend should query directly or we proxy
        # Proxying is better for "BFF" pattern consistency.
        # For now, let's assume this router replaces the frontend logic purely for LOCAL mode,
        # OR we can make it hybrid.
        # User requested robustness, so let's stick to LOCAL for now as primary if mode is Local.
        return []

@router.post("/chat")
async def send_message(msg: MessageCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if settings.CORE_MODE == "LOCAL":
        # 1. Save User Msg
        # [FIX] Use session_id from frontend, fallback to default
        session_id = msg.session_id if msg.session_id else "default-session"
        
        # Check if session exists
        sess = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not sess:
            sess = ChatSession(id=session_id)
            db.add(sess)
            db.commit()
            
        user_msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=msg.role,
            content=msg.content
        )
        db.add(user_msg)
        db.commit()
        
        # 2. Trigger Response (Background)
        # Note: We don't pass 'db' here, the wrapper creates its own SessionLocal
        background_tasks.add_task(generate_response_local_wrapper, msg.content, session_id, msg.provider)
        
        return {"status": "sent", "id": user_msg.id}
    else:
        raise HTTPException(status_code=501, detail="Cloud mode proxy not implemented yet")

@router.get("/tasks")
def get_tasks(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    if settings.CORE_MODE == "LOCAL":
        if not session_id:
            return []
            
        query = db.query(OrchestratorTask)
        # Filter by session
        query = query.filter(OrchestratorTask.session_id == session_id)
        return query.all()
    return []

# --- BACKGROUND WORKER ---

async def generate_response_local(user_text: str, session_id: str, db: Session):
    try:
        from app.services.agent.architect import architect
        
        # Delegate thinking to the Supreme Architect Service
        await architect.process_request(user_text, session_id, db)
        
    except Exception as e:
        print(f"❌ [Local] Orchestrator Error: {e}")
        # Log error
    finally:
        # Cleanup if needed (DB session is passed in, so let caller or dependency handle it? 
        # Actually 'db' in args is likely from Depends(get_db) which closes automatically if it was a route handler,
        # but here it's a BackgroundTask. BackgroundTasks with Depends can be tricky.
        # Original code opened a NEW SessionLocal(). Let's stick to that pattern inside the service or here.
        # Wait, the previous code passed `db` but then opened `local_db = SessionLocal()`. 
        # The Architect service uses the passed `db`. 
        # We should ensure `generate_response_local` creates a fresh session for background work.
        pass

# [FIX] Background Worker needs its own DB Session life-cycle
async def generate_response_local_wrapper(user_text: str, session_id: str, provider: str = None):
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        from app.services.agent.architect import architect
        await architect.process_request(user_text, session_id, db, provider)
    except Exception as e:
        print(f"❌ [Wrapper] Error: {e}")
    finally:
        db.close()
