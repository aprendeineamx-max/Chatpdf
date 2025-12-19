
import sys
import os
import re

# Mock the function from main.py
def extract_page_content(full_content: str, page_num: int, page_mapping: dict = None) -> str | None:
    def try_extract(pn: int) -> str | None:
        patterns = [
            rf'--- PAGE {pn}(?: \(PHYSICAL: \d+\))? ---\n(.*?)(?=--- PAGE \d+ ---|$)',
            rf'--- PAGE {pn} ---\n(.*?)(?=--- PAGE \d+ ---|$)',
            rf'=== PÁGINA {pn} \|.*?===\n+(.*?)(?====+ PÁGINA \d+ ===|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, full_content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    # Strategy 1: Exact Match
    content = try_extract(page_num)
    if content:
        print(f"✅ Found exact PAGE {page_num}")
        return content

    # Strategy 2: Page Mapping (if available)
    if page_mapping:
        # Check if page_num exists as a key (string or int)
        # Mapping is usually { "1": 0, "50": 49 } (Physical -> Index)
        # But our markers are usually 1-based index or physical? 
        # The main.py logic tries to use the mapping to find the "Index" page number.
        target_idx = page_mapping.get(str(page_num))
        if target_idx is not None:
             # Our markers might use Index+1 (PAGE 1)
             mapped_pn = target_idx + 1
             print(f"🔄 Mapping Physical {page_num} -> Index-based PAGE {mapped_pn}")
             content = try_extract(mapped_pn)
             if content:
                 return content
    
    print(f"❌ Could not find content for Page {page_num}")
    return None

# Load DB and content
from app.core.database import SessionLocal, AtomicArtifact

db = SessionLocal()
try:
    # Find the pdf_content.txt
    art = db.query(AtomicArtifact).filter(AtomicArtifact.filename == "pdf_content.txt").first()
    if not art:
        print("CRITICAL: No pdf_content.txt found in DB.")
    else:
        print(f"Loaded content ({len(art.content)} chars).")
        
        # Test Page 79
        content = extract_page_content(art.content, 79)
        if content:
             print("\n--- CONTENT PREVIEW ---")
             print(content[:200])
        else:
             print("\n--- SEARCHING FOR NEARBY PAGES ---")
             # Check if Page 78 or 80 exist
             extract_page_content(art.content, 78)
             extract_page_content(art.content, 80)
             
             # Print snippets of markers
             print("\n--- MARKER SNIPPETS ---")
             matches = re.findall(r'--- PAGE \d+', art.content)
             print(f"Found {len(matches)} markers. First 5: {matches[:5]}. Last 5: {matches[-5:]}")

finally:
    db.close()
