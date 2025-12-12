import os
# Force set key before imports
os.environ["GROQ_API_KEY"] = "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"

try:
    from llama_index.llms.groq import Groq
    print("[INFO] Initializing Groq...")
    llm = Groq(model="llama3-70b-8192", api_key=os.environ["GROQ_API_KEY"])
    
    print("[INFO] Testing completion...")
    resp = llm.complete("Hello, are you working?")
    print(f"[SUCCESS] Response: {resp}")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
