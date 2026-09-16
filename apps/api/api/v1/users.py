from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

from core.database import get_db
from models.user import User
from models.problem import Problem, ProblemStatus
from models.solution import Solution, SolutionStatus
from models.reputation import UserExpertise
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class CategoryExpertise(BaseModel):
    category_name: str
    score: int

class UserProfileResponse(BaseModel):
    id: uuid.UUID
    username: str
    reputation_score: int
    problems_solved: int
    solutions_verified: int
    success_rate: float
    helpful_votes: int
    expertise: List[CategoryExpertise]
    
    class Config:
        from_attributes = True

@router.get("/{user_id}/profile", response_model=UserProfileResponse)
def get_user_profile(user_id: uuid.UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Calculate stats
    problems_solved = db.query(func.count(Solution.id)).filter(
        Solution.author_id == user.id,
        Solution.status == SolutionStatus.ACCEPTED
    ).scalar() or 0
    
    total_solutions_proposed = db.query(func.count(Solution.id)).filter(
        Solution.author_id == user.id
    ).scalar() or 0
    
    success_rate = (problems_solved / total_solutions_proposed * 100) if total_solutions_proposed > 0 else 0.0
    
    solutions_verified = db.query(func.sum(Solution.verification_count)).filter(
        Solution.author_id == user.id
    ).scalar() or 0
    
    helpful_votes = db.query(func.sum(Solution.upvotes)).filter(
        Solution.author_id == user.id
    ).scalar() or 0
    
    # Get expertise
    expertise_records = db.query(UserExpertise).filter(UserExpertise.user_id == user.id).order_by(UserExpertise.score.desc()).limit(5).all()
    expertise = []
    for exp in expertise_records:
        if exp.category:
            expertise.append(CategoryExpertise(category_name=exp.category.name, score=exp.score))
            
    return UserProfileResponse(
        id=user.id,
        username=user.username,
        reputation_score=user.reputation_score,
        problems_solved=problems_solved,
        solutions_verified=solutions_verified,
        success_rate=round(success_rate, 1),
        helpful_votes=helpful_votes,
        expertise=expertise
    )

