from sqlalchemy.orm import Session
from services.ai.orchestrator import InvestigationOrchestrator
from models.ai_investigation import AIInvestigation, InvestigationStatus
from models.problem import Problem, ProblemStatus

def run_ai_investigation(db: Session, investigation_id: str):
    """
    Background worker task to step the Multi-Agent Investigation orchestrator.
    It loops until it hits a stopping condition (WAITING_FOR_USER, READY, COMPLETED, FAILED).
    """
    investigation = db.query(AIInvestigation).filter(AIInvestigation.id == investigation_id).first()
    if not investigation:
        return
        
    problem = investigation.problem
    
    # We might have been triggered by a new problem or a clarification answer.
    # We just run the orchestrator in a loop until it blocks.
    
    orchestrator = InvestigationOrchestrator(db, investigation.id)
    
    stop_states = [
        InvestigationStatus.WAITING_FOR_USER, 
        InvestigationStatus.READY,
        InvestigationStatus.COMPLETED, 
        InvestigationStatus.FAILED
    ]
    
    # Simple retry loop for state transitions
    while investigation.status not in stop_states:
        prev_status = investigation.status
        orchestrator.run_cycle()
        
        # Reload investigation to check new status
        db.refresh(investigation)
        if investigation.status == prev_status:
            # Prevent infinite loop if state didn't change
            break
            
    # Once blocked or finished, update problem status if necessary
    if investigation.status == InvestigationStatus.READY or investigation.status == InvestigationStatus.COMPLETED:
        problem.status = ProblemStatus.OPEN
        db.commit()
