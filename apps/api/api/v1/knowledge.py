from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, desc
import uuid
from typing import List, Optional

from core.database import get_db
from models.knowledge import KnowledgeDocument, KnowledgeStatus
from services.ai.embeddings import generate_embedding
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class KnowledgeSearchResponse(BaseModel):
    id: uuid.UUID
    title: str
    content_snippet: str
    category: Optional[str]
    quality_score: int
    verification_count: int
    relevance: float
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/search", response_model=List[KnowledgeSearchResponse])
def search_knowledge(
    q: Optional[str] = "",
    category: Optional[str] = None,
    verified_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Hybrid Search combining pgvector and Full Text Search.
    Ranking = (Vector Similarity) + (FTS Rank) + (0.1 * log(verification_count + 1)) + (0.01 * quality_score)
    """
    if not q or not q.strip():
        # If no query is provided, return recent verified knowledge
        results = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.status == 'PUBLISHED'
        ).order_by(desc(KnowledgeDocument.created_at)).limit(20).all()
        
        response = []
        for r in results:
            response.append(KnowledgeSearchResponse(
                id=r.id,
                title=r.title,
                content_snippet=r.content[:200] + "..." if len(r.content) > 200 else r.content,
                category=r.category.name if r.category else None,
                quality_score=r.quality_score,
                verification_count=r.verification_count,
                relevance=1.0,
                created_at=r.created_at
            ))
        return response
        
    emb = generate_embedding(q)
    
    # In PostgreSQL, <=> is cosine distance, so smaller is closer.
    # To convert distance to similarity: 1 - (distance)
    
    # We will use raw SQL for hybrid search to balance the text scores and embeddings easily.
    # We format the vector string properly for pgvector.
    vector_str = f"[{','.join(map(str, emb))}]"
    
    base_query = """
        SELECT 
            kd.id, kd.title, kd.content, c.name as category,
            kd.quality_score, kd.verification_count, kd.created_at,
            (1.0 - (kd.embedding <=> :vector)) as vector_score,
            ts_rank_cd(to_tsvector('english', kd.title || ' ' || kd.content), plainto_tsquery('english', :query)) as text_score
        FROM knowledge_documents kd
        LEFT JOIN problem_categories c ON kd.category_id = c.id
        WHERE kd.status = 'PUBLISHED'
    """
    
    filters = []
    params = {"query": q, "vector": vector_str}
    
    if category:
        filters.append("c.name = :category")
        params["category"] = category
        
    if verified_only:
        filters.append("kd.verification_count > 0")
        
    if filters:
        base_query += " AND " + " AND ".join(filters)
        
    # Order by combined hybrid score
    # Note: text_score is usually between 0 and 1, vector_score is usually between 0 and 1.
    # We add a small bonus for verifications and quality score.
    final_query = base_query + """
        ORDER BY (
            (1.0 - (kd.embedding <=> :vector)) * 0.7 + 
            ts_rank_cd(to_tsvector('english', kd.title || ' ' || kd.content), plainto_tsquery('english', :query)) * 0.3 +
            LN(kd.verification_count + 1) * 0.1 +
            (kd.quality_score * 0.01)
        ) DESC
        LIMIT 20
    """
    
    results = db.execute(text(final_query), params).mappings().all()
    
    response = []
    for r in results:
        # Calculate combined relevance for UI display
        rel = (r["vector_score"] * 0.7) + (r["text_score"] * 0.3)
        response.append(KnowledgeSearchResponse(
            id=r["id"],
            title=r["title"],
            content_snippet=r["content"][:200] + "..." if len(r["content"]) > 200 else r["content"],
            category=r["category"],
            quality_score=r["quality_score"],
            verification_count=r["verification_count"],
            relevance=rel,
            created_at=r["created_at"]
        ))
        
    return response

@router.get("/{document_id}")
def get_knowledge_doc(
    document_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == document_id, KnowledgeDocument.status == KnowledgeStatus.PUBLISHED).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    return {
        "id": doc.id,
        "title": doc.title,
        "content": doc.content,
        "category": doc.category.name if doc.category else None,
        "quality_score": doc.quality_score,
        "verification_count": doc.verification_count,
        "created_at": doc.created_at,
        "updated_at": doc.updated_at
    }

