from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.database.models import CameraSourceType, CameraStatus

class CameraBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    source_type: CameraSourceType = Field(default=CameraSourceType.SIMULATION)
    source_url: Optional[str] = Field(None, max_length=500)
    zone: str = Field(default="Classroom A", max_length=100)
    resolution: str = Field(default="1080p", max_length=50)
    fps: int = Field(default=15, ge=1, le=60)
    status: CameraStatus = Field(default=CameraStatus.ONLINE)

class CameraCreate(CameraBase):
    centre_id: int

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    source_type: Optional[CameraSourceType] = None
    source_url: Optional[str] = None
    zone: Optional[str] = None
    resolution: Optional[str] = None
    fps: Optional[int] = None
    status: Optional[CameraStatus] = None

class CameraResponse(CameraBase):
    id: int
    centre_id: int
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
