import requests
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_full_flow():
    # 1. Ingest
    print("\n[1] TEST: Ingesting Document...")
    dummy_pdf = "test_doc.pdf"
    
    # Check if we need to recreate dummy pdf
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(dummy_pdf)
    c.drawString(100, 750, "The code for the secret vault is 7788.")
    c.showPage()
    c.drawString(100, 750, "Page 2 confirms the vault is made of titanium.")
    c.save()

    job_id = None
    with open(dummy_pdf, "rb") as f:
        res = requests.post(f"{BASE_URL}/ingest", files={"file": f})
        try:
            print(f"Ingest Response status: {res.status_code}")
            print(f"Ingest Response body: {res.json()}")
            if res.status_code == 200:
                job_id = res.json()["job_id"]
        except Exception as e:
            print(f"❌ Failed to parse JSON: {res.text}")
            return
    
    if not job_id:
        print("❌ Ingestion failed.")
        return

    # Wait for background processing (Simulated polling)
    # The current API doesn't have a status endpoint yet, so we just wait.
    print("[2] Waiting for Async Processing (5s)...")
    time.sleep(5)
    
    # 2. Query
    print("\n[3] TEST: Querying RAG Engine...")
    query_payload = {
        "query": "What is the secret vault code?",
        "pdf_id": job_id
    }
    
    try:
        res_q = requests.post(f"{BASE_URL}/query", json=query_payload)
        print(f"Query Status: {res_q.status_code}")
        print(f"Query Result: {res_q.json()}")
        
        # Validation
        answer = res_q.json().get("answer", "")
        if "7788" in answer:
             print("✅ SUCCESS: The model retrieved the secret code!")
        else:
             print("⚠️ WARN: Answer might be incorrect or model hallucinated.")
             
    except Exception as e:
        print(f"Query Failed: {e}")

if __name__ == "__main__":
    test_full_flow()
