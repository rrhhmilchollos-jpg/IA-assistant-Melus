"""Authentication routes for Assistant Melus"""
from fastapi import APIRouter, HTTPException, Request, Response
from datetime import timedelta
import bcrypt
import httpx
import logging

from models import (
    User, UserRegister, UserLogin, SessionRequest, SessionResponse, LoginResponse
)
from config import FREE_CREDITS, ADMIN_EMAILS
from utils import generate_id, utc_now, get_authenticated_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=LoginResponse)
async def register_user(user_register: UserRegister, response: Response, request: Request):
    """Register a new user with email and password"""
    db = request.app.state.db
    
    if "@" not in user_register.email or "." not in user_register.email:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    existing_user = await db.users.find_one(
        {"email": user_register.email},
        {"_id": 0}
    )
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if len(user_register.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    password_hash = bcrypt.hashpw(user_register.password.encode('utf-8'), bcrypt.gensalt())
    
    is_admin = user_register.email.lower() in ADMIN_EMAILS
    
    user_id = generate_id("user")
    new_user = {
        "user_id": user_id,
        "email": user_register.email,
        "name": user_register.name,
        "password_hash": password_hash.decode('utf-8'),
        "picture": f"https://ui-avatars.com/api/?name={user_register.name}&background=9333ea&color=fff",
        "credits": 10000 if is_admin else FREE_CREDITS,
        "credits_used": 0,
        "is_admin": is_admin,
        "subscription_tier": "free",
        "created_at": utc_now(),
        "updated_at": utc_now()
    }
    await db.users.insert_one(new_user)
    
    session_token = generate_id("token")
    session_id = generate_id("sess")
    expires_at = utc_now() + timedelta(days=7)
    
    session_data = {
        "session_id": session_id,
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at,
        "created_at": utc_now()
    }
    await db.user_sessions.insert_one(session_data)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7*24*60*60,
        path="/"
    )
    
    del new_user["password_hash"]
    user = User(**new_user)
    
    return LoginResponse(
        user=user,
        session_token=session_token,
        message="User registered successfully"
    )


@router.post("/login", response_model=LoginResponse)
async def login_user(user_login: UserLogin, response: Response, request: Request):
    """Login with email and password"""
    db = request.app.state.db
    
    user_doc = await db.users.find_one(
        {"email": user_login.email},
        {"_id": 0}
    )
    
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if "password_hash" not in user_doc:
        raise HTTPException(status_code=401, detail="Please use Google login for this account")
    
    password_valid = bcrypt.checkpw(
        user_login.password.encode('utf-8'),
        user_doc["password_hash"].encode('utf-8')
    )
    
    if not password_valid:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    session_token = generate_id("token")
    session_id = generate_id("sess")
    expires_at = utc_now() + timedelta(days=7)
    
    session_data = {
        "session_id": session_id,
        "user_id": user_doc["user_id"],
        "session_token": session_token,
        "expires_at": expires_at,
        "created_at": utc_now()
    }
    await db.user_sessions.insert_one(session_data)
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7*24*60*60,
        path="/"
    )
    
    del user_doc["password_hash"]
    user = User(**user_doc)
    
    return LoginResponse(
        user=user,
        session_token=session_token,
        message="Login successful"
    )


@router.post("/session", response_model=SessionResponse)
async def create_session(request: Request, session_request: SessionRequest):
    """Exchange session_id from OAuth for session_token"""
    db = request.app.state.db
    
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_request.session_id},
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid session_id")
            
            auth_data = response.json()
        
        user_doc = await db.users.find_one(
            {"email": auth_data["email"]},
            {"_id": 0}
        )
        
        if user_doc:
            await db.users.update_one(
                {"email": auth_data["email"]},
                {
                    "$set": {
                        "name": auth_data["name"],
                        "picture": auth_data["picture"],
                        "updated_at": utc_now()
                    }
                }
            )
            user_id = user_doc["user_id"]
        else:
            user_id = generate_id("user")
            new_user = {
                "user_id": user_id,
                "email": auth_data["email"],
                "name": auth_data["name"],
                "picture": auth_data["picture"],
                "credits": FREE_CREDITS,
                "credits_used": 0,
                "subscription_tier": "free",
                "created_at": utc_now(),
                "updated_at": utc_now()
            }
            await db.users.insert_one(new_user)
        
        session_token = auth_data.get("session_token") or generate_id("session")
        session_id = generate_id("sess")
        expires_at = utc_now() + timedelta(days=7)
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": expires_at,
            "created_at": utc_now()
        }
        await db.user_sessions.insert_one(session_data)
        
        user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
        user = User(**user_doc)
        
        return SessionResponse(user=user, session_token=session_token)
        
    except httpx.RequestError as e:
        logger.error(f"Auth service error: {e}")
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    except Exception as e:
        logger.error(f"Session creation error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me")
async def get_current_user(request: Request):
    """Get current authenticated user"""
    db = request.app.state.db
    user_doc = await get_authenticated_user(request, db)
    return User(**user_doc)


@router.post("/logout")
async def logout(request: Request, response: Response):
    """Logout user"""
    db = request.app.state.db
    session_token = request.cookies.get("session_token")
    
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    
    response.delete_cookie(
        "session_token",
        path="/",
        secure=True,
        httponly=True,
        samesite="none"
    )
    
    return {"message": "Logged out successfully"}
