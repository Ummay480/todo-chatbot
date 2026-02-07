from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.connection import Base

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    language_preference = Column(String, default="en")  # en for English, ur for Urdu
    report_layout = Column(String, default="standard")  # standard, compact, detailed
    date_format = Column(String, default="DD-MM-YYYY")  # DD-MM-YYYY, MM-DD-YYYY, YYYY-MM-DD
    unit_preference = Column(String, default="liters")  # liters, gallons
    currency_symbol = Column(String, default="₨")  # PKR symbol
    custom_column_order = Column(Text, nullable=True)  # JSON string for custom column ordering in reports
    enable_urdu_translation = Column(Boolean, default=True)  # Whether to show UI in Urdu
    enable_email_notifications = Column(Boolean, default=False)  # Whether to send email notifications
    enable_sms_notifications = Column(Boolean, default=False)  # Whether to send SMS notifications
    custom_report_templates = Column(Text, nullable=True)  # JSON string for custom report templates
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="user_preferences")

    def __repr__(self):
        return f"<UserPreferences(id={self.id}, user_id={self.user_id}, language='{self.language_preference}')>"