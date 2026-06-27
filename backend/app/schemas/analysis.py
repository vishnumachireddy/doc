from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, List, Optional

class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class EducationItem(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None

class ExperienceItem(BaseModel):
    role: Optional[str] = None
    company: Optional[str] = None
    duration: Optional[str] = None
    years: Optional[float] = 0.0
    description: Optional[str] = None

class ProjectItem(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class ExtractedResumeData(BaseModel):
    contact: ContactInfo
    skills: List[str] = []
    education: List[EducationItem] = []
    experience: List[ExperienceItem] = []
    projects: List[ProjectItem] = []
    certifications: List[str] = []
    achievements: List[str] = []

class SuggestionsData(BaseModel):
    project_descriptions: List[str] = []
    skills_ordering: List[str] = []
    bullet_points: List[str] = []
    action_verbs: List[str] = []
    missing_keywords: List[str] = []
    summary_improvements: List[str] = []
    ats_formatting: List[str] = []

class ResumeAnalysisResponse(BaseModel):
    id: str
    document_id: str
    ats_score: int
    ai_likelihood_score: float
    extracted_data: ExtractedResumeData
    suggestions: SuggestionsData
    created_at: datetime

    class Config:
        from_attributes = True
