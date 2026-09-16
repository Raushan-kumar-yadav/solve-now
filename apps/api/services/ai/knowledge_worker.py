from sqlalchemy.orm import Session
import os
import logging
from models.problem import Problem
from models.solution import Solution
from models.knowledge import KnowledgeDocument, KnowledgeSource, KnowledgeStatus
from services.ai.agents.knowledge import KnowledgeAgent
from services.ai.embeddings import generate_embedding

logger = logging.getLogger(__name__)


def run_knowledge_extraction(db: Session, problem_id: str, solution_id: str):
    """
    Background worker that runs when a solution is accepted.
    Evaluates the solution and potentially writes it to the Knowledge Base.
    """
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    solution = db.query(Solution).filter(Solution.id == solution_id).first()

    if not problem or not solution:
        logger.warning(f"Knowledge extraction skipped: problem={problem_id} solution={solution_id} not found")
        return

    api_key = os.environ.get("AI_API_KEY") or os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        logger.warning("Knowledge extraction skipped: AI_API_KEY not configured")
        return

    agent = KnowledgeAgent(api_key=api_key)

    
    problem_text = f"{problem.title}\n{problem.description}"
    out = agent.evaluate_and_draft(problem_text, solution.content, solution.verification_count)
    
    if out.is_quality_sufficient:
        # Generate embedding for hybrid search
        emb = generate_embedding(f"{out.title}\n{out.content}")
        
        doc = KnowledgeDocument(
            title=out.title,
            content=out.content,
            category_id=problem.category_id,
            status=KnowledgeStatus.PUBLISHED,
            quality_score=out.quality_score,
            verification_count=solution.verification_count,
            embedding=emb
        )
        db.add(doc)
        db.flush()
        
        source = KnowledgeSource(
            knowledge_document_id=doc.id,
            problem_id=problem.id,
            solution_id=solution.id
        )
        db.add(source)
        db.commit()

