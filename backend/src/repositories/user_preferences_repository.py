from sqlalchemy.orm import Session
from typing import Optional
from .base_repository import BaseRepository
from ..models.UserPreferences import UserPreferences


class UserPreferencesRepository(BaseRepository[UserPreferences]):
    """
    Repository for UserPreferences model operations
    """

    def __init__(self, db_session: Session):
        super().__init__(UserPreferences, db_session)

    def get_by_user_id(self, user_id: int) -> Optional[UserPreferences]:
        """Get user preferences for a specific user"""
        return self.db_session.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()

    def update_language_preference(self, user_id: int, language: str) -> Optional[UserPreferences]:
        """Update language preference for a user"""
        user_prefs = self.get_by_user_id(user_id)
        if user_prefs:
            user_prefs.language_preference = language
            self.db_session.commit()
            self.db_session.refresh(user_prefs)
        return user_prefs

    def update_report_layout(self, user_id: int, layout: str) -> Optional[UserPreferences]:
        """Update report layout preference for a user"""
        user_prefs = self.get_by_user_id(user_id)
        if user_prefs:
            user_prefs.report_layout = layout
            self.db_session.commit()
            self.db_session.refresh(user_prefs)
        return user_prefs