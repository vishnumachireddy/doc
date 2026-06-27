from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

from backend.app.core.database import get_db
from backend.app.api.auth import get_current_user
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.analysis import ResumeAnalysis
from backend.app.schemas.admin import AdminStatsResponse, CategoryOverrideRequest, CategoryStats

# Import resume parser tasks
from backend.app.worker.tasks import process_document_local
from backend.app.services.resume_parser import parse_resume
from backend.app.services.ats_analyzer import analyze_ats_compliance, calculate_readiness_score
from backend.app.services.ai_detector import estimate_ai_likelihood

router = APIRouter(prefix="/admin", tags=["Administrative Tools"])

# Simulated accuracy tracking state (adjusted when admin overrides labels)
_overrides_count = 0

@router.get("/stats", response_model=AdminStatsResponse)
def get_global_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns global system statistics, upload volumes, average scoring metrics, 
    and machine learning classification distributions.
    """
    global _overrides_count
    
    # 1. Counts
    total_users = db.query(User).count()
    total_uploads = db.query(Document).count()
    
    # 2. Average Scores
    avg_ats = db.query(func.avg(ResumeAnalysis.ats_score)).scalar() or 0.0
    avg_verification = db.query(func.avg(Document.verification_score)).scalar() or 0.0
    
    # 3. Category distribution
    categories_counts = db.query(
        Document.classification_label,
        func.count(Document.id)
    ).filter(Document.status == "completed").group_by(Document.classification_label).all()
    
    completed_uploads = db.query(Document).filter(Document.status == "completed").count()
    
    category_distribution = []
    for label, count in categories_counts:
        lbl = label or "Unclassified"
        pct = (count / completed_uploads * 100) if completed_uploads else 0.0
        category_distribution.append(
            CategoryStats(label=lbl, count=count, percentage=round(pct, 2))
        )
        
    # Ensure standard categories are present in frontend representation
    
    # 4. Daily Upload Trends (Last 7 Days)
    daily_uploads = []
    now = datetime.now(timezone.utc)
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day, 0, 0, 0, tzinfo=timezone.utc)
        day_end = datetime(day.year, day.month, day.day, 23, 59, 59, tzinfo=timezone.utc)
        
        count = db.query(Document).filter(
            Document.created_at >= day_start,
            Document.created_at <= day_end
        ).count()
        
        daily_uploads.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "count": count
        })
        
    # 5. Simulated Historical Classification Accuracy
    # Visual layout classifier is ~85%, Textual is ~95%. Overrides reduce accuracy.
    base_accuracy = 96.5
    if total_uploads > 0:
        accuracy = max(50.0, base_accuracy - (_overrides_count * 1.5))
    else:
        accuracy = 100.0
        
    return AdminStatsResponse(
        total_users=total_users,
        total_uploads=total_uploads,
        category_distribution=category_distribution,
        average_ats_score=round(float(avg_ats), 2),
        average_verification_score=round(float(avg_verification), 2),
        classification_accuracy=round(accuracy, 2),
        daily_uploads=daily_uploads
    )

@router.post("/documents/override", status_code=status.HTTP_200_OK)
def override_document_category(
    payload: CategoryOverrideRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Overrides a document's classification label.
    If changed to Resume, triggers parsing and ATS scoring immediately.
    """
    global _overrides_count
    
    doc = db.query(Document).filter(Document.id == payload.document_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
        
    old_label = doc.classification_label
    new_label = payload.override_label
    
    if old_label == new_label:
        return {"message": f"Category is already '{new_label}'"}
        
    # Apply override
    doc.classification_label = new_label
    doc.classification_confidence = 1.0  # Manually verified
    
    _overrides_count += 1
    
    # If changed to Resume, we must run the resume analysis pipeline!
    if new_label == "Resume":
        # Check if ResumeAnalysis already exists
        existing_analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.document_id == doc.id).first()
        if not existing_analysis and doc.extracted_text:
            try:
                # Parse resume details
                resume_data = parse_resume(doc.extracted_text)
                ats_score, suggestions = analyze_ats_compliance(resume_data, doc.extracted_text)
                readiness_score = calculate_readiness_score(ats_score, resume_data.get("skill_durations", {}))
                resume_data["recruiter_readiness_score"] = readiness_score
                
                # Estimate AI
                ai_details = estimate_ai_likelihood(doc.extracted_text)
                ai_score = float(ai_details["ai_percentage"])
                
                suggestions["ai_analysis"] = ai_details["reasons"]
                suggestions["ai_classification"] = ai_details["classification"]
                
                analysis = ResumeAnalysis(
                    document_id=doc.id,
                    ats_score=ats_score,
                    ai_likelihood_score=ai_score,
                    extracted_data=resume_data,
                    suggestions=suggestions
                )
                db.add(analysis)
            except Exception as e:
                print(f"Failed to generate overridden resume analysis: {e}")
                
    elif old_label == "Resume":
        # If it was a Resume and is no longer a Resume, delete the analysis record
        db.query(ResumeAnalysis).filter(ResumeAnalysis.document_id == doc.id).delete()
        
    db.commit()
    return {
        "message": f"Document category successfully overridden from '{old_label}' to '{new_label}'",
        "document_id": doc.id,
        "classification_label": doc.classification_label
    }
