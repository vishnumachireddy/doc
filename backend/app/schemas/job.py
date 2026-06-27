from pydantic import BaseModel
from typing import List, Optional

class JobMatchRequest(BaseModel):
    document_id: str
    job_description: str

class JobMatchResponse(BaseModel):
    document_id: str
    skill_match_percentage: int
    missing_skills: List[str]
    missing_keywords: List[str]
    improvement_suggestions: List[str]
