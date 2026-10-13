from datetime import datetime, timezone
import enum
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, Enum, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from app.database.database import Base

def utc_now():
    return datetime.now(timezone.utc)

# ---------------------------------------------------------------------------
# Domain Enums
# ---------------------------------------------------------------------------

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    MONITOR = "MONITOR"
    INSPECTOR = "INSPECTOR"
    CENTRE_OPERATOR = "CENTRE_OPERATOR"

class CentreStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    UNDER_REVIEW = "UNDER_REVIEW"
    SUSPENDED = "SUSPENDED"

class CameraSourceType(str, enum.Enum):
    UPLOAD = "UPLOAD"
    WEBCAM = "WEBCAM"
    RTSP = "RTSP"
    SIMULATION = "SIMULATION"

class CameraStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DEGRADED = "DEGRADED"
    UNKNOWN = "UNKNOWN"

class AttendanceSource(str, enum.Enum):
    CENTRE_SUBMITTED = "CENTRE_SUBMITTED"
    IMPORTED = "IMPORTED"
    DEMO = "DEMO"

class ItemType(str, enum.Enum):
    CHAIR = "CHAIR"
    COMPUTER = "COMPUTER"
    WORKBENCH = "WORKBENCH"
    MACHINE = "MACHINE"
    PROJECTOR = "PROJECTOR"

class EventType(str, enum.Enum):
    PERSON_DETECTED = "PERSON_DETECTED"
    EQUIPMENT_DETECTED = "EQUIPMENT_DETECTED"
    OCCUPANCY_CHANGE = "OCCUPANCY_CHANGE"
    INFRASTRUCTURE_DISCREPANCY = "INFRASTRUCTURE_DISCREPANCY"
    ATTENDANCE_DISCREPANCY = "ATTENDANCE_DISCREPANCY"
    ACTIVITY_OBSERVED = "ACTIVITY_OBSERVED"

class ProcessingSource(str, enum.Enum):
    UPLOAD = "UPLOAD"
    WEBCAM = "WEBCAM"
    RTSP = "RTSP"
    SIMULATION = "SIMULATION"

class ProcessingStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertType(str, enum.Enum):
    ATTENDANCE_DISCREPANCY = "ATTENDANCE_DISCREPANCY"
    INFRASTRUCTURE_SHORTAGE = "INFRASTRUCTURE_SHORTAGE"
    ACTIVITY_ANOMALY = "ACTIVITY_ANOMALY"
    CAMERA_OFFLINE = "CAMERA_OFFLINE"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    DATA_INCONSISTENCY = "DATA_INCONSISTENCY"

class AlertSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertStatus(str, enum.Enum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"

# ---------------------------------------------------------------------------
# Domain Models
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.MONITOR, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

class TrainingCentre(Base):
    __tablename__ = "training_centres"

    id = Column(Integer, primary_key=True, index=True)
    centre_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    state = Column(String(100), nullable=False)
    district = Column(String(100), index=True, nullable=False)
    address = Column(String(300), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    capacity = Column(Integer, default=50, nullable=False)
    status = Column(Enum(CentreStatus), default=CentreStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    cameras = relationship("Camera", back_populates="centre", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", back_populates="centre", cascade="all, delete-orphan")
    inventory_items = relationship("InventoryItem", back_populates="centre", cascade="all, delete-orphan")
    detection_events = relationship("DetectionEvent", back_populates="centre", cascade="all, delete-orphan")
    compliance_scores = relationship("ComplianceScore", back_populates="centre", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="centre", cascade="all, delete-orphan")
    processing_sessions = relationship("ProcessingSession", back_populates="centre", cascade="all, delete-orphan")

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    centre_id = Column(Integer, ForeignKey("training_centres.id"), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    source_type = Column(Enum(CameraSourceType), default=CameraSourceType.UPLOAD, nullable=False)
    source_url = Column(String(500), nullable=True)
    zone = Column(String(100), default="Classroom A", nullable=False)
    resolution = Column(String(50), default="1080p", nullable=False)
    fps = Column(Integer, default=15, nullable=False)
    status = Column(Enum(CameraStatus), default=CameraStatus.ONLINE, index=True, nullable=False)
    last_seen = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    centre = relationship("TrainingCentre", back_populates="cameras")
    detection_events = relationship("DetectionEvent", back_populates="camera")
    processing_sessions = relationship("ProcessingSession", back_populates="camera")
    alerts = relationship("Alert", back_populates="camera")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    centre_id = Column(Integer, ForeignKey("training_centres.id"), index=True, nullable=False)
    date = Column(String(20), index=True, nullable=False)  # Format: YYYY-MM-DD
    session = Column(String(50), default="Morning", nullable=False)
    registered_count = Column(Integer, default=0, nullable=False)
    submitted_present = Column(Integer, default=0, nullable=False)
    source = Column(Enum(AttendanceSource), default=AttendanceSource.CENTRE_SUBMITTED, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    __table_args__ = (
        CheckConstraint("registered_count >= 0", name="chk_attendance_registered_positive"),
        CheckConstraint("submitted_present >= 0", name="chk_attendance_submitted_positive"),
        CheckConstraint("submitted_present <= registered_count", name="chk_attendance_submitted_lte_registered"),
        Index("ix_attendance_centre_date", "centre_id", "date"),
    )

    centre = relationship("TrainingCentre", back_populates="attendance_records")

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    centre_id = Column(Integer, ForeignKey("training_centres.id"), index=True, nullable=False)
    item_type = Column(Enum(ItemType), nullable=False)
    item_name = Column(String(200), nullable=False)
    sanctioned_quantity = Column(Integer, default=0, nullable=False)
    minimum_required = Column(Integer, default=0, nullable=False)
    zone = Column(String(100), default="Workshop A", nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    __table_args__ = (
        CheckConstraint("sanctioned_quantity >= 0", name="chk_inventory_sanctioned_positive"),
        CheckConstraint("minimum_required >= 0", name="chk_inventory_minimum_positive"),
        Index("ix_inventory_centre_type", "centre_id", "item_type"),
    )

    centre = relationship("TrainingCentre", back_populates="inventory_items")

class DetectionEvent(Base):
    __tablename__ = "detection_events"

    id = Column(Integer, primary_key=True, index=True)
    centre_id = Column(Integer, ForeignKey("training_centres.id"), index=True, nullable=False)
    camera_id = Column(Integer, ForeignKey("cameras.id"), index=True, nullable=True)
    timestamp = Column(DateTime, index=True, default=utc_now, nullable=False)
    event_type = Column(Enum(EventType), nullable=False)
    object_type = Column(String(100), nullable=True)  # PERSON, CHAIR, COMPUTER, WORKBENCH, MACHINE, PROJECTOR
    count = Column(Integer, default=1, nullable=False)
    confidence = Column(Float, default=0.0, nullable=False)
    zone = Column(String(100), nullable=True)
    metadata_json = Column(Text, nullable=True)  # Serialized JSON metadata (no face/biometric data)
    evidence_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    __table_args__ = (
        CheckConstraint("confidence >= 0.0 AND confidence <= 1.0", name="chk_detection_confidence_range"),
        Index("ix_detection_centre_time", "centre_id", "timestamp"),
    )

    centre = relationship("TrainingCentre", back_populates="detection_events")
    camera = relationship("Camera", back_populates="detection_events")

class ProcessingSession(Base):
    __tablename__ = "processing_sessions"

    id = Column(Integer, primary_key=True, index=True)
    centre_id = Column(Integer, ForeignKey("training_centres.id"), index=True, nullable=False)
    camera_id = Column(Integer, ForeignKey("cameras.id"), index=True, nullable=True)
    source = Column(Enum(ProcessingSource), default=ProcessingSource.UPLOAD, nullable=False)
    started_at = Column(DateTime, default=utc_now, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    frames_processed = Column(Integer, default=0, nullable=False)
    processing_fps = Column(Float, default=0.0, nullable=False)
    average_confidence = Column(Float, default=0.0, nullable=False)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.QUEUED, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    centre = relationship("TrainingCentre", back_populates="processing_sessions")
    camera = relationship("Camera", back_populates="processing_sessions")

class ComplianceScore(Base):
    __tablename__ = "compliance_scores"

    id = Column(Integer, primary_key=True, index=True)
    centre_id = Column(Integer, ForeignKey("training_centres.id"), index=True, nullable=False)
    timestamp = Column(DateTime, index=True, default=utc_now, nullable=False)

    attendance_score = Column(Float, default=100.0, nullable=False)
    infrastructure_score = Column(Float, default=100.0, nullable=False)
    activity_score = Column(Float, default=100.0, nullable=False)
    data_consistency_score = Column(Float, default=100.0, nullable=False)
    overall_score = Column(Float, default=100.0, nullable=False)

    risk_level = Column(Enum(RiskLevel), default=RiskLevel.LOW, nullable=False)

    estimated_physical_presence = Column(Integer, nullable=True)
    submitted_attendance = Column(Integer, nullable=True)
    attendance_discrepancy = Column(Integer, nullable=True)
    attendance_discrepancy_percentage = Column(Float, nullable=True)
    infrastructure_compliance_percentage = Column(Float, nullable=True)

    __table_args__ = (
        CheckConstraint("attendance_score >= 0.0 AND attendance_score <= 100.0", name="chk_attendance_score_range"),
        CheckConstraint("infrastructure_score >= 0.0 AND infrastructure_score <= 100.0", name="chk_infra_score_range"),
        CheckConstraint("overall_score >= 0.0 AND overall_score <= 100.0", name="chk_overall_score_range"),
        Index("ix_compliance_centre_timestamp", "centre_id", "timestamp"),
    )

    centre = relationship("TrainingCentre", back_populates="compliance_scores")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    centre_id = Column(Integer, ForeignKey("training_centres.id"), index=True, nullable=False)
    camera_id = Column(Integer, ForeignKey("cameras.id"), index=True, nullable=True)
    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.MEDIUM, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    confidence = Column(Float, default=0.0, nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.OPEN, index=True, nullable=False)
    evidence_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, index=True, default=utc_now, nullable=False)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint("confidence >= 0.0 AND confidence <= 1.0", name="chk_alert_confidence_range"),
        Index("ix_alerts_centre_status", "centre_id", "status"),
        Index("ix_alerts_severity_created", "severity", "created_at"),
    )

    centre = relationship("TrainingCentre", back_populates="alerts")
    camera = relationship("Camera", back_populates="alerts")
