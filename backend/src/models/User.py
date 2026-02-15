from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    phone_number = Column(String, nullable=True)
<<<<<<< HEAD
    language_preference = Column(String, default="en")
=======
    pump_name = Column(String, nullable=True)
    pump_location = Column(String, nullable=True)
    language_preference = Column(String, default="en")  # en for English, ur for Urdu
>>>>>>> d6ea802f0de91b405329275a8647530d1b4ee92c
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
<<<<<<< HEAD
    tasks = relationship("Task", order_by="Task.id", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", order_by="Conversation.id", back_populates="user", cascade="all, delete-orphan")
=======
    ledger_pages = relationship("LedgerPage", order_by="LedgerPage.id", back_populates="user")
    daily_reports = relationship("DailyReport", order_by="DailyReport.id", back_populates="user")
    monthly_reports = relationship("MonthlyReport", order_by="MonthlyReport.id", back_populates="user")
    user_preferences = relationship("UserPreferences", uselist=False, back_populates="user")
>>>>>>> d6ea802f0de91b405329275a8647530d1b4ee92c

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"