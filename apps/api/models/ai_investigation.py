import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum, Integer, Float, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from .base import Base

class InvestigationStatus(str, enum.Enum):
    CREATED = "CREATED"
    ANALYZING = "ANALYZING"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    RESEARCHING = "RESEARCHING"
    DIAGNOSING = "DIAGNOSING"
    GENERATING = "GENERATING"
    REVIEWING = "REVIEWING"
    READY = "READY"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class AIInvestigation(Base):
    __tablename__ = "ai_investigations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), unique=True, nullable=False)
    status = Column(Enum(InvestigationStatus), default=InvestigationStatus.CREATED, nullable=False)
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    latency_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    problem = relationship("Problem")
    findings = relationship("AIFinding", back_populates="investigation", cascade="all, delete-orphan")
    clarifications = relationship("ProblemClarification", back_populates="investigation", cascade="all, delete-orphan")
    actions = relationship("AIAction", back_populates="investigation", cascade="all, delete-orphan")
    solutions = relationship("AIProposedSolution", back_populates="investigation", cascade="all, delete-orphan")

class AIFinding(Base):
    __tablename__ = "ai_findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id = Column(UUID(as_uuid=True), ForeignKey("ai_investigations.id", ondelete="CASCADE"), nullable=False)
    
    finding = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    evidence = Column(Text, nullable=False)
    source = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    investigation = relationship("AIInvestigation", back_populates="findings")

class AIProposedSolution(Base):
    __tablename__ = "ai_proposed_solutions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id = Column(UUID(as_uuid=True), ForeignKey("ai_investigations.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    steps = Column(JSON, nullable=False) # List of strings
    confidence = Column(Float, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    investigation = relationship("AIInvestigation", back_populates="solutions")
    critic_review = relationship("AICriticReview", back_populates="solution", uselist=False, cascade="all, delete-orphan")

class AICriticReview(Base):
    __tablename__ = "ai_critic_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solution_id = Column(UUID(as_uuid=True), ForeignKey("ai_proposed_solutions.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    is_safe = Column(Boolean, nullable=False)
    missing_evidence = Column(JSON, nullable=True) # List of strings
    contradictions = Column(JSON, nullable=True) # List of strings
    unsafe_instructions = Column(JSON, nullable=True) # List of strings
    weak_assumptions = Column(JSON, nullable=True) # List of strings
    alternative_explanations = Column(JSON, nullable=True) # List of strings
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    solution = relationship("AIProposedSolution", back_populates="critic_review")

class ProblemClarification(Base):
    __tablename__ = "problem_clarifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id = Column(UUID(as_uuid=True), ForeignKey("ai_investigations.id", ondelete="CASCADE"), nullable=False)
    
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    answered_at = Column(DateTime(timezone=True), nullable=True)

    investigation = relationship("AIInvestigation", back_populates="clarifications")

class AIAction(Base):
    __tablename__ = "ai_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id = Column(UUID(as_uuid=True), ForeignKey("ai_investigations.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String, nullable=False) 
    input_metadata = Column(JSON, nullable=True)
    output_metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    investigation = relationship("AIInvestigation", back_populates="actions")

class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id = Column(UUID(as_uuid=True), ForeignKey("ai_investigations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False) 
    content_summary = Column(Text, nullable=False) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
