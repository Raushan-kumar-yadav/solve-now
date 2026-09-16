import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel

from core.database import get_db
from models.user import User, Role
from models.moderation import Report, ReportReason, ModerationAction, ModActionType
from models.problem import Problem
from models.solution import Solution
from api.deps import get_current_user

router = APIRouter()

class ReportCreate(BaseModel):
    entity_type: str
    entity_id: uuid.UUID
    reason: ReportReason
    details: Optional[str] = None

@router.post("/reports")
def create_report(
    report_in: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = Report(
        reporter_id=current_user.id,
        entity_type=report_in.entity_type,
        entity_id=report_in.entity_id,
        reason=report_in.reason,
        details=report_in.details
    )
    db.add(report)
    db.commit()
    return {"message": "Report submitted successfully."}

class ModActionCreate(BaseModel):
    entity_type: str
    entity_id: uuid.UUID
    target_user_id: Optional[uuid.UUID] = None
    action: ModActionType
    reason: str

@router.post("/actions")
def execute_moderation_action(
    action_in: ModActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Ensure current_user is an admin/moderator
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to perform moderation actions")
        
    mod_action = ModerationAction(
        moderator_id=current_user.id,
        entity_type=action_in.entity_type,
        entity_id=action_in.entity_id,
        target_user_id=action_in.target_user_id,
        action=action_in.action,
        reason=action_in.reason
    )
    db.add(mod_action)
    
    # Execute effect based on action and entity type
    if action_in.action in [ModActionType.HIDE, ModActionType.RESTORE]:
        is_hidden = (action_in.action == ModActionType.HIDE)
        
        if action_in.entity_type == "problem":
            problem = db.query(Problem).filter(Problem.id == action_in.entity_id).first()
            if problem:
                problem.is_hidden = is_hidden
        elif action_in.entity_type == "solution":
            solution = db.query(Solution).filter(Solution.id == action_in.entity_id).first()
            if solution:
                solution.is_hidden = is_hidden

    if action_in.action in [ModActionType.LOCK]:
        if action_in.entity_type == "problem":
            problem = db.query(Problem).filter(Problem.id == action_in.entity_id).first()
            if problem:
                problem.is_locked = True
                
    db.commit()
    return {"message": f"Action {action_in.action.value} executed successfully."}

@router.get("/reports")
def get_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    reports = db.query(Report).order_by(desc(Report.created_at)).all()
    return reports

