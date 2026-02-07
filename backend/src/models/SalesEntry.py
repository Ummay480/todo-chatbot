from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.connection import Base

class SalesEntry(Base):
    __tablename__ = "sales_entries"

    id = Column(Integer, primary_key=True, index=True)
    ledger_page_id = Column(Integer, ForeignKey("ledger_pages.id"), nullable=False)
    date = Column(DateTime, nullable=True)  # Date from the ledger entry
    nozzle_id = Column(String, nullable=True)  # Nozzle/Dispenser ID
    fuel_type = Column(String, nullable=True)  # Petrol, Diesel, CNG, etc.
    opening_reading = Column(Float, nullable=True)  # Opening meter reading
    closing_reading = Column(Float, nullable=True)  # Closing meter reading
    liters_sold = Column(Float, nullable=True)  # Calculated liters sold
    rate_per_liter = Column(Float, nullable=True)  # Rate per liter
    total_amount = Column(Float, nullable=True)  # Calculated total amount
    ocr_confidence = Column(Float, nullable=True)  # OCR confidence score for this entry
    is_manual_correction = Column(Boolean, default=False)  # Whether entry was manually corrected
    manual_correction_notes = Column(Text, nullable=True)  # Notes about manual corrections
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    ledger_page = relationship("LedgerPage", back_populates="sales_entries")

    def __repr__(self):
        return f"<SalesEntry(id={self.id}, ledger_page_id={self.ledger_page_id}, fuel_type='{self.fuel_type}', liters_sold={self.liters_sold})>"