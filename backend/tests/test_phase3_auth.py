import pytest
from datetime import timedelta
from fastapi import Depends, APIRouter
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import (
    create_access_token,
    get_password_hash,
    get_current_user,
    require_roles
)
from app.database.database import SessionLocal
from app.database.models import User, UserRole

# Temporary test endpoints to verify RBAC dependencies
test_rbac_router = APIRouter(prefix="/api/v1/test-rbac", tags=["Test RBAC"])

@test_rbac_router.get("/admin-only")
def admin_only_endpoint(user: User = Depends(require_roles(UserRole.ADMIN))):
    return {"success": True, "message": f"Welcome Admin {user.username}"}

@test_rbac_router.get("/inspector-only")
def inspector_only_endpoint(user: User = Depends(require_roles(UserRole.INSPECTOR))):
    return {"success": True, "message": f"Welcome Inspector {user.username}"}

@test_rbac_router.get("/operator-only")
def operator_only_endpoint(user: User = Depends(require_roles(UserRole.CENTRE_OPERATOR))):
    return {"success": True, "message": f"Welcome Operator {user.username}"}

app.include_router(test_rbac_router)

client = TestClient(app)

def test_login_successful():
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "AdminPassword@2026"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["user"]["username"] == "admin"
    assert data["data"]["user"]["role"] == "ADMIN"

def test_login_invalid_password():
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "WrongPassword!"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert "Incorrect username or password" in data["error"]["message"]

def test_login_invalid_user():
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "non_existent_user_999", "password": "AnyPassword123"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False

def test_auth_me_valid_token():
    # Login to get token
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "monitor", "password": "MonitorPassword@2026"}
    )
    token = login_res.json()["data"]["access_token"]

    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    data = me_res.json()
    assert data["success"] is True
    assert data["data"]["username"] == "monitor"
    assert data["data"]["role"] == "MONITOR"

def test_auth_me_unauthorized_missing_token():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False

def test_auth_me_malformed_token():
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.malformed.token"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert "malformed" in data["error"]["message"].lower() or "invalid" in data["error"]["message"].lower()

def test_auth_me_expired_token():
    # Generate expired token (-10 minutes)
    with SessionLocal() as db:
        user = db.query(User).filter(User.username == "admin").first()
    
    expired_token = create_access_token(
        subject=user.id,
        role=user.role.value,
        expires_delta=timedelta(minutes=-10)
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert "expired" in data["error"]["message"].lower()

def test_inactive_user_rejected():
    with SessionLocal() as db:
        # Create an inactive user
        inactive = db.query(User).filter_by(username="inactive_test_user").first()
        if not inactive:
            inactive = User(
                username="inactive_test_user",
                email="inactive@skillguard.gov.in",
                password_hash=get_password_hash("Password123!"),
                role=UserRole.MONITOR,
                is_active=False
            )
            db.add(inactive)
            db.commit()
            db.refresh(inactive)

    # Login should reject inactive user
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "inactive_test_user", "password": "Password123!"}
    )
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert "deactivated" in data["error"]["message"].lower()

def test_role_based_access_control():
    # 1. Login as Operator
    op_login = client.post(
        "/api/v1/auth/login",
        json={"username": "operator", "password": "OperatorPassword@2026"}
    )
    op_token = op_login.json()["data"]["access_token"]

    # Operator accessing operator-only endpoint -> 200 OK
    op_res = client.get(
        "/api/v1/test-rbac/operator-only",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert op_res.status_code == 200

    # Operator accessing inspector-only endpoint -> 403 Forbidden
    forbidden_res = client.get(
        "/api/v1/test-rbac/inspector-only",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert forbidden_res.status_code == 403
    assert "denied" in forbidden_res.json()["error"]["message"].lower()

    # 2. Login as Admin -> should have access to operator & inspector endpoints
    admin_login = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "AdminPassword@2026"}
    )
    admin_token = admin_login.json()["data"]["access_token"]

    admin_on_op = client.get(
        "/api/v1/test-rbac/operator-only",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_on_op.status_code == 200

    admin_on_insp = client.get(
        "/api/v1/test-rbac/inspector-only",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_on_insp.status_code == 200

def test_registration_flow():
    reg_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "new_inspector_user",
            "email": "new_inspector@skillguard.gov.in",
            "password": "SecurePassword123!",
            "role": "INSPECTOR"
        }
    )
    assert reg_response.status_code in [201, 400]
    if reg_response.status_code == 201:
        data = reg_response.json()
        assert data["success"] is True
        assert data["data"]["user"]["username"] == "new_inspector_user"
        assert data["data"]["user"]["role"] == "INSPECTOR"
