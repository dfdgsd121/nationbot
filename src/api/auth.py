# src/api/auth.py
"""
NationBot Auth System — JWT + Password Hashing
Zero-vendor, built-in auth with lazy auth for guests.
"""
import os
import uuid
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

logger = logging.getLogger("nationbot.auth")

# ============================================================================
# CONFIG
# ============================================================================
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "nationbot-super-secret-change-in-prod-" + secrets.token_hex(16))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

# ============================================================================
# IN-MEMORY USER STORE (swap for PostgreSQL in production)
# ============================================================================
USERS_DB: dict[str, dict] = {}   # user_id -> user dict
EMAILS_INDEX: dict[str, str] = {}  # email -> user_id
API_KEYS_INDEX: dict[str, str] = {}  # api_key -> user_id


# ============================================================================
# MODELS
# ============================================================================
class UserBase(BaseModel):
    email: str
    username: str

class SignupRequest(BaseModel):
    email: str
    username: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class GoogleAuthRequest(BaseModel):
    token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    expires_in: int

class UserProfile(BaseModel):
    id: str
    email: str
    username: str
    role: str  # "human" or "agent"
    followed_nations: list[str]
    api_key: Optional[str] = None
    created_at: str
    interaction_count: int

class GuestUser:
    """Represents an unauthenticated guest."""
    def __init__(self):
        self.id = None
        self.username = "Guest"
        self.role = "guest"
        self.is_authenticated = False

class AuthenticatedUser:
    """Represents a logged-in user."""
    def __init__(self, user_data: dict):
        self.id = user_data["id"]
        self.username = user_data["username"]
        self.email = user_data["email"]
        self.role = user_data["role"]
        self.is_authenticated = True
        self.followed_nations = user_data.get("followed_nations", [])
        self.api_key = user_data.get("api_key")


# ============================================================================
# PASSWORD UTILS
# ============================================================================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ============================================================================
# JWT UTILS
# ============================================================================
def create_access_token(user_id: str, username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "username": username,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


# ============================================================================
# USER CRUD
# ============================================================================
def create_user(email: str, username: str, password: str, role: str = "human") -> dict:
    if email.lower() in EMAILS_INDEX:
        raise HTTPException(status_code=409, detail="Email already registered")

    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": email.lower(),
        "username": username,
        "hashed_password": hash_password(password),
        "role": role,
        "auth_provider": "email",
        "picture": None,
        "followed_nations": [],
        "api_key": None,
        "created_at": datetime.utcnow().isoformat(),
        "interaction_count": 0,
    }
    USERS_DB[user_id] = user
    EMAILS_INDEX[email.lower()] = user_id
    logger.info(f"User created: {username} ({email})")
    return user


def create_or_get_google_user(email: str, name: str, picture: str = None) -> dict:
    """Find existing user by email or create a new Google-auth user."""
    existing = get_user_by_email(email)
    if existing:
        # Update picture if changed
        if picture and existing.get("picture") != picture:
            existing["picture"] = picture
        return existing

    user_id = str(uuid.uuid4())
    username = name.replace(" ", "").lower()[:20] or email.split("@")[0]
    # Ensure unique username
    base = username
    counter = 1
    while any(u["username"] == username for u in USERS_DB.values()):
        username = f"{base}{counter}"
        counter += 1

    user = {
        "id": user_id,
        "email": email.lower(),
        "username": username,
        "hashed_password": None,  # No password for Google users
        "role": "human",
        "auth_provider": "google",
        "picture": picture,
        "followed_nations": [],
        "api_key": None,
        "created_at": datetime.utcnow().isoformat(),
        "interaction_count": 0,
    }
    USERS_DB[user_id] = user
    EMAILS_INDEX[email.lower()] = user_id
    logger.info(f"Google user created: {username} ({email})")
    return user

def get_user_by_email(email: str) -> Optional[dict]:
    uid = EMAILS_INDEX.get(email.lower())
    return USERS_DB.get(uid) if uid else None

def get_user_by_id(user_id: str) -> Optional[dict]:
    return USERS_DB.get(user_id)

def generate_api_key(user_id: str) -> str:
    user = USERS_DB.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    key = f"nb_{secrets.token_hex(24)}"
    user["api_key"] = key
    user["role"] = "agent"
    API_KEYS_INDEX[key] = user_id
    return key


# ============================================================================
# FASTAPI DEPENDENCIES
# ============================================================================
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> AuthenticatedUser:
    """Strict auth — raises 401 if not authenticated."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")

    token = credentials.credentials

    # Check API key first
    if token.startswith("nb_"):
        uid = API_KEYS_INDEX.get(token)
        if not uid:
            raise HTTPException(status_code=401, detail="Invalid API key")
        user = USERS_DB.get(uid)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return AuthenticatedUser(user)

    # JWT token
    payload = decode_token(token)
    user = USERS_DB.get(payload.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return AuthenticatedUser(user)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    """Lazy auth — returns GuestUser if not authenticated, AuthenticatedUser if they are."""
    if not credentials:
        return GuestUser()

    try:
        token = credentials.credentials

        # API key
        if token.startswith("nb_"):
            uid = API_KEYS_INDEX.get(token)
            if uid and uid in USERS_DB:
                return AuthenticatedUser(USERS_DB[uid])
            return GuestUser()

        # JWT
        payload = decode_token(token)
        user = USERS_DB.get(payload.get("sub"))
        if user:
            return AuthenticatedUser(user)
    except Exception:
        pass

    return GuestUser()
