from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User, UserRole, AlertSeverity, AlertStatus, AlertType
from app.core.security import get_current_user, require_roles
from app.services.alert_service import AlertService
from app.schemas.alerts import AlertCreate, AlertStatusUpdate, AlertResponse

router = APIRouter(prefix="", tags=["Alerts"])

@router.get("/alerts", response_model=dict)
def list_alerts(
    centre_id: Optional[int] = Query(None),
    severity: Optional[AlertSeverity] = Query(None),
    status_filter: Optional[AlertStatus] = Query(None, alias="status"),
    alert_type: Optional[AlertType] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alerts = AlertService.get_alerts(
        db, centre_id=centre_id, severity=severity, status=status_filter, alert_type=alert_type, skip=skip, limit=limit
    )
    return {
        "success": True,
        "data": [AlertResponse.model_validate(a).model_dump() for a in alerts]
    }

@router.get("/alerts/{alert_id}", response_model=dict)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = AlertService.get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    return {
        "success": True,
        "data": AlertResponse.model_validate(alert).model_dump()
    }

@router.get("/centres/{centre_id}/alerts", response_model=dict)
def get_centre_alerts(
    centre_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alerts = AlertService.get_alerts(db, centre_id=centre_id, skip=skip, limit=limit)
    return {
        "success": True,
        "data": [AlertResponse.model_validate(a).model_dump() for a in alerts]
    }

@router.put("/alerts/{alert_id}/status", response_model=dict)
def update_alert_status(
    alert_id: int,
    status_update: AlertStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.INSPECTOR, UserRole.MONITOR))
):
    updated = AlertService.update_status(db, alert_id, status_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    return {
        "success": True,
        "data": AlertResponse.model_validate(updated).model_dump()
    }
