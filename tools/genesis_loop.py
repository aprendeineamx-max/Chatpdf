
import os
import sys
# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import sqlalchemy
from sqlalchemy import text
from app.core.config import settings

# CONFIG
DB_URL = settings.SUPABASE_DB_URL

def get_db_connection():
    if not DB_URL:
        raise ValueError("SUPABASE_DB_URL is not configured.")
    engine = sqlalchemy.create_engine(DB_URL)
    return engine.connect()

def run_genesis_loop():
    print("♾️ Genesis Loop Active (Autopoietic Singularity)...")
    conn = get_db_connection()
    
    while True:
        try:
            print("   👁️ Monitoring System Health...")
            
            # 1. Detect Failures
            # In a real scenario, this would enable semantic search over logs
            # For MVP, we simulate: Find evidence of 'FAILURE'
            
            # (Mock) Let's pretend we found a failure in 'app/services/pdf/processor.py'
            # Check if we already have an open optimization for it
            
            check_q = text("SELECT id FROM genesis_optimizations WHERE target_artifact = 'app/services/pdf/processor.py' AND status = 'PENDING'")
            existing = conn.execute(check_q).fetchone()
            
            if not existing:
                print("   🚨 Anomaly Detected: Processor efficiency drop.")
                print("   🧠 Architecting Solution...")
                time.sleep(2) # Simulate thinking
                
                # Mock Proposal
                proposal = text("""
                    INSERT INTO genesis_optimizations (target_artifact, issue_detected, proposed_fix, status)
                    VALUES (:tgt, :iss, :fix, 'PENDING')
                """)
                
                fake_fix = """
- def process_pdf(path):
-    return extract_text(path)
+ def process_pdf(path):
+    # Optimized with parallel processing
+    return parallel_extract(path, workers=4)
                """
                
                conn.execute(proposal, {
                    "tgt": "app/services/pdf/processor.py",
                    "iss": "Single-threaded extraction is slow on large files.",
                    "fix": fake_fix.strip()
                })
                conn.commit()
                print("   ✨ Optimization Proposal Created (ID: pending-review).")
            else:
                print("   ✅ System Stable (Pending optimizations in queue).")

            time.sleep(15)
            
        except Exception as e:
            print(f"❌ Genesis Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_genesis_loop()
