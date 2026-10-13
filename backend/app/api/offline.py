"""
Offline and Low-Bandwidth API Router — Phase 14
Provides endpoints for edge device queuing, synchronization, and adaptive sampling profiling.
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.core.security import get_current_user
from app.services.offline_sync import offline_sync_manager

router = APIRouter(prefix="/offline", tags=["Offline & Low-Bandwidth"])

class OfflineEnqueueRequest(BaseModel):
    centre_id: int = Field(..., ge=1)
    camera_id: Optional[int] = None
    payload_type: str = Field(..., description="OCCUPANCY_BATCH | ATTENDANCE_HEARTBEAT | DETECTION_EVENT")
    payload: Dict[str, Any]

@router.get("/status")
def get_offline_status(
    centre_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user)
):
    pending = offline_sync_manager.get_pending(centre_id)
    return {
        "success": True,
        "data": {
            "pending_count": len(pending),
            "pending_items": [
                {
                    "item_id": p.item_id,
                    "centre_id": p.centre_id,
                    "camera_id": p.camera_id,
                    "payload_type": p.payload_type,
                    "queued_at": p.queued_at,
                    "synced": p.synced
                }
                for p in pending
            ],
            "edge_mode": "ACTIVE",
            "offline_storage_limit_mb": 512
        }
    }

@router.post("/queue")
def queue_offline_telemetry(
    req: OfflineEnqueueRequest,
    current_user: User = Depends(get_current_user)
):
    item = offline_sync_manager.enqueue(
        centre_id=req.centre_id,
        camera_id=req.camera_id,
        payload_type=req.payload_type,
        payload=req.payload
    )
    return {
        "success": True,
        "data": {
            "item_id": item.item_id,
            "status": "QUEUED",
            "queued_at": item.queued_at,
            "centre_id": item.centre_id
        }
    }

@router.post("/sync")
def trigger_sync(
    centre_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user)
):
    result = offline_sync_manager.sync_all(centre_id)
    return {
        "success": True,
        "data": result
    }

@router.get("/adaptive-config")
def get_adaptive_config(
    bandwidth_kbps: float = Query(128.0, ge=16.0, le=50000.0),
    current_user: User = Depends(get_current_user)
):
    config = offline_sync_manager.get_adaptive_config(bandwidth_kbps)
    return {
        "success": True,
        "data": config
    }
