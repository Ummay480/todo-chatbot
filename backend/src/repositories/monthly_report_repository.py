from sqlalchemy.orm import Session
from typing import List, Optional
from .base_repository import BaseRepository
from ..models.MonthlyReport import MonthlyReport


class MonthlyReportRepository(BaseRepository[MonthlyReport]):
    """
    Repository for MonthlyReport model operations
    """

    def __init__(self, db_session: Session):
        super().__init__(MonthlyReport, db_session)

    def get_by_user_id(self, user_id: int) -> List[MonthlyReport]:
        """Get all monthly reports for a specific user"""
        return self.db_session.query(MonthlyReport).filter(
            MonthlyReport.user_id == user_id
        ).order_by(MonthlyReport.month_year.desc()).all()

    def get_by_month_year(self, user_id: int, month_year: str) -> Optional[MonthlyReport]:
        """Get a monthly report for a specific user and month-year"""
        return self.db_session.query(MonthlyReport).filter(
            MonthlyReport.user_id == user_id,
            MonthlyReport.month_year == month_year
        ).first()

    def get_latest_for_user(self, user_id: int) -> Optional[MonthlyReport]:
        """Get the latest monthly report for a specific user"""
        return self.db_session.query(MonthlyReport).filter(
            MonthlyReport.user_id == user_id
        ).order_by(MonthlyReport.month_year.desc()).first()