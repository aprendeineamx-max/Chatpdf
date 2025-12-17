with open(r"app\services\rag\engine.py", "rb") as f:
    content = f.read()
    print(f"BYTES: {len(content)}")
    print(f"LINES: {len(content.splitlines())}")
    print("--- TAIL ---")
    print(content[-500:].decode('utf-8', errors='replace'))
