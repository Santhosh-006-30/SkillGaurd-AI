from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.database.models import AttendanceSource

class AttendanceBase(BaseModel):
    centre_id: int
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD")
    session: str = Field(default="Morning", max_length=50)
    registered_count: int = Field(..., ge=0)
    submitted_present: int = Field(..., ge=0)
    source: AttendanceSource = Field(default=AttendanceSource.CENTRE_SUBMITTED)

    @model_validator(mode="after")
    def validate_counts(self):
        if self.submitted_present > self.registered_count:
            raise ValueError("submitted_present cannot exceed registered_count")
        return self

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    session: Optional[str] = None
    registered_count: Optional[int] = Field(None, ge=0)
    submitted_present: Optional[int] = Field(None, ge=0)
    source: Optional[AttendanceSource] = None

class AttendanceResponse(AttendanceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AttendanceReconciliationResponse(BaseModel):
    centre_id: int
    centre_code: str
    date: str
    session: str
    registered_count: int
    submitted_present: int
    estimated_physical_presence: int
    attendance_discrepancy: int
    discrepancy_percentage: float
    status: str  # NORMAL, REVIEW, HIGH_DISCREPANCY
    confidence: float
    observation_window_minutes: int
