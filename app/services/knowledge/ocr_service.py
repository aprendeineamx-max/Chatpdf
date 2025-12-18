"""
Multi-Engine OCR Service
========================
Supports multiple OCR engines for extracting page numbers from PDF images:
- Tesseract (basic, fast)
- EasyOCR (medium, good accuracy)
- PaddleOCR (advanced, best for complex layouts)
- Hybrid (combines best results from all engines)

Author: PDF-Cortex Team
"""
import os
import re
import io
from typing import Optional, Dict, List, Tuple, Any
from abc import ABC, abstractmethod
from datetime import datetime
import json

# Lazy imports for OCR engines (only load when needed)
_tesseract = None
_easyocr_reader = None
_paddle_ocr = None


def _get_tesseract():
    """Lazy import for pytesseract."""
    global _tesseract
    if _tesseract is None:
        try:
            import pytesseract
            _tesseract = pytesseract
            print("✅ [OCR] Tesseract engine loaded")
        except ImportError:
            print("⚠️ [OCR] pytesseract not installed. Run: pip install pytesseract")
    return _tesseract


def _get_easyocr(languages=['es', 'en']):
    """Lazy import for easyocr."""
    global _easyocr_reader
    if _easyocr_reader is None:
        try:
            import easyocr
            _easyocr_reader = easyocr.Reader(languages, gpu=False)
            print("✅ [OCR] EasyOCR engine loaded")
        except ImportError:
            print("⚠️ [OCR] easyocr not installed. Run: pip install easyocr")
    return _easyocr_reader


def _get_paddleocr():
    """Lazy import for paddleocr."""
    global _paddle_ocr
    if _paddle_ocr is None:
        try:
            from paddleocr import PaddleOCR
            _paddle_ocr = PaddleOCR(lang='es', use_angle_cls=True, show_log=False)
            print("✅ [OCR] PaddleOCR engine loaded")
        except ImportError:
            print("⚠️ [OCR] paddleocr not installed. Run: pip install paddleocr paddlepaddle")
    return _paddle_ocr


class OCREngine(ABC):
    """Abstract base class for OCR engines."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this engine is installed and working."""
        pass
    
    @abstractmethod
    def extract_text_from_image(self, image) -> str:
        """Extract all text from an image."""
        pass
    
    def extract_page_number(self, image, search_area: str = "footer") -> Optional[int]:
        """
        Extract page number from image.
        
        Args:
            image: PIL Image or numpy array
            search_area: "footer", "header", or "both"
        
        Returns:
            Detected page number or None
        """
        try:
            text = self.extract_text_from_image(image)
            return self._find_page_number_in_text(text)
        except Exception as e:
            print(f"⚠️ [{self.name}] Page number extraction error: {e}")
            return None
    
    def _find_page_number_in_text(self, text: str) -> Optional[int]:
        """Find standalone page number in text."""
        if not text:
            return None
        
        # Clean text
        text = text.strip()
        
        # Pattern 1: Standalone number at end (page footer)
        match = re.search(r'\b(\d{1,3})\s*$', text)
        if match:
            num = int(match.group(1))
            if 1 <= num <= 999:  # Reasonable page range
                return num
        
        # Pattern 2: Standalone number at start (page header)
        match = re.search(r'^\s*(\d{1,3})\b', text)
        if match:
            num = int(match.group(1))
            if 1 <= num <= 999:
                return num
        
        # Pattern 3: "Página X" or "Page X"
        match = re.search(r'(?:p[aá]gina|page)\s*(\d{1,3})\b', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        return None


class TesseractEngine(OCREngine):
    """Tesseract OCR engine - fast and reliable for clear text."""
    
    @property
    def name(self) -> str:
        return "Tesseract"
    
    def is_available(self) -> bool:
        return _get_tesseract() is not None
    
    def extract_text_from_image(self, image) -> str:
        tesseract = _get_tesseract()
        if not tesseract:
            return ""
        
        try:
            from PIL import Image
            if not isinstance(image, Image.Image):
                image = Image.fromarray(image)
            
            # Use Spanish + English
            text = tesseract.image_to_string(image, lang='spa+eng')
            return text
        except Exception as e:
            print(f"⚠️ [Tesseract] Error: {e}")
            return ""


class EasyOCREngine(OCREngine):
    """EasyOCR engine - good accuracy, supports multiple languages."""
    
    @property
    def name(self) -> str:
        return "EasyOCR"
    
    def is_available(self) -> bool:
        return _get_easyocr() is not None
    
    def extract_text_from_image(self, image) -> str:
        reader = _get_easyocr()
        if not reader:
            return ""
        
        try:
            import numpy as np
            from PIL import Image
            
            if isinstance(image, Image.Image):
                image = np.array(image)
            
            results = reader.readtext(image)
            # Combine all detected text
            text_parts = [item[1] for item in results]
            return " ".join(text_parts)
        except Exception as e:
            print(f"⚠️ [EasyOCR] Error: {e}")
            return ""


class PaddleOCREngine(OCREngine):
    """PaddleOCR engine - best for complex layouts and tables."""
    
    @property
    def name(self) -> str:
        return "PaddleOCR"
    
    def is_available(self) -> bool:
        return _get_paddleocr() is not None
    
    def extract_text_from_image(self, image) -> str:
        ocr = _get_paddleocr()
        if not ocr:
            return ""
        
        try:
            import numpy as np
            from PIL import Image
            
            if isinstance(image, Image.Image):
                image = np.array(image)
            
            results = ocr.ocr(image, cls=True)
            if not results or not results[0]:
                return ""
            
            text_parts = [line[1][0] for line in results[0]]
            return " ".join(text_parts)
        except Exception as e:
            print(f"⚠️ [PaddleOCR] Error: {e}")
            return ""


class HybridOCREngine(OCREngine):
    """
    Hybrid engine that uses multiple OCR engines and selects best result.
    Strategy: Try all available engines, use consensus or highest confidence.
    """
    
    def __init__(self):
        self.engines: List[OCREngine] = []
        
        # Initialize available engines
        if TesseractEngine().is_available():
            self.engines.append(TesseractEngine())
        if EasyOCREngine().is_available():
            self.engines.append(EasyOCREngine())
        if PaddleOCREngine().is_available():
            self.engines.append(PaddleOCREngine())
        
        if self.engines:
            names = [e.name for e in self.engines]
            print(f"🔀 [HybridOCR] Initialized with engines: {', '.join(names)}")
    
    @property
    def name(self) -> str:
        return "Hybrid"
    
    def is_available(self) -> bool:
        return len(self.engines) > 0
    
    def extract_text_from_image(self, image) -> str:
        """Combine text from all engines."""
        all_text = []
        for engine in self.engines:
            text = engine.extract_text_from_image(image)
            if text:
                all_text.append(text)
        return " | ".join(all_text)
    
    def extract_page_number(self, image, search_area: str = "footer") -> Optional[int]:
        """Try all engines and return consensus."""
        results = {}
        
        for engine in self.engines:
            num = engine.extract_page_number(image, search_area)
            if num is not None:
                results[engine.name] = num
        
        if not results:
            return None
        
        # If all engines agree, return that number
        values = list(results.values())
        if len(set(values)) == 1:
            return values[0]
        
        # Return most common result
        from collections import Counter
        counter = Counter(values)
        most_common = counter.most_common(1)[0][0]
        print(f"🔀 [HybridOCR] Engines disagreed: {results}, using: {most_common}")
        return most_common


class OCRService:
    """
    Main OCR service for PDF page number extraction.
    Manages multiple OCR engines and provides high-level API.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.engines: Dict[str, OCREngine] = {}
        self._init_engines()
        self._initialized = True
    
    def _init_engines(self):
        """Initialize all available OCR engines."""
        print("🔧 [OCRService] Initializing OCR engines...")
        
        # Add each engine if available
        tesseract = TesseractEngine()
        if tesseract.is_available():
            self.engines["tesseract"] = tesseract
        
        easyocr = EasyOCREngine()
        if easyocr.is_available():
            self.engines["easyocr"] = easyocr
        
        paddle = PaddleOCREngine()
        if paddle.is_available():
            self.engines["paddleocr"] = paddle
        
        hybrid = HybridOCREngine()
        if hybrid.is_available():
            self.engines["hybrid"] = hybrid
        
        print(f"✅ [OCRService] Available engines: {list(self.engines.keys())}")
    
    def get_available_engines(self) -> List[str]:
        """Return list of available OCR engine names."""
        return list(self.engines.keys())
    
    def extract_page_numbers_from_pdf(
        self,
        pdf_path: str,
        engine: str = "hybrid",
        extract_areas: str = "footer"  # "footer", "header", "both"
    ) -> Dict[int, int]:
        """
        Extract physical page numbers from PDF using OCR.
        
        Args:
            pdf_path: Path to the PDF file
            engine: OCR engine to use ("tesseract", "easyocr", "paddleocr", "hybrid")
            extract_areas: Where to look for page numbers
        
        Returns:
            Dict mapping physical page number -> PyMuPDF index
        """
        import fitz  # PyMuPDF
        from PIL import Image
        
        if engine not in self.engines:
            available = list(self.engines.keys())
            if not available:
                print("❌ [OCRService] No OCR engines available")
                return {}
            engine = available[0]
            print(f"⚠️ [OCRService] Engine '{engine}' not available, using: {available[0]}")
        
        ocr_engine = self.engines[engine]
        page_mapping: Dict[int, int] = {}
        
        print(f"📄 [OCRService] Processing PDF with {engine} engine...")
        
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            for page_idx in range(total_pages):
                page = doc[page_idx]
                pymupdf_index = page_idx + 1  # 1-indexed
                
                # Render page to image
                mat = fitz.Matrix(2, 2)  # 2x zoom for better OCR
                
                # Extract footer region (bottom 100 pixels)
                if extract_areas in ("footer", "both"):
                    footer_rect = fitz.Rect(
                        0, 
                        page.rect.height - 50, 
                        page.rect.width, 
                        page.rect.height
                    )
                    pix = page.get_pixmap(matrix=mat, clip=footer_rect)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    page_num = ocr_engine.extract_page_number(img, "footer")
                    if page_num is not None:
                        page_mapping[page_num] = pymupdf_index
                        print(f"  📄 Physical page {page_num} → PyMuPDF index {pymupdf_index}")
                        continue
                
                # Extract header region (top 50 pixels)
                if extract_areas in ("header", "both"):
                    header_rect = fitz.Rect(
                        0, 0,
                        page.rect.width, 50
                    )
                    pix = page.get_pixmap(matrix=mat, clip=header_rect)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    page_num = ocr_engine.extract_page_number(img, "header")
                    if page_num is not None:
                        page_mapping[page_num] = pymupdf_index
                        print(f"  📄 Physical page {page_num} → PyMuPDF index {pymupdf_index}")
            
            doc.close()
            print(f"✅ [OCRService] Extracted {len(page_mapping)} page mappings")
            
        except Exception as e:
            print(f"❌ [OCRService] Error processing PDF: {e}")
        
        return page_mapping
    
    def extract_text_from_pdf_page(
        self,
        pdf_path: str,
        page_index: int,
        engine: str = "hybrid"
    ) -> str:
        """
        Extract text from a specific PDF page using OCR.
        Useful for scanned PDFs where PyMuPDF text extraction fails.
        
        Args:
            pdf_path: Path to the PDF file
            page_index: 1-indexed page number
            engine: OCR engine to use
        
        Returns:
            Extracted text
        """
        import fitz
        from PIL import Image
        
        if engine not in self.engines:
            return ""
        
        try:
            doc = fitz.open(pdf_path)
            if page_index < 1 or page_index > len(doc):
                return ""
            
            page = doc[page_index - 1]
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            text = self.engines[engine].extract_text_from_image(img)
            doc.close()
            
            return text
            
        except Exception as e:
            print(f"❌ [OCRService] Error: {e}")
            return ""


# Singleton instance
ocr_service = OCRService()
