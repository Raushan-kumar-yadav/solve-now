from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import uuid

from core.database import get_db
from models.problem import Problem
from models.ai_investigation import AIInvestigation, AIAction, AIFinding, AIProposedSolution
from services.ai.factory import get_ai_provider
from services.ai.agents.problem_orchestrator import ProblemOrchestrator
from services.ai.rag.document_processor import DocumentProcessor

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    problem_context: Optional[str] = None
    action_type: str = "chat" # chat, hint, explain, debug, review, optimize
    agent_type: Optional[str] = "auto" # auto, coding, debugging, research, math, tutor, verifier

class ActivityStep(BaseModel):
    step: str
    description: str
    data: Optional[Any] = None

class ChatResponse(BaseModel):
    response: str
    provider: str
    agent_role: Optional[str] = None
    agent_type: Optional[str] = None
    activity_steps: List[Dict[str, Any]] = []

class SolveRequest(BaseModel):
    problem_id_or_public_id: Optional[str] = None
    prompt: Optional[str] = None
    agent_type: Optional[str] = "auto"
    include_files: bool = True

@router.post("/chat", response_model=ChatResponse)
def ai_chat(req: ChatRequest):
    try:
        provider = get_ai_provider()
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Provider Initialization Error: {str(err)}"
        )

    orchestrator = ProblemOrchestrator(provider)
    
    # Map action_type to agent_type if forced by action
    forced = None
    if req.agent_type and req.agent_type != "auto":
        forced = req.agent_type
    elif req.action_type == "hint":
        forced = "tutor"
    elif req.action_type == "explain":
        forced = "tutor"
    elif req.action_type == "debug":
        forced = "debugging"
    elif req.action_type == "review":
        forced = "verifier"

    try:
        res = orchestrator.orchestrate(
            message=req.message,
            problem_context=req.problem_context or "",
            forced_agent=forced
        )
        return res
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"AI Engine Error: {str(e)}")


@router.post("/solve", response_model=ChatResponse)
def ai_solve_problem(req: SolveRequest, db: Session = Depends(get_db)):
    """
    Executes the multi-agent investigation and problem solving engine
    using Problem Context, attached files, and verification.
    """
    try:
        provider = get_ai_provider()
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

    problem = None
    problem_context = ""

    if req.problem_id_or_public_id:
        try:
            val_uuid = uuid.UUID(req.problem_id_or_public_id)
            problem = db.query(Problem).filter((Problem.id == val_uuid) | (Problem.public_id == req.problem_id_or_public_id)).first()
        except ValueError:
            problem = db.query(Problem).filter(Problem.public_id == req.problem_id_or_public_id).first()

    if problem:
        problem_context = f"Title: {problem.title}\nDescription: {problem.description}\nCategory: {problem.category.name if problem.category else 'General'}"
        
        # Read attached files if requested
        if req.include_files and problem.files:
            file_summaries = []
            for pf in problem.files:
                # If local storage file path exists
                if hasattr(pf, 'file_path') and pf.file_path:
                    text_sample = DocumentProcessor.extract_text_from_file(pf.file_path)
                    file_summaries.append(f"File: {pf.original_name}\nContent:\n{text_sample[:1000]}")
            if file_summaries:
                problem_context += "\n\nAttached Files:\n" + "\n---\n".join(file_summaries)

    task_prompt = req.prompt or (problem.description if problem else "Please analyze this problem and provide a comprehensive verified solution.")

    orchestrator = ProblemOrchestrator(provider)
    try:
        forced = req.agent_type if req.agent_type != "auto" else None
        res = orchestrator.orchestrate(
            message=task_prompt,
            problem_context=problem_context,
            forced_agent=forced,
            verify_result=True
        )

        # Record action in investigation if exists
        if problem and problem.investigation:
            act = AIAction(
                investigation_id=problem.investigation.id,
                action_type=f"ORCHESTRATED_{res.get('agent_type', 'SOLVE').upper()}",
                input_metadata={"prompt": task_prompt[:200]},
                output_metadata={"role": res.get("agent_role")}
            )
            db.add(act)
            db.commit()

        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Solving failed: {str(e)}")


@router.post("/explain", response_model=ChatResponse)
def ai_explain(req: ChatRequest):
    req.action_type = "explain"
    req.agent_type = "tutor"
    return ai_chat(req)

@router.post("/hint", response_model=ChatResponse)
def ai_hint(req: ChatRequest):
    req.action_type = "hint"
    req.agent_type = "tutor"
    return ai_chat(req)

@router.post("/debug", response_model=ChatResponse)
def ai_debug(req: ChatRequest):
    req.action_type = "debug"
    req.agent_type = "debugging"
    return ai_chat(req)

@router.post("/research", response_model=ChatResponse)
def ai_research(req: ChatRequest):
    req.action_type = "research"
    req.agent_type = "research"
    return ai_chat(req)

@router.post("/verify", response_model=ChatResponse)
def ai_verify(req: ChatRequest):
    req.action_type = "review"
    req.agent_type = "verifier"
    return ai_chat(req)
