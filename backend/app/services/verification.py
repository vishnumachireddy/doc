import os
import hashlib
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
from pypdf import PdfReader

def calculate_file_hash(file_path: str) -> str:
    """Calculates the SHA-256 hash of a file for cryptographic duplicate checks."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read file in 64kb blocks
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def detect_image_blur(image_path: str) -> Tuple[float, bool]:
    """
    Computes blur score using the Laplacian variance method.
    Returns (variance, is_blurry).
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return 0.0, True
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        # Variance below 100 usually indicates blur
        is_blurry = variance < 100.0
        return round(variance, 2), is_blurry
    except Exception as e:
        print(f"Error in blur detection: {e}")
        return 0.0, True

def detect_image_rotation(image_path: str) -> Tuple[int, bool]:
    """
    Detects if the image is rotated by analyzing dominant line angles.
    Returns (rotation_angle_estimate, is_rotated).
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return 0, False
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        if lines is None:
            return 0, False
            
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            # Normalize to 0-180
            angle = angle % 180
            angles.append(angle)
            
        if not angles:
            return 0, False
            
        # Get dominant angle
        hist, bin_edges = np.histogram(angles, bins=18, range=(0, 180))
        dominant_bin = np.argmax(hist)
        dominant_angle = (bin_edges[dominant_bin] + bin_edges[dominant_bin+1]) / 2
        
        # Check deviation from horizontal (0/180) or vertical (90)
        # If deviation is more than 15 degrees, it's rotated
        is_rotated = False
        rotation_estimate = 0
        
        if 15 < dominant_angle < 75:
            is_rotated = True
            rotation_estimate = int(dominant_angle)
        elif 105 < dominant_angle < 165:
            is_rotated = True
            rotation_estimate = int(dominant_angle - 180)
            
        return rotation_estimate, is_rotated
    except Exception as e:
        print(f"Error in rotation detection: {e}")
        return 0, False

def verify_document_quality(file_path: str, is_duplicate: bool = False) -> Tuple[int, Dict[str, Any]]:
    """
    Evaluates file properties, blur, orientation, and layout grids.
    Returns (verification_score, verification_details).
    """
    ext = os.path.splitext(file_path.lower())[1].lstrip(".")
    
    # Default values
    score = 100
    details = {
        "blur_score": 1000.0,
        "is_blurry": False,
        "rotation": 0,
        "is_rotated": False,
        "page_count": 1,
        "empty_pages": [],
        "duplicate_flag": is_duplicate,
        "low_resolution": False
    }
    
    if is_duplicate:
        score -= 10  # Mild penalty for exact duplicate, though details remain crucial
        
    if ext == "pdf":
        try:
            reader = PdfReader(file_path)
            details["page_count"] = len(reader.pages)
            
            # Check empty pages
            empty_pages = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                # Digital PDF check for empty page: length of text is very small
                # and no images are present on the page
                if len(text.strip()) < 5:
                    empty_pages.append(i + 1)
            details["empty_pages"] = empty_pages
            
            # Deduct for empty pages
            if empty_pages:
                score -= min(30, len(empty_pages) * 10)
                
            # Digital PDFs are never blurry or rotated
            details["blur_score"] = 999.0
            details["is_blurry"] = False
            
        except Exception as e:
            print(f"Error validating PDF quality: {e}")
            score = 30
            details["is_blurry"] = True
            
    elif ext in ["jpg", "jpeg", "png"]:
        # Image quality checks
        try:
            img = cv2.imread(file_path)
            if img is not None:
                h, w, _ = img.shape
                # Check resolution
                if h < 600 or w < 600:
                    details["low_resolution"] = True
                    score -= 15
                
                # Check blur
                blur_score, is_blurry = detect_image_blur(file_path)
                details["blur_score"] = blur_score
                details["is_blurry"] = is_blurry
                if is_blurry:
                    score -= 30
                    
                # Check rotation
                rotation, is_rotated = detect_image_rotation(file_path)
                details["rotation"] = rotation
                details["is_rotated"] = is_rotated
                if is_rotated:
                    score -= 20
                    
                # Check if image is blank (empty page)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                std_dev = np.std(gray)
                if std_dev < 10.0:
                    details["empty_pages"] = [1]
                    score -= 40
            else:
                score = 0
                details["is_blurry"] = True
        except Exception as e:
            print(f"Error checking image quality: {e}")
            score = 20
            
    # Bound score
    score = max(0, min(100, score))
    return score, details
