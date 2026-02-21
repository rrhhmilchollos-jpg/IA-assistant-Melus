"""
MelusAI - OAuth Authentication System
Sistema de autenticación propio con Google, Facebook y Email/Password
"""
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from datetime import timedelta
import bcrypt
import httpx
import logging
import os
import secrets
from urllib.parse import urlencode

from models import User, UserRegister, UserLogin, LoginResponse
from config import FREE_CREDITS, ADMIN_EMAILS
from utils import generate_id, utc_now, get_authenticated_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

# OAuth Configuration from environment
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID', '')
FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET', '')

# Get base URL from environment
def get_base_url():
    return os.environ.get('BASE_URL', 'https://melus-dev-studio.preview.emergentagent.com')

# ============= EMAIL/PASSWORD AUTH =============

@router.post("/register", response_model=LoginResponse)
async def register_user(user_register: UserRegister, response: Response, request: Request):
    """Register a new user with email and password"""
    db = request.app.state.db
    
    if "@" not in user_register.email or "." not in user_register.email:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    existing_user = await db.users.find_one(
        {"email": user_register.email.lower()},
        {"_id": 0}
    )
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if len(user_register.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    password_hash = bcrypt.hashpw(user_register.password.encode('utf-8'), bcrypt.gensalt())
    
    is_admin = user_register.email.lower() in ADMIN_EMAILS
    
    user_id = generate_id("user")
    session_token = generate_id("token")
    
    new_user = {
        "user_id": user_id,
        "email": user_register.email.lower(),
        "name": user_register.name,
        "password_hash": password_hash.decode('utf-8'),
        "picture": f"https://ui-avatars.com/api/?name={user_register.name}&background=9333ea&color=fff",
        "credits": 10000 if is_admin else FREE_CREDITS,
        "credits_used": 0,
        "is_admin": is_admin,
        "subscription_tier": "free",
        "auth_provider": "email",
        "session_token": session_token,
        "created_at": utc_now(),
        "updated_at": utc_now()
    }
    await db.users.insert_one(new_user)
    
    # Create session
    session_id = generate_id("sess")
    expires_at = utc_now() + timedelta(days=30)
    
    session_data = {
        "session_id": session_id,
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at,
        "created_at": utc_now()
    }
    await db.user_sessions.insert_one(session_data)
    
    # Update user with session token
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"session_token": session_token}}
    )
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=30*24*60*60,
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
        {"email": user_login.email.lower()},
        {"_id": 0}
    )
    
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if "password_hash" not in user_doc:
        provider = user_doc.get("auth_provider", "OAuth")
        raise HTTPException(
            status_code=401, 
            detail=f"This account uses {provider} login. Please use that method."
        )
    
    password_valid = bcrypt.checkpw(
        user_login.password.encode('utf-8'),
        user_doc["password_hash"].encode('utf-8')
    )
    
    if not password_valid:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    session_token = generate_id("token")
    session_id = generate_id("sess")
    expires_at = utc_now() + timedelta(days=30)
    
    session_data = {
        "session_id": session_id,
        "user_id": user_doc["user_id"],
        "session_token": session_token,
        "expires_at": expires_at,
        "created_at": utc_now()
    }
    await db.user_sessions.insert_one(session_data)
    
    # Update user with new session token
    await db.users.update_one(
        {"user_id": user_doc["user_id"]},
        {"$set": {"session_token": session_token, "updated_at": utc_now()}}
    )
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=30*24*60*60,
        path="/"
    )
    
    if "password_hash" in user_doc:
        del user_doc["password_hash"]
    user_doc["session_token"] = session_token
    user = User(**user_doc)
    
    return LoginResponse(
        user=user,
        session_token=session_token,
        message="Login successful"
    )


# ============= GOOGLE OAUTH =============

@router.get("/google")
async def google_auth_redirect(request: Request):
    """Redirect to Google OAuth"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        # Redirect to login page with error message instead of 500
        return RedirectResponse(url=f"{get_base_url()}/login?error=google_not_configured")
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state in session (we'll verify it on callback)
    db = request.app.state.db
    await db.oauth_states.insert_one({
        "state": state,
        "provider": "google",
        "created_at": utc_now(),
        "expires_at": utc_now() + timedelta(minutes=10)
    })
    
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": f"{get_base_url()}/api/auth/google/callback",
        "response_type": "code",
        "scope": "email profile",
        "state": state,
        "prompt": "select_account"
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_auth_callback(request: Request, code: str = None, state: str = None, error: str = None):
    """Handle Google OAuth callback"""
    if error:
        return RedirectResponse(url=f"{get_base_url()}/?error={error}")
    
    if not code or not state:
        return RedirectResponse(url=f"{get_base_url()}/?error=missing_params")
    
    db = request.app.state.db
    
    # Verify state
    state_doc = await db.oauth_states.find_one({"state": state, "provider": "google"})
    if not state_doc:
        return RedirectResponse(url=f"{get_base_url()}/?error=invalid_state")
    
    # Delete used state
    await db.oauth_states.delete_one({"state": state})
    
    try:
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": f"{get_base_url()}/api/auth/google/callback"
                }
            )
            
            if token_response.status_code != 200:
                logger.error(f"Google token error: {token_response.text}")
                return RedirectResponse(url=f"{get_base_url()}/?error=token_error")
            
            tokens = token_response.json()
            access_token = tokens["access_token"]
            
            # Get user info
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if user_response.status_code != 200:
                return RedirectResponse(url=f"{get_base_url()}/?error=userinfo_error")
            
            user_info = user_response.json()
        
        # Create or update user
        email = user_info["email"].lower()
        name = user_info.get("name", email.split("@")[0])
        picture = user_info.get("picture", f"https://ui-avatars.com/api/?name={name}&background=4285f4&color=fff")
        
        session_token = generate_id("token")
        
        existing_user = await db.users.find_one({"email": email})
        
        if existing_user:
            user_id = existing_user["user_id"]
            await db.users.update_one(
                {"email": email},
                {"$set": {
                    "name": name,
                    "picture": picture,
                    "session_token": session_token,
                    "auth_provider": "google",
                    "updated_at": utc_now()
                }}
            )
        else:
            user_id = generate_id("user")
            is_admin = email in ADMIN_EMAILS
            
            new_user = {
                "user_id": user_id,
                "email": email,
                "name": name,
                "picture": picture,
                "credits": 10000 if is_admin else FREE_CREDITS,
                "credits_used": 0,
                "is_admin": is_admin,
                "subscription_tier": "free",
                "auth_provider": "google",
                "session_token": session_token,
                "created_at": utc_now(),
                "updated_at": utc_now()
            }
            await db.users.insert_one(new_user)
        
        # Create session
        session_data = {
            "session_id": generate_id("sess"),
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": utc_now() + timedelta(days=30),
            "created_at": utc_now()
        }
        await db.user_sessions.insert_one(session_data)
        
        # Redirect with token
        redirect_url = f"{get_base_url()}/auth/callback?token={session_token}"
        response = RedirectResponse(url=redirect_url)
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=30*24*60*60,
            path="/"
        )
        return response
        
    except Exception as e:
        logger.error(f"Google OAuth error: {e}")
        return RedirectResponse(url=f"{get_base_url()}/?error=oauth_error")


# ============= FACEBOOK OAUTH =============

@router.get("/facebook")
async def facebook_auth_redirect(request: Request):
    """Redirect to Facebook OAuth"""
    if not FACEBOOK_APP_ID or not FACEBOOK_APP_SECRET:
        return RedirectResponse(url=f"{get_base_url()}/login?error=facebook_not_configured")
    
    state = secrets.token_urlsafe(32)
    
    db = request.app.state.db
    await db.oauth_states.insert_one({
        "state": state,
        "provider": "facebook",
        "created_at": utc_now(),
        "expires_at": utc_now() + timedelta(minutes=10)
    })
    
    params = {
        "client_id": FACEBOOK_APP_ID,
        "redirect_uri": f"{get_base_url()}/api/auth/facebook/callback",
        "state": state,
        "scope": "email,public_profile"
    }
    
    auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"
    return RedirectResponse(url=auth_url)


@router.get("/facebook/callback")
async def facebook_auth_callback(request: Request, code: str = None, state: str = None, error: str = None):
    """Handle Facebook OAuth callback"""
    if error:
        return RedirectResponse(url=f"{get_base_url()}/?error={error}")
    
    if not code or not state:
        return RedirectResponse(url=f"{get_base_url()}/?error=missing_params")
    
    db = request.app.state.db
    
    # Verify state
    state_doc = await db.oauth_states.find_one({"state": state, "provider": "facebook"})
    if not state_doc:
        return RedirectResponse(url=f"{get_base_url()}/?error=invalid_state")
    
    await db.oauth_states.delete_one({"state": state})
    
    try:
        async with httpx.AsyncClient() as client:
            # Exchange code for token
            token_response = await client.get(
                "https://graph.facebook.com/v18.0/oauth/access_token",
                params={
                    "client_id": FACEBOOK_APP_ID,
                    "client_secret": FACEBOOK_APP_SECRET,
                    "redirect_uri": f"{get_base_url()}/api/auth/facebook/callback",
                    "code": code
                }
            )
            
            if token_response.status_code != 200:
                logger.error(f"Facebook token error: {token_response.text}")
                return RedirectResponse(url=f"{get_base_url()}/?error=token_error")
            
            tokens = token_response.json()
            access_token = tokens["access_token"]
            
            # Get user info
            user_response = await client.get(
                "https://graph.facebook.com/me",
                params={
                    "fields": "id,name,email,picture.type(large)",
                    "access_token": access_token
                }
            )
            
            if user_response.status_code != 200:
                return RedirectResponse(url=f"{get_base_url()}/?error=userinfo_error")
            
            user_info = user_response.json()
        
        email = user_info.get("email", f"{user_info['id']}@facebook.com").lower()
        name = user_info.get("name", "Facebook User")
        picture = user_info.get("picture", {}).get("data", {}).get("url", 
            f"https://ui-avatars.com/api/?name={name}&background=1877f2&color=fff")
        
        session_token = generate_id("token")
        
        existing_user = await db.users.find_one({"email": email})
        
        if existing_user:
            user_id = existing_user["user_id"]
            await db.users.update_one(
                {"email": email},
                {"$set": {
                    "name": name,
                    "picture": picture,
                    "session_token": session_token,
                    "auth_provider": "facebook",
                    "updated_at": utc_now()
                }}
            )
        else:
            user_id = generate_id("user")
            is_admin = email in ADMIN_EMAILS
            
            new_user = {
                "user_id": user_id,
                "email": email,
                "name": name,
                "picture": picture,
                "credits": 10000 if is_admin else FREE_CREDITS,
                "credits_used": 0,
                "is_admin": is_admin,
                "subscription_tier": "free",
                "auth_provider": "facebook",
                "session_token": session_token,
                "created_at": utc_now(),
                "updated_at": utc_now()
            }
            await db.users.insert_one(new_user)
        
        session_data = {
            "session_id": generate_id("sess"),
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": utc_now() + timedelta(days=30),
            "created_at": utc_now()
        }
        await db.user_sessions.insert_one(session_data)
        
        redirect_url = f"{get_base_url()}/auth/callback?token={session_token}"
        response = RedirectResponse(url=redirect_url)
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=30*24*60*60,
            path="/"
        )
        return response
        
    except Exception as e:
        logger.error(f"Facebook OAuth error: {e}")
        return RedirectResponse(url=f"{get_base_url()}/?error=oauth_error")


# ============= COMMON ENDPOINTS =============

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
    
    session_token = request.cookies.get("session_token") or request.headers.get("X-Session-Token")
    
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
        await db.users.update_one(
            {"session_token": session_token},
            {"$unset": {"session_token": ""}}
        )
    
    response.delete_cookie(
        "session_token",
        path="/",
        secure=True,
        httponly=True,
        samesite="none"
    )
    
    return {"message": "Logged out successfully"}


@router.get("/status")
async def auth_status():
    """Check OAuth configuration status"""
    return {
        "google_configured": bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET),
        "facebook_configured": bool(FACEBOOK_APP_ID and FACEBOOK_APP_SECRET),
        "email_enabled": True
    }
