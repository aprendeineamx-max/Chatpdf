
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
        session_id = "default-session" # simplified for single user
        
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
        background_tasks.add_task(generate_response_local, msg.content, session_id, db)
        
        return {"status": "sent", "id": user_msg.id}
    else:
        raise HTTPException(status_code=501, detail="Cloud mode proxy not implemented yet")

@router.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    if settings.CORE_MODE == "LOCAL":
        return db.query(OrchestratorTask).all()
    return []

# --- BACKGROUND WORKER ---

async def generate_response_local(user_text: str, session_id: str, db: Session):
    # This function needs its own session if async? 
    # Actually, background tasks run in threadpool, so standard blocking session is risky if not scoped.
    # We'll re-create session for safety or use the passed one CAREFULLY (not recommended if request closes).
    # Better: New session.
    from app.core.database import SessionLocal
    local_db = SessionLocal()
    
    try:
        print(f"🧠 [Local] Thinking about: {user_text}")
        context = f"User: {user_text}\nRole: Supreme Architect. Guide the user."
        
        # Call LLM (HiveMind uses API Keys which are separate from DB keys, so this works!)
        # The LLM key (Google/Groq) works even if Supabase is dead.
        response_text = await hive_mind._generate_response("ARCHITECT", context)
        
        # Save Agent Response
        agent_msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role="assistant",
            content=response_text
        )
        local_db.add(agent_msg)
        local_db.commit()
        print("✅ [Local] Replied.")
        
    except Exception as e:
        print(f"❌ [Local] Error: {e}")
    finally:
        local_db.close()
