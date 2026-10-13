"""
Database Initialization Module for SkillGuard AI.
Handles idempotent creation of all schema tables and verifies table integrity.
Usage:
    python -m app.database.init_db
"""

import sys
import logging
from sqlalchemy import inspect
from app.database.database import engine, Base
import app.database.models  # Ensure all models are registered with Base.metadata

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("init_db")

def init_database() -> bool:
    try:
        logger.info("Initializing SkillGuard AI database schema...")
        Base.metadata.create_all(bind=engine)
        
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        expected_tables = [
            "users",
            "training_centres",
            "cameras",
            "attendance_records",
            "inventory_items",
            "detection_events",
            "processing_sessions",
            "compliance_scores",
            "alerts",
        ]
        
        logger.info(f"Verified {len(existing_tables)} tables present in database:")
        all_ok = True
        for tbl in expected_tables:
            if tbl in existing_tables:
                logger.info(f"  [OK] Table: {tbl}")
            else:
                logger.error(f"  [MISSING] Table: {tbl}")
                all_ok = False
        
        if all_ok:
            logger.info("Database schema initialization completed successfully.")
            return True
        else:
            logger.error("Database schema initialization encountered missing tables.")
            return False

    except Exception as e:
        logger.error(f"Error during database initialization: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
