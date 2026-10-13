"""
Tests for Phase 14 (Low-Bandwidth & Offline Mode) and Phase 16 (Dossiers & PDF/JSON Reports).
[SIMULATED DEMO — All data marked synthetic]
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.offline_sync import offline_sync_manager
from app.services.report_generator import generate_centre_dossier_data, generate_pdf_report
from app.database.database import SessionLocal

client = TestClient(app)

def get_auth_token():
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "AdminPassword@2026"})
    return res.json()["data"]["access_token"]

def test_offline_sync_manager_basic():
    item = offline_sync_manager.enqueue(
        centre_id=1,
        camera_id=1,
        payload_type="OCCUPANCY_BATCH",
        payload={"count": 40}
    )
    assert item.item_id is not None
    assert item.synced is False

    pending = offline_sync_manager.get_pending(centre_id=1)
    assert any(p.item_id == item.item_id for p in pending)

    sync_res = offline_sync_manager.sync_all(centre_id=1)
    assert sync_res["synced_count"] >= 1

def test_adaptive_sampling_profiles():
    cfg_ultra = offline_sync_manager.get_adaptive_config(bandwidth_kbps=64.0)
    assert cfg_ultra["adaptive_mode"] == "ULTRA_LOW"
    assert cfg_ultra["sample_rate_fps"] == 0.2
    assert cfg_ultra["metadata_only_transmission"] is True

    cfg_low = offline_sync_manager.get_adaptive_config(bandwidth_kbps=512.0)
    assert cfg_low["adaptive_mode"] == "LOW"
    assert cfg_low["sample_rate_fps"] == 1.0

    cfg_std = offline_sync_manager.get_adaptive_config(bandwidth_kbps=2048.0)
    assert cfg_std["adaptive_mode"] == "STANDARD"
    assert cfg_std["sample_rate_fps"] == 5.0

def test_offline_endpoints():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Status
    res = client.get("/api/v1/offline/status", headers=headers)
    assert res.status_code == 200
    assert res.json()["success"] is True

    # Queue
    res = client.post("/api/v1/offline/queue", headers=headers, json={
        "centre_id": 1,
        "camera_id": 2,
        "payload_type": "ATTENDANCE_HEARTBEAT",
        "payload": {"students_present": 44}
    })
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "QUEUED"

    # Sync
    res = client.post("/api/v1/offline/sync?centre_id=1", headers=headers)
    assert res.status_code == 200
    assert res.json()["success"] is True

    # Adaptive config
    res = client.get("/api/v1/offline/adaptive-config?bandwidth_kbps=100", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["adaptive_mode"] == "ULTRA_LOW"

def test_report_generation_service():
    with SessionLocal() as db:
        dossier = generate_centre_dossier_data(db, centre_id=1)
        assert dossier is not None
        assert "dossier_id" in dossier
        assert "integrity_hash_sha256" in dossier
        assert "compliance" in dossier
        assert "inventory" in dossier
        assert len(dossier["inventory"]) > 0

        pdf_bytes = generate_pdf_report(dossier)
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b"%PDF")
        assert len(pdf_bytes) > 1000

def test_report_endpoints():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Meta
    res = client.get("/api/v1/reports/centre/1", headers=headers)
    assert res.status_code == 200
    assert len(res.json()["data"]["reports"]) == 2

    # JSON
    res = client.get("/api/v1/reports/centre/1/json", headers=headers)
    assert res.status_code == 200
    assert res.json()["data"]["centre"]["code"] == "TN-CBE-001"

    # PDF
    res = client.get("/api/v1/reports/centre/1/pdf", headers=headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF")

    # 404 for nonexistent centre
    res = client.get("/api/v1/reports/centre/999", headers=headers)
    assert res.status_code == 404
