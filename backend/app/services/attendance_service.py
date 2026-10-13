from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import AttendanceRecord, TrainingCentre, ComplianceScore
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate

class AttendanceService:
    @staticmethod
    def get_records(
        db: Session,
        centre_id: Optional[int] = None,
        date: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[AttendanceRecord]:
        query = db.query(AttendanceRecord)
        if centre_id:
            query = query.filter(AttendanceRecord.centre_id == centre_id)
        if date:
            query = query.filter(AttendanceRecord.date == date)
        return query.order_by(AttendanceRecord.date.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_record_by_id(db: Session, record_id: int) -> Optional[AttendanceRecord]:
        return db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()

    @staticmethod
    def create_record(db: Session, obj_in: AttendanceCreate) -> AttendanceRecord:
        rec = AttendanceRecord(**obj_in.model_dump())
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec

    @staticmethod
    def update_record(db: Session, record_id: int, obj_in: AttendanceUpdate) -> Optional[AttendanceRecord]:
        rec = db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
        if not rec:
            return None
        for field, val in obj_in.model_dump(exclude_unset=True).items():
            setattr(rec, field, val)
        # revalidate constraint
        if rec.submitted_present > rec.registered_count:
            raise ValueError("submitted_present cannot exceed registered_count")
        db.commit()
        db.refresh(rec)
        return rec

    @staticmethod
    def delete_record(db: Session, record_id: int) -> bool:
        rec = db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
        if not rec:
            return False
        db.delete(rec)
        db.commit()
        return True

    @staticmethod
    def get_reconciliation(db: Session, centre_id: int) -> Optional[dict]:
        centre = db.query(TrainingCentre).filter(TrainingCentre.id == centre_id).first()
        if not centre:
            return None

        latest_att = (
            db.query(AttendanceRecord)
            .filter(AttendanceRecord.centre_id == centre_id)
            .order_by(AttendanceRecord.date.desc())
            .first()
        )

        latest_comp = (
            db.query(ComplianceScore)
            .filter(ComplianceScore.centre_id == centre_id)
            .order_by(ComplianceScore.timestamp.desc())
            .first()
        )

        reg = latest_att.registered_count if latest_att else centre.capacity
        sub = latest_att.submitted_present if latest_att else 0
        est = latest_comp.estimated_physical_presence if latest_comp and latest_comp.estimated_physical_presence is not None else sub

        # discrepancy = submitted - estimated (only when positive / overreported)
        disc = max(0, sub - est)
        disc_pct = round((disc / sub * 100.0), 2) if sub > 0 else 0.0

        status = "NORMAL"
        if disc_pct > 20.0:
            status = "HIGH_DISCREPANCY"
        elif disc_pct > 10.0:
            status = "REVIEW"

        return {
            "centre_id": centre.id,
            "centre_code": centre.centre_code,
            "date": latest_att.date if latest_att else "N/A",
            "session": latest_att.session if latest_att else "Morning",
            "registered_count": reg,
            "submitted_present": sub,
            "estimated_physical_presence": est,
            "attendance_discrepancy": disc,
            "discrepancy_percentage": disc_pct,
            "status": status,
            "confidence": 0.92,
            "observation_window_minutes": 15
        }
