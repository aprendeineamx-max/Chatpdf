import requests
import json

URL = "http://localhost:8000/api/v1/query"
PAYLOAD = {
    "query_text": "Crea el archivo fallback_test.txt en cualquier repo con el texto 'Funciona estrategia D'",
    "model": "Meta-Llama-3.3-70B-Instruct",
    "provider": "Sambanova"
}

print("--- SENDING FALLBACK WRITE REQUEST ---")
try:
    r = requests.post(URL, json=PAYLOAD)
    data = r.json()
    print("ANSWER:", data.get("answer")[:100])
    if "ACTIONS EXECUTED" in r.text or "Edited:" in r.text or "fallback_test.txt" in r.text:
       print("SUCCESS: Write detected in response.")
    else:
       print("WARNING: No write confirmation in response.")
except Exception as e:
    print("ERROR:", e)
