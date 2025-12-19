
import sys
import os
import re

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

    return try_extract(page_num)

from app.core.database import SessionLocal, AtomicArtifact

db = SessionLocal()
try:
    art = db.query(AtomicArtifact).filter(AtomicArtifact.filename == "pdf_content.txt").first()
    if art:
        for p in [50, 79]:
            content = extract_page_content(art.content, p)
            if content:
                print(f"\n=== PAGE {p} PREVIEW ===")
                print(content[:300].replace("\n", " "))
            else:
                print(f"\n❌ PAGE {p} NOT FOUND")
finally:
    db.close()
