import uuid
from datetime import datetime
from pydantic import BaseModel

class MessageBase(BaseModel):
    content: str

class MessageResponse(MessageBase):
    id: uuid.UUID
    room_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class RoomResponse(BaseModel):
    id: uuid.UUID
    problem_id: uuid.UUID
    is_active: bool
    
    class Config:
        from_attributes = True

