
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Literal

from app.services.system.sync_manager import sync_manager

router = APIRouter(prefix="/api/v1/system", tags=["system"])

class ModeSwitch(BaseModel):
    mode: Literal["LOCAL", "CLOUD"]

class SyncRequest(BaseModel):
    direction: Literal["PUSH", "PULL"]
    strategy: Literal["MERGE", "OVERWRITE"]

@router.get("/status")
def get_system_status():
    return sync_manager.get_status()

@router.post("/mode")
def switch_system_mode(req: ModeSwitch):
    try:
        sync_manager.switch_mode(req.mode)
        return {"status": "success", "message": f"Switched to {req.mode}. Please restart backend to apply fully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def trigger_sync(req: SyncRequest, background_tasks: BackgroundTasks):
    # Sync can be slow, run in background
    background_tasks.add_task(sync_manager.sync_data, req.direction, req.strategy)
    return {"status": "started", "message": f"Sync {req.direction} ({req.strategy}) started in background."}

@router.post("/backup")
def trigger_backup():
    try:
        path = sync_manager.backup_local()
        return {"status": "success", "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
