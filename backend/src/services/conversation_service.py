from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from ..repositories.conversation_repository import ConversationRepository
from ..repositories.message_repository import MessageRepository
from ..models.Conversation import Conversation

class ConversationService:
    """Service layer for conversation business logic"""

    def __init__(self, db: Session):
        self.conversation_repo = ConversationRepository(db)
        self.message_repo = MessageRepository(db)

    def create_conversation(self, user_id: int, title: Optional[str] = None) -> Dict[str, Any]:
        """Create a new conversation"""
        conversation = self.conversation_repo.create(user_id, title)
        return conversation.to_dict()

    def get_conversation(self, conversation_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a conversation with its messages"""
        conversation = self.conversation_repo.get_by_id(conversation_id, user_id)
        if not conversation:
            return None

        messages = self.message_repo.get_by_conversation(conversation_id)
        result = conversation.to_dict()
        result["messages"] = [msg.to_dict() for msg in messages]
        return result

    def list_conversations(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """List all conversations for a user"""
        conversations = self.conversation_repo.get_all_by_user(user_id, limit)
        return [conv.to_dict() for conv in conversations]

    def get_or_create_latest_conversation(self, user_id: int) -> Dict[str, Any]:
        """Get the latest conversation or create a new one"""
        conversation = self.conversation_repo.get_latest_by_user(user_id)
        if not conversation:
            conversation = self.conversation_repo.create(user_id)
        return conversation.to_dict()

    def add_message(self, conversation_id: int, user_id: int, role: str, content: str) -> Dict[str, Any]:
        """Add a message to a conversation"""
        if role not in ["user", "assistant"]:
            raise ValueError("Role must be 'user' or 'assistant'")

        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")

        # Verify conversation belongs to user
        conversation = self.conversation_repo.get_by_id(conversation_id, user_id)
        if not conversation:
            raise ValueError("Conversation not found")

        message = self.message_repo.create(conversation_id, user_id, role, content.strip())
        return message.to_dict()

    def get_conversation_history(self, conversation_id: int, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history"""
        # Verify conversation belongs to user
        conversation = self.conversation_repo.get_by_id(conversation_id, user_id)
        if not conversation:
            return []

        messages = self.message_repo.get_by_conversation(conversation_id, limit)
        return [msg.to_dict() for msg in messages]

    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Delete a conversation"""
        return self.conversation_repo.delete(conversation_id, user_id)
