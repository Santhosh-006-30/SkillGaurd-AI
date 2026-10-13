from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User, UserRole, CameraStatus
from app.core.security import get_current_user, require_roles
from app.services.camera_service import CameraService
from app.schemas.cameras import CameraCreate, CameraUpdate, CameraResponse

router = APIRouter(prefix="", tags=["Cameras"])

@router.get("/cameras", response_model=dict)
def list_cameras(
    centre_id: Optional[int] = Query(None),
    status_filter: Optional[CameraStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cameras = CameraService.get_cameras(
        db, centre_id=centre_id, status=status_filter, skip=skip, limit=limit
    )
    return {
        "success": True,
        "data": [CameraResponse.model_validate(c).model_dump() for c in cameras]
    }

@router.get("/cameras/{camera_id}", response_model=dict)
def get_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cam = CameraService.get_camera_by_id(db, camera_id)
    if not cam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with ID {camera_id} not found"
        )
    return {
        "success": True,
        "data": CameraResponse.model_validate(cam).model_dump()
    }

@router.get("/centres/{centre_id}/cameras", response_model=dict)
def get_centre_cameras(
    centre_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cameras = CameraService.get_cameras(db, centre_id=centre_id)
    return {
        "success": True,
        "data": [CameraResponse.model_validate(c).model_dump() for c in cameras]
    }

@router.post("/cameras", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_camera(
    camera_in: CameraCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CENTRE_OPERATOR))
):
    cam = CameraService.create_camera(db, camera_in)
    return {
        "success": True,
        "data": CameraResponse.model_validate(cam).model_dump()
    }

@router.put("/cameras/{camera_id}", response_model=dict)
def update_camera(
    camera_id: int,
    camera_in: CameraUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CENTRE_OPERATOR))
):
    cam = CameraService.update_camera(db, camera_id, camera_in)
    if not cam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with ID {camera_id} not found"
        )
    return {
        "success": True,
        "data": CameraResponse.model_validate(cam).model_dump()
    }

@router.delete("/cameras/{camera_id}", response_model=dict)
def delete_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    deleted = CameraService.delete_camera(db, camera_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with ID {camera_id} not found"
        )
    return {
        "success": True,
        "data": {"message": f"Camera {camera_id} deleted successfully"}
    }
