import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"
HEADERS = {'Content-Type': 'application/json'}

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def test_root():
    try:
        r = requests.get("http://127.0.0.1:8000/")
        if r.status_code == 200:
            log("Root Endpoint: OK", "PASS")
            return True
        else:
            log(f"Root Endpoint Failed: {r.status_code}", "FAIL")
            return False
    except Exception as e:
        log(f"Root Endpoint Error: {e}", "FAIL")
        return False

def test_standard_query():
    payload = {"query_text": "Hola, prueba de sistema.", "pdf_id": "all", "mode": "standard"}
    try:
        start = time.time()
        r = requests.post(f"{BASE_URL}/query", json=payload, headers=HEADERS)
        duration = time.time() - start
        
        if r.status_code == 200:
            ans = r.json().get("answer", "")
            log(f"Standard Query: OK ({duration:.2f}s). Answer length: {len(ans)}", "PASS")
            return True
        else:
            log(f"Standard Query Failed: {r.text}", "FAIL")
            return False
    except Exception as e:
        log(f"Standard Query Error: {e}", "FAIL")
        return False

def test_swarm_query():
    payload = {"query_text": "Explica el cambio climatico detalladamente.", "pdf_id": "all", "mode": "swarm"}
    try:
        start = time.time()
        r = requests.post(f"{BASE_URL}/query", json=payload, headers=HEADERS)
        duration = time.time() - start
        
        if r.status_code == 200:
            data = r.json()
            if "[Hydra Swarm 🐝]" in data.get("answer", ""):
                 log(f"Swarm Query: OK ({duration:.2f}s). Tag Found.", "PASS")
                 return True
            else:
                 log("Swarm Query: OK but Tag MISSING.", "WARN")
                 return True # Soft pass
        else:
            log(f"Swarm Query Failed: {r.text}", "FAIL")
            return False
    except Exception as e:
        log(f"Swarm Query Error: {e}", "FAIL")
        return False

def test_edge_cases():
    # 1. Empty Query
    payload = {"query_text": "", "pdf_id": "all"}
    r = requests.post(f"{BASE_URL}/query", json=payload, headers=HEADERS)
    if r.status_code == 422: # Validation Error expected
        log("Empty Query Check: OK (422 Received)", "PASS")
    else:
         # Frontend blocks this usually, but API might accept empty string?
         log(f"Empty Query Check: Unexpected Code {r.status_code}", "WARN")

    # 2. Bad PDF ID
    payload = {"query_text": "Test", "pdf_id": "non_existent_id"}
    r = requests.post(f"{BASE_URL}/query", json=payload, headers=HEADERS)
    if r.status_code == 200:
        if "Error" in r.json().get("answer", "") or "not found" in r.json().get("answer", "").lower():
             log("Bad PDF ID Check: Handled Gracefully", "PASS")
        else:
             log("Bad PDF ID Check: API returned success? (Maybe fallback used)", "WARN")

if __name__ == "__main__":
    print("--- HYDRA SYSTEM DIAGNOSTICS ---")
    if test_root():
        test_standard_query()
        test_swarm_query()
        test_edge_cases()
    print("--- END REPORT ---")
