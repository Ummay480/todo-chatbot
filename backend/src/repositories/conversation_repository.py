from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models.Conversation import Conversation

class ConversationRepository:
    """Repository for Conversation data access operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, title: Optional[str] = None) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            user_id=user_id,
            title=title
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_by_id(self, conversation_id: int, user_id: int) -> Optional[Conversation]:
        """Get a conversation by ID for a specific user"""
        return self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()

    def get_all_by_user(self, user_id: int, limit: int = 50) -> List[Conversation]:
        """Get all conversations for a user"""
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).limit(limit).all()

    def get_latest_by_user(self, user_id: int) -> Optional[Conversation]:
        """Get the most recent conversation for a user"""
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).first()

    def update(self, conversation_id: int, user_id: int, **kwargs) -> Optional[Conversation]:
        """Update a conversation"""
        conversation = self.get_by_id(conversation_id, user_id)
        if not conversation:
            return None

        for key, value in kwargs.items():
            if hasattr(conversation, key):
                setattr(conversation, key, value)

        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def delete(self, conversation_id: int, user_id: int) -> bool:
        """Delete a conversation"""
        conversation = self.get_by_id(conversation_id, user_id)
        if not conversation:
            return False

        self.db.delete(conversation)
        self.db.commit()
        return True
