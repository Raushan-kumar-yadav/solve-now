import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import enum

from .base import Base

class KnowledgeStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"
    FLAGGED = "FLAGGED"

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("problem_categories.id"), nullable=True)
    status = Column(Enum(KnowledgeStatus), default=KnowledgeStatus.DRAFT, nullable=False)
    
    # Reputation & Quality signals
    quality_score = Column(Integer, default=0)
    verification_count = Column(Integer, default=0)
    
    # Vector Search
    embedding = Column(Vector(768), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("Category")
    sources = relationship("KnowledgeSource", back_populates="knowledge_document", cascade="all, delete-orphan")
    versions = relationship("KnowledgeVersion", back_populates="knowledge_document", cascade="all, delete-orphan")

class KnowledgeSource(Base):
    """Maps a KnowledgeDocument to the originating Problem and accepted Solution."""
    __tablename__ = "knowledge_sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    knowledge_document_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id"), nullable=False)
    solution_id = Column(UUID(as_uuid=True), ForeignKey("solutions.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    knowledge_document = relationship("KnowledgeDocument", back_populates="sources")

class KnowledgeVersion(Base):
    __tablename__ = "knowledge_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    knowledge_document_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content_diff = Column(Text, nullable=False) # Or just snapshot of content
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    knowledge_document = relationship("KnowledgeDocument", back_populates="versions")

