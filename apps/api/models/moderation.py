import uuid
import enum
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base

class ReportReason(str, enum.Enum):
    SPAM = "spam"
    HARASSMENT = "harassment"
    MISINFORMATION = "misinformation"
    DANGEROUS = "dangerous content"
    PRIVACY = "privacy violation"
    OTHER = "other"

class ReportStatus(str, enum.Enum):
    PENDING = "PENDING"
    REVIEWED = "REVIEWED"
    DISMISSED = "DISMISSED"

class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    entity_type = Column(String, nullable=False) # problem, solution, comment, user
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    
    reason = Column(Enum(ReportReason), nullable=False)
    details = Column(Text, nullable=True)
    
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ModActionType(str, enum.Enum):
    HIDE = "HIDE"
    LOCK = "LOCK"
    RESTORE = "RESTORE"
    WARN = "WARN"
    SUSPEND = "SUSPEND"

class ModerationAction(Base):
    __tablename__ = "moderation_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    moderator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    entity_type = Column(String, nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    target_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    action = Column(Enum(ModActionType), nullable=False)
    reason = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ContentFlag(Base):
    __tablename__ = "content_flags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String, nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    
    risk_level = Column(String, nullable=False) # LOW, MEDIUM, HIGH
    flags = Column(JSONB, nullable=False) # {"pii": True, "spam": False}
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserRestriction(Base):
    __tablename__ = "user_restrictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    restriction_type = Column(String, nullable=False) # e.g., READ_ONLY, SUSPENDED
    reason = Column(Text, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

