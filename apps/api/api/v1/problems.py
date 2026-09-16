import time
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, text
from nanoid import generate

from core.database import get_db
from models.user import User
from models.problem import Problem, Category, Tag, ProblemStatus, problem_tags
from schemas.problem import ProblemCreate, ProblemUpdate, ProblemResponse, PaginatedProblems
from api.deps import get_current_user, get_current_user_optional

router = APIRouter()

from services.ai.worker import run_ai_investigation
from services.ai.embeddings import generate_embedding
from models.ai_investigation import AIInvestigation
from core.config import settings

class ProblemDraft(BaseModel):
    title: str
    description: str

@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return [{"id": str(c.id), "name": c.name, "description": c.description} for c in categories]

@router.post("/similar")
def find_similar_problems(
    draft: ProblemDraft,
    db: Session = Depends(get_db)
):
    text_to_embed = f"{draft.title}\n{draft.description}"
    emb = generate_embedding(text_to_embed)
    
    # Cosine distance: smaller is more similar. Threshold e.g. < 0.2
    similar_problems = db.query(Problem).filter(
        Problem.embedding.cosine_distance(emb) < 0.2,
        Problem.is_public == True
    ).order_by(Problem.embedding.cosine_distance(emb)).limit(5).all()
    
    # Return brief info
    return [{"public_id": p.public_id, "title": p.title, "status": p.status} for p in similar_problems]

@router.post("", response_model=ProblemResponse, status_code=status.HTTP_201_CREATED)
def create_problem(
    *,
    db: Session = Depends(get_db),
    problem_in: ProblemCreate,
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    public_id = generate(size=10)
    
    # Handle category
    category_id = None
    if problem_in.category_name:
        category = db.query(Category).filter(Category.name == problem_in.category_name).first()
        if not category:
            category = Category(name=problem_in.category_name)
            db.add(category)
            db.flush()
        category_id = category.id

    # Generate embedding
    emb = generate_embedding(f"{problem_in.title}\n{problem_in.description}")

    # Moderation analysis
    from services.moderation import analyze_content, record_flags
    analysis = analyze_content(f"{problem_in.title} {problem_in.description}")
    
    # If high risk, block immediately
    if analysis["risk_level"] == "HIGH":
        raise HTTPException(status_code=400, detail="Content blocked by automated moderation.")

    db_problem = Problem(
        public_id=public_id,
        author_id=current_user.id,
        title=problem_in.title,
        description=problem_in.description,
        priority=problem_in.priority,
        urgency=problem_in.urgency,
        is_public=problem_in.is_public,
        location=problem_in.location,
        category_id=category_id,
        status=ProblemStatus.AI_PROCESSING,
        embedding=emb,
        is_hidden=(analysis["risk_level"] == "MEDIUM")
    )
    db.add(db_problem)
    db.flush()

    # Record any flags
    record_flags(db, "problem", str(db_problem.id), analysis)

    # Handle tags
    if problem_in.tags:
        for tag_name in problem_in.tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.flush()
            db_problem.tags.append(tag)

    # Create AI Investigation record
    investigation = AIInvestigation(
        problem_id=db_problem.id,
        provider=settings.AI_PROVIDER,
        model=settings.AI_MODEL
    )
    db.add(investigation)

    db.commit()
    db.refresh(db_problem)
    db.refresh(investigation)
    
    # Trigger AI structuring
    background_tasks.add_task(run_ai_investigation, db, investigation.id)
    
    return db_problem

@router.get("", response_model=PaginatedProblems)
def get_problems(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    is_public: Optional[bool] = None,
    status: Optional[ProblemStatus] = None,
    category: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    query = db.query(Problem)
    
    if current_user:
        if is_public is not None:
            if is_public:
                query = query.filter(Problem.is_public == True, Problem.is_hidden == False)
            else:
                query = query.filter(Problem.author_id == current_user.id, Problem.is_public == False)
        else:
            query = query.filter(((Problem.is_public == True) & (Problem.is_hidden == False)) | (Problem.author_id == current_user.id))
    else:
        query = query.filter(Problem.is_public == True, Problem.is_hidden == False)

    if status:
        query = query.filter(Problem.status == status)
        
    if category:
        query = query.join(Category).filter(Category.name == category)

    total = query.count()
    items = query.order_by(desc(Problem.created_at)).offset((page - 1) * size).limit(size).all()
    
    return PaginatedProblems(items=items, total=total, page=page, size=size)

@router.get("/search", response_model=PaginatedProblems)
def search_problems(
    q: Optional[str] = "",
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
):
    if not q.strip():
        return PaginatedProblems(items=[], total=0, page=page, size=size)
        
    emb = generate_embedding(q)
    
    # Hybrid search
    vector_str = f"[{','.join(map(str, emb))}]"
    
    query = f"""
        SELECT 
            p.*,
            (1.0 - (p.embedding <=> :vector)) as vector_score,
            ts_rank_cd(to_tsvector('english', p.title || ' ' || p.description), plainto_tsquery('english', :query)) as text_score
        FROM problems p
        WHERE p.is_public = True AND p.is_hidden = False
        ORDER BY (
            (1.0 - (p.embedding <=> :vector)) * 0.7 + 
            ts_rank_cd(to_tsvector('english', p.title || ' ' || p.description), plainto_tsquery('english', :query)) * 0.3
        ) DESC
        LIMIT :limit OFFSET :offset
    """
    
    results = db.execute(text(query), {"query": q, "vector": vector_str, "limit": size, "offset": (page - 1) * size}).mappings().all()
    
    # Needs to match ProblemResponse, we can just fetch the actual objects using the ordered IDs
    if not results:
        return PaginatedProblems(items=[], total=0, page=page, size=size)
        
    ids = [r["id"] for r in results]
    
    # To keep the exact sorted order
    problems = db.query(Problem).filter(Problem.id.in_(ids)).all()
    problems_sorted = sorted(problems, key=lambda x: ids.index(x.id))
    
    # Get total count (not exact for hybrid, but we can do a naive count)
    total_query = "SELECT count(*) FROM problems WHERE is_public = True AND is_hidden = False"
    total = db.execute(text(total_query)).scalar()
    
    return PaginatedProblems(items=problems_sorted, total=total, page=page, size=size)

@router.get("/{public_id}", response_model=ProblemResponse)
def get_problem(
    public_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    problem = db.query(Problem).filter(Problem.public_id == public_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    if not problem.is_public or problem.is_hidden:
        if not current_user or problem.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions to view this problem")
        
    return problem

@router.patch("/{public_id}", response_model=ProblemResponse)
def update_problem(
    public_id: str,
    problem_in: ProblemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    problem = db.query(Problem).filter(Problem.public_id == public_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    if problem.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    update_data = problem_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(problem, field, value)
        
    db.commit()
    db.refresh(problem)
    
    # Re-trigger AI
    if problem.investigation and (problem_in.title or problem_in.description):
        background_tasks.add_task(run_ai_investigation, db, problem.investigation.id)
        
    return problem

@router.delete("/{public_id}")
def delete_problem(
    public_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    problem = db.query(Problem).filter(Problem.public_id == public_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    if problem.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    db.delete(problem)
    db.commit()
    return {"message": "Problem deleted successfully"}

class ClarificationAnswer(BaseModel):
    answer: str

@router.post("/{public_id}/clarifications/{clarification_id}", response_model=ProblemResponse)
def answer_clarification(
    public_id: str,
    clarification_id: str,
    answer_in: ClarificationAnswer,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    from models.ai_investigation import ProblemClarification
    
    problem = db.query(Problem).filter(Problem.public_id == public_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    if problem.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    clarification = db.query(ProblemClarification).filter(ProblemClarification.id == clarification_id).first()
    if not clarification:
        raise HTTPException(status_code=404, detail="Clarification not found")
        
    clarification.answer = answer_in.answer
    clarification.answered_at = func.now()
    db.commit()
    
    # Re-trigger AI structuring with new info
    if problem.investigation:
        background_tasks.add_task(run_ai_investigation, db, problem.investigation.id)
        
    db.refresh(problem)
    return problem
