"""
Authentication API Endpoints for Petrol Pump Ledger Automation

This module provides authentication API endpoints using BetterAuth concepts
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

from ...database.connection import get_db_session
from ...services.auth_service import AuthService, get_current_user
from ...models.User import User

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db_session)):
    """
    Login endpoint
    """
    try:
        token = AuthService.login_user(db, user_credentials.email, user_credentials.password)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user info to include in response
        user = db.query(User).filter(User.email == user_credentials.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            user_id=user.id,
            email=user.email
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db_session)):
    """
    Registration endpoint
    """
    try:
        token = AuthService.register_user(
            db,
            user_data.email,
            user_data.password,
            user_data.name
        )

        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Get user info to include in response
        user = db.query(User).filter(User.email == user_data.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )

        return TokenResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            user_id=user.id,
            email=user.email
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )


@router.post("/logout")
async def logout():
    """
    Logout endpoint
    """
    # In a real implementation, you might want to add the token to a blacklist
    # For now, we'll just return a success message
    return {"message": "Logged out successfully"}


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "pump_name": current_user.pump_name,
        "pump_location": current_user.pump_location,
        "language_preference": current_user.language_preference,
        "created_at": current_user.created_at
    }


@router.put("/profile")
async def update_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Update user profile
    """
    try:
        # Update allowed fields
        allowed_fields = {"name", "pump_name", "pump_location", "language_preference"}

        for field, value in profile_data.items():
            if field in allowed_fields and hasattr(current_user, field):
                setattr(current_user, field, value)

        current_user.updated_at = db.func.now()

        db.commit()
        db.refresh(current_user)

        logger.info(f"Profile updated for user ID: {current_user.id}")

        return {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "pump_name": current_user.pump_name,
            "pump_location": current_user.pump_location,
            "language_preference": current_user.language_preference,
            "updated_at": current_user.updated_at
        }
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating profile"
        )


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """
    Change user password
    """
    try:
        success = AuthService.update_user_password(
            db,
            current_user.id,
            password_data.current_password,
            password_data.new_password
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        logger.info(f"Password changed for user ID: {current_user.id}")
        return {"message": "Password changed successfully"}
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while changing password"
        )


@router.post("/refresh-token")
async def refresh_token(token: str):
    """
    Refresh access token
    """
    try:
        new_token = AuthService.refresh_token(token)
        if not new_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return new_token
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while refreshing token"
        )