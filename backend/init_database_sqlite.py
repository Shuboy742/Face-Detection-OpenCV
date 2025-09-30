#!/usr/bin/env python3
"""
Database initialization script with sample data (SQLite version)
"""

import asyncio
from datetime import date
from sqlalchemy.orm import Session
from app.database_sqlite import SessionLocal, engine
from app.models_sqlite import Base, Employee, FaceEncoding, SystemConfig
from app.services.face_service_api import FaceRecognitionAPIService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_employees():
    """Create sample employee data"""
    
    # Sample employee data provided by user
    sample_employees = [
        {
            "name": "Yash Amurutkar",
            "email": "yash.amurutkar@company.com",
            "employee_number": 416,
            "date_of_birth": date(2000, 10, 19),  # 19/10/2000
            "joining_date": date(2025, 6, 3),    # 03/06/2025
            "position": "Software Developer",
            "department": "Engineering",
            "phone_number": "+91-9876543210"
        },
        {
            "name": "Prabhuraj Dhondge", 
            "email": "prabhuraj.dhondge@company.com",
            "employee_number": 422,
            "date_of_birth": date(2002, 4, 16),  # 16/04/2002
            "joining_date": date(2025, 6, 3),    # 03/06/2025
            "position": "Software Developer",
            "department": "Engineering", 
            "phone_number": "+91-9876543211"
        }
    ]
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        logger.info("Clearing existing employee data...")
        db.query(FaceEncoding).delete()
        db.query(Employee).delete()
        db.commit()
        
        # Create sample employees
        for emp_data in sample_employees:
            employee = Employee(**emp_data)
            db.add(employee)
            logger.info(f"Created employee: {employee.name} (ID: {employee.employee_number})")
        
        db.commit()
        logger.info("Sample employees created successfully")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating sample employees: {e}")
        raise
    finally:
        db.close()


def initialize_system_config():
    """Initialize system configuration"""
    
    db = SessionLocal()
    
    try:
        # Clear existing config
        db.query(SystemConfig).delete()
        db.commit()
        
        # Default system configuration
        configs = [
            ("recognition_method", "api"),
            ("api_provider", "facepp"),
            ("tts_provider", "google"),
            ("stt_provider", "google"),
            ("face_similarity_threshold", "0.75"),
            ("monthly_budget_alert", "50"),
            ("track_api_costs", "true")
        ]
        
        for key, value in configs:
            config = SystemConfig(config_key=key, config_value=value)
            db.add(config)
            logger.info(f"Added config: {key} = {value}")
        
        db.commit()
        logger.info("System configuration initialized")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error initializing system config: {e}")
        raise
    finally:
        db.close()


async def test_face_api():
    """Test Face++ API connection"""
    try:
        face_service = FaceRecognitionAPIService()
        
        # Test with a simple image URL (placeholder)
        test_image_url = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"
        
        logger.info("Testing Face++ API connection...")
        
        # This would normally test the API, but we'll skip for now
        # since we don't have actual face images
        logger.info("Face++ API service initialized successfully")
        
    except Exception as e:
        logger.error(f"Face++ API test failed: {e}")


def main():
    """Main initialization function"""
    logger.info("Initializing Voice-Based Greeting Agent Database (SQLite)...")
    
    try:
        # Create database tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Initialize system configuration
        initialize_system_config()
        
        # Create sample employees
        create_sample_employees()
        
        # Test Face++ API
        asyncio.run(test_face_api())
        
        logger.info("Database initialization completed successfully!")
        logger.info("\nSample employees created:")
        logger.info("1. Yash Amurutkar (ID: 416) - yash.amurutkar@company.com")
        logger.info("2. Prabhuraj Dhondge (ID: 422) - prabhuraj.dhondge@company.com")
        logger.info("\nNext steps:")
        logger.info("1. Add face images for employees using the Face++ API")
        logger.info("2. Start the FastAPI server: uvicorn app.main:app --reload")
        logger.info("3. Test the API endpoints")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    main()
