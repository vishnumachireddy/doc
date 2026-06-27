import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.api.auth import get_current_user
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.schemas.document import DocumentResponse, DocumentUploadResponse, DocumentHistoryResponse

# Import worker tasks & Redis checker
from backend.app.worker.tasks import process_document_task, process_document_local
from backend.app.worker.celery_app import is_redis_available

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=List[DocumentUploadResponse], status_code=status.HTTP_202_ACCEPTED)
def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ingests uploaded documents. Validates size, saves locally, registers
    pending records, triggers async workers, and returns task IDs immediately.
    """
    responses = []
    
    for file in files:
        # 1. Size Validation (Max 15MB)
        # Read contents to check size
        try:
            file.file.seek(0, os.SEEK_END)
            size_bytes = file.file.tell()
            file.file.seek(0)
        except Exception:
            size_bytes = 0
            
        size_mb = size_bytes / (1024 * 1024)
        if size_mb > settings.MAX_FILE_SIZE_MB:
            responses.append(DocumentUploadResponse(
                id="N/A",
                status="failed",
                message=f"File '{file.filename}' exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
            ))
            continue
            
        # Validate format extension (raw check)
        ext = os.path.splitext(file.filename.lower())[1].lstrip(".")
        if ext not in ["pdf", "docx", "png", "jpg", "jpeg"]:
            responses.append(DocumentUploadResponse(
                id="N/A",
                status="failed",
                message=f"File '{file.filename}' extension '.{ext}' is not supported."
            ))
            continue
            
        # 2. Save file with unique random identifier
        doc_id = uuid.uuid4().hex
        secure_name = f"{doc_id}_{file.filename}"
        save_path = os.path.join(settings.UPLOAD_DIR, secure_name)
        
        try:
            with open(save_path, "wb") as f:
                content = file.file.read()
                f.write(content)
        except Exception as e:
            responses.append(DocumentUploadResponse(
                id="N/A",
                status="failed",
                message=f"Failed to write file '{file.filename}' to storage: {str(e)}"
            ))
            continue
            
        # 3. Create database pending metadata record
        db_doc = Document(
            id=doc_id,
            user_id=current_user.id,
            file_path=save_path,
            file_hash="pending_hash", # will be computed by worker
            file_size=size_bytes,
            mime_type=file.content_type or "application/octet-stream",
            status="pending"
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)
        
        # 4. Asynchronously delegate processing
        if is_redis_available():
            # Trigger Celery Distributed Worker Task
            process_document_task.delay(doc_id)
            msg = "File queued for asynchronous worker pool analysis."
        else:
            # Trigger Local FastAPI BackgroundTask Fallback
            background_tasks.add_task(process_document_local, doc_id)
            msg = "File queued for local background task analysis (Redis Offline Fallback)."
            
        responses.append(DocumentUploadResponse(
            id=doc_id,
            status="pending",
            message=msg
        ))
        
    return responses

@router.get("/history", response_model=DocumentHistoryResponse)
def get_upload_history(
    search: Optional[str] = Query(None, description="Search by file name or classification category"),
    status: Optional[str] = Query(None, description="Filter by status (pending, processing, completed, failed)"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves a paginated list of the current user's document history."""
    query = db.query(Document).filter(Document.user_id == current_user.id)
    
    if status:
        query = query.filter(Document.status == status)
        
    if search:
        # Search file name (parsed from file path) or classification label
        search_pattern = f"%{search}%"
        query = query.filter(
            (Document.file_path.ilike(search_pattern)) | 
            (Document.classification_label.ilike(search_pattern))
        )
        
    # Sort chronologically
    query = query.order_by(Document.created_at.desc())
    
    total = query.count()
    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()
    
    return DocumentHistoryResponse(total=total, items=items)

@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document_details(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves metadata of a specific document."""
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied."
        )
    return doc

@router.get("/{doc_id}/status")
def get_document_status(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simplified status checker for polling."""
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
    return {
        "id": doc.id,
        "status": doc.status,
        "classification_label": doc.classification_label,
        "verification_score": doc.verification_score,
        "is_completed": doc.status == "completed",
        "is_failed": doc.status == "failed"
    }

@router.delete("/{doc_id}", status_code=status.HTTP_200_OK)
def delete_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Removes a document record and deletes its corresponding local binary file."""
    doc = db.query(Document).filter(Document.id == doc_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
        
    # Delete binary file if it exists
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            print(f"Error removing physical file: {e}")
            
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully"}
