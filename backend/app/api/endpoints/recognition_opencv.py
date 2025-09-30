from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import base64
import requests
import logging

from app.database_sqlite import get_db
from app.services.opencv_face_service import OpenCVFaceDetectionService
from app.services.employee_service_sqlite import EmployeeService
from app.models_sqlite import Employee
from app.schemas.employee import EmployeeCreate, EmployeeResponse
from app.schemas.recognition import FaceRecognitionRequest, FaceRecognitionResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Using imported schemas from app.schemas

@router.post("/scan-face", response_model=FaceRecognitionResponse)
async def scan_face(
    request: FaceRecognitionRequest,
    db: Session = Depends(get_db)
):
    """
    Scan face for recognition using OpenCV Haar Cascade detection
    """
    try:
        face_service = OpenCVFaceDetectionService()
        employee_service = EmployeeService(db)
        
        image_data = None
        if request.image_base64:
            image_data = base64.b64decode(request.image_base64)
        elif request.image_url:
            response = requests.get(request.image_url)
            response.raise_for_status()
            image_data = response.content
        
        if not image_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image data (base64 or URL) is required"
            )
        
        result = await face_service.identify_or_register(image_data)
        
        if result['status'] == 'recognized':
            # Get employee data from database
            employee_id = result.get('employee_id')
            employee = employee_service.get_employee_by_id(employee_id)
            
            if employee:
                # Convert SQLAlchemy object to dictionary
                employee_dict = {
                    'employee_id': str(employee.employee_id),
                    'name': employee.name,
                    'email': employee.email,
                    'employee_number': employee.employee_number,
                    'position': employee.position,
                    'department': employee.department,
                    'date_of_birth': str(employee.date_of_birth) if employee.date_of_birth else None,
                    'joining_date': str(employee.joining_date) if employee.joining_date else None,
                    'phone_number': employee.phone_number,
                    'profile_image_url': employee.profile_image_url,
                    'is_active': employee.is_active,
                    'is_self_registered': employee.is_self_registered,
                    'registration_date': str(employee.registration_date) if employee.registration_date else None,
                    'last_seen': str(employee.last_seen) if employee.last_seen else None
                }
                
                return FaceRecognitionResponse(
                    status='recognized',
                    employee=employee_dict,
                    confidence=result.get('confidence', 0),
                    temp_id=result.get('temp_id'),
                    message=f"Welcome back, {employee.name}! (OpenCV Detection)",
                    needs_registration=False
                )
            else:
                # Employee not found in database but face recognized
                return FaceRecognitionResponse(
                    status='new_employee',
                    employee=None,
                    confidence=None,
                    temp_id=result.get('temp_id'),
                    message="Face recognized but employee not found in database. Please register.",
                    needs_registration=True
                )
        
        elif result['status'] == 'new_employee':
            return FaceRecognitionResponse(
                status='new_employee',
                employee=None,
                confidence=None,
                temp_id=result.get('temp_id'),
                message="New face detected. Please complete registration. (OpenCV Detection)",
                needs_registration=True
            )
        
        elif result['status'] == 'detection_failed':
            return FaceRecognitionResponse(
                status='detection_failed',
                employee=None,
                confidence=None,
                temp_id=None,
                message=result.get('message', 'Face detection failed'),
                needs_registration=False
            )
        
        else:
            # Error case
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('message', 'Face recognition failed')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Face scanning error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/register")
async def register_employee(
    name: str = Form(...),
    email: str = Form(...),
    employee_number: str = Form(...),  # Accept as string first
    position: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    date_of_birth: Optional[str] = Form(None),
    joining_date: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    profile_image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Register new employee with face data using OpenCV detection
    """
    try:
        face_service = OpenCVFaceDetectionService()
        employee_service = EmployeeService(db)
        
        # Convert employee_number to int
        try:
            employee_number_int = int(employee_number)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid employee number: {employee_number}. Must be a valid integer."
            )
        
        # Check if employee already exists
        existing_employee = employee_service.get_employee_by_number(employee_number_int)
        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee with number {employee_number} already exists"
            )
        
        # Read image data
        image_data = await profile_image.read()
        
        # Get face token from image using OpenCV + Face++ API
        face_token = await face_service.get_face_token_from_facepp(image_data)
        if not face_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in the uploaded image. Please upload a clear face photo."
            )
        
        # Create employee data
        employee_data = EmployeeCreate(
            name=name,
            email=email,
            employee_number=employee_number_int,
            position=position,
            department=department,
            date_of_birth=date_of_birth,
            joining_date=joining_date,
            phone_number=phone_number
        )
        
        # Create employee in database
        employee = employee_service.create_employee(employee_data)
        
        # Add face to FaceSet
        face_added = await face_service.add_face_to_faceset(face_token, str(employee.employee_id))
        
        if face_added:
            # Update employee with face data
            employee.face_data = face_token
            employee.face_data_type = 'face_token'
            db.commit()
            
            logger.info(f"Successfully registered employee: {employee.name} with OpenCV face detection")
            
            # Return the employee data in the expected format for the frontend
            employee_dict = {
                'employee_id': str(employee.employee_id),
                'name': employee.name,
                'email': employee.email,
                'employee_number': employee.employee_number,
                'position': employee.position,
                'department': employee.department,
                'date_of_birth': str(employee.date_of_birth) if employee.date_of_birth else None,
                'joining_date': str(employee.joining_date) if employee.joining_date else None,
                'phone_number': employee.phone_number,
                'profile_image_url': employee.profile_image_url,
                'is_active': employee.is_active,
                'is_self_registered': employee.is_self_registered,
                'registration_date': str(employee.registration_date) if employee.registration_date else None,
                'last_seen': str(employee.last_seen) if employee.last_seen else None
            }
            
            # Return the response in the format expected by the frontend
            return {
                'status': 'success',
                'employee': employee_dict,
                'message': f'Employee {employee.name} registered successfully with OpenCV face detection!'
            }
        else:
            # Rollback employee creation if face linking failed
            db.delete(employee)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to link face data to employee"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Employee registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )
