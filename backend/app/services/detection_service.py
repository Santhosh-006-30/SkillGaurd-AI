from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import DetectionEvent, ProcessingSession, EventType, ProcessingStatus
from app.schemas.detections import DetectionEventCreate

class DetectionService:
    @staticmethod
    def get_events(
        db: Session,
        centre_id: Optional[int] = None,
        camera_id: Optional[int] = None,
        event_type: Optional[EventType] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[DetectionEvent]:
        query = db.query(DetectionEvent)
        if centre_id:
            query = query.filter(DetectionEvent.centre_id == centre_id)
        if camera_id:
            query = query.filter(DetectionEvent.camera_id == camera_id)
        if event_type:
            query = query.filter(DetectionEvent.event_type == event_type)
        return query.order_by(DetectionEvent.timestamp.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_event_by_id(db: Session, event_id: int) -> Optional[DetectionEvent]:
        return db.query(DetectionEvent).filter(DetectionEvent.id == event_id).first()

    @staticmethod
    def create_event(db: Session, obj_in: DetectionEventCreate) -> DetectionEvent:
        evt = DetectionEvent(**obj_in.model_dump())
        db.add(evt)
        db.commit()
        db.refresh(evt)
        return evt

    @staticmethod
    def get_sessions(
        db: Session,
        centre_id: Optional[int] = None,
        status: Optional[ProcessingStatus] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ProcessingSession]:
        query = db.query(ProcessingSession)
        if centre_id:
            query = query.filter(ProcessingSession.centre_id == centre_id)
        if status:
            query = query.filter(ProcessingSession.status == status)
        return query.order_by(ProcessingSession.started_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_session_by_id(db: Session, session_id: int) -> Optional[ProcessingSession]:
        return db.query(ProcessingSession).filter(ProcessingSession.id == session_id).first()
