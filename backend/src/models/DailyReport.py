from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.connection import Base

class DailyReport(Base):
    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_date = Column(DateTime, nullable=False)  # The date this report covers
    total_liters_petrol = Column(Float, default=0.0)  # Total liters of petrol sold
    total_liters_diesel = Column(Float, default=0.0)  # Total liters of diesel sold
    total_liters_cng = Column(Float, default=0.0)  # Total liters of CNG sold
    total_revenue_petrol = Column(Float, default=0.0)  # Total revenue from petrol
    total_revenue_diesel = Column(Float, default=0.0)  # Total revenue from diesel
    total_revenue_cng = Column(Float, default=0.0)  # Total revenue from CNG
    total_nozzles_count = Column(Integer, default=0)  # Number of nozzles active
    total_sales_entries = Column(Integer, default=0)  # Total number of sales entries
    grand_total_liters = Column(Float, default=0.0)  # Grand total liters sold
    grand_total_revenue = Column(Float, default=0.0)  # Grand total revenue
    generated_at = Column(DateTime, default=datetime.utcnow)  # When report was generated
    export_format = Column(String, default="json")  # Format: json, csv, pdf
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="daily_reports")

    def __repr__(self):
        return f"<DailyReport(id={self.id}, user_id={self.user_id}, date='{self.report_date}')>"