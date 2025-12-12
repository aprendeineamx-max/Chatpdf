import os
import sys
# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import time
import sqlalchemy
from sqlalchemy import text
from app.core.config import settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# CONFIG
MANIFEST_PATH = r"C:\Users\Administrator\Desktop\Universal Pdf\pdf-cortex\docs\brain\genesis_manifest.json"
DB_URL = settings.SUPABASE_DB_URL

def get_db_connection():
    if not DB_URL:
        raise ValueError("SUPABASE_DB_URL is not configured.")
    engine = sqlalchemy.create_engine(DB_URL)
    return engine.connect()

def load_manifest():
    if not os.path.exists(MANIFEST_PATH):
        return {"files": {}}
    with open(MANIFEST_PATH, 'r') as f:
        return json.load(f)

def run_sync_daemon():
    print("🔮 SyncDaemon Active (Liquid Memory Ingestor)...")
    
    # Initialize Embedding Model
    print("   Loading Embedding Model (MiniLM-L6-v2)...")
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    conn = get_db_connection()
    
    while True:
        try:
            print("   Scanning Manifest...")
            manifest = load_manifest()
            
            for file_id, meta in manifest["files"].items():
                folder_name = meta.get("atomic_folder")
                filename = meta.get("original_name")
                file_hash = meta.get("hash")
                file_path = meta.get("local_path")
                timestamp = meta.get("timestamp")
                
                # 1. Ensure Context Exists
                # (Simple check via INSERT ON CONFLICT DO NOTHING behavior or Select first)
                # For simplicity in pure SQL without ORM:
                
                # Check Context
                result = conn.execute(text("SELECT id FROM atomic_contexts WHERE folder_name = :fn"), {"fn": folder_name})
                ctx_row = result.fetchone()
                
                if not ctx_row:
                    print(f"   -> Registering Context: {folder_name}")
                    # Extract batch_id from folder_name e.g. "2025..._HASH"
                    batch_id = folder_name.split('_')[-1]
                    insert_q = text("""
                        INSERT INTO atomic_contexts (folder_name, timestamp, batch_id) 
                        VALUES (:fn, :ts, :bid) RETURNING id
                    """)
                    result = conn.execute(insert_q, {"fn": folder_name, "ts": timestamp.replace('_', ' ').replace('-', '/'), "bid": batch_id}) # Timestamp parsing might need refine
                    # Fix timestamp format: 2025-12-12_15-03-07 to 2025-12-12 15:03:07
                    # Actually standard strptime is better.
                    conn.commit()
                    ctx_id = result.fetchone()[0]
                else:
                    ctx_id = ctx_row[0]
                
                # 2. Check Artifact
                res_art = conn.execute(text("SELECT id FROM atomic_artifacts WHERE context_id = :cid AND filename = :fname"), {"cid": ctx_id, "fname": filename})
                art_row = res_art.fetchone()
                
                if not art_row:
                    print(f"   -> Ingesting Artifact: {filename}")
                    
                    # Read Content if text
                    content_text = ""
                    if filename.endswith(".md") or filename.endswith(".txt"):
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content_text = f.read()
                        except:
                            pass
                    
                    ins_art = text("""
                        INSERT INTO atomic_artifacts (context_id, filename, file_type, file_hash, local_path, content)
                        VALUES (:cid, :fname, :ftype, :fhash, :lpath, :content) RETURNING id
                    """)
                    
                    res_ins = conn.execute(ins_art, {
                        "cid": ctx_id, "fname": filename, "ftype": meta.get("type"), 
                        "fhash": file_hash, "lpath": file_path, "content": content_text
                    })
                    conn.commit()
                    art_id = res_ins.fetchone()[0]
                    
                    # 3. Generate Embedding (Liquid Memory)
                    if content_text:
                        print(f"      -> Generating Embeddings...")
                        vector = embed_model.get_text_embedding(content_text)
                        
                        ins_vec = text("""
                            INSERT INTO artifact_embeddings (artifact_id, embedding, metadata)
                            VALUES (:aid, :vec, :meta)
                        """)
                        conn.execute(ins_vec, {"aid": art_id, "vec": vector, "meta": json.dumps(meta)})
                        conn.commit()
                        
            print("   Sync Cycle Complete. Sleeping 10s...")
            time.sleep(10)
            
        except Exception as e:
            print(f"❌ Daemon Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_sync_daemon()
