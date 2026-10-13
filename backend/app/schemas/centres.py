from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.database.models import CentreStatus

class TrainingCentreBase(BaseModel):
    centre_code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=3, max_length=200)
    state: str = Field(..., max_length=100)
    district: str = Field(..., max_length=100)
    address: Optional[str] = Field(None, max_length=300)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    capacity: int = Field(default=50, ge=1)
    status: CentreStatus = Field(default=CentreStatus.ACTIVE)

class TrainingCentreCreate(TrainingCentreBase):
    pass

class TrainingCentreUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    state: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    capacity: Optional[int] = Field(None, ge=1)
    status: Optional[CentreStatus] = None

class TrainingCentreResponse(TrainingCentreBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CentreSummaryResponse(BaseModel):
    id: int
    centre_code: str
    name: str
    district: str
    state: str
    capacity: int
    status: str
    camera_count: int
    active_cameras: int
    latest_attendance_submitted: Optional[int] = None
    latest_estimated_presence: Optional[int] = None
    latest_attendance_discrepancy: Optional[int] = None
    overall_compliance_score: Optional[float] = None
    risk_level: Optional[str] = "LOW"
    open_alerts_count: int = 0
    inventory_items_count: int = 0

    model_config = ConfigDict(from_attributes=True)
