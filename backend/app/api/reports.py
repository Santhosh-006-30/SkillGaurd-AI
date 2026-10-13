from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User
from app.core.security import get_current_user
from app.services.report_generator import generate_centre_dossier_data, generate_pdf_report

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/centre/{centre_id}", response_model=dict)
def get_centre_reports(
    centre_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dossier = generate_centre_dossier_data(db, centre_id)
    if not dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training centre with ID {centre_id} not found"
        )
    return {
        "success": True,
        "data": {
            "centre_id": centre_id,
            "dossier_id": dossier["dossier_id"],
            "generated_at": dossier["generated_at"],
            "integrity_hash": dossier["integrity_hash_sha256"],
            "reports": [
                {
                    "id": f"REP-{centre_id}-PDF",
                    "title": "Comprehensive Compliance Audit Dossier (PDF)",
                    "format": "PDF",
                    "download_url": f"/api/reports/centre/{centre_id}/pdf",
                    "status": "AVAILABLE"
                },
                {
                    "id": f"REP-{centre_id}-JSON",
                    "title": "Raw Compliance Audit Package (JSON)",
                    "format": "JSON",
                    "download_url": f"/api/reports/centre/{centre_id}/json",
                    "status": "AVAILABLE"
                }
            ]
        }
    }

@router.get("/centre/{centre_id}/json")
def get_centre_report_json(
    centre_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dossier = generate_centre_dossier_data(db, centre_id)
    if not dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training centre with ID {centre_id} not found"
        )
    return {
        "success": True,
        "data": dossier
    }

@router.get("/centre/{centre_id}/pdf")
def get_centre_report_pdf(
    centre_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dossier = generate_centre_dossier_data(db, centre_id)
    if not dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training centre with ID {centre_id} not found"
        )
    pdf_bytes = generate_pdf_report(dossier)
    filename = f"SkillGuard_Audit_TC_{dossier['centre']['code']}_{centre_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
