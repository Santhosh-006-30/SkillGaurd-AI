from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import TrainingCentre, Camera, AttendanceRecord, ComplianceScore, Alert, InventoryItem, AlertStatus, CameraStatus
from app.schemas.centres import TrainingCentreCreate, TrainingCentreUpdate

class CentreService:
    @staticmethod
    def get_centres(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        district: Optional[str] = None,
        search: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[TrainingCentre]:
        query = db.query(TrainingCentre)
        if district:
            query = query.filter(TrainingCentre.district == district)
        if status:
            query = query.filter(TrainingCentre.status == status)
        if search:
            search_fmt = f"%{search}%"
            query = query.filter(
                (TrainingCentre.name.ilike(search_fmt)) |
                (TrainingCentre.centre_code.ilike(search_fmt)) |
                (TrainingCentre.district.ilike(search_fmt))
            )
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_centre_by_id(db: Session, centre_id: int) -> Optional[TrainingCentre]:
        return db.query(TrainingCentre).filter(TrainingCentre.id == centre_id).first()

    @staticmethod
    def get_centre_by_code(db: Session, centre_code: str) -> Optional[TrainingCentre]:
        return db.query(TrainingCentre).filter(TrainingCentre.centre_code == centre_code).first()

    @staticmethod
    def create_centre(db: Session, obj_in: TrainingCentreCreate) -> TrainingCentre:
        centre = TrainingCentre(**obj_in.model_dump())
        db.add(centre)
        db.commit()
        db.refresh(centre)
        return centre

    @staticmethod
    def update_centre(db: Session, centre_id: int, obj_in: TrainingCentreUpdate) -> Optional[TrainingCentre]:
        centre = db.query(TrainingCentre).filter(TrainingCentre.id == centre_id).first()
        if not centre:
            return None
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(centre, field, value)
        db.commit()
        db.refresh(centre)
        return centre

    @staticmethod
    def delete_centre(db: Session, centre_id: int) -> bool:
        centre = db.query(TrainingCentre).filter(TrainingCentre.id == centre_id).first()
        if not centre:
            return False
        db.delete(centre)
        db.commit()
        return True

    @staticmethod
    def get_centre_summary(db: Session, centre_id: int) -> Optional[dict]:
        centre = db.query(TrainingCentre).filter(TrainingCentre.id == centre_id).first()
        if not centre:
            return None
        
        total_cams = len(centre.cameras)
        active_cams = sum(1 for c in centre.cameras if c.status == CameraStatus.ONLINE)
        
        # Latest attendance
        latest_att = (
            db.query(AttendanceRecord)
            .filter(AttendanceRecord.centre_id == centre_id)
            .order_by(AttendanceRecord.date.desc())
            .first()
        )
        
        # Latest compliance
        latest_comp = (
            db.query(ComplianceScore)
            .filter(ComplianceScore.centre_id == centre_id)
            .order_by(ComplianceScore.timestamp.desc())
            .first()
        )

        open_alerts = (
            db.query(Alert)
            .filter(Alert.centre_id == centre_id, Alert.status == AlertStatus.OPEN)
            .count()
        )

        inventory_count = (
            db.query(InventoryItem)
            .filter(InventoryItem.centre_id == centre_id)
            .count()
        )

        return {
            "id": centre.id,
            "centre_code": centre.centre_code,
            "name": centre.name,
            "district": centre.district,
            "state": centre.state,
            "capacity": centre.capacity,
            "status": centre.status.value if hasattr(centre.status, "value") else str(centre.status),
            "camera_count": total_cams,
            "active_cameras": active_cams,
            "latest_attendance_submitted": latest_att.submitted_present if latest_att else None,
            "latest_estimated_presence": latest_comp.estimated_physical_presence if latest_comp else None,
            "latest_attendance_discrepancy": latest_comp.attendance_discrepancy if latest_comp else None,
            "overall_compliance_score": latest_comp.overall_score if latest_comp else None,
            "risk_level": latest_comp.risk_level.value if latest_comp and hasattr(latest_comp.risk_level, "value") else "LOW",
            "open_alerts_count": open_alerts,
            "inventory_items_count": inventory_count,
        }
