# src/api/endpoints/auth_endpoints.py
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from src.api.auth import (
    SignupRequest, LoginRequest, GoogleAuthRequest, TokenResponse, UserProfile,
    create_user, get_user_by_email, verify_password,
    create_access_token, create_refresh_token,
    get_current_user, AuthenticatedUser, generate_api_key,
    decode_token, USERS_DB, create_or_get_google_user
)

router = APIRouter()

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"

@router.post("/google", response_model=TokenResponse)
async def google_auth(request: GoogleAuthRequest):
    """Authenticate via Google ID token."""
    # Verify the token with Google
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            GOOGLE_TOKENINFO_URL,
            params={"id_token": request.token},
            timeout=10.0,
        )
    
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Google token")
    
    token_info = resp.json()
    email = token_info.get("email")
    name = token_info.get("name", token_info.get("given_name", ""))
    picture = token_info.get("picture")
    
    if not email:
        raise HTTPException(status_code=400, detail="Google token missing email")
    
    # Create or find the user
    user = create_or_get_google_user(email=email, name=name, picture=picture)
    
    access_token = create_access_token(user["id"], user["username"])
    refresh_token = create_refresh_token(user["id"])
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user["id"],
        "username": user["username"],
        "expires_in": 3600 * 24
    }


@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest):
    """Create a new human user account."""
    user = create_user(
        email=request.email,
        username=request.username,
        password=request.password,
        role="human"
    )
    
    access_token = create_access_token(user["id"], user["username"])
    refresh_token = create_refresh_token(user["id"])
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user["id"],
        "username": user["username"],
        "expires_in": 3600 * 24
    }

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login with email and password."""
    user = get_user_by_email(request.email)
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(user["id"], user["username"])
    refresh_token = create_refresh_token(user["id"])
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user["id"],
        "username": user["username"],
        "expires_in": 3600 * 24
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token: str):
    """Refresh an expired access token using a refresh token."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
        user = USERS_DB.get(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
            
        access_token = create_access_token(user["id"], user["username"])
        # Rotate refresh token
        new_refresh_token = create_refresh_token(user["id"])
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user_id": user["id"],
            "username": user["username"],
            "expires_in": 3600 * 24
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.get("/me", response_model=UserProfile)
async def get_my_profile(user: AuthenticatedUser = Depends(get_current_user)):
    """Get current user profile."""
    # Re-fetch from DB to get latest state
    user_data = USERS_DB.get(user.id)
    return user_data

@router.post("/agent-key")
async def create_agent_key(user: AuthenticatedUser = Depends(get_current_user)):
    """Generate or regenerate an API key for agent access."""
    if user.role != "agent" and user.role != "human":
         # In this MVP, humans can become agent-commanders
         pass
         
    api_key = generate_api_key(user.id)
    return {"api_key": api_key, "note": "Save this key! It won't be shown again."}
