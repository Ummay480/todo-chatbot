from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.connection import Base

class ColumnDefinition(Base):
    __tablename__ = "column_definitions"

    id = Column(Integer, primary_key=True, index=True)
    ledger_page_id = Column(Integer, ForeignKey("ledger_pages.id"), nullable=False)
    column_name = Column(String, nullable=False)  # e.g., "Date", "Nozzle ID", "Fuel Type", etc.
    column_type = Column(String, nullable=False)  # e.g., "date", "numeric", "text", "fuel_type", "nozzle_id", etc.
    position_order = Column(Integer, nullable=False)  # Position of column in the table (0-indexed)
    confidence_score = Column(Float, nullable=True)  # AI confidence in column identification
    is_manual_override = Column(Boolean, default=False)  # Whether column definition was manually adjusted
    manual_definition_notes = Column(Text, nullable=True)  # Notes about manual adjustments
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    ledger_page = relationship("LedgerPage", back_populates="column_definitions")

    def __repr__(self):
        return f"<ColumnDefinition(id={self.id}, ledger_page_id={self.ledger_page_id}, name='{self.column_name}', type='{self.column_type}')>"