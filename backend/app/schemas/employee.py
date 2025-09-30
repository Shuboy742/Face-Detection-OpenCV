from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    position: Optional[str] = None
    department: Optional[str] = None
    date_of_birth: Optional[date] = None
    joining_date: Optional[date] = None
    phone_number: Optional[str] = None
    employee_number: Optional[int] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    position: Optional[str] = None
    department: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None
    employee_number: Optional[int] = None


class EmployeeResponse(EmployeeBase):
    employee_id: UUID
    profile_image_url: Optional[str] = None
    is_active: bool
    is_self_registered: bool
    registration_date: datetime
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
