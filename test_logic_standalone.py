import sys
import os

# Set Env Vars manually for testing
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["API_V1_STR"] = "/api/v1" # config defaults

try:
    print("[INFO] Importing RAG Service...")
    from app.services.rag.engine import RAGService
    service = RAGService()
    print("[INFO] Service Initialized.")
    
    # Mock data ingestion
    print("[INFO] Attempting Mock Ingestion...")
    test_pdf_id = "mock_test_id"
    test_dir = "data/processed/mock_test_id/text"
    os.makedirs(test_dir, exist_ok=True)
    with open(f"{test_dir}/page_1.txt", "w") as f:
        f.write("The secret code is 1234. This is page 1.")
        
    index = service.index_document(test_dir, test_pdf_id)
    print("[INFO] Indexing Complete.")
    
    # Query
    print("[INFO] Querying...")
    res = service.query("What is the secret code?", test_pdf_id)
    print(f"[RESULT] {res}")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
