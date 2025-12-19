
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from app.services.knowledge.repo_ingestor import repo_ingestor
from app.services.knowledge.pdf_ingestor import pdf_ingestor

router = APIRouter(prefix="/api/v1/ingest", tags=["ingest"])

class RepoRequest(BaseModel):
    url: str
    scope: str = "global" # 'global' or 'session'
    session_id: Optional[str] = None

class PDFRequest(BaseModel):
    url: str
    scope: str = "global"
    session_id: Optional[str] = None
    rag_mode: str = "injection"  # "injection" or "semantic"
    page_offset: int = 0         # NEW: Manual page offset correction
    enable_ocr: bool = False     # NEW: Enable OCR for scanned PDFs


@router.post("/repo")
async def ingest_repository(req: RepoRequest, background_tasks: BackgroundTasks):
    """
    Triggers a background Clone & Analyze process for the given Repo URL.
    """
    import uuid
    # Simple validation
    if not req.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL")
        
    # [FIX] If session-scoped but no session_id (fresh chat), generate one.
    final_session_id = req.session_id
    if req.scope == "session" and not final_session_id:
        final_session_id = str(uuid.uuid4())
    
    job_id = str(uuid.uuid4())
        
    # Run in background to avoid blocking
    background_tasks.add_task(repo_ingestor.ingest_repo, req.url, job_id, req.scope, final_session_id)
    
    return {
        "status": "started", 
        "message": f"Ingestion started.",
        "job_id": job_id,
        "repo_url": req.url,
        "session_id": final_session_id # Return the ID so frontend can adopt it
    }


@router.post("/pdf")
async def ingest_pdf_url(req: PDFRequest, background_tasks: BackgroundTasks):
    """
    Triggers a background download & process for a PDF URL.
    Supports: Direct links, Google Drive, Dropbox.
    """
    import uuid
    
    if not req.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    # Generate session ID if needed (same pattern as /repo)
    final_session_id = req.session_id
    session_created = False
    if req.scope == "session" and not final_session_id:
        # [FIX] Create the session in chat history so it appears in sidebar
        from app.services.chat.history import chat_history
        final_session_id = chat_history.create_session(title="PDF Knowledge")
        session_created = True
    
    job_id = str(uuid.uuid4())
    
    # Predict filename to return a valid URL immediately (Best Effort)
    # This allows the frontend to start polling/loading the file
    from app.services.knowledge.pdf_ingestor import pdf_ingestor
    predicted_name = pdf_ingestor._extract_filename(req.url)
    
    # Run in background (pass rag_mode, page_offset, enable_ocr for semantic embeddings)
    background_tasks.add_task(
        pdf_ingestor.ingest_pdf_url, 
        req.url, 
        job_id, 
        req.scope, 
        final_session_id,
        req.rag_mode,
        req.page_offset,    # NEW: Pass page offset
        req.enable_ocr      # NEW: Pass OCR flag
    )
    
    # [FIX] Return accessible FILE URL
    # Static mount: /files/pdfs -> data/shared_pdfs
    file_url = f"http://127.0.0.1:8000/files/pdfs/{predicted_name}/original.pdf"

    return {
        "status": "started",
        "message": f"PDF ingestion started (mode: {req.rag_mode}).",
        "job_id": job_id,
        "pdf_url": req.url,           # Original Source
        "file_url": file_url,         # Local Accessible URL [NEW]
        "session_id": final_session_id,
        "rag_mode": req.rag_mode
    }


@router.get("/list")
def list_ingested_repos(session_id: Optional[str] = None):
    """
    Lists all ingested knowledge sources (Repos AND PDFs) AND active jobs.
    """
    from app.core.database import SessionLocal, AtomicContext
    from sqlalchemy import or_
    
    # [FIX] If no session_id provided (new chat), return empty list
    # This ensures the KNOWLEDGE panel is clean for new chats
    if not session_id:
        return []
    
    # 1. Get Completed from DB
    db = SessionLocal()
    completed = []
    try:
        # Filter: batch_id for repos OR pdf- prefix contexts
        contexts = db.query(AtomicContext).filter(
            or_(
                AtomicContext.batch_id == "REPO_INGESTION",
                AtomicContext.batch_id.like("pdf-%")
            )
        ).all()
        
        # In-memory filter: Only show PDFs from THIS session in the KNOWLEDGE panel
        # Global PDFs are still available for queries (see main.py) but don't clutter UI
        filtered_contexts = []
        for ctx in contexts:
            # Only include session-specific PDFs in the display
            if ctx.scope == "session" and ctx.session_id == session_id:
                filtered_contexts.append(ctx)
        
        completed = [
            {
                "id": ctx.id,
                "name": ctx.folder_name,
                "timestamp": ctx.timestamp.isoformat() if ctx.timestamp else None,
                "status": "COMPLETED",
                "scope": ctx.scope # Return scope info
            }
            for ctx in filtered_contexts
        ]
    finally:
        db.close()

    # 2. Get Active/Failed Jobs
    jobs = repo_ingestor.get_active_jobs()
    active_list = []
    
    for jid, job in jobs.items():
        # Avoid duplicates if job is marked COMPLETED but also exists in DB
        # We can filter out COMPLETED jobs here if they are already in DB, 
        # but the Job ID != Context ID, so we might show duplicates transiently.
        # It's better to show the Job status for a bit.
        
        status = job["status"]
        
        job_scope = job.get("scope", "global")
        job_sid = job.get("session_id")

        if job_scope == "session" and job_sid != session_id:
            continue
            
        if status == "COMPLETED" and any(c["name"] == f"REPO: {job['repo'].split('/')[-1].replace('.git','')}" for c in completed):
             continue # Already in DB list
             
        active_list.append({
            "id": jid,
            "name": f"REPO: {job['repo'].split('/')[-1]}",
            "timestamp": job["start_time"],
            "status": status,
            "error": job.get("error"),
            "scope": job_scope
        })

    # 3. Get Active/Failed PDF Jobs
    pdf_jobs = pdf_ingestor.get_active_jobs()
    for jid, job in pdf_jobs.items():
        status = job["status"]
        job_scope = job.get("scope", "global")
        job_sid = job.get("session_id")
        
        if job_scope == "session" and job_sid != session_id:
            continue
        
        # [FIX] Extract name from URL - handle Google Drive '/view' suffix
        url = job.get("url", "")
        pdf_name = "pdf"
        if "/" in url:
            potential_name = url.split("/")[-1].split("?")[0]
            # Skip common URL endings that aren't real filenames
            if potential_name in ["view", "preview", "download", ""]:
                # Use the context_id if available, otherwise timestamp  
                pdf_name = job.get("context_id", f"pdf_{jid[:8]}")
            else:
                pdf_name = potential_name
        
        active_list.append({
            "id": jid,
            "name": f"PDF: {pdf_name}",
            "timestamp": job["start_time"],
            "status": status,
            "error": job.get("error"),
            "scope": job_scope
        })

    # Sort by timestamp desc
    combined = active_list + completed
    # robust sort
    combined.sort(key=lambda x: x["timestamp"] or "", reverse=True)
    
    return combined

@router.get("/files")
def list_repo_files(repo_name: str, path: str = ""):
    """
    Returns file structure for a specific repo or PDF.
    For PDFs, returns artifacts from database instead of filesystem.
    """
    import os
    from app.services.knowledge.repo_ingestor import SHARED_REPOS_DIR
    
    # [FIX] Handle PDFs - return their artifacts from DB
    if repo_name.startswith("PDF:"):
        from app.core.database import SessionLocal, AtomicContext, AtomicArtifact
        
        pdf_name = repo_name.replace("PDF: ", "").strip()
        db = SessionLocal()
        try:
            # Find the PDF context by folder_name
            context = db.query(AtomicContext).filter(
                AtomicContext.folder_name.like(f"%{pdf_name}%")
            ).first()
            
            if not context:
                return []  # Return empty instead of error
            
            # Get all artifacts for this PDF
            artifacts = db.query(AtomicArtifact).filter(
                AtomicArtifact.context_id == context.id
            ).all()
            
            items = []
            for art in artifacts:
                items.append({
                    "name": art.filename,
                    "type": "file",
                    "path": art.filename,
                    "size": len(art.content) if art.content else 0
                })
            return items
        finally:
            db.close()
    
    # REPOS: Original filesystem logic
    safe_repo = repo_name.replace("..", "").replace("/", "").replace("\\", "")
    full_path = os.path.join(SHARED_REPOS_DIR, safe_repo, path.lstrip("/"))
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Path not found")
        
    items = []
    try:
        with os.scandir(full_path) as it:
            for entry in it:
                if entry.name == ".git": continue
                items.append({
                    "name": entry.name,
                    "type": "dir" if entry.is_dir() else "file",
                    "path": os.path.join(path, entry.name).replace("\\", "/")
                })
        print(f"[DEBUG] list_repo_files: Scanned {full_path}, found {len(items)} items")
    except Exception as e:
        print(f"[ERROR] list_repo_files: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    # Sort folders first, then files
    items.sort(key=lambda x: (x["type"] != "dir", x["name"].lower()))
    return items

@router.get("/content")
def get_file_content(repo_name: str, path: str):
    """
    Returns text content of a file (repo file or PDF artifact).
    """
    import os
    from app.services.knowledge.repo_ingestor import SHARED_REPOS_DIR
    
    # [FIX] Handle PDF artifact content
    if repo_name.startswith("PDF:"):
        from app.core.database import SessionLocal, AtomicContext, AtomicArtifact
        
        pdf_name = repo_name.replace("PDF: ", "").strip()
        db = SessionLocal()
        try:
            # Find the PDF context
            context = db.query(AtomicContext).filter(
                AtomicContext.folder_name.like(f"%{pdf_name}%")
            ).first()
            
            if not context:
                raise HTTPException(status_code=404, detail="PDF context not found")
            
            # Get the specific artifact
            artifact = db.query(AtomicArtifact).filter(
                AtomicArtifact.context_id == context.id,
                AtomicArtifact.filename == path
            ).first()
            
            if not artifact:
                raise HTTPException(status_code=404, detail="PDF artifact not found")
            
            return {"content": artifact.content}
        finally:
            db.close()
    
    # REPOS: Original filesystem logic
    safe_repo = repo_name.replace("..", "").replace("/", "").replace("\\", "")
    full_path = os.path.join(SHARED_REPOS_DIR, safe_repo, path.lstrip("/"))
    
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        # Limit size
        if os.path.getsize(full_path) > 1024 * 1024: # 1MB limit
            return {"content": "⚠️ File too large to view directly."}
            
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            return {"content": f.read()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SaveFileRequest(BaseModel):
    repo_name: str
    path: str
    content: str

@router.post("/content")
def save_file_content(req: SaveFileRequest):
    """
    Overwrites the content of a specific file.
    """
    import os
    from app.services.knowledge.repo_ingestor import SHARED_REPOS_DIR
    
    safe_repo = req.repo_name.replace("..", "").replace("/", "").replace("\\", "")
    full_path = os.path.join(SHARED_REPOS_DIR, safe_repo, req.path.lstrip("/"))
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File to save not found. Create not supported yet.")
        
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(req.content)
        return {"status": "success", "message": "File saved."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")
