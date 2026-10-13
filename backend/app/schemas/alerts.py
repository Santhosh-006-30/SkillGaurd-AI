from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.database.models import AlertType, AlertSeverity, AlertStatus

class AlertBase(BaseModel):
    centre_id: int
    camera_id: Optional[int] = None
    alert_type: AlertType
    severity: AlertSeverity = Field(default=AlertSeverity.MEDIUM)
    title: str = Field(..., min_length=3, max_length=200)
    description: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    status: AlertStatus = Field(default=AlertStatus.OPEN)
    evidence_path: Optional[str] = None

class AlertCreate(AlertBase):
    pass

class AlertStatusUpdate(BaseModel):
    status: AlertStatus

class AlertResponse(AlertBase):
    id: int
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
