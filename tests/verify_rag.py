
import sys
import os

# Add app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("--- STARTING RAG TEST ---")
try:
    from app.services.rag.engine import rag_service
    print("[PASS] Import RAG Service")
except Exception as e:
    print(f"[FAIL] Import RAG Service: {e}")
    sys.exit(1)

try:
    msg = rag_service.query("Hello", "all")
    print(f"[PASS] Query Executed: {msg}")
except Exception as e:
    print(f"[FAIL] Query Logic: {e}")
    
print("--- TEST COMPLETE ---")
