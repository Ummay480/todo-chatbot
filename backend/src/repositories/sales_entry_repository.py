from sqlalchemy.orm import Session
from typing import List, Optional
from .base_repository import BaseRepository
from ..models.SalesEntry import SalesEntry


class SalesEntryRepository(BaseRepository[SalesEntry]):
    """
    Repository for SalesEntry model operations
    """

    def __init__(self, db_session: Session):
        super().__init__(SalesEntry, db_session)

    def get_by_ledger_page_id(self, ledger_page_id: int) -> List[SalesEntry]:
        """Get all sales entries for a specific ledger page"""
        return self.db_session.query(SalesEntry).filter(
            SalesEntry.ledger_page_id == ledger_page_id
        ).all()

    def get_by_fuel_type(self, fuel_type: str) -> List[SalesEntry]:
        """Get all sales entries for a specific fuel type"""
        return self.db_session.query(SalesEntry).filter(
            SalesEntry.fuel_type == fuel_type
        ).all()

    def get_by_date_range(self, start_date, end_date):
        """Get sales entries within a date range"""
        return self.db_session.query(SalesEntry).filter(
            SalesEntry.date >= start_date,
            SalesEntry.date <= end_date
        ).all()

    def get_by_nozzle_id(self, nozzle_id: str) -> List[SalesEntry]:
        """Get all sales entries for a specific nozzle ID"""
        return self.db_session.query(SalesEntry).filter(
            SalesEntry.nozzle_id == nozzle_id
        ).all()

    def get_low_confidence_entries(self, threshold: float = 85.0) -> List[SalesEntry]:
        """Get all sales entries with OCR confidence below the threshold"""
        return self.db_session.query(SalesEntry).filter(
            SalesEntry.ocr_confidence < threshold
        ).all()