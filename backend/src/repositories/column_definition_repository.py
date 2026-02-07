from sqlalchemy.orm import Session
from typing import List, Optional
from .base_repository import BaseRepository
from ..models.ColumnDefinition import ColumnDefinition


class ColumnDefinitionRepository(BaseRepository[ColumnDefinition]):
    """
    Repository for ColumnDefinition model operations
    """

    def __init__(self, db_session: Session):
        super().__init__(ColumnDefinition, db_session)

    def get_by_ledger_page_id(self, ledger_page_id: int) -> List[ColumnDefinition]:
        """Get all column definitions for a specific ledger page"""
        return self.db_session.query(ColumnDefinition).filter(
            ColumnDefinition.ledger_page_id == ledger_page_id
        ).order_by(ColumnDefinition.position_order).all()

    def get_by_column_type(self, column_type: str) -> List[ColumnDefinition]:
        """Get all column definitions of a specific type"""
        return self.db_session.query(ColumnDefinition).filter(
            ColumnDefinition.column_type == column_type
        ).all()

    def get_by_position_order(self, ledger_page_id: int, position_order: int) -> Optional[ColumnDefinition]:
        """Get a column definition by ledger page ID and position order"""
        return self.db_session.query(ColumnDefinition).filter(
            ColumnDefinition.ledger_page_id == ledger_page_id,
            ColumnDefinition.position_order == position_order
        ).first()