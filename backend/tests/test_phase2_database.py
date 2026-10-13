import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from app.database.database import SessionLocal, engine, Base
from app.database.models import (
    User, UserRole,
    TrainingCentre, CentreStatus,
    Camera, CameraSourceType, CameraStatus,
    AttendanceRecord, AttendanceSource,
    InventoryItem, ItemType,
    ComplianceScore, RiskLevel,
    Alert, AlertType, AlertSeverity, AlertStatus
)
from app.database.init_db import init_database
from app.database.seed import seed_demo_data
from app.core.security import get_password_hash

def test_database_initialization():
    """Verify init_database runs cleanly and verifies all 9 tables."""
    assert init_database() is True

def test_user_model_constraints():
    """Test user creation, unique constraints on username and email, and required fields."""
    with SessionLocal() as db:
        # Username uniqueness
        duplicate_user = User(
            username="admin",  # seeded admin
            email="unique_new_email@example.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.ADMIN,
        )
        db.add(duplicate_user)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        # Email uniqueness
        duplicate_email = User(
            username="unique_new_username",
            email="admin@skillguard.gov.in",  # seeded admin email
            password_hash=get_password_hash("password123"),
            role=UserRole.ADMIN,
        )
        db.add(duplicate_email)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

def test_training_centre_relationships():
    """Verify training centre relationships to cameras, inventory, attendance, and alerts."""
    with SessionLocal() as db:
        centre = db.query(TrainingCentre).filter_by(centre_code="TN-CBE-001").first()
        assert centre is not None
        assert centre.capacity == 50
        assert len(centre.cameras) >= 1
        assert len(centre.inventory_items) >= 5
        assert len(centre.attendance_records) >= 3

        # Centre code uniqueness
        dup_centre = TrainingCentre(
            centre_code="TN-CBE-001",
            name="Duplicate Centre",
            state="Tamil Nadu",
            district="Coimbatore",
        )
        db.add(dup_centre)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

def test_camera_foreign_key_and_relationships():
    """Verify camera foreign key constraint enforcement."""
    with SessionLocal() as db:
        invalid_cam = Camera(
            centre_id=999999,  # Non-existent centre
            name="Orphan Camera",
            source_type=CameraSourceType.SIMULATION,
            status=CameraStatus.ONLINE,
        )
        db.add(invalid_cam)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

def test_attendance_record_check_constraints():
    """Verify attendance validation: submitted_present <= registered_count."""
    with SessionLocal() as db:
        centre = db.query(TrainingCentre).first()
        assert centre is not None

        # Invalid attendance where submitted > registered
        invalid_attendance = AttendanceRecord(
            centre_id=centre.id,
            date="2026-10-15",
            session="Morning",
            registered_count=30,
            submitted_present=35,  # Exceeds registered!
            source=AttendanceSource.CENTRE_SUBMITTED,
        )
        db.add(invalid_attendance)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

def test_compliance_score_ranges():
    """Verify score range constraints [0, 100]."""
    with SessionLocal() as db:
        centre = db.query(TrainingCentre).first()
        assert centre is not None

        # Score exceeding 100
        invalid_score = ComplianceScore(
            centre_id=centre.id,
            overall_score=150.0,  # Invalid
            attendance_score=90.0,
            infrastructure_score=90.0,
            risk_level=RiskLevel.LOW,
        )
        db.add(invalid_score)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

def test_alert_relationships():
    """Verify alert belongs to centre and optionally camera."""
    with SessionLocal() as db:
        alert = db.query(Alert).filter(Alert.centre_id.isnot(None)).first()
        assert alert is not None
        assert alert.centre is not None
        assert alert.alert_type in AlertType
        assert alert.severity in AlertSeverity
        assert alert.status in AlertStatus

def test_seed_idempotency():
    """Verify that running seed_demo_data multiple times produces no errors and does not duplicate counts."""
    with SessionLocal() as db:
        count_before = db.query(TrainingCentre).count()
        users_before = db.query(User).count()

    success = seed_demo_data()
    assert success is True

    with SessionLocal() as db:
        count_after = db.query(TrainingCentre).count()
        users_after = db.query(User).count()

    assert count_before == count_after
    assert users_before == users_after
