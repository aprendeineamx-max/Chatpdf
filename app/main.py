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
    rag_mode: str = "injection"  # NEW: "injection" or "semantic"

# ============================================================
# PHASE 2: Intelligent Page Query Detection Functions
# ============================================================
import re

def extract_page_query(query_text: str) -> int | None:
    """Detects if user is asking for a specific page number."""
    patterns = [
        r'página\s*(\d+)',
        r'pagina\s*(\d+)', 
        r'page\s*(\d+)',
        r'pag\.?\s*(\d+)',
        r'p\.?\s*(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, query_text.lower())
        if match:
            return int(match.group(1))
    return None

def extract_page_content(full_content: str, page_num: int, page_mapping: dict = None) -> str | None:
    """
    Extracts specific page content using page markers.
    Handles PDF page numbering offset by trying multiple strategies:
    0. Use page_mapping if available (maps physical page -> PyMuPDF index)
    1. Exact page number
    2. Page number +/- 1-2 (for minor offset)
    3. Wide search for printed page number (±60 pages for major offset)
    """
    
    def try_extract(pn: int) -> str | None:
        patterns = [
            rf'--- PAGE {pn}(?: \(PHYSICAL: \d+\))? ---\n(.*?)(?=--- PAGE \d+ ---|$)',
            rf'--- PAGE {pn} ---\n(.*?)(?=--- PAGE \d+ ---|$)',
            rf'=== PÁGINA {pn} \|.*?===\n+(.*?)(?====+ PÁGINA \d+ ===|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, full_content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    # Strategy 0: Use page mapping if available (highest priority)
    if page_mapping:
        # page_mapping keys might be strings (from JSON) - convert
        str_key = str(page_num)
        if str_key in page_mapping:
            actual_index = page_mapping[str_key]
            result = try_extract(int(actual_index))
            if result:
                print(f"📄 [Page Mapping] Physical page {page_num} → PyMuPDF index {actual_index}")
                return result
        # Also try int key
        if page_num in page_mapping:
            actual_index = page_mapping[page_num]
            result = try_extract(int(actual_index))
            if result:
                print(f"📄 [Page Mapping] Physical page {page_num} → PyMuPDF index {actual_index}")
                return result
    
    # Strategy 1: Try exact page number
    result = try_extract(page_num)
    if result:
        print(f"📄 [Page Search] Found page {page_num} with exact match")
        return result
    
    # Strategy 2: Try with small offset +/-1, +/-2
    for offset in [1, -1, 2, -2]:
        result = try_extract(page_num + offset)
        if result:
            print(f"📄 [Page Search] Found page {page_num} using offset {offset:+d}")
            return result
    
    # Strategy 3: Wide search - look for page where physical number appears at end
    for pn in range(max(1, page_num - 60), min(500, page_num + 60)):
        content = try_extract(pn)
        if content:
            last_30 = content[-30:].strip()
            if re.search(rf'\b{page_num}\s*$', last_30):
                print(f"📄 [Page Search] Found physical page {page_num} at end of PAGE {pn}")
                return content
            first_30 = content[:30].strip()
            if re.search(rf'^\s*{page_num}\b', first_30):
                print(f"📄 [Page Search] Found physical page {page_num} at start of PAGE {pn}")
                return content
    
    print(f"⚠️ [Page Search] Could not find page {page_num}")
    return None

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
        
        # [FIX] SESSION-ISOLATED KNOWLEDGE CONTEXT
        # Only include repos and PDFs that belong to THIS session
        # No global scope, no cross-session contamination
        from app.core.database import SessionLocal, AtomicContext, AtomicArtifact
        db = SessionLocal()
        
        knowledge_context = ""
        target_repo = None
        rag_mode_used = request.rag_mode  # Track actual mode used (may change on fallback)
        
        try:
            # Find contexts ONLY for this session (not global - each chat is isolated)
            session_contexts = db.query(AtomicContext).filter(
                AtomicContext.session_id == session_id
            ).all()
            
            session_context_ids = [c.id for c in session_contexts]
            session_repo_names = [c.folder_name.replace("REPO: ", "") for c in session_contexts 
                                  if c.batch_id == "REPO_INGESTION"]
            
            # A. Inject REPO context only if this session has repos
            if session_repo_names:
                from app.services.knowledge.realtime import realtime_knowledge
                
                # Only use explicit repo context if it belongs to this session
                explicit_repo = request.repo_context
                if explicit_repo:
                    explicit_clean = explicit_repo.replace("REPO: ", "")
                    if explicit_clean not in session_repo_names:
                        explicit_repo = None  # Don't use repos from other sessions
                
                # Get file context only for session repos
                if explicit_repo or len(session_repo_names) == 1:
                    repo_to_use = explicit_repo if explicit_repo else f"REPO: {session_repo_names[0]}"
                    knowledge_context, target_repo = realtime_knowledge.get_file_context(
                        request.query_text, repo_to_use
                    )
            
            # B. Inject PDF context for session-specific PDFs
            if session_context_ids:
                pdf_artifacts = db.query(AtomicArtifact).filter(
                    AtomicArtifact.filename.in_(["pdf_content.txt", "pdf_summary.txt"]),
                    AtomicArtifact.context_id.in_(session_context_ids)
                ).all()
                
                if pdf_artifacts:
                    knowledge_context += "\n\n=== DOCUMENTOS PDF DE ESTA CONVERSACIÓN ===\n"
                    
                    # Track which mode was actually used (for frontend indicator)
                    rag_mode_used = request.rag_mode
                    
                    # DUAL-MODE RETRIEVAL WITH AUTO-FALLBACK
                    if request.rag_mode == "semantic":
                        # SEMANTIC RAG: Retrieve relevant chunks
                        semantic_success = False
                        
                        # [PHASE 2] For page-specific queries in semantic mode, 
                        # first inject the exact page content
                        requested_page = extract_page_query(request.query_text)
                        if requested_page:
                            for art in pdf_artifacts:
                                if art.filename == "pdf_content.txt":
                                    page_content = extract_page_content(art.content, requested_page)
                                    if page_content:
                                        knowledge_context += f"\n\n{'='*60}\n"
                                        knowledge_context += f"===== CONTENIDO EXACTO DE LA PÁGINA {requested_page} =====\n"
                                        knowledge_context += f"{'='*60}\n\n"
                                        knowledge_context += page_content
                                        knowledge_context += f"\n\n{'='*60}\n"
                                        knowledge_context += f"===== FIN DE LA PÁGINA {requested_page} =====\n"
                                        knowledge_context += f"{'='*60}\n\n"
                                        print(f"📄 [Semantic + Page Query] Injected specific content for page {requested_page}")
                        
                        try:
                            from app.services.knowledge.vector_store import vector_store
                            
                            all_chunks = []
                            for ctx_id in session_context_ids:
                                relevant_chunks = vector_store.search(
                                    doc_id=ctx_id,
                                    query=request.query_text,
                                    top_k=25  # [FIX] Increased from 10 to 25 for better coverage
                                )
                                all_chunks.extend(relevant_chunks)
                            
                            if all_chunks:
                                knowledge_context += f"--- FRAGMENTOS RELEVANTES (Semantic RAG - {len(all_chunks)} chunks) ---\n"
                                knowledge_context += "\n---\n".join(all_chunks)
                                knowledge_context += "\n\n"
                                print(f"🔍 [Semantic RAG] Injected {len(all_chunks)} relevant chunks")
                                semantic_success = True
                            else:
                                print(f"⚠️ [Semantic RAG] No chunks found, falling back to injection")
                                
                        except Exception as sem_err:
                            print(f"⚠️ [Semantic RAG] Error: {sem_err}, falling back to injection")
                        
                        # AUTO-FALLBACK: If semantic fails or returns nothing, use injection
                        if not semantic_success:
                            rag_mode_used = "injection (fallback)"
                            for art in pdf_artifacts:
                                if art.filename == "pdf_content.txt":
                                    content = art.content[:200000] if len(art.content) > 200000 else art.content
                                    knowledge_context += f"--- CONTENIDO DEL PDF (Fallback Injection) ---\n{content}\n\n"
                                    print(f"💉 [Fallback] Injected {len(content)} chars via injection fallback")
                    
                    else:
                        # DIRECT INJECTION: Full content (default behavior)
                        rag_mode_used = "injection"
                        
                        # [PHASE 2] Detect if asking for specific page
                        requested_page = extract_page_query(request.query_text)
                        page_content_found = False
                        
                        # Load page mapping if available
                        page_mapping = None
                        for art in pdf_artifacts:
                            if art.filename == "page_mapping.json":
                                try:
                                    import json
                                    page_mapping = json.loads(art.content)
                                    print(f"📄 [Page Mapping] Loaded mapping with {len(page_mapping)} entries")
                                except:
                                    pass
                        
                        for art in pdf_artifacts:
                            if art.filename == "pdf_summary.txt":
                                knowledge_context += f"--- RESUMEN DEL PDF ---\n{art.content}\n\n"
                            elif art.filename == "pdf_content.txt":
                                # [PHASE 2] If asking for specific page, extract and inject it FIRST
                                if requested_page:
                                    page_content = extract_page_content(art.content, requested_page, page_mapping)
                                    if page_content:
                                        knowledge_context += f"\n\n{'='*60}\n"
                                        knowledge_context += f"===== CONTENIDO EXACTO DE LA PÁGINA {requested_page} =====\n"
                                        knowledge_context += f"{'='*60}\n\n"
                                        knowledge_context += page_content
                                        knowledge_context += f"\n\n{'='*60}\n"
                                        knowledge_context += f"===== FIN DE LA PÁGINA {requested_page} =====\n"
                                        knowledge_context += f"{'='*60}\n\n"
                                        page_content_found = True
                                        print(f"📄 [Page Query] Injected specific content for page {requested_page}")
                                
                                # Inject full context (up to 200k chars)
                                content_to_inject = art.content[:200000] if len(art.content) > 200000 else art.content
                                knowledge_context += f"--- CONTENIDO COMPLETO DEL PDF ({len(art.content)} chars) ---\n{content_to_inject}\n\n"
        finally:
            db.close()
        
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
        
        # [PHASE 1] INSTRUCCIONES CRÍTICAS PARA DOCUMENTOS PDF
        final_query += "\n\n" + "="*60 + "\n"
        final_query += "=== INSTRUCCIONES CRÍTICAS PARA DOCUMENTOS PDF ===\n"
        final_query += "="*60 + "\n"
        final_query += "PARA PREGUNTAS SOBRE PÁGINAS ESPECÍFICAS (ej: 'página 79'):\n\n"
        final_query += "1. BUSCA el número de página FÍSICA en el texto completo.\n"
        final_query += "   - Los números de página impresos aparecen en el texto como '78', '79', '80', etc.\n"
        final_query += "   - Generalmente aparecen AL FINAL de cada bloque de página, antes del siguiente contenido.\n"
        final_query += "   - Patron típico: 'UNIDAD X\\n78' indica fin de página 78.\n\n"
        final_query += "2. Para encontrar la PÁGINA 79 del libro:\n"
        final_query += "   - Busca el número '79' que aparece solo en una línea dentro del texto.\n"
        final_query += "   - El contenido de la página 79 está DESPUÉS del número '78' y ANTES/HASTA el número '79'.\n"
        final_query += "   - O busca texto que rodea al número 79 impreso.\n\n"
        final_query += "3. NO uses los marcadores '--- PAGE X ---' para páginas específicas.\n"
        final_query += "   - Estos son índices internos de PyMuPDF, NO páginas físicas del libro.\n"
        final_query += "   - La página física 79 puede estar en '--- PAGE 80 ---' o cualquier otro índice.\n\n"
        final_query += "4. CITA el contenido EXACTO encontrado alrededor del número de página solicitado.\n"
        final_query += "5. Si no encuentras el número de página en el texto, indícalo claramente.\n"
        final_query += "="*60 + "\n"

        if request.mode == "swarm":
            response = await rag_service.query_swarm(final_query, request.pdf_id, model=request.model)
        else:
            response = rag_service.query(final_query, request.pdf_id, model=request.model)
            
        # [NEW] AGENTIC ACTION EXECUTOR (Write to Disk)
        # Parse response for Write Blocks
        from app.services.agent.executor import agent_executor
        
        action_log = agent_executor.execute_actions(response, target_repo)
        
        # Append action log to response so frontend knows
        if action_log and isinstance(response, dict):
            # If response is dict, we can't easily append string to it, so we append to answer
            if "answer" in response:
                response["answer"] += action_log
        elif action_log and isinstance(response, str):
            response += action_log

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
    
        # 4. Return result with Session ID and RAG mode used
        if isinstance(response, dict):
            response["session_id"] = session_id
            response["rag_mode_used"] = rag_mode_used  # NEW: For frontend indicator
            
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
