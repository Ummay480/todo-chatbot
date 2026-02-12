from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.Message import Message

class MessageRepository:
    """Repository for Message data access operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, conversation_id: int, user_id: int, role: str, content: str) -> Message:
        """Create a new message"""
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_by_id(self, message_id: int) -> Optional[Message]:
        """Get a message by ID"""
        return self.db.query(Message).filter(Message.id == message_id).first()

    def get_by_conversation(self, conversation_id: int, limit: int = 100) -> List[Message]:
        """Get all messages for a conversation"""
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).limit(limit).all()

    def get_recent_by_conversation(self, conversation_id: int, limit: int = 10) -> List[Message]:
        """Get recent messages for a conversation"""
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(limit).all()

    def delete(self, message_id: int) -> bool:
        """Delete a message"""
        message = self.get_by_id(message_id)
        if not message:
            return False

        self.db.delete(message)
        self.db.commit()
        return True
