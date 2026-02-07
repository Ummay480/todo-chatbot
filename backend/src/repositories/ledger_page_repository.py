from sqlalchemy.orm import Session
from typing import List, Optional
from .base_repository import BaseRepository
from ..models.LedgerPage import LedgerPage


class LedgerPageRepository(BaseRepository[LedgerPage]):
    """
    Repository for LedgerPage model operations
    """

    def __init__(self, db_session: Session):
        super().__init__(LedgerPage, db_session)

    def get_by_user_id(self, user_id: int) -> List[LedgerPage]:
        """Get all ledger pages for a specific user"""
        return self.db_session.query(LedgerPage).filter(LedgerPage.user_id == user_id).all()

    def get_by_processing_status(self, status: str) -> List[LedgerPage]:
        """Get all ledger pages with a specific processing status"""
        return self.db_session.query(LedgerPage).filter(LedgerPage.processing_status == status).all()

    def get_by_user_and_status(self, user_id: int, status: str) -> List[LedgerPage]:
        """Get ledger pages for a user with a specific processing status"""
        return self.db_session.query(LedgerPage).filter(
            LedgerPage.user_id == user_id,
            LedgerPage.processing_status == status
        ).all()

    def get_by_upload_date_range(self, start_date, end_date):
        """Get ledger pages within a date range"""
        return self.db_session.query(LedgerPage).filter(
            LedgerPage.upload_date >= start_date,
            LedgerPage.upload_date <= end_date
        ).all()