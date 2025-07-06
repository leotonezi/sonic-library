from datetime import datetime, timedelta, UTC
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import UserService
from typing import Dict, Optional
import time

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Simple in-memory cache for user authentication
_user_cache: Dict[str, tuple] = {}  # email -> (user_data_dict, timestamp)
CACHE_TTL = 300  # 5 minutes cache TTL

def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Generate a JWT token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = str(int(expire.timestamp()))
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def _get_cached_user(email: str) -> Optional[object]:
    """Get user from cache if not expired."""
    if email in _user_cache:
        user_data_dict, timestamp = _user_cache[email]
        if time.time() - timestamp < CACHE_TTL:
            # Return None to force database lookup to avoid session issues
            return None
        else:
            # Remove expired cache entry
            del _user_cache[email]
    return None

def _cache_user(email: str, user_data: object):
    """Cache user data with timestamp."""
    # Don't cache to avoid session issues
    pass

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get current user from JWT token stored in HTTP-only cookie"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Get token from cookie instead of Authorization header
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_email = payload.get("sub")
        if user_email is None or not isinstance(user_email, str):
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Get user from database (no caching to avoid session issues)
    user_service = UserService(db)
    user = user_service.get_user_by_email(user_email)
    if user is None:
        raise credentials_exception

    return user

def create_activation_token(email: str, expires_delta: timedelta | None = None) -> str:
    """Generate a JWT token specifically for account activation."""
    to_encode = {"sub": email}
    expire = datetime.now(UTC) + (expires_delta or timedelta(hours=24))
    to_encode["exp"] = str(int(expire.timestamp()))
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_activation_token(token: str) -> str:
    """Verify the activation token and extract the email."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if email is None or not isinstance(email, str):
            raise ValueError("Invalid token payload.")
        return email
    except JWTError:
        raise ValueError("Invalid or expired token.")