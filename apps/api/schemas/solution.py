from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime
from models.solution import SolutionStatus
from .user import UserResponse

class SolutionCreate(BaseModel):
    content: str

class SolutionUpdate(BaseModel):
    content: Optional[str] = None

class SolutionVoteCreate(BaseModel):
    value: int = Field(..., description="1 for upvote, -1 for downvote")

class SolutionCommentCreate(BaseModel):
    content: str

class SolutionCommentResponse(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    author: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True

class SolutionResponse(BaseModel):
    id: uuid.UUID
    problem_id: uuid.UUID
    author_id: uuid.UUID
    content: str
    status: SolutionStatus
    confidence_score: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    
    author: Optional[UserResponse] = None
    
    # Calculated fields
    upvotes: int = 0
    downvotes: int = 0
    verification_count: int = 0
    user_vote: int = 0 # What the current user voted
    
    class Config:
        from_attributes = True

