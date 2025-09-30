from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID


class FaceRecognitionRequest(BaseModel):
    """Request for face recognition"""
    image_base64: Optional[str] = None
    image_url: Optional[str] = None


class FaceRecognitionResponse(BaseModel):
    """Response from face recognition"""
    status: str  # 'recognized', 'new_employee', 'error'
    employee: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    temp_id: Optional[str] = None
    message: Optional[str] = None
    needs_registration: Optional[bool] = None


class EmployeeRegistrationRequest(BaseModel):
    """Request for new employee registration"""
    temp_id: str
    name: str
    email: str
    position: Optional[str] = None
    department: Optional[str] = None
    date_of_birth: Optional[str] = None
    joining_date: Optional[str] = None
    phone_number: Optional[str] = None
    employee_number: Optional[int] = None
    image_base64: Optional[str] = None
    image_url: Optional[str] = None


class EmployeeRegistrationResponse(BaseModel):
    """Response from employee registration"""
    status: str  # 'success', 'error'
    employee_id: Optional[UUID] = None
    message: Optional[str] = None
