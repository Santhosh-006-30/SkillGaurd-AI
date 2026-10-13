from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.centres import router as centres_router
from app.api.cameras import router as cameras_router
from app.api.attendance import router as attendance_router
from app.api.infrastructure import router as infrastructure_router
from app.api.detections import router as detections_router
from app.api.processing import router as processing_router
from app.api.compliance import router as compliance_router
from app.api.alerts import router as alerts_router
from app.api.analytics import router as analytics_router
from app.api.reports import router as reports_router
from app.api.evaluation import router as evaluation_router
from app.api.offline import router as offline_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(centres_router)
api_router.include_router(cameras_router)
api_router.include_router(attendance_router)
api_router.include_router(infrastructure_router)
api_router.include_router(detections_router)
api_router.include_router(processing_router)
api_router.include_router(compliance_router)
api_router.include_router(alerts_router)
api_router.include_router(analytics_router)
api_router.include_router(reports_router)
api_router.include_router(evaluation_router)
api_router.include_router(offline_router)
