"""
BetterAuth Authentication Service for Petrol Pump Ledger Automation

This module provides authentication functionality using BetterAuth
"""
import os
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database.connection import get_db_session
from ..models.User import User

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security schemes
security = HTTPBearer()

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class AuthUser(BaseModel):
    id: int
    email: str
    name: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
) -> User:
    """
    Get the current authenticated user from the token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(username=email)
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == token_data.username).first()
    if user is None:
        raise credentials_exception

    return user


def create_user(db: Session, email: str, password: str, name: str = None) -> User:
    """
    Create a new user with hashed password
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise ValueError("User with this email already exists")

    # Hash the password
    hashed_password = get_password_hash(password)

    # Create the user
    db_user = User(
        email=email,
        password_hash=hashed_password,
        name=name
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    logger.info(f"Created new user with email: {email}")
    return db_user


def update_user_password(db: Session, user_id: int, current_password: str, new_password: str) -> bool:
    """
    Update a user's password after verifying the current password
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False

    if not verify_password(current_password, user.password_hash):
        return False

    user.password_hash = get_password_hash(new_password)
    user.updated_at = datetime.utcnow()

    db.commit()
    logger.info(f"Updated password for user ID: {user_id}")
    return True


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by email
    """
    return db.query(User).filter(User.email == email).first()


class AuthService:
    """
    Authentication Service Class
    """

    @staticmethod
    def login_user(db: Session, email: str, password: str) -> Optional[Token]:
        """
        Login a user and return an access token
        """
        user = authenticate_user(db, email, password)
        if not user:
            return None

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )

        logger.info(f"User logged in: {email}")
        return Token(access_token=access_token, token_type="bearer")

    @staticmethod
    def register_user(db: Session, email: str, password: str, name: str = None) -> Optional[Token]:
        """
        Register a new user and return an access token
        """
        try:
            user = create_user(db, email, password, name)

            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.email, "user_id": user.id},
                expires_delta=access_token_expires
            )

            logger.info(f"User registered: {email}")
            return Token(access_token=access_token, token_type="bearer")
        except ValueError as e:
            logger.error(f"Registration failed: {str(e)}")
            return None

    @staticmethod
    def refresh_token(token: str) -> Optional[Token]:
        """
        Refresh an access token
        """
        try:
            # Decode the current token to get user info
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")

            if email is None or user_id is None:
                return None

            # Create a new token with extended expiration
            new_access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            new_access_token = create_access_token(
                data={"sub": email, "user_id": user_id},
                expires_delta=new_access_token_expires
            )

            return Token(access_token=new_access_token, token_type="bearer")
        except jwt.PyJWTError:
            return None