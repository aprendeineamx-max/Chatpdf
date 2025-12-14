
import os
import shutil
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Literal
from sqlalchemy.orm import Session
from supabase import create_client, Client

from app.core.config import settings
from app.core.database import SessionLocal, ChatMessage, ChatSession, OrchestratorTask, engine, Base
from app.core.database import AtomicContext, AtomicArtifact

# Define Paths
ENV_PATH = ".env"
DB_PATH = "data/db/local_core.db"
BACKUP_DIR = "data/db/backups"

class SyncManager:
    def __init__(self):
        # We need independent clients
        self.cloud_client: Client = None
        if settings.CLOUD_SUPABASE_URL and settings.CLOUD_SUPABASE_KEY:
            try:
                self.cloud_client = create_client(settings.CLOUD_SUPABASE_URL, settings.CLOUD_SUPABASE_KEY)
            except Exception as e:
                print(f"⚠️ Cloud Client Init Failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Returns Setup Status and Row Counts"""
        status = {
            "mode": settings.CORE_MODE,
            "local_db": os.path.exists(DB_PATH),
            "cloud_connected": self.cloud_client is not None,
            "stats": {"local": {}, "cloud": {}}
        }
        
        # Local Stats
        try:
            db = SessionLocal()
            status["stats"]["local"] = {
                "messages": db.query(ChatMessage).count(),
                "tasks": db.query(OrchestratorTask).count(),
                "contexts": db.query(AtomicContext).count()
            }
            db.close()
        except:
            status["stats"]["local"] = "error"

        # Cloud Stats (Async check usually, but we do simplified blocking here or skip)
        # Using the REST client is synchronous in python `supabase-py` unless async is used?
        # Standard client is sync.
        if self.cloud_client:
            try:
                # Limit count to avoid latency
                res = self.cloud_client.table("chat_messages").select("id", count="exact").limit(1).execute()
                status["stats"]["cloud"]["messages"] = res.count
            except:
                status["stats"]["cloud"] = "unreachable"
                
        return status

    def switch_mode(self, mode: str):
        """Updates .env to switch CORE_MODE"""
        mode = mode.upper()
        if mode not in ["LOCAL", "CLOUD"]:
            raise ValueError("Invalid Mode")
            
        # Read .env
        with open(ENV_PATH, "r") as f:
            lines = f.readlines()
            
        new_lines = []
        found = False
        for line in lines:
            if line.startswith("CORE_MODE="):
                new_lines.append(f"CORE_MODE={mode}\n")
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            new_lines.append(f"\nCORE_MODE={mode}\n")
            
        with open(ENV_PATH, "w") as f:
            f.writelines(new_lines)
            
        # Update Runtime Settings (Partial, won't affect all singletons)
        settings.CORE_MODE = mode
        # Ideally trigger restart? For now rely on user or hot-reload.

    def backup_local(self) -> str:
        """Creates a timestamped copy of local_core.db"""
        os.makedirs(BACKUP_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{BACKUP_DIR}/local_core_{ts}.db"
        shutil.copy(DB_PATH, backup_path)
        return backup_path

    def sync_data(self, direction: Literal["PUSH", "PULL"], strategy: Literal["MERGE", "OVERWRITE"]):
        """
        PUSH: Local -> Cloud
        PULL: Cloud -> Local
        Strategies:
        - OVERWRITE: Truncate destination, insert all source.
        - MERGE: upsert based on ID.
        Tables: chat_sessions, chat_messages, orchestrator_tasks
        """
        if not self.cloud_client:
            raise Exception("Cloud Disconnected")
            
        db = SessionLocal()
        
        tables = [
            (ChatSession, "chat_sessions"),
            (ChatMessage, "chat_messages"),
            (OrchestratorTask, "orchestrator_tasks"),
            (AtomicContext, "atomic_contexts"),
            (AtomicArtifact, "atomic_artifacts")
        ]
        
        try:
            for Model, table_name in tables:
                print(f"🔄 Syncing {table_name} ({direction})...")
                
                # --- PULL (Cloud -> Local) ---
                if direction == "PULL":
                    # 1. Fetch Cloud Data
                    # Pagination needed for large datasets! For MVP fetching 1000.
                    res = self.cloud_client.table(table_name).select("*").limit(1000).execute()
                    cloud_rows = res.data
                    
                    if strategy == "OVERWRITE":
                        # Truncate Local
                        db.query(Model).delete()
                        db.commit()
                        
                    # Insert/Merge
                    for row in cloud_rows:
                        # Convert ISO strings to datetime objects if needed or rely on SQLA coercion
                        # SQLite stores datetime as string usually, so might be fine.
                        # Supabase returns strings.
                        local_obj = db.merge(Model(**row)) if strategy == "MERGE" else Model(**row)
                        db.add(local_obj)
                    db.commit()

                # --- PUSH (Local -> Cloud) ---
                elif direction == "PUSH":
                    # 1. Fetch Local Data
                    local_rows = db.query(Model).all()
                    data_to_push = []
                    for row in local_rows:
                        # Convert to dict
                        d = row.__dict__.copy()
                        d.pop('_sa_instance_state', None)
                        # Serialize datetimes
                        for k, v in d.items():
                            if isinstance(v, datetime):
                                d[k] = v.isoformat()
                        data_to_push.append(d)
                        
                    if not data_to_push: continue

                    if strategy == "OVERWRITE":
                        # Truncate Cloud (Dangerous!)
                        # self.cloud_client.table(table_name).delete().neq("id", "0000").execute() 
                        # We won't implement Truncate Cloud easily due to RLS/Safety.
                        # Only MERGE supported for Push in MVP.
                        pass
                        
                    # Upsert Cloud
                    self.cloud_client.table(table_name).upsert(data_to_push).execute()
                    
        finally:
            db.close()

sync_manager = SyncManager()
