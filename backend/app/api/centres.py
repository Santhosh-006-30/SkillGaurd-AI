from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User, UserRole
from app.core.security import get_current_user, require_roles
from app.services.centre_service import CentreService
from app.schemas.centres import (
    TrainingCentreCreate,
    TrainingCentreUpdate,
    TrainingCentreResponse,
    CentreSummaryResponse
)

router = APIRouter(prefix="/centres", tags=["Training Centres"])

@router.get("", response_model=dict)
def list_centres(
    district: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    centres = CentreService.get_centres(
        db, skip=skip, limit=limit, district=district, search=search, status=status_filter
    )
    return {
        "success": True,
        "data": [TrainingCentreResponse.model_validate(c).model_dump() for c in centres]
    }

@router.get("/{centre_id}", response_model=dict)
def get_centre(
    centre_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    centre = CentreService.get_centre_by_id(db, centre_id)
    if not centre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training centre with ID {centre_id} not found"
        )
    return {
        "success": True,
        "data": TrainingCentreResponse.model_validate(centre).model_dump()
    }

@router.get("/{centre_id}/summary", response_model=dict)
def get_centre_summary(
    centre_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    summary = CentreService.get_centre_summary(db, centre_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training centre with ID {centre_id} not found"
        )
    return {
        "success": True,
        "data": summary
    }

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_centre(
    centre_in: TrainingCentreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    existing = CentreService.get_centre_by_code(db, centre_in.centre_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Centre with code {centre_in.centre_code} already exists"
        )
    centre = CentreService.create_centre(db, centre_in)
    return {
        "success": True,
        "data": TrainingCentreResponse.model_validate(centre).model_dump()
    }

@router.put("/{centre_id}", response_model=dict)
def update_centre(
    centre_id: int,
    centre_in: TrainingCentreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.INSPECTOR))
):
    centre = CentreService.update_centre(db, centre_id, centre_in)
    if not centre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training centre with ID {centre_id} not found"
        )
    return {
        "success": True,
        "data": TrainingCentreResponse.model_validate(centre).model_dump()
    }

@router.delete("/{centre_id}", response_model=dict)
def delete_centre(
    centre_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    deleted = CentreService.delete_centre(db, centre_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training centre with ID {centre_id} not found"
        )
    return {
        "success": True,
        "data": {"message": f"Training centre {centre_id} deleted successfully"}
    }
