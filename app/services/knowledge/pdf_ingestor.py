"""
PDF URL Ingestor Module
=======================
A modular, independent service for downloading and processing PDFs from URLs.
Supports: Direct links, Google Drive, Dropbox.

Pattern: Follows the same architecture as repo_ingestor.py for consistency.
"""

import os
import re
import uuid
import requests
import fitz  # PyMuPDF
import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlparse, parse_qs

from app.core.database import SessionLocal, AtomicContext, AtomicArtifact

# Storage location for downloaded PDFs
SHARED_PDFS_DIR = "data/shared_pdfs"

# Maximum file size (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024


class PDFIngestor:
    """
    Handles downloading PDFs from URLs and extracting their content.
    Creates AtomicContext and AtomicArtifact entries for agent knowledge.
    """

    def __init__(self):
        os.makedirs(SHARED_PDFS_DIR, exist_ok=True)
        # In-memory job tracking: {job_id: {status, url, error, start_time}}
        self.JOBS: Dict[str, Dict[str, Any]] = {}

    def ingest_pdf_url(
        self, 
        url: str, 
        job_id: str, 
        scope: str = "global", 
        session_id: Optional[str] = None,
        rag_mode: str = "injection",  # "injection" or "semantic"
        page_offset: int = 0,         # Manual page offset correction
        enable_ocr: bool = False      # Enable OCR for scanned PDFs
    ) -> Dict[str, Any]:
        """
        Downloads a PDF from URL and creates knowledge artifacts.
        
        Args:
            url: The PDF URL (direct link, Google Drive, or Dropbox)
            job_id: Unique identifier for this job
            scope: "global" or "session"
            session_id: Required if scope is "session"
            rag_mode: "injection" (direct) or "semantic" (embeddings)
            
        Returns:
            Dict with status and context_id
        """
        self.JOBS[job_id] = {
            "status": "INITIALIZING",
            "url": url,
            "start_time": datetime.utcnow().isoformat(),
            "scope": scope,
            "session_id": session_id,
            "rag_mode": rag_mode,  # Track RAG mode in job
            "error": None
        }

        try:
            # 1. Convert cloud storage links to direct download URLs
            download_url = self._normalize_url(url)
            if not download_url:
                raise ValueError("Could not convert URL to downloadable format")

            # 2. Extract filename from URL
            pdf_name = self._extract_filename(url)
            target_dir = os.path.join(SHARED_PDFS_DIR, pdf_name)
            os.makedirs(target_dir, exist_ok=True)
            
            pdf_path = os.path.join(target_dir, "original.pdf")
            content_path = os.path.join(target_dir, "content.txt")

            # 3. Download the PDF
            self.JOBS[job_id]["status"] = "DOWNLOADING"
            success = self._download_pdf(download_url, pdf_path)
            if not success:
                raise Exception("Failed to download PDF")

            # 4. Extract text content with page mapping
            self.JOBS[job_id]["status"] = "EXTRACTING"
            text_content, page_mapping = self._extract_text_with_mapping(pdf_path, page_offset)
            
            # 4.5 Apply OCR for page number detection if enabled
            if enable_ocr:
                self.JOBS[job_id]["status"] = "OCR_PROCESSING"
                try:
                    from app.services.knowledge.ocr_service import ocr_service
                    ocr_mapping = ocr_service.extract_page_numbers_from_pdf(
                        pdf_path, engine="hybrid", extract_areas="both"
                    )
                    # Merge OCR mapping with text-based mapping (OCR takes priority)
                    page_mapping.update(ocr_mapping)
                    print(f"🔍 [PDFIngestor] OCR detected {len(ocr_mapping)} page numbers")
                except Exception as ocr_err:
                    print(f"⚠️ [PDFIngestor] OCR warning: {ocr_err}")
            
            # Save extracted text
            with open(content_path, "w", encoding="utf-8") as f:
                f.write(text_content)

            # 5. Create database entries
            self.JOBS[job_id]["status"] = "INDEXING"
            context_id = self._create_db_entries(
                pdf_name=pdf_name,
                pdf_path=pdf_path,
                content=text_content,
                scope=scope,
                session_id=session_id,
                page_mapping=page_mapping  # NEW: Pass page mapping
            )

            # 6. Create vector embeddings if semantic RAG mode
            if rag_mode == "semantic":
                self.JOBS[job_id]["status"] = "EMBEDDING"
                try:
                    from app.services.knowledge.vector_store import vector_store
                    num_chunks = vector_store.ingest_document(
                        doc_id=context_id,
                        text=text_content,
                        metadata={
                            "pdf_name": pdf_name,
                            "session_id": session_id,
                            "scope": scope
                        }
                    )
                    print(f"🔍 [PDFIngestor] Created {num_chunks} semantic chunks")
                except Exception as embed_err:
                    print(f"⚠️ [PDFIngestor] Embedding warning: {embed_err}")
                    # Continue even if embedding fails - still have full text

            # 7. Mark as complete
            self.JOBS[job_id]["status"] = "COMPLETED"
            self.JOBS[job_id]["context_id"] = context_id
            
            print(f"✅ [PDFIngestor] Successfully ingested: {pdf_name} (mode: {rag_mode})")
            return {"status": "success", "context_id": context_id, "name": pdf_name, "rag_mode": rag_mode}

        except Exception as e:
            self.JOBS[job_id]["status"] = "FAILED"
            self.JOBS[job_id]["error"] = str(e)
            print(f"❌ [PDFIngestor] Error: {e}")
            return {"status": "error", "error": str(e)}

    def _normalize_url(self, url: str) -> Optional[str]:
        """
        Converts Google Drive, Dropbox links to direct download URLs.
        Returns original URL if it's already a direct link.
        """
        # Google Drive: Convert share link to direct download
        # Format: https://drive.google.com/file/d/{FILE_ID}/view
        # Direct: https://drive.google.com/uc?export=download&id={FILE_ID}
        if "drive.google.com" in url:
            # Try to extract file ID
            patterns = [
                r'/file/d/([a-zA-Z0-9_-]+)',
                r'id=([a-zA-Z0-9_-]+)',
                r'/d/([a-zA-Z0-9_-]+)'
            ]
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    file_id = match.group(1)
                    return f"https://drive.google.com/uc?export=download&id={file_id}"
            return None

        # Dropbox: Replace dl=0 with dl=1 for direct download
        if "dropbox.com" in url:
            if "dl=0" in url:
                return url.replace("dl=0", "dl=1")
            elif "dl=1" not in url:
                return url + ("&dl=1" if "?" in url else "?dl=1")
            return url

        # OneDrive: Convert share link to direct download
        if "1drv.ms" in url or "onedrive.live.com" in url:
            # OneDrive links need special handling
            # For now, we'll try to use them directly
            return url

        # Direct link - return as-is
        return url

    def _extract_filename(self, url: str) -> str:
        """
        Extracts a clean filename from the URL.
        """
        parsed = urlparse(url)
        path = parsed.path
        
        # [FIX] Handle Google Drive URLs: /file/d/{FILE_ID}/view
        # The last segment "view" is not a filename, so we need special handling
        if "drive.google.com" in url and "/file/d/" in url:
            # Extract the file ID from the path
            parts = path.split("/")
            for i, part in enumerate(parts):
                if part == "d" and i + 1 < len(parts):
                    file_id = parts[i + 1]
                    return f"pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Try to get filename from path
        if "/" in path:
            potential_name = path.split("/")[-1]
            # Skip common non-filename endings
            if potential_name and potential_name not in ["view", "preview", "download", ""]:
                if "." in potential_name:
                    # Remove extension and clean
                    name = potential_name.rsplit(".", 1)[0]
                    return self._sanitize_name(name)
        
        # Try query parameters
        query = parse_qs(parsed.query)
        if "id" in query:
            return f"gdrive_{query['id'][0][:8]}"
        
        # Fallback to timestamp
        return f"pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _sanitize_name(self, name: str) -> str:
        """
        Removes invalid characters from filename.
        """
        # Remove invalid chars
        name = re.sub(r'[<>:"/\\|?*]', '', name)
        # Replace spaces with underscores
        name = name.replace(" ", "_")
        # Limit length
        return name[:50] if len(name) > 50 else name

    def _download_pdf(self, url: str, target_path: str) -> bool:
        """
        Downloads PDF from URL to target path.
        Returns True on success.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get("Content-Type", "")
            if "application/pdf" not in content_type and "octet-stream" not in content_type:
                print(f"⚠️ Warning: Content-Type is {content_type}, may not be a PDF")
            
            # Check file size
            content_length = int(response.headers.get("Content-Length", 0))
            if content_length > MAX_FILE_SIZE:
                raise ValueError(f"File too large: {content_length / 1024 / 1024:.1f}MB (max: 50MB)")
            
            # Write to file
            with open(target_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
            
        except requests.RequestException as e:
            print(f"❌ Download error: {e}")
            return False

    def _extract_text(self, pdf_path: str) -> str:
        """
        Extracts text content from PDF using PyMuPDF.
        Legacy method - kept for backwards compatibility.
        """
        text_content, _ = self._extract_text_with_mapping(pdf_path, 0)
        return text_content
    
    def _extract_text_with_mapping(self, pdf_path: str, page_offset: int = 0) -> Tuple[str, Dict[int, int]]:
        """
        Extracts text content from PDF and creates page number mapping.
        
        Args:
            pdf_path: Path to the PDF file
            page_offset: Manual offset to apply to page numbers
        
        Returns:
            Tuple of (text_content, page_mapping)
            page_mapping: {physical_page_number: pymupdf_index}
        """
        text_parts = []
        page_mapping: Dict[int, int] = {}
        
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            for page_num, page in enumerate(doc, 1):
                page_text = page.get_text("text")
                
                if page_text.strip():
                    # Detect physical page number in text
                    physical_num = self._detect_page_number(page_text, page_num)
                    
                    # Apply manual offset if provided
                    if page_offset != 0:
                        adjusted_num = page_num + page_offset
                        if adjusted_num > 0:
                            page_mapping[adjusted_num] = page_num
                    elif physical_num:
                        page_mapping[physical_num] = page_num
                    
                    # Create page marker with both indices
                    physical_info = f" (PHYSICAL: {physical_num})" if physical_num else ""
                    text_parts.append(f"--- PAGE {page_num}{physical_info} ---\n{page_text}")
            
            doc.close()
            
            if not text_parts:
                return "[No extractable text found in PDF - may be image-based]", {}
            
            print(f"📄 [PDFIngestor] Extracted {len(text_parts)} pages, mapped {len(page_mapping)} physical numbers")
            return "\n\n".join(text_parts), page_mapping
            
        except Exception as e:
            print(f"❌ Text extraction error: {e}")
            return f"[Error extracting text: {e}]", {}
    
    def _detect_page_number(self, page_text: str, pymupdf_index: int) -> Optional[int]:
        """
        Tries to detect physical page number from page text content.
        Looks for standalone numbers in footers/headers.
        
        Args:
            page_text: Text content of the page
            pymupdf_index: The PyMuPDF page index (for reference)
        
        Returns:
            Detected physical page number or None
        """
        if not page_text:
            return None
        
        # Pattern 1: Number at end of page (footer) - most common
        last_100 = page_text[-100:].strip() if len(page_text) > 100 else page_text.strip()
        match = re.search(r'\b(\d{1,3})\s*$', last_100)
        if match:
            num = int(match.group(1))
            # Validate: should be a reasonable page number
            if 1 <= num <= 999:
                return num
        
        # Pattern 2: Number at start of page (header)
        first_50 = page_text[:50].strip()
        match = re.search(r'^\s*(\d{1,3})\b', first_50)
        if match:
            num = int(match.group(1))
            if 1 <= num <= 999:
                return num
        
        # Pattern 3: "Página X" or "- X -" patterns
        patterns = [
            r'[Pp][aá]gina\s*(\d{1,3})',
            r'[Pp]age\s*(\d{1,3})',
            r'-\s*(\d{1,3})\s*-',
        ]
        for pattern in patterns:
            match = re.search(pattern, page_text[-200:] if len(page_text) > 200 else page_text)
            if match:
                num = int(match.group(1))
                if 1 <= num <= 999:
                    return num
        
        return None

    def _create_db_entries(
        self, 
        pdf_name: str, 
        pdf_path: str, 
        content: str, 
        scope: str, 
        session_id: Optional[str],
        page_mapping: Dict[int, int] = None  # NEW: Physical page -> PyMuPDF index
    ) -> str:
        """
        Creates AtomicContext and AtomicArtifact entries in the database.
        Returns the context_id.
        """
        db = SessionLocal()
        try:
            context_id = str(uuid.uuid4())
            
            # Create context (like a folder)
            context = AtomicContext(
                id=context_id,
                folder_name=f"PDF: {pdf_name}",
                batch_id=f"pdf-{datetime.now().strftime('%Y%m%d')}",
                scope=scope,
                session_id=session_id,
                timestamp=datetime.utcnow()
            )
            db.add(context)
            
            # Create artifact for the FULL content (no truncation)
            # Store entire PDF text so agent has access to everything
            artifact = AtomicArtifact(
                id=str(uuid.uuid4()),
                context_id=context_id,
                filename="pdf_content.txt",
                content=content,  # [FIX] Store FULL content, no limit
                local_path=pdf_path
            )
            db.add(artifact)
            
            # Create a summary artifact (first 5000 chars for overview)
            summary = content[:5000] if len(content) > 5000 else content
            summary_artifact = AtomicArtifact(
                id=str(uuid.uuid4()),
                context_id=context_id,
                filename="pdf_summary.txt",
                content=f"PDF Summary for {pdf_name} ({len(content)} caracteres totales):\n\n{summary}",
                local_path=pdf_path
            )
            db.add(summary_artifact)
            
            # NEW: Create page mapping artifact if available
            if page_mapping:
                mapping_artifact = AtomicArtifact(
                    id=str(uuid.uuid4()),
                    context_id=context_id,
                    filename="page_mapping.json",
                    content=json.dumps(page_mapping, indent=2),
                    local_path=pdf_path
                )
                db.add(mapping_artifact)
                print(f"📄 [PDFIngestor] Created page mapping with {len(page_mapping)} entries")
            
            db.commit()
            return context_id
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_active_jobs(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns all tracked jobs.
        """
        return self.JOBS

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Returns status for a specific job.
        """
        return self.JOBS.get(job_id)


# Singleton instance
pdf_ingestor = PDFIngestor()
