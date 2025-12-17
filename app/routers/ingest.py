
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from app.services.knowledge.repo_ingestor import repo_ingestor

router = APIRouter(prefix="/api/v1/ingest", tags=["ingest"])

class RepoRequest(BaseModel):
    url: str
    scope: str = "global" # 'global' or 'session'
    session_id: Optional[str] = None


@router.post("/repo")
async def ingest_repository(req: RepoRequest, background_tasks: BackgroundTasks):
    """
    Triggers a background Clone & Analyze process for the given Repo URL.
    """
    import uuid
    # Simple validation
    if not req.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    job_id = str(uuid.uuid4())
        
    # Run in background to avoid blocking
    background_tasks.add_task(repo_ingestor.ingest_repo, req.url, job_id, req.scope, req.session_id)
    
    return {
        "status": "started", 
        "message": f"Ingestion started.",
        "job_id": job_id,
        "repo_url": req.url
    }

@router.get("/list")
def list_ingested_repos(session_id: Optional[str] = None):
    """
    Lists all ingested repositories (AtomicContexts) AND active jobs.
    """
    from app.core.database import SessionLocal, AtomicContext
    
    # 1. Get Completed from DB
    db = SessionLocal()
    completed = []
    try:
        # Filter: Scope 'global' OR Scope 'session' matches current session
        query = db.query(AtomicContext).filter(AtomicContext.batch_id == "REPO_INGESTION")
        contexts = query.all()
        
        # In-memory filter for complex OR logic (SQLite/SQLAlchemy simple fallback)
        filtered_contexts = []
        for ctx in contexts:
            if ctx.scope == "global":
                filtered_contexts.append(ctx)
            elif ctx.scope == "session" and ctx.session_id == session_id:
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

    # Sort by timestamp desc
    combined = active_list + completed
    # robust sort
    combined.sort(key=lambda x: x["timestamp"] or "", reverse=True)
    
    return combined

@router.get("/files")
def list_repo_files(repo_name: str, path: str = ""):
    """
    Returns file structure for a specific repo and path.
    """
    import os
    from app.services.knowledge.repo_ingestor import SHARED_REPOS_DIR
    
    # Security check: prevent traversal
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # Sort folders first, then files
    items.sort(key=lambda x: (x["type"] != "dir", x["name"].lower()))
    return items

@router.get("/content")
def get_file_content(repo_name: str, path: str):
    """
    Returns text content of a file.
    """
    import os
    from app.services.knowledge.repo_ingestor import SHARED_REPOS_DIR
    
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
