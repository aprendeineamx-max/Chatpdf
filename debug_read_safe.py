try:
    with open(r"app\services\rag\engine.py", "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            print(f"{i+1}: {line.strip()}")
except Exception as e:
    print(e)
