from sqlalchemy.orm import Session
from typing import List, Optional
from .base_repository import BaseRepository
from ..models.DailyReport import DailyReport


class DailyReportRepository(BaseRepository[DailyReport]):
    """
    Repository for DailyReport model operations
    """

    def __init__(self, db_session: Session):
        super().__init__(DailyReport, db_session)

    def get_by_user_id(self, user_id: int) -> List[DailyReport]:
        """Get all daily reports for a specific user"""
        return self.db_session.query(DailyReport).filter(
            DailyReport.user_id == user_id
        ).order_by(DailyReport.report_date.desc()).all()

    def get_by_date(self, user_id: int, report_date) -> Optional[DailyReport]:
        """Get a daily report for a specific user and date"""
        return self.db_session.query(DailyReport).filter(
            DailyReport.user_id == user_id,
            DailyReport.report_date == report_date
        ).first()

    def get_by_date_range(self, user_id: int, start_date, end_date):
        """Get daily reports within a date range for a specific user"""
        return self.db_session.query(DailyReport).filter(
            DailyReport.user_id == user_id,
            DailyReport.report_date >= start_date,
            DailyReport.report_date <= end_date
        ).order_by(DailyReport.report_date).all()

    def get_by_month(self, user_id: int, year: int, month: int):
        """Get all daily reports for a specific user in a specific month"""
        from sqlalchemy import extract
        return self.db_session.query(DailyReport).filter(
            DailyReport.user_id == user_id,
            extract('year', DailyReport.report_date) == year,
            extract('month', DailyReport.report_date) == month
        ).order_by(DailyReport.report_date).all()