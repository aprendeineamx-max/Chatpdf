import fitz  # PyMuPDF
import os
from pathlib import Path
from typing import List, Dict, Any
import logging

# Config logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, storage_dir: str = "data/processed"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def process_pdf(self, pdf_path: str, pdf_id: str) -> Dict[str, Any]:
        """
        Procesa un PDF completo:
        1. Genera imágenes para cada página.
        2. Extrae texto.
        3. (Futuro) Genera Markdown estructurado.
        """
        doc = fitz.open(pdf_path)
        
        # Estructura de salida
        output_base = self.storage_dir / pdf_id
        images_dir = output_base / "images"
        text_dir = output_base / "text"
        
        images_dir.mkdir(parents=True, exist_ok=True)
        text_dir.mkdir(parents=True, exist_ok=True)
        
        manifest = {
            "pdf_id": pdf_id,
            "total_pages": len(doc),
            "pages": []
        }

        logger.info(f"Procesando PDF {pdf_id} con {len(doc)} páginas...")

        for page_num, page in enumerate(doc):
            # 1. Guardar Imagen (High Quality)
            # Zoom = 2 (200%) para mejor OCR/Visión
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)
            image_filename = f"page_{page_num + 1}.png"
            image_path = images_dir / image_filename
            pix.save(str(image_path))
            
            # 2. Extraer Texto Base
            text_content = page.get_text()
            text_filename = f"page_{page_num + 1}.txt"
            text_path = text_dir / text_filename
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(text_content)
                
            manifest["pages"].append({
                "page_number": page_num + 1,
                "image_path": str(image_path),
                "text_path": str(text_path)
            })
            
        logger.info(f"Procesamiento completado para {pdf_id}")
        
        # 3. Trigger RAG Indexing (Auto-Index)
        try:
            from app.services.rag.engine import rag_service
            rag_service.index_document(str(text_dir), pdf_id)
        except Exception as e:
            logger.error(f"RAG Indexing Failed: {e}")
            
        return manifest
