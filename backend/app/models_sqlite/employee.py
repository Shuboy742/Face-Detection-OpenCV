from sqlalchemy import Column, String, Date, Boolean, DateTime, Text, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database_sqlite import Base
import uuid


class Employee(Base):
    __tablename__ = "employees"
    
    employee_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    position = Column(String(100))
    department = Column(String(100))
    date_of_birth = Column(Date)
    joining_date = Column(Date, nullable=False, server_default=func.current_date())
    phone_number = Column(String(20))
    employee_number = Column(Integer, unique=True)  # For employee ID like 416, 422
    
    # Face data storage (flexible for both approaches)
    face_data = Column(Text)  # Store face_token or embedding as text
    face_data_type = Column(String(20))  # 'face_token' or 'embedding'
    
    # Profile image
    profile_image_url = Column(String(500))
    
    # Registration metadata
    is_active = Column(Boolean, default=True)
    is_self_registered = Column(Boolean, default=False)
    registration_date = Column(DateTime, server_default=func.now())
    last_seen = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    face_encodings = relationship("FaceEncoding", back_populates="employee", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Employee(name='{self.name}', email='{self.email}', employee_number='{self.employee_number}')>"
