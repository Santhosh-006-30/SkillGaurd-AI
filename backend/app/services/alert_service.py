from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import Alert, AlertSeverity, AlertStatus, AlertType
from app.schemas.alerts import AlertCreate, AlertStatusUpdate

class AlertService:
    @staticmethod
    def get_alerts(
        db: Session,
        centre_id: Optional[int] = None,
        severity: Optional[AlertSeverity] = None,
        status: Optional[AlertStatus] = None,
        alert_type: Optional[AlertType] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Alert]:
        query = db.query(Alert)
        if centre_id:
            query = query.filter(Alert.centre_id == centre_id)
        if severity:
            query = query.filter(Alert.severity == severity)
        if status:
            query = query.filter(Alert.status == status)
        if alert_type:
            query = query.filter(Alert.alert_type == alert_type)
        return query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_alert_by_id(db: Session, alert_id: int) -> Optional[Alert]:
        return db.query(Alert).filter(Alert.id == alert_id).first()

    @staticmethod
    def create_alert(db: Session, obj_in: AlertCreate) -> Alert:
        alert = Alert(**obj_in.model_dump())
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    @staticmethod
    def update_status(db: Session, alert_id: int, status_update: AlertStatusUpdate) -> Optional[Alert]:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        
        alert.status = status_update.status
        now = datetime.now(timezone.utc)
        if status_update.status == AlertStatus.ACKNOWLEDGED and not alert.acknowledged_at:
            alert.acknowledged_at = now
        elif status_update.status in [AlertStatus.RESOLVED, AlertStatus.FALSE_POSITIVE] and not alert.resolved_at:
            alert.resolved_at = now

        db.commit()
        db.refresh(alert)
        return alert
