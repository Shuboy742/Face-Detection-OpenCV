from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database (SQLite for easy setup)
    database_url: str = "sqlite:///./greeting_agent.db"
    
    # JWT
    secret_key: str = "your-super-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # System Configuration
    recognition_method: str = "api"  # 'api' or 'local'
    api_provider: str = "facepp"     # 'facepp', 'clarifai', 'kairos'
    
    # Face++ API Configuration
    facepp_api_key: str = "EPm2lFNs6RlwMRPdMscplSnSYhntBGFh"
    facepp_api_secret: str = "aK4DF89yikoceI2KQtmUrvgafraEOtbo"
    facepp_faceset_token: str = "6110df81aff5fd5d20e7d2571b743bac"
    
    # Voice Configuration
    tts_provider: str = "google"     # 'google', 'pyttsx3', 'gtts'
    stt_provider: str = "google"     # 'google', 'vosk'
    
    # File Storage
    upload_dir: str = "./app/uploads"
    temp_dir: str = "./app/temp"
    cache_dir: str = "./app/cache"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "development"
    debug: bool = True
    
    # CORS
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:19006", 
        "http://localhost:8080"
    ]
    
    # Cost Tracking
    track_api_costs: bool = True
    monthly_budget_alert: float = 50.0
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()

# Create necessary directories
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.temp_dir, exist_ok=True)
os.makedirs(settings.cache_dir, exist_ok=True)
