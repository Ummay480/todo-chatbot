from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.connection import Base

class LedgerPage(Base):
    __tablename__ = "ledger_pages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_image_url = Column(String, nullable=False)
    processed_image_url = Column(String, nullable=True)
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    processing_errors = Column(Text, nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ocr_confidence_score = Column(Float, nullable=True)
    detected_columns = Column(Text, nullable=True)  # JSON string of column definitions
    extracted_data = Column(Text, nullable=True)  # JSON string of extracted entries
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="ledger_pages")
    sales_entries = relationship("SalesEntry", order_by="SalesEntry.id", back_populates="ledger_page")
    column_definitions = relationship("ColumnDefinition", order_by="ColumnDefinition.position_order", back_populates="ledger_page")

    def __repr__(self):
        return f"<LedgerPage(id={self.id}, user_id={self.user_id}, status='{self.processing_status}')>"