from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.database.models import EventType, ProcessingSource, ProcessingStatus

class DetectionEventBase(BaseModel):
    centre_id: int
    camera_id: Optional[int] = None
    event_type: EventType
    object_type: Optional[str] = None
    count: int = Field(default=1, ge=0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    zone: Optional[str] = None
    metadata_json: Optional[str] = None
    evidence_path: Optional[str] = None

class DetectionEventCreate(DetectionEventBase):
    pass

class DetectionEventResponse(DetectionEventBase):
    id: int
    timestamp: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProcessingSessionResponse(BaseModel):
    id: int
    centre_id: int
    camera_id: Optional[int] = None
    source: ProcessingSource
    started_at: datetime
    ended_at: Optional[datetime] = None
    frames_processed: int
    processing_fps: float
    average_confidence: float
    status: ProcessingStatus
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
