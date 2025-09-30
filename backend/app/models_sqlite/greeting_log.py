from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database_sqlite import Base
import uuid


class GreetingLog(Base):
    __tablename__ = "greetings_log"
    
    log_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, ForeignKey('employees.employee_id'))
    greeting_type = Column(String(50))  # 'daily', 'birthday', 'anniversary', 'first_day', etc.
    greeting_text = Column(Text)
    recognition_confidence = Column(Float)  # Confidence score from face recognition
    recognition_method = Column(String(20))  # 'api' or 'local'
    timestamp = Column(DateTime, server_default=func.now())
    
    # Relationship
    employee = relationship("Employee")
    
    def __repr__(self):
        return f"<GreetingLog(employee_id='{self.employee_id}', type='{self.greeting_type}', confidence={self.recognition_confidence})>"
