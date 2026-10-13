import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User, ProcessingStatus
from app.core.security import get_current_user
from app.services.detection_service import DetectionService
from app.schemas.detections import ProcessingSessionResponse
from app.video.processor import VideoProcessor, ALLOWED_EXTENSIONS
from app.services.processing_service import processing_service

router = APIRouter(prefix="/processing", tags=["Processing Sessions"])

video_processor = VideoProcessor()

@router.get("", response_model=dict)
def list_processing_sessions(
    centre_id: Optional[int] = Query(None),
    status_filter: Optional[ProcessingStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = DetectionService.get_sessions(
        db, centre_id=centre_id, status=status_filter, skip=skip, limit=limit
    )
    return {
        "success": True,
        "data": [ProcessingSessionResponse.model_validate(s).model_dump() for s in sessions]
    }


@router.get("/{session_id}", response_model=dict)
def get_processing_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = DetectionService.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Processing session with ID {session_id} not found"
        )
    return {
        "success": True,
        "data": ProcessingSessionResponse.model_validate(session).model_dump()
    }


@router.post("/upload", response_model=dict)
async def upload_and_process_video(
    centre_id: int = Form(..., description="Training centre ID to associate this video with"),
    camera_id: Optional[int] = Form(None, description="Camera ID (optional)"),
    submitted_attendance: Optional[int] = Form(None, description="Register headcount submitted by the centre (for reconciliation)"),
    video: UploadFile = File(..., description="Video stream from CCTV or manual upload"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and process a video file for privacy-preserving attendance and infrastructure analysis.
    
    Privacy guarantee: Zero facial recognition. No biometric embeddings stored or transmitted.
    Analysis is performed using anonymous head/body bounding box detection and short-lived session tracking IDs.
    
    [SIMULATED DEMO DATA — Thresholds are configurable demonstration parameters, not official MSDE policy.]
    """

    # Validate file metadata
    safe_filename = video.filename or "upload.mp4"
    content_length = video.size or 0

    valid, reason = video_processor.validate_file_metadata(safe_filename, content_length)
    if not valid:
        raise HTTPException(status_code=422, detail=f"File validation failed: {reason}")

    # Read and save to disk for processing
    unique_name = f"{uuid.uuid4().hex}_{safe_filename.replace(' ', '_')}"
    file_path = os.path.join(video_processor.upload_dir, unique_name)

    try:
        contents = await video.read()
        if len(contents) > 100 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum allowed size is 100MB.")

        with open(file_path, "wb") as f:
            f.write(contents)

        # Validate container metadata
        meta = video_processor.inspect_video(file_path)
        if not meta.is_valid:
            os.remove(file_path)
            raise HTTPException(status_code=422, detail=f"Invalid video container: {meta.status_message}")

        # Run full AI analysis pipeline
        result = processing_service.process_video_stream(
            db=db,
            centre_id=centre_id,
            camera_id=camera_id,
            file_path=file_path,
            filename=unique_name,
            submitted_attendance=submitted_attendance
        )

        # Cleanup uploaded file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "success": True,
            "data": {
                **result,
                "video_metadata": meta.model_dump(),
            },
            "simulated_demo": True,
            "privacy_notice": "No facial data captured. Anonymous presence estimation only."
        }

    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Processing pipeline error: {str(e)}")
