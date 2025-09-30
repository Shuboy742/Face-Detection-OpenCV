from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class GreetingResponse(BaseModel):
    """Response for greeting generation"""
    greeting_type: str  # 'daily', 'birthday', 'anniversary', 'first_day', etc.
    greeting_text: str
    audio_url: Optional[str] = None
    employee_name: str
    timestamp: datetime
