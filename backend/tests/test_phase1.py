import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from app.database.database import SessionLocal, engine
from app.database.models import Base, User, TrainingCentre, Camera, Alert, ComplianceScore

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"
    assert data["data"]["backend"] == "online"
    assert data["data"]["database"] == "connected"

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "SkillGuard AI"
    assert data["data"]["problem_statement"] == "26245"

def test_password_hashing():
    raw_pwd = "StrongSecurePassword123!"
    hashed = get_password_hash(raw_pwd)
    assert hashed != raw_pwd
    assert verify_password(raw_pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_handling():
    token = create_access_token(subject=1, role="ADMIN")
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "1"
    assert payload["role"] == "ADMIN"
    assert "exp" in payload

def test_database_models_metadata():
    expected_tables = {
        "users",
        "training_centres",
        "cameras",
        "attendance_records",
        "inventory_items",
        "detection_events",
        "compliance_scores",
        "alerts",
        "processing_sessions",
    }
    assert expected_tables.issubset(set(Base.metadata.tables.keys()))

def test_database_session_query():
    with SessionLocal() as db:
        user_count = db.query(User).count()
        assert isinstance(user_count, int)
