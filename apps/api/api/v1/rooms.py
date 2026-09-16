from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import uuid
from datetime import datetime
from pydantic import BaseModel

from core.database import get_db
from models.user import User
from models.problem import Problem
from models.room import ProblemRoom, RoomMember, RoomMessage
from api.deps import get_current_user
from .ws import manager

router = APIRouter()

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

@router.get("/problems/{public_id}/room", response_model=RoomResponse)
def get_or_create_room(
    public_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    problem = db.query(Problem).filter(Problem.public_id == public_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    room = db.query(ProblemRoom).filter(ProblemRoom.problem_id == problem.id).first()
    if not room:
        room = ProblemRoom(problem_id=problem.id)
        db.add(room)
        db.commit()
        db.refresh(room)
        
    return room

@router.get("/rooms/{room_id}/messages", response_model=List[MessageResponse])
def get_room_messages(
    room_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    room = db.query(ProblemRoom).filter(ProblemRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
        
    if room.is_private:
        member = db.query(RoomMember).filter(RoomMember.room_id == room.id, RoomMember.user_id == current_user.id).first()
        if not member:
            raise HTTPException(status_code=403, detail="Not authorized to enter this private room")
            
    # We should order by created_at asc for chat history
    messages = db.query(RoomMessage).filter(RoomMessage.room_id == room_id).order_by(RoomMessage.created_at.asc()).all()
    return messages

@router.post("/rooms/{room_id}/messages", response_model=MessageResponse)
async def create_message(
    room_id: uuid.UUID,
    msg_in: MessageBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    room = db.query(ProblemRoom).filter(ProblemRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
        
    if room.is_private:
        member = db.query(RoomMember).filter(RoomMember.room_id == room.id, RoomMember.user_id == current_user.id).first()
        if not member:
            raise HTTPException(status_code=403, detail="Not authorized to post in this private room")
            
    msg = RoomMessage(
        room_id=room_id,
        author_id=current_user.id,
        content=msg_in.content
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    
    # Broadcast via WS Manager
    await manager.broadcast_to_room(str(room_id), {
        "type": "message.created",
        "payload": {
            "id": str(msg.id),
            "content": msg.content,
            "author_id": str(msg.author_id),
            "author_email": current_user.email,
            "created_at": msg.created_at.isoformat()
        }
    })
    
    return msg

