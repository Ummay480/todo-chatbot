"""
Authentication Middleware for Petrol Pump Ledger Automation

This module provides authentication middleware using BetterAuth concepts
"""
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer
from typing import Optional
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps

from ..database.connection import get_db_session
from ..models.User import User

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

security = HTTPBearer()


class AuthMiddleware:
    """
    Authentication Middleware Class
    """

    @staticmethod
    async def verify_token(token: str) -> dict:
        """
        Verify the JWT token and return the payload
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    async def get_current_user(request: Request) -> User:
        """
        Get the current authenticated user from the request
        """
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ")[1]

        # Verify token
        payload = await AuthMiddleware.verify_token(token)

        # Get user ID from token
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        db_gen = get_db_session()
        db = next(db_gen)
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is inactive",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return user
        finally:
            db.close()


def require_auth():
    """
    Decorator to require authentication for a route
    """
    async def auth_wrapper(request: Request):
        return await AuthMiddleware.get_current_user(request)
    return auth_wrapper


def require_role(required_roles: list):
    """
    Decorator to require specific roles for a route

    Args:
        required_roles: List of roles that are allowed to access the route
    """
    def role_wrapper(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user = await AuthMiddleware.get_current_user(request)

            # Check if user has required role
            # For simplicity, we'll assume user has a role attribute
            # In a real implementation, you might have a UserRole table
            user_role = getattr(user, 'role', 'user')  # Default role is 'user'

            if user_role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )

            return await func(request, *args, **kwargs)
        return wrapper
    return role_wrapper


def get_user_from_token(token: str) -> Optional[dict]:
    """
    Extract user information from token without database lookup
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            'user_id': payload.get('user_id'),
            'email': payload.get('sub'),
            'exp': payload.get('exp')
        }
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None


# FastAPI dependency function for getting current user
async def get_current_user(request: Request) -> User:
    """
    FastAPI dependency to get the current authenticated user
    """
    return await AuthMiddleware.get_current_user(request)


# Example usage as a middleware in FastAPI app
async def auth_middleware(request: Request, call_next):
    """
    FastAPI middleware function for authentication
    """
    # Skip authentication for public routes
    public_routes = ["/", "/health", "/docs", "/redoc", "/api/v1/auth/login", "/api/v1/auth/register"]

    if request.url.path in public_routes:
        return await call_next(request)

    # For API routes, require authentication
    if request.url.path.startswith("/api/"):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ")[1]
        try:
            await AuthMiddleware.verify_token(token)
        except HTTPException:
            return HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    response = await call_next(request)
    return response