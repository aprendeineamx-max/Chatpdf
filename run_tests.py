"""
Comprehensive System Verification Tests
Tests: API, PDF Ingestion, Queries, Page Extraction, Session Isolation
"""
import requests
import time
import json
import uuid
import sys

# Redirect output to file
output_file = open("test_results.txt", "w", encoding="utf-8")
class Tee:
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()

sys.stdout = Tee(sys.stdout, output_file)
import requests
import time
import json
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_result(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"       {details[:200]}")
    return passed

def run_tests():
    results = []
    
    print("\n" + "="*60)
    print("🧪 COMPREHENSIVE SYSTEM VERIFICATION")
    print("="*60 + "\n")
    
    # TEST 1: API Health
    print("--- Test 1: API Health Check ---")
    try:
        r = requests.get(f"{BASE_URL}/ingest/list", timeout=10)
        results.append(test_result("API /ingest/list responds", r.status_code == 200, f"Status: {r.status_code}"))
    except Exception as e:
        results.append(test_result("API /ingest/list responds", False, str(e)))
    
    # TEST 2: New session has empty KNOWLEDGE panel
    print("\n--- Test 2: New Session Isolation ---")
    new_session_id = str(uuid.uuid4())
    try:
        r = requests.get(f"{BASE_URL}/ingest/list?session_id={new_session_id}", timeout=10)
        data = r.json()
        is_empty = len(data) == 0 if isinstance(data, list) else True
        results.append(test_result("New session has empty KNOWLEDGE", is_empty, f"Items: {len(data) if isinstance(data, list) else 'N/A'}"))
    except Exception as e:
        results.append(test_result("New session has empty KNOWLEDGE", False, str(e)))
    
    # TEST 3: Query without WRITE_FILE
    print("\n--- Test 3: Response Without WRITE_FILE ---")
    try:
        r = requests.post(f"{BASE_URL}/query", json={
            "query_text": "¿Qué sabes hacer?",
            "session_id": new_session_id,
            "rag_mode": "injection"
        }, timeout=60)
        data = r.json()
        answer = data.get("answer", "")
        has_write_file = "WRITE_FILE" in answer or "END_WRITE" in answer
        results.append(test_result("Response has NO WRITE_FILE", not has_write_file, f"Answer preview: {answer[:100]}..."))
    except Exception as e:
        results.append(test_result("Response has NO WRITE_FILE", False, str(e)))
    
    # TEST 4: Query with existing PDF (tracemonkey - global)
    print("\n--- Test 4: PDF Content Injection (Global PDF) ---")
    try:
        r = requests.post(f"{BASE_URL}/query", json={
            "query_text": "What is TraceMonkey about?",
            "session_id": new_session_id,
            "rag_mode": "injection"
        }, timeout=90)
        data = r.json()
        answer = data.get("answer", "").lower()
        # TraceMonkey is about JavaScript tracing/compilation
        has_js_content = "javascript" in answer or "trace" in answer or "compiler" in answer
        results.append(test_result("Global PDF content injected", has_js_content, f"Answer preview: {answer[:150]}..."))
    except Exception as e:
        results.append(test_result("Global PDF content injected", False, str(e)))
    
    # TEST 5: Page extraction (page 3 from tracemonkey)
    print("\n--- Test 5: Page Extraction ---")
    try:
        r = requests.post(f"{BASE_URL}/query", json={
            "query_text": "What is the content of page 3?",
            "session_id": new_session_id,
            "rag_mode": "injection"
        }, timeout=90)
        data = r.json()
        answer = data.get("answer", "").lower()
        # Page 3 has LIR code with js_Array_set
        has_page3_content = "lir" in answer or "array" in answer or "exit" in answer or "trace" in answer
        results.append(test_result("Page 3 content extracted", has_page3_content, f"Answer preview: {answer[:150]}..."))
    except Exception as e:
        results.append(test_result("Page 3 content extracted", False, str(e)))
    
    # TEST 6: Session-specific PDF ingestion
    print("\n--- Test 6: PDF Ingestion API ---")
    try:
        test_session = str(uuid.uuid4())
        r = requests.post(f"{BASE_URL}/ingest/pdf", json={
            "url": "https://mozilla.github.io/pdf.js/web/compressed.tracemonkey-pldi-09.pdf",
            "scope": "session",
            "session_id": test_session,
            "rag_mode": "injection"
        }, timeout=30)
        results.append(test_result("PDF ingestion API works", r.status_code == 200, f"Status: {r.status_code}"))
    except Exception as e:
        results.append(test_result("PDF ingestion API works", False, str(e)))
    
    # TEST 7: Check chat sessions API
    print("\n--- Test 7: Chat Sessions API ---")
    try:
        r = requests.get(f"{BASE_URL}/chat/sessions", timeout=10)
        results.append(test_result("Chat sessions API works", r.status_code == 200, f"Status: {r.status_code}"))
    except Exception as e:
        results.append(test_result("Chat sessions API works", False, str(e)))
    
    # SUMMARY
    print("\n" + "="*60)
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️ Some tests failed. Review above for details.")
    
    return passed == total

if __name__ == "__main__":
    run_tests()
