# src/auth/dependencies.py
import logging
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from supabase import Client, create_client
import os

logger = logging.getLogger("auth")
security = HTTPBearer(auto_error=False)

# Supabase Config
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-anon-key")

# Singleton Client
# In real app, consider using a lighter-weight JWT-only decoder to avoid overhead
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class User(BaseModel):
    id: str
    email: Optional[str] = None
    role: str = "user"
    is_guest: bool = False

async def verify_jwt(token: str) -> User:
    """
    Verify Supabase JWT.
    """
    try:
        # Supabase's client.auth.get_user(token) handles signature verification
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        
        return User(
            id=user.id,
            email=user.email,
            role=user.app_metadata.get('role', 'user'),
            is_guest=False
        )
    except Exception as e:
        logger.warning(f"JWT Verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_guest_id: Optional[str] = Header(None)
) -> User:
    """
    Lazy Auth: Returns either a verified User OR a Guest User.
    Usage: For endpoints like 'Like' or 'Reply' where we want to lower friction.
    """
    if authorization:
        return await verify_jwt(authorization.credentials)
    
    # If no token, check for Guest ID (e.g., from LocalStorage/Fingerprint via Header)
    if x_guest_id:
        return User(id=f"guest_{x_guest_id}", role="guest", is_guest=True)
    
    # Fallback: Anonymous/New Guest
    return User(id="guest_anon", role="guest", is_guest=True)

async def get_current_user(
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """
    Strict Auth: Enforces login.
    Usage: For 'Claim Nation', 'Settings', etc.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await verify_jwt(authorization.credentials)
