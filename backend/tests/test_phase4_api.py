import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def admin_headers():
    res = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "AdminPassword@2026"}
    )
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="module")
def monitor_headers():
    res = client.post(
        "/api/v1/auth/login",
        json={"username": "monitor", "password": "MonitorPassword@2026"}
    )
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_unauthenticated_api_rejection():
    # Attempting to access centres without token should return 401
    res = client.get("/api/v1/centres")
    assert res.status_code == 401
    assert res.json()["success"] is False

def test_list_centres(admin_headers):
    res = client.get("/api/v1/centres", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]) >= 3

def test_get_centre_and_summary(admin_headers):
    # Fetch list to get valid ID
    list_res = client.get("/api/v1/centres", headers=admin_headers)
    centre_id = list_res.json()["data"][0]["id"]

    res = client.get(f"/api/v1/centres/{centre_id}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["data"]["id"] == centre_id

    sum_res = client.get(f"/api/v1/centres/{centre_id}/summary", headers=admin_headers)
    assert sum_res.status_code == 200
    s_data = sum_res.json()["data"]
    assert "camera_count" in s_data
    assert "open_alerts_count" in s_data
    assert "overall_compliance_score" in s_data

def test_list_and_filter_cameras(admin_headers):
    res = client.get("/api/v1/cameras", headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 4

    # Filter by status
    res_online = client.get("/api/v1/cameras?status=ONLINE", headers=admin_headers)
    assert res_online.status_code == 200
    assert all(c["status"] == "ONLINE" for c in res_online.json()["data"])

def test_attendance_and_reconciliation(admin_headers):
    list_res = client.get("/api/v1/centres", headers=admin_headers)
    centre_id = list_res.json()["data"][0]["id"]

    # Attendance list
    res = client.get(f"/api/v1/centres/{centre_id}/attendance", headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    # Attendance reconciliation
    rec_res = client.get(f"/api/v1/centres/{centre_id}/attendance/reconciliation", headers=admin_headers)
    assert rec_res.status_code == 200
    data = rec_res.json()["data"]
    assert "attendance_discrepancy" in data
    assert "discrepancy_percentage" in data
    assert data["status"] in ["NORMAL", "REVIEW", "HIGH_DISCREPANCY"]

def test_inventory_and_compliance(admin_headers):
    list_res = client.get("/api/v1/centres", headers=admin_headers)
    centre_id = list_res.json()["data"][0]["id"]

    res = client.get(f"/api/v1/centres/{centre_id}/inventory", headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 5

    comp_res = client.get(f"/api/v1/centres/{centre_id}/inventory/compliance", headers=admin_headers)
    assert comp_res.status_code == 200
    data = comp_res.json()["data"]
    assert "overall_inventory_compliance" in data
    assert "items" in data
    assert len(data["items"]) >= 5

def test_alerts_filtering_and_status_update(admin_headers):
    res = client.get("/api/v1/alerts", headers=admin_headers)
    assert res.status_code == 200
    alerts = res.json()["data"]
    assert len(alerts) >= 1

    alert_id = alerts[0]["id"]
    update_res = client.put(
        f"/api/v1/alerts/{alert_id}/status",
        headers=admin_headers,
        json={"status": "ACKNOWLEDGED"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["data"]["status"] == "ACKNOWLEDGED"

def test_analytics_endpoints(admin_headers):
    # Overview
    ov_res = client.get("/api/v1/analytics/overview", headers=admin_headers)
    assert ov_res.status_code == 200
    ov_data = ov_res.json()["data"]
    assert ov_data["total_centres"] >= 3
    assert ov_data["total_cameras"] >= 4

    # Risk distribution
    rd_res = client.get("/api/v1/analytics/risk-distribution", headers=admin_headers)
    assert rd_res.status_code == 200
    assert len(rd_res.json()["data"]) == 4

    # Compliance trend
    ct_res = client.get("/api/v1/analytics/compliance-trend", headers=admin_headers)
    assert ct_res.status_code == 200

    # Rankings
    rk_res = client.get("/api/v1/analytics/rankings", headers=admin_headers)
    assert rk_res.status_code == 200
    assert len(rk_res.json()["data"]) >= 3

def test_evaluation_and_reports_endpoints(admin_headers):
    eval_res = client.get("/api/v1/evaluation/results", headers=admin_headers)
    assert eval_res.status_code == 200
    assert "person_detection" in eval_res.json()["data"]

    list_res = client.get("/api/v1/centres", headers=admin_headers)
    centre_id = list_res.json()["data"][0]["id"]
    rep_res = client.get(f"/api/v1/reports/centre/{centre_id}", headers=admin_headers)
    assert rep_res.status_code == 200
    assert len(rep_res.json()["data"]["reports"]) >= 1

def test_not_found_handling(admin_headers):
    res = client.get("/api/v1/centres/999999", headers=admin_headers)
    assert res.status_code == 404
    assert res.json()["success"] is False
    assert "not found" in res.json()["error"]["message"].lower()
