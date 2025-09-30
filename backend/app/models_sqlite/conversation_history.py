from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database_sqlite import Base
import uuid


class ConversationHistory(Base):
    __tablename__ = "conversation_history"
    
    conversation_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, ForeignKey('employees.employee_id'))
    session_id = Column(String, nullable=False)
    user_input = Column(Text)
    system_response = Column(Text)
    intent_detected = Column(String(100))
    language_used = Column(String(10), default='en')
    timestamp = Column(DateTime, server_default=func.now())
    
    # Relationship
    employee = relationship("Employee")
    
    def __repr__(self):
        return f"<ConversationHistory(employee_id='{self.employee_id}', session_id='{self.session_id}', intent='{self.intent_detected}')>"
