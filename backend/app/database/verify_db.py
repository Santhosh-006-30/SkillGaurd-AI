"""
Database Verification Script for SkillGuard AI.
Verifies database existence, table schemas, foreign key integrity,
and confirms the presence of simulated demo data.

Usage:
    python -m app.database.verify_db
"""

import sys
import logging
from sqlalchemy import inspect
from app.database.database import SessionLocal, engine
from app.database.models import (
    User, TrainingCentre, Camera, AttendanceRecord,
    InventoryItem, DetectionEvent, ProcessingSession,
    ComplianceScore, Alert
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("verify_db")

def verify_database() -> bool:
    logger.info("==================================================")
    logger.info("   SKILLGUARD AI — DATABASE VERIFICATION REPORT   ")
    logger.info("==================================================")

    # 1. Database Connection Check
    try:
        connection = engine.connect()
        connection.close()
        logger.info("Database: OK")
    except Exception as e:
        logger.error(f"Database: FAILED ({e})")
        return False

    # 2. Table Existence Checks
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    model_table_map = [
        ("Users", "users", User),
        ("Training Centres", "training_centres", TrainingCentre),
        ("Cameras", "cameras", Camera),
        ("Attendance", "attendance_records", AttendanceRecord),
        ("Inventory", "inventory_items", InventoryItem),
        ("Detection Events", "detection_events", DetectionEvent),
        ("Processing Sessions", "processing_sessions", ProcessingSession),
        ("Compliance Scores", "compliance_scores", ComplianceScore),
        ("Alerts", "alerts", Alert),
    ]

    logger.info("\nTables:")
    all_tables_ok = True
    for label, tbl_name, _ in model_table_map:
        if tbl_name in existing_tables:
            logger.info(f"{label}: OK")
        else:
            logger.error(f"{label}: MISSING")
            all_tables_ok = False

    if not all_tables_ok:
        logger.error("\nDatabase schema incomplete.")
        return False

    # 3. Seed Data & Record Count Checks
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        centre_count = db.query(TrainingCentre).count()
        camera_count = db.query(Camera).count()
        attendance_count = db.query(AttendanceRecord).count()
        inventory_count = db.query(InventoryItem).count()
        compliance_count = db.query(ComplianceScore).count()
        alert_count = db.query(Alert).count()

        logger.info("\nRecord Counts:")
        logger.info(f"  Users: {user_count} (Expected >= 4)")
        logger.info(f"  Training Centres: {centre_count} (Expected >= 3)")
        logger.info(f"  Cameras: {camera_count} (Expected >= 4)")
        logger.info(f"  Attendance Records: {attendance_count} (Expected >= 9)")
        logger.info(f"  Inventory Items: {inventory_count} (Expected >= 15)")
        logger.info(f"  Compliance Scores: {compliance_count} (Expected >= 3)")
        logger.info(f"  Alerts: {alert_count} (Expected >= 3)")

        # Verify Foreign Key Relationships
        sample_centre = db.query(TrainingCentre).filter_by(centre_code="TN-CBE-001").first()
        if not sample_centre:
            logger.error("\nSeed data: FAILED (Centre TN-CBE-001 not found)")
            return False

        if len(sample_centre.cameras) == 0:
            logger.error("\nSeed data: FAILED (Cameras relationship empty for TN-CBE-001)")
            return False

        if len(sample_centre.inventory_items) == 0:
            logger.error("\nSeed data: FAILED (Inventory relationship empty for TN-CBE-001)")
            return False

        if (
            user_count >= 4
            and centre_count >= 3
            and camera_count >= 4
            and attendance_count >= 9
            and inventory_count >= 15
            and compliance_count >= 3
            and alert_count >= 3
        ):
            logger.info("\nSeed data:")
            logger.info("OK")
            logger.info("==================================================")
            return True
        else:
            logger.warning("\nSeed data:")
            logger.warning("PARTIAL / INCOMPLETE (Run python -m app.database.seed)")
            return False

    except Exception as e:
        logger.error(f"Error querying database: {e}", exc_info=True)
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = verify_database()
    sys.exit(0 if success else 1)
