import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum, Integer, Float, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from .base import Base

class SolutionStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class Solution(Base):
    __tablename__ = "solutions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(SolutionStatus), default=SolutionStatus.PENDING, nullable=False)
    confidence_score = Column(Float, default=0.0)
    is_hidden = Column(Boolean, default=False, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)

    problem = relationship("Problem", backref="solutions")
    author = relationship("User")
    votes = relationship("SolutionVote", back_populates="solution", cascade="all, delete-orphan")
    verifications = relationship("SolutionVerification", back_populates="solution", cascade="all, delete-orphan")
    comments = relationship("SolutionComment", back_populates="solution", cascade="all, delete-orphan")

class SolutionVote(Base):
    __tablename__ = "solution_votes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solution_id = Column(UUID(as_uuid=True), ForeignKey("solutions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    value = Column(Integer, nullable=False) # 1 for upvote, -1 for downvote
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    solution = relationship("Solution", back_populates="votes")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint('solution_id', 'user_id', name='uq_solution_user_vote'),
    )

class SolutionVerification(Base):
    __tablename__ = "solution_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solution_id = Column(UUID(as_uuid=True), ForeignKey("solutions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    solution = relationship("Solution", back_populates="verifications")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint('solution_id', 'user_id', name='uq_solution_user_verification'),
    )

class SolutionComment(Base):
    __tablename__ = "solution_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    solution_id = Column(UUID(as_uuid=True), ForeignKey("solutions.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    solution = relationship("Solution", back_populates="comments")
    author = relationship("User")

