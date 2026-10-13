"""
Seed Data Script for SkillGuard AI.
Populates simulated demonstration data for SIH Problem Statement 26245.

IMPORTANT NOTICE:
All seeded records represent SIMULATED DEMO DATA for system testing
and prototype evaluation. They do not represent official MSDE statistics or data.

Usage:
    python -m app.database.seed
"""

import sys
import logging
from datetime import datetime, timezone, timedelta
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
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("seed")

def seed_demo_data():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        logger.info("--- Starting SkillGuard AI Seed Data Injection (Idempotent) ---")
        
        # -------------------------------------------------------------------
        # 1. Demo Users (4 Roles)
        # -------------------------------------------------------------------
        demo_users = [
            {
                "username": "admin",
                "email": "admin@skillguard.gov.in",
                "role": UserRole.ADMIN,
                "password": "AdminPassword@2026",
            },
            {
                "username": "monitor",
                "email": "monitor@skillguard.gov.in",
                "role": UserRole.MONITOR,
                "password": "MonitorPassword@2026",
            },
            {
                "username": "inspector",
                "email": "inspector@skillguard.gov.in",
                "role": UserRole.INSPECTOR,
                "password": "InspectorPassword@2026",
            },
            {
                "username": "operator",
                "email": "operator@skillguard.gov.in",
                "role": UserRole.CENTRE_OPERATOR,
                "password": "OperatorPassword@2026",
            },
        ]

        for u_data in demo_users:
            existing = db.query(User).filter(User.username == u_data["username"]).first()
            if not existing:
                user = User(
                    username=u_data["username"],
                    email=u_data["email"],
                    password_hash=get_password_hash(u_data["password"]),
                    role=u_data["role"],
                    is_active=True,
                )
                db.add(user)
                logger.info(f"Seeded User: {u_data['username']} ({u_data['role'].value})")
            else:
                logger.info(f"User '{u_data['username']}' already exists, skipping.")
        
        db.commit()

        # -------------------------------------------------------------------
        # 2. Training Centres (3 Centres)
        # -------------------------------------------------------------------
        centres_data = [
            {
                "centre_code": "TN-CBE-001",
                "name": "Coimbatore Skill Development Centre 01 [SIMULATED DEMO DATA]",
                "state": "Tamil Nadu",
                "district": "Coimbatore",
                "address": "Avinashi Road, Peelamedu, Coimbatore 641004",
                "latitude": 11.0286,
                "longitude": 77.0125,
                "capacity": 50,
                "status": CentreStatus.ACTIVE,
            },
            {
                "centre_code": "TN-CBE-002",
                "name": "Coimbatore Skill Development Centre 02 [SIMULATED DEMO DATA]",
                "state": "Tamil Nadu",
                "district": "Coimbatore",
                "address": "Mettupalayam Road, Thudiyalur, Coimbatore 641034",
                "latitude": 11.0772,
                "longitude": 76.9482,
                "capacity": 50,
                "status": CentreStatus.ACTIVE,
            },
            {
                "centre_code": "TN-CBE-003",
                "name": "Coimbatore Skill Development Centre 03 [SIMULATED DEMO DATA]",
                "state": "Tamil Nadu",
                "district": "Coimbatore",
                "address": "Pollachi Road, Eachanari, Coimbatore 641021",
                "latitude": 10.9324,
                "longitude": 76.9748,
                "capacity": 60,
                "status": CentreStatus.ACTIVE,
            },
        ]

        centre_entities = {}
        for c_data in centres_data:
            existing = db.query(TrainingCentre).filter(TrainingCentre.centre_code == c_data["centre_code"]).first()
            if not existing:
                centre = TrainingCentre(**c_data)
                db.add(centre)
                db.flush()
                centre_entities[c_data["centre_code"]] = centre
                logger.info(f"Seeded Centre: {c_data['centre_code']} - {c_data['name']}")
            else:
                centre_entities[c_data["centre_code"]] = existing
                logger.info(f"Centre '{c_data['centre_code']}' already exists, skipping.")

        db.commit()

        # -------------------------------------------------------------------
        # 3. Cameras
        # -------------------------------------------------------------------
        cameras_data = [
            {
                "centre_code": "TN-CBE-001",
                "name": "TN-CBE-001-CAM-01",
                "source_type": CameraSourceType.SIMULATION,
                "source_url": "simulation://centre_001/stream_a",
                "zone": "Classroom A",
                "resolution": "1080p",
                "fps": 15,
                "status": CameraStatus.ONLINE,
            },
            {
                "centre_code": "TN-CBE-002",
                "name": "TN-CBE-002-CAM-01",
                "source_type": CameraSourceType.SIMULATION,
                "source_url": "simulation://centre_002/stream_a",
                "zone": "Lab 1",
                "resolution": "1080p",
                "fps": 15,
                "status": CameraStatus.ONLINE,
            },
            {
                "centre_code": "TN-CBE-003",
                "name": "TN-CBE-003-CAM-01",
                "source_type": CameraSourceType.SIMULATION,
                "source_url": "simulation://centre_003/stream_a",
                "zone": "Workshop A",
                "resolution": "1080p",
                "fps": 15,
                "status": CameraStatus.ONLINE,
            },
            {
                "centre_code": "TN-CBE-003",
                "name": "TN-CBE-003-CAM-02",
                "source_type": CameraSourceType.SIMULATION,
                "source_url": "simulation://centre_003/stream_b",
                "zone": "Workshop B",
                "resolution": "1080p",
                "fps": 15,
                "status": CameraStatus.ONLINE,
            },
        ]

        camera_entities = {}
        for cam_data in cameras_data:
            c_code = cam_data.pop("centre_code")
            centre = centre_entities[c_code]
            existing = db.query(Camera).filter(Camera.centre_id == centre.id, Camera.name == cam_data["name"]).first()
            if not existing:
                cam = Camera(centre_id=centre.id, **cam_data)
                db.add(cam)
                db.flush()
                camera_entities[cam_data["name"]] = cam
                logger.info(f"Seeded Camera: {cam_data['name']} for Centre {c_code}")
            else:
                camera_entities[cam_data["name"]] = existing
                logger.info(f"Camera '{cam_data['name']}' already exists, skipping.")

        db.commit()

        # -------------------------------------------------------------------
        # 4. Sanctioned Inventory Items
        # -------------------------------------------------------------------
        inventory_data = [
            # Centre 1
            {"centre_code": "TN-CBE-001", "item_type": ItemType.CHAIR, "item_name": "Trainee Ergonomic Chair", "sanctioned": 45, "minimum": 40, "zone": "Classroom A"},
            {"centre_code": "TN-CBE-001", "item_type": ItemType.COMPUTER, "item_name": "Workstation Desktop Computer", "sanctioned": 30, "minimum": 25, "zone": "Classroom A"},
            {"centre_code": "TN-CBE-001", "item_type": ItemType.WORKBENCH, "item_name": "Multi-Student Lab Workbench", "sanctioned": 8, "minimum": 6, "zone": "Classroom A"},
            {"centre_code": "TN-CBE-001", "item_type": ItemType.MACHINE, "item_name": "CNC Demonstration Unit", "sanctioned": 5, "minimum": 4, "zone": "Lab 1"},
            {"centre_code": "TN-CBE-001", "item_type": ItemType.PROJECTOR, "item_name": "Digital Overhead Projector", "sanctioned": 2, "minimum": 1, "zone": "Classroom A"},
            # Centre 2
            {"centre_code": "TN-CBE-002", "item_type": ItemType.CHAIR, "item_name": "Trainee Ergonomic Chair", "sanctioned": 45, "minimum": 40, "zone": "Lab 1"},
            {"centre_code": "TN-CBE-002", "item_type": ItemType.COMPUTER, "item_name": "Workstation Desktop Computer", "sanctioned": 30, "minimum": 25, "zone": "Lab 1"},
            {"centre_code": "TN-CBE-002", "item_type": ItemType.WORKBENCH, "item_name": "Multi-Student Lab Workbench", "sanctioned": 8, "minimum": 6, "zone": "Lab 1"},
            {"centre_code": "TN-CBE-002", "item_type": ItemType.MACHINE, "item_name": "Automotive Diagnostic Rig", "sanctioned": 5, "minimum": 4, "zone": "Lab 1"},
            {"centre_code": "TN-CBE-002", "item_type": ItemType.PROJECTOR, "item_name": "Digital Overhead Projector", "sanctioned": 2, "minimum": 1, "zone": "Lab 1"},
            # Centre 3
            {"centre_code": "TN-CBE-003", "item_type": ItemType.CHAIR, "item_name": "Trainee Ergonomic Chair", "sanctioned": 50, "minimum": 45, "zone": "Workshop A"},
            {"centre_code": "TN-CBE-003", "item_type": ItemType.COMPUTER, "item_name": "Workstation Desktop Computer", "sanctioned": 35, "minimum": 30, "zone": "Workshop A"},
            {"centre_code": "TN-CBE-003", "item_type": ItemType.WORKBENCH, "item_name": "Heavy Duty Industrial Workbench", "sanctioned": 10, "minimum": 8, "zone": "Workshop B"},
            {"centre_code": "TN-CBE-003", "item_type": ItemType.MACHINE, "item_name": "Industrial Sewing / Lathe Machine", "sanctioned": 6, "minimum": 5, "zone": "Workshop B"},
            {"centre_code": "TN-CBE-003", "item_type": ItemType.PROJECTOR, "item_name": "Digital Overhead Projector", "sanctioned": 2, "minimum": 2, "zone": "Workshop A"},
        ]

        for inv in inventory_data:
            centre = centre_entities[inv["centre_code"]]
            existing = db.query(InventoryItem).filter(
                InventoryItem.centre_id == centre.id,
                InventoryItem.item_type == inv["item_type"],
                InventoryItem.item_name == inv["item_name"]
            ).first()
            if not existing:
                item = InventoryItem(
                    centre_id=centre.id,
                    item_type=inv["item_type"],
                    item_name=inv["item_name"],
                    sanctioned_quantity=inv["sanctioned"],
                    minimum_required=inv["minimum"],
                    zone=inv["zone"],
                )
                db.add(item)
                logger.info(f"Seeded Inventory: {inv['item_type'].value} for Centre {inv['centre_code']}")
            else:
                logger.info(f"Inventory '{inv['item_name']}' already exists, skipping.")

        db.commit()

        # -------------------------------------------------------------------
        # 5. Submitted Attendance Records (Last 3 Days)
        # -------------------------------------------------------------------
        today = datetime.now(timezone.utc).date()
        attendance_scenarios = [
            # Centre 1 (Normal / High attendance)
            {"centre_code": "TN-CBE-001", "reg": 45, "sub": 42},
            # Centre 2 (Reported high attendance, discrepancy scenario)
            {"centre_code": "TN-CBE-002", "reg": 45, "sub": 44},
            # Centre 3 (Reported standard attendance)
            {"centre_code": "TN-CBE-003", "reg": 50, "sub": 47},
        ]

        for att_data in attendance_scenarios:
            centre = centre_entities[att_data["centre_code"]]
            for days_ago in range(3):
                att_date = (today - timedelta(days=days_ago)).isoformat()
                existing = db.query(AttendanceRecord).filter(
                    AttendanceRecord.centre_id == centre.id,
                    AttendanceRecord.date == att_date,
                    AttendanceRecord.session == "Morning"
                ).first()
                if not existing:
                    att = AttendanceRecord(
                        centre_id=centre.id,
                        date=att_date,
                        session="Morning",
                        registered_count=att_data["reg"],
                        submitted_present=att_data["sub"],
                        source=AttendanceSource.CENTRE_SUBMITTED,
                    )
                    db.add(att)
                    logger.info(f"Seeded Attendance: {att_date} for Centre {att_data['centre_code']}")
                else:
                    logger.info(f"Attendance for {att_date} already exists, skipping.")

        db.commit()

        # -------------------------------------------------------------------
        # 6. Historical Compliance Scores (Marked as SIMULATED DEMO DATA)
        # -------------------------------------------------------------------
        scores_data = [
            {
                "centre_code": "TN-CBE-001",
                "attendance_score": 96.0,
                "infrastructure_score": 95.0,
                "activity_score": 90.0,
                "data_consistency_score": 95.0,
                "overall_score": 94.4,
                "risk_level": RiskLevel.LOW,
                "estimated_presence": 41,
                "submitted_attendance": 42,
                "discrepancy": 1,
                "discrepancy_pct": 2.38,
                "infra_compliance_pct": 98.0,
            },
            {
                "centre_code": "TN-CBE-002",
                "attendance_score": 52.0,
                "infrastructure_score": 92.0,
                "activity_score": 85.0,
                "data_consistency_score": 70.0,
                "overall_score": 68.3,
                "risk_level": RiskLevel.HIGH,
                "estimated_presence": 28,
                "submitted_attendance": 44,
                "discrepancy": 16,
                "discrepancy_pct": 36.36,
                "infra_compliance_pct": 94.0,
            },
            {
                "centre_code": "TN-CBE-003",
                "attendance_score": 90.0,
                "infrastructure_score": 45.0,
                "activity_score": 55.0,
                "data_consistency_score": 75.0,
                "overall_score": 60.5,
                "risk_level": RiskLevel.HIGH,
                "estimated_presence": 45,
                "submitted_attendance": 47,
                "discrepancy": 2,
                "discrepancy_pct": 4.25,
                "infra_compliance_pct": 52.0,
            },
        ]

        for sc in scores_data:
            centre = centre_entities[sc["centre_code"]]
            existing = db.query(ComplianceScore).filter(ComplianceScore.centre_id == centre.id).first()
            if not existing:
                score_obj = ComplianceScore(
                    centre_id=centre.id,
                    timestamp=datetime.now(timezone.utc),
                    attendance_score=sc["attendance_score"],
                    infrastructure_score=sc["infrastructure_score"],
                    activity_score=sc["activity_score"],
                    data_consistency_score=sc["data_consistency_score"],
                    overall_score=sc["overall_score"],
                    risk_level=sc["risk_level"],
                    estimated_physical_presence=sc["estimated_presence"],
                    submitted_attendance=sc["submitted_attendance"],
                    attendance_discrepancy=sc["discrepancy"],
                    attendance_discrepancy_percentage=sc["discrepancy_pct"],
                    infrastructure_compliance_percentage=sc["infra_compliance_pct"],
                )
                db.add(score_obj)
                logger.info(f"Seeded ComplianceScore: Centre {sc['centre_code']} (Score: {sc['overall_score']}, Risk: {sc['risk_level'].value})")
            else:
                logger.info(f"ComplianceScore for Centre {sc['centre_code']} already exists, skipping.")

        db.commit()

        # -------------------------------------------------------------------
        # 7. Historical Alerts (Marked as SIMULATED DEMO DATA)
        # -------------------------------------------------------------------
        demo_alerts = [
            {
                "centre_code": "TN-CBE-002",
                "camera_name": "TN-CBE-002-CAM-01",
                "alert_type": AlertType.ATTENDANCE_DISCREPANCY,
                "severity": AlertSeverity.HIGH,
                "title": "Severe Attendance Discrepancy Flagged [SIMULATED DEMO DATA]",
                "description": (
                    "Submitted attendance reported 44 trainees present; estimated physical presence "
                    "averaged 28 over the observation window (discrepancy of 36.4%)."
                ),
                "confidence": 0.92,
                "status": AlertStatus.OPEN,
            },
            {
                "centre_code": "TN-CBE-003",
                "camera_name": "TN-CBE-003-CAM-01",
                "alert_type": AlertType.INFRASTRUCTURE_SHORTAGE,
                "severity": AlertSeverity.HIGH,
                "title": "Sanctioned Machine Equipment Shortage [SIMULATED DEMO DATA]",
                "description": (
                    "Sanctioned inventory mandates 6 Industrial Machines in Workshop B; only 3 detected "
                    "consistently over the observation window (potential shortage of 3 units)."
                ),
                "confidence": 0.88,
                "status": AlertStatus.OPEN,
            },
            {
                "centre_code": "TN-CBE-003",
                "camera_name": "TN-CBE-003-CAM-02",
                "alert_type": AlertType.LOW_CONFIDENCE,
                "severity": AlertSeverity.MEDIUM,
                "title": "Camera Angle Partial Occlusion Detected [SIMULATED DEMO DATA]",
                "description": (
                    "Camera field of view suffers partial occlusion in Zone 2; detection confidence "
                    "dropped below the configured threshold (0.40)."
                ),
                "confidence": 0.65,
                "status": AlertStatus.ACKNOWLEDGED,
            },
        ]

        for alt in demo_alerts:
            centre = centre_entities[alt["centre_code"]]
            camera = camera_entities.get(alt["camera_name"])
            existing = db.query(Alert).filter(
                Alert.centre_id == centre.id,
                Alert.title == alt["title"]
            ).first()
            if not existing:
                alert_obj = Alert(
                    centre_id=centre.id,
                    camera_id=camera.id if camera else None,
                    alert_type=alt["alert_type"],
                    severity=alt["severity"],
                    title=alt["title"],
                    description=alt["description"],
                    confidence=alt["confidence"],
                    status=alt["status"],
                    created_at=datetime.now(timezone.utc) - timedelta(hours=2),
                )
                db.add(alert_obj)
                logger.info(f"Seeded Alert: '{alt['title']}' for Centre {alt['centre_code']}")
            else:
                logger.info(f"Alert '{alt['title']}' already exists, skipping.")

        db.commit()
        logger.info("--- Seed Data Injection Completed Successfully ---")
        return True

    except Exception as e:
        logger.error(f"Error seeding database: {e}", exc_info=True)
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = seed_demo_data()
    sys.exit(0 if success else 1)
