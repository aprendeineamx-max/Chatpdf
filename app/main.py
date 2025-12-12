from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.services.ingestion.processor import PDFProcessor
import shutil
import os
import uuid

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="API for Advanced PDF RAG System"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev (Vite runs on random ports)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Instance Processor
processor = PDFProcessor()

@app.get("/")
def read_root():
    return {"message": "PDF Cortex is Online", "version": "0.1.0"}

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
    pdf_id: str
    mode: str = "standard" 
    session_id: Optional[str] = None # [NEW] Persistence

@app.post(f"{settings.API_V1_STR}/query")
async def query_document(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Query a processed PDF. Saves history asynchronously.
    """
    from app.services.rag.engine import rag_service
    from app.services.chat.history import chat_history
    
    # 1. Manage Session
    session_id = request.session_id
    if not session_id:
        # Create new session if none provided
        session_id = chat_history.create_session(title=request.query_text[:30])
    
    # 2. Execute Logic
    if request.mode == "swarm":
        response = await rag_service.query_swarm(request.query_text, request.pdf_id)
    else:
        response = rag_service.query(request.query_text, request.pdf_id)
        
    # 3. Save History (Async)
    if isinstance(response, dict):
        # We need the text answer and sources
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
