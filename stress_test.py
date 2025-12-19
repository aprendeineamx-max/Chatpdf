"""
COMPREHENSIVE STRESS TEST SUITE
Tests all system functions with multiple iterations
"""
import requests
import time
import json
import uuid
import concurrent.futures
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"
FRONTEND_URL = "http://127.0.0.1:5173"

# Output to file
output_file = open("stress_test_results.txt", "w", encoding="utf-8")
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

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def test_result(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    log(f"{status}: {name}")
    if details:
        log(f"       {details[:300]}")
    return passed

def run_stress_tests():
    results = []
    start_time = time.time()
    
    log("\n" + "="*70)
    log("🔥 COMPREHENSIVE STRESS TEST SUITE")
    log("="*70 + "\n")
    
    # ========================================
    # PHASE 1: Server Health Checks
    # ========================================
    log("\n--- PHASE 1: Server Health (10 iterations) ---")
    for i in range(10):
        try:
            r1 = requests.get(f"{BASE_URL}/ingest/list", timeout=10)
            r2 = requests.get(f"{FRONTEND_URL}/", timeout=10)
            passed = r1.status_code == 200 and r2.status_code == 200
            if i == 0 or i == 9:
                results.append(test_result(f"Health Check {i+1}/10", passed, f"Backend:{r1.status_code} Frontend:{r2.status_code}"))
        except Exception as e:
            results.append(test_result(f"Health Check {i+1}/10", False, str(e)))
        time.sleep(0.2)
    
    # ========================================
    # PHASE 2: Session Isolation Tests
    # ========================================
    log("\n--- PHASE 2: Session Isolation (5 sessions) ---")
    sessions = [str(uuid.uuid4()) for _ in range(5)]
    for i, sid in enumerate(sessions):
        try:
            r = requests.get(f"{BASE_URL}/ingest/list?session_id={sid}", timeout=10)
            data = r.json()
            is_empty = len(data) == 0 if isinstance(data, list) else True
            results.append(test_result(f"Session {i+1} Isolation", is_empty, f"Items: {len(data) if isinstance(data, list) else 'error'}"))
        except Exception as e:
            results.append(test_result(f"Session {i+1} Isolation", False, str(e)))
    
    # ========================================
    # PHASE 3: Query Tests (No WRITE_FILE)
    # ========================================
    log("\n--- PHASE 3: Query Response Quality (5 iterations) ---")
    test_queries = [
        "¿Qué sabes hacer?",
        "Hola, ¿cómo estás?",
        "Explain your capabilities",
        "¿Cuál es tu función?",
        "What can you help me with?"
    ]
    for i, query in enumerate(test_queries):
        try:
            r = requests.post(f"{BASE_URL}/query", json={
                "query_text": query,
                "session_id": sessions[0],
                "rag_mode": "injection"
            }, timeout=90)
            data = r.json()
            answer = data.get("answer", "")
            has_write = "WRITE_FILE" in answer or "END_WRITE" in answer
            results.append(test_result(f"Query {i+1} No WRITE_FILE", not has_write, f"Query: '{query[:30]}...' Answer: {answer[:80]}..."))
        except Exception as e:
            results.append(test_result(f"Query {i+1} No WRITE_FILE", False, str(e)))
    
    # ========================================
    # PHASE 4: PDF Content Tests
    # ========================================
    log("\n--- PHASE 4: PDF Content Injection (3 queries) ---")
    pdf_queries = [
        ("What is TraceMonkey?", ["javascript", "trace", "compiler"]),
        ("What is the main topic of the document?", ["trace", "javascript", "compilation", "type"]),
        ("Explain the abstract of the paper", ["dynamic", "language", "javascript", "trace"])
    ]
    for i, (query, keywords) in enumerate(pdf_queries):
        try:
            r = requests.post(f"{BASE_URL}/query", json={
                "query_text": query,
                "session_id": sessions[0],
                "rag_mode": "injection"
            }, timeout=90)
            data = r.json()
            answer = data.get("answer", "").lower()
            has_content = any(kw in answer for kw in keywords)
            results.append(test_result(f"PDF Content {i+1}: {query[:25]}...", has_content, f"Found keywords: {[k for k in keywords if k in answer]}"))
        except Exception as e:
            results.append(test_result(f"PDF Content {i+1}", False, str(e)))
    
    # ========================================
    # PHASE 5: Page Extraction Tests
    # ========================================
    log("\n--- PHASE 5: Page Extraction (Pages 1-5) ---")
    page_keywords = {
        1: ["trace", "javascript", "dynamic", "languages", "abstract"],
        2: ["trace", "tree", "loop", "iteration"],
        3: ["lir", "array", "state", "exit"],
        4: ["iteration", "side exit", "guard"],
        5: ["trace", "type", "trees"]
    }
    for page, keywords in page_keywords.items():
        try:
            r = requests.post(f"{BASE_URL}/query", json={
                "query_text": f"What is the exact content of page {page}?",
                "session_id": sessions[0],
                "rag_mode": "injection"
            }, timeout=90)
            data = r.json()
            answer = data.get("answer", "").lower()
            has_content = any(kw in answer for kw in keywords)
            results.append(test_result(f"Page {page} Extraction", has_content, f"Keywords found: {[k for k in keywords if k in answer][:3]}"))
        except Exception as e:
            results.append(test_result(f"Page {page} Extraction", False, str(e)))
    
    # ========================================
    # PHASE 6: PDF Ingestion Test
    # ========================================
    log("\n--- PHASE 6: PDF Ingestion API ---")
    try:
        test_session = str(uuid.uuid4())
        r = requests.post(f"{BASE_URL}/ingest/pdf", json={
            "url": "https://mozilla.github.io/pdf.js/web/compressed.tracemonkey-pldi-09.pdf",
            "scope": "session",
            "session_id": test_session,
            "rag_mode": "injection",
            "page_offset": 0,
            "enable_ocr": False
        }, timeout=30)
        results.append(test_result("PDF Ingestion API", r.status_code == 200, f"Status: {r.status_code}"))
    except Exception as e:
        results.append(test_result("PDF Ingestion API", False, str(e)))
    
    # ========================================
    # PHASE 7: Concurrent Requests Test
    # ========================================
    log("\n--- PHASE 7: Concurrent Requests (10 parallel) ---")
    def make_request(i):
        try:
            r = requests.get(f"{BASE_URL}/ingest/list?session_id={uuid.uuid4()}", timeout=15)
            return r.status_code == 200
        except:
            return False
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, i) for i in range(10)]
        concurrent_results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    passed_concurrent = sum(concurrent_results)
    results.append(test_result("Concurrent Requests", passed_concurrent >= 8, f"{passed_concurrent}/10 succeeded"))
    
    # ========================================
    # PHASE 8: Chat Session Management
    # ========================================
    log("\n--- PHASE 8: Chat Session Flow ---")
    try:
        # Create a session flow
        session = str(uuid.uuid4())
        
        # First query
        r1 = requests.post(f"{BASE_URL}/query", json={
            "query_text": "Hola, mi nombre es Carlos",
            "session_id": session,
            "rag_mode": "injection"
        }, timeout=60)
        results.append(test_result("Chat Flow: Initial message", r1.status_code == 200))
        
        # Second query
        r2 = requests.post(f"{BASE_URL}/query", json={
            "query_text": "What programming language is TraceMonkey about?",
            "session_id": session,
            "rag_mode": "injection"
        }, timeout=60)
        answer2 = r2.json().get("answer", "").lower()
        results.append(test_result("Chat Flow: PDF query", "javascript" in answer2, f"Contains 'javascript': {'javascript' in answer2}"))
        
    except Exception as e:
        results.append(test_result("Chat Flow", False, str(e)))
    
    # ========================================
    # PHASE 9: Error Handling
    # ========================================
    log("\n--- PHASE 9: Error Handling ---")
    try:
        # Invalid session (should not crash)
        r = requests.get(f"{BASE_URL}/ingest/list?session_id=invalid-uuid-format", timeout=10)
        results.append(test_result("Error: Invalid session", r.status_code in [200, 400], f"Status: {r.status_code}"))
        
        # Empty query
        r = requests.post(f"{BASE_URL}/query", json={
            "query_text": "",
            "session_id": str(uuid.uuid4()),
            "rag_mode": "injection"
        }, timeout=30)
        results.append(test_result("Error: Empty query", r.status_code in [200, 400, 422], f"Status: {r.status_code}"))
        
    except Exception as e:
        results.append(test_result("Error Handling", False, str(e)))
    
    # ========================================
    # SUMMARY
    # ========================================
    elapsed = time.time() - start_time
    passed = sum(1 for r in results if r)
    total = len(results)
    
    log("\n" + "="*70)
    log(f"📊 FINAL RESULTS: {passed}/{total} tests passed ({100*passed/total:.1f}%)")
    log(f"⏱️ Total time: {elapsed:.1f} seconds")
    log("="*70)
    
    if passed == total:
        log("🎉 ALL TESTS PASSED! System is 100% functional.")
    elif passed >= total * 0.9:
        log("✅ System is working well (>90% pass rate)")
    elif passed >= total * 0.7:
        log("⚠️ Some issues detected (70-90% pass rate)")
    else:
        log("❌ Significant issues detected (<70% pass rate)")
    
    return passed == total

if __name__ == "__main__":
    run_stress_tests()
    output_file.close()
