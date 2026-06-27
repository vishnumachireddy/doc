from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional, List

class VerificationDetails(BaseModel):
    blur_score: float
    page_count: int
    rotation: int
    duplicate_flag: bool
    empty_pages: List[int]
    is_blurry: bool
    is_rotated: bool

class DocumentBase(BaseModel):
    file_path: Optional[str] = None
    file_size: int
    mime_type: str

class DocumentCreate(DocumentBase):
    user_id: str
    file_hash: str

class DocumentResponse(BaseModel):
    id: str
    file_path: Optional[str] = None
    file_size: int
    mime_type: str
    classification_label: Optional[str] = None
    classification_confidence: float
    verification_score: int
    verification_details: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    id: str
    status: str
    message: str

class DocumentHistoryResponse(BaseModel):
    total: int
    items: List[DocumentResponse]
