import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.core.database import Base

def generate_uuid():
    return uuid.uuid4().hex

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_hash = Column(String(64), index=True, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Classification Metadata
    classification_label = Column(String(100), nullable=True)
    classification_confidence = Column(Float, default=0.0)
    
    # Verification Score & Details
    verification_score = Column(Integer, default=0)
    verification_details = Column(JSON, nullable=True)  # Store dict of: blur_score, page_count, rotation, duplicate_flag, empty_pages
    
    # Extracted Plain Text
    extracted_text = Column(Text, nullable=True)
    
    # Lifecycle Status
    status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="documents")
    resume_analysis = relationship("ResumeAnalysis", back_populates="document", uselist=False, cascade="all, delete-orphan")
