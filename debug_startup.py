import sys
try:
    print("--- Attempting Import app.main ---")
    import app.main
    print("--- Import Successful ---")
except Exception as e:
    print(f"--- CRASH DETECTED ---")
    print(e)
    import traceback
    traceback.print_exc()
