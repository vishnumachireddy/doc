import os
import numpy as np
from typing import List, Dict, Any

# Global EasyOCR Reader holder to satisfy worker pre-initialization NFR
_ocr_reader = None

def init_ocr_engine(languages: List[str] = None):
    """Initializes the EasyOCR reader globally. Called during worker startup."""
    global _ocr_reader
    if _ocr_reader is not None:
        return
        
    if languages is None:
        languages = ['en']
        
    try:
        import easyocr
        print(f"Loading EasyOCR models for languages: {languages}...")
        _ocr_reader = easyocr.Reader(languages, gpu=False)  # CPU default, safe for Windows dev env
        print("EasyOCR loaded successfully!")
    except Exception as e:
        print(f"Failed to pre-load EasyOCR: {e}")

def get_ocr_reader():
    """Lazily gets or initializes the reader if not pre-loaded."""
    global _ocr_reader
    if _ocr_reader is None:
        init_ocr_engine()
    return _ocr_reader

def extract_text_from_image(image_path: str) -> str:
    """Runs OCR on the given image and returns the compiled plain text."""
    reader = get_ocr_reader()
    if reader is None:
        return ""
        
    try:
        results = reader.readtext(image_path, detail=0)
        return "\n".join(results)
    except Exception as e:
        print(f"Error in OCR text extraction: {e}")
        return ""

def extract_structured_ocr(image_path: str) -> Dict[str, Any]:
    """
    Runs OCR and returns structured word elements with coordinates.
    Also groups text blocks into a primitive table grid by analyzing horizontal line bands.
    """
    reader = get_ocr_reader()
    if reader is None:
        return {"text": "", "tables": []}
        
    try:
        # readtext with detail=1 returns [([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], text, confidence), ...]
        raw_results = reader.readtext(image_path, detail=1)
        
        full_text_list = []
        rows: Dict[int, List[Dict[str, Any]]] = {}  # Grouped by y-coordinate band
        
        for bbox, text, conf in raw_results:
            full_text_list.append(text)
            
            # Get center coordinates
            y_center = (bbox[0][1] + bbox[2][1]) / 2.0
            x_center = (bbox[0][0] + bbox[1][0]) / 2.0
            
            # Find or create a horizontal row band (allow +/- 15px deviation)
            placed = False
            for y_band in rows.keys():
                if abs(y_center - y_band) < 15:
                    rows[y_band].append({"text": text, "x": x_center})
                    placed = True
                    break
                    
            if not placed:
                rows[int(y_center)] = [{"text": text, "x": x_center}]
                
        # Reconstruct tables by sorting columns horizontally
        table_rows = []
        for y_band in sorted(rows.keys()):
            sorted_cols = sorted(rows[y_band], key=lambda item: item["x"])
            row_str = " | ".join([col["text"] for col in sorted_cols])
            table_rows.append(row_str)
            
        return {
            "text": "\n".join(full_text_list),
            "tables": table_rows
        }
    except Exception as e:
        print(f"Error in structured OCR extraction: {e}")
        return {"text": "", "tables": []}
