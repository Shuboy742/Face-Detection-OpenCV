from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.sql import func
from app.database_sqlite import Base
import uuid


class APIUsageLog(Base):
    __tablename__ = "api_usage_log"
    
    usage_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    api_name = Column(String(50), nullable=False)
    endpoint = Column(String(100))
    request_count = Column(Integer, default=1)
    cost_estimate = Column(Float)  # Cost in USD
    timestamp = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<APIUsageLog(api='{self.api_name}', endpoint='{self.endpoint}', cost={self.cost_estimate})>"
