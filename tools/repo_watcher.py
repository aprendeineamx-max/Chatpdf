
import sys
import time
import os
import uuid
import logging
from datetime import datetime
from dotenv import load_dotenv

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add root to path
sys.path.append(os.getcwd())

# Configuration
WATCH_DIR = r"C:\Users\Administrator\Desktop\Universal Pdf\pdf-cortex"
IGNORE_DIRS = {".git", "node_modules", "venv", "__pycache__", ".gemini", "dist", "build"}
IGNORE_EXTS = {".pyc", ".log", ".tmp"}

# Setup Logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Load Env
load_dotenv(".env")
load_dotenv("genesis-web/.env") 

# Supabase Init
try:
    from supabase import create_client
    from app.core.config import settings
    
    url = settings.SUPABASE_URL or os.getenv("VITE_SUPABASE_URL")
    key = settings.SUPABASE_KEY or os.getenv("VITE_SUPABASE_KEY")
    
    if url and key:
        supabase = create_client(url, key)
        logger.info("✅ Connected to Supabase Timeline")
    else:
        supabase = None
        logger.warning("⚠️ No Supabase credentials found. Running in local audit mode.")
except ImportError:
    supabase = None
    logger.warning("⚠️ Supabase lib not installed. Running in local audit mode.")


class GenesisRepoHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return

        # Filtering
        path = event.src_path
        filename = os.path.basename(path)
        
        # Skip hidden/ignored
        parts = path.split(os.sep)
        if any(p in IGNORE_DIRS for p in parts):
            return
            
        if any(filename.endswith(ext) for ext in IGNORE_EXTS):
            return

        # Prepare Event Data
        event_type = event.event_type
        rel_path = os.path.relpath(path, WATCH_DIR)
        
        logger.info(f"👁️ Caught {event_type.upper()}: {rel_path}")
        
        # Debounce/Logic could go here (e.g. don't log every micro-save)
        # For now, we log direct to timeline.
        
        if supabase:
            try:
                self._push_to_timeline(event_type, rel_path)
            except Exception as e:
                logger.error(f"Failed to sync event: {e}")

    def _push_to_timeline(self, event_type, rel_path):
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        data = {
            "id": str(uuid.uuid4()),
            "type": "repo_change",
            "folder_name": f"REPO: {rel_path}", # Timeline Header
            "content": f"File {event_type}: {rel_path}",
            "batch_id": "REPO",
            "timestamp": ts,
            "metadata": {
                "event": event_type,
                "path": rel_path,
                "source": "RepoWatcher"
            },
            "created_at": datetime.now().isoformat()
        }
        
        # Async execution of blocking call? No, threads are fine for this background tool.
        supabase.table("atomic_contexts").insert(data).execute()


if __name__ == "__main__":
    event_handler = GenesisRepoHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=True)
    
    logger.info(f"🦅 Omni-Eye Watching: {WATCH_DIR}")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
