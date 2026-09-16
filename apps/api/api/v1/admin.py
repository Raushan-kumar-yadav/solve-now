import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta

from core.database import get_db
from models.user import User, Role
from models.problem import Problem
from models.solution import Solution
from models.moderation import Report, ModerationAction, ModActionType
from models.ai_investigation import AIInvestigation
from api.deps import get_current_admin
from schemas.user import UserResponse

router = APIRouter(dependencies=[Depends(get_current_admin)])

@router.get("/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    # Calculate real stats from DB
    users_count = db.execute(text("SELECT count(*) FROM users")).scalar()
    problems_count = db.execute(text("SELECT count(*) FROM problems")).scalar()
    solutions_count = db.execute(text("SELECT count(*) FROM solutions")).scalar()
    reports_count = db.execute(text("SELECT count(*) FROM reports WHERE status = 'PENDING'")).scalar()
    ai_requests = db.execute(text("SELECT count(*) FROM ai_investigations")).scalar()
    ai_failures = db.execute(text("SELECT count(*) FROM ai_investigations WHERE status = 'FAILED'")).scalar()
    
    # Latency avg
    ai_latency = db.execute(text("SELECT avg(latency_ms) FROM ai_investigations")).scalar() or 0
    
    # Verification rate
    verified_solutions = db.execute(text("SELECT count(*) FROM solutions WHERE verified_at IS NOT NULL")).scalar()
    verification_rate = (verified_solutions / solutions_count * 100) if solutions_count else 0
    
    return {
        "users": users_count,
        "problems": problems_count,
        "solutions": solutions_count,
        "pending_reports": reports_count,
        "ai_requests": ai_requests,
        "ai_failures": ai_failures,
        "ai_latency_ms": round(ai_latency),
        "verification_rate": round(verification_rate, 1)
    }

@router.get("/users", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(User).order_by(desc(User.created_at)).offset(skip).limit(limit).all()

@router.post("/users/{user_id}/suspend")
def suspend_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_active = False # Disable login
    
    # Audit log
    action = ModerationAction(
        moderator_id=admin.id,
        entity_type="user",
        entity_id=user.id,
        target_user_id=user.id,
        action=ModActionType.SUSPEND,
        reason="Admin suspension"
    )
    db.add(action)
    db.commit()
    
    return {"message": f"User {user.username} suspended."}

@router.post("/users/{user_id}/restore")
def restore_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_active = True
    
    action = ModerationAction(
        moderator_id=admin.id,
        entity_type="user",
        entity_id=user.id,
        target_user_id=user.id,
        action=ModActionType.RESTORE,
        reason="Admin restore"
    )
    db.add(action)
    db.commit()
    
    return {"message": f"User {user.username} restored."}

@router.get("/problems")
def list_problems(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    # Need basic problem data for admin table, ignoring hidden logic
    problems = db.query(Problem).order_by(desc(Problem.created_at)).offset(skip).limit(limit).all()
    return [{
        "id": p.id,
        "public_id": p.public_id,
        "title": p.title,
        "author": p.author.username,
        "created_at": p.created_at,
        "is_hidden": p.is_hidden,
        "is_locked": p.is_locked,
        "status": p.status
    } for p in problems]

@router.get("/ai")
def list_ai_metrics(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    investigations = db.query(AIInvestigation).order_by(desc(AIInvestigation.created_at)).offset(skip).limit(limit).all()
    return [{
        "id": inv.id,
        "problem_id": inv.problem_id,
        "status": inv.status,
        "model": inv.model,
        "provider": inv.provider,
        "latency_ms": inv.latency_ms,
        "tokens_used": inv.tokens_used,
        "created_at": inv.created_at
    } for inv in investigations]

