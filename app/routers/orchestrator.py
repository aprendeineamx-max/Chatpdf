
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
def get_tasks(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    if settings.CORE_MODE == "LOCAL":
        query = db.query(OrchestratorTask)
        if session_id:
            # Filter by session
            query = query.filter(OrchestratorTask.session_id == session_id)
        return query.all()
    return []

# --- BACKGROUND WORKER ---

async def generate_response_local(user_text: str, session_id: str, db: Session):
    debug_path = r"C:\Users\Administrator\Desktop\Universal Pdf\pdf-cortex\debug_rag_context.txt"
    try:
        with open(debug_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n--- NEW REQUEST: {user_text} ---\n")
            
        from app.core.database import SessionLocal, AtomicArtifact
        from app.services.chat.history import history_service
        local_db = SessionLocal()
        
        print(f"🧠 [Local] Thinking about: {user_text}")
        
        # 1. RAG Retrieval (Simple Injection of Repo Summaries)
        artifacts = local_db.query(AtomicArtifact).filter(AtomicArtifact.filename == "file_structure.tree").all()
        
        with open(debug_path, "a", encoding="utf-8") as f:
            f.write(f"Found {len(artifacts)} artifacts.\n")

        knowledge_context = ""
        if artifacts:
            knowledge_context += "\n\nAVAILABLE REPOSITORIES:\n"
            for art in artifacts:
                # Robust path handling for Windows/Linux strings
                path = art.local_path.replace("\\", "/") # Normalize to forward slashes
                repo_name = path.split("/")[-1]
                
                with open(debug_path, "a", encoding="utf-8") as f:
                     f.write(f"Injecting {repo_name}\n")
                
                knowledge_context += f"--- REPOSITORY: {repo_name} ---\nStructure Root:\n{art.content[:4000]}\n" # Increased limit

        # Also try to fetch summaries if query mentions "repo" or "code"
        if "repo" in user_text.lower() or "code" in user_text.lower() or "access" in user_text.lower():
             pass

        # [NEW] Inject Session Roadmap
        existing_tasks = local_db.query(OrchestratorTask).filter(OrchestratorTask.session_id == session_id).all()
        if existing_tasks:
            task_list_str = "\n".join([f"- [{t.status}] {t.title}" for t in existing_tasks])
            knowledge_context += f"\nCURRENT ROADMAP (Use this context):\n{task_list_str}\n"

        context = f"User: {user_text}\nRole: Supreme Architect. Guide the user.\n{knowledge_context}"
        
        with open(debug_path, "a", encoding="utf-8") as f:
             f.write("FULL CONTEXT:\n" + context + "\n----------------\n")
        
        # Call LLM
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
        
        # 2. Extract Tasks (Roadmap)
        if "road map" in user_text.lower() or "roadmap" in user_text.lower() or "plan" in user_text.lower():
            try:
                # Direct extraction to ensure it works
                import re
                from app.core.database import OrchestratorTask
                
                tasks = []
                # numbered lists 1. Task
                matches = re.findall(r'^\d+\.\s+(.*)', response_text, re.MULTILINE)
                tasks.extend(matches)
                # bullet points - Task
                matches_bullets = re.findall(r'^-\s+(.*)', response_text, re.MULTILINE)
                tasks.extend(matches_bullets)
                
                for t_title in tasks:
                    clean_title = t_title.strip("**").strip()
                    if len(clean_title) > 3:
                        task = OrchestratorTask(
                            id=str(uuid.uuid4()),
                            title=clean_title,
                            status="PENDING",
                            assigned_agent="ARCHITECT",
                            session_id=session_id # [NEW] Link to session
                        )
                        local_db.add(task)
                local_db.commit()
                print(f"✅ [Local] Extracted {len(tasks)} tasks.")
            except Exception as e_task:
                print(f"⚠️ Task Extraction Error: {e_task}")

        print("✅ [Local] Replied.")
        
    except Exception as e:
        print(f"❌ [Local] Error: {e}")
        try:
             with open(debug_path, "a", encoding="utf-8") as f:
                 f.write(f"CRITICAL ERROR: {e}\n")
        except: pass
    finally:
        try: local_db.close()
        except: pass
