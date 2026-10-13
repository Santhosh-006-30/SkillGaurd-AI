from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class OverviewAnalyticsResponse(BaseModel):
    total_centres: int
    active_cameras: int
    total_cameras: int
    open_alerts: int
    high_risk_centres: int
    average_compliance: float
    total_attendance_discrepancies: int
    total_infrastructure_shortages: int
    offline_cameras: int

class RiskDistributionItem(BaseModel):
    name: str  # LOW, MEDIUM, HIGH, CRITICAL
    count: int
    percentage: float

class ComplianceTrendPoint(BaseModel):
    date: str
    attendance_score: float
    infrastructure_score: float
    overall_score: float

class AlertTrendPoint(BaseModel):
    date: str
    high_count: int
    medium_count: int
    low_count: int
    critical_count: int

class CentreRankingItem(BaseModel):
    centre_code: str
    name: str
    district: str
    overall_score: float
    risk_level: str
    open_alerts: int
