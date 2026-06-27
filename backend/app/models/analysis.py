import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.core.database import Base

def generate_uuid():
    return uuid.uuid4().hex

class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), unique=True, nullable=False)
    ats_score = Column(Integer, default=0, nullable=False)
    ai_likelihood_score = Column(Float, default=0.0, nullable=False)  # 0.0 to 100.0 or 0.0 to 1.0. Let's keep it as percentage (0-100) or float
    
    # Flexible JSON fields for structured data and suggestions
    extracted_data = Column(JSON, nullable=True)  # Name, Email, Phone, Skills, Education, Experience, Projects, Certs, Achievements
    suggestions = Column(JSON, nullable=True)     # Better Project Descriptions, Skills ordering, Stronger Bullet Points, Verb improvements, etc.
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    document = relationship("Document", back_populates="resume_analysis")
