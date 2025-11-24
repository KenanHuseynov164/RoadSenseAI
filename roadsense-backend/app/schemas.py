from pydantic import BaseModel, validator
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


class UserRegister(BaseModel):
    email: str
    name: str
    password: str

    @validator("password")
    def password_max_length(cls, v):
        if len(v) > 72:
            raise ValueError("Password must be 72 characters or less.")
        return v


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"