from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.database_sqlite import engine, SessionLocal
from app.models_sqlite import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Voice-Based Greeting Agent API (OpenCV)",
    description="Face recognition system using OpenCV Haar Cascade for accurate detection",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers
from app.api.endpoints import recognition_opencv

app.include_router(
    recognition_opencv.router,
    prefix="/api/v1/recognition",
    tags=["Face Recognition (OpenCV)"]
)

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        # Create all database tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        logger.info("Starting Voice-Based Greeting Agent API (OpenCV)...")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Voice-Based Greeting Agent API (OpenCV)...")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Voice-Based Greeting Agent API (OpenCV)",
        "version": "2.0.0",
        "detection_method": "OpenCV Haar Cascade",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-01-27T12:00:00Z",
        "database": "SQLite",
        "detection_method": "OpenCV Haar Cascade",
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
