from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class IncidentCreate(BaseModel):
    description: str

class IncidentResponse(BaseModel):
    id: int
    description: str
    created_at: datetime
    legal_articles: List[str]
    explanation: str
    recommendation: str
    what_to_say: str

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str
    name: Optional[str] = None

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True
