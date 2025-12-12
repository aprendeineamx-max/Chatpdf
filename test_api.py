import requests
import time
import sys

def test_ingestion():
    url = "http://127.0.0.1:8000/api/v1/ingest"
    
    # Create a dummy PDF for testing if one doesn't exist
    from reportlab.pdfgen import canvas
    dummy_pdf_path = "test_doc.pdf"
    
    c = canvas.Canvas(dummy_pdf_path)
    c.drawString(100, 750, "Hello World from PDF Cortex Page 1")
    c.showPage()
    c.drawString(100, 750, "This is Page 2 - Logic Test")
    c.save()
    
    print(f"Submitting {dummy_pdf_path}...")
    
    try:
        with open(dummy_pdf_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files)
            
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            job_id = response.json().get("job_id")
            print(f"✅ Ingestion started successfully. Job ID: {job_id}")
            print("Check server logs for background processing details.")
        else:
            print("❌ Ingestion failed.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ingestion()
