from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.connection import Base

class MonthlyReport(Base):
    __tablename__ = "monthly_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    month_year = Column(String, nullable=False)  # Format: "YYYY-MM" (e.g., "2025-12")
    total_liters_petrol = Column(Float, default=0.0)  # Total liters of petrol sold in the month
    total_liters_diesel = Column(Float, default=0.0)  # Total liters of diesel sold in the month
    total_liters_cng = Column(Float, default=0.0)  # Total liters of CNG sold in the month
    total_revenue_petrol = Column(Float, default=0.0)  # Total revenue from petrol in the month
    total_revenue_diesel = Column(Float, default=0.0)  # Total revenue from diesel in the month
    total_revenue_cng = Column(Float, default=0.0)  # Total revenue from CNG in the month
    avg_daily_liters = Column(Float, default=0.0)  # Average daily liters sold
    avg_daily_revenue = Column(Float, default=0.0)  # Average daily revenue
    peak_sales_day = Column(DateTime, nullable=True)  # Day with highest sales
    peak_sales_amount = Column(Float, nullable=True)  # Amount of peak sales
    total_operational_days = Column(Integer, default=0)  # Number of operational days
    total_daily_reports = Column(Integer, default=0)  # Number of daily reports aggregated
    trend_indicator = Column(String, default="neutral")  # up, down, neutral
    generated_at = Column(DateTime, default=datetime.utcnow)  # When report was generated
    export_format = Column(String, default="json")  # Format: json, csv, pdf
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="monthly_reports")

    def __repr__(self):
        return f"<MonthlyReport(id={self.id}, user_id={self.user_id}, month='{self.month_year}')>"