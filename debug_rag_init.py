import sys
import traceback

print("--- STARTING DEBUG ---")
try:
    print("1. Importing libraries...")
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    # Delay expensive imports
    print("2. Importing Postgres/Supabase settings...")
    from app.core.config import settings
    print(f"   DB URL mapped: {settings.SUPABASE_DB_URL is not None}")
    
    print("3. Importing Engine Module (triggers instantiation)...")
    import app.services.rag.engine
    print("   Engine module imported.")
    
    print("4. Accessing rag_service...")
    service = app.services.rag.engine.rag_service
    print("   rag_service accessed.")

    print("5. Testing Query...")
    # Mock query to force lazy logic if any
    # result = service.query("test", "all")
    # print("   Query result:", result)
    
except Exception as e:
    print(f"\n--- CRASH DETECTED ---")
    print(f"Type: {type(e).__name__}")
    print(f"Error: {e}")
    print("Traceback:")
    traceback.print_exc()

