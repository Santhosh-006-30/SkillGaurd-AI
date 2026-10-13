from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User, UserRole, EventType
from app.core.security import get_current_user, require_roles
from app.services.detection_service import DetectionService
from app.schemas.detections import DetectionEventCreate, DetectionEventResponse

router = APIRouter(prefix="", tags=["Detections"])

@router.get("/detections", response_model=dict)
def list_detections(
    centre_id: Optional[int] = Query(None),
    camera_id: Optional[int] = Query(None),
    event_type: Optional[EventType] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    events = DetectionService.get_events(
        db, centre_id=centre_id, camera_id=camera_id, event_type=event_type, skip=skip, limit=limit
    )
    return {
        "success": True,
        "data": [DetectionEventResponse.model_validate(e).model_dump() for e in events]
    }

@router.get("/detections/{event_id}", response_model=dict)
def get_detection(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = DetectionService.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detection event with ID {event_id} not found"
        )
    return {
        "success": True,
        "data": DetectionEventResponse.model_validate(event).model_dump()
    }

@router.get("/centres/{centre_id}/detections", response_model=dict)
def get_centre_detections(
    centre_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    events = DetectionService.get_events(db, centre_id=centre_id, skip=skip, limit=limit)
    return {
        "success": True,
        "data": [DetectionEventResponse.model_validate(e).model_dump() for e in events]
    }
