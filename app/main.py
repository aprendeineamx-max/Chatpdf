from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.services.ingestion.processor import PDFProcessor
from app.routers.hive import router as hive_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="API for Advanced PDF RAG System"
)

# CORS Middleware
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Explicit origins for credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
from app.routers.orchestrator import router as orchestrator_router
from app.routers.system import router as system_router
from app.routers.ingest import router as ingest_router

app.include_router(hive_router, prefix="/api/hive", tags=["hive-mind"])
app.include_router(orchestrator_router)
app.include_router(system_router)
app.include_router(ingest_router)

@app.on_event("startup")
async def startup_event():
    if settings.CORE_MODE == "LOCAL":
        from app.core.database import init_db
        init_db()

# Instance Processor
processor = PDFProcessor()


@app.post(f"{settings.API_V1_STR}/ingest")
async def ingest_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Ingest a PDF file.
    Returns a Job ID immediately. Processing happens in background.
    """
    # job_id = str(uuid.uuid4())
    job_id = "all" # MVP: Force single index for Chat UI
    temp_path = f"data/temp/{job_id}.pdf"
    
    # Ensure temp dir exists
    os.makedirs("data/temp", exist_ok=True)
    
    # Save file
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Background Processing
    background_tasks.add_task(process_job, temp_path, job_id)
    
    return {"job_id": job_id, "status": "processing_started"}

def process_job(file_path: str, job_id: str):
    """
    Wrapper to run the synchronous processor in background
    """
    try:
        result = processor.process_pdf(file_path, job_id)
        print(f"Job {job_id} Success: {result['total_pages']} pages processed.")
        # TODO: Here we would trigger the RAG Indexing
    except Exception as e:
        print(f"Job {job_id} Failed: {str(e)}")
    finally:
        # Cleanup temp file
        if os.path.exists(file_path):
            os.remove(file_path)

from pydantic import BaseModel

from typing import Optional

class QueryRequest(BaseModel):
    query_text: str
    pdf_id: str = "all"
    mode: str = "standard" 
    session_id: Optional[str] = None # Persistence
    model: Optional[str] = None # [NEW] Model Override
    repo_context: Optional[str] = None # [NEW] Active Repo from UI

@app.post(f"{settings.API_V1_STR}/query")
async def query_document(request: QueryRequest, background_tasks: BackgroundTasks):
    try:
        from app.services.rag.engine import rag_service
        from app.services.chat.history import chat_history
        
        # 1. Manage Session
        session_id = request.session_id
        if not session_id:
            session_id = chat_history.create_session(title=request.query_text[:30])
        
        # 2. Execute Logic
        
        # [NEW] REAL-TIME FILE SYSTEM ACCESS (Agent Mode)
        # Replaces static DB artifacts with live disk read
        import os
        knowledge_context = ""
        
        base_repos_path = "data/shared_repos"
        # Determine Target Repo
        target_repo = None
        
        if os.path.exists(base_repos_path):
            repos = [d for d in os.listdir(base_repos_path) if os.path.isdir(os.path.join(base_repos_path, d))]
            
            # Strategy 0: Explicit Context from UI (Highest Priority)
            print(f"DEBUG AGENT: Request Context: {request.repo_context}") # DEBUG
            if request.repo_context:
                # Clean up "REPO: " prefix if present or verify existence
                clean_ctx = request.repo_context.replace("REPO: ", "")
                if clean_ctx in repos:
                    target_repo = clean_ctx
                    print(f"DEBUG AGENT: Target Repo set to {target_repo} via Context") # DEBUG

            # Strategy A: Explicit Mention in Query (Override context if explicit?)
            if not target_repo:
                for r in repos:
                    repo_parts = r.lower().replace("-", " ").split()
                    if r.lower() in request.query_text.lower() or any(p in request.query_text.lower() for p in repo_parts if len(p)>3):
                        target_repo = r
                        print(f"DEBUG AGENT: Target Repo set to {target_repo} via Query Heuristic") # DEBUG
                        break
            
            # Strategy B: Implicit Context (If only 1 repo exists, assume it's the target)
            if not target_repo and len(repos) == 1:
                target_repo = repos[0]

            # Strategy D: Default Fallback (If user says 'any repo' or vague)
            if not target_repo and len(repos) > 0:
                print(f"DEBUG AGENT: Defaulting to first repo {repos[0]} as fallback")
                target_repo = repos[0]
                
            # Strategy C: File Hunting (If user asks for specific file, look for it in all repos)
            # This handles "show me metadata.py" without naming the repo
            if not target_repo:
                words = request.query_text.split()
                potential_files = [w for w in words if "." in w and len(w) > 3] # simple heuristic
                for r in repos:
                    # check if any potential file exists in this repo
                    repo_root_check = os.path.join(base_repos_path, r)
                    for pf in potential_files:
                         # simple check if file exists anywhere in repo tree (shallow check first or full walk?)
                         # let's just do a quick assumption or assign the first repo.
                         # Better: Default to the most recently modified repo?
                         # For MVP: Just pick the first repo if we can't decide. User can clarify.
                         target_repo = repos[0] 
                         break
                    if target_repo: break
            
            # 2. Walk and Read
            if target_repo:
                repo_root = os.path.join(base_repos_path, target_repo)
                knowledge_context += f"\n\n--- 🔴 LIVE FILE SYSTEM ACCESS: {target_repo} ---\n"
                knowledge_context += "The user has granted you READ access to the following files. ANSWER ONLY BASED ON THIS CODE. DO NOT HALLUCINATE OR GIVE GENERIC DEFINITIONS.\n"
                
                file_count = 0
                total_chars = 0
                MAX_CHARS = 50000 # Increased for larger reads
                
                for root, dirs, files in os.walk(repo_root):
                    # Exclude noise
                    if ".git" in root or "node_modules" in root or "__pycache__" in root: continue
                    
                    for f in files:
                        if f in ["package-lock.json", ".DS_Store", "yarn.lock"]: continue
                        if f.endswith(".png") or f.endswith(".jpg"): continue
                        
                        file_path = os.path.join(root, f)
                        rel_path = os.path.relpath(file_path, repo_root)
                        
                        # Prioritize the requested file if mentioned
                        is_priority = f.lower() in request.query_text.lower()
                        
                        try:
                            with open(file_path, "r", encoding="utf-8", errors="ignore") as file_obj:
                                content = file_obj.read()
                                
                                # If this is the specific file requested, ensure it gets in!
                                if is_priority:
                                    knowledge_context = f"\n[PRIORITY FILE: {rel_path}]\n```\n{content}\n```\n" + knowledge_context
                                    total_chars += len(content)
                                    file_count += 1
                                    continue

                                if total_chars + len(content) > MAX_CHARS:
                                    knowledge_context += f"\n[FILE: {rel_path}] (Truncated context)\n"
                                    continue
                                    
                                knowledge_context += f"\n[FILE: {rel_path}]\n```\n{content}\n```\n"
                                total_chars += len(content)
                                file_count += 1
                        except Exception as e_read:
                             print(f"Error reading {rel_path}: {e_read}")
                
                print(f"✅ [Live Read] Injected {file_count} files ({total_chars} chars) from {target_repo}")

        # Prepend context to query
        final_query = f"{request.query_text}\n\nCONTEXT:\n{knowledge_context}"
        
        # [NEW] Agentic Prompt Injection (Read + Write)
        final_query += "\n\nINSTRUCCIONES: Eres un Agente de IA autónomo dentro del IDE.\n"
        final_query += "1. LEE el contexto del código de arriba.\n"
        final_query += "2. IDIOMA: Responde SIEMPRE en ESPAÑOL.\n"
        final_query += "3. SI te piden crear/editar un archivo, USA ESTE FORMATO EXACTO:\n"
        final_query += "*** WRITE_FILE: <ruta_relativa_desde_raiz_repo> ***\n"
        final_query += "<contenido_del_codigo>\n"
        final_query += "*** END_WRITE ***\n"
        final_query += "IMPORTANTE: OBEDECE LA RUTA SOLICITADA EXACTAMENTE. Si piden en la raíz, usa 'archivo.txt', NO inventes carpetas (src, docs) si no se piden.\n"
        final_query += "Ejemplo: *** WRITE_FILE: utils/helper.js ***\nconsole.log('hola');\n*** END_WRITE ***\n"

        if request.mode == "swarm":
            response = await rag_service.query_swarm(final_query, request.pdf_id, model=request.model)
        else:
            response = rag_service.query(final_query, request.pdf_id, model=request.model)
            
        # [NEW] AGENTIC ACTION EXECUTOR (Write to Disk)
        # Parse response for Write Blocks
        
        print(f"DEBUG FULL RESPONSE TYPE: {type(response)}") # DEBUG
        print(f"DEBUG FULL RESPONSE CONTENT: {response}") # DEBUG

        # Normalize Response (Handle Dict vs Str)
        response_text = response
        if isinstance(response, dict):
            response_text = response.get("answer", "")
            
        if isinstance(response_text, str) and "*** WRITE_FILE:" in response_text:
            if not target_repo:
                 print("⚠️ AGENT WARNING: Agent tried to write file but no TARGET REPO identified. Write skipped.")
            else:
                try:
                    # Regex to capture path and content (FLEXIBLE WHITESPACE)
                    import re
                    # Handles: "*** WRITE_FILE: path ***", "***WRITE_FILE: path***", newline, content, "*** END_WRITE ***"
                    action_blocks = re.findall(r"\*\*\*\s*WRITE_FILE:\s*(.*?)\s*\*\*\*\n(.*?)\s*(\*\*\*\s*END_WRITE\s*\*\*\*|$)", response_text, re.DOTALL)
                    
                    writes_log = []
                    repo_root = os.path.join(base_repos_path, target_repo)
                    
                    for path_raw, content_raw, _ in action_blocks:
                        rel_path = path_raw.strip()
                        file_content = content_raw.strip()
                        
                        # [FIX] Redundant Path Handling
                        # If agent writes 'repo_name/file.txt', strip 'repo_name/'
                        if target_repo and rel_path.startswith(f"{target_repo}/"):
                            rel_path = rel_path[len(target_repo)+1:]
                            print(f"⚠️ FIXED STRING: Stripped repo name from path -> {rel_path}")

                        # Security Check: Prevent traversal
                        if ".." in rel_path or rel_path.startswith("/"):
                            print(f"⚠️ Security blocked write to: {rel_path}")
                            continue
                            
                        full_path = os.path.join(repo_root, rel_path)
                        
                        # Ensure dir exists
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        
                        with open(full_path, "w", encoding="utf-8") as f_write:
                            f_write.write(file_content)
                        print(f"✅ AGENT WROTE TO: {full_path}")
                        writes_log.append(f"Edited: {rel_path}")
                    
                    # Append action log to response so frontend knows
                    if writes_log:
                        response += f"\n\n⚡ AGENT ACTIONS EXECUTED:\n- " + "\n- ".join(writes_log)
                        
                except Exception as e_action:
                    print(f"Agent Action Failed: {e_action}")

        # 3. Save History (Async)
            
        # 3. Save History (Async)
        if isinstance(response, dict):
            answer_text = response.get("answer", "")
            sources_list = response.get("sources", [])
            
            background_tasks.add_task(
                chat_history.save_interaction,
                session_id,
                request.query_text,
                answer_text,
                sources_list
            )
    
        # 4. Return result with Session ID
        if isinstance(response, dict):
            response["session_id"] = session_id
            
        return response

    except Exception as e:
        import traceback
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
            f.write(f"\nError: {str(e)}")
        print("CRITICAL ERROR LOGGED TO error_log.txt")
        return {"answer": f"Backend Critical Error: {str(e)}", "sources": []}

@app.post(f"{settings.API_V1_STR}/sessions")
def create_session():
    """Create a new empty session"""
    from app.services.chat.history import chat_history
    session_id = chat_history.create_session(title="New Conversation")
    return {"session_id": session_id}

@app.post(f"{settings.API_V1_STR}/sessions/{{session_id}}/clone")
def clone_session_endpoint(session_id: str):
    """Clone an existing session (Time Travel)"""
    from app.services.chat.history import chat_history
    new_session_id = chat_history.clone_session(session_id)
    if not new_session_id:
        return {"error": "Failed to clone session (not found or DB error)"}
    return {"session_id": new_session_id, "status": "cloned"}

@app.delete(f"{settings.API_V1_STR}/sessions/{{session_id}}")
def delete_session_endpoint(session_id: str):
    """Delete a session"""
    from app.services.chat.history import chat_history
    success = chat_history.delete_session(session_id)
    return {"success": success}

@app.get(f"{settings.API_V1_STR}/sessions")
def get_sessions():
    from app.services.chat.history import chat_history
    sessions = chat_history.get_recent_sessions()
    return [{"id": s.id, "title": s.title, "created_at": s.created_at} for s in sessions]

@app.get(f"{settings.API_V1_STR}/sessions/{{session_id}}")
def get_session_history(session_id: str):
    from app.services.chat.history import chat_history
    messages = chat_history.get_session_history(session_id)
    return [{
        "role": m.role, 
        "content": m.content, 
        "sources": m.sources,
        "id": m.id
    } for m in messages]

if __name__ == "__main__":
    import uvicorn
    # Use string reference for reload to work
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
