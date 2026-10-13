from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User, RiskLevel
from app.core.security import get_current_user
from app.services.compliance_service import ComplianceService
from app.services.analytics_service import AnalyticsService
from app.schemas.compliance import ComplianceScoreResponse

router = APIRouter(prefix="", tags=["Compliance"])

@router.get("/compliance", response_model=dict)
def list_compliance_scores(
    centre_id: Optional[int] = Query(None),
    risk_level: Optional[RiskLevel] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scores = ComplianceService.get_scores(
        db, centre_id=centre_id, risk_level=risk_level, skip=skip, limit=limit
    )
    return {
        "success": True,
        "data": [ComplianceScoreResponse.model_validate(s).model_dump() for s in scores]
    }

@router.get("/centres/{centre_id}/compliance", response_model=dict)
def get_centre_compliance(
    centre_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    latest = ComplianceService.get_latest_centre_score(db, centre_id)
    if not latest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No compliance scores recorded for centre {centre_id}"
        )
    return {
        "success": True,
        "data": ComplianceScoreResponse.model_validate(latest).model_dump()
    }

@router.get("/analytics/compliance", response_model=dict)
def get_compliance_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    trend = AnalyticsService.get_compliance_trend(db)
    overview = AnalyticsService.get_overview(db)
    return {
        "success": True,
        "data": {
            "average_compliance": overview["average_compliance"],
            "trend": trend
        }
    }
