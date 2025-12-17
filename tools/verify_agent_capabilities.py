import requests
import time
import os

BASE_URL = "http://localhost:8000/api/v1"
REPO_NAME = "crawlbase-mcp"
REPO_CONTEXT = f"REPO: {REPO_NAME}"

def send_query(text):
    print(f"\n[USER]: {text}")
    try:
        res = requests.post(f"{BASE_URL}/query", json={
            "query_text": text,
            "pdf_id": "all",
            "repo_context": REPO_CONTEXT # Critical: Passing context
        })
        res.raise_for_status()
        data = res.json()
        print(f"[AGENT]: {data['response']}")
        return data
    except Exception as e:
        print(f"[ERROR]: {e}")
        return None

def verify_file(path, expected_content_part):
    full_path = os.path.join(r"data\shared_repos", REPO_NAME, path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        if expected_content_part in content:
            print(f"✅ VERIFIED: {path} contains '{expected_content_part}'")
        else:
            print(f"❌ FAIL: {path} content mismatch.\nFound: {content}")
    else:
        print(f"❌ FAIL: {path} NOT FOUND at {full_path}")

import sys
import io

# Force utf-8 for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("--- STARTING AGENTIC CAPABILITY TEST ---")

# 1. Create New File
send_query("Crea un archivo en la raiz llamado 'demo_creation.js' que imprima 'Created by API Script'")
time.sleep(2) # Give it a moment to write
verify_file("demo_creation.js", "Created by API Script")

# 2. Edit Existing File
send_query("Edita el archivo src/hello_agent.js y cambia el mensaje a 'Updated by API Script'")
time.sleep(2)
verify_file("src/hello_agent.js", "Updated by API Script")
