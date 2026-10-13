import time
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.database.database import engine, Base, SessionLocal

# Setup structured logging
setup_logging()

# Initialize tables
import app.database.models
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Privacy-Preserving AI-Based Training Centre Attendance and Infrastructure Compliance Monitoring",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Standardized Error Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    from fastapi.encoders import jsonable_encoder
    errors = exc.errors()
    first_msg = errors[0].get("msg") if errors else "Validation failed"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": first_msg,
                "details": errors
            }
        })
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Check system logs for details."
            }
        }
    )

# Health check endpoints
@app.get("/health")
@app.get("/api/v1/health")
def health_check():
    db_status = "connected"
    tables_count = 0
    centres_count = 0
    users_count = 0
    try:
        from sqlalchemy import inspect
        from app.database.models import TrainingCentre, User
        inspector = inspect(engine)
        tables_count = len(inspector.get_table_names())
        with SessionLocal() as db:
            centres_count = db.query(TrainingCentre).count()
            users_count = db.query(User).count()
    except Exception as e:
        logger.error(f"Database health check query failed: {e}")
        db_status = "disconnected"

    return {
        "success": True,
        "data": {
            "status": "healthy",
            "backend": "online",
            "database": db_status,
            "tables": tables_count,
            "demo_centres": centres_count,
            "users": users_count,
            "ai_engine": "ready",
            "storage": "writable",
            "version": settings.VERSION,
            "low_bandwidth_mode": settings.LOW_BANDWIDTH_MODE
        }
    }

@app.get("/")
def root():
    return {
        "success": True,
        "data": {
            "name": settings.PROJECT_NAME,
            "subtitle": "Privacy-Preserving AI-Based Training Centre Attendance and Infrastructure Compliance Monitoring",
            "problem_statement": "26245",
            "version": settings.VERSION,
            "health_url": "/api/v1/health",
            "docs_url": "/docs"
        }
    }

# Mount Modular API Router
from app.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
