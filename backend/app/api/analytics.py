from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User
from app.core.security import get_current_user
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/overview", response_model=dict)
def get_analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    overview = AnalyticsService.get_overview(db)
    return {
        "success": True,
        "data": overview
    }

@router.get("/risk-distribution", response_model=dict)
def get_risk_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dist = AnalyticsService.get_risk_distribution(db)
    return {
        "success": True,
        "data": dist
    }

@router.get("/compliance-trend", response_model=dict)
def get_compliance_trend(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    trend = AnalyticsService.get_compliance_trend(db)
    return {
        "success": True,
        "data": trend
    }

@router.get("/alerts-trend", response_model=dict)
def get_alerts_trend(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    trend = AnalyticsService.get_alerts_trend(db)
    return {
        "success": True,
        "data": trend
    }

@router.get("/rankings", response_model=dict)
def get_centre_rankings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rankings = AnalyticsService.get_centre_ranking(db)
    return {
        "success": True,
        "data": rankings
    }
