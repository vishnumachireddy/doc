from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.api.auth import get_current_user
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.analysis import ResumeAnalysis
from backend.app.schemas.analysis import ResumeAnalysisResponse
from backend.app.schemas.job import JobMatchRequest, JobMatchResponse
from backend.app.services.job_matcher import match_resume_to_jd

router = APIRouter(prefix="/analysis", tags=["Resume Intelligence"])

@router.get("/{doc_id}", response_model=ResumeAnalysisResponse)
def get_resume_analysis(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves the full parsed Resume Intelligence report for a document."""
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied."
        )
        
    if doc.classification_label != "Resume":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This document is classified as a '{doc.classification_label}', not a 'Resume'. Resume Intelligence is unavailable."
        )
        
    analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.document_id == doc_id).first()
    if not analysis:
        if doc.status in ["pending", "processing"]:
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail="Resume parsing is currently in progress. Please poll again in a few moments."
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume analysis data not found. Processing may have failed."
        )
        
    return analysis

@router.post("/{doc_id}/match", response_model=JobMatchResponse)
def match_job_description(
    doc_id: str,
    payload: JobMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Computes semantic similarity and identifies skill gaps between the 
    specified Resume and a provided Job Description.
    """
    if payload.document_id != doc_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL document ID and payload document ID must match."
        )
        
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
        
    analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.document_id == doc_id).first()
    if not analysis or not doc.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume text has not been parsed yet. Ensure status is completed."
        )
        
    resume_skills = analysis.extracted_data.get("skills", [])
    
    # Calculate matching metrics
    match_results = match_resume_to_jd(doc.extracted_text, payload.job_description, resume_skills)
    
    return JobMatchResponse(
        document_id=doc_id,
        skill_match_percentage=match_results["skill_match_percentage"],
        missing_skills=match_results["missing_skills"],
        missing_keywords=match_results["missing_keywords"],
        improvement_suggestions=match_results["improvement_suggestions"]
    )

@router.get("/{doc_id}/export", response_class=PlainTextResponse)
def export_suggestions(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates and returns a formatted structured markdown report of
    resume optimization recommendations for download.
    """
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
        
    analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.document_id == doc_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume analysis suggestions not found."
        )
        
    data = analysis.extracted_data
    sug = analysis.suggestions
    
    # Compile markdown text
    report = []
    report.append(f"# ResumeIQ Optimization Report - {data.get('contact', {}).get('name', 'Applicant')}")
    report.append(f"ATS Compliance Score: {analysis.ats_score}/100")
    report.append(f"Estimated AI Written Percentage: {analysis.ai_likelihood_score}%")
    report.append(f"Generated on: {analysis.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append("\n" + "="*50 + "\n")
    
    report.append("## 1. Action Verbs Improvements")
    if sug.get("action_verbs"):
        for item in sug["action_verbs"]:
            report.append(f"- {item}")
    else:
        report.append("- No issues detected. Excellent verb use!")
        
    report.append("\n## 2. Formatting & ATS Integrity")
    if sug.get("ats_formatting"):
        for item in sug["ats_formatting"]:
            report.append(f"- {item}")
    else:
        report.append("- Layout and formatting comply with standard ATS guidelines.")
        
    report.append("\n## 3. Project Explanations & Descriptions")
    if sug.get("project_descriptions"):
        for item in sug["project_descriptions"]:
            report.append(f"- {item}")
    else:
        report.append("- Project descriptions are sufficiently detailed.")
        
    report.append("\n## 4. Skills Reordering Suggestions")
    if sug.get("skills_ordering"):
        for item in sug["skills_ordering"]:
            report.append(f"- {item}")
    else:
        report.append("- Skills lists are concise and structured.")
        
    report.append("\n## 5. Vocabulary & AI Written Feedback")
    if sug.get("ai_analysis"):
        report.append(f"AI Classification: {sug.get('ai_classification', 'Unknown')}")
        for item in sug["ai_analysis"]:
            report.append(f"- {item}")
            
    report.append("\n" + "="*50)
    report.append("Thank you for using ResumeIQ to optimize your profile!")
    
    file_content = "\n".join(report)
    
    headers = {
        "Content-Disposition": f"attachment; filename=resumeiq_suggestions_{doc_id}.md"
    }
    
    return PlainTextResponse(content=file_content, headers=headers)
