import requests
import os

API_URL = "http://127.0.0.1:8000/api/v1/ingest"
PDF_PATH = r"C:\Users\Administrator\Desktop\Universal Pdf\PDFs\1.- B3CNP - Nuestro Planeta la tierra - Libro del Adulto.pdf"

def ingest_prod_pdf():
    if not os.path.exists(PDF_PATH):
        print(f"❌ File not found: {PDF_PATH}")
        return

    print(f"🚀 Sending PDF to Cortex Cloud: {os.path.basename(PDF_PATH)}")
    
    with open(PDF_PATH, "rb") as f:
        files = {"file": f}
        try:
            response = requests.post(API_URL, files=files, timeout=600) # Long timeout for processing
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Task ID: {data.get('task_id')}")
                print(f"Filename: {data.get('filename')}")
                print("Processing started in background...")
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Request Failed: {e}")

if __name__ == "__main__":
    ingest_prod_pdf()
