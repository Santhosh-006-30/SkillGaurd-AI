import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "SkillGuard AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = Field(
        default=f"sqlite:///{BASE_DIR}/skillguard.db",
        description="SQLAlchemy Database URL"
    )
    
    # Security & Auth
    JWT_SECRET: str = "skillguard_super_secret_jwt_key_sih26245_dev_mode"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 1440  # 24 hours in minutes
    
    # File Storage Paths
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    EVIDENCE_DIR: str = str(BASE_DIR / "evidence")
    MODEL_PATH: str = str(BASE_DIR.parent / "ai_models")
    MAX_UPLOAD_SIZE: int = 200 * 1024 * 1024  # 200 MB
    
    # AI Engine Thresholds & Parameters
    PERSON_CONFIDENCE: float = 0.50
    EQUIPMENT_CONFIDENCE: float = 0.40
    FRAME_SKIP: int = 3
    OBSERVATION_WINDOW: int = 300  # 5 minutes in seconds
    
    # Bandwidth & Networking Modes
    LOW_BANDWIDTH_MODE: bool = False
    OFFLINE_BUFFER_LIMIT: int = 5000

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )

settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.EVIDENCE_DIR, exist_ok=True)
