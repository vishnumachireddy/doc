from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class CategoryStats(BaseModel):
    label: str
    count: int
    percentage: float

class AdminStatsResponse(BaseModel):
    total_users: int
    total_uploads: int
    category_distribution: List[CategoryStats]
    average_ats_score: float
    average_verification_score: float
    classification_accuracy: float
    daily_uploads: List[Dict[str, Any]]  # List of {"date": "YYYY-MM-DD", "count": int}

class CategoryOverrideRequest(BaseModel):
    document_id: str
    override_label: str
