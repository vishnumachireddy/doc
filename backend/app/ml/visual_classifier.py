import os
import cv2
import numpy as np
import pdfplumber
from pypdf import PdfReader
from typing import Dict, Any, Tuple

class VisualLayoutClassifier:
    """
    Evaluates the visual structure of a document (aspect ratio, table grids, 
    contours, density) to predict document classification categories.
    """
    
    CATEGORIES = [
        "Resume", "Aadhaar Card", "PAN Card", "Passport", "Driving License", 
        "Marksheet", "Degree Certificate", "Invoice", "Receipt", "Bank Statement", 
        "Generic Document"
    ]
    
    def extract_layout_features(self, file_path: str) -> Dict[str, Any]:
        """Extract layout metrics using OpenCV for images and structure for PDFs."""
        ext = os.path.splitext(file_path.lower())[1].lstrip(".")
        
        # Default features
        features = {
            "aspect_ratio": 0.707,  # Standard A4 portrait aspect ratio
            "grid_count": 0,
            "text_blocks": 0,
            "photo_boxes": 0,
            "file_type": ext,
            "has_table": False
        }
        
        if ext == "pdf":
            try:
                with pdfplumber.open(file_path) as pdf:
                    if len(pdf.pages) > 0:
                        first_page = pdf.pages[0]
                        features["aspect_ratio"] = float(first_page.width) / float(first_page.height) if first_page.height else 1.414
                        features["grid_count"] = len(first_page.rects) + len(first_page.lines)
                        features["text_blocks"] = len(first_page.extract_words())
                        features["has_table"] = len(first_page.find_tables()) > 0
                        features["photo_boxes"] = len(first_page.images)
            except Exception as e:
                print(f"Error extracting layout features from PDF: {e}")
                
        elif ext in ["jpg", "jpeg", "png"]:
            try:
                img = cv2.imread(file_path)
                if img is not None:
                    h, w, _ = img.shape
                    features["aspect_ratio"] = float(w) / float(h)
                    
                    # Convert to grayscale
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    
                    # Detect lines (grids)
                    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
                    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=50, maxLineGap=10)
                    features["grid_count"] = len(lines) if lines is not None else 0
                    
                    # Detect contours (potential photos or card boundaries)
                    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
                    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    photo_boxes = 0
                    text_blocks = 0
                    for c in contours:
                        x, y, cw, ch = cv2.boundingRect(c)
                        area = cw * ch
                        aspect = float(cw) / ch if ch else 0
                        
                        # ID photo: medium sized, square-ish, typically top-right or top-left
                        if 1000 < area < 50000 and 0.7 < aspect < 1.3:
                            photo_boxes += 1
                        # Text blocks
                        elif area > 100:
                            text_blocks += 1
                            
                    features["photo_boxes"] = photo_boxes
                    features["text_blocks"] = text_blocks
                    features["has_table"] = features["grid_count"] > 10
            except Exception as e:
                print(f"Error extracting layout features from image: {e}")
                
        return features

    def predict_visual_category(self, file_path: str) -> Tuple[str, float]:
        """
        Calculates match likelihoods using structural features and outputs 
        the predicted visual category and confidence score.
        """
        features = self.extract_layout_features(file_path)
        file_type = features["file_type"]
        
        # Docx files are always portrait text documents
        if file_type == "docx":
            features["aspect_ratio"] = 0.707
            
        aspect = features["aspect_ratio"]
        grids = features["grid_count"]
        blocks = features["text_blocks"]
        photos = features["photo_boxes"]
        has_table = features["has_table"]
        
        scores = {}
        
        # 1. Cards (Aadhaar, PAN, DL) typically have landscape aspect ratios (~1.5 to 1.7)
        if 1.4 < aspect < 1.8 and file_type != "docx":
            scores["Aadhaar Card"] = 0.6 if photos > 0 else 0.4
            scores["PAN Card"] = 0.7 if (photos == 1 and blocks < 100) else 0.3
            scores["Driving License"] = 0.6 if (photos == 1 and grids > 2) else 0.3
        else:
            scores["Aadhaar Card"] = 0.0
            scores["PAN Card"] = 0.0
            scores["Driving License"] = 0.0

        # 2. Passport: portrait (0.6 - 0.8) or open landscape (1.3 - 1.5), photo box, specific layout
        if 0.6 < aspect < 0.8 and file_type != "docx":
            scores["Passport"] = 0.7 if photos >= 1 else 0.3
        elif 1.3 < aspect < 1.5 and file_type != "docx":
            scores["Passport"] = 0.5 if photos >= 1 else 0.2
        else:
            scores["Passport"] = 0.0

        # 3. Resume: portrait aspect ratio (~0.7), high text density (dense blocks), few grid lines, no tables usually
        if 0.65 < aspect < 0.8:
            scores["Resume"] = 0.8 if (blocks > 100 or file_type == "docx") else 0.3
            scores["Marksheet"] = 0.6 if (has_table or grids > 15) else 0.2
            scores["Degree Certificate"] = 0.5 if (blocks < 150 and grids < 10 and photos == 0) else 0.2
            scores["Invoice"] = 0.6 if (has_table and blocks > 50) else 0.2
            scores["Receipt"] = 0.4 if (blocks < 100 and grids > 2) else 0.2
            scores["Bank Statement"] = 0.6 if (has_table and grids > 20) else 0.1
            scores["Generic Document"] = 0.4
        else:
            scores["Resume"] = 0.1
            scores["Marksheet"] = 0.1
            scores["Degree Certificate"] = 0.1
            scores["Invoice"] = 0.1
            scores["Receipt"] = 0.1
            scores["Bank Statement"] = 0.1
            scores["Generic Document"] = 0.2

        # Adjust for mobile photo aspects / receipt aspect ratios (long vertical strips)
        if aspect < 0.5:
            scores["Receipt"] = 0.7
            scores["Invoice"] = 0.3
            
        # Select best category
        best_category = max(scores, key=scores.get)
        confidence = scores[best_category]
        
        # Safety fallback: if docx somehow matched something else, ensure it is classified as Resume
        if file_type == "docx" and best_category in ["Aadhaar Card", "PAN Card", "Passport", "Driving License"]:
            best_category = "Resume"
            confidence = 0.9
            
        return best_category, round(confidence, 2)

visual_layout_classifier = VisualLayoutClassifier()
