import os
import shutil
import glob
from datetime import datetime

# Configuration
# This is the Agent's "Brain" path where it stores memory/plans
# In a real scenario, this might need dynamic detection, but for this session we know it.
BRAIN_PATH = r"C:\Users\Administrator\.gemini\antigravity\brain\37b97713-890f-42a7-ae15-7004b5903f12"
TARGET_DIR = r"..\docs\agent_brain"

def sync_artifacts():
    print(f"🧠 Syncing Agent Artifacts...")
    print(f"FROM: {BRAIN_PATH}")
    print(f"TO:   {os.path.abspath(TARGET_DIR)}")
    
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        print(f"Created target directory: {TARGET_DIR}")

    # File types to sync
    extensions = ['*.md', '*.png', '*.webp', '*.jpg']
    
    count = 0
    for ext in extensions:
        files = glob.glob(os.path.join(BRAIN_PATH, ext))
        for file in files:
            filename = os.path.basename(file)
            target_file = os.path.join(TARGET_DIR, filename)
            
            # Simple Copy (Overwrite if newer logic could be added, but overwrite is fine for now)
            shutil.copy2(file, target_file)
            print(f" -> Synced: {filename}")
            count += 1
            
    print(f"\n✅ Synced {count} files successfully!")
    print("These documents are now part of your codebase.")

if __name__ == "__main__":
    sync_artifacts()
