import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from .base import Base

class ExpertStatus(str, enum.Enum):
    UNVERIFIED = "UNVERIFIED"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    SUSPENDED = "SUSPENDED"

class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"

class ExpertProfile(Base):
    __tablename__ = "expert_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    status = Column(Enum(ExpertStatus), default=ExpertStatus.UNVERIFIED, nullable=False)
    verification_level = Column(Integer, default=1) # 1=Standard, 2=Premium, etc.
    
    bio = Column(Text, nullable=True)
    timezone = Column(String, default="UTC")
    is_available = Column(Boolean, default=True)
    years_experience = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User")
    
class ExpertRequest(Base):
    __tablename__ = "expert_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem_id = Column(UUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False)
    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    expert_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING, nullable=False)
    message = Column(Text, nullable=True) # Optional message from requester
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    problem = relationship("Problem")
    requester = relationship("User", foreign_keys=[requester_id])
    expert = relationship("User", foreign_keys=[expert_id])

