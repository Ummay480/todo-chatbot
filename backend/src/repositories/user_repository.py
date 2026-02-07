from sqlalchemy.orm import Session
from typing import Optional
from .base_repository import BaseRepository
from ..models.User import User


class UserRepository(BaseRepository[User]):
    """
    Repository for User model operations
    """

    def __init__(self, db_session: Session):
        super().__init__(User, db_session)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        return self.db_session.query(User).filter(User.email == email).first()

    def get_by_phone_number(self, phone_number: str) -> Optional[User]:
        """Get user by phone number"""
        return self.db_session.query(User).filter(User.phone_number == phone_number).first()

    def get_by_pump_name(self, pump_name: str) -> Optional[User]:
        """Get user by pump name"""
        return self.db_session.query(User).filter(User.pump_name == pump_name).first()