import requests
import json
import time

URL = "http://localhost:8000/api/v1/query"
PAYLOAD = {
    "query_text": "Crea un archivo rulestone.md en el repo crawlbase-node. Ponle el texto 'rules'.",
    "model": "Meta-Llama-3.3-70B-Instruct",
    "provider": "Sambanova"
}

print("--- SENDING REPO-NAMED PATH REQUEST ---")
try:
    r = requests.post(URL, json=PAYLOAD)
    data = r.json()
    answer_text = data.get("answer", "")
    print("ANSWER:", answer_text[:150])
    
    # Check what path it chose
    if "*** WRITE_FILE: rulestone.md ***" in answer_text:
         print("✅ SUCCESS: Agent proposed 'rulestone.md' (Implied Root of Target Repo).")
    elif "*** WRITE_FILE: crawlbase-node/rulestone.md ***" in answer_text:
         print("⚠️ WARNING: Agent included repo name in path 'crawlbase-node/rulestone.md'. Backend must handle this!")
    else:
         print(f"❌ FAILURE/OTHER: {answer_text}")

except Exception as e:
    print("ERROR:", e)
