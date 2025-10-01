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
    
    # Enhanced registration fields
    person_type: Optional[str] = "employee"
    special_notes: Optional[str] = None
    visit_purpose: Optional[str] = None
    expected_duration: Optional[str] = None
    host_employee_id: Optional[str] = None
    access_level: Optional[str] = "standard"
    
    # Additional metadata
    is_vip: Optional[bool] = False
    requires_escort: Optional[bool] = False
    badge_required: Optional[bool] = True


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
    
    # Enhanced registration fields
    person_type: Optional[str] = None
    special_notes: Optional[str] = None
    visit_purpose: Optional[str] = None
    expected_duration: Optional[str] = None
    host_employee_id: Optional[str] = None
    access_level: Optional[str] = None
    
    # Additional metadata
    is_vip: Optional[bool] = None
    requires_escort: Optional[bool] = None
    badge_required: Optional[bool] = None


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
