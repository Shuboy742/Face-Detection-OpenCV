from sqlalchemy import Column, String, Date, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database_sqlite import Base
import uuid


class SpecialEvent(Base):
    __tablename__ = "special_events"
    
    event_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, ForeignKey('employees.employee_id'), nullable=False)
    event_type = Column(String(50), nullable=False)  # 'birthday', 'anniversary', 'achievement', etc.
    event_date = Column(Date, nullable=False)
    event_description = Column(Text)
    greeting_template = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationship
    employee = relationship("Employee")
    
    def __repr__(self):
        return f"<SpecialEvent(employee_id='{self.employee_id}', type='{self.event_type}', date='{self.event_date}')>"
