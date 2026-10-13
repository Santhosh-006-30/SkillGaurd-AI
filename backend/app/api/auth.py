from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)
from app.database.database import get_db
from app.database.models import User, UserRole
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=dict)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    access_token = create_access_token(
        subject=user.id,
        role=user.role.value,
        expires_delta=timedelta(minutes=settings.JWT_EXPIRATION)
    )

    return {
        "success": True,
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRATION * 60,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        }
    }

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # Check if username exists
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already registered"
        )

    hashed_pw = get_password_hash(request.password)
    user = User(
        username=request.username,
        email=request.email,
        password_hash=hashed_pw,
        role=request.role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(
        subject=user.id,
        role=user.role.value,
        expires_delta=timedelta(minutes=settings.JWT_EXPIRATION)
    )

    return {
        "success": True,
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRATION * 60,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        }
    }

@router.get("/me", response_model=dict)
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role.value,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None
        }
    }

@router.post("/refresh", response_model=dict)
def refresh_token(current_user: User = Depends(get_current_user)):
    new_token = create_access_token(
        subject=current_user.id,
        role=current_user.role.value,
        expires_delta=timedelta(minutes=settings.JWT_EXPIRATION)
    )
    return {
        "success": True,
        "data": {
            "access_token": new_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRATION * 60,
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "role": current_user.role.value,
                "is_active": current_user.is_active
            }
        }
    }
