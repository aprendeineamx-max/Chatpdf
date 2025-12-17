import requests
import json

URL = "http://localhost:8000/api/v1/query"
PAYLOAD = {
    "query_text": "¿Quién eres?",
    "model": "Meta-Llama-3.3-70B-Instruct",
    "provider": "Sambanova"
}

print("--- SENDING SPANISH TEST REQUEST ---")
try:
    r = requests.post(URL, json=PAYLOAD)
    data = r.json()
    print("ANSWER:", data.get("answer"))
except Exception as e:
    print("ERROR:", e)
