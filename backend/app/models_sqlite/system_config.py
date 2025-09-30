from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
from app.database_sqlite import Base


class SystemConfig(Base):
    __tablename__ = "system_config"
    
    config_key = Column(String(100), primary_key=True)
    config_value = Column(Text)
    updated_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<SystemConfig(key='{self.config_key}', value='{self.config_value}')>"
