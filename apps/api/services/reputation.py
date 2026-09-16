import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from models.reputation import ReputationEvent, UserExpertise
from models.user import User

class ReputationRules:
    SOLUTION_ACCEPTED = 50
    SOLUTION_VERIFIED = 20
    UPVOTE_RECEIVED = 5
    DOWNVOTE_RECEIVED = -2
    SPAM_PENALTY = -100

class ReputationService:
    def __init__(self, db: Session):
        self.db = db

    def award_points(self, user_id: uuid.UUID, event_type: str, points: int, problem_id: uuid.UUID = None, solution_id: uuid.UUID = None, category_id: uuid.UUID = None):
        """
        Awards reputation points. Implements strict anti-gaming rules.
        """
        # Anti-gaming: Cap daily upvote points to 50
        if event_type == "UPVOTE_RECEIVED":
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            daily_upvotes_query = self.db.query(func.sum(ReputationEvent.points)).filter(
                ReputationEvent.user_id == user_id,
                ReputationEvent.event_type == "UPVOTE_RECEIVED",
                ReputationEvent.created_at >= today_start
            ).scalar()
            
            daily_total = daily_upvotes_query or 0
            if daily_total >= 50:
                return # Daily cap reached

        # Create audit event
        event = ReputationEvent(
            user_id=user_id,
            event_type=event_type,
            points=points,
            problem_id=problem_id,
            solution_id=solution_id
        )
        self.db.add(event)
        
        # Update user cache
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.reputation_score += points
            
        # Update Category Expertise if category provided
        if category_id and points > 0:
            expertise = self.db.query(UserExpertise).filter(
                UserExpertise.user_id == user_id,
                UserExpertise.category_id == category_id
            ).first()
            
            if not expertise:
                expertise = UserExpertise(user_id=user_id, category_id=category_id, score=points)
                self.db.add(expertise)
            else:
                expertise.score += points

        self.db.commit()

    def revoke_points(self, user_id: uuid.UUID, event_type: str, points: int, problem_id: uuid.UUID = None, solution_id: uuid.UUID = None):
        """
        Reverses points, e.g., if an upvote is removed.
        """
        event = ReputationEvent(
            user_id=user_id,
            event_type=f"{event_type}_REVERTED",
            points=-points,
            problem_id=problem_id,
            solution_id=solution_id
        )
        self.db.add(event)
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.reputation_score -= points
            
        self.db.commit()

