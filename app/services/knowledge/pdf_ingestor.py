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
from datetime import datetime
from typing import Dict, Any, Optional
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
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Downloads a PDF from URL and creates knowledge artifacts.
        
        Args:
            url: The PDF URL (direct link, Google Drive, or Dropbox)
            job_id: Unique identifier for this job
            scope: "global" or "session"
            session_id: Required if scope is "session"
            
        Returns:
            Dict with status and context_id
        """
        self.JOBS[job_id] = {
            "status": "INITIALIZING",
            "url": url,
            "start_time": datetime.utcnow().isoformat(),
            "scope": scope,
            "session_id": session_id,
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

            # 4. Extract text content
            self.JOBS[job_id]["status"] = "EXTRACTING"
            text_content = self._extract_text(pdf_path)
            
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
                session_id=session_id
            )

            # 6. Mark as complete
            self.JOBS[job_id]["status"] = "COMPLETED"
            self.JOBS[job_id]["context_id"] = context_id
            
            print(f"✅ [PDFIngestor] Successfully ingested: {pdf_name}")
            return {"status": "success", "context_id": context_id, "name": pdf_name}

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
        
        # Try to get filename from path
        if "/" in path:
            potential_name = path.split("/")[-1]
            if potential_name and "." in potential_name:
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
        """
        text_parts = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc, 1):
                page_text = page.get_text("text")
                if page_text.strip():
                    text_parts.append(f"--- PAGE {page_num} ---\n{page_text}")
            
            doc.close()
            
            if not text_parts:
                return "[No extractable text found in PDF - may be image-based]"
            
            return "\n\n".join(text_parts)
            
        except Exception as e:
            print(f"❌ Text extraction error: {e}")
            return f"[Error extracting text: {e}]"

    def _create_db_entries(
        self, 
        pdf_name: str, 
        pdf_path: str, 
        content: str, 
        scope: str, 
        session_id: Optional[str]
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
