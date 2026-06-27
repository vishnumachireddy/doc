import os
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from backend.app.worker.celery_app import celery_app
from backend.app.core.database import SessionLocal
from backend.app.models.document import Document
from backend.app.models.analysis import ResumeAnalysis

# Import services
from backend.app.services.binary_signature import validate_binary_signature
from backend.app.services.verification import calculate_file_hash, verify_document_quality
from backend.app.services.extractor import extract_document_text
from backend.app.services.ocr_engine import init_ocr_engine, extract_text_from_image, extract_structured_ocr
from backend.app.services.redaction import redact_sensitive_data
from backend.app.services.resume_parser import parse_resume
from backend.app.services.ats_analyzer import analyze_ats_compliance, calculate_readiness_score
from backend.app.services.ai_detector import estimate_ai_likelihood
from backend.app.ml.visual_classifier import visual_layout_classifier
from backend.app.ml.text_classifier import text_document_classifier

# OCR engine will initialize lazily when a background task runs to avoid blocking API Gateway boot.

def process_document_core(db: Session, doc_id: str) -> bool:
    """
    Executes the multi-stage document verification and parsing pipeline.
    """
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        print(f"Document {doc_id} not found in database.")
        return False
        
    try:
        # 1. Update status to processing
        doc.status = "processing"
        db.commit()
        db.refresh(doc)
        
        file_path = doc.file_path
        
        # 2. Binary signature (magic numbers) validation
        detected_ext = validate_binary_signature(file_path)
        if not detected_ext:
            doc.status = "failed"
            doc.extracted_text = "Verification Failed: File extension spoofing detected or file format corrupt."
            db.commit()
            print(f"Document {doc_id} failed magic number binary signature checks.")
            return False
            
        # 3. Cryptographic deduplication check
        file_hash = calculate_file_hash(file_path)
        doc.file_hash = file_hash
        
        # Look for existing documents with same hash (completed/processing)
        duplicate = db.query(Document).filter(
            Document.file_hash == file_hash,
            Document.id != doc_id,
            Document.status.in_(["completed", "processing"])
        ).first()
        is_duplicate = duplicate is not None
        
        # 4. Ingestion: Extract text and run OCR if image
        extracted_text = ""
        page_count = 1
        
        ext = os.path.splitext(file_path.lower())[1].lstrip(".")
        if ext in ["pdf", "docx"]:
            extracted_text, page_count = extract_document_text(file_path)
            
            # If text is extremely short, it could be a scanned PDF. Trigger OCR on PDF pages.
            if ext == "pdf" and len(extracted_text.strip()) < 100:
                print(f"Document {doc_id} appears to be a scanned PDF. Attempting OCR fallback...")
                # In a local/CPU setup, we extract text via simpler PDF parsers.
                # If we need true page OCR, we convert PDF to image, but to avoid extra heavy binaries,
                # we'll read OCR tokens where possible or flag it in verification score.
                pass
        elif ext in ["png", "jpg", "jpeg"]:
            # Run OCR on image
            ocr_results = extract_structured_ocr(file_path)
            extracted_text = ocr_results["text"]
            
        # 5. Deterministic Document Quality Verification
        verification_score, verification_details = verify_document_quality(file_path, is_duplicate=is_duplicate)
        verification_details["page_count"] = page_count
        
        doc.verification_score = verification_score
        doc.verification_details = verification_details
        
        # 6. Two-Pass Document Classification
        visual_label, visual_conf = visual_layout_classifier.predict_visual_category(file_path)
        text_label, text_conf = text_document_classifier.predict_text_category(extracted_text)
        
        final_label, final_conf = text_document_classifier.cross_validate(
            visual_label, visual_conf, text_label, text_conf
        )
        
        doc.classification_label = final_label
        doc.classification_confidence = final_conf
        
        # 7. Compliance Data Redaction Pipeline
        redacted_text = redact_sensitive_data(extracted_text, final_label)
        doc.extracted_text = redacted_text
        
        # Save baseline document results
        doc.status = "completed"
        db.commit()
        db.refresh(doc)
        print(f"Document {doc_id} core processing complete. Classified as: {final_label} ({final_conf})")
        
        # 8. Resume Intelligence Pipeline
        if final_label == "Resume":
            print(f"Launching Resume Intelligence analysis for document {doc_id}...")
            
            # Extract structured details
            resume_data = parse_resume(redacted_text)
            
            # Run ATS compliance checking
            ats_score, suggestions = analyze_ats_compliance(resume_data, redacted_text)
            
            # Calculate Recruiter Readiness Score
            readiness_score = calculate_readiness_score(ats_score, resume_data.get("skill_durations", {}))
            
            # Add readiness to structured data
            resume_data["recruiter_readiness_score"] = readiness_score
            
            # Estimate AI Writing Likelihood
            ai_details = estimate_ai_likelihood(redacted_text)
            ai_score = float(ai_details["ai_percentage"])
            
            # Add AI analysis summary to suggestions
            suggestions["ai_analysis"] = ai_details["reasons"]
            suggestions["ai_classification"] = ai_details["classification"]
            
            # Create ResumeAnalysis record
            analysis = ResumeAnalysis(
                document_id=doc_id,
                ats_score=ats_score,
                ai_likelihood_score=ai_score,
                extracted_data=resume_data,
                suggestions=suggestions
            )
            db.add(analysis)
            db.commit()
            print(f"Resume Intelligence parsing completed for document {doc_id}. ATS: {ats_score}, AI: {ai_score}%")
            
        return True
        
    except Exception as e:
        db.rollback()
        doc.status = "failed"
        doc.extracted_text = f"Process Error: {str(e)}"
        db.commit()
        print(f"Failed to process document {doc_id}: {e}")
        import traceback
        traceback.print_exc()
        return False

# Celery Asynchronous Task Definition
@celery_app.task(name="process_document_task")
def process_document_task(doc_id: str):
    """Celery worker task wrapper."""
    db = SessionLocal()
    try:
        process_document_core(db, doc_id)
    finally:
        db.close()

# Local Background Task Fallback (for Redis-less setups)
def process_document_local(doc_id: str):
    """FastAPI local background task runner."""
    db = SessionLocal()
    try:
        print(f"Running local background task for document {doc_id}...")
        process_document_core(db, doc_id)
    finally:
        db.close()
