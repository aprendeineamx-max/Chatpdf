import requests
import json
import time

URL = "http://localhost:8000/api/v1/query"
PAYLOAD = {
    "query_text": "Crea archivo raiz.txt DIRECTAMENTE en la raiz del repo con texto 'soy raiz'. NO uses carpeta src ni docs.",
    "model": "Meta-Llama-3.3-70B-Instruct",
    "provider": "Sambanova"
}

print("--- SENDING ROOT WRITE REQUEST ---")
try:
    # Wait for restart
    time.sleep(2)
    r = requests.post(URL, json=PAYLOAD)
    data = r.json()
    print("ANSWER:", data.get("answer")[:100])
    
    answer_text = data.get("answer", "")
    if "*** WRITE_FILE: raiz.txt ***" in answer_text:
         print("✅ SUCCESS: Agent proposed writing to 'raiz.txt' (Root).")
    elif "*** WRITE_FILE: src/raiz.txt ***" in answer_text:
         print("❌ FAILURE: Agent defaulted to 'src/raiz.txt'.")
    elif "*** WRITE_FILE: docs/raiz.txt ***" in answer_text:
         print("❌ FAILURE: Agent defaulted to 'docs/raiz.txt'.")
    else:
         print(f"⚠️ UNCERTAIN: Check output. {answer_text[:50]}...")

except Exception as e:
    print("ERROR:", e)
