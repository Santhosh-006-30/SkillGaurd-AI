from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.database.models import RiskLevel

class ComplianceScoreBase(BaseModel):
    centre_id: int
    attendance_score: float = Field(default=100.0, ge=0.0, le=100.0)
    infrastructure_score: float = Field(default=100.0, ge=0.0, le=100.0)
    activity_score: float = Field(default=100.0, ge=0.0, le=100.0)
    data_consistency_score: float = Field(default=100.0, ge=0.0, le=100.0)
    overall_score: float = Field(default=100.0, ge=0.0, le=100.0)
    risk_level: RiskLevel = Field(default=RiskLevel.LOW)
    estimated_physical_presence: Optional[int] = None
    submitted_attendance: Optional[int] = None
    attendance_discrepancy: Optional[int] = None
    attendance_discrepancy_percentage: Optional[float] = None
    infrastructure_compliance_percentage: Optional[float] = None

class ComplianceScoreCreate(ComplianceScoreBase):
    pass

class ComplianceScoreResponse(ComplianceScoreBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
