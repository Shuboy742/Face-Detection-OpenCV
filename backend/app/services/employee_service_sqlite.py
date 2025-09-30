from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime
import logging

from app.models_sqlite.employee import Employee
from app.models_sqlite.face_encoding import FaceEncoding
from app.schemas.employee import EmployeeCreate, EmployeeUpdate

logger = logging.getLogger(__name__)


class EmployeeService:
    """Service for employee management (SQLite version)"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_employee(self, employee_data: EmployeeCreate, face_token: str = None) -> Employee:
        """Create a new employee"""
        try:
            # Create employee record
            employee = Employee(
                name=employee_data.name,
                email=employee_data.email,
                position=employee_data.position,
                department=employee_data.department,
                date_of_birth=employee_data.date_of_birth,
                joining_date=employee_data.joining_date or datetime.now().date(),
                phone_number=employee_data.phone_number,
                employee_number=employee_data.employee_number,
                face_data=face_token if face_token else None,  # Store as string for SQLite
                face_data_type='face_token' if face_token else None,
                is_self_registered=True
            )
            
            self.db.add(employee)
            self.db.flush()  # Get the employee_id
            
            # Create face encoding record if face_token provided
            if face_token:
                face_encoding = FaceEncoding(
                    employee_id=employee.employee_id,
                    face_data=face_token,  # Store as string for SQLite
                    face_data_type='face_token',
                    is_primary=True
                )
                self.db.add(face_encoding)
            
            self.db.commit()
            self.db.refresh(employee)
            
            logger.info(f"Created employee: {employee.name} (ID: {employee.employee_id})")
            return employee
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating employee: {str(e)}")
            raise
    
    def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """Get employee by ID"""
        try:
            return self.db.query(Employee).filter(
                and_(Employee.employee_id == employee_id, Employee.is_active == True)
            ).first()
        except Exception as e:
            logger.error(f"Error getting employee by ID {employee_id}: {str(e)}")
            return None
    
    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email"""
        try:
            return self.db.query(Employee).filter(
                and_(Employee.email == email, Employee.is_active == True)
            ).first()
        except Exception as e:
            logger.error(f"Error getting employee by email {email}: {str(e)}")
            return None
    
    def get_employee_by_number(self, employee_number: int) -> Optional[Employee]:
        """Get employee by employee number"""
        try:
            return self.db.query(Employee).filter(
                and_(Employee.employee_number == employee_number, Employee.is_active == True)
            ).first()
        except Exception as e:
            logger.error(f"Error getting employee by number {employee_number}: {str(e)}")
            return None
    
    def get_employee_by_face_token(self, face_token: str) -> Optional[Employee]:
        """Get employee by face token"""
        try:
            # First find the face encoding
            face_encoding = self.db.query(FaceEncoding).filter(
                FaceEncoding.face_data == face_token,
                FaceEncoding.is_primary == True
            ).first()
            
            if face_encoding:
                # Then get the employee
                return self.db.query(Employee).filter(
                    and_(Employee.employee_id == face_encoding.employee_id, Employee.is_active == True)
                ).first()
            
            return None
        except Exception as e:
            logger.error(f"Error getting employee by face token: {str(e)}")
            return None
    
    def get_all_employees(self) -> List[Employee]:
        """Get all active employees"""
        try:
            return self.db.query(Employee).filter(Employee.is_active == True).all()
        except Exception as e:
            logger.error(f"Error getting all employees: {str(e)}")
            return []
    
    def update_employee(self, employee_id: str, employee_data: EmployeeUpdate) -> Optional[Employee]:
        """Update employee information"""
        try:
            employee = self.get_employee_by_id(employee_id)
            if not employee:
                return None
            
            # Update fields
            if employee_data.name is not None:
                employee.name = employee_data.name
            if employee_data.email is not None:
                employee.email = employee_data.email
            if employee_data.position is not None:
                employee.position = employee_data.position
            if employee_data.department is not None:
                employee.department = employee_data.department
            if employee_data.phone_number is not None:
                employee.phone_number = employee_data.phone_number
            
            employee.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(employee)
            
            logger.info(f"Updated employee: {employee.name}")
            return employee
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating employee: {str(e)}")
            raise
    
    def deactivate_employee(self, employee_id: str) -> bool:
        """Deactivate employee (soft delete)"""
        try:
            employee = self.get_employee_by_id(employee_id)
            if not employee:
                return False
            
            employee.is_active = False
            employee.updated_at = datetime.now()
            self.db.commit()
            
            logger.info(f"Deactivated employee: {employee.name}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating employee: {str(e)}")
            return False
    
    def update_last_seen(self, employee_id: str) -> bool:
        """Update employee's last seen timestamp"""
        try:
            employee = self.get_employee_by_id(employee_id)
            if not employee:
                return False
            
            employee.last_seen = datetime.now()
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating last seen for employee: {str(e)}")
            return False
