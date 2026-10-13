from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import Camera, CameraStatus
from app.schemas.cameras import CameraCreate, CameraUpdate

class CameraService:
    @staticmethod
    def get_cameras(
        db: Session,
        centre_id: Optional[int] = None,
        status: Optional[CameraStatus] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Camera]:
        query = db.query(Camera)
        if centre_id:
            query = query.filter(Camera.centre_id == centre_id)
        if status:
            query = query.filter(Camera.status == status)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_camera_by_id(db: Session, camera_id: int) -> Optional[Camera]:
        return db.query(Camera).filter(Camera.id == camera_id).first()

    @staticmethod
    def create_camera(db: Session, obj_in: CameraCreate) -> Camera:
        cam = Camera(**obj_in.model_dump())
        db.add(cam)
        db.commit()
        db.refresh(cam)
        return cam

    @staticmethod
    def update_camera(db: Session, camera_id: int, obj_in: CameraUpdate) -> Optional[Camera]:
        cam = db.query(Camera).filter(Camera.id == camera_id).first()
        if not cam:
            return None
        for field, val in obj_in.model_dump(exclude_unset=True).items():
            setattr(cam, field, val)
        db.commit()
        db.refresh(cam)
        return cam

    @staticmethod
    def delete_camera(db: Session, camera_id: int) -> bool:
        cam = db.query(Camera).filter(Camera.id == camera_id).first()
        if not cam:
            return False
        db.delete(cam)
        db.commit()
        return True
