import os
import shutil
import glob
import time
import json
import hashlib
from datetime import datetime

# --- CONFIGURATION ---
BRAIN_PATH = r"C:\Users\Administrator\.gemini\antigravity\brain\37b97713-890f-42a7-ae15-7004b5903f12"
REPO_ROOT = r"C:\Users\Administrator\Desktop\Universal Pdf\pdf-cortex"
DOCS_BRAIN = os.path.join(REPO_ROOT, "docs", "brain")
HISTORY_DIR = os.path.join(DOCS_BRAIN, "history")
MANIFEST_FILE = os.path.join(DOCS_BRAIN, "genesis_manifest.json")

# --- UTILS ---
def load_manifest():
    if os.path.exists(MANIFEST_FILE):
        try:
            with open(MANIFEST_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"files": {}}
    return {"files": {}}

def save_manifest(data):
    with open(MANIFEST_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def get_file_type(filename):
    if filename.startswith("uploaded_"):
        return "USER_SENT"
    return "AGENT_RECEIVED"

class MindSync:
    def __init__(self):
        self.manifest = load_manifest()
        print(f"🧠 MindSync v2.0 Initialized")
        print(f"   Watching: {BRAIN_PATH}")
        print(f"   Target:   {DOCS_BRAIN}")

    def sync_session(self, found_files):
        """
        Syncs a batch of files into a Single Atomic Folder (The 'Message' Concept).
        """
        if not found_files:
            return

        # 1. Create Atomic Folder Name (Timestamp + ID)
        # Using a short hash of the first filename to create a pseudo-ID if we don't have a real one
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        batch_id = hashlib.sha256(found_files[0].encode()).hexdigest()[:8]
        folder_name = f"{timestamp}_{batch_id}"
        
        # Determine strict direction based on majority (or split? User asked for grouped by message)
        # We will assume mixed content goes into one "Interaction" folder for context preservation.
        
        target_dir = os.path.join(HISTORY_DIR, folder_name)
        
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            print(f"📂 Created Atomic Context: {folder_name}")

        for source_path in found_files:
            filename = os.path.basename(source_path)
            
            try:
                # Check for duplications in manifest to avoid re-importing the EXACT same file 
                # into a new folder if it hasn't changed? 
                # User wants history. So if I find it again, is it a new message?
                # For this simplicity, we only import NEW files found in Brain that aren't in Manifest yet.
                
                # ... Hash check logic here ...
                file_hash = calculate_hash(source_path)
                
                # COPY
                dest_path = os.path.join(target_dir, filename)
                shutil.copy2(source_path, dest_path)
                
                # MANIFEST UPDATE
                ftype = get_file_type(filename)
                entry_id = f"{folder_name}/{filename}"
                
                self.manifest["files"][entry_id] = {
                    "original_name": filename,
                    "type": ftype,
                    "atomic_folder": folder_name,
                    "hash": file_hash,
                    "timestamp": timestamp,
                    "local_path": dest_path
                }
                
                print(f"   -> 📎 {filename}")
                
            except Exception as e:
                print(f"   ❌ Failed: {filename} - {e}")

        save_manifest(self.manifest)

    def run_once(self):
        # Scan for supported files
        extensions = ['*.md', '*.png', '*.webp', '*.jpg', '*.txt']
        current_files = []
        for ext in extensions:
            current_files.extend(glob.glob(os.path.join(BRAIN_PATH, ext)))
        
        # Filter: Only sync files that are NOT in the manifest or have changed?
        # To simulate "New Messages", we strictly look for files whose HASH is not in our DB
        # associated with any previous entry.
        
        # Build set of known hashes
        known_hashes = set()
        for k, v in self.manifest["files"].items():
            known_hashes.add(v["hash"])
            
        new_batch = []
        for f in current_files:
            try:
                h = calculate_hash(f)
                if h not in known_hashes:
                    new_batch.append(f)
            except:
                continue
                
        if new_batch:
            print(f"⚡ Detected {len(new_batch)} new cognitive artifacts...")
            self.sync_session(new_batch)
        else:
            print("💤 No new interactions detected.")

    def watch(self):
        print("👀 Watch Mode Active. Pres Ctrl+C to stop.")
        try:
            while True:
                self.run_once()
                time.sleep(5)
        except KeyboardInterrupt:
            print("🛑 MindSync Stopped.")

if __name__ == "__main__":
    engine = MindSync()
    # For this session, we run once. To enable watch mode, uncomment:
    # engine.watch() 
    engine.run_once()
