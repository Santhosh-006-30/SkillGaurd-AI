from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User, UserRole
from app.core.security import get_current_user, require_roles
from app.services.attendance_service import AttendanceService
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
    AttendanceReconciliationResponse
)

router = APIRouter(prefix="", tags=["Attendance"])

@router.get("/attendance", response_model=dict)
def list_attendance(
    centre_id: Optional[int] = Query(None),
    date: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    records = AttendanceService.get_records(
        db, centre_id=centre_id, date=date, skip=skip, limit=limit
    )
    return {
        "success": True,
        "data": [AttendanceResponse.model_validate(r).model_dump() for r in records]
    }

@router.get("/centres/{centre_id}/attendance", response_model=dict)
def get_centre_attendance(
    centre_id: int,
    date: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    records = AttendanceService.get_records(
        db, centre_id=centre_id, date=date, skip=skip, limit=limit
    )
    return {
        "success": True,
        "data": [AttendanceResponse.model_validate(r).model_dump() for r in records]
    }

@router.get("/centres/{centre_id}/attendance/reconciliation", response_model=dict)
def get_centre_attendance_reconciliation(
    centre_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reconciliation = AttendanceService.get_reconciliation(db, centre_id)
    if not reconciliation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training centre with ID {centre_id} not found"
        )
    return {
        "success": True,
        "data": reconciliation
    }

@router.post("/attendance", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_attendance_record(
    att_in: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CENTRE_OPERATOR))
):
    try:
        rec = AttendanceService.create_record(db, att_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return {
        "success": True,
        "data": AttendanceResponse.model_validate(rec).model_dump()
    }

@router.put("/attendance/{record_id}", response_model=dict)
def update_attendance_record(
    record_id: int,
    att_in: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CENTRE_OPERATOR))
):
    try:
        rec = AttendanceService.update_record(db, record_id, att_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with ID {record_id} not found"
        )
    return {
        "success": True,
        "data": AttendanceResponse.model_validate(rec).model_dump()
    }

@router.delete("/attendance/{record_id}", response_model=dict)
def delete_attendance_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    deleted = AttendanceService.delete_record(db, record_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with ID {record_id} not found"
        )
    return {
        "success": True,
        "data": {"message": f"Attendance record {record_id} deleted successfully"}
    }
