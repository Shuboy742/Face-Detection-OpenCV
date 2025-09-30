from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database_sqlite import Base
import uuid


class FaceEncoding(Base):
    __tablename__ = "face_encodings"
    
    encoding_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, ForeignKey('employees.employee_id'), nullable=False)
    face_data = Column(Text, nullable=False)  # face_token or embedding as text
    face_data_type = Column(String(20), nullable=False)  # 'face_token' or 'embedding'
    image_url = Column(String(500))
    encoding_quality = Column(Float)  # Quality score of the face encoding
    is_primary = Column(Boolean, default=False)  # Primary encoding for this employee
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationship
    employee = relationship("Employee", back_populates="face_encodings")
    
    def __repr__(self):
        return f"<FaceEncoding(employee_id='{self.employee_id}', type='{self.face_data_type}', primary={self.is_primary})>"
