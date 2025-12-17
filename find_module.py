import sys
import os

# Add CWD to path
sys.path.insert(0, os.getcwd())

try:
    import app.services.rag.engine
    print(f"MODULE PATH: {app.services.rag.engine.__file__}")
except Exception as e:
    print(f"IMPORT ERROR: {e}")
